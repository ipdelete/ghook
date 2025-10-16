# GitHub Instructions

This document provides guidance for contributors and maintainers working with this GitHub webhook testing repository.

## About This Project

This repository contains a lightweight GitHub webhook server designed for local development and testing. It uses Microsoft DevTunnel to expose your local webhook endpoint to GitHub, allowing you to test webhook integrations without deploying to a remote server.

## Setting Up Webhooks

### Creating a Webhook Secret

Generate a secure webhook secret using OpenSSL:

```bash
openssl rand -hex 32
```

Store this secret in your `.env` file and use the same value when configuring the webhook in your GitHub repository settings.

### Configuring Repository Webhooks

To test this webhook server with a GitHub repository:

1. Navigate to your repository's Settings → Webhooks → Add webhook
2. Set the Payload URL to your DevTunnel URL with the `/webhook` path (e.g., `https://xxxxx.devtunnels.ms/webhook`)
3. Choose `application/json` as the content type
4. Enter your webhook secret (must match the value in your `.env` file)
5. Select which events should trigger the webhook (currently configured for Issues)
6. Ensure "Active" is checked and save the webhook

### Supported Events

Currently, the webhook server is configured to handle:

- **Issues**: Specifically the `opened` action, which displays detailed issue information in the console and optionally clones the repository

You can extend the webhook handler in `webhook.py` to support additional events such as pull requests, pushes, releases, and more.

## Repository Cloning on Issue Creation

The webhook server can automatically clone repositories when issues are opened, enabling automated analysis and processing of repository content.

### Configuration

Enable repository cloning by setting environment variables in your `.env` file:

```bash
# Clone repositories when issues are opened
CLONE_REPOS=true                    # Enable/disable auto-cloning (default: false)

# Base directory for cloned repositories
CLONE_BASE_DIR=./repos              # Default: ./repos (relative to webhook.py)

# Update existing repositories
CLONE_UPDATE_EXISTING=false         # Pull updates if repo exists (default: false)
```

### Prerequisites for Cloning

Repository cloning requires the GitHub CLI (`gh`) to be installed and authenticated:

