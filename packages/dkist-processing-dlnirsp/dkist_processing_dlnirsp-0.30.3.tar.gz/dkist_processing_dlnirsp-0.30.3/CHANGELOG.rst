v0.30.3 (2025-09-02)
====================

Misc
----

- Update pre-commit hook versions and replace python-reorder-imports with isort. (`#106 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/106>`__)
- Update `dkist-processing-common` to allow instrument level changes to cadence-related keywords when writing L1 data. (`#107 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/107>`__)
- Update `dkist-processing-math` to remove a deprecated package dependency. (`#107 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/107>`__)


v0.30.2 (2025-08-12)
====================

Misc
----

- Update some pre-commit hook versions. (`#103 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/103>`__)
- Update verion of `dkist-processing-common` to v11.2.1 to fix bug that caused Wavecal quality metrics to not be rendered in Quality Reports.
  Also bump `dkist-quality` to v2.0.0 for the same reason. (`#105 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/105>`__)


v0.30.1 (2025-07-28)
====================

Misc
----

- Update `solar-wavelength-calibration` to allow retries when failing to get atlas data. (`#104 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/104>`__)


v0.30.0 (2025-07-18)
====================

Bugfixes
--------

- Update `dkist-processing-common` to include the results of wavelength calibration when determining spectral lines in the data. (`#102 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/102>`__)


v0.29.1 (2025-07-15)
====================

Misc
----

- Replace `FakeGQLClient` with the `fake_gql_client` fixture imported from the `mock_metadata_store` module
  in `dkist-processing-common`.  Because the fixture is imported into `conftest.py`, individual imports are not needed. (`#98 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/98>`__)


v0.29.0 (2025-07-10)
====================

Bugfixes
--------

- Update the DL-NIRSP workflows such that the `SubmitDatasetMetadata` task is now dependent on the `AssembleDlnirspMovie` task. This ensures that the metadata is submitted only after the movie has been assembled and that it is counted in downstream checks. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/101>`__)


Misc
----

- Update dkist-processing-common to handle non-finite values in quality wavecal metrics. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/101>`__)


v0.28.2 (2025-07-08)
====================

Misc
----

- Update dkist-inventory to 1.9.0 in order to stay current with production generation of inventory and metadata.asdf files in trial workflows. (`#100 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/100>`__)


v0.28.1 (2025-07-07)
====================

Bugfixes
--------

- Remove duplicate `normalize_kernel` kwarg in call to `interpolate_replace_nans` in the `WavelengthCalibration` task. (`#98 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/98>`__)


v0.28.0 (2025-07-03)
====================

Features
--------

- Add the `WavelengthCalibration` task, which computes an absolute wavelength solution that is encoded in L1 headers. (`#94 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/94>`__)


Misc
----

- Clean up the imports of `BadPixelCalibration` and `IfuDriftCalibration` into workflows. They are now imported directly from `.tasks`. (`#94 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/94>`__)


Documentation
-------------

- Add online documentation page for new `WavelengthCalibration` task. (`#94 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/94>`__)


v0.27.1 (2025-07-02)
====================

Misc
----

- Update `dkist-processing-common` to v11.0.0 and update affected `Stem`'s for the new API. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/97>`__)
- Bump `dkist-quality`. This update contains machinery for plotting wavelength calibration results, which DLNIRSP doesn't use.... yet. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/97>`__)


v0.27.0 (2025-06-26)
====================

Features
--------

- Increase permissiveness of valid IFU drift amounts. We now allow any groups *within the drift amount of the array edge*
  to change their size. Previously, we had only allowed groups right on the edge of the array to change. (`#91 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/91>`__)
- Allow demodulation matrices to *not* be fit spatially in the :py:meth:`InstrumentPolarizationCalibration <dkist_processing_dlnirsp.tasks.instrument_polarization.InstrumentPolarizationCalibration.fit_demodulation_matrices_by_group>`
  task. To turn off the fit set the "dlnirsp_polcal_demodulation_spatial_poly_fit_order" parameter to -1. (`#95 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/95>`__)


