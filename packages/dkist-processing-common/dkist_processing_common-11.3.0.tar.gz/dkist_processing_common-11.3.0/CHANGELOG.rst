v11.3.0 (2025-08-30)
====================

Misc
----

- Split out writing L1 frame timing headers so that their calculation can be separately defined by instruments, as required. (`#263 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/263>`__)
- Update pre-commit hook versions and replace python-reorder-imports with isort. (`#264 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/264>`__)


v11.2.1 (2025-08-12)
====================

Bugfixes
--------

- Add `multi_plot_data` to quality creation mutation when submitting quality report data. (`#262 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/262>`__)


Misc
----

- Explicitly set color and ordering of lines in wavecal metric plots.
  This gets around issues with order not being preserved in the quality database. (`#262 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/262>`__)
- Update database name for vertical multi-pane plot metric data. It's now called "multi_plot_data". (`#262 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/262>`__)


v11.2.0 (2025-07-18)
====================

Bugfixes
--------

- Move the writing of spectral line keys in L1 data to later in the process, after the instruments have had a chance to rewrite the WCS info. (`#252 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/252>`__)


v11.1.0 (2025-07-15)
====================

Misc
----

- The graphql and input dataset models are now set to validate whenever attributes are assigned, including after instantiation. (`#255 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/255>`__)
- Create a factory for custom `FakeGQLClient` used in tests.  The factory and associated default returns live in a
  new `mock_metadata_store.py` module in the tests directory.  `FakeGQLClient` is now a test fixture and does not need to
  be imported in tests. (`#255 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/255>`__)
- Fix a Pydantic warning in the graphql model.  Because we validate the `RecipeRunConfiguration` as a JSON dictionary and
  convert it to a model after validation, we need a serializer so Pydantic knows what to expect back out. (`#258 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/258>`__)


v11.0.1 (2025-07-10)
====================

Bugfixes
--------

- Ignore NaN and Inf values when storing the quality results of a wavelength calibration fit. (`#260 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/260>`__)


Misc
----

- Removing usages of `pkg_resources`, which is on track to be deprecated. (`#254 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/254>`__)


v11.0.0 (2025-07-02)
====================

Features
--------

- Move `location_of_dkist` from the `WriteL1` task to its own module (`~dkist_processing_common.models.dkist_location`).
  Also make it a constant variable instead of a function. (`#256 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/256>`__)
- `Stems` that only match a specific task types can now check against a list of task types.
  This replaces the `ip_task_type` kwarg with `ip_task_types` (which can still be a single string, if desired.) (`#257 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/257>`__)
- Add ability to store and build a quality metric showing the results of wavelength calibration. (`#259 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/259>`__)


v10.9.0 (2025-06-02)
====================

Features
--------

- Add two new codecs:  Basemodel codecs are used for encoding and decoding Pydantic BaseModel objects.  For decoding, the intended model
  is passed to the decoder through a keyword argument in the task read method.  Array codecs are used for encoding and decoding numpy
  arrays similar to the standard np.load() and np.save(), but with the task tag-based write method. (`#235 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/235>`__)


Misc
----

- Remove the input_dataset mixin and replace it with input_dataset Pydantic BaseModel models. (`#235 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/235>`__)
- Change the behavior of ParameterBase such that it takes the task scratch as an argument to provide access to the
  parameter document and parameters that are files.  This behavior replaces the input dataset mixin parameter read method. (`#235 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/235>`__)


v10.8.3 (2025-05-28)
====================

Features
--------

- Further constrain when the ATMOS_R0 header key is written in L1 data based on the following metrics:

  * the ATMOS_R0 value in the L0 data must be less than or equal to 30cm
  * the AO_LOCK value in the L0 data must be True
  * the OOBSHIFT value in the L0 data must be less than 100

  The wavefront sensor has about 1500 subapertures from which x and y shifts are measured. When the adaptive optics loop is locked, we count how many of these shifts exceed a threshold considered to be out of bounds. The r0 measurement gets less accurate as more of these shifts are out of bounds and so this is another way to detect outliers in the r0 value. (`#250 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/250>`__)


v10.8.2 (2025-05-27)
====================

Bugfixes
--------

- Prevent the `WAVEBAND` key from being populated with a spectral line that falls outside the wavelength bounds of the data. (`#251 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/251>`__)


v10.8.1 (2025-05-22)
====================

Misc
----

- Update `dkist-processing-core` to v5.1.1. (`#253 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/253>`__)


v10.8.0 (2025-05-15)
====================

Features
--------

- Add checksum verification to the hdu decoder. (`#222 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/222>`__)


