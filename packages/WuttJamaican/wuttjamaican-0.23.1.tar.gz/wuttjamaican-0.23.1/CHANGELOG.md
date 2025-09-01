
# Changelog
All notable changes to WuttJamaican will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## v0.23.1 (2025-08-31)

### Fix

- fix 'too-many-branches' for pylint
- fix 'attribute-defined-outside-init' for pylint
- fix 'too-many-locals' for pylint
- fix 'too-many-positional-arguments' for pylint
- fix 'too-many-arguments' for pylint
- fix 'import-outside-toplevel' for pylint
- format all code with black
- fix 'too-many-instance-attributes' for pylint
- fix 'too-many-lines' for pylint
- fix 'too-many-public-methods' for pylint
- more cleanup for pylint
- fix 'abstract-method' for pylint
- fix 'no-member' for pylint
- fix 'redefined-outer-name' for pylint
- fix 'possibly-used-before-assignment' for pylint
- fix 'no-self-argument' for pylint
- fix 'missing-module-docstring' for pylint
- fix 'missing-function-docstring' for pylint
- fix 'line-too-long' for pylint
- fix 'duplicate-code' for pylint
- fix 'consider-using-dict-comprehension' for pylint
- fix 'consider-using-set-comprehension' for pylint
- fix 'cyclic-import' for pylint
- fix 'consider-using-f-string' for pylint
- fix 'wrong-import-order' for pylint
- fix 'no-else-return' for pylint
- fix 'assignment-from-none' for pylint
- fix 'assignment-from-no-return' for pylint
- fix 'empty-docstring' for pylint
- fix 'disallowed-name' for pylint
- fix 'trailing-whitespace' for pylint
- fix 'broad-exception-caught' for pylint
- fix 'bare-except' for pylint
- fix 'too-few-public-methods' for pylint
- fix 'invalid-name' for pylint
- fix another 'unused-argument'
- fix 'unused-argument' for pylint
- fix 'anomalous-backslash-in-string' for pylint
- fix 'inconsistent-return-statements' for pylint
- fix 'redefined-argument-from-local' for pylint
- fix 'unused-import' for pylint
- fix 'unspecified-encoding' for pylint

## v0.23.0 (2025-08-10)

### Feat

- add problem checks + handler feature
- add minimal attachments support for email messages

### Fix

- fix typo
- allow caller to specify default subject for email message

## v0.22.1 (2025-08-09)

### Fix

- delay import for orm, in case SA not installed

## v0.22.0 (2025-08-09)

### Feat

- add WuttaConfigProfile base class
- add user API tokens; handler methods to manage/authenticate
- allow arbitrary kwargs for `config.get()` and `app.get_setting()`

## v0.21.1 (2025-06-29)

## v0.21.0 (2025-06-29)

### Feat

- remove version cap for SQLAlchemy (allow 1.x or 2.x)

## v0.20.6 (2025-06-29)

### Fix

- remove unused kwargs from `app.get_setting()` signature

## v0.20.5 (2025-02-19)

### Fix

- remove temp config files in startup

## v0.20.4 (2025-02-01)

### Fix

- add `make_person()` method for people, auth handlers

## v0.20.3 (2025-01-25)

### Fix

- add `make_proxy()` convenience method for data model Base

## v0.20.2 (2025-01-23)

### Fix

- return empty string instead of None when rendering date/time

## v0.20.1 (2025-01-13)

### Fix

- add `get_batch_handler()` method for app handler

## v0.20.0 (2025-01-11)

### Feat

- add basic support for "reports" feature

### Fix

- add `render_percent()` method for app handler
- set global default sender to root@localhost

## v0.19.3 (2025-01-09)

### Fix

- flush session when removing batch row
- detach row from batch when removing

## v0.19.2 (2025-01-06)

### Fix

- add `cascade_backrefs=False` for all ORM relationships
- add `get_effective_rows()` method for batch handler
- add `make_full_name()` function, app handler method
- add batch handler logic to remove row
- add `render_boolean`, `render_quantity` app handler methods
- update post-install webapp command suggestion

## v0.19.1 (2024-12-28)

### Fix

- add simple rendering logic for currency values and errors

## v0.19.0 (2024-12-23)

### Feat

- add "email settings" feature for admin, previews

### Fix

- move `email` stuff from subpackage to module
- add `is_enabled()` method for email handler, to check per type

## v0.18.1 (2024-12-18)

### Fix

- force interpolation of `%(here)s`, `%(__file__)s` in config files
- only read each config file once on startup

## v0.18.0 (2024-12-15)

### Feat

- add basic batch feature, data model and partial handler
- add basic db handler, for tracking counter values

### Fix

- add basic execution methods for batch handler
- add `render_date()`, `render_datetime()` methods for app handler
- add command for `wutta make-appdir`

## v0.17.1 (2024-12-08)

### Fix

- use proper uuid for special role getters

## v0.17.0 (2024-12-07)

### Feat

- convert all uuid fields from str to proper UUID

## v0.16.2 (2024-12-06)

### Fix

- add mechanism to discover external `wutta` subcommands

## v0.16.1 (2024-12-05)

### Fix

