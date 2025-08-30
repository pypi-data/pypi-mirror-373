# Changelog

## [0.4.0](https://github.com/AZX-PBC/morpheus/compare/v0.3.0...v0.4.0) (2025-08-30)


### Features

* add version-aware migration tracking initialization in MigrationExecutor ([#15](https://github.com/AZX-PBC/morpheus/issues/15)) ([9eb1612](https://github.com/AZX-PBC/morpheus/commit/9eb1612f94efe1fc0bb56dd4aeb21b0917e1457e))

## [0.3.0](https://github.com/AZX-PBC/morpheus/compare/v0.2.0...v0.3.0) (2025-08-29)


### Features

* implement migration hash validation and error handling across commands ([#12](https://github.com/AZX-PBC/morpheus/issues/12)) ([663f084](https://github.com/AZX-PBC/morpheus/commit/663f08456dac8a541fc0bc6f57fb76e2b7144d21))

## [0.2.0](https://github.com/AZX-PBC/morpheus/compare/v0.1.3...v0.2.0) (2025-08-28)


### Features

* add programmatic morpheus api usage ([#10](https://github.com/AZX-PBC/morpheus/issues/10)) ([5e5e8a1](https://github.com/AZX-PBC/morpheus/commit/5e5e8a16a7b0ef740371332cee62f9905b0527de))

## [0.1.3](https://github.com/AZX-PBC/morpheus/compare/v0.1.2...v0.1.3) (2025-08-20)


### Bug Fixes

* move pytest-cov&gt;=6.2.1 to dev dependencies ([#8](https://github.com/AZX-PBC/morpheus/issues/8)) ([25a8af7](https://github.com/AZX-PBC/morpheus/commit/25a8af7dd5192178e47a8f2000f95be221b58c3d))

## [0.1.2](https://github.com/AZX-PBC/morpheus/compare/v0.1.1...v0.1.2) (2025-08-20)


### Documentation

* Update README to clarify migration directory structure and configuration syntax ([62ed798](https://github.com/AZX-PBC/morpheus/commit/62ed798e505ef9b6a6bcb2fa3a8045986c25bca4))

## [0.1.1](https://github.com/AZX-PBC/morpheus/compare/v0.1.0...v0.1.1) (2025-08-20)


### Bug Fixes

* Set release_created to true in publish job for consistent behavior ([ba118d9](https://github.com/AZX-PBC/morpheus/commit/ba118d95dd17d0e4dba4dc77289d25df0aa8b596))

## 0.1.0 (2025-08-20)


### Features

* Add .gitignore to exclude Python-generated files and virtual environments ([bb84de8](https://github.com/AZX-PBC/morpheus/commit/bb84de848ffbfe6767a230fd3d9790bfa300a0ed))
* Add backward compatibility for dependencies and implement migration description retrieval ([0d1c17d](https://github.com/AZX-PBC/morpheus/commit/0d1c17d5da81479b619d287ccdbcdf00dec81311))
* Add confirmation skip option to upgrade command ([7ced68e](https://github.com/AZX-PBC/morpheus/commit/7ced68eefbad180fde7ee37c8e52fcebd5064ac3))
* Add environment variable support for configuration loading and enhance test coverage ([5275a60](https://github.com/AZX-PBC/morpheus/commit/5275a60fd9eab9b046a41f5b5b8871d77feae1f9))
* Add id-token permission for release workflow ([5771812](https://github.com/AZX-PBC/morpheus/commit/577181226b04e2ef99d91925a54f5ddc71396ca0))
* add pytestcov ([389fc12](https://github.com/AZX-PBC/morpheus/commit/389fc12d80963a18b7ed2dc5d5c6a0a817a8541e))
* Add textual format option for DAG visualization and implement interactive viewer ([9eb129b](https://github.com/AZX-PBC/morpheus/commit/9eb129bdb90f8ffb8be11e5025d4b59366ca2d96))
* Enhance error handling and messaging for migration failures ([712a83d](https://github.com/AZX-PBC/morpheus/commit/712a83d4d7b42fb285d2400ff32b8bf01efb576e))
* Enhance init_command to support interactive directory selection ([4cbfbc1](https://github.com/AZX-PBC/morpheus/commit/4cbfbc152a4ac82f4cc9a083b35aa77984626ed8))
* Enhance Makefile with additional test targets and cleanup commands ([9a1f41b](https://github.com/AZX-PBC/morpheus/commit/9a1f41ba1e742666f164bd5c422421dda516febc))
* Enhance migration status retrieval with error handling and warning checks for missing Migration label ([b6d47df](https://github.com/AZX-PBC/morpheus/commit/b6d47df06131b7941d5f753454706ae3faf86275))
* Enhance upgrade command with CI mode for detailed status messages on migration failures ([3ceeac1](https://github.com/AZX-PBC/morpheus/commit/3ceeac1a75c891239cd674e93066831e73aabed6))
* Implement enhanced error handling for migration failures with detailed guidance ([63f3a39](https://github.com/AZX-PBC/morpheus/commit/63f3a398615a00b11ed85e2948520d7e95dfb8d0))
* Implement failfast option for upgrade command and enhance migration skipping logic ([b1a3fba](https://github.com/AZX-PBC/morpheus/commit/b1a3fba4dd6efc4e407850f0c9a559fcc29858a6))
* Implement resolve_migrations_dir utility function and update migration directory resolution in commands ([9bc3e4e](https://github.com/AZX-PBC/morpheus/commit/9bc3e4e209db6deebc2f28beb093fc357b6502e9))
* Improve migration status command with handling for uninitialized tracking and warning display ([b711efc](https://github.com/AZX-PBC/morpheus/commit/b711efc5a0ba5880ba352dd68c4972a8b12904d3))
* Integrate MigrationStatus enumeration across migration commands and update status handling ([1d65515](https://github.com/AZX-PBC/morpheus/commit/1d65515507a9eb3c83b81bdef9d28a2fb3899460))
* Introduce MigrationStatus enumeration and update MigrationExecutor to use it ([79c7579](https://github.com/AZX-PBC/morpheus/commit/79c7579dd3d78f16b6242275d5fde9c52a6a1cea))
* **migration:** Refactor migration system to support class-based migrations ([750ecf0](https://github.com/AZX-PBC/morpheus/commit/750ecf0df640c9c34e9a7bef55546e8821f1c33e))
* Refactor project structure to support morpheus-neo4j package and update related configurations ([#3](https://github.com/AZX-PBC/morpheus/issues/3)) ([5048903](https://github.com/AZX-PBC/morpheus/commit/5048903c5ec89d6f7aeee56ff0bc34e06d44f8ed))
* Rename configuration file to morpheus-config.yml and update related references ([1dc9df8](https://github.com/AZX-PBC/morpheus/commit/1dc9df80c61fad023fee1943218eaa7f7ff03d75))
* Update Config class to support environment variables in YAML configuration ([5895541](https://github.com/AZX-PBC/morpheus/commit/5895541fcca653363a9a4330fcf576fb799150b0))
* Update configuration and initialization to support environment variables in YAML ([1446002](https://github.com/AZX-PBC/morpheus/commit/14460028d8f4baeb111f3adb310b1e8431ad93f2))


### Bug Fixes

* Correct dependency direction in DAGResolver and related tests ([1edfed6](https://github.com/AZX-PBC/morpheus/commit/1edfed64f4a145b3b65899b515596574675413b8))
* Handle migration status update failure gracefully in execute_single_migration ([ce4cc15](https://github.com/AZX-PBC/morpheus/commit/ce4cc15e3ea97997f2fa52ce3ca3dd26396e1bec))


### Documentation

* Add comprehensive README documentation for Morpheus migration system ([#1](https://github.com/AZX-PBC/morpheus/issues/1)) ([7858e83](https://github.com/AZX-PBC/morpheus/commit/7858e837bccd013fb4e225e6bb7ef728990c4460))
* Add MIT License file to the repository ([aef36af](https://github.com/AZX-PBC/morpheus/commit/aef36af43e55b181655281d33873fb177ee03818))