Bugfixes
--------

- Modify usage of CompImageHeader to support astropy 7. (`#222 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/222>`__)


v10.7.2 (2025-04-21)
====================

Bugfixes
--------

- Fix a bug in which the AO_LOCK header key is assumed to exist.  The AO_LOCK header key is optional. (`#249 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/249>`__)


v10.7.1 (2025-04-17)
====================

Bugfixes
--------

- Fix a bug exposed by updates in the `dkist-inventory` package that did not manage HISTORY or COMMENT cards correctly. (`#248 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/248>`__)


v10.7.0 (2025-04-14)
====================

Features
--------

- New data percentiles are added to the headers to make the range symmetric. (`#242 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/242>`__)
- L1 headers are now created by removing only the keys listed in SPEC-122 as opposed to removing all keys not present in SPEC-214. In addition, any SPEC-214 keys marked as `level0_only` are removed. This will allow spurious header keys to be discovered more easily. (`#246 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/246>`__)


Bugfixes
--------

- Header keys that write the percentiles of the data are now correctly named (from DATA<pp> to DATAP<pp>). (`#242 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/242>`__)


Misc
----

- Prevent header keys from being included if they are not a part of the Level 1 SPEC-0214 specification. (`#242 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/242>`__)
- Add missing build dependency specifications. (`#247 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/247>`__)


v10.6.4 (2025-03-31)
====================

Bugfixes
--------

- Allow input dataset IDs to be conditionally written into the L1 data headers. (`#243 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/243>`__)


v10.6.3 (2025-03-27)
====================

Bugfixes
--------

- Fix a bug where transfer input dataset fails if any of the input dataset part documents are missing. (`#241 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/241>`__)
- Pydantic model validator now returns the validated instance. (`#240 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/240>`__)

v10.6.2 (2025-03-19)
====================

Bugfixes
--------

- Fix a bug in manual processing where a metadata store dataclass has been previously converted to
  a Pydantic BaseModel.  Add a test that will catch future similar bugs. (`#239 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/239>`__)


Misc
----

- Add coverage badge to README.rst. (`#238 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/238>`__)


v10.6.1 (2025-03-14)
====================

Misc
----

- Convert dataclasses in the graphql model to Pydantic BaseModels for additional validation. In the
  RecipeRunResponse class, configuration is converted from a JSON dictionary to its own Pydantic BaseModel.
  In the InputDatasetPartResponse class, the inputDatasetPartDocument is now returned as a list of dictionaries. (`#236 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/236>`__)
- Change returns from the metadata store queries into Pydantic BaseModel instances.  Remove unnecessary parsing
  and error checking in the metadata store mixin. (`#236 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/236>`__)


v10.6.0 (2025-03-03)
====================

Features
--------

- Add the `RetarderNameBud` that can parse the name of the GOS retarder and ensure that only a single retarder was used
  for the given set of POLCAL input data. (`#235 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/235>`__)


v10.5.15 (2025-02-24)
=====================

Misc
----

- Update dkist-processing-core to 5.1.0 to use apache-airflow 2.10.5. (`#234 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/234>`__)


v10.5.14 (2025-02-19)
=====================

Features
--------

- Compute PRODUCT L1 header key from IDSOBSID and PROCTYPE.  The minimum productId length is 8 characters. (`#232 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/232>`__)


v10.5.13 (2025-02-14)
=====================

Misc
----

- Bump version of `dkist-processing-core` to 5.0.0; automated processing workers will now use the "frozen" pip extra of
  instrument pipelines to ensure a constant environment for a given version of that pipeline. (`#233 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/233>`__)


v10.5.12 (2025-02-12)
=====================

Features
--------

- Compute datasetId using sqids rather than hashids.  The minimum datasetId length is now 6 characters. (`#231 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/231>`__)


v10.5.11 (2025-02-06)
=====================

Misc
----

- Use the new `dkist_inventory.asdf_generator.make_asdf_file_object` helper function and add a history entry to the trial framework ASDF. (`#230 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/230>`__)


v10.5.10 (2025-02-04)
=====================

Features
--------

- Convert the parse_tag method in scratch from private to public. (`#225 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/225>`__)
- Add list flattening before building a generic filename based on tags to allow for nested lists of tags. (`#225 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/225>`__)


Misc
----

- Fix typo in tags, ``task_geometric_sepectral_shifts`` -> ``task_geometric_spectral_shifts``.  Add type hinting to tags. (`#225 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/225>`__)
- Update Bitbucket pipelines to use execute script for standard steps. (`#229 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/229>`__)


