v1.12.2 (2025-09-02)
====================

Bugfixes
--------

- Update CADENCE-related and XPOSURE headers to take the instrument mode into account. (`#216 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/216>`__)


Misc
----

- Update `dkist-processing-common` to allow instrument level changes to cadence-related keywords when writing L1 data. (`#216 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/216>`__)
- Update `dkist-processing-math` to remove a deprecated package dependency. (`#216 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/216>`__)
- Update pre-commit hook versions and replace python-reorder-imports with isort. (`#217 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/217>`__)


v1.12.1 (2025-08-12)
====================

Misc
----

- Update verion of `dkist-processing-common` to v11.2.1 to fix bug that caused Wavecal quality metrics to not be rendered in Quality Reports.
  Also bump `dkist-quality` to v2.0.0 for the same reason. (`#215 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/215>`__)


v1.12.0 (2025-07-30)
====================

Features
--------

- Enable handling of single-map, single-step observations with repeated measurements that end in an abort. (`#212 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/212>`__)


Misc
----

- Update some pre-commit hook versions. (`#213 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/213>`__)


v1.11.1 (2025-07-28)
====================

Misc
----

- Update `solar-wavelength-calibration` to allow retries when failing to get atlas data. (`#214 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/214>`__)


v1.11.0 (2025-07-18)
====================

Bugfixes
--------

- Calculate the `WAVEMIN` and `WAVEMAX` after correcting the spectral WCS keys instead of before. (`#200 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/200>`__)
- Update `dkist-processing-common` to include the results of wavelength calibration when determining spectral lines in the data. (`#211 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/211>`__)


v1.10.1 (2025-07-15)
====================

Misc
----

- Replace `FakeGQLClient` with the `fake_gql_client` fixture imported from the `mock_metadata_store` module
  in `dkist-processing-common`.  Because the fixture is imported into `conftest.py`, individual imports are not needed. (`#208 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/208>`__)


v1.10.0 (2025-07-14)
====================

Features
--------

- This change pulls the dispersion axis correction out of the Cryonirsp pipeline and uses the generalized solar-wavelength-calibration library. (`#167 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/167>`__)


v1.9.0 (2025-07-10)
===================

Bugfixes
--------

- Update the CRYO-NIRSP workflows such that the `SubmitDatasetMetadata` task is now dependent on the `AssembleCryonirspMovie` task. This ensures that the metadata is submitted only after the movie has been assembled and that it is counted in downstream checks. (`#210 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/210>`__)


Misc
----

- Update dkist-processing-common to handle non-finite values in quality wavecal metrics. (`#210 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/210>`__)


v1.8.3 (2025-07-08)
===================

Misc
----

- Update dkist-inventory to 1.9.0 in order to stay current with production generation of inventory and metadata.asdf files in trial workflows. (`#209 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/209>`__)


v1.8.2 (2025-07-02)
===================

Misc
----

- Bump `dkist-quality`. This update contains machinery for plotting wavelength calibration results. (`#207 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/207>`__)
- Update `dkist-processing-common` to v11.0.0. This requires updating affected `Stem`'s for the new API and changing to imported location of `location_of_dkist`.
  With the new `location_of_dkist` we can also remove its re-definition in the `SPDispersionAxisCorrection` task. (`#207 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/207>`__)


v1.8.1 (2025-06-25)
===================

Misc
----

- Update dkist-inventory to 1.8.4 in order to avoid a bug in the generation of inventory and metadata.asdf files in trial workflows. (`#206 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/206>`__)


v1.8.0 (2025-06-16)
===================

Bugfixes
--------

- Update the beam alignment code to handle edge effects in determining the shift required to align beams one and two. The final spectra passed to the cross correlation method are now cropped by removing the outside 10% of pixels on each edge. (`#195 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/195>`__)


v1.7.7 (2025-06-02)
===================

Misc
----

- Remove use of input dataset mixin imported from dkist-processing-common. (`#190 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/190>`__)


v1.7.6 (2025-05-30)
===================

Misc
----

- Update `dkist-fits-specifications` to v4.17.0 (`#205 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/205>`__)


v1.7.5 (2025-05-28)
===================

Misc
----

- Update `dkist-processing-common` to v10.8.3 (`#204 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/204>`__)


v1.7.4 (2025-05-27)
===================

Misc
----

- Update `dkist-processing-common` to v10.8.2 (`#203 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/203>`__)


v1.7.3 (2025-05-23)
===================

Misc
----

- Update `dkist-processing-common` to v10.8.1. (`#202 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/202>`__)
- Explicitly specify types on beam boundary values due to type issues with the `largestinteriorrectangle` package. (`#202 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/202>`__)
- Update `numpy` to v2.2.5. (`#202 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/202>`__)


v1.7.2 (2025-05-21)
===================

Bugfixes
--------

- Update unit tests for slightly modified API in `dkist-data-simulator`;
  instrument name must be "cryonirsp" without a hyphen (`#199 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/199>`__)


v1.7.1 (2025-05-21)
===================

