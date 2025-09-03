l0_to_l1_vbi_no-speckle
=======================

The VBI can operate in various modes, one of which is that raw data taken at the summit is delivered directly to the Data Center.
In this mode, the Data Center calibrates the data and prepares it for storage using the following workflow.

For more detail on each workflow task, you can click on the task in the diagram.

.. workflow_diagram:: dkist_processing_vbi.workflows.l0_processing.l0_pipeline

In this workflow, raw dark and gain frames are used to generate average dark and gain frames that are subsequently subtracted from the L0 science data before being packaged for delivery to a science user.