Bugfixes
--------

- Ensure that the IFU drift amount keeps the same number of spatial pixels in pairs of groups from the 2 polarimetric beams. (`#91 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/91>`__)


v0.26.1 (2025-06-25)
====================

Misc
----

- Update dkist-inventory to 1.8.4 in order to avoid a bug in the generation of inventory and metadata.asdf files in trial workflows. (`#96 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/96>`__)


v0.26.0 (2025-06-23)
====================

Features
--------

- Save a remapped version of the Bad Pixel Map so a user can identify the, now masked, bad pixels in L1 data. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/92>`__)
- Make bad pixels in `ScienceCalibration` task. L1 data no-longer show NaN at bad pixel locations. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/92>`__)


Bugfixes
--------

- Bad pixel map is now correctly saved as a binary (0 and 1) array. Previously it could have had values as high as 3. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/92>`__)


v0.25.0 (2025-06-03)
====================

Features
--------

- Add ability to linearize data from both "SubFrame" camera readout mode and "UpTheRamp" camera readout mode combined with "Discrete" modulator spin mode. (`#71 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/71>`__)
- Add application of correction polynomial to all linearization algorithms, including the existing UpTheRamp Continuous algorithm. (`#71 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/71>`__)
- Harden IFU drift calculation against NaN values in Solar Gain image. (`#71 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/71>`__)


Misc
----

- Remove `DlnirspLinearityTaskBase` base class. The `LinearityCorrection` now has parameters and therefore uses the
  standard `DlnirspTaskBase` base. (`#71 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/71>`__)


Documentation
-------------

- Add exact, mathematical definitions for linearization algorithms. (`#71 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/71>`__)


v0.24.6 (2025-06-02)
====================

Misc
----

- Remove use of input dataset mixin imported from dkist-processing-common. (`#80 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/80>`__)


v0.24.5 (2025-05-30)
====================

Misc
----

- Update `dkist-fits-specifications` to v4.17.0


v0.24.4 (2025-05-28)
====================

Misc
----

- Update `dkist-processing-common` to v10.8.3 (`#93 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/93>`__)


v0.24.3 (2025-05-27)
====================

Misc
----

- Update `dkist-processing-common` to v10.8.2 (`#90 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/90>`__)


v0.24.2 (2025-05-23)
====================

Misc
----

- Update dkist-processing-common dependency to v10.8.1 (`#89 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/89>`__)


v0.24.1 (2025-05-21)
====================

Misc
----

- Update dkist-fits-specifications dependency to v4.16.0. (`#88 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/88>`__)


v0.24.0 (2025-05-15)
====================

Misc
----

- Updating dependencies to cross astropy 7.0.0 and numpy 2.0.0. (`#87 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/87>`__)


v0.23.5 (2025-05-06)
====================

Misc
----

- Update dkist-fits-specifications to add the `THEAP` keyword. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/86>`__)


v0.23.4 (2025-05-01)
====================

Misc
----

- Use the latest version of dkist-inventory for trial workflow inventory and metadata ASDF generation. (`#85 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/85>`__)


v0.23.3 (2025-04-24)
====================

Misc
----

- Use the latest version of dkist-inventory for trial workflow inventory and metadata ASDF generation. (`#84 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/84>`__)


v0.23.2 (2025-04-21)
====================

Misc
----

- Bump dkist-processing-common to v10.7.2, which fixes a bug that required the AO_LOCK keyword to be present in the headers. (`#83 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/83>`__)


v0.23.1 (2025-04-21)
====================

Bugfixes
--------

- Update the value of "BUNIT" key in L1 headers.
  L1 pixels do not have units because their values are relative to disk center at the time of solar gain observation. (`#79 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/79>`__)


Misc
----

- Remove our own version of `PolcalTaskFlower` and import the identical object from `dkist-processing-common` (even though we did it first :p). (`#78 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/78>`__)


Documentation
-------------

