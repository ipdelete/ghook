# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Automatic repository cloning on issue creation via webhook
- Repository information extraction and display (full_name, owner, private status, URL)
- Configurable cloning behavior via environment variables:
  - `CLONE_REPOS` - Enable/disable auto-cloning (default: false)
  - `CLONE_BASE_DIR` - Base directory for cloned repos (default: ./repos)
  - `CLONE_UPDATE_EXISTING` - Pull updates for existing repos (default: false)
- Path sanitization to prevent directory traversal attacks
- Integration tests for repository cloning functionality
- `/verify` slash command for pulling latest changes and running tests post-review
- `/document` slash command for updating documentation and changelog

### Changed
- Enhanced console output to include repository details when issues are created
- Existing repositories are skipped during cloning with informational message
- `.gitignore` updated to exclude `repos/` and `test-repos/` directories
