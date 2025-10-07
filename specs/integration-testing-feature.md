# Integration Testing Feature Specification

## Overview

This specification describes the addition of integration tests for the GitHub webhook handler (`webhook.py`). The tests will use pytest to run the actual webhook server and send real HTTP requests to validate expected behavior without mocks or unit tests.

## Goals

The primary goal is to create end-to-end integration tests that:

1. Start the actual webhook server process
2. Send real HTTP requests with valid and invalid payloads
3. Assert expected responses and behavior
4. Validate signature verification works correctly
5. Validate issue event handling works as expected

## Current State

Currently, there are no automated tests for the webhook server. Testing is done manually by:
- Starting the server
- Configuring a GitHub webhook
- Creating issues and observing console output

## Proposed Solution

Create integration tests using pytest that:
- Use `uv` for Python package management and script execution
- Run the actual webhook server as a subprocess
- Send HTTP requests using `httpx` or `requests`
- Validate responses and behavior
- Test both success and failure scenarios

## Test Scenarios

### 1. Server Startup Test
- Verify the server starts successfully
- Verify it listens on the expected port
- Verify it responds to health checks (if added)

### 2. Valid Webhook with Correct Signature
- Send a properly signed webhook payload for an "issues opened" event
- Verify 200 OK response
- Verify response body contains expected data
- Optionally capture console output to verify issue info was printed

### 3. Invalid Signature
- Send a webhook payload with an incorrect signature
- Verify 401 Unauthorized response
- Verify appropriate error message

### 4. Missing Signature
- Send a webhook payload without a signature header
- Verify 401 Unauthorized response

### 5. Different Event Types
- Send webhook payloads for different event types (issues closed, pull request, etc.)
- Verify appropriate responses
- Verify only "issues opened" events are processed specially

### 6. Malformed Payload
- Send invalid JSON payload
- Verify appropriate error response

## Implementation Details

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # pytest fixtures for server setup/teardown
└── test_webhook_integration.py  # integration tests
```

### Test Script Dependencies

Create a test script with inline dependencies using PEP 723:

```python
#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "pytest",
#     "httpx",
#     "python-dotenv",
# ]
# ///
```

### Key Components

#### 1. Server Fixture
Create a pytest fixture that:
- Sets up test environment variables (test webhook secret)
- Starts the webhook server as a subprocess
- Waits for server to be ready
- Yields the server URL
- Tears down server after tests

#### 2. Helper Functions
- `generate_signature(payload: bytes, secret: str) -> str`: Generate valid GitHub webhook signatures
- `create_issue_payload(**kwargs) -> dict`: Create valid GitHub issue webhook payloads

#### 3. Test Functions
Each test function will:
- Use the server fixture
- Send HTTP requests with appropriate headers and payloads
- Assert response status codes and bodies
- Clean up any test artifacts

### Configuration

Add test configuration to `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### Environment Variables for Testing

Tests will use a dedicated test secret:
- `GITHUB_WEBHOOK_SECRET` will be set to a known value during tests
- Tests will run on a random available port to avoid conflicts

## Running Tests

Tests should be runnable with:

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_webhook_integration.py

# Run specific test
uv run pytest tests/test_webhook_integration.py::test_valid_webhook
```

## Dependencies

New dependencies for testing:
- `pytest` - testing framework
- `httpx` - HTTP client for sending requests to the webhook
- Test dependencies should be added using: `uv add --dev pytest httpx`

Existing dependencies from webhook.py (will be reused):
- `fastapi`
- `uvicorn`
- `python-dotenv`

## Success Criteria

1. Tests can be run with `uv run pytest` and pass consistently
2. Tests start and stop the webhook server cleanly without leaving processes
3. Tests validate signature verification works correctly
4. Tests validate issue event handling
5. Tests run in under 10 seconds
6. Tests can run in CI/CD environments

## Testing Approach

**What We're Testing:**
- Real HTTP requests and responses
- Signature verification logic
- Event handling logic
- Server startup and configuration

**What We're NOT Testing:**
- Internal implementation details
- Mocked or stubbed components
- Unit-level function isolation

## Security Considerations

1. Tests will use a known test secret, not production secrets
2. Tests will not make external API calls
3. Tests will not require real GitHub credentials
4. Test payloads will be self-contained and not require network access

## Future Enhancements

1. Add performance tests (request throughput, response time)
2. Add tests for concurrent requests
3. Add tests for webhook payload edge cases
4. Integration with CI/CD pipelines
5. Code coverage reporting

## Notes

- Tests should be fast and not depend on external services
- Tests should clean up after themselves (no leftover processes or files)
- Tests should be deterministic and not flaky
- Consider using a different port for tests to avoid conflicts with development server
