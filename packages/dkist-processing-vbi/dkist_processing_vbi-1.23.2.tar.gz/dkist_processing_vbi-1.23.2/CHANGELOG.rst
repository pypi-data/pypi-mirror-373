v1.23.2 (2025-09-02)
====================

Misc
----

- Update pre-commit hook versions and replace python-reorder-imports with isort. (`#148 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/148>`__)
- Update `dkist-processing-math` to remove a deprecated package dependency. (`#149 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/149>`__)
- Update `dkist-processing-common` to allow instrument level changes to cadence-related keywords when writing L1 data. (`#149 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/149>`__)


v1.23.1 (2025-08-12)
====================

Misc
----

- Update some pre-commit hook versions. (`#146 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/146>`__)
- Update verion of `dkist-processing-common` to v11.2.1 to fix bug that caused Wavecal quality metrics to not be rendered in Quality Reports.
  Also bump `dkist-quality` to v2.0.0 for the same reason. This doesn't affect VBI, but it's nice to stay up-to-date. (`#147 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/147>`__)


v1.23.0 (2025-07-18)
====================

Bugfixes
--------

- Update `dkist-processing-common` to include the results of wavelength calibration when determining spectral lines in the data. (`#145 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/145>`__)


v1.22.1 (2025-07-15)
====================

Misc
----

- Replace `FakeGQLClient` with the `fake_gql_client` fixture imported from the `mock_metadata_store` module
  in `dkist-processing-common`.  Because the fixture is imported into `conftest.py`, individual imports are not needed. (`#143 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/143>`__)


v1.22.0 (2025-07-10)
====================

Bugfixes
--------

- Update the VBI workflows such that the `SubmitDatasetMetadata` task is now dependent on the `AssembleVbiMovie` task. This ensures that the metadata is submitted only after the movie has been assembled and that it is counted in downstream checks. (`#144 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/144>`__)


Misc
----

- Update dkist-processing-common to handle non-finite values in quality wavecal metrics. (`#144 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/144>`__)


v1.21.9 (2025-07-08)
====================

Misc
----

- Update dkist-inventory to 1.9.0 in order to stay current with production generation of inventory and metadata.asdf files in trial workflows.


v1.21.8 (2025-07-02)
====================

Misc
----

- Update `dkist-processing-common` to v11.0.0 and update affected `Stem`'s for the new API. (`#142 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/142>`__)
- Bump version of `dkist-quality`. This change doesn't affect `dkist-processing-vbi`, but it's nice to stay up-to-date. (`#142 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/142>`__)


v1.21.7 (2025-06-25)
====================

Misc
----

- Update dkist-inventory to 1.8.4 in order to avoid a bug in the generation of inventory and metadata.asdf files in trial workflows. (`#141 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/141>`__)


v1.21.6 (2025-06-02)
====================

Misc
----

- Remove use of input dataset mixin imported from dkist-processing-common. (`#128 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/128>`__)


v1.21.5 (2025-05-30)
====================

Misc
----

- Update `dkist-fits-specifications` to v4.17.0 (`#140 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/140>`__)


v1.21.4 (2025-05-28)
====================

Misc
----

- Update `dkist-processing-common` to v10.8.3 (`#139 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/139>`__)


v1.21.3 (2025-05-27)
====================

Bugfixes
--------

- Populate the `WAVEBAND` keyword with the name of the VBI filter used. (`#135 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/135>`__)


v1.21.2 (2025-05-23)
====================

Misc
----

- Update dkist-processing-common dependency to v10.8.1 (`#138 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/138>`__)


v1.21.1 (2025-05-21)
====================

Misc
----

- Update dkist-fits-specifications dependency to v4.16.0. (`#137 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/137>`__)


v1.21.0 (2025-05-15)
====================

Misc
----

- Updating dependencies to cross astropy 7.0.0 and numpy 2.0.0. (`#136 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/136>`__)


v1.20.4 (2025-05-06)
====================

Misc
----

- Update dkist-fits-specifications to add the `THEAP` keyword. (`#134 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/134>`__)


v1.20.3 (2025-05-01)
====================

Misc
----

- Use the latest version of dkist-inventory for trial workflow inventory and metadata ASDF generation. (`#133 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/133>`__)


