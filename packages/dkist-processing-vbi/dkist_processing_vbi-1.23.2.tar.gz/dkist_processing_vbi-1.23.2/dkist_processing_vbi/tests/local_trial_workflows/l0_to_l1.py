import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from random import randint

import numpy as np
from astropy.io import fits
from dkist_header_validator import spec122_validator
from dkist_header_validator import spec214_validator
from dkist_processing_common.codecs.basemodel import basemodel_encoder
from dkist_processing_common.manual import ManualProcessing
from dkist_processing_common.models.input_dataset import InputDatasetPartDocumentList
from dkist_processing_common.tasks import AssembleQualityData
from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialQualityReport
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import WorkflowTaskBase
from dkist_service_configuration.logging import logger

from dkist_processing_vbi.models.tags import VbiTag
from dkist_processing_vbi.tasks.assemble_movie import AssembleVbiMovie
from dkist_processing_vbi.tasks.dark import DarkCalibration
from dkist_processing_vbi.tasks.gain import GainCalibration
from dkist_processing_vbi.tasks.make_movie_frames import MakeVbiMovieFrames
from dkist_processing_vbi.tasks.parse import ParseL0VbiInputData
from dkist_processing_vbi.tasks.process_summit_processed import GenerateL1SummitData
from dkist_processing_vbi.tasks.quality_metrics import VbiQualityL0Metrics
from dkist_processing_vbi.tasks.quality_metrics import VbiQualityL1Metrics
from dkist_processing_vbi.tasks.science import ScienceCalibration
from dkist_processing_vbi.tasks.vbi_base import VbiTaskBase
from dkist_processing_vbi.tasks.write_l1 import VbiWriteL1Frame
from dkist_processing_vbi.tests.conftest import VbiInputDatasetParameterValues

INV = False
try:
    from dkist_inventory.asdf_generator import dataset_from_fits

    INV = True
except ModuleNotFoundError:
    logger.warning(
        "Could not load dkist-inventory. CreateTrialDatasetInventory and CreateTrialAsdf require dkist-inventory."
    )
    pass

QUALITY = False
try:
    import dkist_quality

    QUALITY = True
except ModuleNotFoundError:
    logger.warning("Could not load dkist-quality. CreateTrialQualityReport requires dkist-quality.")

if QUALITY:
    import matplotlib.pyplot as plt

    plt.ioff()


def tag_inputs_task(suffix: str):
    class TagInputs(WorkflowTaskBase):
        def run(self) -> None:
            logger.info(f"Looking in {os.path.abspath(self.scratch.workflow_base_path)}")
            for file in self.scratch.workflow_base_path.glob(f"*.{suffix}"):
                logger.info(f"Found {file}")
                self.tag(path=file, tags=[VbiTag.input(), VbiTag.frame()])

    return TagInputs


def translate_task(summit_processed: bool = False, suffix: str = "FITS"):
    class Translate122To214L0(WorkflowTaskBase):
        def run(self) -> None:
            raw_dir = Path(self.scratch.scratch_base_path) / f"VBI{self.recipe_run_id:03n}"
            if not os.path.exists(self.scratch.workflow_base_path):
                os.makedirs(self.scratch.workflow_base_path)
            for file in raw_dir.glob(f"*.{suffix}"):
                translated_file_name = Path(self.scratch.workflow_base_path) / os.path.basename(
                    file
                )
                logger.info(f"Translating and compressing {file} -> {translated_file_name}")
                hdl = fits.open(file)
                data = hdl[0].data
                if summit_processed:
                    data = data.astype(np.float32)
                header = spec122_validator.validate_and_translate_to_214_l0(
                    hdl[0].header, return_type=fits.HDUList
                )[0].header
                trans_hdl = fits.HDUList(
                    [fits.PrimaryHDU(), fits.CompImageHDU(data=data, header=header)]
                )

                trans_hdl.writeto(translated_file_name, overwrite=True)
                hdl.close()
                trans_hdl.close()
                del hdl, trans_hdl

    return Translate122To214L0


class CreateInputDatasetParameterDocument(WorkflowTaskBase):
    def run(self) -> None:
        relative_path = "input_dataset_parameters.json"
        self.write(
            data=InputDatasetPartDocumentList(
                doc_list=self.input_dataset_document_simple_parameters_part
            ),
            relative_path=relative_path,
            tags=VbiTag.input_dataset_parameters(),
            encoder=basemodel_encoder,
        )
        logger.info(f"Wrote input dataset parameter doc to {relative_path}")

    @property
    def input_dataset_document_simple_parameters_part(self):
        parameters_list = []
        value_id = randint(1000, 2000)
        for pn, pv in asdict(VbiInputDatasetParameterValues()).items():
            values = [
                {
                    "parameterValueId": value_id,
                    "parameterValue": json.dumps(pv),
                    "parameterValueStartDate": "1946-11-20",
                }
            ]
            parameter = {"parameterName": pn, "parameterValues": values}
            parameters_list.append(parameter)

        return parameters_list


class ShowExposureTimes(VbiTaskBase):
    def run(self) -> None:
        logger.info(f"{self.constants.dark_exposure_times = }")
        logger.info(f"{self.constants.gain_exposure_times = }")
        logger.info(f"{self.constants.observe_exposure_times = }")