v10.5.9 (2025-01-29)
====================

Bugfixes
--------

- Update to dkist-processing-common which handles a bug in dacite==1.9.0


v10.5.8 (2025-01-27)
====================

Bugfixes
--------

- Add more splitting characters to improve the accuracy of getting base package names.


v10.5.7 (2025-01-27)
====================

Features
--------

- Prevent colons from being written as part of tag-created filenames due to being an illegal character under some operating systems. (`#227 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/227>`__)


Misc
----

- Remove usage of the deprecated `pkg_resources` module. (`#204 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/204>`__)
- Update bitbucket pipelines to use common scripts for checking for changelog snippets and verifying doc builds. (`#228 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/228>`__)


v10.5.6 (2025-01-09)
====================

Misc
----

- Upgrade to dkist-processing-core 4.3.0. (`#226 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/226>`__)


v10.5.5 (2024-12-20)
====================

Misc
----

- Update Bitbucket pipelines to use standardized lint and scan steps. (`#224 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/224>`__)


Documentation
-------------

- Change the documentation landing page to focus more on users and less on developers. (`#223 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/223>`__)


v10.5.4 (2024-12-18)
====================

Features
--------

- Change the quality report to plot and calculate the average of the Fried parameter only where the AO lock status is True. (`#221 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/221>`__)
- Remove the Fried parameter header keyword from final FITS files where the AO system was unlocked. (`#221 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/221>`__)


v10.5.3 (2024-11-25)
====================

Misc
----

- Pinning astropy upperbound to < 7.0.0 (`#220 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/220>`__)


v10.5.2 (2024-11-21)
====================

Misc
----

- Upgrade to dkist-inventory 1.4.3 which patches a bug in creating dataset inventory from SPECLN* keys.


v10.5.1 (2024-11-20)
====================

Bugfixes
--------

- Constrain asdf < 4.0.0


v10.5.0 (2024-11-20)
====================

Features
--------

- Modify movie assembly to manage a breaking change in the moviepy API. (`#219 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/219>`__)
- Modify the asdf decoder to manage a breaking change in the asdf API. (`#219 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/219>`__)


v10.4.0 (2024-11-14)
====================

Misc
----

- Functions that build the list of items to transfer for a trial outflow are now based on lists of tags
  instead of configuration switches. (`#218 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/218>`__)
- Refactor `TranferTrialDataBase` from an inherited base class to a standalone class
  and rename it `TransferTrialData`. (`#218 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/218>`__)


v10.3.0 (2024-10-15)
====================

Features
--------

- Update the machinery in `quality_store_polcal_results` to handle NaN values.
  This is required for the new error-handling paradigm in `dkist-processing-pac` v3.1.0. (`#214 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/214>`__)
- Add new argument, `num_points_to_sample`, to `quality_store_polcal_results`, which allows a user to reduce the number of points saved for inclusion in the quality report.
  This allows us to mitigate large quality metrics. (`#215 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/215>`__)


Bugfixes
--------

- Correctly clean up tags used for file name uniqueness. (`#217 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/217>`__)


v10.2.2 (2024-10-14)
====================

Misc
----

- Switch from setup.cfg to pyproject.toml for build configuration (`#214 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/214>`__)
- Make and publish wheels at code push in build pipeline (`#214 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/214>`__)


v10.2.1 (2024-09-27)
====================

Misc
----

- Upgrade to dkist-processing-core 4.2.1 which patches a bug causing the doc builds to fail. (`#213 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/213>`__)


v10.2.0 (2024-09-27)
====================

Misc
----

- Upgrade dkist-processing-core to 4.2.0 which includes the upgrade of airflow to 2.10.2. (`#212 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/212>`__)


v10.1.0 (2024-09-26)
====================

Features
--------

- Adding the `NearFloatBud` and `TaskNearFloatBud` for use in parsing, for when numeric values in a given header should be within a given range. (`#207 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/207>`__)


v10.0.1 (2024-09-24)
====================

Bugfixes
--------

- "FRAMEVOL" key in L1 headers now correctly reports the on-disk size (in MB) of each file. (`#211 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/211>`__)


Misc
----

- Add test coverage for the interservice bus mixin (`#209 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/209>`__)


v10.0.0 (2024-09-23)
====================

Features
--------

- Remove usage of `self.tags` from `WriteL1` task. This greatly improves database usage. It is a breaking change because
  OUTPUT files will no longer share extra tags with their corresponding CALIBRATED files and as a result any downstream
  tasks that depend on richer tags on OUTPUT files will need to swap to using CALIBRATED files instead. (`#210 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/210>`__)