Misc
----

- Update dkist-fits-specifications dependency to v4.16.0. (`#201 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/201>`__)


v1.7.0 (2025-05-15)
===================

Misc
----

- Updating dependencies to cross astropy 7.0.0. (`#198 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/198>`__)


v1.6.5 (2025-05-06)
===================

Misc
----

- Update dkist-fits-specifications to add the `THEAP` keyword. (`#197 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/197>`__)


v1.6.4 (2025-05-01)
===================

Misc
----

- Use the latest version of dkist-inventory for trial workflow inventory and metadata ASDF generation. (`#196 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/196>`__)


v1.6.3 (2025-04-24)
===================

Misc
----

- Use the latest version of dkist-inventory for trial workflow inventory and metadata ASDF generation. (`#194 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/194>`__)


v1.6.2 (2025-04-21)
===================

Misc
----

- Bump dkist-processing-common to v10.7.2, which fixes a bug that required the AO_LOCK keyword to be present in the headers. (`#193 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/193>`__)


v1.6.1 (2025-04-21)
===================

Bugfixes
--------

- Update the value of "BUNIT" key in L1 headers.
  L1 pixels do not have units because their values are relative to disk center at the time of solar gain observation. (`#189 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/189>`__)


Documentation
-------------

- Update online `SP L1 Science Calibration docs <https://docs.dkist.nso.edu/projects/cryo-nirsp/en/latest/sp_science_calibration.html>`_
  (and `CI <https://docs.dkist.nso.edu/projects/cryo-nirsp/en/latest/ci_science_calibration.html>`_)
  to include information about the units of L1 science frames. (`#189 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/189>`__)


v1.6.0 (2025-04-17)
===================

Misc
----

- Add missing build dependency specifications. (`#191 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/191>`__)
- Update dkist-processing-common to only remove level 0 header keys from the level 1 files. (`#192 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/192>`__)


v1.5.5 (2025-03-31)
===================

Bugfixes
--------

- Update dkist-processing-common to v10.6.4 to fix a bug in writing L1 frames when input dataset parts are missing. (`#188 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/188>`__)


v1.5.4 (2025-03-27)
===================

Bugfixes
--------

- Update dkist-processing-common to v10.6.3 to fix a bug when input dataset parts are missing. (`#187 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/187>`__)


v1.5.3 (2025-03-21)
===================

Misc
----

- Add code coverage badge to README.rst. (`#185 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/185>`__)
- Bump `dkist-inventory` to v1.7.0. No affect for Cryo, but nice to stay up to date. (`#186 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/186>`__)


v1.5.2 (2025-03-19)
===================

Misc
----

- Bump dkist-processing-common to v10.6.2, which fixes a bug in manual processing. (`#184 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/184>`__)


v1.5.1 (2025-03-14)
===================

Misc
----

- Bump dkist-processing-common to v10.6.1 (`#184 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/184>`__)


v1.5.0 (2025-03-03)
===================

Features
--------

- Information about the initial set of values (e.g., the name of the GOS retarder) to use when fitting demodulation
  matrices now comes directly from the headers of the POLCAL task data instead of being a pipeline parameter.
  This allows different proposals to use different GOS optics without the need for parameter changes. (`#182 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/182>`__)


v1.4.23 (2025-02-26)
====================

Misc
----

- Update `dkist-processing-common` to use version 2.10.5 of `apache-airflow. (`#181 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/181>`__)


v1.4.22 (2025-02-24)
====================

Misc
----

- Bump `dkist-processing-math` to v2.2.0 (`#180 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/180>`__)


v1.4.21 (2025-02-19)
====================

Misc
----

- Bump `dkist-processing-common` to 10.5.14, which computes PRODUCT when creating L1 FITS headers. (`#179 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/179>`__)


v1.4.20 (2025-02-14)
====================

Misc
----

- Bump version of `dkist-processing-common` to bring along new version of `dkist-processing-core` that uses frozen dependencies for pipeline install. (`#177 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/177>`__)
- Add Bitbucket pipeline steps to check that full dependencies were correctly frozen. (`#177 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/177>`__)


v1.4.19 (2025-02-12)
====================

Misc
----

- Bump `dkist-processing-common` to 10.5.12, which increases the DSETID to 6 characters. (`#178 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/178>`__)
- Bump `dkist-inventory` to 1.6.1. (`#178 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/178>`__)


v1.4.18 (2025-02-10)
====================

Features
--------

- Bump `dkist-fits-specifications` to 4.11.0, which adds the L1 PRODUCT keyword. (`#176 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/176>`__)


v1.4.17 (2025-02-06)
====================

Misc
----

- Bump `dkist-inventory` and `dkist-processing-common` for non-Cryo related updates.
  Also bump a few minimum versions required by this update. (`#175 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/175>`__)


1.4.11.dev1+g0bcc38b (2025-02-06)
=================================

Misc
----

- Bump `dkist-inventory` and `dkist-processing-common` for non-Cryo related updates.
  Also bump a few minimum versions required by this update. (`#175 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/175>`__)


