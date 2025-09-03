from itertools import chain

import pytest
from dkist_processing_common._util.scratch import WorkflowFileSystem
from dkist_processing_common.codecs.fits import fits_hdulist_encoder
from dkist_processing_common.models.constants import BudName

from dkist_processing_vbi.models.constants import VbiBudName
from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.parse import ParseL0VbiInputData
from dkist_processing_vbi.tests.conftest import Vbi122DarkFrames
from dkist_processing_vbi.tests.conftest import Vbi122GainFrames
from dkist_processing_vbi.tests.conftest import Vbi122ObserveFrames
from dkist_processing_vbi.tests.conftest import generate_214_l0_fits_frame


@pytest.fixture(scope="function")
def parse_inputs_task(tmp_path, recipe_run_id):
    with ParseL0VbiInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_parse_l0_inputs",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_program_types = 3
        task.num_steps = 4
        task.num_exp_per_step = 3
        task.test_num_mosaic_repeats = 2
        ds1 = Vbi122DarkFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=1,
        )
        ds2 = Vbi122GainFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=1,
        )
        ds3 = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.test_num_mosaic_repeats,
            num_mosaics_per_dsps_repeat=1,  # No subrepeats
            camera_str="red",
        )
        ds = chain(ds1, ds2, ds3)
        header_generator = (d.header() for d in ds)
        for header in header_generator:
            hdul = generate_214_l0_fits_frame(s122_header=header)
            task.write(
                data=hdul, tags=[VbiTag.input(), VbiTag.frame()], encoder=fits_hdulist_encoder
            )
        yield task
        task._purge()


@pytest.fixture(
    scope="function", params=[pytest.param("red"), pytest.param("blue"), pytest.param("red_all")]
)
def parse_inputs_task_with_only_observe(tmp_path, recipe_run_id, request):
    camera_str = request.param
    with ParseL0VbiInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_parse_l0_inputs",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_program_types = 3
        task.num_steps = 4
        task.num_exp_per_step = 1
        task.test_num_mosaic_repeats = 2
        ds = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.test_num_mosaic_repeats,
            num_mosaics_per_dsps_repeat=1,  # No subrepeats
            camera_str=camera_str,
        )
        header_generator = (d.header() for d in ds)
        for header in header_generator:
            hdul = generate_214_l0_fits_frame(s122_header=header)
            task.write(
                data=hdul, tags=[VbiTag.input(), VbiTag.frame()], encoder=fits_hdulist_encoder
            )
        yield task, camera_str
        task._purge()


@pytest.fixture(scope="function")
def parse_inputs_task_with_subrepeats(tmp_path, recipe_run_id):
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
        ds = Vbi122ObserveFrames(
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


@pytest.fixture(scope="function")
def parse_inputs_task_with_out_of_sequence_DSPSNUMS(tmp_path, recipe_run_id):
    with ParseL0VbiInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_parse_l0_inputs",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        task.num_steps = 4
        task.num_exp_per_step = 1
        task.test_num_mosaic_repeats = 4
        ds = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=task.num_steps,
            num_exp_per_step=task.num_exp_per_step,
            num_dsps_repeats=task.test_num_mosaic_repeats,
            num_mosaics_per_dsps_repeat=1,  # No subrepeats
        )
        header_generator = (d.header() for d in ds)
        for i, header in enumerate(header_generator):
            if header["DKIST009"] == 1003:
                # Skip the 3rd frame (this needs to not be the last one; that would be an aborted last mosaic)
                continue
            hdul = generate_214_l0_fits_frame(s122_header=header)
            task.write(
                data=hdul, tags=[VbiTag.input(), VbiTag.frame()], encoder=fits_hdulist_encoder
            )
        yield task
        task._purge()


@pytest.fixture(scope="function")
def parse_inputs_task_with_aborted_last_mosaic(tmp_path, recipe_run_id):
    num_steps = 4
    num_exp_per_step = 3
    num_mosaic_repeats = 4
    with ParseL0VbiInputData(
        recipe_run_id=recipe_run_id,
        workflow_name="vbi_parse_l0_inputs",
        workflow_version="VX.Y",
    ) as task:
        task.scratch = WorkflowFileSystem(scratch_base_path=tmp_path, recipe_run_id=recipe_run_id)
        ds = Vbi122ObserveFrames(
            array_shape=(1, 10, 10),
            num_steps=num_steps,
            num_exp_per_step=num_exp_per_step,
            num_dsps_repeats=num_mosaic_repeats,
            num_mosaics_per_dsps_repeat=1,  # No subrepeats
        )
        header_generator = (d.header() for d in ds)
        for i, header in enumerate(header_generator):
            if header["DKIST009"] == num_mosaic_repeats and header["VBI__004"] > num_steps - 2:
                # Skip the last 2 mosaic steps of the last repeat
                continue
            hdul = generate_214_l0_fits_frame(s122_header=header)
            task.write(
                data=hdul, tags=[VbiTag.input(), VbiTag.frame()], encoder=fits_hdulist_encoder
            )
        yield task, num_mosaic_repeats - 1
        task._purge()


