# Feature: AI Developer Inner-Loop (ADIL)

## Feature Description

ADIL is a command-line utility script that integrates GitHub Copilot CLI into the development workflow for this webhook testing repository. It enables developers to leverage AI-powered assistance for development tasks by automatically loading project context (via `docs/prime.md`) and passing user prompts to Copilot. This accelerates the inner development loop by reducing context-switching and enabling seamless AI-assisted coding within the existing workflow.

## User Story

As a developer working on this webhook server
I want to run a simple command with a development task description
So that Copilot automatically loads project context and helps me implement features, fix bugs, or perform other development work efficiently

## Problem Statement

Developers need to manually run `copilot -p` commands while ensuring they have proper project context. This requires remembering to read `docs/prime.md` for context setup and manually constructing the command-line invocation. ADIL eliminates this friction by automating context loading and providing a simple script-based interface.

## Solution Statement

Create a new uv script (`src/adil.py`) that wraps the `copilot` CLI tool. The script accepts a user prompt as arguments, automatically combines it with the prime.md context directive, and invokes Copilot with appropriate flags. This maintains consistency across the development team and ensures everyone has the same project context when using AI assistance.

## Relevant Files

- **`src/webhook.py`** - Existing uv script that demonstrates the project's script pattern; ADIL will follow the same structure and conventions
- **`.github/copilot-instructions.md`** - Project's Copilot instructions that define development practices and patterns
- **`docs/prime.md`** - Project context and initialization guide that ADIL will reference
- **`README.md`** - Project overview and documentation structure
- **`pyproject.toml`** - Project configuration (for consistency reference)

### New Files

- **`src/adil.py`** - Main ADIL script that integrates Copilot with project context

## Implementation Plan

### Phase 1: Foundation

Understand the existing uv script pattern used in `src/webhook.py`. ADIL will follow the same structure with a `#!/usr/bin/env -S uv run` shebang, inline dependencies declaration in a `# /// script` block, and a main function entry point.

### Phase 2: Core Implementation

Implement the ADIL script that accepts user prompts as command-line arguments and constructs a full prompt combining the prime.md context directive with the user-provided text. The script will invoke `copilot -p` with `--allow-all-tools` flag to enable automation and pipe the execution to the terminal.

### Phase 3: Integration

Ensure the script is executable and follows repository conventions. The script integrates seamlessly with the existing development workflow as a peer to `src/webhook.py`.

## Step by Step Tasks

### Step 1: Create the ADIL script

- Create `src/adil.py` with the uv script shebang and inline dependencies
- Add argument parsing to accept the user prompt from command-line arguments
- Implement the core logic that constructs the full prompt: `f"follow docs/prime.md and {argument}"`
- Execute `copilot -p` with the constructed prompt and `--allow-all-tools` flag
- Include proper error handling for missing copilot command and missing arguments
- Return appropriate exit codes for success and error conditions

### Step 2: Make the script executable

- Verify the script has the correct shebang line: `#!/usr/bin/env -S uv run`
- Test that the script can be invoked directly: `./src/adil.py "your prompt here"`
- Test that the script can be invoked via uv: `uv run src/adil.py "your prompt here"`

### Step 3: Test the implementation

- Run ADIL with a simple test prompt to verify copilot integration works
- Verify that copilot receives the correct combined prompt with prime.md context
- Verify that Copilot executes with the `--allow-all-tools` flag
- Test error handling with no arguments provided
- Test error handling when copilot command is not available

### Step 4: Validate with acceptance criteria

- Execute all validation commands to ensure zero regressions
- Verify the script syntax is valid Python
- Confirm the script follows the same pattern as webhook.py
- Ensure the feature meets all acceptance criteria

## Testing Strategy

### Manual Testing

- Run `./src/adil.py "add support for pull request events"` and verify Copilot opens with the correct context
- Run `./src/adil.py "fix the webhook signature verification"` and verify Copilot receives the combined prompt
- Run `uv run src/adil.py "document the API endpoints"` and verify it works with uv invocation
- Verify the output shows that copilot is being invoked with correct flags

### Edge Cases

- No arguments provided (should display usage instructions)
- Multi-word prompts with special characters
- Copilot command not installed (should display helpful error message)
- Very long prompts (should be passed correctly to copilot)

## Acceptance Criteria

- ADIL script exists at `src/adil.py` with proper uv shebang
- Script accepts a prompt argument (single or multiple words)
- Script constructs the full prompt as: `follow docs/prime.md and {user_prompt}`
- Script executes `copilot -p "{full_prompt}" --allow-all-tools`
- Script displays helpful error message if copilot is not available
- Script displays usage instructions if no prompt argument is provided
- Script can be invoked as `./src/adil.py "prompt"` or `uv run src/adil.py "prompt"`
- Script follows the same conventions and style as `src/webhook.py`
- No existing tests or functionality is broken

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `python -c "import ast; ast.parse(open('src/adil.py').read())"` - Verify Python syntax is valid
- `./src/adil.py` - Test missing arguments (should display usage instructions)
- `uv run src/adil.py "test prompt"` - Test basic invocation with uv
- `python -m py_compile src/adil.py` - Verify Python bytecode compilation succeeds
- `uv run pytest` - Run full test suite to verify zero regressions
- `git ls-files | grep adil.py` - Verify the script is tracked by git

## Notes

- The ADIL script does not require any external dependencies beyond what's already in the project
- The script uses subprocess.run to invoke copilot, following the pattern used in webhook.py for gh CLI invocation
- Future enhancements could include support for environment variables to customize the copilot model, additional flags, or conditional context loading
- The script name "ADIL" stands for "AI Developer Inner-Loop" and should be documented in the README if this feature is widely adopted