v1.4.16 (2025-02-04)
====================

Features
--------

- Remove read/write mixins for tasks: intermediate frame, linearized frame, and beam access.
  The functionality of those mixins is replaced with the standard read and write methods
  from `dkist-processing-common` and three new elements: New composite tags for intermediate
  frames, linearized frames, and beam boundary data; New `cryo_fits_access_decoder` and
  `cryo_fits_array_decoder` that optionally slice out the illuminated beam
  portion of the array and take `fits_access_class` arguments;
  New`CryonirspLinearizedFitsAccess` fits access class that inherits from CryonirspL0FitsAccess
  and handles flipping the dispersion axis for the SP arm so that wavelength increases from left
  to right like the other instruments. (`#170 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/170>`__)


Bugfixes
--------

- Remove the lamp gain task from CI local workflows. (`#174 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/174>`__)


Misc
----

- Move the BeamBoundaries dataclass from the beam_boundaries_base task to a new beam_boundaries model module.
  The move allows BeamBoundaries to be used without circular imports. (`#170 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/170>`__)
- Use the existing BeamBoundaries dataclass and new intermediate_beam_boundaries composite tag with
  standard read methods to access beam boundaries where beam slicing is necessary. BeamBoundary objects
  are passed to new decoders to access the illuminated beam portion of the array. (`#170 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/170>`__)


v1.4.15 (2025-01-30)
====================

Bugfixes
--------

- Correct how gain files are read in the PickyBuds during parsing of CRYO-NIRSP CI linearized data. (`#172 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/172>`__)


v1.4.14 (2025-01-29)
====================

Misc
----

- Update dkist-processing-common and dkist-quality to manage a bug present in dacite 1.9.0.


v1.4.13 (2025-01-29)
====================

Features
--------

- Remove lamp gain calibration from the CRYO-NIRSP CI pipeline. (`#168 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/168>`__)


Misc
----

- Update Bitbucket pipelines to use execute script for standard steps. (`#170 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/170>`__)


v1.4.12 (2025-01-27)
====================

Misc
----

- Update bitbucket pipelines to use common scripts for checking for changelog snippets and verifying doc builds. (`#169 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/169>`__)
- Update dkist-processing-common to remove some deprecated packages.


v1.4.11 (2025-01-09)
====================

Misc
----

- Update dkist-inventory to change dataset inventory parsing logic in trial workflows.


v1.4.10 (2025-01-09)
====================

Misc
----

- Update dkist-processing-common to pull in the new version of airflow.


v1.4.9 (2025-01-03)
===================

Bugfixes
--------

- Change units of the grating constant used in calculations as well as in the L1 headers from `mm^-1` to `m^-1`. (`#161 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/161>`__)


v1.4.8 (2024-12-20)
===================

Documentation
-------------

- Change the documentation landing page to focus more on users and less on developers. (`#164 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/164>`__)


v1.4.7 (2024-12-18)
===================

Features
--------

- Bump common to remove Fried parameter from the L1 headers and the quality metrics where the AO system is unlocked. (`#166 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/166>`__)


Misc
----

- Update Bitbucket pipelines to use standardized lint and scan steps. (`#165 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/165>`__)


v1.4.6 (2024-12-05)
===================

Misc
----

- Pin `sphinx-autoapi` to v3.3.3 to avoid `this issue <https://github.com/readthedocs/sphinx-autoapi/issues/505>`_ until it is fixed. (`#163 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/163>`__)


v1.4.5 (2024-11-26)
===================

Misc
----

- Write the CNAMEn keywords to the instrument headers. (`#160 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/160>`__)
- Bumping dkist-fits-specification to v4.10.0 and dkist-processing-common to v10.5.3 (`#160 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/160>`__)


v1.4.4 (2024-11-21)
===================

Misc
----

- This change adds a new pickybud to make sure that the dataset contains both lamp gain frames and solar gain frames (we need both for calibration). If we don't have both types of frames, the pipeline will fail fast. (`#159 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/159>`__)


v1.4.3 (2024-11-21)
===================

Bugfixes
--------

- Update dkist-inventory and dkist-processing-common to fix a bug in producing dataset inventory from the SPECLN* keys


v1.4.2 (2024-11-20)
===================

Bugfixes
--------

- Update dkist-processing-common to constrain asdf < 4.0.0


v1.4.1 (2024-11-20)
===================

Misc
----

- Update dkist-processing-common to manage breaking API changes in asdf and moviepy.


v1.4.0 (2024-11-14)
===================

Misc
----

- Replace `TransferCryoTrialData` with `TransferTrialData` from dkist-processing-common. (`#158 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/158>`__)


v1.3.5 (2024-10-15)
===================

Misc
----

- Bump `dkist-processing-common` to v10.3.0 and `dkist-processing-pac` to v3.1.0, both of which harden polcal fitting against bad input data. (`#157 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/157>`__)


v1.3.4 (2024-10-14)
===================

Misc
----

