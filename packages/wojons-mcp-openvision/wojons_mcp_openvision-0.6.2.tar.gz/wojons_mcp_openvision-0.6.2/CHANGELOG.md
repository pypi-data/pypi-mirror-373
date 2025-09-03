# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.6.0] - 2025-03-31

### Added

- Support for multiple MIME types

### Changed

- More informative error messages when processing image input

## [0.5.2] - 2025-03-31

### Fixed

- Auto-release workflow should now trigger the publish workflow correctly

## [0.5.1] - 2025-03-30

### Fixed

- Explanation about model usage

## [0.5.0] - 2025-03-30

### Changed

- `messages` parameter removed, we're using only the `query` parameter which will be used as a "user" role message

## [0.4.0] - 2025-03-30

### Added

- System/user message structure for OpenRouter API
- `system_prompt` parameter to control the model's role and behavior
- Enhanced documentation for the new parameters

### Changed

- Renamed `prompt` parameter to `query` for clarity

## [0.3.0] - 2025-03-30

### Added

- Support for relative images paths

### Changed

- Updated examples to demonstrate the new parameters
- Improved error messages

## [0.2.0] - 2025-03-29

### Added

- Support for multiple image input types
- Improved error handling
- Added project_root parameter for relative paths

## [0.1.0] - 2025-03-28

### Added

- Initial implementation of the MCP OpenVision server
- Basic image analysis tool
