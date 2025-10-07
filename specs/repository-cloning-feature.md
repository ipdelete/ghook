# Feature: Repository Cloning on Issue Creation

## Feature Description
Automatically clone GitHub repositories when issues are created via webhook. When an issue is opened, the webhook handler will parse the repository information from the payload and clone the repository locally using the `gh` CLI. This enables local inspection, analysis, or automated processing of repository content triggered by issue creation.

## User Story
As a webhook server operator  
I want repositories to be automatically cloned when issues are created  
So that I can perform local analysis, inspection, or automated processing on the repository content

## Problem Statement
Currently, the webhook handler only logs issue information to the console but doesn't provide access to the repository content. To perform automated analysis, code inspection, or other operations on the repository, users must manually clone repositories after seeing issue notifications. This manual step is inefficient and prevents automation of repository-based workflows.

## Solution Statement
Extend the webhook handler to automatically clone repositories using the GitHub CLI (`gh`) when issue webhooks are received. The implementation will extract repository metadata from the webhook payload, validate the clone target path, and execute the clone operation using `gh repo clone`. The feature will be configurable via environment variables and include robust error handling for common failure scenarios like missing `gh` CLI, existing repositories, and authentication issues.

## Current Behavior

When an issue is created, the webhook handler:

1. Verifies the webhook signature using HMAC SHA-256
2. Parses the webhook payload
3. Prints issue information to the console (title, number, author, state, URL, created_at, body)
4. Returns a success response

## Proposed Changes

### 1. Parse Repository Information

Extract and display repository information from the webhook payload:

- `repository.full_name` - The full repository name (e.g., "owner/repo")
- `repository.name` - The repository name only
- `repository.owner.login` - The repository owner username
- `repository.html_url` - The repository URL
- `repository.private` - Whether the repository is private

### 2. Clone Repository Using `gh` CLI

After parsing the repository information, automatically clone the repository using the GitHub CLI.

**Clone Location:**
- Base directory: `./repos/` (relative to webhook.py location, configurable via environment variable)
- Full path: `./repos/{owner}/{repo-name}/`
- Example: `./repos/octocat/Hello-World/`

**Clone Method:**
- Use `gh repo clone {full_name} {target_path}` command
- The `gh` CLI handles authentication automatically using configured credentials
- Supports both public and private repositories (if user has access)

**Error Handling:**
- Check if `gh` CLI is installed and available
- Handle cases where the repository already exists (skip with informational message)
- Handle authentication failures (log error, continue webhook processing)
- Handle network errors (log error, continue webhook processing)
- Handle cases where user lacks access to the repository

**Clone Behavior:**
- If repository already exists: Skip cloning and log that it already exists
- If repository doesn't exist: Clone it fresh
- Environment variable controls whether to pull updates for existing repos

### 3. Enhanced Console Output

Update the console output to include repository information and clone status:

```
============================================================
🎉 NEW ISSUE CREATED!
============================================================
Repository:  octocat/Hello-World
Owner:       octocat
Private:     False
Repo URL:    https://github.com/octocat/Hello-World

Issue Details:
Title:       Found a bug
Number:      #1
Author:      octocat
State:       open
URL:         https://github.com/octocat/Hello-World/issues/1
Created at:  2024-01-01T00:00:00Z

Body:
I'm having a problem with this.

Repository Clone:
✅ Cloned successfully to: ./repos/octocat/Hello-World
============================================================
```

### 4. Configuration

Add optional environment variables to `.env`:

```bash
# Clone behavior
CLONE_REPOS=true                    # Enable/disable auto-cloning (default: false)
CLONE_BASE_DIR=./repos              # Base directory for cloned repos (default: ./repos)
CLONE_UPDATE_EXISTING=false         # Pull updates if repo already exists (default: false)
```

## Security Considerations

1. **Authentication**: The `gh` CLI must be properly authenticated before the webhook server starts. Add a startup check for valid authentication.

2. **Path Traversal**: Validate repository names to prevent path traversal attacks. Sanitize owner and repo names to ensure they don't contain `..`, `/`, or other dangerous characters.

3. **Disk Space**: Cloning repositories can consume significant disk space. Consider implementing:
   - Shallow clones to reduce storage requirements
   - Cleanup of old repositories based on age or count limits
   - Disk space checks before cloning

4. **Private Repositories**: Ensure the authenticated user has access to private repositories before attempting to clone.

## Relevant Files

### Existing Files

- **`src/webhook.py`** - Main webhook handler that needs to be enhanced with repository cloning functionality
- **`tests/test_webhook_integration.py`** - Integration tests that validate webhook behavior; needs new tests for cloning feature
- **`tests/conftest.py`** - Shared pytest fixtures including `webhook_server`, `generate_signature`, and `create_issue_payload`; needs enhancement to support repository field assertions
- **`.env.sample`** - Sample environment configuration that needs new clone-related variables
- **`.gitignore`** - Needs to ignore the `repos/` directory where cloned repositories are stored