- Update online `L1 Science Calibration docs <https://docs.dkist.nso.edu/projects/dl-nirsp/en/latest/science_calibration.html>`_
  to include information about the units of L1 science frames. (`#79 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/79>`__)


v0.23.0 (2025-04-17)
====================

Misc
----

- Add missing build dependency specifications. (`#81 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/81>`__)
- Update dkist-processing-common to only remove level 0 header keys from the level 1 files. (`#82 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/82>`__)


v0.22.5 (2025-03-31)
====================

Bugfixes
--------

- Update dkist-processing-common to v10.6.4 to fix a bug in writing L1 frames when input dataset parts are missing. (`#77 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/77>`__)


v0.22.4 (2025-03-27)
====================

Bugfixes
--------

- Update dkist-processing-common to v10.6.3 to fix a bug when input dataset parts are missing. (`#76 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/76>`__)


v0.22.3 (2025-03-21)
====================

Misc
----

- Add code coverage badge to README.rst. (`#74 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/74>`__)
- Bump `dkist-inventory` to v1.7.0, which adds support for sparse mosaics to Trial tasks. Probably doesn't affect DLNIRSP, but nice to stay up to date. (`#75 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/75>`__)


v0.22.2 (2025-03-19)
====================

Misc
----

- Fix bug that caused some tests to incorrectly fail depending on how they were assigned to xdist workers. (`#72 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/72>`__)
- Bump dkist-processing-common to v10.6.2, which fixes a bug in manual processing. (`#73 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/73>`__)


v0.22.1 (2025-03-14)
====================

Misc
----

- Bump dkist-processing-common to v10.6.1 (`#70 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/70>`__)


v0.22.0 (2025-03-03)
====================

Features
--------

- Information about the initial set of values (e.g., the name of the GOS retarder) to use when fitting demodulation
  matrices now comes directly from the headers of the POLCAL task data instead of being a pipeline parameter.
  This allows different proposals to use different GOS optics without the need for parameter changes. (`#69 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/69>`__)


v0.21.6 (2025-02-26)
====================

Misc
----

- Update `dkist-processing-common` to use version 2.10.5 of `apache-airflow. (`#68 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/68>`__)


v0.21.5 (2025-02-24)
====================

Bugfixes
--------

- Make the `IFUDriftCalibration` task a workflow dependency for the `BadPixelCalibration` task.
  The bad pixel task needs the drifted group ID array to get the illuminated portion of the lamp gain frame. (`#63 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/63>`__)
- Use new `stddev_numpy_arrays` from `dkist-processing-math` to compute dynamic bad pixel mask from a large stack of dark frames.
  The old method of using `numpy.std` could easily cause an out-of-memory failure because it needed to load all arrays into memory at once. (`#65 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/65>`__)
- Make the amount CRPIX[12] values are rounded *only when sorting mosaic tiles* a pipeline parameter. (`#66 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/66>`__)


v0.21.4 (2025-02-19)
====================

Misc
----

- Bump `dkist-processing-common` to 10.5.14, which computes PRODUCT when creating L1 FITS headers. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/67>`__)


v0.21.3 (2025-02-14)
====================

Misc
----

- Add Bitbucket pipeline steps to check that full dependencies were correctly frozen. (`#62 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/62>`__)
- Bump version of `dkist-processing-common` to bring along new version of `dkist-processing-core` that uses frozen dependencies for pipeline install. (`#62 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/62>`__)


v0.21.2 (2025-02-12)
====================

Misc
----

- Bump `dkist-inventory` to 1.6.1. (`#64 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/64>`__)
- Bump `dkist-processing-common` to 10.5.12, which increases the DSETID to 6 characters. (`#64 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/64>`__)


v0.21.1 (2025-02-10)
====================

Features
--------

- Bump `dkist-fits-specifications` to 4.11.0, which adds the L1 PRODUCT keyword. (`#61 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/61>`__)


v0.21.0 (2025-02-06)
====================

Features
--------

