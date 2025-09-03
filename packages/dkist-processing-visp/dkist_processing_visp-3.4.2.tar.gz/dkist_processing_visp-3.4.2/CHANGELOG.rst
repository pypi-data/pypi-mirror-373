v3.4.2 (2025-09-02)
===================

Bugfixes
--------

- Update CADENCE-related and XPOSURE headers to take the instrument mode into account. (`#237 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/237>`__)


Misc
----

- Update `dkist-processing-common` to allow instrument level changes to cadence-related keywords when writing L1 data. (`#237 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/237>`__)
- Update `dkist-processing-math` to remove a deprecated package dependency. (`#237 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/237>`__)
- Update pre-commit hook versions and replace python-reorder-imports with isort. (`#238 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/238>`__)


v3.4.1 (2025-08-12)
===================

Bugfixes
--------

- Fix a bug in which a recent change to the time parsers in dkist-processing-common did not fully propagate
  to the development tools in the local_trial_helpers.py file. (`#233 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/233>`__)


Misc
----

- Update some pre-commit hook versions. (`#232 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/232>`__)
- Update verion of `dkist-processing-common` to v11.2.1 to fix bug that caused Wavecal quality metrics to not be rendered in Quality Reports.
  Also bump `dkist-quality` to v2.0.0 for the same reason. This doesn't affect ViSP, for now, but it will soon. (`#236 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/236>`__)


v3.4.0 (2025-07-18)
===================

Bugfixes
--------

- Update `dkist-processing-common` to include the results of wavelength calibration when determining spectral lines in the data. (`#231 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/231>`__)


v3.3.1 (2025-07-15)
===================

Misc
----

- Replace `FakeGQLClient` with the `fake_gql_client` fixture imported from the `mock_metadata_store` module
  in `dkist-processing-common`.  Because the fixture is imported into `conftest.py`, individual imports are not needed. (`#227 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/227>`__)


v3.3.0 (2025-07-10)
===================

Bugfixes
--------

- Update the VISP workflows such that the `SubmitDatasetMetadata` task is now dependent on the `AssembleVispMovie` task. This ensures that the metadata is submitted only after the movie has been assembled and that it is counted in downstream checks. (`#230 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/230>`__)


Misc
----

- Update dkist-processing-common to handle non-finite values in quality wavecal metrics. (`#230 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/230>`__)


v3.2.9 (2025-07-08)
===================

Misc
----

- Update dkist-inventory to 1.9.0 in order to stay current with production generation of inventory and metadata.asdf files in trial workflows. (`#229 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/229>`__)


v3.2.8 (2025-07-02)
===================

Misc
----

- Bump `dkist-quality`. This update contains machinery for plotting wavelength calibration results, which ViSP doesn't use.... yet. (`#226 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/226>`__)
- Update `dkist-processing-common` to v11.0.0 and update affected `Stem`'s for the new API. (`#226 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/226>`__)


v3.2.7 (2025-06-25)
===================

Misc
----

- Update dkist-inventory to 1.8.4 in order to avoid a bug in the generation of inventory and metadata.asdf files in trial workflows. (`#225 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/225>`__)


v3.2.6 (2025-06-02)
===================

Misc
----

- Remove use of input dataset mixin imported from dkist-processing-common. (`#212 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/212>`__)


v3.2.5 (2025-05-30)
===================

Misc
----

- Update `dkist-fits-specifications` to v4.17.0 (`#224 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/224>`__)


v3.2.4 (2025-05-28)
===================

Misc
----

- Update `dkist-processing-common` to v10.8.3 (`#223 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/223>`__)


v3.2.3 (2025-05-27)
===================

Misc
----

- Update `dkist-processing-common` to v10.8.2 (`#222 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/222>`__)


v3.2.2 (2025-05-23)
===================

Misc
----

- Update dkist-processing-common dependency to v10.8.1 (`#221 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/221>`__)


v3.2.1 (2025-05-21)
===================

Misc
----

- Update dkist-fits-specifications dependency to v4.16.0. (`#220 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/220>`__)


v3.2.0 (2025-05-15)
===================

Misc
----

- Updating dependencies to cross astropy 7.0.0 and numpy 2.0.0. (`#219 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/219>`__)


v3.1.5 (2025-05-06)
===================

Misc
----

- Update dkist-fits-specifications to add the `THEAP` keyword. (`#218 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/218>`__)


v3.1.4 (2025-05-01)
===================

Misc
----

- Use the latest version of dkist-inventory for trial workflow inventory and metadata ASDF generation. (`#217 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/217>`__)


v3.1.3 (2025-04-24)
===================

Misc
----

- Use the latest version of dkist-inventory for trial workflow inventory and metadata ASDF generation. (`#216 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/216>`__)


v3.1.2 (2025-04-21)
===================

Misc
----

- Bump dkist-processing-common to v10.7.2, which fixes a bug that required the AO_LOCK keyword to be present in the headers. (`#215 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/215>`__)


v3.1.1 (2025-04-21)
===================

Bugfixes
--------

- Update the value of "BUNIT" key in L1 headers.
  L1 pixels do not have units because their values are relative to disk center at the time of solar gain observation. (`#209 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/209>`__)


Documentation
-------------

- Update online `L1 Science Calibration docs <https://docs.dkist.nso.edu/projects/visp/en/stable/science_calibration.html>`_
  to include information about the units of L1 science frames. (`#209 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/209>`__)


