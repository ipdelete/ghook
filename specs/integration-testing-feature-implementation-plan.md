# Feature: Integration Testing with pytest

## Metadata
spec_file: `specs/integration-testing-feature.md`

## Feature Description

This feature adds comprehensive integration tests for the GitHub webhook handler using pytest. The tests will run the actual webhook server as a subprocess and send real HTTP requests to validate behavior. This approach tests the complete system end-to-end without mocks or stubs, ensuring the webhook handler works correctly in real-world scenarios.

The testing suite will validate signature verification, event handling, error responses, and server startup/shutdown. Tests will use uv for dependency management and pytest for test execution, following the project's existing patterns with PEP 723 inline script dependencies.

## User Story

As a developer maintaining the webhook server
I want automated integration tests that validate real-world behavior
So that I can confidently make changes without breaking functionality and catch issues before deployment

## Problem Statement

Currently, the webhook server has no automated tests. All testing is manual, requiring:
- Starting the server manually
- Configuring actual GitHub webhooks
- Creating real issues to trigger events
- Manually inspecting console output

This manual process is time-consuming, error-prone, and doesn't provide quick feedback during development. It's also difficult to test edge cases and error conditions. Without automated tests, refactoring or adding features carries significant risk of introducing regressions.

## Solution Statement

Create a pytest-based integration test suite that automatically starts the webhook server, sends HTTP requests with various payloads and signatures, and validates responses and behavior. The tests will use the actual production code without mocks, providing high confidence that the system works correctly. Tests will be fast, deterministic, and runnable locally or in CI/CD pipelines using uv and pytest.

## Relevant Files

### Existing Files
- `src/webhook.py` - The webhook server to be tested. We'll need to understand its endpoints, signature verification, and event handling logic.
- `pyproject.toml` - Project configuration where we'll add pytest configuration and dev dependencies.
- `.env.sample` - Sample environment configuration that tests will reference for required environment variables.
- `README.md` - Documentation that should be updated to include testing instructions.

### New Files

#### `tests/__init__.py`
Empty file to make tests a Python package.

#### `tests/conftest.py`
Pytest configuration and fixtures including:
- Server fixture to start/stop webhook server
- Helper fixtures for creating test payloads
- Signature generation helpers

#### `tests/test_webhook_integration.py`
Main integration test file with inline uv dependencies (PEP 723) containing:
- Tests for valid webhook requests
- Tests for invalid signatures
- Tests for different event types
- Tests for error conditions

## Implementation Plan

### Phase 1: Foundation
Set up the testing infrastructure including directory structure, pytest configuration, and helper utilities. This includes creating the test fixtures that manage the webhook server lifecycle and helper functions for generating valid webhook signatures and payloads.

### Phase 2: Core Implementation
Implement the actual integration tests that cover the main use cases: valid requests with correct signatures, invalid signatures, different event types, and error conditions. Each test will send real HTTP requests to the running webhook server and validate responses.

### Phase 3: Integration
Ensure tests run smoothly with uv, update documentation with testing instructions, and validate that tests can run in different environments. Add pytest configuration to pyproject.toml and ensure all tests pass reliably.

## Step by Step Tasks

### Step 1: Create test directory structure
- Create `tests/` directory in the repository root
- Create `tests/__init__.py` as an empty file to make it a package
- Verify directory structure matches pytest conventions

### Step 2: Create pytest fixtures and helpers (tests/conftest.py)
- Create `tests/conftest.py` with PEP 723 inline dependencies (pytest, httpx, python-dotenv)
- Add shebang: `#!/usr/bin/env -S uv run`
- Implement `webhook_server` fixture that:
  - Sets up test environment variables (GITHUB_WEBHOOK_SECRET with known test value)
  - Starts webhook.py as a subprocess on a random available port
  - Waits for server to be ready using health checks or retry logic
  - Yields server URL (e.g., "http://localhost:PORT")
  - Tears down server gracefully after tests
- Implement helper function `generate_signature(payload: bytes, secret: str) -> str` to create valid HMAC-SHA256 signatures
- Implement helper function `create_issue_payload(**kwargs) -> dict` to generate valid GitHub issue webhook payloads with sensible defaults
- Test the fixtures manually by running a simple test

### Step 3: Create main integration test file (tests/test_webhook_integration.py)
- Create `tests/test_webhook_integration.py` with PEP 723 inline dependencies (pytest, httpx, python-dotenv)
- Add shebang: `#!/usr/bin/env -S uv run`
- Import necessary modules and helpers from conftest
- Create test class or use plain test functions following pytest conventions

### Step 4: Implement test for valid webhook with correct signature
- Test name: `test_valid_webhook_with_correct_signature`
- Use webhook_server fixture
- Create an "issues opened" payload using helper function
- Generate valid signature for the payload
- Send POST request to `/webhook` with:
  - `X-Hub-Signature-256` header with valid signature
  - `X-GitHub-Event: issues` header
  - JSON payload
- Assert response status is 200
- Assert response JSON contains expected fields (status: "success")

### Step 5: Implement test for invalid signature
- Test name: `test_invalid_signature_returns_401`
- Use webhook_server fixture
- Create an "issues opened" payload
- Generate an incorrect signature (use wrong secret)
- Send POST request to `/webhook` with invalid signature
- Assert response status is 401
- Assert response contains appropriate error message

### Step 6: Implement test for missing signature
- Test name: `test_missing_signature_returns_401`
- Use webhook_server fixture
- Create payload but don't include signature header
- Send POST request to `/webhook` without `X-Hub-Signature-256` header
- Assert response status is 401