- All mosaiced datasets will always have MAXIS = 2 in L1 headers, even if the mosaic only has one dimension.
  MAXIS[12] = 1 will be used to represent static axes. (`#57 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/57>`__)
- L1 mosaic index header keys are now correctly populated based on absolute orientation determined from WCS information (CPRIX).
  Previously they had been based on the DLNIRSP spatial step pattern keys, which were relative and could vary drastically depending on the spatial step pattern used. (`#57 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/57>`__)


Misc
----

- Bump some minimum dependencies for compatibility with new versions of `dkist-inventory` and `dkist-processing-common`. (`#57 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/57>`__)


v0.20.5 (2025-02-04)
====================

Features
--------

- Remove three read/write mixins for tasks: intermediate frame, linearized frame, and input frame.
  Replace the functionality of those mixins with a combination of the standard read and write methods
  from `dkist-processing-common` and new composite tags for intermediate frames and linearized frames. (`#59 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/59>`__)


v0.20.4 (2025-01-29)
====================

Misc
----

- Update dkist-processing-common and dkist-quality to manage a bug present in dacite 1.9.0.
- Update Bitbucket pipelines to use execute script for standard steps. (`#60 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/60>`__)


v0.20.3 (2025-01-27)
====================

Misc
----

- Update bitbucket pipelines to use common scripts for checking for changelog snippets and verifying doc builds. (`#58 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/58>`__)
- Update dkist-processing-common to remove some deprecated packages.


v0.20.2 (2025-01-09)
====================

Misc
----

- Update dkist-inventory to change dataset inventory parsing logic in trial workflows.


v0.20.1 (2025-01-09)
====================

Misc
----

- Update dkist-processing-common to pull in the new version of airflow.


v0.20.0 (2025-01-03)
====================

Features
--------

- Add task to compute bad pixel maps based on static arrays provided by DL team and (for IR only) dynamically discovered
  pixels based on average lamp data and the standard deviation of dark frames. (`#52 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/52>`__)


v0.19.1 (2024-12-20)
====================

Documentation
-------------

- Change the documentation landing page to focus more on users and less on developers. (`#53 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/53>`__)


v0.19.0 (2024-12-20)
====================

Features
--------

- Add framework for applying corrections to known inaccuracies in the L0 WCS header values.
  The framework allows for arbitrary corrections to both the PC matrix and CRPIX values, and are parameterized with pipeline parameters. (`#54 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/54>`__)


v0.18.1 (2024-12-18)
====================

Features
--------

- Bump common to remove Fried parameter from the L1 headers and the quality metrics where the AO system is unlocked. (`#56 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/56>`__)


Misc
----

- Update Bitbucket pipelines to use standardized lint and scan steps. (`#55 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/55>`__)


v0.18.0 (2024-12-04)
====================

Features
--------

- Improve preserving relative scaling of slitbeams in final gain image. See Science Changelog for more information. (`#50 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/50>`__)


Misc
----

- Update "solar gain as science" local trial workflow to support polarimetric input/output data. (`#49 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/49>`__)
- Pin `sphinx-autoapi` to v3.3.3 to avoid `this issue <https://github.com/readthedocs/sphinx-autoapi/issues/505>`_ until it is fixed. (`#51 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/51>`__)


Documentation
-------------

- Add individual online documentation pages for important pipeline steps.
  These pages are found `here <https://docs.dkist.nso.edu/projects/dl-nirsp/en/latest/>`_. (`#46 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/46>`__)
- Make all private methods public so they (and their docstrings) are shown on online documentation. (`#47 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/47>`__)


v0.17.4 (2024-11-26)
====================

Misc
----

- Bumping dkist-fits-specification to v4.10.0 and dkist-processing-common to v10.5.3 (`#48 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/48>`__)
- Write the CNAMEn keywords to the instrument headers. (`#48 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/48>`__)


v0.17.3 (2024-11-21)
====================

Bugfixes
--------

- Update dkist-inventory and dkist-processing-common to fix a bug in producing dataset inventory from the SPECLN* keys