v3.1.0 (2025-04-17)
===================

Misc
----

- Update dkist-processing-common to only remove level 0 header keys from the level 1 files. (`#212 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/212>`__)
- Add missing build dependency specifications. (`#214 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/214>`__)


v3.0.2 (2025-04-03)
===================

Bugfixes
--------

- Change instrument polarization task to use the readout exposure time of observations. (`#211 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/211>`__)


v3.0.1 (2025-04-02)
===================

Bugfixes
--------

- Fix a bug in instrument polarization calibration by using the correct FITS access object type. (`#210 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/210>`__)


v3.0.0 (2025-04-01)
===================

Features
--------

- Update polarization calibration to use the darks and gains taken as part of the instrument polarization sequence. (`#202 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/202>`__)


v2.21.5 (2025-03-31)
====================

Bugfixes
--------

- Update dkist-processing-common to v10.6.4 to fix a bug in writing L1 frames when input dataset parts are missing. (`#208 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/208>`__)


v2.21.3 (2025-03-21)
====================

Misc
----

- Add code coverage badge to README.rst. (`#203 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/203>`__)
- Fix bug that caused some tests to incorrectly fail depending on how they were assigned to xdist workers. (`#204 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/204>`__)
- Bump `dkist-inventory` to v1.7.0. No affect for ViSP, but nice to stay up to date. (`#205 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/205>`__)


v2.21.2 (2025-03-19)
====================

Misc
----

- Bump dkist-processing-common to v10.6.2, which fixes a bug in manual processing. (`#201 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/201>`__)


v2.21.1 (2025-03-14)
====================

Misc
----

- Bump dkist-processing-common to v10.6.1 (`#200 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/200>`__)


v2.21.0 (2025-03-03)
====================

Features
--------

- Information about the initial set of values (e.g., the name of the GOS retarder) to use when fitting demodulation
  matrices now comes directly from the headers of the POLCAL task data instead of being a pipeline parameter.
  This allows different proposals to use different GOS optics without the need for parameter changes. (`#199 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/199>`__)


v2.20.20 (2025-02-26)
=====================

Misc
----

- Update `dkist-processing-common` to use version 2.10.5 of `apache-airflow. (`#198 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/198>`__)


v2.20.19 (2025-02-24)
=====================

Misc
----

- Bump `dkist-processing-math` to v2.2.0 (`#197 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/197>`__)


v2.20.18 (2025-02-19)
=====================

Misc
----

- Bump `dkist-processing-common` to 10.5.14, which computes PRODUCT when creating L1 FITS headers. (`#196 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/196>`__)


v2.20.17 (2025-02-14)
=====================

Misc
----

- Bump version of `dkist-processing-common` to bring along new version of `dkist-processing-core` that uses frozen dependencies for pipeline install. (`#194 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/194>`__)
- Add Bitbucket pipeline steps to check that full dependencies were correctly frozen. (`#194 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/194>`__)


v2.20.16 (2025-02-12)
=====================

Misc
----

- Bump `dkist-inventory` to 1.6.1. (`#115 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/115>`__)
- Bump `dkist-processing-common` to 10.5.12, which increases the DSETID to 6 characters. (`#115 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/115>`__)


v2.20.15 (2025-02-10)
=====================

Features
--------

- Bump `dkist-fits-specifications` to 4.11.0, which adds the L1 PRODUCT keyword. (`#193 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/193>`__)


v2.20.14 (2025-02-06)
=====================

Misc
----

- Bump `dkist-inventory` and `dkist-processing-common` for non-ViSP related updates.
  Also bump a few minimum versions required by this update. (`#192 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/192>`__)


v2.20.13 (2025-02-04)
=====================

Features
--------

- Remove intermediate frame read/write mixin for tasks and use standard read/write
  methods from `dkist-processing-common` instead.  To facilitate intermediate file read/write,
  add new composite tag methods that return lists of tags. (`#190 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/190>`__)


Misc
----

- Update Bitbucket pipelines to use execute script for standard steps. (`#191 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/191>`__)


v2.20.12 (2025-01-29)
=====================

Misc
----

- Update dkist-processing-common and dkist-quality to manage a bug present in dacite 1.9.0.


v2.20.11 (2025-01-27)
=====================

Misc
----

- Update bitbucket pipelines to use common scripts for checking for changelog snippets and verifying doc builds. (`#189 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/189>`__)
- Update dkist-processing-common to remove some deprecated packages.


v2.20.10 (2025-01-09)
=====================

Misc
----

- Update dkist-inventory to change dataset inventory parsing logic in trial workflows.


v2.20.9 (2025-01-09)
====================

Misc
----

- Update dkist-processing-common to pull in the new version of airflow.


v2.20.8 (2024-12-20)
====================

Documentation
-------------

- Change the documentation landing page to focus more on users and less on developers. (`#186 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/186>`__)


v2.20.7 (2024-12-18)
====================

Documentation
-------------

- Update docstrings and comments to indicate that the most likely source of extra hairline signals is dust on the slit
  (as opposed to ghosts or reflections). (`#184 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/184>`__)
- Add online doc page for the `GeometricCalibration` task. (`#185 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/185>`__)


v2.20.6 (2024-12-18)
====================

Features
--------

- Bump common to remove Fried parameter from the L1 headers and the quality metrics where the AO system is unlocked. (`#188 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/188>`__)


Misc
----

