# Feature: Dev Setup Script

## Metadata
issue_number: N/A
adw_id: N/A
issue_json: Manual feature request

## Feature Description
Create a comprehensive development setup script (`dev-setup.sh`) that automates the complete workflow for setting up a GitHub webhook development environment. The script will orchestrate starting the DevTunnel, launching the webhook server, and automatically configuring a GitHub repository webhook to point to the DevTunnel URL. This eliminates manual configuration steps and provides developers with a one-command solution to start testing webhooks locally.

## User Story
As a developer
I want to quickly set up and test GitHub webhooks locally with a single command
So that I can efficiently develop and debug webhook integrations without manual configuration steps

## Problem Statement
Currently, developers must manually execute multiple steps to set up a webhook testing environment:
1. Start the DevTunnel using `scripts/start-devtunnel.sh`
2. Copy the DevTunnel URL from the output
3. Start the webhook server with `uv run src/webhook.py`
4. Navigate to GitHub repository settings in a browser
5. Manually configure the webhook with the DevTunnel URL, secret, and event types

This multi-step process is error-prone, time-consuming, and requires context-switching between terminal and browser. It creates friction for developers who want to quickly test webhook functionality.

## Solution Statement
Create a unified `scripts/dev-setup.sh` script that accepts a GitHub repository URL as an argument and automatically:
- Validates prerequisites (`.env` file, webhook secret, `gh` CLI authentication)
- Starts DevTunnel in the background
- Extracts the DevTunnel URL from the output
- Creates a GitHub webhook via the `gh` API pointing to the DevTunnel
- Configures the webhook to trigger only on issue events
- Starts the webhook server
- Provides clear status updates and handles cleanup on exit

The script will provide a single-command developer experience: `./scripts/dev-setup.sh https://github.com/owner/repo`

## Relevant Files
Use these files to implement the feature:

- **`scripts/start-devtunnel.sh`** - Existing DevTunnel setup script that needs to be invoked as a subprocess; provides the DevTunnel URL that must be captured
- **`src/webhook.py`** - Existing webhook server that needs to be started; runs on port 8080 by default
- **`.env.sample`** - Template for environment variables including `GITHUB_WEBHOOK_SECRET` which is required for webhook verification
- **`README.md`** - Project documentation that should be updated with usage instructions for the new script
- **`.github/github-instructions.md`** - Developer documentation that should be updated with the new simplified workflow

### New Files
- **`scripts/dev-setup.sh`** - New unified development setup script that orchestrates the entire workflow

## Implementation Plan

### Phase 1: Foundation
Create the basic script structure with argument parsing, validation checks, and helper functions. Implement prerequisite validation to ensure the environment is properly configured before attempting to start services. This includes checking for the `.env` file, validating the webhook secret is set, and verifying `gh` CLI is installed and authenticated.

### Phase 2: Core Implementation
Implement the orchestration logic to start DevTunnel and webhook server as background processes. Add logic to capture and parse the DevTunnel URL from the DevTunnel output. Implement GitHub API integration using `gh` CLI to automatically create webhooks with proper configuration (URL, secret, events). Add proper process management and cleanup handlers.

### Phase 3: Integration
Add comprehensive error handling, status reporting, and user feedback throughout the process. Implement graceful shutdown that cleans up both background processes. Update project documentation to reflect the new simplified workflow. Test the script end-to-end with real GitHub repositories.

## Step by Step Tasks

### Task 1: Create script file structure and validation logic
- Create `scripts/dev-setup.sh` with proper bash shebang and error handling (`set -e`)
- Add color codes for terminal output (matching style from `start-devtunnel.sh`)
- Implement argument parsing to accept repository URL (required)
- Add validation for repository URL format (support `https://github.com/owner/repo`, `git@github.com:owner/repo.git`, and `owner/repo`)
- Extract owner and repo name from the URL using regex
- Implement `.env` file existence check and creation from `.env.sample` if missing
- Add validation that `GITHUB_WEBHOOK_SECRET` is set and not the default placeholder value

### Task 2: Add prerequisite checks
- Check if `gh` CLI is installed (`command -v gh`)
- Verify `gh` CLI is authenticated (`gh auth status`)
- Display clear error messages with remediation steps if prerequisites are missing
- Add success indicators when all prerequisites are met

### Task 3: Implement DevTunnel orchestration
- Start `scripts/start-devtunnel.sh` as a background process
- Redirect output to a temporary log file for URL extraction
- Store the process ID for cleanup
- Implement polling logic to wait for DevTunnel to initialize (with timeout)
- Parse the DevTunnel HTTPS URL from the log output using grep/regex
- Validate that a URL was successfully extracted
- Display the extracted DevTunnel URL to the user

