## [v0.5.7](https://pypi.org/project/amsdal_cli/0.5.7/) - 2025-09-02

### Changed

- Allow to specify source directory

## [v0.5.6](https://pypi.org/project/amsdal_cli/0.5.6/) - 2025-08-15

### Changed

- Allow to generate migrations for plugins

## [v0.5.5](https://pypi.org/project/amsdal_cli/0.5.5/) - 2025-08-14

### Changed

- Changed the files of contrib plugin structure

## [v0.5.4](https://pypi.org/project/amsdal_cli/0.5.4/) - 2025-08-14

### Added

- Plugin commands

## [v0.5.3](https://pypi.org/project/amsdal_cli/0.5.3/) - 2025-08-01

### Changed

- Switched to use `uv` package manager

## [v0.5.2](https://pypi.org/project/amsdal_cli/0.5.2/) - 2025-07-11

### Added

- Populate config_dir in AmsdalConfig

## [v0.5.1](https://pypi.org/project/amsdal_cli/0.5.1/) - 2025-06-20

### Changed

- Adjusted migrations for new functionality

## [v0.5.0](https://pypi.org/project/amsdal_cli/0.5.0/) - 2025-05-23

### Changed

- Adjustments for the migrations improvements

## [v0.4.16](https://pypi.org/project/amsdal_cli/0.4.16/) - 2025-05-12

### Fixed

- Pin `click` version

## [v0.4.15](https://pypi.org/project/amsdal_cli/0.4.15/) - 2025-05-01

### Fixed

- Fixed import in generated tests

### Added

- Added support for date and datetime types in tests

## [v0.4.14](https://pypi.org/project/amsdal_cli/0.4.14/) - 2025-05-01

### Fixed

- Fixed for nested models in tests

## [v0.4.13](https://pypi.org/project/amsdal_cli/0.4.13/) - 2025-04-14

### Changed

- `AMSDAL_APPLICATION_UUID` is used if exist.

## [v0.4.12](https://pypi.org/project/amsdal_cli/0.4.12/) - 2025-04-09

### Added

- Ability to set the application uuid via `AMSDAL_APPLICATION_UUID` env (if not specified in .amsdal-cli).

## [v0.4.11](https://pypi.org/project/amsdal_cli/0.4.11/) - 2025-04-07

### Changed

- Quite build on most commands

## [v0.4.10](https://pypi.org/project/amsdal_cli/0.4.10/) - 2025-04-03

### Fixed

- Fix for migrations detection

## [v0.4.9](https://pypi.org/project/amsdal_cli/0.4.9/) - 2025-04-01

### Fixed

- Fix for M2M migration generation for JSON format.

## [v0.4.8](https://pypi.org/project/amsdal_cli/0.4.8/) - 2025-03-25

### Fixed

- Fix for python model generation

## [v0.4.7](https://pypi.org/project/amsdal_cli/0.4.7/) - 2025-03-24

### Added

- Added support for `integer` type as attribute
- Async hooks

### Changed

- `typer` version updated

## [v0.4.6](https://pypi.org/project/amsdal_cli/0.4.6/) - 2025-03-21

### Fixed

- Docs update and fixes

## [v0.4.5](https://pypi.org/project/amsdal_cli/0.4.5/) - 2025-03-17

### Fixed

- Fixed reset command
- Adjusted reg-conn help
- Added `integer` as supported type to the test generation

## [v0.4.4](https://pypi.org/project/amsdal_cli/0.4.4/) - 2025-03-13

### Added

- Added ability to register csv connection

## [v0.4.3](https://pypi.org/project/amsdal_cli/0.4.3/) - 2025-03-11

### Fixed

- Fixtures build fixed

## [v0.4.2](https://pypi.org/project/amsdal_cli/0.4.2/) - 2025-03-07

### Fixed

- Model and test generation fixes

## [v0.4.1](https://pypi.org/project/amsdal_cli/0.4.1/) - 2025-03-05

### Added

- Register connection command

### Fixed

- Generate async transaction in async mode

## [v0.4.0](https://pypi.org/project/amsdal_cli/0.4.0/) - 2025-02-26

### Changed

- Update `amsdal` version


## [v0.3.6](https://pypi.org/project/amsdal_cli/0.3.6/) - 2024-12-16


### Fixed

- Fixed sync-db auth error (sync-db-auth-error)

## [v0.3.5](https://pypi.org/project/amsdal_cli/0.3.5/) - 2024-12-14


### Changed

- Async build in migrations apply (async-build-in-migrations)
## [v0.3.4](https://pypi.org/project/amsdal_cli/0.3.4/) - 2024-12-10


### Added

- Run async workers (run-async-workers)
## [v0.3.3](https://pypi.org/project/amsdal_cli/0.3.3/) - 2024-12-10


### Fixed

- Init internal models (init-models)
## [v0.3.2](https://pypi.org/project/amsdal_cli/0.3.2/) - 2024-12-10


### Added

- Async support (async-support)
## [v0.3.1](https://pypi.org/project/amsdal_cli/0.3.1/) - 2024-12-02


### Fixed

- Fix fo restore command (restore-command)
## [v0.3.0](https://pypi.org/project/amsdal_cli/0.3.0/) - 2024-11-28


No significant changes.
## [v0.2.5](https://pypi.org/project/amsdal_cli/0.2.5/) - 2024-11-04


### Added

- Python3.12 support added (python3.12-support)

### Fixed

- Show correct env on deployment deletion (correct-env-on-deletion)
## [v0.2.4](https://pypi.org/project/amsdal_cli/0.2.4/) - 2024-10-28


