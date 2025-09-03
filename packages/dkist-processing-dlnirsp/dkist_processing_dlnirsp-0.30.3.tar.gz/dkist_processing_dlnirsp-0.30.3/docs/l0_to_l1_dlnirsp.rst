l0_to_l1_dlnirsp
================

In the normal operating mode, raw DLNIRSP data is gathered at the summit and delivered to the Data Center.
The Data Center then calibrates this data and prepares it for storage using the following workflow.

For more detail on each workflow task, you can click on the task in the diagram.

.. workflow_diagram:: dkist_processing_dlnirsp.workflows.l0_processing.l0_pipeline

In this workflow, raw dark, gain, and polarization calibration data is used to generate calibration products that are then applied to the science frames before repackaging them for storage and delivery to a science user.
