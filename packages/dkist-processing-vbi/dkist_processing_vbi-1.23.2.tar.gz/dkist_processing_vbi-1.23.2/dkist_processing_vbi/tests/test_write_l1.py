from dataclasses import asdict
from random import randint
from typing import Literal

import numpy as np
import pytest
from astropy.io import fits
from dkist_fits_specifications import __version__ as spec_version
from dkist_header_validator import spec122_validator
from dkist_header_validator import spec214_validator
from dkist_processing_common.codecs.fits import fits_array_encoder
from dkist_processing_common.models.tags import Tag
from dkist_service_configuration.logging import logger

from dkist_processing_vbi.models.constants import VbiConstants
from dkist_processing_vbi.tasks.write_l1 import VbiWriteL1Frame
from dkist_processing_vbi.tests.conftest import Vbi122ObserveFrames
from dkist_processing_vbi.tests.conftest import VbiConstantsDb


@pytest.fixture(scope="function")
def calibrated_header(is_mosaic: bool, camera_str: Literal["red", "blue", "red_all"]):
    ds = Vbi122ObserveFrames(array_shape=(1, 2, 2), num_steps=1, camera_str=camera_str)
    header_list = [
        spec122_validator.validate_and_translate_to_214_l0(d.header(), return_type=fits.HDUList)[
            0
        ].header
        for d in ds
    ]

    header = header_list[0]
    header["CUNIT1"] = "m"
    header["CUNIT2"] = "arcsec"
    header["CUNIT3"] = "s"
    if is_mosaic:
        if camera_str == "blue":
            header["VBINSTP"] = 9
            header["VBISTP"] = 5
        elif camera_str == "red_all":
            header["VBINSTP"] = 5
            header["VBISTP"] = 5
        else:
            header["VBINSTP"] = 4
            header["VBISTP"] = 3
    else:
        header["VBINSTP"] = 1
        header["VBISTP"] = 1
        header["VBISTPAT"] = "5"
    header["VBINFRAM"] = 3
    header["VBICFRAM"] = 2
    header["VBINMOSC"] = 3
    header["VBICMOSC"] = 2
    header["DSPSNUM"] = 1002  # To mimic a large offset
    header["DATE-BEG"] = "2025-07-11T00:00:00"
    header["TEXPOSUR"] = 100
    return header


@pytest.fixture(scope="function")
def write_l1_task(calibrated_header, num_mosaic_repeats, camera_str: Literal["red", "blue"]):
    recipe_run_id = randint(0, 99999)
    spatial_step_pattern = {
        "red": "1, 2, 4, 3",
        "red_all": "1, 2, 4, 3, 5",
        "blue": "5, 6, 3, 2, 1, 4, 7, 8, 9",
    }
    constants_db = VbiConstantsDb(
        AVERAGE_CADENCE=10,
        MINIMUM_CADENCE=10,
        MAXIMUM_CADENCE=10,
        VARIANCE_CADENCE=0,
        NUM_MOSAIC_REPEATS=num_mosaic_repeats,
        SPATIAL_STEP_PATTERN=spatial_step_pattern[camera_str],
    )
    # Repeat ini_vbi_constants fixture here because of a scope conflict
    constants = VbiConstants(recipe_run_id=recipe_run_id, task_name="test")
    constants._update(asdict(constants_db))
    with VbiWriteL1Frame(
        recipe_run_id=recipe_run_id,
        workflow_name="workflow_name",
        workflow_version="workflow_version",
    ) as task:
        # Random data needed so skew and kurtosis don't barf
        data = np.random.random((1, 10, 11)) * 100
        task.write(
            data=data,
            header=calibrated_header,
            tags=[Tag.calibrated(), Tag.frame(), Tag.stokes("I")],
            encoder=fits_array_encoder,
        )
        yield task
        task._purge()


