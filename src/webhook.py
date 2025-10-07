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
import subprocess
import re
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = FastAPI()

# GitHub webhook secret from environment
WEBHOOK_SECRET = os.getenv("GITHUB_WEBHOOK_SECRET")
if not WEBHOOK_SECRET:
    raise ValueError("GITHUB_WEBHOOK_SECRET environment variable is not set. Please create a .env file with this variable.")

# Repository cloning configuration
CLONE_REPOS = os.getenv("CLONE_REPOS", "false").lower() == "true"
CLONE_BASE_DIR = Path(os.getenv("CLONE_BASE_DIR", "./repos"))
CLONE_UPDATE_EXISTING = os.getenv("CLONE_UPDATE_EXISTING", "false").lower() == "true"


def is_gh_cli_available() -> bool:
    """Check if the gh CLI is installed and available.
    
    Returns:
        True if gh CLI is available, False otherwise
    """
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


def sanitize_path_component(component: str) -> str:
    """Sanitize a path component to prevent path traversal attacks.
    
    Args:
        component: A path component (e.g., owner name or repo name)
        
    Returns:
        Sanitized path component
        
    Raises:
        ValueError: If the component contains invalid characters
    """
    # Remove leading/trailing whitespace
    component = component.strip()
    
    # Check for path traversal attempts
    if ".." in component or "/" in component or "\\" in component:
        raise ValueError(f"Invalid path component: {component}")
    
    # Allow only alphanumeric, hyphens, underscores, and dots (not at start or end, and no consecutive dots)
    if not re.match(r'^[a-zA-Z0-9](?:[\w-]|(?:\.(?!\.)))*[a-zA-Z0-9_-]$', component):
        raise ValueError(f"Invalid characters in path component: {component}")
    
    return component


def clone_repository(full_name: str, owner: str, repo_name: str) -> dict:
    """Clone a GitHub repository using the gh CLI.
    
    Args:
        full_name: The full repository name (e.g., "owner/repo")
        owner: The repository owner username
        repo_name: The repository name
        
    Returns:
        Dict with status and message about the clone operation
    """
    try:
        # Sanitize path components
        safe_owner = sanitize_path_component(owner)
        safe_repo = sanitize_path_component(repo_name)
    except ValueError as e:
        return {"status": "error", "message": f"Invalid repository path: {e}"}
    
    # Check if gh CLI is available
    if not is_gh_cli_available():
        return {"status": "error", "message": "gh CLI is not installed or not available"}
    
    # Build target path
    target_path = CLONE_BASE_DIR / safe_owner / safe_repo
    
    # Check if repository already exists
    if target_path.exists() and (target_path / ".git").exists():
        if CLONE_UPDATE_EXISTING:
            # Pull updates
            try:
                result = subprocess.run(
                    ["git", "-C", str(target_path), "pull"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result.returncode == 0:
                    return {"status": "updated", "path": str(target_path)}
                else:
                    return {"status": "error", "message": f"Failed to pull updates: {result.stderr}"}
            except subprocess.SubprocessError as e:
                return {"status": "error", "message": f"Failed to pull updates: {e}"}
        else:
            return {"status": "exists", "path": str(target_path)}
    
    # Create parent directory
    target_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Clone the repository
    try:
        result = subprocess.run(
            ["gh", "repo", "clone", full_name, str(target_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            return {"status": "cloned", "path": str(target_path)}
        else:
            return {"status": "error", "message": f"Clone failed: {result.stderr}"}
    except subprocess.SubprocessError as e:
        return {"status": "error", "message": f"Clone failed: {e}"}


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
        repository = payload.get("repository", {})
        
        # Extract repository information
        repo_full_name = repository.get("full_name", "")
        repo_name = repository.get("name", "")
        repo_owner = repository.get("owner", {}).get("login", "")
        repo_url = repository.get("html_url", "")
        repo_private = repository.get("private", False)
        
        print("\n" + "="*60)
        print("🎉 NEW ISSUE CREATED!")
        print("="*60)
        print(f"Repository:  {repo_full_name}")
        print(f"Owner:       {repo_owner}")
        print(f"Private:     {repo_private}")
        print(f"Repo URL:    {repo_url}")
        print()
        print("Issue Details:")
        print(f"Title:       {issue.get('title')}")
        print(f"Number:      #{issue.get('number')}")
        print(f"Author:      {issue.get('user', {}).get('login')}")
        print(f"State:       {issue.get('state')}")
        print(f"URL:         {issue.get('html_url')}")
        print(f"Created at:  {issue.get('created_at')}")
        print(f"\nBody:\n{issue.get('body', 'No description provided')}")
        
        # Clone repository if enabled
        clone_result = None
        if CLONE_REPOS and repo_full_name:
            print("\nRepository Clone:")
            clone_result = clone_repository(repo_full_name, repo_owner, repo_name)
            
            if clone_result["status"] == "cloned":
                print(f"✅ Cloned successfully to: {clone_result['path']}")
            elif clone_result["status"] == "exists":
                print(f"ℹ️  Repository already exists at: {clone_result['path']}")
            elif clone_result["status"] == "updated":
                print(f"🔄 Updated existing repository at: {clone_result['path']}")
            elif clone_result["status"] == "error":
                print(f"❌ Clone failed: {clone_result['message']}")
        
        print("="*60 + "\n")
        
        response = {
            "status": "success",
            "message": "Issue information printed",
            "repository": {
                "full_name": repo_full_name,
                "owner": repo_owner,
                "private": repo_private,
                "url": repo_url
            }
        }
        
        if clone_result:
            response["clone"] = clone_result
        
        return response
    
    # Handle other events
    return {"status": "received", "event": event_type}


def main() -> None:
    """Start the webhook server."""
    # Allow port configuration via environment variable for testing
    port = int(os.getenv("WEBHOOK_PORT", "8080"))
    
    print("🚀 Starting GitHub webhook server...")
    print(f"📡 Listening on http://0.0.0.0:{port}/webhook")
    print("💡 Configure your GitHub webhook to point to this endpoint")
    
    # Display clone configuration
    if CLONE_REPOS:
        print(f"\n🔄 Repository cloning: ENABLED")
        print(f"📁 Clone directory: {CLONE_BASE_DIR.absolute()}")
        print(f"♻️  Update existing: {CLONE_UPDATE_EXISTING}")
        
        # Check gh CLI availability
        if is_gh_cli_available():
            print("✅ gh CLI is available")
        else:
            print("⚠️  WARNING: gh CLI is not available - cloning will fail")
    else:
        print("\n⏸️  Repository cloning: DISABLED")
        print("   Set CLONE_REPOS=true in .env to enable")
    
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