v0.17.2 (2024-11-20)
====================

Bugfixes
--------

- Update dkist-processing-common to constrain asdf < 4.0.0


v0.17.1 (2024-11-20)
====================

Misc
----

- Update dkist-processing-common to manage breaking API changes in asdf and moviepy.


v0.17.0 (2024-11-14)
====================

Misc
----

- Replace `TransferDlnirspTrialData` with `TransferTrialData` from dkist-processing-common. (`#44 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/44>`__)


v0.16.0 (2024-10-30)
====================

Features
--------

- Add ability to determine order of X/Y mosaic step loops.
  Understanding the loop order is crucial for correctly slicing the mosaic when observations were aborted. (`#45 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/45>`__)


v0.15.1 (2024-10-22)
====================

Bugfixes
--------

- Don't require the presence of DARK task frames with an exposure time matching that of the POLCAL task frames.
  POLCAL frames are corrected with their own darks that are taken as part of the polcal sequence and are given the POLCAL task type. (`#43 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/43>`__)


v0.15.0 (2024-10-15)
====================

Features
--------

- Compute demodulation matrices separately for each spatial pixel and then fit the demodulation matrices as a function
  of spatial pixel within each group. (`#39 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/39>`__)
- Allow groups that border the edges of the array to have their area changed by IFU drifts. (`#40 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/40>`__)


v0.14.3 (2024-10-14)
====================

Misc
----

- Switch from setup.cfg to pyproject.toml for build configuration (`#41 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/41>`__)
- Make and publish wheels at code push in build pipeline (`#41 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/41>`__)


v0.14.2 (2024-10-07)
====================

Misc
----

- Bump dkist-fits-specifications to v4.7.0. This adjusted the TTBLTRCK allowed values, adjusted CRSP_051 and CRSP_052 to accommodate blocking filters,adjusted CRSP_073 to include a new grating, and added a new allowed value to CAM__044. (`#47 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/47>`__)


v0.14.1 (2024-10-01)
====================

Bugfixes
--------

- Make `IfuDriftCalibration` a workflow dependency of the `InstrumentPolarizationCalibration` task. (`#38 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/38>`__)


v0.14.0 (2024-10-01)
====================

Features
--------

- Account for the slow drift over time of the IFU in the FOV by measuring the offset between stored IFU metrology arrays,
  which are used during calibration, and the dataset currently being processed. (`#36 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/36>`__)


v0.13.0 (2024-10-01)
====================

Features
--------

- Add support for "dither" mode where each full mosaic is repeated a second time with a slight offset. (`#31 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/31>`__)


v0.12.1 (2024-09-27)
====================

Misc
----

- Bump `dkist-processing-common` to v10.2.1. This fixes a documentation build bug in Airflow.


v0.12.0 (2024-09-27)
====================

Misc
----

- Bump `dkist-processing-common` to v10.2.0. This includes upgrading to the latest version of Airflow (2.10.2).


v0.11.2 (2024-09-26)
====================

Misc
----

- Bump `dkist-processing-common` to v10.1.0. This enables the usage of the `NearFloatBud` and `TaskNearFloatBud` in parsing.


v0.11.1 (2024-09-24)
====================

Misc
----

- Bump `dkist-processing-common` to v10.0.1. This fixes a bug in the reported FRAMEVOL key in L1 headers. (`#37 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/37>`__)


v0.11.0 (2024-09-23)
====================

Features
--------

- Reorder task dependencies in workflows. Movie and L1 quality tasks are no longer dependent on the presence of OUTPUT
  frames and thus can be run in parallel with the `WriteL1` task. (`#34 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/34>`__)


Misc
----

- Use CALIBRATED instead of OUTPUT frames in post-science movie and quality tasks. This doesn't change their output at all
  (the arrays are the same), but it's necessary for `dkist-processing-common >= 10.0.0` that will break using OUTPUT frames. (`#34 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/34>`__)


v0.10.1 (2024-09-19)
====================

Misc
----