v1.20.2 (2025-04-24)
====================

Misc
----

- Use the latest version of dkist-inventory for trial workflow inventory and metadata ASDF generation. (`#132 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/132>`__)


v1.20.1 (2025-04-21)
====================

Misc
----

- Bump dkist-processing-common to v10.7.2, which fixes a bug that required the AO_LOCK keyword to be present in the headers. (`#131 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/131>`__)


v1.20.0 (2025-04-17)
====================

Misc
----

- Update dkist-processing-common to only remove level 0 header keys from the level 1 files. (`#128 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/128>`__)
- Add missing build dependency specifications. (`#130 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/130>`__)


v1.19.14 (2025-03-31)
=====================

Bugfixes
--------

- Update dkist-processing-common to v10.6.4 to fix a bug in writing L1 frames when input dataset parts are missing. (`#127 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/127>`__)


v1.19.13 (2025-03-27)
=====================

Bugfixes
--------

- Update dkist-processing-common to v10.6.3 to fix a bug when input dataset parts are missing. (`#126 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/126>`__)


v1.19.12 (2025-03-24)
=====================

Features
--------

- Add the option of a five-step mosaic pattern for VBI-RED observations. This is achieved by treating the five positions as a 3x3 array with the four corners and center position populated. (`#106 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/106>`__)


v1.19.11 (2025-03-21)
=====================

Misc
----

- Add code coverage badge to README.rst. (`#123 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/123>`__)
- Fix bug that caused some tests to incorrectly fail depending on how they were assigned to xdist workers. (`#124 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/124>`__)
- Bump `dkist-inventory` to v1.7.0. This adds support for sparsely sampled mosaics, which will be used by VBI in the future, to Trial workflows. (`#125 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/125>`__)


v1.19.10 (2025-03-19)
=====================

Misc
----

- Bump dkist-processing-common to v10.6.2, which fixes a bug in manual processing. (`#122 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/122>`__)


v1.19.9 (2025-03-14)
====================

Misc
----

- Bump dkist-processing-common to v10.6.1 (`#121 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/121>`__)


v1.19.8 (2025-03-03)
====================

Misc
----

- Bump `dkist-processing-common` to v10.6.0. No change to VBI pipeline. (`#120 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/120>`__)


v1.19.7 (2025-02-26)
====================

Misc
----

- Update `dkist-processing-common` to use version 2.10.5 of `apache-airflow. (`#119 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/119>`__)


v1.19.6 (2025-02-24)
====================

Misc
----

- Bump `dkist-processing-math` to v2.2.0 (`#118 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/118>`__)


v1.19.5 (2025-02-20)
====================

Misc
----

- Change the color map used in VBI movies from `viridis` to `gray`. (`#116 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/116>`__)


v1.19.4 (2025-02-19)
====================

Misc
----

- Bump `dkist-processing-common` to 10.5.14, which computes PRODUCT when creating L1 FITS headers. (`#117 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/117>`__)


v1.19.3 (2025-02-14)
====================

Misc
----

- Add Bitbucket pipeline steps to check that full dependencies were correctly frozen. (`#114 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/114>`__)
- Bump version of `dkist-processing-common` to bring along new version of `dkist-processing-core` that uses frozen dependencies for pipeline install. (`#114 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/114>`__)


v1.19.2 (2025-02-12)
====================

Misc
----

- Bump `dkist-inventory` to 1.6.1. (`#115 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/115>`__)
- Bump `dkist-processing-common` to 10.5.12, which increases the DSETID to 6 characters. (`#115 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/115>`__)


v1.19.1 (2025-02-10)
====================

Features
--------

- Bump `dkist-fits-specifications` to 4.11.0, which adds the L1 PRODUCT keyword. (`#113 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/113>`__)


v1.19.0 (2025-02-06)
====================

Features
--------

- Update the orientation of the mosaic MINDEX{12} header keys.
  Previously the MINDEX keys described a row-major mosaic with the origin in the upper-left, but a more natural and
  intuitive mosaic orientation is column-major with the origin in the lower-left. (`#109 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/109>`__)


Misc
----