v9.1.0 (2024-09-10)
===================

Misc
----

- Accommodate changes to the GraphQL API associated with refactoring the quality database (`#208 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/208>`__)


v9.0.0 (2024-08-20)
===================

Features
--------

- Greatly improve performance of `QualityL0Metrics` task by eliminating calls to tag database to determine the TASK type
  of *every* file. Instead we now explicitly loop over the TASKs we want and read only those files. (`#205 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/205>`__)
- Allow language in polcal metrics to support binning schemes that aren't 2 dimensional.
  For example, we can now have "...spanning 4 spatial bins." or "...spanning 2 spectral, 4 spatial, and 5 mosaic bins.".
  Any dimensionality is supported (except zero). (`#206 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/206>`__)


v8.2.2 (2024-07-25)
===================

Misc
----

- Rewrite to eliminate warnings in unit tests. (`#203 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/203>`__)


v8.2.1 (2024-07-12)
===================

Bugfixes
--------

- Fix bug that accumulated workflow task tags on files written to scratch if the tags passed in were a list and were reused for multiple writes. (`#202 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/202>`__)


v8.2.0 (2024-07-10)
===================

Misc
----

- Make private methods public when we want them to show up in the ReadTheDocs documentation. (`#201 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/201>`__)


v8.1.0 (2024-07-01)
===================

Misc
----

- Update dkist-processing-core to 4.1.0 which includes an upgrade to airflow 2.9.2. (`#200 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/200>`__)
- Update the instructions for development to include the dependency on redis. (`#200 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/200>`__)


v8.0.0 (2024-06-20)
===================

Features
--------

- Default behavior of `ParameterBase._find_most_recent_past_value` is to use `obs_ip_start_time` as the date. Previously
  the default had been `datetime.now()`. An implication of this is that *all* users of `ParameterBase` should instantiate
  their parameters object with `obs_ip_start_time`. The one exception is parameters needed for parsing, which should
  explicitly pass `datetime.now()` to the `start_date` kwarg of `_find_most_recent_past_value`. (`#198 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/198>`__)
- Add the `ParameterArmIdMixin` for defining parameters that depend on the value of an arm ID constant. (`#199 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/199>`__)
- A method to `ParameterBase` (`_load_param_value_from_fits`) for loading file parameters saved as FITS files. (`#199 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/199>`__)
- Add method to `ParameterBase` (`_load_param_value_from_numpy_save`) for loading file parameters saved as numpy save files. (`#199 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/199>`__)


v7.0.0 (2024-06-03)
===================

Misc
----

- Update `sphinx-auotapi` pin to only exclude the breaking version. The bug was fixed in subsequent versions. (`#195 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/195>`__)
- Resolve matplotlib version conflict (`#196 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/196>`__)
- Upgrade dkist-processing-core to support airflow to 2.9.1 which includes the dependency on pydantic 2 and consequently a few other libraries that needed upgrading for the same pydantic 2 dependency. (`#197 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/197>`__)


v6.2.4 (2024-05-20)
===================

Bugfixes
--------

- No longer crash when building polcal metrics where some CS steps had `I_sys` fixed during the polcal fit. (`#193 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/193>`__)


Misc
----

- Change the DKIST site time zone to US/Hawaii to correctly account for daylight savings time. (`#192 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/192>`__)
- Pin `sphinx-autoapi` to avoid failure in doc build. (`#194 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/194>`__)


v6.2.3 (2024-05-09)
===================

Features
--------

- Save all floating point arrays as float32. The extra precision of float64 is not needed, especially when lossy quantization is applied before compression. (`#191 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/191>`__)


Bugfixes
--------

- `QualityMixin.avg_noise` is now NaN aware. I.e., it will ignore NaN values when computing the noise. (`#190 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/190>`__)


Misc
----

- Cap the length of browse movies at 60 seconds by default. (`#189 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/189>`__)


v6.2.2 (2024-05-07)
===================

Features
--------

- Add the ability to create a quality report from a trial workflow. (`#185 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/185>`__)


Bugfixes
--------

- `QualityL0Metrics.calculate_l0_metrics` now correctly identifies the TASK type. Previously it could have erroneously used the WORKFLOWTASK tag to find the IP TASK TYPE. (`#185 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/185>`__)


v6.2.1 (2024-05-01)
===================

Misc
----

- Change filenames of browse movie and quality report to free up namespace for other future files. (`#124 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/124>`__)
- Trial framework asdf filenames match production run asdf filenames. (`#186 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/186>`__)
- Capture tracing data for rollback calls to enhance observability. (`#187 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/187>`__)
- Update legacy type hinting. (`#188 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/188>`__)


