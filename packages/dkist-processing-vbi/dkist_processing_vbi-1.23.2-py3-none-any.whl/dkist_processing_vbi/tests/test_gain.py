import json

import numpy as np
import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_decoder
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.tags import Tag

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.gain import GainCalibration
from dkist_processing_vbi.tests.conftest import Vbi122GainFrames
from dkist_processing_vbi.tests.conftest import VbiConstantsDb
from dkist_processing_vbi.tests.conftest import ensure_all_inputs_used
from dkist_processing_vbi.tests.conftest import generate_214_l0_fits_frame


@pytest.fixture(scope="function")
def gain_calibration_task(tmp_path, recipe_run_id, init_vbi_constants_db):
    num_steps = 4
    exp_time = 2.3
    constants_db = VbiConstantsDb(NUM_SPATIAL_STEPS=num_steps, GAIN_EXPOSURE_TIMES=(exp_time,))
    init_vbi_constants_db(recipe_run_id, constants_db)
    with GainCalibration(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_gain_calibration",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_steps = num_steps
        task.num_exp_per_step = 3
        ds = Vbi122GainFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
        )
        header_generator = (d.header() for d in ds)
        for s in range(1, task.num_steps + 1):
            for e in range(task.num_exp_per_step):
                header = next(header_generator)
                data = (np.ones((1, 10, 10)) * (e + 1)) + s + (s * 10)
                hdul = generate_214_l0_fits_frame(s122_header=header, data=data)
                task.write(
                    data=hdul,
                    tags=[
                        VbiTag.input(),
                        VbiTag.task_gain_frame(spatial_step=s, exposure_time=exp_time),
                    ],
                    encoder=fits_hdulist_encoder,
                )

            dark_cal = np.zeros((1, 10, 10)) + (s * 10)
            task.write(
                data=dark_cal,
                tags=[
                    VbiTag.intermediate(),
                    VbiTag.task_dark_frame(spatial_step=s, exposure_time=exp_time),
                ],
                encoder=fits_array_encoder,
            )
        ensure_all_inputs_used(header_generator)
        yield task
        task._purge()


def test_gain_calibration(gain_calibration_task, mocker, fake_gql_client):
    """
    Given: a set of parsed input gain frames, dark calibration frames, and a GainCalibration task
    When: the task is run
    Then: a single array is produced for each step and the array values are correctly normalized
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    gain_calibration_task()

    correct_mean = np.mean(np.arange(1, gain_calibration_task.num_steps + 1) + 2)
    for s in range(1, gain_calibration_task.num_steps + 1):
        gain_array_list = list(
            gain_calibration_task.read(
                tags=[
                    VbiTag.intermediate(),
                    VbiTag.task_gain_frame(spatial_step=s),
                ],
                decoder=fits_array_decoder,
            )
        )
        assert len(gain_array_list) == 1
        expected_array = (np.ones((10, 10)) * 2 + s) / correct_mean
        np.testing.assert_equal(expected_array, gain_array_list[0])

    input_gain_frames = list(
        gain_calibration_task.read(tags=[VbiTag.input(), VbiTag.task_gain_frame()])
    )

    quality_files = list(gain_calibration_task.read(tags=[Tag.quality("TASK_TYPES")]))
    for file in quality_files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert data["total_frames"] == len(input_gain_frames)
