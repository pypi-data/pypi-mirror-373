from dataclasses import asdict
from random import randint

import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.fits_access import FitsAccessBase

from dkist_processing_vbi.models.constants import VbiConstants
from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l1_fits_access import VbiL1FitsAccess
from dkist_processing_vbi.tasks.make_movie_frames import MakeVbiMovieFrames
from dkist_processing_vbi.tests.conftest import Vbi122ObserveFrames
from dkist_processing_vbi.tests.conftest import VbiConstantsDb
from dkist_processing_vbi.tests.conftest import ensure_all_inputs_used
from dkist_processing_vbi.tests.conftest import generate_214_l1_fits_frame


@pytest.fixture(scope="function")
def raw_make_movie_frames_task(tmp_path, recipe_run_id, init_vbi_constants_db):
    num_steps = 4
    num_mosaic_repeats = 2
    constants_db = VbiConstantsDb(
        NUM_SPATIAL_STEPS=num_steps,
        NUM_MOSAIC_REPEATS=num_mosaic_repeats,
    )
    init_vbi_constants_db(recipe_run_id, constants_db)
    with MakeVbiMovieFrames(
        recipe_run_id=recipe_run_id, workflow_name="vbi_make_movie_frames", workflow_version="VX.Y"
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_steps = 4
        task.num_exp_per_step = 2
        task.testing_num_mosaic_repeats = num_mosaic_repeats
        ds = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.testing_num_mosaic_repeats,
            num_mosaics_per_dsps_repeat=1,  # No subcycling
        )
        header_generator = (d.header() for d in ds)
        for s in range(1, task.num_steps + 1):
            for e in range(1, task.num_exp_per_step + 1):
                for m in range(1, task.testing_num_mosaic_repeats + 1):
                    value = (s - 1) + (e - 1) * 2 + (m - 1)
                    data = np.ones((10, 10)) * value
                    header = next(header_generator)
                    hdl = generate_214_l1_fits_frame(data=data, s122_header=header)
                    hdl[1].header["CRVAL1"] = 0.0
                    hdl[1].header["CRVAL2"] = 0.0
                    hdl[1].header["CDELT1"] = 1.0
                    hdl[1].header["CDELT2"] = 1.0
                    hdl[1].header["CRPIX1"] = (s % 2) * 7
                    hdl[1].header["CRPIX2"] = -1 * ((s - 1) // 2 - 1) * 7
                    hdl[1].header["DSPSNUM"] = m
                    hdl[1].header["VBISTP"] = s
                    task.write(
                        data=hdl,
                        tags=[
                            VbiTag.calibrated(),
                            VbiTag.frame(),
                            VbiTag.spatial_step(s),
                            VbiTag.mosaic(m),
                        ],
                        encoder=fits_hdulist_encoder,
                    )
        ensure_all_inputs_used(header_generator)
        yield task
        task._purge()


@pytest.fixture(scope="module")
def make_movie_frames_task_with_averages(tmp_path_factory):
    num_steps = 4
    num_mosaic_repeats = 2
    recipe_run_id = randint(0, 99999)
    constants_db = VbiConstantsDb(
        NUM_SPATIAL_STEPS=num_steps, NUM_MOSAIC_REPEATS=num_mosaic_repeats
    )
    # Repeat ini_vbi_constants fixture here because of a scope conflict
    constants = VbiConstants(recipe_run_id=recipe_run_id, task_name="test")
    constants._update(asdict(constants_db))
    with MakeVbiMovieFrames(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_make_movie_frames",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(
            scratch_base_path=tmp_path_factory.mktemp("scratch"), recipe_run_id=recipe_run_id
        )
        task.num_steps = 4
        task.num_exp_per_step = 1
        task.testing_num_mosaic_repeats = num_mosaic_repeats
        ds = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.testing_num_mosaic_repeats,
            num_mosaics_per_dsps_repeat=1,  # No subcycling
        )
        header_generator = (d.header() for d in ds)
        for s in range(1, task.num_steps + 1):
            for m in range(1, task.testing_num_mosaic_repeats + 1):
                header = next(header_generator)
                value = s - 1 + m - 1
                data = np.ones((10, 10)) * value
                hdl = generate_214_l1_fits_frame(s122_header=header, data=data)
                hdl[1].header["CRVAL1"] = 0.0
                hdl[1].header["CRVAL2"] = 0.0
                hdl[1].header["CDELT1"] = 1.0
                hdl[1].header["CDELT2"] = 1.0
                hdl[1].header["CRPIX1"] = (s % 2) * 7
                hdl[1].header["CRPIX2"] = -1 * ((s - 1) // 2 - 1) * 7
                hdl[1].header["DSPSNUM"] = m
                hdl[1].header["VBISTP"] = s
                task.write(
                    data=hdl,
                    tags=[
                        VbiTag.intermediate(),
                        VbiTag.task("AVG_MOVIE_FRAME"),
                        VbiTag.spatial_step(s),
                        VbiTag.mosaic(m),
                    ],
                    encoder=fits_hdulist_encoder,
                )
        ensure_all_inputs_used(header_generator)
        yield task
        task._purge()


@pytest.fixture(scope="module")
def place_pos_arguments():
    ref_header = fits.Header()
    ref_header["CRPIX1"] = 8
    ref_header["CRPIX2"] = 8
    data = np.ones((10, 10)) * 7  # No reason this is 7. Nice to have it be different than 1
    hdu = fits.PrimaryHDU(data=data)
    hdu.header["CRPIX1"] = 7.5
    hdu.header["CRPIX2"] = 0.5
    access = FitsAccessBase(hdu=hdu, name=None, auto_squeeze=True)

    output = np.zeros((17, 17))
    px_count = np.zeros((17, 17))

    return access, ref_header, output, px_count


def compute_expected_mosiac(modification: int):

    expected = np.zeros((17, 17))
    counts = np.zeros((17, 17))

    hann_1d = np.abs(np.hanning(10))
    hann_2d = np.sqrt(np.outer(hann_1d, hann_1d))

    # Step 1
    expected[:10, :10] += (1 + modification) * hann_2d
    counts[:10, :10] += 1 * hann_2d
    # Step 2
    expected[:10, 7:] += (2 + modification) * hann_2d
    counts[:10, 7:] += 1 * hann_2d
    # Step 3
    expected[7:, :10] += (3 + modification) * hann_2d
    counts[7:, :10] += 1 * hann_2d
    # Step 4
    expected[7:, 7:] += (4 + modification) * hann_2d
    counts[7:, 7:] += 1 * hann_2d

    idx = np.where(counts != 0)
    expected[idx] /= counts[idx]

    return expected


def test_make_movie_frames_task(raw_make_movie_frames_task, mocker, fake_gql_client):
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )

    raw_make_movie_frames_task()

    frame_access_list = list(
        raw_make_movie_frames_task.read(
            tags=[VbiTag.movie_frame()],
            decoder=fits_access_decoder,
            fits_access_class=VbiL1FitsAccess,
        )
    )
    assert len(frame_access_list) == raw_make_movie_frames_task.testing_num_mosaic_repeats

    frame_access_list = sorted(frame_access_list, key=lambda x: x.current_dsps_repeat)
    assert [o.current_dsps_repeat for o in frame_access_list] == list(
        range(1, raw_make_movie_frames_task.testing_num_mosaic_repeats + 1)
    )
    for i in range(raw_make_movie_frames_task.testing_num_mosaic_repeats):
        np.testing.assert_almost_equal(frame_access_list[i].data, compute_expected_mosiac(i))