- Make and publish wheels at code push in build pipeline (`#156 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/156>`__)
- Switch from setup.cfg to pyproject.toml for build configuration (`#156 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/156>`__)


v1.3.3 (2024-10-07)
===================

Misc
----

- Bump dkist-fits-specifications to v4.7.0. This adjusted the TTBLTRCK allowed values, adjusted CRSP_051 and CRSP_052 to accommodate blocking filters,adjusted CRSP_073 to include a new grating, and added a new allowed value to CAM__044. (`#155 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/155>`__)


v1.3.2 (2024-09-30)
===================

Features
--------

- Use the `TaskNearFloatBud` to allow the CRYONIRSP-SP grating position and littrow angle to vary within a given tolerance. (`#153 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/153>`__)


v1.3.1 (2024-09-27)
===================

Misc
----

- Bump `dkist-processing-common` to v10.2.1. This fixes a documentation build bug in Airflow.


v1.3.0 (2024-09-27)
===================

Misc
----

- Bump `dkist-processing-common` to v10.2.0. This includes upgrading to the latest version of Airflow (2.10.2).


v1.2.2 (2024-09-26)
====================

Misc
----

- Bump `dkist-processing-common` to v10.1.0. This enables the usage of the `NearFloatBud` and `TaskNearFloatBud` in parsing.


v1.2.1 (2024-09-24)
===================

Misc
----

- Bump `dkist-processing-common` to v10.0.1. This fixes a bug in the reported FRAMEVOL key in L1 headers. (`#154 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/154>`__)


v1.2.0 (2024-09-23)
===================

Features
--------

- Reorder task dependencies in workflows. Movie and L1 quality tasks are no longer dependent on the presence of OUTPUT
  frames and thus can be run in parallel with the `WriteL1` task. (`#152 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/152>`__)


Misc
----

- Use CALIBRATED instead of OUTPUT frames in post-science movie and quality tasks. This doesn't change their output at all (the arrays are the same), but
  it's necessary for `dkist-processing-common >= 10.0.0` that will break using OUTPUT frames. (`#151 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/151>`__)
- Remove `AssembleCryonirspMovie` as workflow dependency on `SubmitDatasetMetadata`. This dependency has been unnecessary
  since the introduction of `SubmitDatasetMetadata` in v0.0.60. (`#151 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/151>`__)


v1.1.2 (2024-09-19)
===================

Misc
----

- Bump `dkist-quality` to v1.1.1. This fixes raincloud plot rendering in trial workflows. (`#152 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/152>`__)


v1.1.1 (2024-09-18)
===================

Bugfixes
--------

- Add validation in linearity_correction task to ensure that the value of NUM_FRAMES_IN_RAMP is the same
  across all frames in a ramp, and that the value of NUM_FRAMES_IN_RAMP actually matches the number of frames found. (`#147 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/147>`__)
- When writing linearized frames, use a fixed tag list as opposed to one derived from L0 data to alleviate load on redis. (`#148 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/148>`__)


v1.1.0 (2024-09-10)
===================

Misc
----

- Accommodate changes to the GraphQL API associated with refactoring the quality database (`#150 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/150>`__)


v1.0.1 (2024-09-06)
===================

Bugfixes
--------

- Don't save two identical versions of the polcal metric that lists the values kept fix in the CU fits. (`#149 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/149>`__)


v1.0.0 (2024-08-21)
===================

Misc
----

- CRYO-NIRSP processing pipeline data accepted for release to the community.


v0.0.82 (2024-08-21)
====================

Misc
----

- Update some Quality related tasks and methods for the new API in `dkist-processing-common` v9.0.0. No change to any outputs. (`#146 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/146>`__)


v0.0.81 (2024-08-16)
====================

Bugfixes
--------

- Correct derivation of PCi_j header keys in CRYO-NIRSP CI runs. (`#145 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/145>`__)


v0.0.80 (2024-08-15)
====================

Bugfixes
--------

- Use arm-specific Parsing tasks from v0.0.78 in local trial (AKA GROGU) workflows as well. (`#143 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/143>`__)
- Re-activate `CryonirspL0QualityMetrics` task in "l0_to_l1" local trial workflow. (`#143 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/143>`__)
- Correctly load a saved SP Dispersion Axis calibration when running local trial workflows. (`#143 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/143>`__)
- Move to version 4.6.0 of `dkist-fits-specifications` to correct allowed values of the TTBLTRCK header keyword.



Misc
----

- Make private methods public where documentation needs to be generated. (`#144 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/144>`__)


v0.0.79 (2024-08-12)
====================

Misc
----

- Move to version 4.5.0 of `dkist-fits-specifications` which includes `PV1_nA` keys for non linear dispersion.


v0.0.78 (2024-08-09)
====================

Misc
----

- Make parsing of some header keys arm specific. (`#142 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/142>`__)


v0.0.77 (2024-08-07)
====================

Features
--------