class ValidateL1Output(VbiTaskBase):
    def run(self) -> None:
        files = self.read(tags=[VbiTag.output(), VbiTag.frame()])
        for f in files:
            logger.info(f"Validating {f}")
            spec214_validator.validate(f, extra=False)


def setup_APM_config() -> None:
    mesh_config = {
        "system-monitoring-log-apm": {
            "mesh_address": "system-monitoring-log-apm.service.sim.consul",
            "mesh_port": 8200,
        },
        "automated-processing-scratch-inventory": {"mesh_address": "localhost", "mesh_port": 6379},
        "internal-api-gateway": {"mesh_address": "localhost", "mesh_port": 80},
    }
    apm_options = {"TRANSACTION_MAX_SPANS": 10000}
    os.environ["MESH_CONFIG"] = json.dumps(mesh_config)
    os.environ["ELASTIC_APM_ENABLED"] = "true"
    os.environ["ELASTIC_APM_OTHER_OPTIONS"] = json.dumps(apm_options)


def l0_pipeline_workflow(manual_processing_run: ManualProcessing) -> None:
    manual_processing_run.run_task(task=ShowExposureTimes)
    manual_processing_run.run_task(task=VbiQualityL0Metrics)
    manual_processing_run.run_task(task=DarkCalibration)
    manual_processing_run.run_task(task=GainCalibration)
    manual_processing_run.run_task(task=ScienceCalibration)


def summit_data_processing_workflow(manual_processing_run: ManualProcessing) -> None:
    manual_processing_run.run_task(task=GenerateL1SummitData)


def main(
    scratch_path,
    recipe_run_id,
    suffix: str = "FITS",
    skip_translation: bool = False,
    skip_movie: bool = False,
    only_translate: bool = False,
    science_workflow_name: str = "l0_processing",
    use_apm: bool = False,
):
    if use_apm:
        setup_APM_config()
    science_func_dict = {
        "l0_pipeline": l0_pipeline_workflow,
        "summit_data_processed": summit_data_processing_workflow,
    }
    science_workflow = science_func_dict[science_workflow_name]
    with ManualProcessing(
        workflow_path=scratch_path,
        recipe_run_id=recipe_run_id,
        testing=True,
        workflow_name=f"vbi-{science_workflow_name}",
        workflow_version="GROGU",
    ) as manual_processing_run:
        if not skip_translation:
            manual_processing_run.run_task(
                task=translate_task(
                    summit_processed=science_workflow_name == "summit_data_processed", suffix=suffix
                )
            )
        if only_translate:
            return
        manual_processing_run.run_task(task=CreateInputDatasetParameterDocument)
        manual_processing_run.run_task(task=tag_inputs_task(suffix))
        manual_processing_run.run_task(task=ParseL0VbiInputData)
        science_workflow(manual_processing_run)
        manual_processing_run.run_task(task=VbiWriteL1Frame)
        manual_processing_run.run_task(task=QualityL1Metrics)
        manual_processing_run.run_task(task=VbiQualityL1Metrics)
        manual_processing_run.run_task(task=AssembleQualityData)
        manual_processing_run.run_task(task=ValidateL1Output)

        # Put this here because the movie stuff takes a long time
        if INV:
            manual_processing_run.run_task(task=CreateTrialAsdf)
        else:
            logger.warning(
                "Did NOT make dataset asdf file because the asdf generator is not installed"
            )

        if QUALITY:
            manual_processing_run.run_task(task=CreateTrialQualityReport)
        else:
            logger.warning("Did NOT make quality report pdf because dkist-quality is not installed")

        if not skip_movie:
            manual_processing_run.run_task(task=MakeVbiMovieFrames)
            manual_processing_run.run_task(task=AssembleVbiMovie)

        manual_processing_run.count_provenance()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Run an end-to-end test of the VBI DC Science pipeline"
    )
    parser.add_argument("scratch_path", help="Location to use as the DC 'scratch' disk")
    parser.add_argument("--suffix", help="File suffix to treat as INPUT frames", default="FITS")
    parser.add_argument(
        "-W",
        "--workflow_name",
        help="Name of VBI workflow to test",
        choices=["l0_pipeline", "summit_data_processed"],
        default="l0_pipeline",
    )
    parser.add_argument(
        "-i",
        "--run-id",
        help="Which subdir to use. This will become the recipe run id",
        type=int,
        default=4,
    )
    parser.add_argument(
        "-T",
        "--skip-translation",
        help="Skip the translation of raw 122 l0 frames to 214 l0",
        action="store_true",
    )
    parser.add_argument(
        "-t", "--only-translate", help="Do ONLY the translation step", action="store_true"
    )
    parser.add_argument("-M", "--skip-movie", help="Skip making output movie", action="store_true")
    parser.add_argument("-A", "--use-apm", help="Send APM spans to SIM", action="store_true")
    args = parser.parse_args()

    sys.exit(
        main(
            scratch_path=args.scratch_path,
            recipe_run_id=args.run_id,
            suffix=args.suffix,
            skip_translation=args.skip_translation,
            only_translate=args.only_translate,
            skip_movie=args.skip_movie,
            science_workflow_name=args.workflow_name,
            use_apm=args.use_apm,
        )
    )