### New Files

None required - all changes are additions to existing files.

## Testing Strategy

### Integration Testing Philosophy

Following the project's testing philosophy, we use **integration tests with real repositories** instead of mocks or unit tests. Tests start an actual webhook server as a subprocess and send real HTTP requests. For cloning functionality, tests will use a small real GitHub repository.

### Test Repository Selection

Use `octocat/Hello-World` as the test repository because it is:
- Small (~2KB) - minimal impact on test execution time and disk space
- Public - no authentication required for basic clone tests
- Stable - maintained by GitHub and unlikely to disappear
- Well-known - standard test repository used across GitHub documentation

### Integration Tests

**Test Cases:**

1. **Test successful repository cloning**
   - Send webhook with `octocat/Hello-World` repository
   - Verify server returns 200 status
   - Verify repository is cloned to `./test-repos/octocat/Hello-World/`
   - Verify `.git` directory exists in cloned repository
   - Cleanup: Remove cloned repository after test

2. **Test handling of existing repository**
   - Pre-create the repository directory before sending webhook
   - Send webhook with same repository
   - Verify server returns 200 status
   - Verify response indicates repository already exists (not re-cloned)
   - Verify no error occurs
   - Cleanup: Remove repository after test

3. **Test cloning disabled via environment variable**
   - Set `CLONE_REPOS=false` in test environment
   - Send webhook payload
   - Verify server returns 200 status
   - Verify no clone attempt is made (directory not created)
   
4. **Test handling when gh CLI is not available**
   - Mock PATH to exclude `gh` binary location
   - Send webhook payload
   - Verify server returns 200 status (webhook still processes)
   - Verify appropriate error message in response
   - Verify no clone directory created

5. **Test repository information extraction**
   - Send webhook with comprehensive repository payload
   - Verify all repository fields are correctly extracted and logged
   - Verify response includes repository metadata

6. **Test path sanitization**
   - Send webhook payload with malicious repository name (e.g., `../../../etc/passwd`)
   - Verify path traversal is prevented
   - Verify error response is returned

### Test Fixtures

Enhance `tests/conftest.py` with:

- **`test_clone_dir`** - Fixture that creates a temporary clone directory for tests and cleans it up afterward
- **Enhanced `create_issue_payload`** - Include full repository object with all necessary fields (full_name, owner, html_url, private, etc.)
- **`gh_cli_available`** - Fixture that checks if `gh` CLI is available and skips tests if not (or mocks unavailability)

### Edge Cases

- Repository name contains spaces or special characters
- Repository is private but user is not authenticated
- Network connection fails during clone
- Insufficient disk space for clone operation
- Multiple webhooks received simultaneously for same repository
- Repository name exceeds filesystem path length limits
- `gh` CLI installed but not authenticated

## Acceptance Criteria

1. ✅ When an issue webhook is received with `CLONE_REPOS=true`, the repository is cloned to `{CLONE_BASE_DIR}/{owner}/{repo-name}/`
2. ✅ Repository information (full_name, owner, private status, URL) is extracted from payload and logged
3. ✅ If repository already exists, cloning is skipped with informational message
4. ✅ If `gh` CLI is not available, webhook processing continues with error logged
5. ✅ If `CLONE_REPOS=false` or unset, no cloning is attempted
6. ✅ Path traversal attempts in repository names are prevented with validation
7. ✅ Integration tests use real repository (`octocat/Hello-World`) and verify actual cloning
8. ✅ All integration tests pass without errors
9. ✅ Existing webhook functionality (signature verification, issue logging) remains unchanged
10. ✅ `.env.sample` is updated with new configuration variables and documentation

## Implementation Notes

- Use Python's `subprocess` module (built-in) for executing `gh` CLI commands
- Use `pathlib.Path` (built-in) for safe path handling and validation
- Implement clone operation asynchronously or with timeout to prevent blocking webhook responses
- Log all clone operations (success, failure, skip) for debugging and monitoring
- Ensure repository directory structure (`repos/{owner}/{repo}/`) is created before cloning
- Add startup validation to check `gh` CLI availability and authentication status

## Dependencies

- `gh` CLI must be installed on the system (runtime requirement, not Python dependency)
- User must be authenticated with `gh auth login` (runtime requirement)
- Python `subprocess` module (built-in)
- Python `pathlib` module (built-in)

## Backward Compatibility

All changes are additive and optional. The webhook will continue to function as before if:
- `CLONE_REPOS` is set to `false` or not set (default behavior)
- `gh` CLI is not available (with appropriate warnings logged)

Existing functionality (signature verification, issue logging) is preserved without changes.