v6.1.2 (2024-04-12)
===================

Misc
----

- Refactor retrieval of input dataset parts to only occur when directly requested. (`#180 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/180>`__)
- Populate MANPROCD header key (which denotes if any steps had manual intervention) in L1 data based upon the provenance records for the run. (`#181 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/181>`__)


v6.1.1 (2024-04-10)
===================

Misc
----

- Audit scratch write/tag before they happen so if a failure occurs during or between write and tag, the rollback feature will still perform an idempotent removal. (`#182 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/182>`__)
- Cache the result of checking if a tag is new for the purposes of auditing tags added by a task. (`#183 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/183>`__)
- Retry connection errors that can occur during a connection to Redis. (`#184 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/184>`__)


v6.1.0 (2024-04-04)
===================

Features
--------

- Implement a common 'rollback' method on all Tasks, and Task specific rollback steps where applicable, to facilitate manual processing and operational fault remediation/recovery. (`#177 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/177>`__)


Misc
----

- Make the scratch inventory (Redis) db count configurable through an environment variable with a default which remains the same as the previously hardcoded value. (`#177 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/177>`__)


v6.0.4 (2024-03-26)
===================

Bugfixes
--------

- `FitsAccessBase.from_header` no longer clobbers "NAXISn" (and likely other FITS controlled keys) values from input header. (`#179 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/179>`__)


v6.0.3 (2024-03-05)
===================

Features
--------

- Populate new L1 header keyword `SOLARRAD` in all L1 data with the value of the solar angular radius as seen by an observer located at the DKIST site, in arcseconds. (`#176 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/176>`__)


v6.0.2 (2024-03-04)
===================

Bugfixes
--------

- Trial ASDF files no longer contain the absolute scratch path in the filenames. They are now relative to the generated
  ASDF file, which mimics the behavior in non-trial ASDF generation. (`#175 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/175>`__)


Misc
----

- No longer log a warning when no paths are found for a set of tags. (`#174 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/174>`__)


v6.0.1 (2024-02-29)
===================

Features
--------

- Support arbitrarily nested lists of tags for tag database operations. (`#172 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/172>`__)


Bugfixes
--------

- All movies are now forced to have an even number of pixels in each dimension. This is a requirement of the H.264 codec; if the dimensions
  are odd then some players/browsers will be unable to play the movies. (`#173 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/173>`__)


Misc
----

- Update object-clerk to 0.1.1 to remove the logging of bytes objects. (`#171 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/171>`__)


v6.0.0 (2024-02-15)
===================

Misc
----

- Allow `fits_array_encoder` to accept a `dict` header (previously header had to be `fits.Header`). (`#165 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/165>`__)
- Completely remove `FitsDataMixin`. Use `self.read` and `self.write` with codecs instead. (`#166 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/166>`__)


v5.1.1 (2024-02-01)
===================

Misc
----

- Add a switch to add movie files to a Globus transfer list in a trial workflow. (`#168 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/168>`__)


v5.1.0 (2024-01-25)
===================

Misc
----

- Add tasks to simulate the generation of dataset inventory and ASDF files for 'Trial' workflows. (`#162 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/162>`__)
- Update minimum version of pillow to address security vulnerability. (`#167 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/167>`__)


v5.0.1 (2024-01-12)
===================

Bugfixes
--------

- Add "STOKES" key to all L1 headers. Non-polarimetric data will always have a value of "I". This matches how data are
  treated in inventory. (`#164 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/164>`__)


Misc
----

- Update `dkist-fits-specifications` and associated (validator, simulator) to use new conditional requiredness framework. (`#164 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/164>`__)


v5.0.0 (2023-12-20)
===================

Misc
----

- Upgrade dkist-processing-core to 3.0.1 which includes manual-processing-worker build utilities. (`#163 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/163>`__)


v4.2.0 (2023-11-28)
===================

Features
--------