- add `db.util.make_topo_sortkey()` function
- use true UUID type for Upgrades table primary key
- let caller set data type for `uuid_column()` and `uuid_fk_column()`
- avoid error when loading installer templates

## v0.16.0 (2024-11-30)

### Feat

- make v7 UUID values instead of v1

## v0.15.0 (2024-11-24)

### Feat

- add `User.prevent_edit` flag for account lockdown

## v0.14.0 (2024-11-24)

### Feat

- add install handler and related logic
- add `parse_bool()` and `parse_list()` methods for config object
- add `wutta` top-level command with `make-uuid` subcommand

## v0.13.3 (2024-08-30)

### Fix

- move model base class out of model subpkg

## v0.13.2 (2024-08-27)

### Fix

- add basic support for wutta-continuum data versioning/history

## v0.13.1 (2024-08-27)

### Fix

- add common `DataTestCase` for use in other packages

## v0.13.0 (2024-08-26)

### Feat

- add basic email handler support
- add `util.resource_path()` function
- add app handler method, `get_appdir()`
- add basic support for progress indicators
- add table/model for app upgrades

## v0.12.1 (2024-08-22)

### Fix

- add app handler methods: `get_node_title()`, `get_node_type()`

## v0.12.0 (2024-08-15)

### Feat

- add util function `get_class_hierarchy()`

## v0.11.1 (2024-08-15)

### Fix

- tweak methods for `FileConfigTestCase`
- cascade deletes for User -> UserRole

## v0.11.0 (2024-08-13)

### Feat

- add dict-like behavior to model class instances

## v0.10.0 (2024-08-06)

### Feat

- add app handler methods `save_setting()`, `delete_setting()`

## v0.9.0 (2024-08-05)

### Feat

- add AppHandler methods, get_distribution() and get_version()

### Fix

- remove print statement

## v0.8.3 (2024-08-05)

### Fix

- add `AuthHandler.user_is_admin()` method
- add `AppHandler.make_title()` convenience method

## v0.8.2 (2024-07-18)

### Fix

- add `check_user_password()` method for auth handler

## v0.8.1 (2024-07-17)

### Fix

- make `AuthHandler.get_user()` do lookups for uuid, username

## v0.8.0 (2024-07-14)

### Feat

- flesh out the auth handler; add people handler
- add model for Person; tie to User

### Fix

- add migration for auth tables

## v0.7.0 (2024-07-14)

### Feat

- add basic "auth" data models: user/role/perm

### Fix

- always use 'wutta' prefix for provider entry points

## v0.6.1 (2024-07-12)

### Fix

- add `AppHandler.load_object()` method
- add `WuttaConfig.production()` method

## v0.6.0 (2024-07-11)

### Feat

- add basic data model support

## v0.5.0 (2024-07-09)

### Feat

- drop python 3.6 support

## v0.4.0 (2024-07-04)

### Feat

- remove legacy command system

### Fix

- use more explicit import in config constructor

## v0.3.2 (2024-07-04)

### Fix

- let config class specify default app handler, engine maker
- ensure config has no app when constructor finishes

## v0.3.1 (2024-06-14)

### Fix

- fallback to `importlib_metadata` when loading entry points

## v0.3.0 (2024-06-10)

### Feat

- use hatchling for package build backend

## v0.2.1 (2024-06-10)

### Fix

- use `importlib-metadata` backport for older systems

## v0.2.0 (2024-06-10)

### Feat

- replace setup.cfg with pyproject.toml

## [0.1.12] - 2024-05-28
### Changed
- Fix bug when default config paths do not exist.

## [0.1.11] - 2024-04-14
### Changed
- Fix import for `logging.config`.
- Raise `AttributeError` if no app provider has it.

## [0.1.10] - 2024-04-14
### Changed
- `WuttaConfig.get_list()` now returns `None` (instead of `[]`) by
  default if there is no config value present.

## [0.1.9] - 2023-11-30
### Changed
- Add generic handler base class, tests, docs.
- Avoid deprecation warning for ConfigParser.

## [0.1.8] - 2023-11-24
### Changed
- Add app providers, tests, docs.

## [0.1.7] - 2023-11-24
### Changed
- Add config extension class, tests, docs.

## [0.1.6] - 2023-11-22
### Changed
- Move cli framework to `wuttjamaican.cmd` subpackage.
- Add `date-organize` subcommand.

## [0.1.5] - 2023-11-22
### Changed
- Add `wutta make-appdir` subcommand.
- Add `--stdout` and `--stderr` args for base Command class.

## [0.1.4] - 2023-11-21
### Changed
- Add `Subcommand.make_arg_parser()` method.
- Allow factory override in `make_config()`.

## [0.1.3] - 2023-11-21
### Changed
- Allow specifying config object for Command constructor.
- Change entry point group naming for subcommands.

## [0.1.2] - 2023-11-20
### Changed
- Add `get_config_paths()` function, split off from `make_config()`.

## [0.1.1] - 2023-11-19
### Changed
- Add `make_engine_from_config()` method for AppHandler.

## [0.1.0] - 2023-11-19
### Added
- Initial version, with basic config and command frameworks.