def test_parse_l0_input_data_spatial_pos(parse_inputs_task, mocker, fake_gql_client):
    """
    Given: a set of raw inputs of multiple task types and a ParseL0VbiInputData task
    When: the task is run
    Then: the input frames are correctly tagged by spatial position
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    parse_inputs_task()

    for step in range(1, parse_inputs_task.num_steps + 1):
        translated_files = list(
            parse_inputs_task.read(tags=[VbiTag.input(), VbiTag.frame(), VbiTag.spatial_step(step)])
        )
        assert (
            len(translated_files)
            == (parse_inputs_task.num_program_types - 1)  # for non observe frames
            + parse_inputs_task.num_exp_per_step
            * parse_inputs_task.constants._db_dict[
                VbiBudName.num_mosaics_repeats.value
            ]  # for observe frames
        )
        for filepath in translated_files:
            assert filepath.exists()


def test_parse_l0_input_constants(parse_inputs_task, mocker, fake_gql_client):
    """
    Given: a set of raw inputs of multiple task types and a ParseL0VbiInputData task
    When: the task is run
    Then: pipeline constants are correctly updated from the input headers
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    parse_inputs_task()

    assert (
        parse_inputs_task.constants._db_dict[VbiBudName.num_spatial_steps.value]
        == parse_inputs_task.num_steps
    )
    assert (
        parse_inputs_task.constants._db_dict[VbiBudName.num_mosaics_repeats.value]
        == parse_inputs_task.test_num_mosaic_repeats
    )
    assert parse_inputs_task.constants._db_dict[VbiBudName.spatial_step_pattern.value] == "1,2,4,3"
    assert BudName.obs_ip_start_time.value in parse_inputs_task.constants._db_dict


def test_parse_l0_input_frames_found(parse_inputs_task, mocker, fake_gql_client):
    """
    Given: a set of raw inputs of multiple task types and a ParseL0VbiInputData task
    When: the task is run
    Then: the frames from each task type are correctly identified and tagged
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    parse_inputs_task()
    assert (
        len(list(parse_inputs_task.read(tags=[VbiTag.input(), VbiTag.task_dark()])))
        == parse_inputs_task.num_steps
    )
    assert (
        len(list(parse_inputs_task.read(tags=[VbiTag.input(), VbiTag.task_gain()])))
        == parse_inputs_task.num_steps
    )

    assert (
        len(list(parse_inputs_task.read(tags=[VbiTag.input(), VbiTag.task_observe()])))
        == parse_inputs_task.num_steps
        * parse_inputs_task.num_exp_per_step
        * parse_inputs_task.test_num_mosaic_repeats
    )


def test_parse_l0_input_with_only_observe(
    parse_inputs_task_with_only_observe, mocker, fake_gql_client
):
    """
    Given: a set of raw inputs of a single task type and a ParseL0VbiInputData task
    When: the task is run
    Then: the observe frames are correctly identified and tagged
    """
    task, camera_str = parse_inputs_task_with_only_observe
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task()
    if camera_str == "red":
        assert task.constants._db_dict[VbiBudName.spatial_step_pattern.value] == "1,2,4,3"
    elif camera_str == "red_all":
        assert task.constants._db_dict[VbiBudName.spatial_step_pattern.value] == "1,2,4,3,5"
    else:
        assert task.constants._db_dict[VbiBudName.spatial_step_pattern.value] == "5,6,3,2,1,4,7,8,9"
    for mosaic_repeat in range(1, task.test_num_mosaic_repeats + 1):
        for step in range(1, task.num_steps + 1):
            translated_files = list(
                task.read(
                    tags=[
                        VbiTag.input(),
                        VbiTag.frame(),
                        VbiTag.task_observe(),
                        VbiTag.spatial_step(step),
                        VbiTag.mosaic(mosaic_repeat),
                    ]
                )
            )
            assert len(translated_files) == task.num_exp_per_step
            for filepath in translated_files:
                assert filepath.exists()


def test_parse_l0_aborted_last_mosaic(
    parse_inputs_task_with_aborted_last_mosaic, mocker, fake_gql_client
):
    """
    Given: a set of raw inputs representing a dataset with an aborted last mosaic
    When: the task is run
    Then: pipeline constants are correctly updated from the input headers
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task, expected_num_mosaic_repeats = parse_inputs_task_with_aborted_last_mosaic
    task()

    assert (
        task.constants._db_dict[VbiBudName.num_mosaics_repeats.value] == expected_num_mosaic_repeats
    )


def test_parse_l0_correctly_tagged_mosaic_subrepeats(
    parse_inputs_task_with_subrepeats, mocker, fake_gql_client
):
    """
    Given: A set of observe frames taken with subrepeats (i.e., multiple mosaics per DSPS repeat)
    When: the parse task is run
    Then: pipeline constants are correctly updated and the correct
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = parse_inputs_task_with_subrepeats
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
