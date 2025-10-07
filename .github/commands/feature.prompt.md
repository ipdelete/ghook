# Feature Planning

Create a new plan to implement a feature using the exact specified markdown `Plan Format`. Follow the `Instructions` to create the plan and use the `Relevant Files` to focus on the right files.

## Variables
spec_file: $1

## Instructions

- IMPORTANT: You're writing a plan to implement a net new feature based on the specification file that will add value to the application.
- IMPORTANT: The specification describes the feature that will be implemented. Remember we're not implementing the feature, we're creating an actionable implementation plan based on the `Plan Format` below.
- Create the plan in the `specs/` directory with filename: `{spec_file_basename}-implementation-plan.md`
  - Replace `{spec_file_basename}` with the base name of the spec file without extension (e.g., "repository-cloning-feature" becomes "repository-cloning-feature-implementation-plan.md")
- Use the `Plan Format` below to create the plan.
- Research the codebase to understand existing patterns, architecture, and conventions before planning the feature.
- IMPORTANT: Replace every <placeholder> in the `Plan Format` with the requested value. Add as much detail as needed to implement the feature successfully.
- Use your reasoning: THINK HARD about the feature requirements, design, and implementation approach.
- Follow existing patterns and conventions in the codebase. Don't reinvent the wheel.
- Design for extensibility and maintainability.
- This project uses `uv` for Python package management and running scripts.
- IMPORTANT: Python files in `src/` use uv's inline script dependencies (PEP 723):
  - Scripts have inline dependencies declared in `# /// script` blocks (see webhook.py for example)
  - To run scripts: `./src/webhook.py` or `uv run src/webhook.py`
  - To add dependencies to a script: `uv add --script src/webhook.py <package>`
  - All new Python scripts should follow this pattern with `#!/usr/bin/env -S uv run` shebang
- Keep it simple and Pythonic.
- Respect requested files in the `Relevant Files` section.
- Start your research by reading the `README.md` file.

## Relevant Files

Focus on the following files:
- `README.md` - Contains the project overview and instructions.
- `src/**` - Contains the Python codebase.
- `scripts/**` - Contains bash scripts.
- `specs/**` - Contains feature specifications.
- `pyproject.toml` - Contains project dependencies and configuration.
- `.env.sample` - Contains sample environment configuration.

Ignore all other files in the codebase.

## Plan Format

```md
# Feature: <feature name>

## Metadata
spec_file: `{spec_file}`

## Feature Description
<describe the feature in detail, including its purpose and value to users>

## User Story
As a <type of user>
I want to <action/goal>
So that <benefit/value>

## Problem Statement
<clearly define the specific problem or opportunity this feature addresses>

## Solution Statement
<describe the proposed solution approach and how it solves the problem>

## Relevant Files
Use these files to implement the feature:

<find and list the files that are relevant to the feature and describe why they are relevant in bullet points. If there are new files that need to be created to implement the feature, list them in an h3 'New Files' section.>

## Implementation Plan
### Phase 1: Foundation
<describe the foundational work needed before implementing the main feature>

### Phase 2: Core Implementation
<describe the main implementation work for the feature>

### Phase 3: Integration
<describe how the feature will integrate with existing functionality>

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

<list step by step tasks as h3 headers plus bullet points. Use as many h3 headers as needed to implement the feature. Order matters, start with the foundational shared changes required then move on to the specific implementation. Include testing throughout the implementation process.>

<Your last step should be running the `Validation Commands` to validate the feature works correctly with zero regressions.>

## Testing Strategy
### Manual Testing
<describe manual tests needed to validate the feature>

### Edge Cases
<list edge cases that need to be tested>

## Acceptance Criteria
<list specific, measurable criteria that must be met for the feature to be considered complete>

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

<list commands you'll use to validate with 100% confidence the feature is implemented correctly with zero regressions. Every command must execute without errors so be specific about what you want to run to validate the feature works as expected. Include commands to test the feature end-to-end.>

Example commands:
- `./src/webhook.py` or `uv run src/webhook.py` - Start the webhook server and verify it starts without errors
- `gh --version` - Verify gh CLI is available (if required by feature)
- `uv add --script src/webhook.py <package>` - Add a dependency to the webhook.py uv script
- `python -c "import ast; ast.parse(open('src/webhook.py').read())"` - Verify Python syntax is valid

## Notes
<optionally list any additional notes, future considerations, or context that are relevant to the feature that will be helpful to the developer>
```

## Feature
Read the specification file from the `spec_file` variable and extract the feature details.

## Report

- IMPORTANT: Return exclusively the path to the plan file created and nothing else.