- Bump `dkist-quality` to v1.1.1. This fixes raincloud plot rendering in trial workflows. (`#35 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/35>`__)


v0.10.0 (2024-09-11)
====================

Misc
----

- Accommodate changes to the GraphQL API associated with refactoring the quality database (`#33 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/33>`__)


v0.9.1 (2024-09-09)
===================

Misc
----

- Use High Memory worker for `InsturmentPolarizationCalibration` task.
  Writing the VIS demodulation matrices to disk is causing some memory issues on STAGE. (`#32 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/32>`__)


v0.9.0 (2024-09-09)
===================

Bugfixes
--------

- Perform Calibration Unit (CU) and demodulation matrix fits separately for each of the two polarized beams (instead of a
  single CU fit with the average of both beams). (`#30 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/30>`__)


v0.8.0 (2024-09-04)
===================

Features
--------

- Add support for multiple coadds in linearization task. (`#28 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/28>`__)
- Add camera-sample-sequence-based checks of ramp validity during linearization task. (`#29 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/29>`__)


v0.7.1 (2024-08-21)
===================

Misc
----

- Update some Quality related tasks and methods for the new API in `dkist-processing-common` v9.0.0. (`#27 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/27>`__)


Documentation
-------------

- Description of polcal bins in quality report no longer needs to include a dummy dimension. (`#27 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/27>`__)


v0.7.0 (2024-08-19)
===================

Features
--------

- Update linearity correction to average initial bias frames if more than one is found. Uses the last read NDR as opposed to the last NDR, which may be a bias NDR. (`#22 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/22>`__)


v0.6.4 (2024-08-15)
===================

Misc
----

- Move to version 4.6.0 of `dkist-fits-specifications` to correct allowed values of the TTBLTRCK header keyword.


v0.6.3 (2024-08-12)
===================

Misc
----

- Move to version 4.5.0 of `dkist-fits-specifications` which includes `PV1_nA` keys for non linear dispersion.


v0.6.2 (2024-08-05)
===================

Documentation
-------------

- Add pre-commit hook for documentation and edit README.rst. (`#18 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/18>`__)


v0.6.1 (2024-08-01)
===================

Misc
----

- Remove the loops from linear interpolation in remapping the ifu cube in order to speed up the code. (`#17 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/17>`__)


v0.6.0 (2024-07-30)
===================

Features
--------

- Update solar gain algorithm to compute a single characteristic spectrum across *all* slitbeams. This helps mitigate
  strong spectral gain feautres that exist across the entire spatial extent of a single slitbeam. (`#25 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/25>`__)


Bugfixes
--------

- Update "Avg Noise" QA metric computation to avoid errors caused by infinity values in the data. (`#16 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/16>`__)
- Calibrated L1 data no longer have large regions of all-NaN data at start and end of wavelength axis. This was fixed by
  constraining the reference "wavelength" axis to exclude regions with a large fraction of NaN values (the specific fraction is a parameter). (`#19 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/19>`__)
- Correctly parse the number of X/Y_tiles in cases where aborts lead to only a single complete mosaic/X_tile.
  This was very unlikely to happen in practice, but does come up in some of our tests. (`#20 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/20>`__)
- IFU cubes now have the correct spatial axis ordering. Previously the difference between numpy and cartesian ordering
  had caused the output spatial axes to be swapped. (`#21 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/21>`__)
- Preserve slitbeam scale differences in final solar gain image. This ensures that these real differences are corrected
  when the solar gain is applied to science data. (`#25 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/25>`__)


Misc
----

- Add DEBUG output to Science task that contains the stack slit spectra just prior to IFU remapping (called "SLIT_STACKED"). (`#25 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/25>`__)


v0.5.3 (2024-07-26)
===================

Misc
----

- Update dkist-processing-common to v8.2.2 to fix some warning messages. (`#24 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/24>`__)


v0.5.2 (2024-07-19)
===================

Misc
----

- Move to version 4.4.2 of `dkist-fits-specifications` which includes the `PVi_j` keywords.


