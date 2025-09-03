import json

import numpy as np
import pytest
from astropy.io import fits
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.tags import Tag

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.dark import DarkCalibration
from dkist_processing_vbi.tests.conftest import Vbi122DarkFrames
from dkist_processing_vbi.tests.conftest import VbiConstantsDb
from dkist_processing_vbi.tests.conftest import ensure_all_inputs_used


@pytest.fixture(scope="function")
def dark_calibration_task(tmp_path, recipe_run_id, init_vbi_constants_db):
    num_steps = 4
    gain_exp_time = 1.0
    obs_exp_time = 0.01
    unused_time = 100.0
    dark_exp_times = (gain_exp_time, obs_exp_time, unused_time)
    constants_db = VbiConstantsDb(
        NUM_SPATIAL_STEPS=num_steps,
        DARK_EXPOSURE_TIMES=dark_exp_times,
        GAIN_EXPOSURE_TIMES=(gain_exp_time,),
        OBSERVE_EXPOSURE_TIMES=(obs_exp_time,),
    )
    init_vbi_constants_db(recipe_run_id, constants_db)
    with DarkCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_dark_calibration",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_steps = num_steps
        task.num_exp_per_step = 3
        task.exp_times = [gain_exp_time, obs_exp_time]
        task.unused_time = unused_time
        for exp in task.exp_times + [task.unused_time]:
            ds = Vbi122DarkFrames(
                array_shape=(1, 10, 10),
                num_steps=task.num_steps,
                num_exp_per_step=task.num_exp_per_step,
            )
            header_generator = (d.header() for d in ds)
            for p in range(1, task.num_steps + 1):
                for e in range(task.num_exp_per_step):
                    header = fits.Header(next(header_generator))
                    data = (np.ones((1, 10, 10)) * (e + 1)) * 10.0**p * exp * 10
                    task.write(
                        data=data,
                        header=header,
                        tags=[
                            VbiTag.input(),
                            VbiTag.task_dark_frame(spatial_step=p, exposure_time=exp),
                        ],
                        encoder=fits_array_encoder,
                    )
            ensure_all_inputs_used(header_generator)
        yield task
        task._purge()


def test_dark_calibration_task(dark_calibration_task, mocker, fake_gql_client):
    """
    Given: a set of parsed input dark frames and a DarkCalibration task
    When: running the task
    Then: a single output array is produced for each spatial step and the array values are correct
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    dark_calibration_task()

    for exp in dark_calibration_task.exp_times:
        for p in range(1, dark_calibration_task.num_steps + 1):
            data_list = list(
                dark_calibration_task.read(
                    tags=[
                        VbiTag.intermediate(),
                        VbiTag.task_dark_frame(spatial_step=p, exposure_time=exp),
                    ],
                    decoder=fits_array_decoder,
                )
            )
            assert len(data_list) == 1
            expected_array = np.ones((10, 10)) * 2 * 10.0**p * exp * 10
            np.testing.assert_equal(expected_array, data_list[0])

    unused_time_read = dark_calibration_task.read(
        tags=[
            VbiTag.intermediate(),
            VbiTag.task_dark_frame(exposure_time=dark_calibration_task.unused_time),
        ]
    )
    assert len(list(unused_time_read)) == 0

    num_darks = dark_calibration_task.count(tags=[VbiTag.input(), VbiTag.task_dark_frame()])

    quality_files = list(dark_calibration_task.read(tags=[Tag.quality("TASK_TYPES")]))
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == num_darks
            assert (
                data["frames_not_used"]
                == dark_calibration_task.num_steps * dark_calibration_task.num_exp_per_step
            )
