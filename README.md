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