v0.5.1 (2024-07-15)
===================

Bugfixes
--------

- Use `TrialTeardown` task in trial workflow. This task sets the recipe run status to TRIALSUCCESS. (`#15 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/15>`__)


v0.5.0 (2024-07-15)
===================

Features
--------

- L1 output files are now fully remapped IFU cubes! (`#8 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/8>`__)
- Add trial workflow for processing data without activating downstream Data Center services. This is useful for
  making "official" L1 data for assessing the performance of the pipeline. (`#10 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/10>`__)
- Add the `TransferDlnirspTrialData` task. This task is used to collect a set of file produced during a pipeline run
  and move them to a permanent location outside of the local (and ephemeral) scratch. (`#10 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/10>`__)


Misc
----

- Build and upload the Manual Processing Worker (mpw) notebooks as part of the Bitbucket release pipeline. (`#11 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/11>`__)
- Local trial workflows that don't depend on OBSERVE frames (solar-gain-as-science and polcal-as-science) now produce
  the full set of L1 outputs (except the inventory ASDF). (`#12 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/12>`__)
- Bump `dkist-quality` to version 1.1.0. (`#14 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/14>`__)


v0.4.0 (2024-07-12)
===================

Bugfixes
--------

- Correctly mock/populate OBS_IP_START_TIME in local trial workflows that don't use Observe frames. (`#9 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/9>`__)


Misc
----

- Move to version 8.2.1 of `dkist-processing-common` which includes the publication of select private methods for documentation purposes. (`#13 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/13>`__)


v0.3.0 (2024-07-01)
===================

Misc
----

- Move to version 8.1.0 of `dkist-processing-common` which includes an upgrade to airflow 2.9.2. (`#7 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/7>`__)


v0.2.1 (2024-06-25)
===================

Misc
----

- Remove High Memory Worker requirement from `InstrumentPolarizationCalibration` task. (Should have been part of `PR #4 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/4>`__)
- Pin `twine` to non-breaking version in BitBucket pipeline

v0.2.0 (2024-06-25)
===================

Features
--------

- Greatly reduce memory requirements of `InstrumentPolarizationCalibration` task (and speed it up a little bit, too). (`#4 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/4>`__)


Misc
----

- Use `nd_left_matrix_multiply` from `dkist-processing-math` and remove the local Mixin that had this method. (`#1 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/1>`__)
- Don't initialize a `parameters` object `DlnirspLinearityTaskBase`; we don't use parameters in Linearization. (`#1 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/1>`__)
- Update for new usage of `_find_most_recent_past_value` now requiring `obs_ip_start_time` or explicit time.
- Use `asdf` codecs from `dkist-processing-common` instead of locally defined codecs (they were the same). (`#1 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/1>`__)
- Use `ParameterArmIdMixin` and `_load_param_value_from_fits` from `dkist-processing-common` (they're identical). (`#1 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/1>`__)
- Update all non-DKIST dependencies (and `dkist-processing-pac`) to current versions. (`#2 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/2>`__)
- Remove crufty "build_docs" and "upload_docs" from setup.cfg. (`#2 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/2>`__)
- Put `GroupIdMixin` on `DlnirspTaskBase` instead of using it separately for each Task class. This also helps
  soften the dependencies of the `CorrectionsMixin` on `GroupIdMixin` because now the presence of the `group_id_*` methods
  is guaranteed. (`#3 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/3>`__)
- Use pre-defined `*Tag.task_FOO()` tags and controlled `TaskName.foo` values, when available. (`#5 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/5>`__)


v0.1.1 (2024-06-12)
===================

Misc
----

- Bump `dkist-fits-specifications` to v4.3.0. We need this in DL-NIRSP so some dither-related keywords are no longer required.
  (They are only present if dithering is used). (`#6 <https://bitbucket.org/dkistdc/dkist-processing-dlnirsp/pull-requests/6>`__)


v0.1.0 (2024-06-06)
===================

- Initial release. Mostly for first release to DC stacks (i.e., not "production" quality).
