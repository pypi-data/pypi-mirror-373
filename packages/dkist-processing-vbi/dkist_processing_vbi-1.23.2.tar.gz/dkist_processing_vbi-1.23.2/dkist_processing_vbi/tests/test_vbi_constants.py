import re
from dataclasses import asdict

import pytest

from dkist_processing_vbi.models.constants import VbiBudName
from dkist_processing_vbi.models.constants import VbiConstants
from dkist_processing_vbi.tasks.vbi_base import VbiTaskBase
from dkist_processing_vbi.tests.conftest import VbiConstantsDb


@pytest.fixture(scope="session")
def expected_constant_dict() -> dict:
    lower_dict = asdict(VbiConstantsDb())
    return {k.upper(): v for k, v in lower_dict.items()}


@pytest.fixture(scope="function")
def vbi_science_task_with_constants(expected_constant_dict, recipe_run_id):
    class Task(VbiTaskBase):
        def run(self): ...

    task = Task(
        recipe_run_id=recipe_run_id,
        workflow_name="test_vbi_constants",
        workflow_version="VX.Y",
    )
    task.constants._update(expected_constant_dict)

    yield task

    task._purge()


def test_vbi_constants(vbi_science_task_with_constants, expected_constant_dict):
    """
    Given: A VbiScienceTask with a constants attribute
    When: Accessing specific constants
    Then: The correct values are returned
    """
    task = vbi_science_task_with_constants
    for k, v in expected_constant_dict.items():
        if k == VbiBudName.spatial_step_pattern.value:
            continue
        if type(v) is tuple:
            v = list(v)  # Because dataclass

        raw_val = getattr(task.constants, k.lower())
        if type(raw_val) is tuple:
            raw_val = list(raw_val)  # Because dataclass

        assert raw_val == v

    assert task.constants.spatial_step_pattern == [5, 6, 3, 2, 1, 4, 7, 8, 9]
    assert task.constants.mindices_of_mosaic_field_positions == [
        "index_placeholder",
        (1, 3),
        (2, 3),
        (3, 3),
        (1, 2),
        (2, 2),
        (3, 2),
        (1, 1),
        (2, 1),
        (3, 1),
    ]


@pytest.mark.parametrize(
    "constants_dict, expected_spatial_step_pattern, expected_mindices",
    [
        pytest.param(
            {VbiBudName.spatial_step_pattern.value: "1,2,4,3"},
            [1, 2, 4, 3],
            [
                "index_placeholder",
                (1, 2),
                (2, 2),
                (1, 1),
                (2, 1),
            ],
            id="RED",
        ),
        pytest.param(
            {VbiBudName.spatial_step_pattern.value: "5,6,3,2,1,4,7,8,9"},
            [5, 6, 3, 2, 1, 4, 7, 8, 9],
            [
                "index_placeholder",
                (1, 3),
                (2, 3),
                (3, 3),
                (1, 2),
                (2, 2),
                (3, 2),
                (1, 1),
                (2, 1),
                (3, 1),
            ],
            id="BLUE",
        ),
        pytest.param(
            {VbiBudName.spatial_step_pattern.value: "5"},
            [5],
            [
                "index_placeholder",
                "index_placeholder",
                "index_placeholder",
                "index_placeholder",
                "index_placeholder",
                (1, 1),
            ],
            id="SINGLE",
        ),
    ],
)
def test_mindices_constants(
    recipe_run_id, constants_dict, expected_spatial_step_pattern, expected_mindices
):
    """
    Given: Constants with various spatial_step_pattern values
    When: Accessing the `spatial_step_pattern` and `minidices_of_mosaic_field_positions`
    Then: The correct values are returned
    """
    constants = VbiConstants(recipe_run_id=recipe_run_id, task_name="test_constants")
    constants._update(constants_dict)
    assert constants.spatial_step_pattern == expected_spatial_step_pattern
    assert constants.mindices_of_mosaic_field_positions == expected_mindices


def test_mindices_invalid(recipe_run_id):
    """
    Given: Constants with a spatial step pattern describing a wonky mosaic
    When: Accessing the `minidices_of_mosaic_field_positions` constant
    Then: An error is raised
    """
    constants = VbiConstants(recipe_run_id=recipe_run_id, task_name="test_constants")
    constants._update({VbiBudName.spatial_step_pattern.value: "1, 2, 3"})
    with pytest.raises(
        ValueError,
        match=re.escape(
            "Spatial step pattern [1, 2, 3] describes an unknown mosaic. Parsing should have caught this."
        ),
    ):
        _ = constants.mindices_of_mosaic_field_positions