- Add calibration task to compute accurate header values for
  CTYPE1, CUNIT1, CRPIX1, PV1_0, PV1_1, PV1_2, CRVAL1, CDELT1, PV1_2,
  CTYPE1A, CUNIT1A, CRPIX1A, PV1_0A, PV1_1A, PV1_2A, CRVAL1A, CDELT1A, PV1_2A.

  This is done by shifting the raw wavelength value (CRVAL1/A) to align with the FTS atlas, and
  then fitting a model to infer and correct the values of the aforementioned headers. (`#110 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/110>`__)


v0.0.76 (2024-08-05)
====================

Documentation
-------------

- Add pre-commit hook for documentation, add missing workflow documentation and update README.rst. (`#139 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/139>`__)


v0.0.75 (2024-07-31)
====================

Features
--------

- This change corrects the CryoNIRSP SP helioprojective and equatorial spatial coordinates and writes these to the Level 1 headers. (`#135 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/135>`__)


v0.0.74 (2024-07-25)
====================

Misc
----

- Rewrite to eliminate warnings in unit tests. (`#140 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/140>`__)


v0.0.73 (2024-07-19)
====================

Misc
----

- Move to version 4.2.2 of `dkist-fits-specifications` which includes `PV1_n` keys for non linear dispersion.



v0.0.72 (2024-07-12)
====================

Misc
----

- Move to version 8.2.1 of `dkist-processing-common` which includes the publication of select private methods for documentation purposes. (`#138 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/138>`__)


v0.0.71 (2024-07-01)
====================

Misc
----

- Move to version 8.1.0 of `dkist-processing-common` which includes an upgrade to airflow 2.9.2. (`#137 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/137>`__)


v0.0.70 (2024-06-25)
====================

Features
--------

- Use ParameterMixin paradigm from `dkist-processing-common` to simplify the definitions of Parameter classes. Specifically, this
  means using the `ParameterWavelengthMixin` and `ParameterArmIdMixin` to provide support for parameters that depend on either wavelength
  or arm ID. This functionality had existed previously, but now it is achieved by using standard tools in `dkist-processing-common`. (`#134 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/134>`__)


Misc
----

- Move to version 8.0.0 of `dkist-processing-common`. This version changes the default behavior of `_find_most_recent_past_value` in
  parameter classes. (`#134 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/134>`__)
- Bump `dkist-processing-pac` to v3.0.2. No effect on `dkist-processing-cryonirsp`. (`#136 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/136>`__)


v0.0.69 (2024-06-12)
====================

Misc
----

- Bump `dkist-fits-specifications` to v4.3.0. This version contains bugfixes for DL-NIRSP, but we want to say current. (`#133 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/133>`__)


v0.0.68 (2024-06-12)
====================

Misc
----

- Update all CRYO-NIRSP dependencies to their latest versions. (`#130 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/130>`__)


v0.0.67 (2024-06-11)
====================

Misc
----

- Refactor production workflows to correct dependency of the `SubmitDatasetMetadata` task. (`#132 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/132>`__)
- Remove trial workflows that don't create science data. (`#132 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/132>`__)


v0.0.66 (2024-06-11)
====================

Misc
----

- Cast linearization threshold values to float 32 if they are found to be float64. (`#122 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/122>`__)
- Add CRYO-NIRSP arm ID to the L1 filename. (`#131 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/131>`__)


v0.0.65 (2024-06-04)
====================

Misc
----