### Task 4: Implement GitHub webhook creation
- Construct the webhook URL by appending `/webhook` to the DevTunnel URL
- Use `gh api` to check if a webhook already exists for this URL
- If webhook doesn't exist, create it via `gh api POST repos/{owner}/{repo}/hooks` with:
  - `config.url` set to the webhook URL
  - `config.content_type` set to `json`
  - `config.secret` set to `$GITHUB_WEBHOOK_SECRET`
  - `events` set to `['issues']` only
  - `active` set to `true`
- Handle API errors gracefully with informative messages
- Display success confirmation with webhook details

### Task 5: Start webhook server
- Change to project root directory
- Start webhook server with `uv run src/webhook.py` as background process
- Store the process ID for cleanup
- Add a brief sleep to allow server to initialize
- Display confirmation that server is running

### Task 6: Add cleanup and signal handling
- Implement `cleanup()` function that:
  - Kills the webhook server process
  - Kills the DevTunnel process
  - Removes temporary log files
  - Displays cleanup confirmation
- Register cleanup function with `trap cleanup SIGINT SIGTERM EXIT`
- Add wait loop to keep script running until interrupted
- Ensure both processes are properly terminated on exit

### Task 7: Add user feedback and final touches
- Add clear section headers and visual separators
- Display a summary of what's running (repository, webhook URL, events)
- Add instructions for testing (create an issue)
- Add reminder about how to stop (Ctrl+C)
- Make the script executable (`chmod +x scripts/dev-setup.sh`)
- Add comments explaining key sections of the script

### Task 8: Update documentation
- Update `README.md` to add a "Quick Start" section mentioning the new script
- Update `.github/github-instructions.md` development workflow section to reference the script
- Add usage examples showing the different URL formats supported
- Document what the script does and what prerequisites are needed

### Task 9: Manual testing
- Test the script with a real GitHub repository URL
- Verify DevTunnel starts correctly and URL is captured
- Verify webhook is created in GitHub with correct configuration
- Verify webhook server starts and receives events
- Test creating an issue to confirm webhook triggers
- Test Ctrl+C cleanup to ensure both processes terminate
- Test error conditions (missing .env, not authenticated, invalid URL)
- Test with different URL formats (https, git@, owner/repo)

### Task 10: Run validation commands
Execute all validation commands to ensure the feature works correctly with zero regressions.

## Testing Strategy

### Unit Tests
No unit tests required - this is a bash script that orchestrates existing tools. Manual testing is sufficient given the operational nature of the script.

### Edge Cases
- Repository URL in various formats (https, ssh, shorthand)
- Missing or invalid `.env` file
- Webhook secret not configured or using default value
- `gh` CLI not installed
- `gh` CLI not authenticated
- Webhook already exists for the repository
- DevTunnel fails to start or URL cannot be extracted
- Webhook creation API fails (permissions, rate limits)
- Port 8080 already in use
- Interrupted startup (Ctrl+C during initialization)
- Multiple script instances running simultaneously

## Acceptance Criteria
1. Script accepts a GitHub repository URL as the first argument
2. Script validates all prerequisites before starting services
3. Script successfully starts DevTunnel in the background
4. Script extracts and displays the DevTunnel URL
5. Script creates a GitHub webhook pointing to the DevTunnel URL with issues events only
6. Script starts the webhook server successfully
7. Script displays clear status messages throughout the process
8. Script handles errors gracefully with helpful error messages
9. Script properly cleans up background processes when interrupted with Ctrl+C
10. Documentation is updated to reflect the new workflow
11. Script can be run multiple times without creating duplicate webhooks
12. Created webhook successfully receives issue events from GitHub

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `chmod +x scripts/dev-setup.sh` - Make the script executable
- `bash -n scripts/dev-setup.sh` - Check bash syntax is valid
- `shellcheck scripts/dev-setup.sh || true` - Run shellcheck if available (optional)
- `cat scripts/dev-setup.sh | head -20` - Verify script header and structure
- Manual test: `./scripts/dev-setup.sh https://github.com/owner/test-repo` - Test with a real repository
- Manual test: Create an issue in the configured repository and verify webhook is triggered
- Manual test: Press Ctrl+C and verify both processes terminate cleanly
- Manual test: Run script again with same repo and verify it handles existing webhook
- `git diff README.md` - Verify documentation updates
- `git diff .github/github-instructions.md` - Verify developer documentation updates

## Notes
- The script should NOT require tests since it's a bash orchestration script for local development
- Consider adding a `--help` flag in future iterations for better discoverability
- Future enhancement: Add `--events` flag to allow customizing which events trigger the webhook
- Future enhancement: Add `--port` flag to customize webhook server port
- Future enhancement: Add `--no-webhook` flag to skip webhook creation (just start services)
- The script assumes DevTunnel output format remains stable; may need updates if DevTunnel CLI changes
- Consider adding a `--cleanup` flag to delete the webhook when done testing
- The temporary log file location `/tmp/devtunnel-output.log` works on Linux/macOS but may need adjustment for other platforms
