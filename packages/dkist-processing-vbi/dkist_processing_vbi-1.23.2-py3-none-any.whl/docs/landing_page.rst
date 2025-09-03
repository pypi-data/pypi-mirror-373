Overview
========

The mission of the Visible Broadband Imager (VBI) is to record images at the highest possible spatial and
temporal resolution at specific wavelengths in the visible spectrum, prioritizing high cadence and short
exposure times.

The `dkist-processing-vbi` code repository contains the implementation of the VBI calibration pipelines,
which convert Level 0 files from the telescope into Level 1 output products. Currently, VBI data are processed
outside of the Data Center and so the VBI “pipeline” mostly just repackages the processed data to be consistent
with other Data Center products. Pipelines are built on
`dkist-processing-common <https://docs.dkist.nso.edu/projects/common/>`_ tasks and use
the `dkist-processing-core <https://docs.dkist.nso.edu/projects/core/>`_ framework. Follow links
on this page for more information about calibration pipelines.

Level 1 data products are available at the `DKIST Data Portal <https://dkist.data.nso.edu/>`_ and can be
analyzed with `DKIST Python User Tools <https://docs.dkist.nso.edu/projects/python-tools/>`_.  For help, please
contact the `DKIST Help Desk <https://nso.atlassian.net/servicedesk/customer/portals/>`_.