- Bump `dkist-data-simulator` to v5.2.0 and `dkist-inventory` to v1.4.0. These versions add support for DLNIRSP data (but it's nice to be up-to-date). (`#129 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/129>`__)


v0.0.64 (2024-06-03)
====================

Misc
----

- Resolve matplotlib version conflict (`#127 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/127>`__)
- Upgrade the version of dkist-processing-common which brings along various major version upgrades to libraries associated with Pydantic 2. (`#128 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/128>`__)


v0.0.63 (2024-05-20)
====================

Bugfixes
--------

- Polcal fit/modulation matrix quality metrics are now correctly rendered in quality report. (`#125 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/125>`__)
- Correctly render L0 quality metrics (individual frame and dataset average and RMS values for dark, lamp, and solar frames).
  Previously these had been missing from quality reports of polarimetric datasets. (`#125 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/125>`__)


Misc
----

- Remove `CryoStemName.modstate` and `CryonirspTag.modstate`. Both of these already exist in `*-common` and can be used directly from there. (`#125 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/125>`__)
- Update `dkist-processing-common` to v6.2.4. This fixes a bug that could cause the quality report to fail to render if
  the demodulation matrices were fit with the (very old) "use_M12" fit mode. (`#126 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/126>`__)


v0.0.62 (2024-05-16)
====================

Misc
----

- Bumped dkist-fits-specifications to 4.2.0 (`#124 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/124>`__)


v0.0.61 (2024-05-09)
====================

Misc
----

- Bumped common to 6.2.3 (`#123 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/123>`__)


v0.0.60 (2024-05-07)
====================

Features
--------

- Add the ability to create a quality report from a trial workflow. (`#121 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/121>`__)


v0.0.59 (2024-05-06)
====================

Misc
----

- Add ability to handle data with zero modulator states corresponding to intensity mode. (`#118 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/118>`__)


v0.0.58 (2024-05-03)
====================

Bugfixes
--------

- Some Cryo-NIRSP CI movies were far too large (>1GB).
  This fix made the movies smaller by scaling down the size of the movies. (`#119 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/119>`__)


v0.0.57 (2024-05-02)
====================

Misc
----

- Reduce flakyness in bad px correction test by contriving bad px neighborhood to give a known result. (`#116 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/116>`__)
- Rename non-FITS L1 products to better manage namespace. (`#120 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/120>`__)


v0.0.56 (2024-04-26)
====================

Documentation
-------------

- Update online documentation for Cryo-NIRSP bad pixel correction, beam angle calculation, and beam boundary calculation. (`#117 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/117>`__)


v0.0.55 (2024-04-12)
====================

Misc
----

- Populate the value of MANPROCD in the L1 headers with a boolean indicating whether there were manual steps involved in the frames production. (`#115 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/115>`__)


v0.0.54 (2024-04-11)
====================

Misc
----

- Update to use the latest version of dkist-processing-common to take advantage of optimizations in the task auditing feature. (`#114 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/114>`__)


v0.0.53 (2024-04-04)
====================

Features
--------

- The ability to rollback tasks in a workflow for possible retry has been added via dkist-processing-common 6.1.0. (`#112 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/112>`__)


v0.0.52 (2024-04-02)
====================

Misc
----

- Update bad pixel correction method such that if more than a given fraction of the frame is impacted, a faster and more general algorithm is used. This reduces processing time in cases where the data has readout problems or other large scale issues. (`#109 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/109>`__)


v0.0.51 (2024-03-27)
====================

Features
--------

- Wavelength range of CI data is now determined using header keys containing the filter central wavelength and full width half maximum. (`#111 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/111>`__)


v0.0.50 (2024-03-26)
====================

Misc
----

- Update `dkist-processing-common` to v6.0.4 to fix bug affecting NAXISn keys in `FitsAccessBase` subclasses.

v0.0.49 (2024-03-15)
====================

Bugfixes
--------

- Correctly identify *partially* incomplete scan steps. Previously any scan step that had at least a single file was
  considered to exist in its entirety, even if some of its files were missing. (`#108 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/108>`__)


v0.0.48 (2024-03-15)
====================

Bugfixes
--------

- Fixes a bug in `ParseL0CryonirspLinearizedData` which conflated dark frames with the same exposure time but different OD filters. We need to be able to identify dark frame based on their exposure conditions (exposure time, Optical Density Filter) and use the exposure conditions to correlate the sets of dark frames with the frames sets they will be used to correct (lamp gain, solar gain, observe). (`#106 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/106>`__)


v0.0.47 (2024-03-15)
====================

Bugfixes
--------

- Fixed a bug in `LinearityCorrection` that allowed an incomplete ramp to be linearized and passed onto the next processing stage. Incomplete ramps are now skipped and the parsing task will detect any incompleteness in the map and respond appropriately. (`#105 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/105>`__)


v0.0.46 (2024-03-13)
====================

Features
--------

- Normalize Q, U, and V polarimetric beams by their respective Stokes-I prior to beam combination, then multiply the combination
  by the average Stokes-I data. (`#104 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/104>`__)


Bugfixes
--------

- L1 CI Science frames now have array values that are given relative to value at disk center. Previously they had been raw counts per second.
  With this change the L1 CI frames have the same units as the L1 SP frames (i.e., counts/sec relative to disk center). (`#103 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/103>`__)


v0.0.45 (2024-03-06)
====================

Features
--------

- Save spectral corrected solar arrays as an intermediate file for inclusion in trial data products. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/101>`__)


Misc
----

- Add option to `l0_to_l1` local trial workflow to mimic running the `TransferCryoTrialData`. The command line option is `-X` and an optional argument can point
  to a specific place (anywhere in the filesystem) to save the trial outputs. If no argument to `-X` is specified then trial data will be saved in a directory called
  "trial_output" under the recipe run directory. (`#102 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/102>`__)


v0.0.44 (2024-03-05)
====================

Misc
----

- Update dkist-processing-common to v6.0.3 (adding the SOLARRAD keyword to L1 headers)


v0.0.43 (2024-03-04)
====================

Misc
----

- Bump common to v6.0.2 (`#100 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/100>`__)


v0.0.42 (2024-02-29)
====================

Bugfixes
--------

- Update dkist-processing-common to v6.0.1 (all movies are now forced to have an even number of pixels in each dimension)


v0.0.41 (2024-02-27)
====================

Misc
----

- Update the versions of the dkist-data-simulator and dkist-inventory packages. (`#99 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/99>`__)


v0.0.40 (2024-02-26)
====================

Misc
----

- Update dkist-fist-specifications to 4.1.1 (allow DEAXES = 0)


v0.0.39 (2024-02-23)
====================

Features
--------

- Added time-based computation of flux-scaled, fringe-removed, lamp gain to correct for spectral lines leaking into the average solar gain images. This problem will be resolved by the installation of a new optical filter. (`#98 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/98>`__)


v0.0.38 (2024-02-22)
====================

Bugfixes
--------

- Fixed bugs in `SPGeometricCalibration` task to use basic-corrected or gain-corrected arrays where needed. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/97>`__)
- Fixed errors in `CorrectionsMixin` that caused problems in rotation, shift and spectral curvature computations. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/97>`__)