- Update Bitbucket pipelines to use standardized lint and scan steps. (`#187 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/187>`__)


v2.20.5 (2024-12-05)
====================

Misc
----

- Pin `sphinx-autoapi` to v3.3.3 to avoid `this issue <https://github.com/readthedocs/sphinx-autoapi/issues/505>`_ until it is fixed. (`#183 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/183>`__)


v2.20.4 (2024-11-26)
====================

Misc
----

- Write the CNAMEn keywords to the instrument headers. (`#182 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/182>`__)
- Bumping dkist-fits-specification to v4.10.0 and dkist-processing-common to v10.5.3. (`#182 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/182>`__)


v2.20.3 (2024-11-21)
====================

Bugfixes
--------

- Update dkist-inventory and dkist-processing-common to fix a bug in producing dataset inventory from the SPECLN* keys


v2.20.2 (2024-11-20)
====================

Bugfixes
--------

- Update dkist-processing-common to constrain asdf < 4.0.0


v2.20.1 (2024-11-20)
====================

Misc
----

- Update dkist-processing-common to manage breaking API changes in asdf and moviepy.


v2.20.0 (2024-11-14)
====================

Misc
----

- Replace `TransferVispTrialData` with `TransferTrialData` from dkist-processing-common. (`#181 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/181>`__)


v2.19.5 (2024-10-29)
====================

Documentation
-------------

- Change ViSP task methods from private to public so they appear in the documentation (`#180 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/180>`__)


v2.19.4 (2024-10-15)
====================

Misc
----

- Bump `dkist-processing-common` to v10.3.0 and `dkist-processing-pac` to v3.1.0, both of which harden polcal fitting against bad input data. (`#179 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/179>`__)


v2.19.3 (2024-10-14)
====================

Misc
----

- Make and publish wheels at code push in build pipeline (`#178 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/178>`__)
- Switch from setup.cfg to pyproject.toml for build configuration (`#178 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/178>`__)


v2.19.2 (2024-10-07)
====================

Misc
----

- Bump dkist-fits-specifications to v4.7.0. This adjusted the TTBLTRCK allowed values, adjusted CRSP_051 and CRSP_052 to accommodate blocking filters,adjusted CRSP_073 to include a new grating, and added a new allowed value to CAM__044. (`#177 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/177>`__)


v2.19.1 (2024-09-27)
====================

Misc
----

- Bump `dkist-processing-common` to v10.2.1. This fixes a documentation build bug in Airflow.


v2.19.0 (2024-09-27)
====================

Misc
----

- Bump `dkist-processing-common` to v10.2.0. This includes upgrading to the latest version of Airflow (2.10.2).


v2.18.2 (2024-09-26)
====================

Misc
----

- Bump `dkist-processing-common` to v10.1.0. This enables the usage of the `NearFloatBud` and `TaskNearFloatBud` in parsing.


v2.18.1 (2024-09-24)
====================

Misc
----

- Bump `dkist-processing-common` to v10.0.1. This fixes a bug in the reported FRAMEVOL key in L1 headers. (`#176 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/176>`__)


v2.18.0 (2024-09-23)
====================

Features
--------

- Reorder task dependencies in workflows. Movie and L1 quality tasks are no longer dependent on the presence of OUTPUT
  frames and thus can be run in parallel with the `WriteL1` task. (`#174 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/174>`__)


Misc
----

- Remove `AssembleVispMovie` as workflow dependency on `SubmitDatasetMetadata`. This dependency has been unnecessary
  since the introduction of `SubmitDatasetMetadata` in v2.11.0. (`#174 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/174>`__)
- Use CALIBRATED instead of OUTPUT frames in post-science movie and quality tasks. This doesn't change their output at all (the arrays are the same), but
  it's necessary for `dkist-processing-common >= 10.0.0` that will break using OUTPUT frames. (`#174 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/174>`__)


v2.17.1 (2024-09-19)
====================

Misc
----

- Bump `dkist-quality` to v1.1.1. This fixes raincloud plot rendering in trial workflows. (`#175 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/175>`__)


v2.17.0 (2024-09-10)
====================

Misc
----

- Accommodate changes to the GraphQL API associated with refactoring the quality database (`#173 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/173>`__)


v2.16.7 (2024-08-21)
====================

Misc
----

- Update some Quality related tasks and methods for the new API in `dkist-processing-common` v9.0.0. No change to any outputs. (`#172 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/172>`__)


v2.16.6 (2024-08-15)
====================

Misc
----

- Remove log statement when writing L1 spectrographic files. (`#171 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/171>`__)


v2.16.5 (2024-08-15)
====================

Misc
----

- Move to version 4.6.0 of `dkist-fits-specifications` to correct allowed values of the TTBLTRCK header keyword.


v2.16.4 (2024-08-12)
====================

Misc
----

- Move to version 4.5.0 of `dkist-fits-specifications` which includes `PV1_nA` keys for non linear dispersion.


v2.16.3 (2024-08-05)
====================

Documentation
-------------

- Add pre-commit hook for documentation, add missing workflow documentation and update README.rst. (`#169 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/169>`__)


v2.16.2 (2024-07-25)
====================

Misc
----

- Rewrite to eliminate warnings in unit tests. (`#168 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/168>`__)


v2.16.1 (2024-07-19)
====================

Misc
----

- Move to version 4.2.2 of `dkist-fits-specifications` which includes `PV1_n` keys for non linear dispersion.



v2.16.0 (2024-07-12)
====================

