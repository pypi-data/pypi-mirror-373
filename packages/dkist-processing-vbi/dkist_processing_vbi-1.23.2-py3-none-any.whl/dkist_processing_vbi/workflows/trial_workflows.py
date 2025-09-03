"""
Workflow for trial runs.

These runs send their outputs (as well as intermediate files) to an unpublished location so that
the DC, in coordination instrument scientists, can assess the performance of the pipeline.
"""

from dkist_processing_common.tasks import AssembleQualityData
from dkist_processing_common.tasks import CreateTrialAsdf
from dkist_processing_common.tasks import CreateTrialDatasetInventory
from dkist_processing_common.tasks import CreateTrialQualityReport
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferTrialData
from dkist_processing_common.tasks import TrialTeardown
from dkist_processing_core import Workflow

from dkist_processing_vbi.tasks import AssembleVbiMovie
from dkist_processing_vbi.tasks import DarkCalibration
from dkist_processing_vbi.tasks import GainCalibration
from dkist_processing_vbi.tasks import GenerateL1SummitData
from dkist_processing_vbi.tasks import MakeVbiMovieFrames
from dkist_processing_vbi.tasks import ParseL0VbiInputData
from dkist_processing_vbi.tasks import ScienceCalibration
from dkist_processing_vbi.tasks import VbiQualityL0Metrics
from dkist_processing_vbi.tasks import VbiQualityL1Metrics
from dkist_processing_vbi.tasks import VbiWriteL1Frame

# Summit-calibrated pipeline
full_trial_summit_pipeline = Workflow(
    input_data="l0",
    output_data="l1",
    category="vbi",
    detail="summit-calibrated-full-trial",
    workflow_package=__package__,
)
full_trial_summit_pipeline.add_node(task=TransferL0Data, upstreams=None)

# Science flow
full_trial_summit_pipeline.add_node(task=ParseL0VbiInputData, upstreams=TransferL0Data)
full_trial_summit_pipeline.add_node(task=GenerateL1SummitData, upstreams=ParseL0VbiInputData)
full_trial_summit_pipeline.add_node(task=VbiWriteL1Frame, upstreams=GenerateL1SummitData)

# Movie flow
full_trial_summit_pipeline.add_node(task=MakeVbiMovieFrames, upstreams=GenerateL1SummitData)
full_trial_summit_pipeline.add_node(task=AssembleVbiMovie, upstreams=MakeVbiMovieFrames)

# Quality flow
full_trial_summit_pipeline.add_node(task=VbiQualityL1Metrics, upstreams=GenerateL1SummitData)
full_trial_summit_pipeline.add_node(task=QualityL1Metrics, upstreams=GenerateL1SummitData)
full_trial_summit_pipeline.add_node(
    task=AssembleQualityData, upstreams=[VbiQualityL1Metrics, QualityL1Metrics]
)

# Output flow
full_trial_summit_pipeline.add_node(
    task=CreateTrialDatasetInventory, upstreams=VbiWriteL1Frame, pip_extras=["inventory"]
)
full_trial_summit_pipeline.add_node(
    task=CreateTrialAsdf, upstreams=VbiWriteL1Frame, pip_extras=["asdf"]
)
full_trial_summit_pipeline.add_node(
    task=CreateTrialQualityReport, upstreams=AssembleQualityData, pip_extras=["quality"]
)
full_trial_summit_pipeline.add_node(
    task=TransferTrialData,
    upstreams=[
        AssembleVbiMovie,
        CreateTrialDatasetInventory,
        CreateTrialAsdf,
        CreateTrialQualityReport,
    ],
)

# goodbye
full_trial_summit_pipeline.add_node(task=TrialTeardown, upstreams=TransferTrialData)


# No-speckle pipeline
full_trial_no_speckle_pipeline = Workflow(
    input_data="l0",
    output_data="l1",
    category="vbi",
    detail="no-speckle-full-trial",
    workflow_package=__package__,
)
full_trial_no_speckle_pipeline.add_node(task=TransferL0Data, upstreams=None)

# Science flow
full_trial_no_speckle_pipeline.add_node(task=ParseL0VbiInputData, upstreams=TransferL0Data)
full_trial_no_speckle_pipeline.add_node(task=DarkCalibration, upstreams=ParseL0VbiInputData)
full_trial_no_speckle_pipeline.add_node(task=GainCalibration, upstreams=DarkCalibration)
full_trial_no_speckle_pipeline.add_node(task=ScienceCalibration, upstreams=GainCalibration)
full_trial_no_speckle_pipeline.add_node(task=VbiWriteL1Frame, upstreams=ScienceCalibration)

# Movie flow
full_trial_no_speckle_pipeline.add_node(task=MakeVbiMovieFrames, upstreams=ScienceCalibration)
full_trial_no_speckle_pipeline.add_node(task=AssembleVbiMovie, upstreams=MakeVbiMovieFrames)

# Quality flow
full_trial_no_speckle_pipeline.add_node(task=VbiQualityL0Metrics, upstreams=ParseL0VbiInputData)
full_trial_no_speckle_pipeline.add_node(task=QualityL1Metrics, upstreams=ScienceCalibration)
full_trial_no_speckle_pipeline.add_node(task=VbiQualityL1Metrics, upstreams=ScienceCalibration)
full_trial_no_speckle_pipeline.add_node(
    task=AssembleQualityData, upstreams=[VbiQualityL0Metrics, QualityL1Metrics, VbiQualityL1Metrics]
)

# Output flow
full_trial_no_speckle_pipeline.add_node(
    task=CreateTrialDatasetInventory, upstreams=VbiWriteL1Frame, pip_extras=["inventory"]
)
full_trial_no_speckle_pipeline.add_node(
    task=CreateTrialAsdf, upstreams=VbiWriteL1Frame, pip_extras=["asdf"]
)
full_trial_no_speckle_pipeline.add_node(
    task=CreateTrialQualityReport, upstreams=AssembleQualityData, pip_extras=["quality"]
)
full_trial_no_speckle_pipeline.add_node(
    task=TransferTrialData,
    upstreams=[
        AssembleVbiMovie,
        CreateTrialDatasetInventory,
        CreateTrialAsdf,
        CreateTrialQualityReport,
    ],
)

# goodbye
full_trial_no_speckle_pipeline.add_node(task=TrialTeardown, upstreams=TransferTrialData)