### Step 7: Implement test for different event types
- Test name: `test_non_issue_event_returns_received_status`
- Use webhook_server fixture
- Create payload for a different event type (e.g., "pull_request")
- Generate valid signature
- Send POST request with proper headers but different event type
- Assert response status is 200
- Assert response JSON indicates event was received but not specially processed

### Step 8: Implement test for malformed JSON payload
- Test name: `test_malformed_json_returns_error`
- Use webhook_server fixture
- Send POST request with invalid JSON body
- Generate signature for the invalid JSON
- Assert appropriate error response (422 or 400 depending on FastAPI behavior)

### Step 9: Add pytest configuration to pyproject.toml
- Open `pyproject.toml`
- Add `[tool.pytest.ini_options]` section with:
  - `testpaths = ["tests"]`
  - `python_files = ["test_*.py"]`
  - `python_classes = ["Test*"]`
  - `python_functions = ["test_*"]`
- Add development dependencies section if not present
- Document how to add pytest and httpx dependencies

### Step 10: Run tests and fix any issues
- Run `uv run pytest -v` to execute all tests
- Verify all tests pass
- Check for any race conditions or timing issues with server startup
- Adjust retry logic or wait times if needed
- Ensure server cleanup works (no zombie processes)

### Step 11: Update README.md with testing instructions
- Add a "Testing" section to README.md
- Document how to run tests: `uv run pytest`
- Document how to run tests with verbose output: `uv run pytest -v`
- Document how to run specific tests
- Note that tests are integration tests that start the actual server
- Mention that no external services or real GitHub credentials are needed

### Step 12: Validation - Run all validation commands
- Execute all commands from the "Validation Commands" section below
- Ensure all commands succeed without errors
- Fix any issues that arise
- Confirm tests are reliable and don't leave processes running

## Testing Strategy

### Manual Testing
1. Run pytest and verify all tests pass
2. Intentionally break webhook.py (e.g., change signature verification logic) and verify tests catch the failure
3. Run tests multiple times to ensure they're not flaky
4. Check that no webhook processes remain running after tests complete
5. Verify tests can run without internet connection (no external dependencies)

### Edge Cases
- Server fails to start (port already in use) - fixture should handle gracefully
- Server takes longer than expected to start - retry logic with timeout
- Invalid JSON in payload - FastAPI should return 422 Unprocessable Entity
- Empty payload - should fail signature verification
- Very large payload - should handle gracefully
- Concurrent test execution - tests should use different ports or run serially

## Acceptance Criteria

1. Tests can be run with `uv run pytest` command and all tests pass
2. Tests start and stop the webhook server cleanly without leaving zombie processes
3. At least 5 integration tests covering:
   - Valid webhook with correct signature (200 response)
   - Invalid signature (401 response)
   - Missing signature (401 response)
   - Different event types (200 response with different handling)
   - Malformed JSON (error response)
4. Tests use the actual webhook server code, not mocks
5. Tests run in under 10 seconds total
6. Tests are deterministic and pass consistently
7. README.md includes testing instructions
8. pyproject.toml includes pytest configuration

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

```bash
# Verify Python syntax is valid for all test files
python -c "import ast; ast.parse(open('tests/conftest.py').read())"
python -c "import ast; ast.parse(open('tests/test_webhook_integration.py').read())"

# Verify the webhook server still works without tests
./src/webhook.py --help || echo "Server can be executed"

# Run all integration tests with verbose output
uv run pytest -v

# Run tests and show test coverage summary if possible
uv run pytest -v --tb=short

# Verify no processes left running after tests
ps aux | grep webhook.py | grep -v grep || echo "No webhook processes running - good!"

# Run specific test file to ensure it works in isolation
uv run pytest tests/test_webhook_integration.py -v

# Verify tests can be discovered
uv run pytest --collect-only

# Run tests with more verbose output to see what's happening
uv run pytest -vv

# Check that pyproject.toml is valid TOML
python -c "import tomllib; tomllib.load(open('pyproject.toml', 'rb'))"
```

## Notes

### Testing Philosophy
This implementation uses integration tests rather than unit tests because:
- The webhook server is a relatively small, cohesive component
- Integration tests provide more value by testing real HTTP interactions
- Signature verification and event handling are best tested end-to-end
- Avoiding mocks makes tests simpler and more maintainable

### Port Selection
Tests should use a random available port to avoid conflicts with:
- The development webhook server
- Other test runs
- Other services on the system

Consider using port 0 in the subprocess and parsing the actual port from output, or using a helper to find available ports.

### Server Startup Wait
The webhook server may take a moment to start. The fixture should:
- Wait for the server to be ready before tests run
- Use retry logic with exponential backoff
- Timeout after a reasonable period (e.g., 5 seconds)
- Consider adding a `/health` endpoint to webhook.py for easier readiness checks

### Cleanup Considerations
Ensure proper cleanup even if tests fail:
- Use pytest fixtures with proper teardown
- Use try/finally blocks
- Consider using `subprocess.Popen` with context managers
- Send SIGTERM then SIGKILL if needed

### Dependencies Management
Since both conftest.py and test files use PEP 723 inline dependencies:
- Each file is independently executable
- uv handles dependency installation automatically
- No need for a separate requirements.txt for tests
- pytest can run all tests using the inline dependencies

### Future Enhancements
- Add a `/health` endpoint to webhook.py for better test readiness checking
- Add performance benchmarks
- Test concurrent webhook requests
- Add integration with CI/CD (GitHub Actions)
- Add code coverage reporting with pytest-cov