Misc
----

- Move to version 8.2.1 of `dkist-processing-common` which includes the publication of select private methods for documentation purposes. (`#167 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/167>`__)


v2.15.0 (2024-07-01)
====================

Misc
----

- Move to version 8.1.0 of `dkist-processing-common` which includes an upgrade to airflow 2.9.2. (`#166 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/166>`__)


v2.14.0 (2024-06-25)
====================

Misc
----

- Move to version 8.0.0 of `dkist-processing-common`. This version changes the default behavior of `_find_most_recent_past_value` in
  parameter classes. (`#164 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/164>`__)
- Update `dkist-processing-pac` to v3.0.2. No effect on `dkist-processing-visp`. (`#165 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/165>`__)


v2.13.4 (2024-06-12)
====================

Misc
----

- Bump `dkist-fits-specifications` to v4.3.0. This version contains bugfixes for DL-NIRSP, but we want to say current. (`#163 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/163>`__)


v2.13.3 (2024-06-12)
====================

Misc
----

- Update all VISP dependencies to their latest versions. (`#161 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/161>`__)


v2.13.2 (2024-06-11)
====================

Misc
----

- Remove non-science trial pipelines. (`#162 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/162>`__)
- Refactor the dependencies in the production workflows to no longer have TransferL1Data be dependent on SubmitDatasetMetadata. (`#162 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/162>`__)


v2.13.1 (2024-06-04)
====================

Misc
----

