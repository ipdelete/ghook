# Feature: Koozie ASCII Art Script

## Feature Description

Create a new standalone Python script in the `src/` folder that displays the word "koozie" in fun, large ASCII art format. This script will be a simple utility that can be executed directly or via `uv run` to output colorful ASCII art representation of the word "koozie" to the terminal.

## User Story

As a developer
I want to run a script that displays "koozie" in ASCII art
So that I can enjoy a fun visual output and showcase the project's playful side

## Problem Statement

There is no existing utility in the project to display fun ASCII art. This feature adds a lighthearted utility script that can be run as a standalone tool or integrated into other project workflows (e.g., welcome messages, documentation, CI/CD output).

## Solution Statement

Create a new Python script (`koozie.py`) in the `src/` folder that uses ASCII art libraries or custom ASCII patterns to render the word "koozie" in a visually appealing format. The script will follow the project's existing patterns for Python scripts using `uv` with inline script dependencies.

## Relevant Files

- `src/webhook.py` - Reference for uv script pattern, shebang, and script structure
- `pyproject.toml` - Project configuration and dependencies
- `README.md` - Project documentation (may need updates if feature is highlighted)

### New Files

- `src/koozie.py` - The main koozie ASCII art script with uv inline dependencies

## Implementation Plan

### Phase 1: Foundation

- Review existing Python script patterns in the project (e.g., `webhook.py`, `adil.py`, `sdlc.py`)
- Understand the uv inline script dependency system (PEP 723) used in the project
- Select an ASCII art approach: either use a library like `pyfiglet` or `art`, or create custom ASCII patterns
- Design the ASCII art output to be visually appealing and easily readable

### Phase 2: Core Implementation

- Create `src/koozie.py` with proper `#!/usr/bin/env -S uv run` shebang
- Implement inline script dependencies using the `# /// script` block (PEP 723)
- Add ASCII art rendering logic for the word "koozie"
- Implement optional color support using standard terminal ANSI codes or a color library if preferred
- Add a main entry point that executes the ASCII art display when run

### Phase 3: Integration

- Ensure the script is executable and can be run via `./src/koozie.py` or `uv run src/koozie.py`
- Verify the script follows project conventions and style guidelines
- Ensure no dependencies on project-specific environment variables (script should be standalone)
- Consider optional enhancements like command-line arguments for different art styles or output options

## Step by Step Tasks

### Create the koozie.py script

- Create `src/koozie.py` with the proper shebang line
- Add PEP 723 script dependencies block with selected ASCII art library (e.g., `pyfiglet` or `art`)
- Implement the ASCII art rendering function using the selected library
- Add optional styling, colors, or multiple art style options
- Ensure the script is executable: `chmod +x src/koozie.py`

### Test the script

- Execute via direct script: `./src/koozie.py` and verify output
- Execute via uv: `uv run src/koozie.py` and verify output
- Verify the output displays "koozie" in fun ASCII art format
- Test on different terminal environments to ensure compatibility
- Verify no errors are produced and script exits cleanly

### Validation

- Run syntax validation: `python -c "import ast; ast.parse(open('src/koozie.py').read())"`
- Run the script multiple times to ensure consistent output
- Verify the script works standalone without requiring `.env` configuration

## Testing Strategy

### Manual Testing

- Execute the script directly: `./src/koozie.py`
- Execute via uv: `uv run src/koozie.py`
- Verify the ASCII art output is displayed correctly in the terminal
- Test on different terminal sizes and backgrounds to ensure readability

### Edge Cases

- Verify the script handles being run from different directories
- Ensure the script does not depend on any project environment variables
- Verify proper error handling if the script encounters any issues
- Test script execution with different Python versions (3.12+)

## Acceptance Criteria

- ✓ Script is created at `src/koozie.py` with proper executable permissions
- ✓ Script uses `#!/usr/bin/env -S uv run` shebang for consistency with project patterns
- ✓ Script includes PEP 723 inline script dependencies block
- ✓ Script displays "koozie" in fun ASCII art format when executed
- ✓ Script can be executed directly: `./src/koozie.py`
- ✓ Script can be executed via uv: `uv run src/koozie.py`
- ✓ Script produces output without errors
- ✓ Script follows project code style and conventions
- ✓ Script is standalone and does not require `.env` configuration
- ✓ ASCII art output is visually appealing and clearly displays the word "koozie"

## Validation Commands

Execute every command to validate the feature works correctly with zero regressions.

- `python -c "import ast; ast.parse(open('src/koozie.py').read())"` - Verify Python syntax is valid
- `./src/koozie.py` - Execute script directly and verify ASCII art output displays without errors
- `uv run src/koozie.py` - Execute script via uv and verify ASCII art output displays without errors
- `file src/koozie.py` - Verify script has executable permissions and proper shebang
- `uv run pytest` - Run full test suite to ensure no regressions to existing functionality

## Notes

- The script is intentionally lightweight and standalone, requiring no project configuration or environment variables
- Consider using `pyfiglet` library for flexible ASCII art generation or `art` library for pre-built ASCII art styles
- The script serves as a simple utility and demonstration of the project's fun side
- Future enhancements could include command-line arguments for different styles, colors, or additional output options
- This script does not need to be integrated into the existing webhook or testing infrastructure
