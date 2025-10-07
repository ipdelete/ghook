# GitHub Webhook with DevTunnel

Quick setup for testing GitHub webhooks locally using Microsoft DevTunnel.

## Quick Start

1. **Setup Environment**
   ```bash
   cp .env.sample .env
   ```
   Edit `.env` and set your `GITHUB_WEBHOOK_SECRET` (generate one with `openssl rand -hex 32`)

2. **Start DevTunnel**
   ```bash
   ./start-devtunnel.sh
   ```
   Copy the DevTunnel URL from the output (e.g., `https://xxxxx.devtunnels.ms`)

3. **Start Webhook Server**
   ```bash
   uv run webhook.py
   ```

4. **Configure GitHub Webhook**
   - Go to your repository settings → Webhooks → Add webhook
   - Payload URL: `https://your-devtunnel-url.devtunnels.ms/webhook`
   - Content type: `application/json`
   - Secret: Use the same secret from your `.env` file
   - Events: Select "Issues"
   - Save webhook

The webhook will print issue details to the console when issues are created or updated.

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
