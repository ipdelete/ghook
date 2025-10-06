# Repository Cloning Feature Specification

## Overview

This specification describes enhancements to the GitHub webhook handler (`webhook.py`) to automatically clone repositories when issues are created. The webhook will parse repository information from the GitHub webhook payload and use the `gh` CLI to clone the repository locally.

## Goals

The primary goal is to extend the webhook handler to automatically clone the source repository when a new issue is created, enabling local inspection, analysis, or automated processing of the repository content.

## Current Behavior

Currently, when an issue is created, the webhook handler:

1. Verifies the webhook signature
2. Parses the webhook payload
3. Prints issue information to the console (title, number, author, state, URL, created_at, body)
4. Returns a success response

## Proposed Changes

### 1. Parse Repository Information

Extract and display repository information from the webhook payload, including:

- `repository.full_name` - The full repository name (e.g., "owner/repo")
- `repository.name` - The repository name only
- `repository.owner.login` - The repository owner username
- `repository.html_url` - The repository URL
- `repository.private` - Whether the repository is private
- `repository.clone_url` - The HTTPS clone URL
- `repository.ssh_url` - The SSH clone URL

### 2. Clone Repository Using `gh` CLI

After parsing the repository information, automatically clone the repository using the GitHub CLI (`gh`).

#### Implementation Details

**Clone Location:**
- Base directory: `./repos/` (relative to webhook.py location)
- Full path: `./repos/{owner}/{repo-name}/`
- Example: `./repos/octocat/Hello-World/`

**Clone Method:**
- Use `gh repo clone {full_name} {target_path}` command
- The `gh` CLI will handle authentication automatically using configured credentials
- Supports both public and private repositories (if user has access)

**Error Handling:**
- Check if `gh` CLI is installed and available
- Handle cases where the repository already exists
- Handle authentication failures
- Handle network errors
- Handle cases where user lacks access to the repository

**Clone Behavior:**
- If repository already exists: Skip cloning and log that it already exists
- If repository doesn't exist: Clone it fresh
- Optional: Add a flag or environment variable to control update behavior (pull latest changes if exists)

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
CLONE_REPOS=true                    # Enable/disable auto-cloning
CLONE_BASE_DIR=./repos              # Base directory for cloned repos
CLONE_UPDATE_EXISTING=false         # Pull updates if repo already exists
```

## Implementation Steps

### Step 1: Extract Repository Information
Modify the `github_webhook` function to extract repository details from the payload:

```python
repository = payload.get("repository", {})
repo_full_name = repository.get("full_name")
repo_name = repository.get("name")
repo_owner = repository.get("owner", {}).get("login")
repo_url = repository.get("html_url")
is_private = repository.get("private", False)
```

### Step 2: Create Clone Function
Add a new function to handle repository cloning:

```python
import subprocess
from pathlib import Path

def clone_repository(full_name: str, base_dir: str = "./repos") -> dict:
    """Clone a GitHub repository using gh CLI.
    
    Args:
        full_name: Repository full name (owner/repo)
        base_dir: Base directory for cloning repositories
        
    Returns:
        dict with status, message, and path
    """
    # Implementation details here
    pass
```

### Step 3: Check for `gh` CLI
Verify that `gh` CLI is installed:

```python
def check_gh_cli_available() -> bool:
    """Check if gh CLI is installed and authenticated."""
    try:
        result = subprocess.run(
            ["gh", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False
```

### Step 4: Integrate Cloning into Webhook Handler
Call the clone function within the issue creation handler and display results.

## Security Considerations

1. **Authentication**: The `gh` CLI must be properly authenticated before the webhook server starts. The server should check for valid authentication on startup.

2. **Path Traversal**: Validate repository names to prevent path traversal attacks. The owner and repo names should be sanitized.

3. **Disk Space**: Cloning repositories can consume significant disk space. Consider implementing:
   - Maximum number of cloned repositories
   - Automatic cleanup of old repositories
   - Shallow clones to reduce storage requirements

4. **Rate Limiting**: Be aware of GitHub API rate limits when cloning multiple repositories.

5. **Private Repositories**: Ensure that the authenticated user has access to private repositories before attempting to clone.

## Testing Plan

1. **Unit Tests**:
   - Test repository information extraction from webhook payload
   - Test clone function with mocked subprocess calls
   - Test path construction and validation

2. **Integration Tests**:
   - Test with a real webhook payload for a public repository
   - Test with a private repository
   - Test behavior when repository already exists
   - Test error handling when `gh` CLI is not available

3. **Manual Testing**:
   - Configure webhook on a test repository
   - Create an issue and verify automatic cloning
   - Create another issue and verify handling of existing repository
   - Test with both public and private repositories

## Future Enhancements

1. **Selective Cloning**: Add webhook payload inspection to conditionally clone based on issue labels, title patterns, or other criteria

2. **Shallow Clones**: Use `--depth 1` for shallow clones to save space

3. **Repository Management**: Add endpoints to list, update, or delete cloned repositories

4. **Webhook Actions**: Trigger additional automated actions after cloning (linting, testing, analysis)

5. **Multi-event Support**: Extend to handle other webhook events (pull requests, commits, releases)

6. **Database Tracking**: Track cloned repositories in a database with metadata (clone time, last update, issue association)

## Dependencies

- `gh` CLI must be installed on the system
- User must be authenticated with `gh auth login`
- Python `subprocess` module (built-in)
- Python `pathlib` module (built-in)

## Backward Compatibility

All changes are additive and optional. The webhook will continue to function as before if:
- `CLONE_REPOS` is set to `false` or not set
- `gh` CLI is not available (with appropriate warnings)

Existing functionality (printing issue information) will be preserved.
