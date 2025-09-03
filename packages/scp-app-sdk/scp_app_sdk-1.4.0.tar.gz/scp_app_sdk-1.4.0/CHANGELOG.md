# Changelog

All notable changes to this project will be documented here.

## [1.4.0] - 2025-09-02
### Improved
- Split library into scp-app-lib and scp-app-sdk, keeping only the SDK in this package (SFD-102)
- Improved SDK CLI code (SFD-99)

## [1.3.0] - 2025-08-05
### Added
- Support for UI plugins.

## [1.2.1] - 2025-07-09
### Fixed
- Script could not be executed (FMG-3876).

## [1.2.0] - 2025-05-07
### Improved
- Document the route that updates app configuration (FMG-3675).

## [1.1.0] - 2025-04-18
### Added
- `env` parameter in `create` CLI command (FMG-3376).
- Ability to set app version in manifest.
- Ability to add library in the app.

### Improved
- Review source code of build rendering.
- Review manifest generation issue with CLI.
- Improve docs for non-Python developers.
- Update README with detailed app creation/configuration instructions.
- Add input parameter to `run_uninstall` function.

### Fixed
- Issue retrieving template in CLI.
- Packaging issue with templating.
- API key not sent when publishing a new app.
- Git version check.
- Uninstall script execution by adding input parameter.

## [1.0.0] - 2025-02-05
### Added
- Validation schema for apps, builds, user apps, and app manifests (Marshmallow).
- API documentation of APP store (Tornado).
- CLI to manage apps — create, validate, build, and publish.
- Library to manage APP manifest.
- Library to manage CSFE.
- Library to validate manifest, apps, and runners.
- Library to manage builds.
- Icon support.
