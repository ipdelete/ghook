# Verify Command

Pull the latest changes from the remote branch and run the test suite to verify everything works correctly after code review changes have been addressed.

## Instructions

1. **Check current branch and status**
   
   Verify which branch you're on:
   ```bash
   git branch --show-current
   git status --short
   ```
   
   If there are uncommitted changes, inform the user and ask if they want to:
   - Stash changes and proceed
   - Commit changes first
   - Abort the test run

2. **Pull latest changes**
   
   Pull the latest commits from the remote branch:
   ```bash
   git pull --rebase
   ```
   
   If there are merge conflicts, inform the user and abort with instructions to resolve conflicts.

3. **Verify Python environment**
   
   Ensure the project dependencies are available:
   ```bash
   uv --version
   ```

4. **Run the test suite**
   
   Execute all tests with verbose output:
   ```bash
   uv run pytest -v
   ```
   
   This will run all integration tests and display detailed results.

5. **Display test results**
   
   The pytest output will show:
   - Number of tests passed/failed/skipped
   - Execution time for each test
   - Overall test summary
   - Any error messages or failures

6. **Report status**
   
   Based on the test results:
   - If all tests pass: Confirm success with test count and execution time
   - If tests fail: Display which tests failed and why
   - If tests are skipped: Note which tests were skipped and reason

## Report

Output a concise summary:
- Branch name
- Number of commits pulled (if any)
- Test results (passed/failed/skipped counts)
- Total execution time
- Status: ✅ All tests passed or ❌ Tests failed

Example output:
```
Branch: feature/repository-cloning
Pulled 2 commits from remote
Tests: 8 passed in 3.45s
✅ All tests passed
```

## Notes

- This command is intended to be run after code review feedback has been addressed
- Use this to verify changes made by others on the PR branch work correctly before merging
- This command uses `--rebase` to maintain a linear history when pulling
- Tests run with `-v` (verbose) flag for detailed output
- If you want more detailed output, you can manually run `uv run pytest -vv`
- For specific test files, run: `uv run pytest tests/test_file.py -v`
- For a single test, run: `uv run pytest tests/test_file.py::test_name -v`