- Bump `dkist-data-simulator` to v5.2.0 and `dkist-inventory` to v1.4.0. These versions add support for DLNIRSP data (but it's nice to be up-to-date). (`#160 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/160>`__)


v2.13.0 (2024-06-03)
====================

Misc
----

- Resolve matplotlib version conflict (`#158 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/158>`__)
- Upgrade the version of dkist-processing-common which brings along various major version upgrades to libraries associated with Pydantic 2. (`#159 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/159>`__)


v2.12.1 (2024-05-20)
====================

Misc
----

- Update `dkist-processing-common` to v6.2.4. This fixes a bug that could cause the quality report to fail to render if
  the demodulation matrices were fit with the (very old) "use_M12" fit mode. (`#157 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/157>`__)


v2.12.0 (2024-05-16)
====================

Misc
----

- Bumped dkist-fits-specifications to 4.2.0 (`#156 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/156>`__)


v2.11.1 (2024-05-09)
====================

Misc
----

- Bumped common to 6.2.3 (`#155 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/155>`__)


v2.11.0 (2024-05-08)
====================

Features
--------

- Add the ability to create a quality report from a trial workflow. (`#153 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/153>`__)


v2.10.16 (2024-05-02)
=====================

Misc
----

- Rename non-FITS L1 products to better manage namespace. (`#154 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/154>`__)


v2.10.15 (2024-04-12)
=====================

Misc
----

- Populate the value of MANPROCD in the L1 headers with a boolean indicating whether there were manual steps involved in the frames production. (`#152 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/152>`__)


v2.10.14 (2024-04-11)
=====================

Misc
----

- Update to use the latest version of dkist-processing-common to take advantage of optimizations in the task auditing feature. (`#151 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/151>`__)


v2.10.13 (2024-04-04)
=====================

Features
--------

- The ability to rollback tasks in a workflow for possible retry has been added via dkist-processing-common 6.1.0. (`#149 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/149>`__)


v2.10.12 (2024-03-26)
=====================

Misc
----

- Update `dkist-processing-common` to v6.0.4 (fix bug affecting NAXISn keys in `FitsAccessBase` subclasses).


v2.10.11 (2024-03-05)
=====================

Misc
----

- Update dkist-processing-common to v6.0.3 (adding the SOLARRAD keyword to L1 headers)


v2.10.10 (2024-03-04)
=====================

Misc
----

- Bump common to v6.0.2 (`#148 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/148>`__)


v2.10.9 (2024-02-29)
====================

Bugfixes
--------

- Update dkist-processing-common to v6.0.1 (all movies are now forced to have an even number of pixels in each dimension)


v2.10.8 (2024-02-27)
====================

Misc
----

- Update the versions of the dkist-data-simulator and dkist-inventory packages. (`#147 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/147>`__)


v2.10.7 (2024-02-26)
====================

Misc
----

- Update dkist-fist-specifications to 4.1.1 (allow DEAXES = 0)


v2.10.6 (2024-02-15)
====================

Misc
----

- Add `test` pip extra as requirement for `grogu` test extra. Grogu scripts use "conftest.py", which imports `pytest`. (`#145 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/145>`__)
- Bump common to 6.0.0 (total removal of `FitsData` mixin). (`#146 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/146>`__)


v2.10.5 (2024-02-01)
====================

Misc
----

- Add tasks to trial workflows enabling ASDF, dataset inventory, and movie generation. (`#144 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/144>`__)


v2.10.4 (2024-01-31)
====================

Misc
----

- Bump versions of `dkist-fits-specifications`, `dkist-data-simulator`, and `dkist-header-validator` for fits spec version 4.1.0 (`#142 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/142>`__)


v2.10.3 (2024-01-25)
====================

Misc
----

- Update version of dkist-processing-common to 5.1.0 which includes common tasks for cataloging in trial workflows. (`#143 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/143>`__)


v2.10.2 (2024-01-12)
====================

Bugfixes
--------

- Compute polarimetric noise and sensitivity values and add to L1 headers (POL_NOIS, and POL_SENS, respectively). These
  keywords are now required by the fits-spec. (`#141 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/141>`__)


Misc
----

- Update `dkist-fits-specifications` and associated (validator, simulator) to use new conditional requiredness framework. (`#141 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/141>`__)


v2.10.1 (2024-01-03)
====================

Misc
----

- Bump version of `dkist-processing-pac` to v3.0.1. No change to pipeline behavior at all. (`#140 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/140>`__)


v2.10.0 (2023-12-20)
====================

Misc
----

- Adding manual processing worker capabilities via dkist-processing-common update. (`#139 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/139>`__)


v2.9.0 (2023-11-29)
===================

Features
--------

- Use `DarkReadoutExpTimePickyBud` to fail fast (during `Parse`)if the required set of dark frames are not present in the input data. (`#133 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/133>`__)


Misc
----

- Create new `VispParsingParameters` class that contains only those parameters that are needed for parsing. (`#127 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/127>`__)
- Simplify `VispParameter` class by using new defaults and mixins from `dkist-processing-common`. (`#127 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/127>`__)
- Use new `TaskName` paradigm from `dkist-processing-common` to minimize replication of constant strings corresponding to IP task types. (`#128 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/128>`__)
- Use new `TaskUniqueBud` to simplify and normalize parsing Buds with the framework in `dkist-processing-common`. (`#128 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/128>`__)
- Refactor `IntermediateFrameHelpersMixin` to have clearer arguments and method flow. `intermediate_frame_helpers_load_intermediate_arrays` now just takes in raw tags. (`#130 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/130>`__)
- Remove all usage of `FitsDataMixin`. The codec aware `write` and `read` are how we do this now. (`#131 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/131>`__)
- Refactor stale and mostly-unused `InputFrameLoadersMixin` to `BeamAccessMixin` that contains method for extracting a single beam from raw input data. (`#132 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/132>`__)
- Big refactor of unit tests for improved maintainability. (`#135 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/135>`__)
- Remove `nd_left_matrix_multiply` and instead import it from updated `dkist-processing-math`. It's the same function, just in a more obvious place. (`#136 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/136>`__)


Documentation
-------------

- Update online doc for background light algorithm to indicate that it isn't applied since a hardware fix in Nov 2022. (`#138 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/138>`__)


v2.8.2 (2023-11-24)
===================

Misc
----

- Updates to core and common to patch security vulnerabilities and deprecations. (`#135 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/135>`__)


v2.8.1 (2023-11-22)
===================

Misc
----

- Update the FITS header specification to remove some CRYO-NIRSP specific keywords. (`#134 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/134>`__)


v2.8.0 (2023-11-15)
===================

Features
--------

- Define a public API for tasks such that they can be imported directly from dkist-processing-visp.tasks (`#129 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/129>`__)


v2.7.5 (2023-10-11)
===================

Misc
----

- Use latest version of dkist-processing-common (4.1.4) which adapts to the new metadata-store-api. (`#126 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/126>`__)


v2.7.4 (2023-09-29)
====================

Misc
----

- Update dkist-processing-common to elimate APM steps in writing L1 data.


v2.7.3 (2023-09-21)
===================

Misc
----

- Update dkist-fits-specifications to conform to Revision I of SPEC-0122.



v2.7.2 (2023-09-08)
===================

Misc
----

- Use latest version of dkist-processing-common (4.1.2) which adds support for high memory tasks. (`#125 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/125>`__)


v2.7.1 (2023-09-06)
===================

Misc
----

- Update to version 4.1.1 of dkist-processing-common which primarily adds logging and scratch file name uniqueness. (`#124 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/124>`__)


v2.7.0 (2023-07-28)
===================

Bugfixes
--------

- Use the exposure time *per readout* to compute and correct for dark signal. A single FPA (i.e., frame) can be
  made up of multiple on-camera readouts and it is the exposure time of a single readout that is important for correcting
  the dark current. (`#123 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/123>`__)


v2.6.3 (2023-07-26)
===================

Misc
----

- Update dkist-fits-specifications to include ZBLANK.


v2.6.2 (2023-07-26)
===================

Misc
----

- Update dkist-processing-common to upgrade dkist-header-validator to 4.1.0.


v2.6.1 (2023-07-17)
===================

Misc
----

- Update dkist-processing-common and the dkist-header-validator to propagate dependency breakages in PyYAML < 6.0. (`#122 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/122>`__)


v2.6.0 (2023-07-14)
===================

Features
--------

- Enable intensity mode observations to be calibrated with polarized calibration data. (`#121 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/121>`__)


Bugfixes
--------

- Include Lamp Gain intermediate files in default trial output. (`#120 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/120>`__)


v2.5.1 (2023-07-11)
===================

Misc
----

- Update dkist-processing-common to upgrade Airflow to 2.6.3.


v2.5.0 (2023-06-29)
===================

Misc
----

- Update to python 3.11 and update library package versions. (`#119 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/119>`__)


v2.4.0 (2023-06-27)
===================

Features
--------

- Wield `*-common`'s development framework to tag DEBUG frames and create new trial workflows for local and PROD-level testing. (`#116 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/116>`__)


Misc
----

- Update to support `dkist-processing-common` 3.0.0. Specifically the new signature of some of the `FitsDataMixin` methods. (`#117 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/117>`__)


v2.3.1 (2023-06-15)
===================

Bugfixes
--------

- Fix failure in Geometric task that happened when some modstates had a a different number of identified hairline regions than others. (`#118 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/118>`__)


v2.3.0 (2023-05-17)
===================

Misc
----

- Bumping common to 2.7.0: ParseL0InputData --> ParseL0InputDataBase, constant_flowers --> constant_buds (`#115 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/115>`__)


v2.2.0 (2023-05-16)
===================

Bugfixes
--------

- Lots of small updates to harden the beam angle calculation against pathological data. We are now resistant to lamp data with large gradients and/or data with a high density of bad pixels. (`#114 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/114>`__)


v2.1.1 (2023-05-05)
===================

Misc
----

- Update dkist-processing-common to 2.6.0 which includes an upgrade to airflow 2.6.0


v2.1.0 (2023-05-02)
===================

Features
--------

- Support for a parameter that sets the number of spatial bins used when computing demodulation matrices. This is mostly to speed up testing and deployment; real science data will probably not be binned at all. (`#112 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/112>`__)


Misc
----

- Offload calculation of "WAVEMIN/MAX" in L1 headers to new functionality in `*-common` that uses the already-defined `get_wavelength_range`. The result is that this logic now only lives in one place. (`#113 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/113>`__)


v2.0.2 (2023-04-24)
===================

Misc
----

- Update `dkist-fits-specifications` to include new header keys.


v2.0.1 (2023-04-17)
===================

Bugfixes
--------

- Correct the determination of which spectral lines should be present in L1 frames. (`#111 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/111>`__)


v2.0.0 (2023-04-13)
===================

Features
--------

- Large improvements to gain algorithm. Primary improvement is usage of lamp gain images to help separate optical/spectral signals
  and improve solar characteristic spectra removal from solar gain images. (`#105 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/105>`__)
- Improve spatial residuals in polarimetric data by computing a demodulation matrix for every spatial pixel and then
  smoothing the resulting demodulation matrices in the spatial dimension. (`#106 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/106>`__)
- Normalize Q, U, and V polarimetric beams by their respective Stokes-I prior to beam combination, then multiply the combination
  by the average Stokes-I data. (`#107 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/107>`__)
- Improvement to accuracy of beam angle calculation. The angle is now measured directly from the hairlines instead of using a Hough transform,
  which has less accuracy due to the width of the hairlines. (`#108 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/108>`__)
- Use new and improved PAC fit mode for improved polarimetric accuracy. Also update code to support/interact with
  `dkist-processing-pac` >= 2.0.0. This is mostly renaming kwargs on API calls. Also removed unneeded dummy dimensions
  and renamed a matrix multiple function. (`#109 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/109>`__)


Misc
----

- Replace `logging.[thing]` with `logging42.logger.[thing]` for logging bliss. (`#104 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/104>`__)


Documentation
-------------

- Add machinery for a "Scientific" changelog that tracks only those changes that affect L1 output data. (`#110 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/110>`__)


v1.6.1 (2023-04-10)
===================

Misc
----
- FITS header specification update to add spectral line keys.


v1.6.0 (2023-03-16)
===================

Misc
----
- FITS header specification update to add new keys and change some units.


v1.5.6 (2023-03-01)
===================

Misc
----

- Logging fix in the dkist-header-validator.


v1.5.5 (2023-02-22)
===================

Misc
----

- Move the header specification to revision H of SPEC-0122.


v1.5.4 (2023-02-17)
===================

Misc
----

- Update dkist-processing-common due to an Airflow upgrade.


v1.5.3 (2023-02-06)
===================

Features
--------

- Bump `dkist-processing-common` to allow inclusion of multiple proposal or experiment IDs in headers.


v1.5.2 (2023-02-02)
===================

Misc
----

- Bump FITS specification to revision G.


v1.5.1 (2023-01-31)
===================

Misc
----

- Don't include always-unused polcal dark frames as part of the frame counts quality metric for the Background task. (`#102 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/102>`__)
- Bump `dkist-processing-common`

v1.5.0 (2022-12-15)
===================

Features
--------

- Add parameter to switch on/off the background light correction. This parameter is based of the time *of observation* not the time of pipeline execution. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/101>`__)


Bugfixes
--------

- Remove overriding method to allow `HLSVERS` to be written into the data. (`#100 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/100>`__)


v1.4.2 (2022-12-05)
===================

Bugfix
------

- Update dkist-processing-common to include movie headers in transfers.


v1.4.1 (2022-12-02)
===================

Misc
----

- Update dkist-processing-common to improve handling of Globus issues.


v1.4.0 (2022-11-15)
====================

Misc
----

- Update dkist-processing-common


v1.3.0 (2022-11-14)
===================

Bugfixes
--------

- Fix bug in how final beam overlap is computed. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/97>`__)


Documentation
-------------

- Add changelog to RTD left hand TOC to include rendered changelog in documentation build. (`#99 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/99>`__)


v1.2.4 (2022-11-09)
===================

Misc
----

- Update dkist-processing-common to improve Globus event logging


v1.2.3 (2022-11-08)
===================

Misc
----

- Update dkist-processing-common to handle empty GLobus event lists


v1.2.2 (2022-11-08)
===================

Misc
----

- Update dkist-processing-common to include Globus retries in transfer tasks


v1.2.1 (2022-11-04)
===================

Bugfixes
--------

- Change how intermediate CALIBRATED frames are saved so that the L1 FRAMEVOL header key reports the correct on-disk size of the compressed data. (`#98 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/98>`__)


v1.2.0 (2022-11-02)
===================

Misc
----

- Upgraded dkist-processing-math, dkist-processing-pac, and dkist-processing-common to production versions (`#96 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/96>`__)


v1.1.1 (2022-11-02)
====================

Misc
--------

- Use updated dkist-processing-core version 1.1.2.  Task startup logging enhancements.


v1.1.0 (2022-11-01)
===================

Bugfixes
--------

- Bump `dkist-processing-pac` to 0.9.0 to fix bug in how Telescope Mueller matrices were calculated. (`#95 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/95>`__)


v1.0.0 (2022-10-31)
====================

Misc
----

- Scientific acceptance of the VISP pipeline.



v0.26.1 (2022-10-27)
====================

Features
--------

- All Background Light parameters are now wavelength dependent for finer control. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/92>`__)


Misc
----

- Update dependency versions in "grogu" dev testing install target. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/92>`__)


