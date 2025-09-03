import json

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.tags import Tag
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.quality_metrics import VbiQualityL0Metrics
from dkist_processing_vbi.tasks.quality_metrics import VbiQualityL1Metrics
from dkist_processing_vbi.tests.conftest import VbiConstantsDb


class BaseSpec214Dataset(Spec122Dataset):
    def __init__(self, instrument="vbi"):
        self.array_shape = (1, 10, 10)
        super().__init__(
            dataset_shape=(2, 10, 10),
            array_shape=self.array_shape,
            time_delta=1,
            instrument=instrument,
            file_schema="level0_spec214",
        )


@pytest.fixture
def vbi_l0_quality_task(recipe_run_id, tmp_path):

    with VbiQualityL0Metrics(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)

        yield task
        task._purge()


@pytest.fixture()
def l0_quality_task_types() -> list[str]:
    # The tasks types we want to build l0 metrics for
    return [TaskName.lamp_gain.value, TaskName.dark.value]


@pytest.fixture()
def dataset_task_types(l0_quality_task_types) -> list[str]:
    # The task types that exist in the dataset. I.e., a larger set than we want to build metrics for.
    return l0_quality_task_types + [TaskName.solar_gain.value, TaskName.observe.value]


@pytest.fixture
def write_l0_task_frames_to_task(dataset_task_types):
    def writer(task):
        for task_type in dataset_task_types:
            ds = BaseSpec214Dataset()
            for modstate, frame in enumerate(ds, start=1):
                header = frame.header()
                data = np.ones(ds.array_shape)
                task.write(
                    data=data,
                    header=header,
                    tags=[
                        VbiTag.input(),
                        VbiTag.frame(),
                        VbiTag.task(task_type),
                    ],
                    encoder=fits_array_encoder,
                )

    return writer


def test_l0_quality_task(vbi_l0_quality_task, write_l0_task_frames_to_task, l0_quality_task_types):
    """
    Given: A `VbiQualityL0Metrics` task and some INPUT frames tagged with their task type and modstate
    When: Running the task
    Then: The expected L0 quality metric files exist
    """
    # NOTE: We rely on the unit tests in `*-common` to verify the correct format/data of the metric files
    task = vbi_l0_quality_task
    write_l0_task_frames_to_task(task)

    task()

    task_metric_names = ["FRAME_RMS", "FRAME_AVERAGE"]
    for metric_name in task_metric_names:
        for task_type in l0_quality_task_types:
            tags = [VbiTag.quality(metric_name), VbiTag.quality_task(task_type)]
            files = list(task.read(tags))
            assert len(files) == 1

    global_metric_names = ["DATASET_AVERAGE", "DATASET_RMS"]
    for metric_name in global_metric_names:
        files = list(task.read(tags=[VbiTag.quality(metric_name)]))
        assert len(files) > 0


@pytest.fixture
def vbi_l1_quality_task(tmp_path, recipe_run_id, init_vbi_constants_db):
    constants_db = VbiConstantsDb()
    init_vbi_constants_db(recipe_run_id, constants_db)
    with VbiQualityL1Metrics(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        for i in range(10):
            header_dict = [
                d.header(required_only=False, expected_only=False) for d in BaseSpec214Dataset()
            ][0]
            data = np.ones(shape=BaseSpec214Dataset().array_shape)
            task.write(
                data=data,
                header=fits.Header(header_dict),
                tags=[Tag.calibrated(), Tag.frame()],
                encoder=fits_array_encoder,
            )
        yield task
    task._purge()


def test_noise(vbi_l1_quality_task):
    """
    Given: a task with the QualityL1Metrics class
    When: checking that the noise metric was created and stored correctly
    Then: the metric is encoded as a json object, which when opened contains a dictionary with the expected schema
    """
    task = vbi_l1_quality_task
    task()
    files = list(task.read(tags=Tag.quality("NOISE")))
    for file in files:
        with file.open() as f:
            data = json.load(f)
            assert isinstance(data, dict)
            assert all(isinstance(item, str) for item in data["x_values"])
            assert all(isinstance(item, float) for item in data["y_values"])