def test_average_all_exposures(raw_make_movie_frames_task):
    raw_make_movie_frames_task.average_all_exposures()
    for s in range(1, raw_make_movie_frames_task.num_steps + 1):
        for m in range(1, raw_make_movie_frames_task.testing_num_mosaic_repeats + 1):
            arrays = list(
                raw_make_movie_frames_task.read(
                    tags=[
                        VbiTag.intermediate(),
                        VbiTag.task("AVG_MOVIE_FRAME"),
                        VbiTag.spatial_step(s),
                        VbiTag.mosaic(m),
                    ],
                    decoder=fits_array_decoder,
                )
            )
            assert len(arrays) == 1
            data = arrays[0]
            expected = np.ones((10, 10)) * (s + m - 1)
            np.testing.assert_equal(data, expected)


def test_find_ref_pos(make_movie_frames_task_with_averages):
    access_list = list(
        make_movie_frames_task_with_averages.read(
            tags=[VbiTag.intermediate(), VbiTag.task("AVG_MOVIE_FRAME"), VbiTag.mosaic(2)],
            decoder=fits_access_decoder,
            fits_access_class=VbiL1FitsAccess,
        )
    )
    assert make_movie_frames_task_with_averages.find_ref_pos(access_list) == 1


def test_get_fov_size(make_movie_frames_task_with_averages):
    access_list = list(
        make_movie_frames_task_with_averages.read(
            tags=[VbiTag.intermediate(), VbiTag.task("AVG_MOVIE_FRAME"), VbiTag.mosaic(1)],
            decoder=fits_access_decoder,
            fits_access_class=VbiL1FitsAccess,
        )
    )
    assert make_movie_frames_task_with_averages.get_fov_size(
        access_list, access_list[0].header
    ) == (17, 17)


def test_place_pos_in_full_fov(make_movie_frames_task_with_averages, place_pos_arguments):
    access, ref_header, output, px_count = place_pos_arguments
    make_movie_frames_task_with_averages.place_pos_in_full_fov(*place_pos_arguments)

    hann_1d = np.abs(np.hanning(10))
    hann_2d = np.sqrt(np.outer(hann_1d, hann_1d))

    expected_output = np.zeros((17, 17))
    expected_counts = np.zeros((17, 17))
    expected_output[7:, :10] += 7 * hann_2d
    expected_counts[7:, :10] += 1 * hann_2d

    np.testing.assert_almost_equal(expected_output, output)
    np.testing.assert_almost_equal(expected_counts, px_count)