v0.26.0 (2022-10-26)
====================

Misc
----

- Update versions of dkist-processing-common and dkist-fits-specifications. (`#94 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/94>`__)


v0.25.2 (2022-10-26)
====================

Misc
----

- Update versions of dkist-processing-common and astropy. (`#93 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/93>`__)


v0.25.1 (2022-10-20)
====================

Misc
----

- Require python 3.10+. (`#91 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/91>`__)


v0.25.0 (2022-10-19)
====================

Bugfixes
--------

- Dataset axes in L1 headers now assign dynamically based on L0 CTYPE headers. (`#90 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/90>`__)


v0.24.0 (2022-10-19)
====================

Features
--------

- Trim L1 frames to only include the region where both beams overlap. (`#87 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/87>`__)


v0.23.0 (2022-10-19)
====================

Features
--------

- Expose parameter to switch on/off the fitting and removal of a linear intensity trend across a whole PolCal Calibration Sequence. (`#86 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/86>`__)


v0.22.0 (2022-10-18)
====================

Misc
----

- Only record the constant polcal parameters to the quality report once (i.e., not for both beams; it's the same for both). (`#85 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/85>`__)


v0.21.3 (2022-10-18)
====================

Misc
----

- Even more memory savings in the BackgroundLight algorithm. (`#89 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/89>`__)


v0.21.2 (2022-10-18)
====================

Misc
------

- Changing metrics included in quality reports



v0.21.1 (2022-10-12)
====================

Bugfix
------

- Moving to a new version of dkist-processing-common to fix a Globus bug


v0.21.0 (2022-10-11)
====================

Misc
----

- Upgrading to a new version of Airflow


v0.20.1 (2022-10-06)
====================

Misc
----

- Refactor spatial binning in Background Light algorithm to use less memory. (`#88 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/88>`__)


v0.20.0 (2022-10-05)
====================

Features
--------

- Add functionality to compute and correct for residual background light (`#84 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/84>`__)


Misc
----

- Remove world coordinate system transposition to level set all L1 data. (`#83 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/83>`__)


v0.19.4 (2022-09-16)
====================

Misc
----

- Update tests for new input dataset document format from `*-common >= 0.24.0` (`#82 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/82>`__)


v0.19.3 (2022-09-14)
====================

Misc
----

- FITS spec was using incorrect types for some keys.


v0.19.2 (2022-09-12)
====================

Misc
----

- Updating the underlying FITS specification used.

v0.19.0 (2022-09-08)
====================

Features
--------

- Use bi-quintic interpolation for rotation and offset corrections to minimize residuals in very narrow lines. (`#77 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/77>`__)
- Big update of gain algorithm to use high-pass-filtered lamp gains and more thoughtfully filtered solar gains in tandem
  to remove both detector and optical response variations. (`#77 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/77>`__)
- Compute beam 2's rotation angle so that its spectra line up with those from beam 1 (instead of just straightening the hairlines). (`#81 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/81>`__)
- Improve beam/modstate offset matching in cases where the beams have low-frequency illumination differences. (`#81 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/81>`__)


Bugfixes
--------

- Update version of `dkist-processing-math` to fix bug in angle finding algorithm. (`#78 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/78>`__)


Misc
----

- Re-pin `asdf == 2.10.1` in "grogu" install target. Needed because `airflow`. (`#79 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/79>`__)
- Move to `scipy==1.9.0`. This has some implications with calculations in the WriteL1 task; constant arrays will now cause this task to fail. (`#80 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/80>`__)


v0.18.1 (2022-08-09)
====================

Misc
----

- Corrected workflow naming in docs.


v0.18.0 (2022-08-08)
====================

Misc
----

- Update minimum required version of `dkist-processing-core` due to breaking changes in workflow naming.


v0.17.1 (2022-08-03)
====================

Bugfixes
--------

- Use nearest neighbor interpolation to resize movie frames. This helps avoid weirdness if the maps are very small. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/101>`__)


v0.17.0 (2022-07-28)
====================

Features
--------

- Add ability to handle transposed WCS headers and reorder them correctly in output L1 data. (`#76 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/76>`__)


v0.16.0 (2022-07-21)
====================

Bugfixes
--------

- Fix ordering of dataset header keywords. (`#75 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/75>`__)

Features
--------

- Bumped version of dkist-processing-common in setup.cfg. The change adds microsecond support to datetimes, prevents quiet file overwriting by default, and sets the default fits compression tile size to astropy defaults.


v0.15.0 (2022-07-14)
====================

Features
--------

- Save PolCal metrics for inclusion in quality report document. (`#71 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/71>`__)
- Use bi-cubic interpolation when upsampling to produce smoother demodulation matrices. (`#72 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/72>`__)
- Modstate/beam offset calculation now ignores regions that aren't associated with strong spectral features when computing offset. (`#74 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/74>`__)


v0.14.1 (2022-06-27)
====================

Bugfixes
--------

- Bumped version of dkist-header-validator in setup.cfg.
  The change fixes a bug in handling multiple fits header commentary cards (HISTORY and COMMENT). (`#73 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/73>`__)


v0.14.0 (2022-06-20)
====================

Features
--------

- Change how L1 filenames are constructed.

v0.13.1 (2022-06-14)
====================

Features
--------

- Add capability to handle summit aborts or cancellations mid observation. (`#69 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/69>`__)


v0.13.0 (2022-06-13)
====================

Features
--------

- Compute Calibration Unit parameters once over entire FOV prior to fitting demodulation matrices for the requested bins (`#70 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/70>`__)


v0.12.1 (2022-06-03)
====================

Misc
----

- Update for new `dkist_processing_pac` API (version 0.7.0) (`#68 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/68>`__)


v0.12.0 (2022-05-12)
====================

Features
--------

- Remove `RewriteInputFramesToCorrectHeaders` and the "l0_to_l1_visp_rewrite_input_headers_workflow". (`#67 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/67>`__)
- Use map scan numbers to build movie images. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/67>`__)
- Move determination of map scan structure to the `Parse` task. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/67>`__)
- Use map scan numbers as the DINDEXn value for the second spatial dimension. (`#67 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/67>`__)