- Bump some minimum dependencies for compatibility with new versions of `dkist-inventory` and `dkist-processing-common`. (`#109 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/109>`__)


v1.18.14 (2025-02-05)
=====================

Bugfixes
--------

- Fix bug in movie assembly where `np.nanpercentile` uses a range of 0-100 instead of 0-1. (`#112 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/112>`__)


v1.18.13 (2025-02-04)
=====================

Features
--------

- Remove intermediate loader mixin for tasks and replace with standard read method
  from `dkist-processing-common` and composite tags, task_dark_frame and task_gain_frame. (`#108 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/108>`__)


v1.18.12 (2025-02-03)
=====================

Features
--------

- Clip the top and bottom 0.5% of values in the movie array, based on the Cumulative Distribution Function, to improve contrast. (`#111 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/111>`__)


v1.18.11 (2025-01-29)
=====================

Misc
----

- Update dkist-processing-common and dkist-quality to manage a bug present in dacite 1.9.0.
- Update Bitbucket pipelines to use execute script for standard steps. (`#109 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/109>`__)


v1.18.10 (2025-01-28)
=====================

Bugfixes
--------

- Handle a memory leak caused by opening a FITS file without closing it. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/101>`__)


v1.18.9 (2025-01-27)
====================

Misc
----

- Update bitbucket pipelines to use common scripts for checking for changelog snippets and verifying doc builds. (`#107 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/107>`__)
- Update dkist-processing-common to remove some deprecated packages.


v1.18.8 (2025-01-09)
====================

Misc
----

- Update dkist-inventory to change dataset inventory parsing logic in trial workflows.


v1.18.7 (2025-01-09)
====================

Misc
----

- Update dkist-processing-common to pull in the new version of airflow.


v1.18.6 (2024-12-20)
====================

Documentation
-------------

- Change the documentation landing page to focus more on users and less on developers. (`#103 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/103>`__)


v1.18.5 (2024-12-18)
====================

Features
--------

- Bump common to remove Fried parameter from the L1 headers and the quality metrics where the AO system is unlocked. (`#105 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/105>`__)


Misc
----

- Update Bitbucket pipelines to use standardized lint and scan steps. (`#104 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/104>`__)


v1.18.4 (2024-11-26)
====================

Misc
----

- Bumping dkist-fits-specification to v4.10.0 and dkist-processing-common to v10.5.3 (`#102 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/102>`__)
- Write the CNAMEn keywords to the instrument headers. (`#102 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/102>`__)


v1.18.3 (2024-11-21)
====================

Bugfixes
--------

- Update dkist-inventory and dkist-processing-common to fix a bug in producing dataset inventory from the SPECLN* keys


v1.18.2 (2024-11-20)
====================

Bugfixes
--------

- Update dkist-processing-common to constrain asdf < 4.0.0


v1.18.1 (2024-11-20)
====================

Misc
----

- Update dkist-processing-common to manage breaking API changes in asdf and moviepy.


v1.18.0 (2024-11-14)
====================

Misc
----

- Replace `TransferVispTrialData` with `TransferTrialData` from dkist-processing-common. (`#100 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/100>`__)


v1.17.5 (2024-10-15)
====================

Misc
----

- Bump `dkist-processing-common` to v10.3.0, which hardens polcal fitting against bad input data.
  This doesn't affect VBI at all, but it's nice to stay up-to-date. (`#99 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/99>`__)


v1.17.4 (2024-10-14)
====================

Misc
----

- Make and publish wheels at code push in build pipeline (`#98 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/98>`__)
- Switch from setup.cfg to pyproject.toml for build configuration (`#98 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/98>`__)


v1.17.3 (2024-10-07)
====================

Misc
----

- Bump dkist-fits-specifications to v4.7.0. This adjusted the TTBLTRCK allowed values, adjusted CRSP_051 and CRSP_052 to accommodate blocking filters,adjusted CRSP_073 to include a new grating, and added a new allowed value to CAM__044. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/97>`__)


v1.17.2 (2024-10-04)
====================

Features
--------

- Add trial workflows (`#96 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/96>`__)


v1.17.1 (2024-09-27)
====================

Misc
----

- Bump `dkist-processing-common` to v10.2.1. This fixes a documentation build bug in Airflow.


