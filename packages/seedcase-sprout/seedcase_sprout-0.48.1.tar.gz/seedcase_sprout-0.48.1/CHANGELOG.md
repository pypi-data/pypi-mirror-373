## 0.48.1 (2025-09-01)

### Refactor

- :recycle: apply changes from copier template

## 0.48.0 (2025-08-25)

### Feat

- :sparkles: add field information to README (#1510)

## 0.47.3 (2025-08-19)

### Fix

- :lipstick: improve badge quality by setting them as SVGs (#1507)

## 0.47.2 (2025-08-18)

### Fix

- :bug: revert syncing with `template-python-package` (#1508)

## 0.47.1 (2025-07-25)

### Fix

- :bug: do not create duplicate batch files (#1493)

## 0.47.0 (2025-07-25)

### Feat

- :sparkles: dedent resource and field descriptions in `write_properties()` (#1488)

## 0.46.6 (2025-07-23)

### Refactor

- 🚚 rename obj in package properties script to `package_properties` (#1484)

## 0.46.5 (2025-07-23)

### Refactor

- :recycle: rename properties script to `package_properties.py` (#1482)

## 0.46.4 (2025-07-23)

### Fix

- :bug: dedent `description` in `as_readme_text()` and `write_properties()` (#1476)

## 0.46.3 (2025-07-03)

### Refactor

- :recycle: move `_get_nested_attr()` into internals (#1455)

## 0.46.2 (2025-06-30)

### Refactor

- ♻️ simplify extraction to field properties only (#1443)

## 0.46.1 (2025-06-30)

### Fix

- :adhesive_bandage: fix `mypy` errors in strict mode (#1437)

## 0.46.0 (2025-06-26)

### Feat

- :sparkles: add `read_resource_data()` (#1433)

## 0.45.2 (2025-06-26)

### Refactor

- :recycle: raise error for non-Parquet batch files (#1428)

## 0.45.1 (2025-06-24)

### Refactor

- :recycle: convert to internal functions with `_` prefix (#1423)

## 0.45.0 (2025-06-23)

### Feat

- :sparkles: add resource properties template (#1369)

## 0.44.12 (2025-06-23)

### Refactor

- :wrench: set up mypy and fix issues from it (#1403)

## 0.44.11 (2025-06-23)

### Refactor

- :recycle: change `fields_match` type to list (#1410)

## 0.44.10 (2025-06-20)

### Fix

- :bug: change `fields_match` to be an array in `extract_resource_properties()` (#1392)

## 0.44.9 (2025-06-19)

### Fix

- :adhesive_bandage: use a temp folder in example code (#1396)

## 0.44.8 (2025-06-12)

### Refactor

- :recycle: don't overwrite the `properties.py` script (#1383)

## 0.44.7 (2025-06-11)

### Refactor

- :recycle: import from `internals` only, not sub-modules of it (#1382)

## 0.44.6 (2025-06-11)

### Fix

- :bug: use camel case in JSON dict (#1389)

## 0.44.5 (2025-06-10)

### Refactor

- :recycle: re-export pprint and textwrap (#1385)

## 0.44.4 (2025-06-10)

### Fix

- :bug: forgot to quote the function in `__all__.py` (#1380)

## 0.44.3 (2025-06-06)

### Refactor

- :recycle: rename to properties_script (#1375)

## 0.44.2 (2025-06-06)

### Refactor

- :fire: remove `MissingValueProperties` (#1374)

## 0.44.1 (2025-06-03)

### Refactor

- ♻️ simplify to only `write_properties()` (#1366)

## 0.44.0 (2025-05-30)

### Feat

- :sparkles: add properties template (#1345)

## 0.43.6 (2025-05-28)

### Refactor

- :recycle: simplify and move into internals (#1348)

## 0.43.5 (2025-05-28)

### Refactor

- :recycle: remove `update_package_properties()` and revise docs (#1355)

## 0.43.4 (2025-05-27)

### Refactor

- :recycle: simplify and make `check_datapackage` self-contained (#1342)

## 0.43.3 (2025-05-22)

### Refactor

- :truck: remove `core` folders (#1336)

## 0.43.2 (2025-05-22)

### Refactor

- :recycle: action of `create_resource_structure()` into `write_resource_batch()` (#1295)

## 0.43.1 (2025-05-21)

### Refactor

- :recycle: update `extract_resource_properties()` to take `pl.DataFrame` (#1264)

## 0.43.0 (2025-05-21)

### Feat

- :sparkles: add custom package name to `ExamplePackage` (#1309)

## 0.42.5 (2025-05-19)

### Fix

- :bug: raise a more informative error when the data list is empty (#1308)

## 0.42.4 (2025-05-13)

### Fix

- :bug: resolve temp paths so tests pass on MacOS as well (#1322)

## 0.42.3 (2025-05-01)

### Refactor

- :recycle: have a default method only for `PackageProperties` (#1304)

## 0.42.2 (2025-04-30)

### Fix

- :bug: do not escape non-ASCII characters when writing JSON (#1305)

## 0.42.1 (2025-04-25)

### Refactor

- :recycle: use `ExamplePackage` in examples (#1301)

## 0.42.0 (2025-04-25)

### Feat

- :sparkles: `write_resource_data()` (#1302)

## 0.41.2 (2025-04-24)

### Refactor

- :recycle: moved functions into internals/location of use (#1298)

## 0.41.1 (2025-04-24)

### Refactor

- :recycle: make master Frictionless - Polars type map (#1284)

## 0.41.0 (2025-04-23)

### Feat

- :sparkles: add default path for path functions (#1285)

## 0.40.1 (2025-04-22)

### Fix

- :lock: fixed bandit flagged issues, moved dataclass gen into `tools/` (#1292)

## 0.40.0 (2025-04-16)

### Feat

- :sparkles: only return `.parquet` files in the batch folder (#1283)

## 0.39.0 (2025-04-16)

### Feat

- :sparkles: finish up `PackagePath` and `resource_batch_files()` (#1282)

## 0.38.3 (2025-04-15)

### Refactor

- :recycle: move `check_properties.py` into root code folder (#1278)

## 0.38.2 (2025-04-15)

### Refactor

- :recycle: move `cdp` constant into `constants.py` (#1279)

## 0.38.1 (2025-04-15)

### Refactor

- :recycle: move all `check_data()` internals into same file (#1275)

## 0.38.0 (2025-04-15)

### Feat

- :sparkles: add example package (#1265)

## 0.37.1 (2025-04-15)

### Refactor

- :recycle: move `write_json()` into internals module (#1274)

## 0.37.0 (2025-04-15)

### Feat

- :sparkles: add simple `root()` method in `PackagePath` (#1280)

## 0.36.4 (2025-04-15)

### Refactor

- :recycle: move `read_*` functions (one) into internal module (#1273)

## 0.36.3 (2025-04-15)

### Refactor

- :recycle: use `_map2()` in `read_resource_batches()` (#1276)

## 0.36.2 (2025-04-15)

### Refactor

- :recycle: move `check_is_*` into internal module (#1271)

## 0.36.1 (2025-04-15)

### Refactor

- :recycle: create a simpler map functional (#1270)

## 0.36.0 (2025-04-14)

### Feat

- :sparkles: `write_resource_batch()` (#1213)

## 0.35.0 (2025-04-14)

### Feat

- :sparkles: get cwd at call time in `PackagePath` (#1266)

## 0.34.0 (2025-04-14)

### Feat

- ✨ `join_resource_batches()` (#1252)

## 0.33.0 (2025-04-14)

### Feat

- :sparkles: use `check_data()` in `read_resource_batches()` (#1263)

## 0.32.2 (2025-04-11)

### Refactor

- :recycle: simplify imports and `__init__.py` file (#1257)

## 0.32.1 (2025-04-11)

### Refactor

- :recycle: match `check_properties()` with design (#1255)

## 0.32.0 (2025-04-11)

### Feat

- :sparkles: check column names in `check_data()` (#1247)

## 0.31.0 (2025-04-11)

### Feat

- :sparkles: `check_data()` with column type checks (#1246)

## 0.30.0 (2025-04-09)

### Feat

- :sparkles: add example data frame (#1244)

## 0.29.1 (2025-04-08)

### Fix

- :bug: update nested objects correctly (#1138)

## 0.29.0 (2025-04-07)

### Feat

- :sparkles: add `read_resource_batches()` - without `check_data()` (#1201)

## 0.28.2 (2025-04-07)

### Refactor

- :recycle: clean split of `check_datapackage` sub-package (#1239)

## 0.28.1 (2025-04-04)

### Refactor

- :recycle: convert `path_` functions into class without checks (#1173)

## 0.28.0 (2025-03-31)

### Feat

- :sparkles: add `example_resource_properties()` (#1212)

## 0.27.1 (2025-03-31)

### Refactor

- :fire: remove multi-user features, we won't be doing them (#1216)

## 0.27.0 (2025-03-27)

### Feat

- :sparkles: add `read_properties()` function (#1156)

## 0.26.9 (2025-03-27)

### Fix

- :bug: check that package and resource properties are `dict`s (#1179)

## 0.26.8 (2025-03-27)

### Refactor

- :recycle: revised to `update_package_properties()` (#1157)

## 0.26.7 (2025-03-27)

### Refactor

- :fire: remove `create_package_properties()` and replace it with `write_*()` (#1153)

## 0.26.6 (2025-03-24)

### Refactor

- :recycle: check column data types (#1111)

## 0.26.5 (2025-03-21)

### Refactor

- :recycle: rename `build_` to `as_readme_text()` (#1172)

## 0.26.4 (2025-03-19)

### Refactor

- :recycle: expose `extract_resource_properties()` (#1152)

## 0.26.3 (2025-03-19)

### Refactor

- :recycle: remove original extension and `.gz` from batch file names (#1147)

## 0.26.2 (2025-03-18)

### Refactor

- 🚚 rename `raw` to `batch` within Python code (#1145)

## 0.26.1 (2025-03-17)

### Refactor

- :recycle: major refactor of path functions to be local-first (#1114)

## 0.26.0 (2025-03-17)

### Feat

- :sparkles: add `check_data_header()` (#1130)

## 0.25.0 (2025-03-17)

### Feat

- :sparkles: add `set_missing_values_to_null()` (#1131)

## 0.24.0 (2025-03-12)

### Feat

- :sparkles: add `read_csv()` to load CSV as DataFrames (#1129)

## 0.23.0 (2025-03-10)

### Feat

- :sparkles: make `build_readme_text()` and `write_file()` public (#1119)

## 0.22.0 (2025-03-06)

### Feat

- :sparkles: add mapping from Frictionless data types to Polars data types (#1106)

## 0.21.1 (2025-03-05)

### Fix

- :bug: only remove qmd files in reference post render to fix md formatting issues (#1107)

## 0.21.0 (2025-03-04)

### Feat

- :sparkles: add `path_readme()` (#1100)

## 0.20.1 (2025-03-04)

### Refactor

- 🚚 rename `create_readme_text()` to `build_readme_text()` (#1099)

## 0.20.0 (2025-02-26)

### Feat

- ✨ extract resource properties from `.json`, `.ndjson`, and `.jsonl` files (#1085)

## 0.19.0 (2025-02-24)

### Feat

- :sparkles: add conversion from resource properties to Pandera schema (#1051)

## 0.18.2 (2025-02-24)

### Refactor

- :recycle: switch `create_package_structure()` to make properties only (#1047)

## 0.18.1 (2025-02-24)

### Refactor

- :recycle: convert `example_package_properties` to function (#1046)

## 0.18.0 (2025-02-21)

### Feat

- ✨ add initial `extract_resource_properties()` (csv, tsv, and parquet files) (#1067)

## 0.17.0 (2025-02-19)

### Feat

- :sparkles: add Pandera checks on the data (#1050)

## 0.16.0 (2025-02-12)

### Feat

- :sparkles: add an `example_package_properties` object (#1044)

## 0.15.0 (2025-02-12)

### Feat

- :sparkles: add `get_nested_attr()` (#1039)

## 0.14.3 (2025-01-28)

### Refactor

- :recycle: use jinja template for README (#1011)

## 0.14.2 (2025-01-28)

### Refactor

- :recycle: commonise Sprout checks (#998)

## 0.14.1 (2025-01-27)

### Refactor

- :recycle: make schema path resolve when working directory different (#1000)

## 0.14.0 (2025-01-27)

### Feat

- :sparkles: add `write_package_properties()` (#984)

## 0.13.3 (2025-01-27)

### Refactor

- :recycle: use checks in `write_resource_properties()` (#990)

## 0.13.2 (2025-01-27)

### Refactor

- :recycle: use new checks in `create_resource_properties()` (#988)

## 0.13.1 (2025-01-27)

### Refactor

- :recycle: use check functions in `edit_package_properties` (#974)

## 0.13.0 (2025-01-24)

### Feat

- ✨ output everything from code cells in Reference docs (#997)

## 0.12.2 (2025-01-24)

### Refactor

- :recycle: `path_package_properties()` -> `path_properties()` (#996)

## 0.12.1 (2025-01-23)

### Refactor

- :recycle: use `CheckErrorMatcher` in Sprout checks (#973)

## 0.12.0 (2025-01-23)

### Feat

- :sparkles: add `CheckErrorMatcher` object (#972)

## 0.11.1 (2025-01-22)

### Refactor

- ♻️  user `Properties` classes in user facing functions (#976)

## 0.11.0 (2025-01-21)

### Feat

- :sparkles: add `check_properties()` (#967)

## 0.10.0 (2025-01-21)

### Feat

- :sparkles: add `check_package_properties()` (#966)

## 0.9.0 (2025-01-21)

### Feat

- :sparkles: add `check_resource_properties()` (#965)

## 0.8.0 (2025-01-21)

### Feat

- :sparkles: collect all Sprout-specific property errors (#964)

## 0.7.0 (2025-01-21)

### Feat

- :sparkles: add functions to check required and blank fields (#963)

## 0.6.0 (2025-01-21)

### Feat

- :sparkles: add simple helper functions (#962)

## 0.5.0 (2025-01-20)

### Feat

- :sparkles: put required fields into constants (#961)

## 0.4.0 (2025-01-20)

### Feat

- :sparkles: Add custom `CheckError` for check functions (#924)

## 0.3.0 (2025-01-20)

### Feat

- :sparkles: add custom renderer to remove floating `:` (#959)

## 0.2.4 (2025-01-10)

### Refactor

- :recycle: can't use the word global on it's own, so renamed to path
- :truck: rename sprout root to sprout global

## 0.2.3 (2025-01-10)

### Refactor

- :truck: rename `SPROUT_ROOT` to `SPROUT_GLOBAL` (#935)

## 0.2.2 (2024-12-18)

### Refactor

- ♻️ rename `verify_` functions to `check_` (#918)

## 0.2.1 (2024-12-18)

### Refactor

- :recycle: move `check_` tests to `checks` folder (#915)

## 0.2.0 (2024-12-16)

### Feat

- :sparkles: check properties against standard (#905)

## 0.1.1 (2024-11-21)

### Fix

- :bug: compact form of nested properties (#887)

## 0.1.0 (2024-11-13)

- Start of making the CHANGELOG for Sprout.