- Add `TaskName` enum that holds the strings related to specific IP task types. Also add corresponding tags (e.g., `Tag.task_dark()`). (`#151 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/151>`__)
- `ParameterBase` now takes and stores observe IP start time as an optional kwarg. (`#152 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/152>`__)
- Add `TaskUniqueBud`, a version of `UniqueBud` that only parses files from a given IP task. (`#153 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/153>`__)
- Add `ObserveWavelengthBud` that produces a constant equal to the wavelength of the OBSERVE frames. (`#154 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/154>`__)
- Provide standard methods for more complicated header IP task parsing (e.g., for lamp/solar gain or polcal darks/clears). (`#155 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/155>`__)
- Add standardized wavelength-aware mixin that can be used to add wavelength-dependent parsing to `ParameterBase` subclasses. (`#156 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/156>`__)
- Add codec for ASDF files. (`#157 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/157>`__)
- Add `auto_squeeze` kwarg to `fits_array_decoder` to match behavior of `FitsAccessBase` objects. This kwarg squeezes out dummy WCS dimensions present in raw summit data. (`#158 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/158>`__)
- Add `angle_round_ndigits` kwarg to `CSStep` object that specifies the desired precision when matching the angles of GOS optics. The default rounding amount has also been changed from 3 digits to 1 digit (tenth's place). (`#159 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/159>`__)


Misc
----

- Greatly improve speed of parsing by intelligently caching the `Stem.petals` property. (`#160 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/160>`__)


v4.1.5 (2023-11-24)
===================

Misc
----

- Use the latest version dkist-processing-core which patches security vulnerabilities and deprecations. (`#161 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/161>`__)


v4.1.4 (2023-10-11)
===================

Misc
----

- Update metadata-store-api calls to use new framework paradigms for authorization, queries, and mutations. (`#150 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/150>`__)
- Centralize environment configuration using the dkist-service-configuration library. (`#150 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/150>`__)


v4.1.3 (2023-09-29)
===================

Misc
----

- Clean up APM spans in the WriteL1Frame task class. (`#149 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/149>`__)


v4.1.2 (2023-09-08)
===================

Misc
----

- Use the latest version dkist-processing-core which adds the ability to select different resource queues for tasks in a workflow. (`#148 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/148>`__)


v4.1.1 (2023-09-05)
===================

Misc
----

- Change how intermediate files are named to use a sequence number to enforce uniqueness across identically tagged files. (`#146 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/146>`__)
- Log when APM spans are created to provide some info in the case of SIGTERM process failures. (`#147 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/147>`__)


v4.1.0 (2023-07-28)
===================

Features
--------

- New Buds and Flower to parse per-readout exposure time and number of readouts per FPA. (`#145 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/145>`__)


v4.0.3 (2023-07-26)
===================

Misc
----

- Updating dkist-header-validator to include python 3.10 support.


v4.0.2 (2023-07-17)
===================

Bugfixes
--------

- Updates to support new major revisions of `pillow` and `pydantic`. (`#142 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/142>`__)


Misc
----

- Update to latest dkist-header-validator. (`#143 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/143>`__)


v4.0.1 (2023-07-11)
===================

Misc
----

- Update core dependency for airflow upgrade. (`#143 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/143>`__)


v4.0.0 (2023-06-29)
===================

Misc
----

- Move to dkist-processing-core 1.5.0 which includes airflow 2.6.2 and python 3.11 support. (`#141 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/141>`__)


v3.0.0 (2023-06-27)
===================

Features
--------

- Tag all files written with the name of the task that wrote the file.  This is expected to be helpful in fault analysis. (`#138 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/138>`__)
- Add DEBUG tags for writing files that are easily identifiable for later retrieval. (`#139 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/139>`__)
- Base task to facilitate "trial" workflows that save specific (and arbitrary) pipeline products to a special development bucket for further analysis. (`#139 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/139>`__)
- Redesign `WorkflowTaskBase` `read` and `write` to accept decoders and encoders. The result is that `read` and `write` are now the methods to be
  used in *all* cases of reading and writing (i.e., we no longer need different read/write functions for different data types). A library of codecs
  is also provided for all data types currently used. (`#140 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/140>`__)


v2.7.0 (2023-05-17)
===================

Misc
----

- Refactor parsing task to support more varied use cases by defining more abstract components that can be composed. (`#137 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/137>`__)


v2.6.0 (2023-05-05)
===================

Misc
----

- Update dkist-processing-core to 1.4.0 which includes an upgrade to airflow 2.6.0 (`#136 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/136>`__)


v2.5.0 (2023-05-02)
===================

Bugfixes
--------

- Replace `astropy.time.Time` with `datetime.datetime` for reading header "DATE-OBS" values in `ParseL0InputData` task. This should produce a very large speedup in the task when parsing large datasets. (`#134 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/134>`__)


Misc
----

- Set WAVEMIN and WAVEMAX header keys based on abstract method get_wavelength_range implemented by each instrument (`#133 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/133>`__)
- Improved `__repr__` in `CSStep` and `FitsAccessBase` objects. The latter affects all `*FitsAccess` subclasses as well. (`#135 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/135>`__)


v2.4.1 (2023-04-14)
===================

Misc
----

- remove spectral line support from dkist-processing-common because it now resides in `dkist-spectral-lines <https://pypi.org/project/dkist-spectral-lines/>`_ (`#128 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/128>`__)


v2.4.0 (2023-04-12)
===================

Features
--------

- Make histogram plots of all parameters that are free in local PolCal fits. (`#132 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/132>`__)


Misc
----

- Update polcal quality metric machinery for new `dkist-processing-pac` version (>=2.0.0). (`#129 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/129>`__)
- Normalize use of `logger.[thing]` across repo. Previously had also been using `logging.[thing]`. (`#130 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/130>`__)


v2.3.0 (2023-02-17)
===================

Misc
----

- Update dkist-processing-core to include new version of Airflow


v2.2.0 (2023-02-03)
===================

Features
--------

- Parse proposal and experiment IDs to aggregate information and include it in L1 headers. (`#126 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/126>`__)


v2.1.0 (2023-01-31)
===================

Features
--------

- Added capability to load parameters from files. (`#125 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/125>`__)


v2.0.0 (2022-12-15)
===================

Features
--------

- Expose tag removal at `WorkflowTaskBase` level. Thus tag removal is now directly accessible to all instrument tasks. (`#123 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/123>`__)


Bugfixes
--------

- Fix bug that caused `TagDB.remove` to fail silently if called directly. (`#123 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/123>`__)


Misc
----

- *Require* instruments to provide `DATE-END` calculation in `WriteL1` task. (`#120 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/120>`__)


v1.2.2 (2022-12-05)
===================

Bugfix
------

- Movie file is uploaded separately as movie headers need to be handled.


v1.2.1 (2022-12-02)
===================

Misc
----

- Movie file is uploaded during the Globus transfer instead of separately. (`#121 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/121>`__)
- Add environment variable to configure auth client transport parameters such as retries. (`#122 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/122>`__)


v1.2.0 (2022-11-15)
===================

Misc
----

- Use updated dkist-processing-core version 1.2.0.


v1.1.0 (2022-11-14)
===================

Bugfixes
--------

- Allow quality metric values to be sent to encoder as `np.float32` (which is a single number) type. (`#117 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/117>`__)


Documentation
-------------

- Add changelog to RTD left hand TOC to include rendered changelog in documentation build. (`#119 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/119>`__)


v1.0.3 (2022-11-09)
===================

Bugfixes
--------

- Improve Globus event logging (`#118 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/118>`__)


v1.0.2 (2022-11-08)
===================

Bugfixes
--------

- Handle an empty Globus event list. (`#116 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/116>`__)


v1.0.1 (2022-11-08)
===================

Misc
----

- Be more tolerant of globus error events during a transfer because globus retries and may recover. (`#115 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/115>`__)


v1.0.0 (2022-11-02)
===================

Misc
----

- Upgrade version of the redis client library to move with the redis infrastructure upgrade to 7.x (`#114 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/114>`__)


v0.27.1 (2022-11-02)
====================

Misc
----

- Use updated dkist-processing-core version 1.1.2.  Task startup logging enhancements.


v0.27.0 (2022-10-26)
====================

Bugfixes
--------

- Change `VELOSYS` keyword type from bool to float. (`#113 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/113>`__)


v0.26.2 (2022-10-26)
====================

Bugfixes
--------

- Remove compression and other keys from the headers before refactoring into tables. (`#112 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/112>`__)


v0.26.1 (2022-10-20)
====================

Misc
----

- Make python 3.10 the minimum supported version (`#109 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/109>`__)
- Increase the HTTP timeout for retryable status codes when connecting to the metadata-store-api. (`#111 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/111>`__)


v0.26.0 (2022-10-18)
====================

Features
--------

- Add PolCal metric showing the constant parameters (mirror and p_y) used in polcal model. (`#106 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/106>`__)


Bugfixes
--------

- Re-cast polcal transmission values in quality report as percentages to increase the number of sig figs. (`#106 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/106>`__)
- Use hard-coded location of DKIST to never again need to rely on querying `astropy` databases. (`#107 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/107>`__)


v0.25.2 (2022-10-11)
====================

Bugfixes
--------

- Fix call to globus task status API which fails on transfers greater than 60s (`#110 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/110>`__)


v0.25.1 (2022-10-11)
====================

Bugfixes
--------

- Make dkist-processing-core a pinned dependency because otherwise the automated processing framework can backrev airflow with undesirable results. (`#108 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/108>`__)


Misc
----

- Upgrade to use the globus-sdk version 3.x. (`#108 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/108>`__)


v0.24.0 (2022-09-16)
====================

Features
--------

- Refactor the input dataset mix in to support input dataset parts being accessed individually from the metadata-store-api (`#105 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/105>`__)
- Added the following keys to the 214 headers.
  - IDSPARID: Input Dataset Part Id for parameters
  - IDSOBSID: Input Dataset Part Id for observation frames
  - IDSCALID: Input Dataset Part Id for calibration frames
  - WKFLNAME: Workflow Name
  - WKFLVERS: Workflow Version (`#105 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/105>`__)


v0.23.0 (2022-08-08)
====================

Misc
----

- Update minimum required version of `dkist-processing-core` due to breaking changes in workflow naming.

v0.22.1 (2022-08-03)
====================

Bugfixes
--------

- Use nearest neighbor interpolation to resize movie frames. This helps avoid weirdness if the maps are very small. (`#101 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/101>`__)


Misc
----

- Add logging to WriteL1Frame. (`#103 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/103>`__)
- Improve/add test coverage of polcal quality metric generation. (`#104 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/104>`__)


v0.22.0 (2022-07-20)
====================

Features
--------

- Add microsecond precision to datetimes in headers. (`#98 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/98>`__)
- Compression tile size will revert to defaults chosen by astropy unless otherwise specified in the recipe run configuration. (`#99 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/99>`__)
- Prevent overwriting files on /scratch unless specified with the overwrite flag. (`#100 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/100>`__)


v0.21.1 (2022-07-12)
====================

Bugfixes
--------

- Expose polcal_label_list as property on SubmitQuality so that the polcal metrics actually get built.

v0.21.0 (2022-07-12)
====================

Features
--------

- Add support for new Polcal quality metrics. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/97>`__)
- Replace "Polarimetric Noise" metric with "Sensitivity" metric that applies to both non-polarimetric and polarimetric data. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/97>`__)
- Remove "Polarimetric Sensitivity" metric. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/97>`__)


Misc
----

- Big refactor of `QualityMixin` to split up different metric task types and improve readability. (`#97 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/97>`__)


