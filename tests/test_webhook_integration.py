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
import httpx
import json
from tests.conftest import generate_signature, create_issue_payload


def test_valid_webhook_with_correct_signature(webhook_server):
    """Test that a valid webhook request with correct signature returns 200."""
    server = webhook_server
    
    # Create issue payload
    payload = create_issue_payload()
    payload_bytes = json.dumps(payload).encode()
    
    # Generate valid signature
    signature = generate_signature(payload_bytes, server["secret"])
    
    # Send POST request
    response = httpx.post(
        f"{server['url']}/webhook",
        content=payload_bytes,
        headers={
            "X-Hub-Signature-256": signature,
            "X-GitHub-Event": "issues",
            "Content-Type": "application/json"
        },
        timeout=5.0
    )
    
    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data


def test_invalid_signature_returns_401(webhook_server):
    """Test that a webhook request with invalid signature returns 401."""
    server = webhook_server
    
    # Create issue payload
    payload = create_issue_payload()
    payload_bytes = json.dumps(payload).encode()
    
    # Generate signature with WRONG secret
    wrong_signature = generate_signature(payload_bytes, "wrong_secret")
    
    # Send POST request with invalid signature
    response = httpx.post(
        f"{server['url']}/webhook",
        content=payload_bytes,
        headers={
            "X-Hub-Signature-256": wrong_signature,
            "X-GitHub-Event": "issues",
            "Content-Type": "application/json"
        },
        timeout=5.0
    )
    
    # Assert response
    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


def test_missing_signature_returns_401(webhook_server):
    """Test that a webhook request without signature header returns 401."""
    server = webhook_server
    
    # Create issue payload
    payload = create_issue_payload()
    payload_bytes = json.dumps(payload).encode()
    
    # Send POST request WITHOUT signature header
    response = httpx.post(
        f"{server['url']}/webhook",
        content=payload_bytes,
        headers={
            "X-GitHub-Event": "issues",
            "Content-Type": "application/json"
        },
        timeout=5.0
    )
    
    # Assert response
    assert response.status_code == 401


def test_non_issue_event_returns_received_status(webhook_server):
    """Test that non-issue events are received but not specially processed."""
    server = webhook_server
    
    # Create a pull request payload (different event type)
    payload = {
        "action": "opened",
        "pull_request": {
            "number": 1,
            "title": "Test PR"
        }
    }
    payload_bytes = json.dumps(payload).encode()
    
    # Generate valid signature
    signature = generate_signature(payload_bytes, server["secret"])
    
    # Send POST request with pull_request event
    response = httpx.post(
        f"{server['url']}/webhook",
        content=payload_bytes,
        headers={
            "X-Hub-Signature-256": signature,
            "X-GitHub-Event": "pull_request",
            "Content-Type": "application/json"
        },
        timeout=5.0
    )
    
    # Assert response
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"
    assert data["event"] == "pull_request"


def test_malformed_json_returns_error(webhook_server):
    """Test that malformed JSON payload returns appropriate error."""
    server = webhook_server
    
    # Create invalid JSON
    invalid_json = b"{ invalid json content"
    
    # Generate signature for the invalid JSON
    signature = generate_signature(invalid_json, server["secret"])
    
    # Send POST request with malformed JSON
    response = httpx.post(
        f"{server['url']}/webhook",
        content=invalid_json,
        headers={
            "X-Hub-Signature-256": signature,
            "X-GitHub-Event": "issues",
            "Content-Type": "application/json"
        },
        timeout=5.0
    )
    
    # Assert error response (FastAPI returns 422 for JSON decode errors)
    assert response.status_code in [400, 422, 500]
