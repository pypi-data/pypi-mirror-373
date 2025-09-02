# History

0.3.9 (2025-09-01)
------------------

- Make threedimodel valid timeout wait for pickup of make_gridadmin task thereby 
  honoring potential processing queue delays 


0.3.8 (2025-04-30)
------------------

- Check if latest revision is valid


0.3.7 (2025-04-17)
------------------

- Sqlite to Geopackage conversion in create revision


0.3.6 (2025-04-17)
------------------

- Validate threedimodel generation tasks to exit on task failures.
- Decrease timeout for threedimodel generation and simulation to 10 minutes. 


0.3.5 (2025-03-25)
------------------

- Added support for lizard postprocessing


0.3.4 (2025-03-13)
------------------

- Prioritize geopackage over sqlite for model DB.


0.3.3 (2025-03-04)
------------------

- Fix bug where name resolver for bulkfiles would crash on multiple files.


0.3.2 (2025-02-26)
------------------

- Upgrade threedi-schema version and update DB interface for vegetation.


0.3.1 (2025-01-31)
------------------

- Substances can also added through bulk lateral file


0.3.0 (2025-01-14)
------------------

- Add posibility to add substances to a simulation scenario and scenario events


0.2.2 (2025-01-08)
------------------

- Fix filelateral upload bug


0.2.1 (2024-12-19)
------------------

- Bump websockets to 14.1 and let threedi-schema be greater than 0.227


0.2 (2024-12-19)
----------------

- Derive scenario names from openapi specification


0.1 (2024-12-11)
----------------

- Set environment parameter for lizard resources
- Implement backoff for simulation queue full 429 response
- Add linting github action


0.0.30 (2024-10-24)
-------------------

- Add organisation parameter to process call


0.0.29 (2024-10-24)
-------------------

- Fix incorrect merge


0.0.28 (2024-10-23)
-------------------

- Expose `use_rich_logging` as a setting


0.0.27 (2024-09-05)
-------------------

- Wait for completion of simulation template task


0.0.26 (2024-08-16)
-------------------

- Pin threedi-schema between 0.217 and 0.221


0.0.25 (2024-08-15)
-------------------

- updated github action python version to 3.10


0.0.24 (2024-08-15)
-------------------

- Add constanntlateral, filelateral, localrainconstant,
   localraintimeseries, and raintimeserieslizard to yaml converter.


0.0.23 (2024-04-12)
-------------------

- Add threedi-schema dependency to setup.py


0.0.22 (2024-04-12)
-------------------

- Added threedi-schema as a dependency.


0.0.21 (2024-04-11)
-------------------

- Added support for automatic schematisation upload.

- Refactored websocket settings.

- Support Lizard results postprocessing


0.0.20 (2022-10-10)
-------------------

- Use threedimodel_id instead of threedimodel on Simulation resource.


0.0.19 (2022-10-10)
-------------------

- Pop threedimodel from simulation template create request.


0.0.18 (2022-10-10)
-------------------

- Upgraded scenario runner to use simulation templates.


0.0.17 (2022-08-10)
-------------------

- Made bumping arrow (dependency) possible.

- Increase timeout for leakge/rain/sources_sinks file upload 'processed' event.


0.0.16 (2022-02-08)
-------------------

- Replaced PyPi token


0.0.15 (2022-02-08)
-------------------

- Bugfix: Don't set `None`` values on threedi-api-client OpenAPI models.


0.0.14 (2021-08-11)
-------------------

- Bugfix in groundwater initial waterlevel scenario handling.

- File structure  control scenario support


0.0.13 (2021-08-03)
-------------------

- Upgraded from `openapi_client` to `threed_api_client`


0.0.12 (2021-08-02)
-------------------

- Added support for schematisations scenarios


0.0.11 (2021-06-15)
-------------------

- Changed import paths


0.0.10 (2021-06-15)
-------------------

- Removed unused imports


0.0.9 (2021-05-05)
------------------

- Renamed general settings to physical settings


0.0.8 (2021-04-28)
------------------

- Use auth refresh method from upstream package.


0.0.7 (2021-04-14)
------------------

- Added settings to scenario-test-framework


0.0.6 (2021-03-24)
------------------

- Added leakage and bumped threedi-openapi-client


0.0.5 (2021-02-05)
------------------

- Specify arrow version, as newer versions don't work well with 'days' directive in
  YAML (arrow is used in jinja2-time).

- Caches the config per endpoint. This includes a scenario folder option to supply
  a custom scenario folder location (per endpoint).


0.0.4 (2021-02-04)
------------------

- Fixed saving 'organisation_uuid' and 'result_folder' with the `api settings`
  command.

- First official release candidate as a typer app that introduces a plugin system.



0.0.3 (2020-12-21)

- Fixed settings context if config file is not yet available.


## 0.0.1b (2020-12-18)

- First (beta) pypi release.