v0.0.37 (2024-02-21)
====================

Bugfixes
--------

- Added ObsIpStartTimeBud to ramp parser to support parameter access outside of parse tasks (`#95 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/95>`__)
- Fix local workflow code to use the correct polyfit coefficients for local data processing. (`#96 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/96>`__)


v0.0.36 (2024-02-20)
====================

Features
--------

- Browse movies for polarimetric data now only show Stokes-I (with a label indicating this). (`#92 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/92>`__)


v0.0.35 (2024-02-16)
====================

Misc
----

- Transform the `cryonirsp_linearization_polyfit_coeffs_ci` and `cryonirsp_linearization_polyfit_coeffs_sp` parameters storage from being a file to json. (`#94 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/94>`__)


v0.0.34 (2024-02-15)
====================

Misc
----

- Bump common to 6.0.0 (total removal of `FitsData` mixin). (`#93 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/93>`__)


v0.0.33 (2024-02-14)
====================

Features
--------

- SP movie frames now show the 2D spectra for each L1 frame instead of stacked slit positions integrated over a wavelength range.
  This means that each spatial step now gets its own movie frame. It is expected that this is a temporary change. (`#91 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/91>`__)


Bugfixes
--------

- Movies now have the same aspect ratio as the L1 output frames. (`#91 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/91>`__)


Misc
----

- Update local trial workflow scripts to improve functionality. (`#90 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/90>`__)
- Replace overly chatty APM spans in MakeMovieFrames task with `logger` statements. These spans recorded map scan and step numbers, which
  are both unbounded. (`#91 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/91>`__)


v0.0.32 (2024-02-08)
====================

Bugfixes
--------

- Improved accuracy of beam identification algorithm in `BeamBoundariesCalibration` by using a different algorithm to align the images. This also results in less data being discarded. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Improved accuracy of beam angle and offset calcuations in `SPGeometricCalibration` by using a different algorithm to align the images. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Update algorithm used to compute translations between two arrays (which is used for alignment in both translation and rotation). The new method is based on T. Schad's gradient approach. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Fixed missing flip on spectral axis in linearized_frame mixin. (`#89 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/89>`__)


Misc
----

- Created the `ShiftMeasurementsMixin` class to share shift measurement calculation methods with both the `BeamBoundariesCalibration` and `SPGeometricCalibration` classes. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Renamed 3 `geo_strip` parameters in the `CryonirspParameters` class, as they are now used on both spectral and spatial axes. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Added the `AxisParams` dataclass to the `ShiftMeasurementsMixin` class to support axis information required when computing shifts along an axis. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)
- Added the `BeamBoundaries` dataclass to the `BeamBoundariesCalibrationBase` class to support aggregation of beam boundary information into a single data structure. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/86>`__)


v0.0.31 (2024-02-06)
====================

Bugfixes
--------

- Flipping value of CDELT1 to account for the dispersion axis flip. (`#80 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/80>`__)
- Flipping dispersion axis in the final reduced data. (`#80 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/80>`__)


v0.0.30 (2024-02-02)
====================

Features
--------

- Enable intensity mode observations to be calibrated with polarized calibration data. (`#83 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/83>`__)


v0.0.29 (2024-02-01)
====================

Misc
----

- Add tasks to trial workflows enabling ASDF, dataset inventory, and movie generation. (`#88 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/88>`__)


v0.0.28 (2024-01-31)
====================

Misc
----

- Bump versions of `dkist-fits-specifications`, `dkist-data-simulator`, and `dkist-header-validator` for fits spec version 4.1.0 (`#85 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/85>`__)


v0.0.27 (2024-01-29)
====================

Features
--------

- Modify parsing to correctly detect the use of dual nested internal scanning loops, with the outer loop step size set to zero to emulate a DSP map scan. (`#79 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/79>`__)


Bugfixes
--------

- Fixed errors in the ordering of the Helioprojective Latitude and Longitude axes in the L1 headers. (`#71 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/71>`__)


v0.0.26 (2024-01-25)
====================

Misc
----

- Update version of dkist-processing-common to 5.1.0 which includes common tasks for cataloging in trial workflows. (`#87 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/87>`__)


v0.0.25 (2024-01-12)
====================

Bugfixes
--------

- Compute polarimetric noise and sensitivity values and add to L1 headers (POL_NOIS, and POL_SENS, respectively). These
  keywords are now required by the fits-spec. (`#84 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/84>`__)


Misc
----

- Update `dkist-fits-specifications` and associated (validator, simulator) to use new conditional requiredness framework. (`#84 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/84>`__)