v0.20.0 (2022-06-15)
====================

Bugfixes
--------

- Repair reference to dataset ID in constructing L1 filenames. (`#96 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/96>`__)


v0.19.0 (2022-06-15)
====================

Features
--------

- Change how L1 filenames are constructed. (`#95 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/95>`__)


v0.18.0 (2022-05-02)
====================

Bugfixes
--------

- Use CAM__004 (XPOSURE) as fpa_exposure_time (`#93 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/93>`__)


v0.17.4 (2022-04-22)
====================

Bugfixes
--------

- Change movie codec to allow for playback on Chrome browsers. (`#94 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/94>`__)


v0.17.3 (2022-04-19)
====================

Bugfixes
--------

- Look for Globus vestigial folders one level higher

v0.17.2 (2022-04-19)
====================

Misc
----

- Delete folder objects created by the Globus transfer of Level 1 data to the object store. (`#92 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/92>`__)


v0.17.1 (2022-03-31)
====================

Features
--------

- Sentinel `Thorn` class that indicates a Bud/Stem shouldn't be picked. Allows for Buds that just check stuff without returning a value. (`#90 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/90>`__)


Misc
----

- Increase verbosity in message publishing APM steps (`#89 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/89>`__)


Documentation
-------------

- Add changelog (`#91 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/91>`__)


v0.17.0 (2022-03-24)
====================

Features
--------

- Exposure "teardown_enabled" configuration kwarg to optionally skip the Teardown task (`#85 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/85>`__)
- Add `.from_path` class method to FitsAccess (`#88 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/88>`__)


Bugfixes
--------

- Fix name of "fpa_exposure_time" parameter (`#86 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/86>`__)
- Report correct units (adu / s) for quality report RMS values (`#87 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/87>`__)
- Save resources in quality metrics task by using paths instead of full FitsAccess objects (`#88 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/88>`__)


v0.16.3 (2022-03-18)
====================

Bugfixes
--------

- Remove some vestigial raw `self.apm_step` calls

v0.16.2 (2022-03-18)
====================

Features
--------

- Increase usefulness of APM logging with type-specific spans (`#84 <https://bitbucket.org/dkistdc/dkist-processing-common/pull-requests/84>`__)

v0.16.1 (2022-03-10)
====================

Misc
----

- Add graphviz to build env so docs render correctly

v0.16.0 (2022-03-10)
====================

First version to be used on DKIST summit data
