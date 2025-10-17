# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- SDLC (Complete SDLC Automation) tool (`src/sdlc.py`)
  - Orchestrates complete software development lifecycle from feature planning to pull request creation
  - Executes multiple Copilot prompts in sequence: feature planning → branch creation → implementation → documentation → pull request
  - Manages context automatically between workflow stages (passes spec file and branch information)
  - Generates unique 8-character workflow IDs for tracking and audit trail
  - Creates timestamped markdown log files in `logs/<workflow-id>/logfile_<timestamp>.md` format
  - Logs all commands executed and their outputs for debugging and audit purposes
  - Graceful error handling with informative failure messages identifying which stage failed
  - Clear console output showing workflow progress and final summary
  - Integrates with GitHub Copilot CLI for all automation stages
  - Creates feature specifications, git branches, documentation updates, and pull requests automatically
- Koozie ASCII art script (`src/koozie.py`)
  - Displays "koozie" in large, colorful ASCII art format
  - Executable as standalone script or via `uv run`
  - Uses `pyfiglet` library for flexible ASCII art generation
  - Lightweight utility with no project configuration required
- ADIL (AI Developer Inner-Loop) command-line utility (`src/adil.py`)
  - Integrates GitHub Copilot CLI into development workflow
  - Automatically loads project context from `docs/prime.md`
  - Accepts task descriptions as command-line arguments
  - Combines user prompts with project context for Copilot
  - Invokes Copilot with `--allow-all-tools` flag for automation
  - Supports both direct execution (`./src/adil.py`) and uv invocation (`uv run src/adil.py`)
  - Includes error handling for missing copilot command and missing arguments
- Automated development setup script (`scripts/dev-setup.sh`) for one-command webhook testing
  - Automatically starts DevTunnel in the background
  - Launches webhook server
  - Creates GitHub webhook via `gh` CLI API
  - Configures webhook for issues events only
  - Supports multiple repository URL formats (https, ssh, shorthand)
  - Graceful cleanup on exit (Ctrl+C)
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
- README.md now prioritizes automated setup workflow
- GitHub CLI (`gh`) added as prerequisite for automated setup
