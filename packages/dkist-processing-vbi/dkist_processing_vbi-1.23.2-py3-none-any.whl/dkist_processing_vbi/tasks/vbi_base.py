"""VBI base task."""

from abc import ABC

from dkist_processing_common.tasks import WorkflowTaskBase

from dkist_processing_vbi.models.constants import VbiConstants


class VbiTaskBase(WorkflowTaskBase, ABC):
    """
    Task class for base VBI tasks.

    Parameters
    ----------
    recipe_run_id : int
        id of the recipe run used to identify the workflow run this task is part of
    workflow_name : str
        name of the workflow to which this instance of the task belongs
    workflow_version : str
        version of the workflow to which this instance of the task belongs

    """

    # So tab completion shows all the ViSP constants
    constants: VbiConstants

    @property
    def constants_model_class(self):
        """Provide VBI constants access."""
        return VbiConstants