v1.17.0 (2024-09-27)
====================

Misc
----

- Bump `dkist-processing-common` to v10.2.0. This includes upgrading to the latest version of Airflow (2.10.2).


v1.16.3 (2024-09-26)
====================

Misc
----

- Bump `dkist-processing-common` to v10.1.0. This enables the usage of the `NearFloatBud` and `TaskNearFloatBud` in parsing.


v1.16.2 (2024-09-24)
====================

Misc
----

- Bump `dkist-processing-common` to v10.0.1. This fixes a bug in the reported FRAMEVOL key in L1 headers. (`#95 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/95>`__)


v1.16.1 (2024-09-23)
====================

Bugfixes
--------

- Look for CALIBRATED frames during the `VbiQualityL1Metrics` task. This was missed in version 1.16.0 (`#94 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/94>`__)


v1.16.0 (2024-09-23)
====================

Features
--------

- Reorder task dependencies in workflows. Movie and L1 quality tasks are no longer dependent on the presence of OUTPUT
  frames and thus can be run in parallel with the `WriteL1` task. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/92>`__)


Misc
----

- Use CALIBRATED instead of OUTPUT frames in post-science movie and quality tasks. This doesn't change the output at all (the arrays are the same), but
  it's necessary for `dkist-processing-common >= 10.0.0` that will break using OUTPUT frames. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/92>`__)
- Don't use `self.tags()` when processing summit-calibrated data. Instead we list exactly the tags we want to apply, which is much cheaper. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/92>`__)
- Remove `AssembleVbiMovie` as workflow dependency on `SubmitDatasetMetadata`. This dependency has been unnecessary
  since the introduction of `SubmitDatasetMetadata` in v1.9.0. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/92>`__)


v1.15.1 (2024-09-19)
====================

Misc
----

- Bump `dkist-quality` to v1.1.1. This fixes raincloud plot rendering in trial workflows. VBI doesn't ever make raincloud
  plots (because they're only for polarimetric data), but it's nice to be up-to-date. (`#93 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/93>`__)


v1.15.0 (2024-09-11)
====================

Misc
----

- Accommodate changes to the GraphQL API associated with refactoring the quality database (`#91 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/91>`__)


v1.14.7 (2024-08-21)
====================

Misc
----

- Update some Quality related tasks and methods for the new API in `dkist-processing-common` v9.0.0. No change to any outputs. (`#90 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/90>`__)


v1.14.5 (2024-08-12)
====================

Misc
----

- Move to version 4.6.0 of `dkist-fits-specifications` to correct allowed values of the TTBLTRCK header keyword.



v1.14.4 (2024-08-12)
====================

Misc
----

- Move to version 4.5.0 of `dkist-fits-specifications` which includes `PV1_nA` keys for non linear dispersion.


v1.14.3 (2024-08-05)
====================

Documentation
-------------

- Add pre-commit hook for documentation. Edit README.rst. (`#88 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/88>`__)


v1.14.2 (2024-07-25)
====================

Misc
----

- Rewrite to eliminate warnings in unit tests. (`#87 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/87>`__)


v1.14.1 (2024-07-19)
====================

Misc
----

- Move to version 4.2.2 of `dkist-fits-specifications` which includes `PV1_n` keys for non linear dispersion.



v1.14.0 (2024-07-12)
====================

Misc
----

- Move to version 8.2.1 of `dkist-processing-common` which includes the publication of select private methods for documentation purposes. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/86>`__)


v1.13.0 (2024-07-01)
====================

Misc
----

- Move to version 8.1.0 of `dkist-processing-common` which includes an upgrade to airflow 2.9.2. (`#85 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/85>`__)


v1.12.5 (2024-06-25)
====================

Misc
----

- Move to version 8.0.0 of `dkist-processing-common`. This version only affects parameters and therefore doesn't impact `dkist-processing-vbi` at all, but it's nice to be up-to-date. (`#84 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/84>`__)


v1.12.4 (2024-06-12)
====================

Misc
----

- Bump `dkist-fits-specifications` to v4.3.0. This version contains bugfixes for DL-NIRSP, but we want to say current. (`#83 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/83>`__)


