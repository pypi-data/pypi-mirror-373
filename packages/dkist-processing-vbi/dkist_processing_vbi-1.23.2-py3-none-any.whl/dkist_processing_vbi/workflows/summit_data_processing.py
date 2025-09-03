"""VBI summit_processed_data workflow.

DKIST: https://nso.edu/telescopes/dki-solar-telescope/

VBI: https://nso.edu/telescopes/dkist/instruments/vbi/

This workflow is used when VBI data was processed on the DKIST summit.
In this case it is then transferred to the DKIST Data Center for packaging, but no further calibrations are applied.

To determine the type of calibrations applied, please inspect the `VBI__005` keyword in the FITS headers.
It will indicate whether frame selection, speckle imaging, or other calibration algorithms were applied.
"""

from dkist_processing_common.tasks import AssembleQualityData
from dkist_processing_common.tasks import PublishCatalogAndQualityMessages
from dkist_processing_common.tasks import QualityL1Metrics
from dkist_processing_common.tasks import SubmitDatasetMetadata
from dkist_processing_common.tasks import Teardown
from dkist_processing_common.tasks import TransferL0Data
from dkist_processing_common.tasks import TransferL1Data
from dkist_processing_core import Workflow

from dkist_processing_vbi.tasks import AssembleVbiMovie
from dkist_processing_vbi.tasks import GenerateL1SummitData
from dkist_processing_vbi.tasks import MakeVbiMovieFrames
from dkist_processing_vbi.tasks import ParseL0VbiInputData
from dkist_processing_vbi.tasks import VbiQualityL1Metrics
from dkist_processing_vbi.tasks import VbiWriteL1Frame

summit_processed_data = Workflow(
    input_data="l0",
    output_data="l1",
    category="vbi",
    detail="summit-calibrated",
    workflow_package=__package__,
)
summit_processed_data.add_node(task=TransferL0Data, upstreams=None)

# Science flow
summit_processed_data.add_node(task=ParseL0VbiInputData, upstreams=TransferL0Data)
summit_processed_data.add_node(task=GenerateL1SummitData, upstreams=ParseL0VbiInputData)
summit_processed_data.add_node(task=VbiWriteL1Frame, upstreams=GenerateL1SummitData)

# Movie flow
summit_processed_data.add_node(task=MakeVbiMovieFrames, upstreams=GenerateL1SummitData)
summit_processed_data.add_node(task=AssembleVbiMovie, upstreams=MakeVbiMovieFrames)

# Quality flow
summit_processed_data.add_node(task=VbiQualityL1Metrics, upstreams=GenerateL1SummitData)
summit_processed_data.add_node(task=QualityL1Metrics, upstreams=GenerateL1SummitData)
summit_processed_data.add_node(
    task=AssembleQualityData, upstreams=[VbiQualityL1Metrics, QualityL1Metrics]
)

# Output flow
summit_processed_data.add_node(
    task=SubmitDatasetMetadata, upstreams=[VbiWriteL1Frame, AssembleQualityData, AssembleVbiMovie]
)
summit_processed_data.add_node(task=TransferL1Data, upstreams=[VbiWriteL1Frame, AssembleVbiMovie])
summit_processed_data.add_node(
    task=PublishCatalogAndQualityMessages, upstreams=[SubmitDatasetMetadata, TransferL1Data]
)

# goodbye
summit_processed_data.add_node(task=Teardown, upstreams=PublishCatalogAndQualityMessages)
