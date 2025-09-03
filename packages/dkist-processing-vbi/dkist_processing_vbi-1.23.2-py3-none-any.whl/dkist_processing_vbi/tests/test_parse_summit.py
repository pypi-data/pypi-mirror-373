"""
This might be a totally redundant test. Leave it in for now.
"""

from itertools import chain

import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_hdulist_encoder

from dkist_processing_vbi.models.constants import VbiBudName
from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.parse import ParseL0VbiInputData
from dkist_processing_vbi.tests.conftest import Vbi122DarkFrames
from dkist_processing_vbi.tests.conftest import Vbi122SummitObserveFrames
from dkist_processing_vbi.tests.conftest import generate_214_l0_fits_frame


@pytest.fixture(scope="function")
def parse_summit_processed_task(tmp_path, recipe_run_id):
    with ParseL0VbiInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_parse_summit_processed",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_steps = 4
        task.num_exp_per_step = 1
        task.test_num_mosaic_repeats = 1
        ds0 = Vbi122SummitObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.test_num_mosaic_repeats,
            num_mosaics_per_dsps_repeat=1,  # No subrepeats
        )
        ds1 = Vbi122DarkFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
        )
        ds = chain(ds0, ds1)
        header_generator = (d.header() for d in ds)
        for header in header_generator:
            hdul = generate_214_l0_fits_frame(s122_header=header)
            task.write(
                data=hdul, tags=[VbiTag.input(), VbiTag.frame()], encoder=fits_hdulist_encoder
            )
        yield task
        task._purge()


@pytest.fixture(scope="function")
def parse_summit_task_with_subrepeats(tmp_path, recipe_run_id):
    with ParseL0VbiInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_parse_l0_inputs",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_program_types = 3
        task.num_steps = 4
        task.num_exp_per_step = 1
        task.test_num_mosaic_repeats = 4
        task.test_num_dsps_repeats = 2
        ds = Vbi122SummitObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.test_num_dsps_repeats,
            num_mosaics_per_dsps_repeat=task.test_num_mosaic_repeats // task.test_num_dsps_repeats,
        )
        header_generator = (d.header() for d in ds)
        for header in header_generator:
            hdul = generate_214_l0_fits_frame(s122_header=header)
            task.write(
                data=hdul, tags=[VbiTag.input(), VbiTag.frame()], encoder=fits_hdulist_encoder
            )
        yield task
        task._purge()


def test_parse_summit_proccessed_data(parse_summit_processed_task, mocker, fake_gql_client):
    """
    Given: a set of raw inputs of summit-processed data and a ParseL0VbiInputData task
    When: the task is run
    Then: the observe frames are correctly identified and tagged
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    parse_summit_processed_task()

    for mosaic in range(1, parse_summit_processed_task.test_num_mosaic_repeats + 1):
        for step in range(1, parse_summit_processed_task.num_steps + 1):
            translated_files = list(
                parse_summit_processed_task.read(
                    tags=[
                        VbiTag.input(),
                        VbiTag.frame(),
                        VbiTag.task_observe(),
                        VbiTag.spatial_step(step),
                        VbiTag.mosaic(mosaic),
                    ]
                )
            )
            assert len(translated_files) == parse_summit_processed_task.num_exp_per_step
            for filepath in translated_files:
                assert filepath.exists()


def test_parse_summit_correctly_tagged_mosaic_subrepeats(
    parse_summit_task_with_subrepeats, mocker, fake_gql_client
):
    """
    Given: A set of observe frames taken with subrepeats (i.e., multiple mosaics per DSPS repeat)
    When: the parse task is run
    Then: pipeline constants are correctly updated and the correct
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = parse_summit_task_with_subrepeats
    task()

    found_num_mosaic_repeats = task.constants._db_dict[VbiBudName.num_mosaics_repeats.value]
    assert found_num_mosaic_repeats == task.test_num_mosaic_repeats
    for mosaic in range(1, found_num_mosaic_repeats + 1):
        for step in range(1, task.num_steps + 1):
            file_list = list(
                task.read(
                    tags=[
                        VbiTag.input(),
                        VbiTag.frame(),
                        VbiTag.task_observe(),
                        VbiTag.spatial_step(step),
                        VbiTag.mosaic(mosaic),
                    ],
                )
            )
            assert len(file_list) == task.num_exp_per_step
            for f in file_list:
                assert f.exists()
