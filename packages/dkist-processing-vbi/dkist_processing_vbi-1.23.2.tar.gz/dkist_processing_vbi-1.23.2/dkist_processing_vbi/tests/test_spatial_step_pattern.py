from dataclasses import dataclass

import pytest
from dkist_processing_common.models.task_name import TaskName

from dkist_processing_vbi.models.constants import VbiBudName
from dkist_processing_vbi.parsers.spatial_step_pattern import SpatialStepPatternBud


@dataclass
class DummyFitsAccess:
    spatial_step_pattern: str
    ip_task_type: str = TaskName.observe.value


@pytest.fixture
def fits_objs_with_spatial_step_pattern(spatial_step_patterns):
    if not isinstance(spatial_step_patterns, list):
        spatial_step_patterns = [spatial_step_patterns]
    return [DummyFitsAccess(pattern) for pattern in spatial_step_patterns]


@pytest.mark.parametrize(
    "spatial_step_patterns, expected_pattern",
    [
        pytest.param(["1,2,4,3", "1,2,4,3"], "1,2,4,3", id="RED"),
        pytest.param(
            ["5, 6, 3, 2, 1, 4, 7, 8, 9", "5, 6, 3, 2, 1, 4, 7, 8, 9"],
            "5, 6, 3, 2, 1, 4, 7, 8, 9",
            id="BLUE",
        ),
        pytest.param(["1, 2, 4, 3, 5"], "1, 2, 4, 3, 5", id="RED_ALL"),
        pytest.param(["5", "5"], "5", id="SINGLE"),
        pytest.param("1,2,3,4", "1,2,3,4", id="Single_frame"),
    ],
)
def test_spatial_step_pattern_bud_valid(fits_objs_with_spatial_step_pattern, expected_pattern):
    """
    Given: A SpatialStepPatternBud and a set of valid FitsAccess objects
    When: Ingesting the objects into the Bud
    Then: The correct `.bud` value is returned
    """
    Bud = SpatialStepPatternBud()
    for i, fits_obj in enumerate(fits_objs_with_spatial_step_pattern):
        Bud.update(f"file{i}", fits_obj)

    assert Bud.bud.value == expected_pattern


@pytest.mark.parametrize(
    "spatial_step_patterns, expected_error_msg",
    [
        pytest.param(
            ["1,2,4,3", "4,3,2,1"],
            f"Multiple {VbiBudName.spatial_step_pattern.value} values found",
            id="Not_unique",
        ),
        pytest.param(
            ["1,2,3"],
            "does not represent either a 1x1, 2x2, 3x3 mosaic, or a 5-step raster. We don't know how to deal with this",
            id="Bad_mosaic",
        ),
        pytest.param(
            [""],
            "does not represent either a 1x1, 2x2, 3x3 mosaic, or a 5-step raster. We don't know how to deal with this",
            id="Empty",
        ),
    ],
)
def test_spatial_step_pattern_bud_invalid(fits_objs_with_spatial_step_pattern, expected_error_msg):
    """
    Given: A SpatialStepPatternBud and a set of invalid FitsAccess objects
    When: Ingesting the objects into the Bud and accessing the `.bud`
    Then: The correct Error is raised
    """
    Bud = SpatialStepPatternBud()
    for i, fits_obj in enumerate(fits_objs_with_spatial_step_pattern):
        Bud.update(f"file{i}", fits_obj)

    with pytest.raises(ValueError, match=expected_error_msg):
        _ = Bud.bud.value
