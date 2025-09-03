import json

import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_access_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.tags import Tag

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.parsers.vbi_l0_fits_access import VbiL0FitsAccess
from dkist_processing_vbi.tasks.science import ScienceCalibration
from dkist_processing_vbi.tests.conftest import Vbi122ObserveFrames
from dkist_processing_vbi.tests.conftest import VbiConstantsDb
from dkist_processing_vbi.tests.conftest import ensure_all_inputs_used
from dkist_processing_vbi.tests.conftest import generate_214_l0_fits_frame


@pytest.fixture(scope="function")
def science_calibration_task(tmp_path, recipe_run_id, init_vbi_constants_db, abort_mosaic):
    num_steps = 4
    num_mosaic_repeats = 3
    num_exp_per_step = 2
    exp_time = 0.01
    constants_db = VbiConstantsDb(
        NUM_SPATIAL_STEPS=num_steps,
        NUM_MOSAIC_REPEATS=num_mosaic_repeats - (1 * abort_mosaic),
        OBSERVE_EXPOSURE_TIMES=(exp_time,),
    )
    init_vbi_constants_db(recipe_run_id, constants_db)
    with ScienceCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_science_calibration",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        ds = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=num_steps,
            num_exp_per_step=num_exp_per_step,
            num_mosaics_per_dsps_repeat=1,
            num_dsps_repeats=num_mosaic_repeats,
        )
        header_generator = (d.header() for d in ds)
        for s in range(1, num_steps + 1):
            dark_cal = np.zeros((1, 10, 10)) + (s * 10)
            task.write(
                data=dark_cal,
                tags=[
                    VbiTag.intermediate(),
                    VbiTag.task_dark_frame(spatial_step=s, exposure_time=exp_time),
                ],
                encoder=fits_array_encoder,
            )

            # Put in a fake dark just to make sure it doesn't get used
            bad_dark_cal = np.zeros((1, 10, 10)) + (s**2 * 10)
            task.write(
                data=bad_dark_cal,
                tags=[
                    VbiTag.intermediate(),
                    VbiTag.task_dark_frame(spatial_step=s, exposure_time=exp_time**2),
                ],
                encoder=fits_array_encoder,
            )

            gain_cal = np.zeros((1, 10, 10)) + (s + 1)
            task.write(
                data=gain_cal,
                tags=[
                    VbiTag.intermediate(),
                    VbiTag.task_gain_frame(spatial_step=s),
                ],
                encoder=fits_array_encoder,
            )

            for e in range(num_exp_per_step):
                for m in range(1, num_mosaic_repeats + 1):
                    if abort_mosaic and m == num_mosaic_repeats and s > num_steps - 2:
                        # Abort the last two mosaic steps of the last DSPS repeat
                        continue
                    header = fits.Header(next(header_generator))
                    data = (np.ones((1, 10, 10)) * (e + 1)) + s + (m * 10)
                    # Multiple by gain
                    data *= gain_cal
                    # Add dark
                    data += dark_cal
                    hdul = generate_214_l0_fits_frame(s122_header=header, data=data)
                    task.write(
                        data=hdul,
                        tags=[
                            VbiTag.input(),
                            VbiTag.task_observe(),
                            VbiTag.spatial_step(s),
                            VbiTag.mosaic(m),
                            VbiTag.frame(),
                            VbiTag.exposure_time(exp_time),
                        ],
                        encoder=fits_hdulist_encoder,
                    )
        if not abort_mosaic:
            ensure_all_inputs_used(header_generator)
        yield task, num_steps, num_exp_per_step, num_mosaic_repeats - (1 * abort_mosaic)
        task._purge()


@pytest.mark.parametrize(
    "abort_mosaic",
    [pytest.param(False, id="Full set"), pytest.param(True, id="Aborted last mosaic")],
)
def test_science_calibration(science_calibration_task, mocker, fake_gql_client):
    """
    Given: a set of parsed input observe frames, dark and gain calibrations, and a ScienceCalibration task
    When: the task is run
    Then: the science frames are processed, no exposures are averaged, and the array values are correct
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, num_steps, num_exp_per_step, expected_num_mosaic_repeats = science_calibration_task
    task()

    for s in range(1, num_steps + 1):
        tags = [
            VbiTag.calibrated(),
            VbiTag.frame(),
            VbiTag.spatial_step(s),
            VbiTag.stokes("I"),
        ]
        file_list = list(task.read(tags=tags))
        # Make sure any aborted mosaics didn't get processed
        assert len(file_list) == num_exp_per_step * expected_num_mosaic_repeats

        for m in range(1, expected_num_mosaic_repeats + 1):
            sci_access_list = list(
                task.read(
                    tags=tags + [VbiTag.mosaic(m)],
                    decoder=fits_access_decoder,
                    fits_access_class=VbiL0FitsAccess,
                )
            )
            assert len(sci_access_list) == num_exp_per_step
            sorted_access = sorted(sci_access_list, key=lambda x: np.mean(x.data))
            for e, obj in enumerate(sorted_access):
                assert isinstance(obj._hdu, fits.CompImageHDU)
                expected_array = (np.ones((10, 10)) * (e + 1)) + s + (m * 10)
                np.testing.assert_equal(expected_array, obj.data)

    input_obs_frames = list(task.read(tags=[VbiTag.input(), VbiTag.frame(), VbiTag.task_observe()]))

    quality_files = list(task.read(tags=[Tag.quality("TASK_TYPES")]))
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == len(input_obs_frames)