Misc
----

- Replace all code usages of "DSPS repeat" with "map scan". (`#67 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/67>`__)


v0.11.0 (2022-05-02)
====================

Features
--------

- Allow non-integer binning of FOV when computing demodulation matrices (`#64 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/64>`__)

Bugfixes
--------

- Use new version of `dkist-processing-common` (0.18.0) to correct source for "fpa exposure time" keyword

Misc
----

- Raise KeyError if a header doesn't have a key expected by the `VispFitsAccess` classes (`#65 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/65>`__)


v0.10.0 (2022-04-28)
====================

Features
--------

- FITS specification now uses Rev. F of SPEC0122 as a base. (`#66 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/66>`__)


v0.9.1 (2022-04-22)
===================

Bugfixes
--------

- Change movie codec for better compatibility.

v0.9.0 (2022-04-21)
===================

Features
--------

- Add support for (somewhat) arbitrary sampling of FOV when computing demodulation matrices (`#62 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/62>`__)
- Save best-fit flux from Calibration Unit fit (`#63 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/63>`__)


Misc
----

- Polcal binning values moved from `dkist_processing_visp.models.constants` to `dkist_processing_visp.models.parameters` (`#62 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/62>`__)
- Collect InstPolCal QA-esq object generation into a single function (`#63 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/63>`__)


