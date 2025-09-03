import json
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import is_dataclass
from random import randint
from typing import Generator
from typing import Literal

import numpy as np
import pytest
from astropy.io import fits
from dkist_data_simulator.dataset import key_function
from dkist_data_simulator.spec122 import Spec122Dataset
from dkist_header_validator.translator import sanitize_to_spec214_level1
from dkist_header_validator.translator import translate_spec122_to_spec214_l0
from dkist_processing_common.codecs.basemodel import basemodel_encoder
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.models.task_name import TaskName
from dkist_processing_common.tests.mock_metadata_store import fake_gql_client

from dkist_processing_vbi.models.constants import VbiConstants
from dkist_processing_vbi.models.parameters import VbiParameters
from dkist_processing_vbi.models.tags import VbiTag


@pytest.fixture()
def recipe_run_id():
    return randint(0, 99999)


class VbiS122Headers(Spec122Dataset):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        num_steps: int = 4,
        num_exp_per_step: int = 1,
        num_dsps_repeats: int = 5,
        num_mosaics_per_dsps_repeat: int = 1,
        time_delta: float = 10.0,
        instrument: str = "vbi",
        DKIST008_value: int | None = None,
        DKIST009_offset_value: int = 0,
    ):
        if DKIST008_value is None:
            DKIST008_value = num_dsps_repeats
        dataset_shape = (
            num_exp_per_step * num_steps * num_dsps_repeats * num_mosaics_per_dsps_repeat,
        ) + array_shape[-2:]
        super().__init__(
            dataset_shape=dataset_shape,
            array_shape=array_shape,
            time_delta=time_delta,
            instrument=instrument,
        )
        self.num_steps = num_steps
        self.num_exp_per_step = num_exp_per_step
        self.num_dsps_repeats = num_dsps_repeats
        self.num_mosaic_per_dsps_repeat = num_mosaics_per_dsps_repeat
        self.DKIST009_offset = DKIST009_offset_value
        self.add_constant_key("WAVELNTH", 656.282)
        self.add_constant_key("TELSCAN", "None")
        self.add_constant_key("ID___004")
        self.add_constant_key("ID___013")
        self.add_constant_key("CAM__001", "test")
        self.add_constant_key("CAM__002", "test")
        self.add_constant_key("CAM__003", 1)
        self.add_constant_key("CAM__004", 1.0)
        self.add_constant_key("CAM__005", 1.0)
        self.add_constant_key("CAM__006", 1.0)
        self.add_constant_key("CAM__007", 1)
        self.add_constant_key("CAM__008", 1)
        self.add_constant_key("CAM__009", 1)
        self.add_constant_key("CAM__010", 1)
        self.add_constant_key("CAM__011", 1)
        self.add_constant_key("CAM__012", 1)
        self.add_constant_key("CAM__013", 1)
        self.add_constant_key("CAM__014", 1)
        self.add_constant_key("CAM__015", 1)
        self.add_constant_key("CAM__016", 1)
        self.add_constant_key("CAM__017", 1)
        self.add_constant_key("CAM__018", 1)
        self.add_constant_key("CAM__019", 1)
        self.add_constant_key("CAM__020", 1)
        self.add_constant_key("CAM__021", 1)
        self.add_constant_key("CAM__022", 1)
        self.add_constant_key("CAM__023", 1)
        self.add_constant_key("CAM__024", 1)
        self.add_constant_key("CAM__025", 1)
        self.add_constant_key("CAM__026", 1)
        self.add_constant_key("CAM__027", 1)
        self.add_constant_key("CAM__028", 1)
        self.add_constant_key("CAM__029", 1)
        self.add_constant_key("CAM__030", 1)
        self.add_constant_key("CAM__031", 1)
        self.add_constant_key("CAM__032", 1)
        self.add_constant_key("VBI__003", num_steps)
        self.add_constant_key("VBI__007", num_exp_per_step)
        self.add_constant_key("DKIST008", DKIST008_value)

    @key_function("VBI__004")
    def spatial_step(self, key: str) -> int:
        return ((self.index // self.num_exp_per_step) % self.num_steps) + 1

    @key_function("VBI__008")
    def current_dsp_output(self, key: str) -> int:
        return (self.index % self.num_exp_per_step) + 1

    @key_function("DKIST009")
    def dsps_num(self, key: str) -> int:
        return (
            (
                self.index
                // (self.num_steps * self.num_exp_per_step * self.num_mosaic_per_dsps_repeat)
            )
            + 1
            + self.DKIST009_offset
        )


class Vbi122DarkFrames(VbiS122Headers):
    def __init__(self, array_shape: tuple[int, ...], num_steps: int = 4, num_exp_per_step: int = 1):
        super().__init__(
            array_shape, num_steps=num_steps, num_exp_per_step=num_exp_per_step, num_dsps_repeats=1
        )
        self.add_constant_key("DKIST004", TaskName.dark.value)


class Vbi122GainFrames(VbiS122Headers):
    def __init__(self, array_shape: tuple[int, ...], num_steps: int = 4, num_exp_per_step: int = 1):
        super().__init__(
            array_shape, num_steps=num_steps, num_exp_per_step=num_exp_per_step, num_dsps_repeats=1
        )
        self.add_constant_key("DKIST004", TaskName.gain.value)
        self.add_constant_key("PAC__002", "Clear")
        self.add_constant_key("TELSCAN", "Raster")


class Vbi122ObserveFrames(VbiS122Headers):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        num_steps: int = 4,
        num_exp_per_step: int = 1,
        num_dsps_repeats: int = 1,
        num_mosaics_per_dsps_repeat: int = 5,
        DKIST008_value: int | None = None,
        DKIST009_offset_value: int = 0,
        camera_str: Literal["blue", "red", "red_all"] = "red",
    ):
        super().__init__(
            array_shape,
            num_steps=num_steps,
            num_exp_per_step=num_exp_per_step,
            num_dsps_repeats=num_dsps_repeats,
            num_mosaics_per_dsps_repeat=num_mosaics_per_dsps_repeat,
            DKIST008_value=DKIST008_value,
            DKIST009_offset_value=DKIST009_offset_value,
        )
        self.add_constant_key("DKIST004", TaskName.observe.value)
        self.add_constant_key("ID___012", "EXPERIMENT ID")
        if camera_str == "red":
            self.add_constant_key("VBI__002", "1,2,4,3")
        elif camera_str == "red_all":
            self.add_constant_key("VBI__002", "1,2,4,3,5")
        else:
            self.add_constant_key("VBI__002", "5,6,3,2,1,4,7,8,9")


class Vbi122SummitObserveFrames(Vbi122ObserveFrames):
    def __init__(
        self,
        array_shape: tuple[int, ...],
        num_steps: int = 4,
        num_exp_per_step: int = 1,
        num_dsps_repeats: int = 1,
        num_mosaics_per_dsps_repeat: int = 1,
        DKIST008_value: int | None = None,
        DKIST009_offset_value: int = 0,
        camera_str: Literal["blue", "red"] = "red",
    ):
        super().__init__(
            array_shape,
            num_steps=num_steps,
            num_exp_per_step=num_exp_per_step,
            num_dsps_repeats=num_dsps_repeats,
            num_mosaics_per_dsps_repeat=num_mosaics_per_dsps_repeat,
            DKIST008_value=DKIST008_value,
            DKIST009_offset_value=DKIST009_offset_value,
            camera_str=camera_str,
        )
        self.add_constant_key("VBI__005", "SpeckleImaging")


def generate_214_l0_fits_frame(
    s122_header: fits.Header, data: np.ndarray | None = None
) -> fits.HDUList:
    """Convert S122 header into 214 L0"""
    if data is None:
        data = np.ones((1, 10, 10))
    translated_header = translate_spec122_to_spec214_l0(s122_header)
    del translated_header["COMMENT"]
    hdu = fits.PrimaryHDU(data=data, header=fits.Header(translated_header))
    return fits.HDUList([hdu])


def generate_compressed_214_l0_fits_frame(
    s122_header: fits.Header, data: np.ndarray | None = None
) -> fits.HDUList:
    """Convert S122 header into 214 L0"""
    if data is None:
        data = np.ones((1, 10, 10))
    translated_header = translate_spec122_to_spec214_l0(s122_header)
    del translated_header["COMMENT"]
    hdu = fits.CompImageHDU(data=data, header=fits.Header(translated_header))
    return fits.HDUList([fits.PrimaryHDU(), hdu])


def generate_214_l1_fits_frame(
    s122_header: fits.Header, data: np.ndarray | None = None
) -> fits.HDUList:
    """Convert S122 header into 214 L1 only.

    This does NOT include populating all L1 headers, just removing 214 L0 only headers

    NOTE: The stuff you care about will be in hdulist[1]
    """
    l0_s214_hdul = generate_214_l0_fits_frame(s122_header, data)
    l0_header = l0_s214_hdul[0].header
    l0_header["DNAXIS"] = 3
    l0_header["DAAXES"] = 2
    l0_header["DEAXES"] = 1
    l1_header = sanitize_to_spec214_level1(input_headers=l0_header)
    hdu = fits.CompImageHDU(header=l1_header, data=l0_s214_hdul[0].data)

    return fits.HDUList([fits.PrimaryHDU(), hdu])


def ensure_all_inputs_used(header_generator: Generator) -> None:
    try:
        _ = next(header_generator)
        raise ValueError("Did not write all of the input data!")
    except StopIteration:
        return


@pytest.fixture()
def init_vbi_constants_db():
    def constants_maker(recipe_run_id: int, constants_obj):
        if is_dataclass(constants_obj):
            constants_obj = asdict(constants_obj)
        constants = VbiConstants(recipe_run_id=recipe_run_id, task_name="test")
        constants._update(constants_obj)
        return

    return constants_maker


@dataclass
class VbiConstantsDb:
    INSTRUMENT: str = "VBI"
    NUM_MOSAIC_REPEATS: int = 3
    SPATIAL_STEP_PATTERN: str = "5,6,3,2,1,4,7,8,9"
    NUM_SPATIAL_STEPS: int = 4
    DARK_EXPOSURE_TIMES: tuple[float, ...] = (0.01, 1.0, 100.0)
    GAIN_EXPOSURE_TIMES: tuple[float, ...] = (1.0,)
    OBSERVE_EXPOSURE_TIMES: tuple[float, ...] = (0.01,)
    AVERAGE_CADENCE: float = 10.0
    MINIMUM_CADENCE: float = 10.0
    MAXIMUM_CADENCE: float = 10.0
    VARIANCE_CADENCE: float = 0.0
    STOKES_PARAMS: tuple[str] = (
        "I",
        "Q",
        "U",
        "V",
    )  # A tuple because lists aren't allowed on dataclasses
    CONTRIBUTING_PROPOSAL_IDS: tuple[str] = (
        "PROPID1",
        "PROPID2",
    )
    CONTRIBUTING_EXPERIMENT_IDS: tuple[str] = (
        "EXPERID1",
        "EXPERID2",
        "EXPERID3",
    )
    OBS_IP_START_TIME: str = "2022-11-28T13:54:00"


@dataclass
class VbiInputDatasetParameterValues:
    vbi_movie_intensity_clipping_percentile: float = 0.5


@pytest.fixture(scope="session")
def testing_obs_ip_start_time() -> str:
    return "1946-11-20T12:34:56"


@pytest.fixture(scope="session")
def input_dataset_document_simple_parameters_part():
    """Convert a dataclass of parameterValues into an actual input dataset parameters part."""

    def make_input_dataset_parameters_part(parameter_values: dataclass):
        parameters_list = []
        value_id = randint(1000, 2000)
        for pn, pv in asdict(parameter_values).items():
            values = [
                {
                    "parameterValueId": value_id,
                    "parameterValue": json.dumps(pv),
                    "parameterValueStartDate": "1946-11-20",  # Remember Duane Allman
                }
            ]
            parameter = {"parameterName": pn, "parameterValues": values}
            parameters_list.append(parameter)
        return parameters_list

    return make_input_dataset_parameters_part


@pytest.fixture(scope="session")
def assign_input_dataset_doc_to_task(
    input_dataset_document_simple_parameters_part, testing_obs_ip_start_time
):
    def update_task(
        task,
        parameter_values,
        parameter_class=VbiParameters,
        obs_ip_start_time=testing_obs_ip_start_time,
    ):
        task.write(
            data=InputDatasetPartDocumentList(
                doc_list=input_dataset_document_simple_parameters_part(parameter_values)
            ),
            tags=VbiTag.input_dataset_parameters(),
            encoder=basemodel_encoder,
        )
        task.parameters = parameter_class(
            scratch=task.scratch,
            obs_ip_start_time=obs_ip_start_time,
        )

    return update_task
