"""VBI movie frame creation."""

import numpy as np
import scipy.ndimage as spnd
from astropy.io import fits
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdu_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_math.statistics import average_numpy_arrays
from dkist_service_configuration.logging import logger

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l1_fits_access import VbiL1FitsAccess
from dkist_processing_vbi.tasks.vbi_base import VbiTaskBase

__all__ = ["MakeVbiMovieFrames"]


class MakeVbiMovieFrames(VbiTaskBase):
    """
    Make VBI movie frames and tag with VBITag.movie_frame().

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs
    """

    def run(self) -> None:
        """
        For each mosaic repeat.

          - Average all exposures for each spatial step
          - Stitch spatial positions into a full-FOV array
          - Write full FOV as a move_frame

        Returns
        -------
        None

        """
        with self.apm_processing_step("averaging exposures"):
            self.average_all_exposures()

        with self.apm_processing_step("stitching full FOV frames"):
            for mosaic in range(1, self.constants.num_mosaic_repeats + 1):
                logger.info(f"stitching full FOV for mosaic repeat {mosaic}")
                output_hdl = self.stitch_single_mosaic_repeat(mosaic)

                with self.apm_writing_step(
                    f"writing stitched movie frame for mosaic repeat {mosaic}"
                ):
                    self.write(
                        data=output_hdl,
                        tags=[VbiTag.movie_frame(), VbiTag.mosaic(mosaic)],
                        encoder=fits_hdulist_encoder,
                    )

    def average_all_exposures(self):
        """For each spatial step and each mosaic repeat, average all exposures into a single frame."""
        for step in range(1, self.constants.num_spatial_steps + 1):
            for mosaic in range(1, self.constants.num_mosaic_repeats + 1):
                apm_str = f"step {step} and repeat number {mosaic}"

                logger.info(f"averaging exposures for {apm_str}")
                output_hdu_generator = self.read(
                    tags=[
                        VbiTag.calibrated(),
                        VbiTag.frame(),
                        VbiTag.spatial_step(step),
                        VbiTag.mosaic(mosaic),
                    ],
                    decoder=fits_hdu_decoder,
                )

                # We're doing it with a list right now to save having to construct a second generator just to get
                # the first header. This may need to change if LOTS of exposures are taken.
                output_hdus = list(output_hdu_generator)
                # We're still keeping the data access in a generator, though
                output_arrays = (h.data for h in output_hdus)
                averaged_frame = average_numpy_arrays(output_arrays)
                first_header = output_hdus[0].header

                logger.info(f"writing averaged data for {apm_str}")
                self.write(
                    data=averaged_frame,
                    header=first_header,
                    tags=[
                        VbiTag.intermediate(),
                        VbiTag.task("AVG_MOVIE_FRAME"),
                        VbiTag.spatial_step(step),
                        VbiTag.mosaic(mosaic),
                    ],
                    encoder=fits_array_encoder,
                )

    def stitch_single_mosaic_repeat(self, mosaic_repeat: int) -> fits.HDUList:
        """
        Take all spatial positions from a single mosaic and stitch them together into a full FOV.

        Each spatial position's location within the full FOV is determined via WCS header information. Overlap regions
        are simply averaged together.

        Parameters
        ----------
        mosaic_repeat : int
             The current dataset parameters repeat

        Returns
        -------
        fits.HDUList
            Full FOV HDUList
        """
        # noinspection PyTypeChecker
        all_step_access: list[VbiL1FitsAccess] = list(
            self.read(
                tags=[
                    VbiTag.intermediate(),
                    VbiTag.task("AVG_MOVIE_FRAME"),
                    VbiTag.mosaic(mosaic_repeat),
                ],
                decoder=fits_access_decoder,
                fits_access_class=VbiL1FitsAccess,
            )
        )

        if len(all_step_access) != self.constants.num_spatial_steps:
            raise ValueError(
                f"Found {len(all_step_access)} spatial positions instead of {self.constants.num_spatial_steps} for {mosaic_repeat=}"
            )

        ref_pos = self.find_ref_pos(all_step_access)
        logger.info(f"reference position automatically determined to be {ref_pos}")
        ref_header = [o.header for o in all_step_access if o.current_spatial_step == ref_pos][0]

        # We get weird with the order of axes here. This is because we want to create frames that "look right" in ds9
        # The names used here in the code will always correspond to numpy ordering, but their order will change.
        size_x, size_y = self.get_fov_size(all_step_access, ref_header)
        logger.info(f"size of stitched output array: ({size_x}, {size_y})")
        output = np.zeros((size_y, size_x))
        px_count = np.zeros((size_y, size_x))

        with self.apm_processing_step(
            f"stitching all camera positions together for {mosaic_repeat=}"
        ):
            for o in all_step_access:
                logger.info(f"Placing position {o.current_spatial_step} into full frame")
                self.place_pos_in_full_fov(o, ref_header, output, px_count)

        # Normalize by the number of overlapping pixels and the Hanning weights
        non_zero_idx = np.where(px_count != 0)
        output[non_zero_idx] /= px_count[non_zero_idx]

        self.write(
            data=px_count,
            tags=[VbiTag.task("MOVIE_PX_COUNT"), VbiTag.debug()],
            encoder=fits_array_encoder,
        )

        return fits.HDUList([fits.PrimaryHDU(data=output, header=ref_header)])

    def find_ref_pos(self, access_list: list[VbiL1FitsAccess]) -> int:
        """
        Find the spatial position with the smallest wcs coordinates.

        This is done by finding the position with the LARGEST CRPIX[12] values. This is because all positions have
        the same values for CRVAL and so the smallest extent of the full FOV wcs will be in the position where the
        location of CRVAL is the farthest from the origin of that position's array. This is the same as saying the
        position with the largest CRPIX values.

            wcs coords ->  2 3 4 5 6 7 8
            px coords  ->  0 1 2 3 4
            frame 1    -> [- - - - -]
            px coords  ->        0 1 2 3
            frame 2    ->       [- - - -]

            For both frames we'll say CRVAL is 6. This implies that frame 1 has CRPIX = 4, while frame 2 has CRPIX = 1.
            Thus we can see that the largest CRPIX corresponds to the smallest extent of the WCS coords.

        Parameters
        ----------
        access_list
            list of VBI intermediate movie frames for a single mosaic repeat


        Returns
        -------
        int
            spatial position with the smallest wcs coordinates

        """
        rpix_list = [o.header["CRPIX1"] ** 2 + o.header["CRPIX2"] ** 2 for o in access_list]
        logger.info(f"{rpix_list=}")
        logger.info(f"positions={[o.current_spatial_step for o in access_list]}")
        ref_idx = np.argmax(rpix_list)

        return access_list[ref_idx].current_spatial_step

    def get_fov_size(
        self, access_list: list[VbiL1FitsAccess], ref_header: fits.Header
    ) -> tuple[int, int]:
        """
        Look at the WCS information for all spatial positions and determine the array size needed to just contain all pixels in the FOV.

        Parameters
        ----------
        access_list
            list of VBI intermediate movie frames for a single mosaic repeat

        ref_header
            reference header used for normalization factors

        Returns
        -------
        2D FOV size (x, y)
        """
        largest_wcs_x = [
            np.max(
                (np.arange(o.header["NAXIS1"]) - (o.header["CRPIX1"])) * o.header["CDELT1"]
                + o.header["CRVAL1"]
            )
            for o in access_list
        ]

        smallest_wcs_x = [
            np.min(
                (np.arange(o.header["NAXIS1"]) - (o.header["CRPIX1"])) * o.header["CDELT1"]
                + o.header["CRVAL1"]
            )
            for o in access_list
        ]

        size_x = (max(largest_wcs_x) - min(smallest_wcs_x)) / ref_header["CDELT1"]

        largest_wcs_y = [
            np.max(
                (np.arange(o.header["NAXIS2"]) - (o.header["CRPIX2"])) * o.header["CDELT2"]
                + o.header["CRVAL2"]
            )
            for o in access_list
        ]

        smallest_wcs_y = [
            np.min(
                (np.arange(o.header["NAXIS2"]) - (o.header["CRPIX2"])) * o.header["CDELT2"]
                + o.header["CRVAL2"]
            )
            for o in access_list
        ]

        size_y = (max(largest_wcs_y) - min(smallest_wcs_y)) / ref_header["CDELT2"]

        # Add 1 to each dimension because indexing starts at 0, which results in being off by 1 using the method above
        return int(np.ceil(size_x)) + 1, int(np.ceil(size_y)) + 1

    def place_pos_in_full_fov(
        self,
        access_obj: VbiL1FitsAccess,
        ref_header: fits.Header,
        output: np.ndarray,
        px_count: np.ndarray,
    ) -> None:
        """
        Shift and place a single spatial position into the full FOV.

        Any shift > 1 pixel is handled by simply slicing into the correct index of the output array. Sub-pixel shifts
        come via a simple interpolation.

        The output and px_count arrays are updated in place.

        Parameters
        ----------
        access_obj  : VbiL1FitsAccess
            L1 FitsAccess object

        ref_header : fits.Header
            reference header

        output : np.ndarray
            array of zeros to write results to

        px_count : np.ndarray
            pixel count

        Returns
        -------
        None
        """
        # See the note in stitch_single_mosaic_repeat() about the transposition of x and y coordinates.
        # tl;dr: it's because ds9 and numpy aren't the same when it comes to [row|column] major.
        size_x, size_y = output.shape
        data = access_obj.data
        small_size_y, small_size_x = [int(s) for s in data.shape]
        counts = np.ones((small_size_y, small_size_x))
        counts[np.where(data == 0)] = 0

        # Location of first px in fiducial header's pixel space
        x_pos = ref_header["CRPIX1"] - access_obj.header["CRPIX1"]
        y_pos = ref_header["CRPIX2"] - access_obj.header["CRPIX2"]

        # We only need to shift onto an integer grid. The gross shifting is taken care of by placing the resampled
        # data into the correct spot of the output array
        x_shift = x_pos % 1
        y_shift = y_pos % 1
        if x_shift < 1e-4:
            x_shift = 0
        if y_shift < 1e-4:
            y_shift = 0
        if 1 - x_shift < 1e-4:
            x_shift = 0
            x_pos += 1
        if 1 - y_shift < 1e-4:
            y_shift = 0
            y_pos += 1
        logger.info(f"[x,y] location of first px in output coordinate space: [{x_pos}, {y_pos}]")
        logger.info(f"[x,y] shift values: [{x_shift}, {y_shift}]")
        logger.info(f"shape of input data: {data.shape}")

        data[~np.isfinite(data)] = np.max(data[np.isfinite(data)])
        shifted = spnd.shift(data, (x_shift, y_shift))
        counts = spnd.shift(counts, (x_shift, y_shift))

        x_min = int(x_pos)
        y_min = int(y_pos)
        x_max = x_min + small_size_x
        y_max = y_min + small_size_y

        # Make sure we're not trying to overfill the output array
        if y_min < 0:
            shifted = shifted[-y_min:, :]
            counts = counts[-y_min:, :]
            y_min = 0
        if x_min < 0:
            shifted = shifted[:, -x_min:]
            counts = counts[:, -x_min:]
            x_min = 0
        if y_max > size_y:
            shifted = shifted[: size_y - y_max, :]
            counts = counts[: size_y - y_max, :]
            y_max = size_y
        if x_max > size_x:
            shifted = shifted[:, : size_x - x_max]
            counts = counts[:, : size_x - x_max]
            x_max = size_x

        logger.info(f"output slice: [{y_min}:{y_max}, {x_min}:{x_max}]")
        logger.info(f"shape of shifted data: {shifted.shape}")
        logger.info(f"shape of output slice: {output[y_min:y_max, x_min:x_max].shape}")

        logger.info("Applying Hann window to output")
        # This is purely aesthetic; it removes hard edges along the mosaic stitch lines
        #   why those edges are there at all? I have no idea.

        # Method for 2D Hann from
        # https://stackoverflow.com/questions/65940166/create-2d-hanning-hamming-blackman-gaussian-window-in-numpy
        hann_x = np.abs(np.hanning(shifted.shape[0]))
        hann_y = np.abs(np.hanning(shifted.shape[1]))
        hann_2d = np.sqrt(np.outer(hann_x, hann_y))

        shifted *= hann_2d
        counts *= hann_2d

        output[y_min:y_max, x_min:x_max] += shifted
        px_count[y_min:y_max, x_min:x_max] += counts