1. **Install GitHub CLI**
   - macOS: `brew install gh`
   - Linux: See [GitHub CLI installation guide](https://github.com/cli/cli#installation)
   - Windows: `winget install --id GitHub.cli`

2. **Authenticate with GitHub**
   ```bash
   gh auth login
   ```
   Follow the prompts to authenticate with your GitHub account.

3. **Verify authentication**
   ```bash
   gh auth status
   ```

### How It Works

When an issue webhook is received with `CLONE_REPOS=true`:

1. Repository information is extracted from the webhook payload (full_name, owner, private status, URL)
2. A sanitized target path is created: `{CLONE_BASE_DIR}/{owner}/{repo-name}/`
3. The repository is cloned using `gh repo clone {full_name} {target_path}`
4. If the repository already exists:
   - By default, cloning is skipped with an informational message
   - If `CLONE_UPDATE_EXISTING=true`, a `git pull` is performed to update the repository
5. Clone status is displayed in the console output

### Security

**Path Sanitization:** Repository names are validated to prevent directory traversal attacks. Any repository name containing `..`, absolute paths, or other dangerous characters will be rejected.

**Authentication:** The `gh` CLI uses your authenticated GitHub account, so you can only clone repositories you have access to (both public and private repositories).

**Disk Space:** Cloned repositories are stored locally and can consume significant disk space. Monitor your `CLONE_BASE_DIR` and clean up old repositories as needed.

## Development Workflow

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Microsoft DevTunnel CLI (for exposing local endpoints)
- GitHub CLI (`gh`) - for automated webhook setup

### Local Testing

#### Automated Setup (Recommended)

The easiest way to start testing webhooks is using the automated setup script:

1. Copy the environment template and configure your secret:
   ```bash
   cp .env.sample .env
   # Edit .env and add your GITHUB_WEBHOOK_SECRET (use: openssl rand -hex 32)
   ```

2. Ensure GitHub CLI is authenticated:
   ```bash
   gh auth login
   ```

3. Run the setup script with your repository:
   ```bash
   ./scripts/dev-setup.sh https://github.com/owner/repo
   ```
   
   This single command will:
   - Start DevTunnel automatically
   - Launch the webhook server
   - Create a GitHub webhook for your repository (configured for issues events only)
   - Display real-time webhook events in the console
   
   Press Ctrl+C to stop both services when done.

4. Test by creating an issue in your repository and watch the console output

#### Manual Setup

If you prefer to run each component separately:

1. Copy the environment template and configure your secret:
   ```bash
   cp .env.sample .env
   # Edit .env and add your GITHUB_WEBHOOK_SECRET
   ```

2. Start the DevTunnel in one terminal:
   ```bash
   ./scripts/start-devtunnel.sh
   ```

3. Start the webhook server in another terminal:
   ```bash
   uv run src/webhook.py
   ```

4. Configure your GitHub webhook using the DevTunnel URL from step 2

5. Test by creating an issue in your repository and watch the console output

## Testing

### Running Tests

This repository includes comprehensive integration tests for the webhook server. The tests start an actual webhook server as a subprocess and send real HTTP requests to validate behavior.

Run all tests:
```bash
uv run pytest
```

Run tests with verbose output:
```bash
uv run pytest -v
```

Run tests with detailed output:
```bash
uv run pytest -vv
```

Run a specific test file:
```bash
uv run pytest tests/test_webhook_integration.py -v
```

Run a specific test:
```bash
uv run pytest tests/test_webhook_integration.py::test_valid_webhook_with_correct_signature -v
```

### Test Coverage

The integration test suite covers:

- **Valid webhook requests**: Verifies that properly signed webhook requests are accepted and processed correctly
- **Signature verification**: Tests that invalid or missing signatures are properly rejected with 401 status
- **Event handling**: Validates different GitHub event types (issues, pull requests, etc.) are handled appropriately
- **Error handling**: Tests malformed JSON payloads and edge cases return proper error responses
- **Server lifecycle**: Ensures the webhook server starts, responds to requests, and shuts down cleanly
- **Repository cloning**: Tests automatic cloning with real repositories (`octocat/Hello-World`)
- **Path sanitization**: Validates protection against directory traversal attacks
- **Feature toggles**: Tests that cloning can be enabled/disabled via environment variables

### Test Environment

The tests run completely offline and do not require:
- A real GitHub account or repository (except for optional clone tests which use `octocat/Hello-World`)
- External network access (except for optional clone tests)
- Production credentials or secrets

All tests use:
- Mock webhook payloads with realistic data structures
- Test secrets generated specifically for the test suite
- A dedicated test server running on port 18080 (to avoid conflicts)
- Automatic server startup and cleanup via pytest fixtures

### Test Fixtures

The test suite provides reusable fixtures in `tests/conftest.py`:

- **`webhook_server`**: Starts a webhook server subprocess with test configuration and cleans it up after tests
- **`generate_signature(payload, secret)`**: Creates valid HMAC SHA-256 signatures for webhook payloads
- **`create_issue_payload(**kwargs)`**: Generates realistic GitHub issue webhook payloads with customizable fields, including full repository information
- **`test_clone_dir`**: Creates and manages temporary directories for repository cloning tests

## Security Considerations

### Webhook Signature Verification

This server implements GitHub's recommended HMAC SHA-256 signature verification to ensure webhook payloads are authentic. Every incoming webhook request is validated against the shared secret before processing.

**Never** commit your webhook secret to version control. Always use environment variables and keep your `.env` file in `.gitignore`.

### Best Practices

- Rotate your webhook secrets periodically
- Use strong, randomly generated secrets (at least 32 bytes)
- Validate all webhook payloads before processing
- Log security-related events for audit purposes
- Use HTTPS endpoints in production (DevTunnel provides this automatically)

## Contributing

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for function signatures
- Include docstrings for functions and classes
- Keep code modular and well-documented

### Adding New Event Handlers

To handle additional GitHub events:

1. Add a new conditional block in the `github_webhook` function in `webhook.py`
2. Check for the specific event type and action
3. Extract relevant data from the payload
4. Implement your handler logic
5. Return an appropriate response

Example:
```python
if event_type == "pull_request" and payload.get("action") == "opened":
    pr = payload.get("pull_request", {})
    # Handle pull request opened event
    return {"status": "success", "message": "PR processed"}
```

## Troubleshooting

### Webhook Not Receiving Events

- Verify DevTunnel is running and accessible
- Check that the webhook URL in GitHub settings is correct
- Ensure the webhook secret matches between `.env` and GitHub configuration
- Review GitHub's webhook delivery logs in repository settings

### Signature Verification Failures

- Confirm the `GITHUB_WEBHOOK_SECRET` in `.env` matches the secret configured in GitHub
- Verify the secret doesn't have leading/trailing whitespace
- Check that you're using the correct header (`X-Hub-Signature-256`)

### Connection Issues

- Ensure port 8080 is not already in use
- Verify firewall settings allow incoming connections
- Check DevTunnel logs for connection errors

### Repository Cloning Issues

**gh CLI Not Found:**
- Verify `gh` is installed: `gh --version`
- Ensure `gh` is in your system PATH
- If not installed, see [GitHub CLI installation guide](https://github.com/cli/cli#installation)

**Authentication Failures:**
- Check authentication status: `gh auth status`
- Re-authenticate if needed: `gh auth login`
- Ensure you have access to the repository being cloned (check permissions for private repos)

**Clone Permission Denied:**
- Verify your GitHub account has read access to the repository
- For private repositories, ensure you're authenticated with an account that has access
- Check repository visibility settings

**Repository Already Exists:**
- By default, existing repositories are skipped (this is normal behavior)
- To update existing repositories, set `CLONE_UPDATE_EXISTING=true` in `.env`
- Manually remove old repositories from `{CLONE_BASE_DIR}` if needed

**Disk Space Issues:**
- Check available disk space: `df -h`
- Clean up old repositories in the `CLONE_BASE_DIR` directory
- Consider using shallow clones for large repositories (requires code modification)

## Resources

- [GitHub Webhooks Documentation](https://docs.github.com/en/webhooks)
- [Securing Webhooks](https://docs.github.com/en/webhooks/using-webhooks/validating-webhook-deliveries)
- [Microsoft DevTunnel Documentation](https://learn.microsoft.com/en-us/azure/developer/dev-tunnels/overview)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For questions or issues related to this webhook server, please open an issue in this repository with:

- A clear description of the problem
- Steps to reproduce
- Relevant error messages or logs
- Your environment details (OS, Python version, etc.)