v0.0.24 (2024-01-03)
====================

Misc
----

- Bump version of `dkist-processing-pac` to v3.0.1. No change to pipeline behavior at all. (`#82 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/82>`__)


v0.0.23 (2023-12-20)
====================

Misc
----

- Adding manual processing worker capabilities via dkist-processing-common update. (`#81 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/81>`__)


v0.0.22 (2023-12-01)
====================

Misc
----

- Use `TaskName`, task-tags, and Task-parsing flowers from `dkist-processing-common`. These had all been defined in `dkist-processing-cryonirsp`, but
  were recetly moved up to `*-common`. (`#78 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/78>`__)


v0.0.21 (2023-11-24)
====================

Misc
----

- Updates to core and common to patch security vulnerabilities and deprecations. (`#77 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/77>`__)


v0.0.20 (2023-11-22)
====================

Misc
----

- Update the FITS header specification to remove some CRYO-NIRSP specific keywords from the L1 headers. (`#76 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/76>`__)


v0.0.19 (2023-11-15)
====================

Features
--------

- Define a public API for tasks such that they can be imported directly from dkist-processing-cryonirsp.tasks (`#75 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/75>`__)


v0.0.18 (2023-11-08)
====================

Bugfixes
--------

- Removes cross-talk correction from SP science task. (`#72 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/72>`__)
- Turn on bad-pixel correction of science observe frames for science team evaluation. (`#73 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/73>`__)
- Fix computation of characteristic spectrum by removing incorrect median normalization. (`#74 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/74>`__)


v0.0.17 (2023-11-06)
====================

Features
--------

- Implement relative photometric calibration. Linearized ramp sets are normalized to counts per second. Attenuation due to Optical Density filters is compensated. Solar gain image is no longer normalized to mean of 1. Observe images are now in units of flux relative to solar center. (`#70 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/70>`__)


v0.0.16 (2023-11-02)
====================

Features
--------

- Add check to ensure calibration frames with exposure times correlated with observe frames exist and fail fast if they do not. (`#51 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/51>`__)


v0.0.15 (2023-10-17)
====================

Bugfixes
--------

- Fixed bug in SP solar gain task where lamp gain was being applied to the average solar image,
  causing the spectral transmission profile to be removed from the resulting solar gain image.
  The lamp gain is no longer applied. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/67>`__)


Misc
----

- Complete refactorization of the SP solar gain task. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/67>`__)


v0.0.14 (2023-10-17)
====================

Features
--------

- Modifies the linearity correction to divide the process into smaller chunks using less memory. No longer requires that entire ramp set be stored in memory at once. (`#65 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/65>`__)


v0.0.13 (2023-10-11)
====================

Misc
----

- Use latest version of dkist-processing-common (4.1.4) which adapts to the new metadata-store-api. (`#68 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/68>`__)


v0.0.12 (2023-10-06)
====================

Misc
----

- Identify ramps with only one frame as invalid and do not linearize them. (`#62 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/62>`__)


v0.0.11 (2023-10-05)
====================

Features
--------

- Removes casts and flips used when loading parameter files. The files are now changed to be in the format we want. (`#68 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/68>`__)


v0.0.10 (2023-09-29)
====================

Misc
----

- Remove and edit selected APM spans to reduce load on aggregating span data. (`#64 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/64>`__)


v0.0.9 (2023-09-29)
===================

Features
--------

- Removes all references to the FitsDataMixin and its methods, which are deprecated. Uses the new self.read() and self.write() methods with encoder and decoder support. (`#63 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/63>`__)


Misc
----

- Update pillow to address security vulnerability. (`#66 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/66>`__)


v0.0.8 (2023-09-21)
===================

Misc
----

- Update dkist-fits-specifications to conform to Revision I of SPEC-0122.


v0.0.7 (2023-09-11)
===================

Bugfixes
--------

- Fixes error in intermediate file mixin log statement. (`#57 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/57>`__)


Misc
----

- Refactor to reduce complexity and hidden mixin->mixin dependency. (`#55 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/55>`__)


v0.0.6 (2023-09-08)
===================

Misc
----

- Use the latest version of dkist-processing-common (4.1.2) to allow the Linearity Correction task to be run on a higher memory worker. (`#60 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/60>`__)


v0.0.5 (2023-09-06)
===================

Misc
----

- Refactor linearity correction to improve memory usage. (`#59 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/59>`__)


v0.0.4 (2023-09-06)
===================

Misc
----

- Update to version 4.1.1 of dkist-processing-common which primarily adds logging and scratch file name uniqueness. (`#58 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/58>`__)


v0.0.3 (2023-08-31)
===================

Misc
----

- Remove parallel computations from the linearity correction task. (`#56 <https://bitbucket.org/dkistdc/dkist-processing-cryonirsp/pull-requests/56>`__)


v0.0.2 (2023-08-25)
===================

Misc
----

- Change workflow names in documentation builds.


v0.0.1 (2023-08-25)
===================

Misc
----

- Initial release of pipeline for science review