### Added

- Added missing generated migrations check on deploy (missing-migrations-check)
## [v0.2.3](https://pypi.org/project/amsdal_cli/0.2.3/) - 2024-10-22


### Fixed

- Fix for worker models init (worker-init)
## [v0.2.2](https://pypi.org/project/amsdal_cli/0.2.2/) - 2024-10-18


### Added

- Pagination added to restore command (restore-pagination)
## [v0.2.1](https://pypi.org/project/amsdal_cli/0.2.1/) - 2024-10-18


### Changed

- Update for sync DB command (sync-db-update)
## [v0.2.0](https://pypi.org/project/amsdal_cli/0.2.0/) - 2024-10-17


### Added

- AMSDAL Glue integration (glue-integration)
## [v0.1.21](https://pypi.org/project/amsdal_cli/0.1.21/) - 2024-09-18


### Added

- Added google style docstring (docstring)
## [v0.1.20](https://pypi.org/project/amsdal_cli/0.1.20/) - 2024-09-05


### Added

- Commands to run worker (worker-commands)
## [v0.1.19](https://pypi.org/project/amsdal_cli/0.1.19/) - 2024-08-26


### Added

- Generate and run tests (tests)
## [v0.1.18](https://pypi.org/project/amsdal_cli/0.1.18/) - 2024-06-07

**Added**

- Cloud operation to delete environment (cloud-operation-to-delete-environment)
- Command to generate permission fixtures (command-to-generate-permission-fixtures)

**Changed**

- Improved output for several commands (improved-output-for-several-commands)

**Fixed**

- Command suggestions for migrations creation (command-suggestions-for-migrations-creation)



## [v0.1.17](https://pypi.org/project/amsdal_cli/0.1.17/) - 2024-05-24

**Added**

- Default .amsdal directory on new project creation (default-amsdal-directory-on-new-project-creation)


## [v0.1.16](https://pypi.org/project/amsdal_cli/0.1.16/) - 2024-05-22

**Added**

- GIT integration for environment commands (git-integration-for-environment-commands)


## [v0.1.15](https://pypi.org/project/amsdal_cli/0.1.15/) - 2024-05-17

**Changed**

- Better interaction with environments (better-interaction-with-environments)


## [v0.1.14](https://pypi.org/project/amsdal_cli/0.1.14/) - 2024-05-15

**Added**

- Support for environments (support-for-environments)


## [v0.1.13](https://pypi.org/project/amsdal_cli/0.1.13/) - 2024-05-09

**Fixed**

- Unique fields generation (unique-fields-generation)


## [v0.1.12](https://pypi.org/project/amsdal_cli/0.1.12/) - 2024-05-03

**Added**

- `clean` command (clean-command)


## [v0.1.11](https://pypi.org/project/amsdal_cli/0.1.11/) - 2024-04-25

**Added**

- Command for CI/CD manifest generation (command-for-ci-cd-manifest-generation)


## [v0.1.10](https://pypi.org/project/amsdal_cli/0.1.10/) - 2024-04-25

**Added**

- Silent deploy (silent-deploy)
- Check missing secrets and dependencies (check-missing-secrets-and-dependencies)


## [v0.1.9](https://pypi.org/project/amsdal_cli/0.1.9/) - 2024-04-12

**Changed**

- Added back migrations command and marked as deprecated (added-back-migrations-command-and-marked-as-deprecated)


## [v0.1.8](https://pypi.org/project/amsdal_cli/0.1.8/) - 2024-04-12

**Changed**

- Migration commands improvements (migration-commands-improvements)


## [v0.1.7](https://pypi.org/project/amsdal_cli/0.1.7/) - 2024-04-02

**Fixed**

- Fix: removed init all class versions (fix-removed-init-all-class-versions)


## [v0.1.6](https://pypi.org/project/amsdal_cli/0.1.6/) - 2024-04-01

**Fixed**

- Fixed migrate apply command: init all class versions (fixed-migrate-apply-command-init-all-class-versions)


## [v0.1.5](https://pypi.org/project/amsdal_cli/0.1.5/) - 2024-03-29

**Fixed**

- Fix for `serve` command (fix-for-serve-command)

## [v0.1.4](https://pypi.org/project/amsdal_cli/0.1.4/) - 2024-03-28


**Changed**

- Renamed migrations to migrate command. Improved showing info about applied migrations (renamed-migrations-to-migrate-command)
- Added zero migration (zero-migration)

**Added**

- Commands to mange Basic Auth and Allowlist (commands-to-mange-basic-auth-and-allowlist)



## [v0.1.3](https://pypi.org/project/amsdal_cli/0.1.3/) - 2024-03-25

**Changed**

- Remove migrations initialize command (remove-migrations-initialize-command)


## [v0.1.2](https://pypi.org/project/amsdal_cli/0.1.2/) - 2024-03-22

**Fixed**

- Fixtures processing (fixtures-processing)


## [v0.1.1](https://pypi.org/project/amsdal_cli/0.1.1/) - 2024-03-21

**Fixed**

- Build transactions first (build-transactions-first)


## [v0.1.0](https://pypi.org/project/amsdal_cli/0.1.0/) - 2024-03-21

**Changed** 

- Upgraded `amsdal_utils`, `amsdal_data`, `amsdal_model`, `amsdal` and `amsdal_cli` dependencies to `0.1.*` (upgraded-amsdal-utils-amsdal-data-amsdal-model-amsdal-and-amsdal-cli-dependencies)
