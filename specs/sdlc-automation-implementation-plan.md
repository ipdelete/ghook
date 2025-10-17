# Feature: SDLC Automation (Complete ADIL)

## Feature Description
Create a complete SDLC automation tool that orchestrates the full software development lifecycle from feature planning to pull request creation. This tool will execute multiple copilot prompts in sequence, managing state between stages and logging all activities in human-readable markdown files.

## User Story
As a developer
I want to automate the entire SDLC workflow from feature ideation to PR creation
So that I can focus on describing what I want to build while the automation handles the implementation process

## Problem Statement
Currently, developers must manually execute each stage of the SDLC (feature planning, branching, building, documenting, PR creation) separately using individual prompt files. This requires remembering the sequence, manually passing context between stages, and tracking progress across multiple terminal sessions. There's no centralized logging or workflow orchestration.

## Solution Statement
Create a new `sdlc.py` script that mirrors `adil.py` but executes multiple stages in sequence. Each stage will invoke copilot with the appropriate prompt file, capture outputs, pass context between stages, and log all activities to timestamped markdown files in a unique workflow folder.

## Relevant Files

### Existing Files
- `src/adil.py` - Template for copilot CLI invocation pattern
- `.github/prompts/feature.prompt.md` - Feature planning stage
- `.github/prompts/branch.prompt.md` - Branch creation stage
- `.github/prompts/build.prompt.md` - Implementation stage
- `.github/prompts/document.prompt.md` - Documentation stage
- `.github/prompts/pr.prompt.md` - Pull request stage
- `docs/prime.md` - Project context

### New Files
- `src/sdlc.py` - Main SDLC automation script with workflow orchestration
- `logs/<workflow-id>/logfile_<timestamp>.md` - Workflow execution log

## Implementation Plan

### Phase 1: Foundation
Create the core data structures and utilities:
- Workflow ID generation (8 character alphanumeric)
- Logging infrastructure with markdown formatting
- Command builder class for constructing copilot commands
- Response parser class for extracting spec files and other outputs

### Phase 2: Core Implementation
Implement the workflow stages:
- Feature stage: Run feature planning prompt with user input
- Branch stage: Create branch using spec from feature stage
- Build stage: Implement feature using spec from feature stage
- Document stage: Update documentation
- PR stage: Create pull request

### Phase 3: Integration
Connect the stages into a cohesive workflow:
- Stage orchestration with proper sequencing
- Context passing between stages (spec file path)
- Error handling and graceful degradation
- Progress reporting and logging

## Step by Step Tasks

### Step 1: Create Workflow ID Generator
- Add function to generate 8-character alphanumeric IDs
- Use random or timestamp-based approach for uniqueness
- Make it collision-resistant

### Step 2: Create Logging Infrastructure
- Create function to initialize log directory structure
- Implement markdown log writer with human-readable formatting
- Add timestamp formatting for log filenames
- Create log entry functions for stages, commands, and outputs

### Step 3: Create Command Builder Class
- Implement `CopilotCommand` class
- Add methods to construct copilot command arrays
- Support different prompt types (with/without prime context)
- Handle argument substitution

### Step 4: Create Response Parser Class
- Implement `StageResponse` class
- Add parser for feature stage output (extract spec file path)
- Store metadata like stage name, timestamp, success status
- Capture stdout and stderr

### Step 5: Implement Feature Stage
- Create function to run feature planning prompt
- Pass user input to feature.prompt.md
- Capture spec file path from output
- Log command and response

### Step 6: Implement Branch Stage
- Create function to run branch prompt
- Pass spec file path from feature stage
- Capture branch name from output
- Log command and response

### Step 7: Implement Build Stage
- Create function to run build prompt
- Pass spec file path from feature stage
- Capture build output
- Log command and response

### Step 8: Implement Document Stage
- Create function to run document prompt
- Include prime context
- Capture documentation changes
- Log command and response

### Step 9: Implement PR Stage
- Create function to run PR prompt
- Include prime context
- Capture PR URL and number
- Log command and response

### Step 10: Implement Workflow Orchestrator
- Create main orchestration function
- Run stages in sequence: feature → branch → build → document → PR
- Pass context between stages
- Handle errors gracefully
- Log workflow start and completion

### Step 11: Add CLI Interface
- Parse command-line arguments (user input)
- Display usage information
- Initialize workflow
- Run orchestrator
- Display summary

### Step 12: Test the Implementation
- Run with sample feature request
- Verify log file creation
- Validate stage execution
- Check context passing between stages
- Confirm error handling

### Step 13: Validate with Existing Tests
- Run `uv run pytest -v` to ensure no regressions
- Verify Python syntax: `python -c "import ast; ast.parse(open('src/sdlc.py').read())"`
- Test with real feature input

## Testing Strategy

### Manual Testing
1. Run with simple feature: `./src/sdlc.py "add timestamp logging to webhook events"`
2. Verify log directory creation with correct ID format
3. Check log file content for readability and completeness
4. Validate spec file is created and passed correctly
5. Confirm all stages execute in order
6. Verify PR is created successfully

### Edge Cases
- Empty user input (should show usage)
- Very long user input (should handle gracefully)
- Copilot CLI not available (should fail with clear message)
- Stage failures (should log error and potentially continue or abort)
- Spec file not found between stages (should handle gracefully)
- Git repository not clean (branch stage should handle)

## Acceptance Criteria
- [x] Script generates unique 8-character workflow IDs
- [x] Log directory is created in `logs/<workflow-id>/`
- [x] Log file uses format `logfile_YYYY-MM-DD_HH-MM-SS.md`
- [x] Log file is human-readable markdown with clear sections
- [x] `CopilotCommand` class builds correct command strings
- [x] `StageResponse` class captures and parses outputs
- [x] Feature stage runs and extracts spec file path
- [x] Branch stage receives spec file and creates branch
- [x] Build stage receives spec file and implements feature
- [x] Document stage runs with prime context
- [x] PR stage runs with prime context and creates PR
- [x] Each stage logs its command and output
- [x] Workflow executes stages in correct order
- [x] Context is passed correctly between stages
- [x] Script displays clear progress and summary

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

```bash
# Verify Python syntax
python -c "import ast; ast.parse(open('src/sdlc.py').read())"

# Make script executable
chmod +x src/sdlc.py

# Test with sample feature (may require manual intervention for copilot prompts)
./src/sdlc.py "add a simple hello endpoint to webhook server"

# Verify log directory was created
ls -la logs/

# Check log file content
find logs/ -name "logfile_*.md" -type f -exec head -20 {} \;

# Verify existing tests still pass
uv run pytest -v

# Verify sdlc.py can be run with uv
uv run src/sdlc.py --help || echo "Help command test"
```

## Notes
- This is a complex orchestration tool that wraps multiple copilot CLI calls
- The workflow is linear: feature → branch → build → document → PR
- Each stage depends on context from previous stages (especially the spec file)
- Error handling is critical since copilot may fail or return unexpected output
- The log files serve as both audit trail and debugging tool
- Future enhancements could include: parallel stage execution, stage skipping, resume from checkpoint, configuration file support
- Consider adding a `--dry-run` flag to show what would be executed without actually running
- Consider adding stage selection flags like `--stages feature,branch` to run subset of stages
- The 8-character ID should be sufficient for collision avoidance in typical usage
