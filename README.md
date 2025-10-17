# GitHub Webhook with DevTunnel

Quick setup for testing GitHub webhooks locally using Microsoft DevTunnel.

## Quick Start

### Automated Setup (Recommended)

The fastest way to get started is using the automated setup script:

1. **Setup Environment**
   ```bash
   cp .env.sample .env
   ```
   Edit `.env` and set your `GITHUB_WEBHOOK_SECRET` (generate one with `openssl rand -hex 32`)

2. **Run the Setup Script**
   ```bash
   ./scripts/dev-setup.sh https://github.com/owner/repo
   ```
   
   This single command will:
   - Start DevTunnel automatically
   - Launch the webhook server
   - Create a GitHub webhook configured for issues events
   - Display the webhook URL and status
   
   Press Ctrl+C to stop both services when done.

**Prerequisites:**
- GitHub CLI (`gh`) installed and authenticated (`gh auth login`)
- `.env` file with `GITHUB_WEBHOOK_SECRET` configured

**Supported repository URL formats:**
- `https://github.com/owner/repo`
- `git@github.com:owner/repo.git`
- `owner/repo`

### Manual Setup

If you prefer to run each component separately:

1. **Setup Environment**
   ```bash
   cp .env.sample .env
   ```
   Edit `.env` and set your `GITHUB_WEBHOOK_SECRET` (generate one with `openssl rand -hex 32`)
   
   **Optional: Enable Repository Cloning**
   ```bash
   CLONE_REPOS=true                    # Enable auto-cloning (default: false)
   CLONE_BASE_DIR=./repos              # Base directory (default: ./repos)
   CLONE_UPDATE_EXISTING=false         # Pull updates if exists (default: false)
   ```
   
   Note: Repository cloning requires the `gh` CLI to be installed and authenticated (`gh auth login`)

2. **Start DevTunnel**
   ```bash
   ./scripts/start-devtunnel.sh
   ```
   Copy the DevTunnel URL from the output (e.g., `https://xxxxx.devtunnels.ms`)

3. **Start Webhook Server**
   ```bash
   uv run src/webhook.py
   ```

4. **Configure GitHub Webhook**
   - Go to your repository settings → Webhooks → Add webhook
   - Payload URL: `https://your-devtunnel-url.devtunnels.ms/webhook`
   - Content type: `application/json`
   - Secret: Use the same secret from your `.env` file
   - Events: Select "Issues"
   - Save webhook

The webhook will print issue details to the console when issues are created or updated. If `CLONE_REPOS=true`, it will also automatically clone the repository locally.

## AI Developer Inner-Loop (ADIL)

ADIL is a command-line utility that integrates GitHub Copilot CLI into your development workflow. It automatically loads project context and helps with development tasks:

```bash
# Get help with implementing a feature
./src/adil.py "add support for pull request events"

# Or use via uv
uv run src/adil.py "fix the webhook signature verification"
```

ADIL combines your prompt with project context from `docs/prime.md` and invokes Copilot with automation enabled. This accelerates the development loop by eliminating manual context setup.

**Prerequisites:**
- GitHub Copilot CLI installed and authenticated
- Python 3.12 or higher

## Testing

Run the integration test suite to verify the webhook server works correctly:

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run tests with even more verbose output
uv run pytest -vv

# Run specific test file
uv run pytest tests/test_webhook_integration.py -v

# Run specific test
uv run pytest tests/test_webhook_integration.py::test_valid_webhook_with_correct_signature -v
```

The tests are integration tests that start the actual webhook server as a subprocess and send real HTTP requests to validate behavior. No external services or real GitHub credentials are needed - tests run completely offline and use mock payloads with test secrets.