v1.12.3 (2024-06-12)
====================

Misc
----

- Update all VBI dependencies to their latest versions. (`#81 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/81>`__)


v1.12.2 (2024-06-11)
====================

Misc
----

- Refactor production workflows to correct dependency of the `SubmitDatasetMetadata` task. (`#82 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/82>`__)


v1.12.1 (2024-06-04)
====================

Misc
----

- Bump `dkist-data-simulator` to v5.2.0 and `dkist-inventory` to v1.4.0. These versions add support for DLNIRSP data (but it's nice to be up-to-date). (`#79 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/79>`__)


v1.12.0 (2024-06-03)
====================

Misc
----

- Resolve matplotlib version conflict (`#78 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/78>`__)
- Upgrade the version of dkist-processing-common which brings along various major version upgrades to libraries associated with Pydantic 2. (`#79 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/79>`__)


v1.11.1 (2024-05-20)
====================

Misc
----

- Bump `dkist-processing-common` to v6.2.4. Doesn't affect `dkist-processing-vbi` at all, but nice to stay up-to-date. (`#77 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/77>`__)


v1.11.0 (2024-05-17)
====================

Bugfixes
--------

- Updating `matplotlib` function calls due to deprecation of parts of the `cm` module. No change in functionality. (`#76 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/76>`__)


v1.10.0 (2024-05-16)
====================

Misc
----

- Bumped dkist-fits-specifications to 4.2.0 (`#75 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/75>`__)


v1.9.1 (2024-05-09)
===================

Misc
----

- Bumped to common 6.3.2 (`#74 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/74>`__)


v1.9.0 (2024-05-08)
===================

Features
--------

- Add the ability to create a quality report from a trial workflow. (`#72 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/72>`__)


v1.8.9 (2024-05-02)
===================

Misc
----

- Rename non-FITS L1 products to better manage namespace. (`#73 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/73>`__)


v1.8.8 (2024-04-12)
===================

Misc
----

- Populate the value of MANPROCD in the L1 headers with a boolean indicating whether there were manual steps involved in the frames production. (`#71 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/71>`__)


v1.8.7 (2024-04-11)
===================

Misc
----

- Update to use the latest version of dkist-processing-common to take advantage of optimizations in the task auditing feature.


v1.8.6 (2024-04-04)
===================

Features
--------

- The ability to rollback tasks in a workflow for possible retry has been added via dkist-processing-common 6.1.0. (`#69 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/69>`__)


v1.8.5 (2024-03-26)
===================

Misc
----

-  Update `dkist-processing-common` to v6.0.4 (fix bug affecting NAXISn keys in `FitsAccessBase` subclasses).


v1.8.4 (2024-03-05)
===================

Misc
----

- Update dkist-processing-common to v6.0.3 (adding the SOLARRAD keyword to L1 headers)


v1.8.3 (2024-03-04)
===================

Misc
----

- Bump common to v6.0.2 (`#68 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/68>`__)


v1.8.2 (2024-02-29)
===================

Bugfixes
--------

- Update dkist-processing-common to v6.0.1 (all movies are now forced to have an even number of pixels in each dimension)


v1.8.1 (2024-02-28)
===================

Features
--------

- Parsing of the spatial step pattern (VBISTPAT/VBI__002) now checks that the pattern describes either a 1x1, 2x2, or 3x3 mosaic. Error otherwise. (`#65 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/65>`__)


Bugfixes
--------

- MINDEX L1 header keys are now correctly based off of mosaic step pattern. (`#65 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/65>`__)
- "DWNAME" and "DPNAME" dataset keywords are now correct and match the CTYPE values. Previously they had swapped latitude and longitude. (`#66 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/66>`__)


v1.8.0 (2024-02-27)
===================

Bugfixes
--------

- DNAXIS and DEAXES now take the temporal axis into account. (`#50 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/50>`__)


v1.7.6 (2024-02-26)
===================

Misc
----

- Update dkist-fist-specifications to 4.1.1 (allow DEAXES = 0)
- Move "grogu_test.py" to "tests/local_trial_workflows/l0_to_l1.py". This normalizes the local trial workflow (i.e., GROGU) machinery across all `dkist-processing-*` instrument packages.


v1.7.5 (2024-02-15)
===================

Misc
----

- Bump common to 6.0.0 (total removal of `FitsData` mixin). (`#64 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/64>`__)


v1.7.4 (2024-02-01)
===================

Misc
----

- Add tasks to trial workflows enabling ASDF, dataset inventory, and movie generation. (`#63 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/63>`__)


v1.7.3 (2024-01-31)
===================

Misc
----

- Bump versions of `dkist-fits-specifications`, `dkist-data-simulator`, and `dkist-header-validator` for fits spec version 4.1.0 (`#61 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/61>`__)


v1.7.2 (2024-01-25)
===================

Misc
----

- Update version of dkist-processing-common to 5.1.0 which includes common tasks for cataloging in trial workflows. (`#62 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/62>`__)


v1.7.1 (2024-01-12)
===================

Misc
----

- Update `dkist-fits-specifications` and associated (validator, simulator) to use new conditional requiredness framework. (`#60 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/60>`__)


v1.7.0 (2023-12-20)
===================

Misc
----

- Adding manual processing worker capabilities via dkist-processing-common update. (`#59 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/59>`__)


v1.6.0 (2023-12-01)
===================

Misc
----

- Use new `TaskName` and task-tags from `dkist-processing-common` to replace multiple usages of strings corresponding to IP task names/types. (`#57 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/57>`__)
- Remove all usages of `FitsDataMixin`. Codec-aware `read` and `write` and how we do this now. (`#58 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/58>`__)


v1.5.2 (2023-11-24)
===================

Misc
----

- Updates to core and common to patch security vulnerabilities and deprecations. (`#56 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/56>`__)


v1.5.1 (2023-11-22)
===================

Misc
----

- Update the FITS header specification to remove some CRYO-NIRSP specific keywords. (`#55 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/55>`__)


v1.5.0 (2023-11-15)
===================

Features
--------

- Define a public API for tasks such that they can be imported directly from dkist-processing-vbi.tasks (`#54 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/54>`__)


v1.4.11 (2023-10-11)
====================

Misc
----

- Use latest version of dkist-processing-common (4.1.4) which adapts to the new metadata-store-api. (`#53 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/53>`__)


v1.4.10 (2023-09-29)
====================

Misc
----

- Update dkist-processing-common to elimate APM steps in writing L1 data.


v1.4.9 (2023-09-21)
===================

Misc
----

- Update dkist-fits-specifications to conform to Revision I of SPEC-0122.


v1.4.8 (2023-09-08)
===================

Misc
----

- Use latest version of dkist-processing-common (4.1.2) which adds support for high memory tasks. (`#52 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/52>`__)


v1.4.7 (2023-09-06)
===================

Misc
----

- Update to version 4.1.1 of dkist-processing-common which primarily adds logging and scratch file name uniqueness. (`#50 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/50>`__)


v1.4.6 (2023-07-28)
===================

Misc
----

- Bump dkist-processing-common to 4.1.0


v1.4.5 (2023-07-26)
===================

Misc
----

- Update dkist-fits-specifications to include ZBLANK.


v1.4.4 (2023-07-26)
===================

Misc
----

- Update dkist-processing-common to upgrade dkist-header-validator to 4.1.0.


v1.4.2 (2023-07-17)
===================

Misc
----

- Update dkist-processing-common and the dkist-header-validator to propagate dependency breakages in PyYAML < 6.0. (`#49 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/49>`__)


v1.4.1 (2023-07-11)
===================

Misc
----

- Update dkist-processing-common to upgrade Airflow to 2.6.3.


v1.4.0 (2023-06-29)
===================

Misc
----

- Update to python 3.11 and update library package versions. (`#48 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/48>`__)


v1.3.1 (2023-06-27)
===================

Misc
----

- Update to support `dkist-processing-common` 3.0.0. Specifically the new signature of some of the `FitsDataMixin` methods. (`#47 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/47>`__)


v1.3.0 (2023-05-17)
===================

Misc
----

- Bumping common to 2.7.0: ParseL0InputData --> ParseL0InputDataBase, constant_flowers --> constant_buds (`#46 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/46>`__)


v1.2.1 (2023-05-05)
===================

Misc
----

- Update dkist-processing-common to 2.6.0 which includes an upgrade to airflow 2.6.0


v1.2.0 (2023-05-02)
===================

Features
--------

- Add support for "subcycling" that can result in multiple repeats of a mosaic for a single DSPS repeat. (`#41 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/41>`__)


Misc
----

- Offload calculation of "WAVEMIN/MAX" in L1 headers to new functionality in `*-common` that uses the already-defined `get_wavelength_range`. The result is that this logic now only lives in one place. (`#44 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/44>`__)


Documentation
-------------

- Replace use of `logging.[thing]` with `logger.[thing]` from `logging42`. (`#42 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/42>`__)
- Add machinery for a "Scientific" changelog that tracks only those changes that affect L1 output data. (`#43 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/43>`__)


v1.1.11 (2023-04-24)
====================

Misc
----

- Update `dkist-fits-specifications` to include header keys for tracking VBI mosaics.

v1.1.10 (2023-04-17)
====================

Bugfixes
--------

- Correct the determination of which spectral lines should be present in L1 frames. (`#40 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/40>`__)


v1.1.9 (2023-04-13)
===================

Misc
----
- Bump version of `dkist-processing-common`

v1.1.8 (2023-04-10)
===================

Misc
----
- FITS header specification update to add spectral line keys.


v1.1.7 (2023-03-16)
===================

Misc
----
- FITS header specification update to add new keys and change some units.


v1.1.6 (2023-03-01)
===================

Misc
----

- Logging fix in the dkist-header-validator.


v1.1.5 (2023-02-22)
===================

Misc
----

- Move the header specification to revision H of SPEC-0122.


v1.1.4 (2023-02-17)
===================

Misc
----

- Update dkist-processing-common due to an Airflow upgrade.


v1.1.3 (2023-02-06)
===================

Features
--------

- Bump `dkist-processing-common` to allow inclusion of multiple proposal or experiment IDs in headers.


v1.1.2 (2023-02-02)
===================

Misc
----
- Bump FITS specification to revision G.


v1.1.1 (2023-01-31)
===================

Misc
----

- Bump `dkist-processing-common`

v1.1.0 (2022-12-15)
===================

Bugfixes
--------

- Don't re-compress already compressed data that are processed at the summit. This maintains the *exact* data received from the summit pipeline. (`#39 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/39>`__)


Misc
----

- Calculate the `DATE-END` keyword value at the instrument level. (`#33 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/33>`__)


v1.0.0 (2022-12-08)
===================

Misc
--------

- Moving the DKIST VBI pipelines into production.



v0.16.0 (2022-12-06)
====================

Features
--------

- If data include an aborted mosaic at the last DSPS repeat then drop that mosaic from the L1 dataset. (`#38 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/38>`__)


Bugfixes
--------

- Change how intermediate CALIBRATED frames are saved so that the L1 FRAMEVOL header key reports the correct on-disk size of the compressed data. (`#32 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/32>`__)
- The "summit_data_processing" workflow now produces *all* L1 quality metrics. (`#35 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/35>`__)
- Fix incorrect DINDEX3 values in L1 data. (`#37 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/37>`__)


Misc
----

- Use a Hann window to smooth out hard mosaic edges in the browse movie. Purely aesthetic. (`#36 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/36>`__)


v0.15.2 (2022-12-05)
====================

Bugfix
------

- Update dkist-processing-common to include movie headers in transfers.


v0.15.1 (2022-12-02)
====================

Misc
----

- Update dkist-processing-common to improve handling of Globus issues.



v0.15.0 (2022-11-15)
====================

Misc
----

- Update dkist-processing-common


v0.14.0 (2022-11-14)
====================

Bugfixes
--------

- Correctly organize data when DSPSREPS (DKIST008) includes instruments other than VBI (and is therefore very large), which may also cause DSPSNUM (DKIST009) to be offset from 1 by a large number. (`#30 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/30>`__)
- Bump `dkist-processing-common` to 1.1.0 to fix bug when running summit-calibrated workflow on float32 data.

Documentation
-------------

- Add changelog to RTD left hand TOC to include rendered changelog in documentation build. (`#31 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/31>`__)
- Fixed markdown errors in CHANGELOG.rst headers. (`#31 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/31>`__)


v0.13.3 (2022-11-09)
====================

Misc
----

- Update dkist-processing-common to improve Globus event logging


v0.13.2 (2022-11-08)
====================

Misc
----

- Update dkist-processing-common to handle empty Globus event lists
- Bump scipy to 1.9.0 and fix an associated test.


v0.13.1 (2022-11-08)
====================

Misc
----

- Update dkist-processing-common to include Globus retries in transfer tasks


v0.13.0 (2022-11-02)
====================

Misc
----

- Upgraded dkist-processing-math and dkist-processing-common to production version (`#28 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/28>`__)


v0.12.1 (2022-11-02)
====================

Misc
--------

- Use updated dkist-processing-core version 1.1.2.  Task startup logging enhancements.


v0.12.0 (2022-10-26)
====================

Misc
----

- Update versions of dkist-processing-common and dkist-fits-specifications. (`#27 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/27>`__)


v0.11.4 (2022-10-26)
====================

Misc
----

- Update versions of dkist-processing-common and astropy. (`#26 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/26>`__)


v0.11.3 (2022-10-20)
====================

Misc
----

- Require python 3.10 and above. (`#25 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/25>`__)


v0.11.2 (2022-10-18)
====================

Misc
------

- Changing metrics included in quality reports


v0.11.1 (2022-10-12)
====================

Bugfix
------

- Moving to a new version of dkist-processing-common to fix a Globus bug


v0.11.0 (2022-10-11)
====================

Misc
----

- Upgrading to a new version of Airflow


v0.10.5 (2022-09-16)
====================

Misc
----

- Update tests for new input dataset document format from `*-common >= 0.24.0` (`#24 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/24>`__)


v0.10.4 (2022-09-14)
====================

Misc
----

- FITS spec was using incorrect types for some keys.

v0.10.3 (2022-09-12)
====================

Misc
----

- Updating the underlying FITS specification used.

v0.10.1 (2022-08-09)
====================

Misc
----

- Corrected workflow naming in docs.


v0.10.0 (2022-08-08)
====================

Misc
----

- Update minimum required version of `dkist-processing-core` due to breaking changes in workflow naming.


v0.9.3 (2022-08-03)
===================

Bugfixes
--------

- Use nearest neighbor interpolation to resize movie frames. This helps avoid weirdness if the maps are very small. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/101>`__)


v0.9.2 (2022-07-21)
===================

Features
--------

- Bumped version of dkist-processing-common in setup.cfg. The change adds microsecond support to datetimes, prevents quiet file overwriting by default, and sets the default fits compression tile size to astropy defaults.

v0.9.1 (2022-06-27)
===================

Bugfixes
--------

- Bumped version of dkist-header-validator in setup.cfg.
  The change fixes a bug in handling multiple fits header commentary cards (HISTORY and COMMENT). (`#23 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/23>`__)


v0.9.0 (2022-06-20)
===================

Features
--------

- Change how L1 filenames are constructed.


v0.8.0 (2022-05-03)
===================

Bugfixes
--------

- Use new version of `dkist-processing-common` (0.18.0) to correct source for "fpa exposure time" keyword
- Bump version of `dkist` to allow for installation of "grogu" target

v0.7.0 (2022-04-28)
===================

Features
--------

- FITS specification now uses Rev. F of SPEC0122 as a base. (`#22 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/22>`__)


v0.6.4 (2022-04-22)
===================

Bugfixes
--------

- Change movie codec for better compatibility.


v0.6.1 (2022-04-06)
===================

Documentation
-------------

- Add changelog and towncrier machinery (`#21 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/21>`__)


Misc
----

- Update usage of `VbiQualityL0Metrics` to reflect changes in `dkist-processing-common >= 0.17.0`

v0.6.0 (2022-03-18)
===================

Features
--------

- Increase usefulness of APM logging for debugging pipeline performance (`#20 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/20>`__)


Documentation
-------------

- Big ol' update and pydocstyle-ization of docs (`#18 <https://bitbucket.org/dkistdc/dkist-processing-vbi/pull-requests/18>`__)