@pytest.mark.parametrize(
    "num_mosaic_repeats", [pytest.param(3, id="Time axis"), pytest.param(1, id="No time axis")]
)
@pytest.mark.parametrize(
    "is_mosaic, camera_str",
    [
        pytest.param(True, "blue", id="BLUE"),
        pytest.param(True, "red", id="RED"),
        pytest.param(True, "red_all", id="RED-ALL"),
        pytest.param(False, "red", id="Non-Mosaic"),
    ],
)
def test_write_l1_frame(
    write_l1_task, num_mosaic_repeats, is_mosaic, camera_str, mocker, fake_gql_client
):
    """
    :Given: a write L1 task
    :When: running the task
    :Then: no errors are raised
    """
    mocker.patch(
        "dkist_processing_common.tasks.mixin.metadata_store.GraphQLClient", new=fake_gql_client
    )
    task = write_l1_task
    task()
    files = list(task.read(tags=[Tag.frame(), Tag.output(), Tag.stokes("I")]))
    assert len(files) == 1
    for file in files:
        logger.info(f"Checking file {file}")
        assert file.exists
        hdl = fits.open(file)
        assert len(hdl) == 2
        header = hdl[1].header
        assert spec214_validator.validate(input_headers=header, extra=False)
        assert header["DNAXIS1"] == 11
        assert header["DNAXIS2"] == 10

        assert header["DTYPE1"] == "SPATIAL"
        assert header["DUNIT1"] == header["CUNIT1"]
        assert header["DWNAME1"] == "helioprojective longitude"
        assert header["DPNAME1"] == "helioprojective longitude"

        assert header["DTYPE2"] == "SPATIAL"
        assert header["DUNIT2"] == header["CUNIT2"]
        assert header["DWNAME2"] == "helioprojective latitude"
        assert header["DPNAME2"] == "helioprojective latitude"

        if num_mosaic_repeats > 1:
            assert header["DEAXES"] == 1
            assert header["DNAXIS3"] == header["VBINFRAM"] * header["VBINMOSC"]
            assert header["DTYPE3"] == "TEMPORAL"
            assert header["DUNIT3"] == "s"
            assert header["DPNAME3"] == "time"
            assert header["DWNAME3"] == "time"
            assert header["DINDEX3"] == 5 if camera_str == "blue" else 3
        else:
            assert header["DEAXES"] == 0
            assert "DNAXIS3" not in header
            assert "DTYPE3" not in header
            assert "DUNIT3" not in header
            assert "DPNAME3" not in header
            assert "DWNAME3" not in header
            assert "DINDEX3" not in header

        if is_mosaic:
            assert header["MAXIS"] == 2
            if camera_str == "blue":
                assert header["MAXIS1"] == 3
                assert header["MAXIS2"] == 3
                assert header["MINDEX1"] == 1  # Because VBISTP = 5 from the fixture, which is
                assert header["MINDEX2"] == 3  # mosaic field #1, which has MINDEX (1, 3)
            elif camera_str == "red_all":
                assert header["MAXIS1"] == 3
                assert header["MAXIS2"] == 3
                assert header["MINDEX1"] == 2  # Because VBISTP = 5 from the fixture, which is
                assert header["MINDEX2"] == 2  # mosaic field #5, which has MINDEX (2, 2)
            else:
                assert header["MAXIS1"] == 2
                assert header["MAXIS2"] == 2
                assert header["MINDEX1"] == 2  # Because VBISTP = 3 from the fixture, which is
                assert header["MINDEX2"] == 1  # mosaic field #4, which has MINDEX (2, 1)
        else:
            assert "MAXIS" not in header
            assert "MAXIS1" not in header
            assert "MAXIS2" not in header
            assert "MINDEX1" not in header
            assert "MINDEX2" not in header

        assert header["WAVEMIN"] == 656.258
        assert header["WAVEMAX"] == 656.306
        assert header["INFO_URL"] == task.docs_base_url
        assert header["HEADVERS"] == spec_version
        assert (
            header["HEAD_URL"] == f"{task.docs_base_url}/projects/data-products/en/v{spec_version}"
        )
        calvers = task.version_from_module_name()
        assert header["CALVERS"] == calvers
        assert (
            header["CAL_URL"]
            == f"{task.docs_base_url}/projects/{task.constants.instrument.lower()}/en/v{calvers}/{task.workflow_name}.html"
        )
        assert header["DATE-END"] == "2025-07-11T00:00:00.100000"
        assert isinstance(header["HLSVERS"], str)
        assert header["PROPID01"] == "PROPID1"
        assert header["PROPID02"] == "PROPID2"
        assert header["EXPRID01"] == "EXPERID1"
        assert header["EXPRID02"] == "EXPERID2"
        assert header["EXPRID03"] == "EXPERID3"
        assert header["WAVEBAND"] == "VBI-Red H-alpha"
        assert header["SPECLN01"] == "H alpha (656.28 nm)"
        with pytest.raises(KeyError):
            header["SPECLN02"]
