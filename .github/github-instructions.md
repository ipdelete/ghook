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

- **Issues**: Specifically the `opened` action, which displays detailed issue information in the console

You can extend the webhook handler in `webhook.py` to support additional events such as pull requests, pushes, releases, and more.

## Development Workflow

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- Microsoft DevTunnel CLI (for exposing local endpoints)

### Local Testing

1. Copy the environment template and configure your secret:
   ```bash
   cp .env.sample .env
   # Edit .env and add your GITHUB_WEBHOOK_SECRET
   ```

2. Start the DevTunnel in one terminal:
   ```bash
   ./start-devtunnel.sh
   ```

3. Start the webhook server in another terminal:
   ```bash
   uv run webhook.py
   ```

4. Configure your GitHub webhook using the DevTunnel URL from step 2

5. Test by creating an issue in your repository and watch the console output

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
