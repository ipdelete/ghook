#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pytest",
#     "httpx",
#     "python-dotenv",
# ]
# ///

import pytest
import subprocess
import time
import os
import hmac
import hashlib
import signal
import httpx
from pathlib import Path


@pytest.fixture
def webhook_server():
    """Start the webhook server as a subprocess and return its URL."""
    # Set test environment variables
    test_secret = "test_webhook_secret_12345"
    test_port = 18080
    
    env = os.environ.copy()
    env["GITHUB_WEBHOOK_SECRET"] = test_secret
    env["WEBHOOK_PORT"] = str(test_port)
    
    # Path to webhook.py
    webhook_path = Path(__file__).parent.parent / "src" / "webhook.py"
    
    # Start the server with modified port
    process = subprocess.Popen(
        ["python", str(webhook_path)],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        preexec_fn=os.setsid  # Create new process group for easier cleanup
    )
    
    # Wait for server to be ready
    server_url = f"http://localhost:{test_port}"
    max_retries = 30
    retry_delay = 0.2
    
    for i in range(max_retries):
        try:
            # Try to connect to the server
            response = httpx.get(f"{server_url}/", timeout=1.0)
            # If we get any response, server is up (even 404 is fine)
            break
        except (httpx.ConnectError, httpx.TimeoutException):
            if i == max_retries - 1:
                # Kill process and fail
                os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                process.wait(timeout=2)
                raise RuntimeError(f"Server failed to start after {max_retries * retry_delay} seconds")
            time.sleep(retry_delay)
    
    # Yield server URL and secret for tests
    yield {
        "url": server_url,
        "secret": test_secret,
        "port": test_port
    }
    
    # Cleanup: terminate the server
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGTERM)
        process.wait(timeout=2)
    except subprocess.TimeoutExpired:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
        process.wait()


def generate_signature(payload: bytes, secret: str) -> str:
    """Generate a valid GitHub webhook signature for the given payload.
    
    Args:
        payload: The raw request body as bytes
        secret: The webhook secret
        
    Returns:
        The signature in the format 'sha256=<hex_digest>'
    """
    mac = hmac.new(secret.encode(), msg=payload, digestmod=hashlib.sha256)
    return f"sha256={mac.hexdigest()}"


def create_issue_payload(**kwargs) -> dict:
    """Create a GitHub issue webhook payload with sensible defaults.
    
    Args:
        **kwargs: Override default values (action, issue fields, etc.)
        
    Returns:
        A dictionary representing a GitHub issue webhook payload
    """
    default_payload = {
        "action": "opened",
        "issue": {
            "number": 42,
            "title": "Test Issue",
            "body": "This is a test issue body",
            "state": "open",
            "html_url": "https://github.com/test/repo/issues/42",
            "created_at": "2024-01-01T12:00:00Z",
            "user": {
                "login": "testuser"
            }
        },
        "repository": {
            "name": "test-repo",
            "full_name": "test/test-repo"
        }
    }
    
    # Merge provided kwargs with defaults
    if kwargs:
        # Handle nested updates
        if "issue" in kwargs:
            default_payload["issue"].update(kwargs["issue"])
            del kwargs["issue"]
        default_payload.update(kwargs)
    
    return default_payload