v0.8.3 (2022-04-19)
===================

Misc
----

- Bump version of `dkist-processing-common` to 0.17.3

v0.8.2 (2022-04-06)
===================

Misc
----

- Refactor Science task to save some I/O (`#61 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/61>`__)


v0.8.1 (2022-04-04)
===================

Features
--------

- APM steps added to RewriteInputFramesToCorrectHeaders task.


v0.8.0 (2022-04-04)
===================

Features
--------

- Fail fast if multiple frames are found for a single (dsps, modstate, raster step) tuple. (`#58 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/58>`__)
- New workflow that includes a task to dynamically overwrite DKIST008 and DKIST009 header values. (`#60 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/60>`__)


v0.7.2 (2022-03-25)
===================

Bugfixes
--------
- Restore correct passing of PA&C fit parameters

v0.7.1 (2022-03-25)
===================

Bugfixes
--------
- Don't fail in spectrographic mode with compressed inputs

v0.7.0 (2022-03-25)
===================

Features
--------

- Don't split beams in separate task (`#53 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/53>`__)
- Fail fast if an incomplete raster map is detected (`#54 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/54>`__)


Bugfixes
--------

- Fix DPNAME descriptions in L1 data and start DINDEX3 at 1 (`#50 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/50>`__)
- Processed polarimetric frames now have DATE-BEG equal to earliest input modstate and DATE-END equal to latest input modstate + exposure time (`#52 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/52>`__)
- Fix negative sign error and issue with low slit-hairline contrast in Geometric task (`#56 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/56>`__)


Misc
----

- Update `VispL0QualityMetrics` to use new paradigm in `dkist-procesing-common` v0.17.0 `#55 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/55>`__


v0.6.0 (2022-03-18)
===================

Features
--------

- Increase usefulness of APM logging for debugging pipeline performance (`#48 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/48>`__)


Bugfixes
--------

- Fix bug mismatching tags when writing intermediate frames (`#49 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/49>`__)


Documentation
-------------

- Update docs to conform to pydocstyle (`#51 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/51>`__)


v0.5.1 (2022-03-11)
===================

Documentation
-------------

- Use `use_M12` PA&C Fit mode as default
- Add full code documentation (`#45 <https://bitbucket.org/dkistdc/dkist-processing-visp/pull-requests/45>`__)

v0.5.1 (2022-03-10)
===================

First release to be run on DKIST summit data
