#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "fastapi",
#     "uvicorn",
#     "python-dotenv",
# ]
# ///

from fastapi import FastAPI, Request, HTTPException
import uvicorn
import hmac
import hashlib
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# GitHub webhook secret from environment
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
if not WEBHOOK_SECRET:
    raise ValueError("GITHUB_WEBHOOK_SECRET environment variable is not set. Please create a .env file with this variable.")


def verify_signature(payload_body: bytes, signature_header: str) -> bool:
    """Verify that the payload was sent from GitHub by validating SHA256.
    
    Args:
        payload_body: The raw request body bytes
        signature_header: The X-Hub-Signature-256 header value
        
    Returns:
        True if signature is valid, False otherwise
    """
    if not signature_header:
        return False
    
    # Get the signature from the header (format: sha256=...)
    hash_algorithm, github_signature = signature_header.split('=')
    if hash_algorithm != 'sha256':
        return False
    
    # Create our own signature
    mac = hmac.new(WEBHOOK_SECRET.encode(), msg=payload_body, digestmod=hashlib.sha256)
    expected_signature = mac.hexdigest()
    
    # Compare signatures
    return hmac.compare_digest(expected_signature, github_signature)


@app.post("/webhook")
async def github_webhook(request: Request):
    """Handle GitHub webhook events."""
    # Get the signature from headers
    signature_header = request.headers.get("X-Hub-Signature-256")
    
    # Get raw body for signature verification
    body = await request.body()
    
    # Verify the signature
    if not verify_signature(body, signature_header):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Get the event type from headers
    event_type = request.headers.get("X-GitHub-Event")
    
    # Parse the JSON payload from the body bytes
    payload = json.loads(body)
    
    # Handle issue creation events
    if event_type == "issues" and payload.get("action") == "opened":
        issue = payload.get("issue", {})
        
        print("\n" + "="*60)
        print("🎉 NEW ISSUE CREATED!")
        print("="*60)
        print(f"Title:       {issue.get('title')}")
        print(f"Number:      #{issue.get('number')}")
        print(f"Author:      {issue.get('user', {}).get('login')}")
        print(f"State:       {issue.get('state')}")
        print(f"URL:         {issue.get('html_url')}")
        print(f"Created at:  {issue.get('created_at')}")
        print(f"\nBody:\n{issue.get('body', 'No description provided')}")
        print("="*60 + "\n")
        
        return {"status": "success", "message": "Issue information printed"}
    
    # Handle other events
    return {"status": "received", "event": event_type}


def main() -> None:
    """Start the webhook server."""
    # Allow port configuration via environment variable for testing
    port = int(os.getenv("WEBHOOK_PORT", "8080"))
    
    print("🚀 Starting GitHub webhook server...")
    print(f"📡 Listening on http://0.0.0.0:{port}/webhook")
    print("💡 Configure your GitHub webhook to point to this endpoint")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
