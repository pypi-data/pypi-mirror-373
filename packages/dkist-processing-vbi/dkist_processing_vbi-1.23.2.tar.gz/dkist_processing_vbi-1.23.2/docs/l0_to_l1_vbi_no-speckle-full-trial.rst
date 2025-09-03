l0_to_l1_vbi_no-speckle-full-trial
==================================

This trial workflow is designed for pipeline testing internal to the DKIST Data Center (DC). It runs the dark and gain
calibrations but does not reconstruct the data in any way.  The workflow stops short of publishing the results or
activating downstream DC services. The pipeline products are transferred to an internal location where they can be
examined by DC personnel or DKIST scientists.

For more detail on each workflow task, you can click on the task in the diagram.

.. workflow_diagram:: dkist_processing_vbi.workflows.trial_workflows.full_trial_no_speckle_pipeline
