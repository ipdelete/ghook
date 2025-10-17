#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""SDLC Automation Tool

Orchestrates the complete software development lifecycle from feature planning
to pull request creation. Executes multiple copilot prompts in sequence,
managing state between stages and logging all activities.

Usage:
    ./src/sdlc.py "feature description"
    uv run src/sdlc.py "feature description"

Example:
    ./src/sdlc.py "add timestamp logging to webhook events"
"""

import random
import string
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def generate_workflow_id() -> str:
    """Generate a unique 8-character alphanumeric workflow ID.
    
    Returns:
        An 8-character string combining timestamp and random characters
    """
    # Use timestamp prefix for ordering + random suffix for uniqueness
    timestamp_part = datetime.now().strftime("%H%M%S")[:4]
    random_part = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))
    return f"{timestamp_part}{random_part}"


def init_log_directory(workflow_id: str) -> Path:
    """Initialize the log directory structure for a workflow.
    
    Args:
        workflow_id: The unique workflow identifier
        
    Returns:
        Path to the created workflow directory
    """
    workflow_dir = Path("logs") / workflow_id
    workflow_dir.mkdir(parents=True, exist_ok=True)
    return workflow_dir


def create_log_file(workflow_dir: Path) -> Path:
    """Create a timestamped log file.
    
    Args:
        workflow_dir: Directory where the log file should be created
        
    Returns:
        Path to the created log file
    """
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = workflow_dir / f"logfile_{timestamp}.md"
    return log_file


class LogWriter:
    """Writes human-readable markdown logs for workflow execution."""
    
    def __init__(self, log_file: Path):
        self.log_file = log_file
        self.log_file.touch()
        
    def write_header(self, workflow_id: str, user_input: str):
        """Write the log file header."""
        with open(self.log_file, 'a') as f:
            f.write(f"# SDLC Workflow Log\n\n")
            f.write(f"**Workflow ID:** {workflow_id}\n\n")
            f.write(f"**Started:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**User Input:** {user_input}\n\n")
            f.write("---\n\n")
    
    def write_stage_start(self, stage_name: str):
        """Write a stage start marker."""
        with open(self.log_file, 'a') as f:
            f.write(f"## Stage: {stage_name}\n\n")
            f.write(f"**Started:** {datetime.now().strftime('%H:%M:%S')}\n\n")
    
    def write_command(self, command: List[str]):
        """Write the command being executed."""
        with open(self.log_file, 'a') as f:
            f.write(f"**Command:**\n```bash\n{' '.join(command)}\n```\n\n")
    
    def write_output(self, stdout: str, stderr: str, success: bool):
        """Write command output."""
        with open(self.log_file, 'a') as f:
            f.write(f"**Status:** {'✓ Success' if success else '✗ Failed'}\n\n")
            if stdout:
                f.write(f"**Output:**\n```\n{stdout}\n```\n\n")
            if stderr:
                f.write(f"**Errors:**\n```\n{stderr}\n```\n\n")
    
    def write_stage_end(self, stage_name: str, success: bool):
        """Write a stage end marker."""
        with open(self.log_file, 'a') as f:
            status = "✓ Completed" if success else "✗ Failed"
            f.write(f"**{stage_name} {status}** at {datetime.now().strftime('%H:%M:%S')}\n\n")
            f.write("---\n\n")
    
    def write_footer(self, success: bool):
        """Write the log file footer."""
        with open(self.log_file, 'a') as f:
            f.write(f"## Workflow Summary\n\n")
            f.write(f"**Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Status:** {'✓ Success' if success else '✗ Failed'}\n\n")


class CopilotCommand:
    """Builder class for constructing copilot CLI commands."""
    
    def __init__(self):
        self.base_command = ["copilot"]
        self.model = "claude-haiku-4.5"
        
    def build_feature_command(self, user_input: str) -> List[str]:
        """Build command for feature planning stage.
        
        Args:
            user_input: The user's feature description
            
        Returns:
            Command array for subprocess execution
        """
        prompt = f"follow @.github/prompts/feature.prompt.md {user_input}"
        return self.base_command + [
            "-p", prompt,
            "--allow-all-tools",
            "--model", self.model
        ]
    
    def build_branch_command(self, spec_path: str) -> List[str]:
        """Build command for branch creation stage.
        
        Args:
            spec_path: Path to the specification file
            
        Returns:
            Command array for subprocess execution
        """
        prompt = f"follow @.github/prompts/branch.prompt.md {spec_path}"
        return self.base_command + [
            "-p", prompt,
            "--allow-all-tools",
            "--model", self.model
        ]
    
    def build_build_command(self, spec_path: str) -> List[str]:
        """Build command for implementation stage.
        
        Args:
            spec_path: Path to the specification file
            
        Returns:
            Command array for subprocess execution
        """
        prompt = f"follow @.github/prompts/build.prompt.md {spec_path}"
        return self.base_command + [
            "-p", prompt,
            "--allow-all-tools",
            "--model", self.model
        ]
    
    def build_document_command(self) -> List[str]:
        """Build command for documentation stage.
        
        Returns:
            Command array for subprocess execution
        """
        prompt = "follow docs/prime.md and @.github/prompts/document.prompt.md"
        return self.base_command + [
            "-p", prompt,
            "--allow-all-tools",
            "--model", self.model
        ]
    
    def build_pr_command(self) -> List[str]:
        """Build command for pull request stage.
        
        Returns:
            Command array for subprocess execution
        """
        prompt = "follow docs/prime.md and @.github/prompts/pr.prompt.md"
        return self.base_command + [
            "-p", prompt,
            "--allow-all-tools",
            "--model", self.model
        ]


@dataclass
class StageResponse:
    """Captures and parses the response from a workflow stage."""
    
    stage_name: str
    success: bool
    stdout: str = ""
    stderr: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    spec_path: Optional[str] = None
    branch_name: Optional[str] = None
    
    def parse_spec_path(self) -> Optional[str]:
        """Extract spec file path from feature stage output.

        Returns:
            Path to the created specification file, or None if not found
        """
        import re

        # Look for specs/*.md pattern in the output
        # Handles various formats: specs/file.md, `specs/file.md`, at specs/file.md, etc.
        # Pattern allows for hyphens, underscores, and alphanumeric characters in filename
        pattern = r'`?(specs/[\w-]+\.md)`?'
        matches = re.findall(pattern, self.stdout)

        if matches:
            # Return the first match found, stripped of any backticks
            spec_path = matches[0].strip('`"\'')
            self.spec_path = spec_path
            return self.spec_path

        # Fallback: Look for lines containing "specs/" and ending with ".md"
        for line in self.stdout.split('\n'):
            line = line.strip().strip('`"\'')
            if 'specs/' in line and '.md' in line:
                # Extract just the path part using regex
                match = re.search(r'(specs/[\w-]+\.md)', line)
                if match:
                    self.spec_path = match.group(1)
                    return self.spec_path

        return None
    
    def parse_branch_name(self) -> Optional[str]:
        """Extract branch name from branch stage output.

        Returns:
            The created branch name, or None if not found
        """
        # Look for "Created and checked out branch:" or similar patterns
        for line in self.stdout.split('\n'):
            line = line.strip()
            if 'branch:' in line.lower():
                # Extract the branch name after the colon
                parts = line.split(':', 1)
                if len(parts) == 2:
                    # Strip whitespace and markdown formatting (backticks, quotes)
                    branch_name = parts[1].strip().strip('`"\'')
                    self.branch_name = branch_name
                    return self.branch_name
        return None


class WorkflowOrchestrator:
    """Orchestrates the execution of SDLC workflow stages."""
    
    def __init__(self, workflow_id: str, user_input: str):
        self.workflow_id = workflow_id
        self.user_input = user_input
        self.workflow_dir = init_log_directory(workflow_id)
        self.log_file = create_log_file(self.workflow_dir)
        self.log_writer = LogWriter(self.log_file)
        self.command_builder = CopilotCommand()
        self.spec_path: Optional[str] = None
        self.branch_name: Optional[str] = None
        
    def run_stage(self, stage_name: str, command: List[str]) -> StageResponse:
        """Execute a single workflow stage.
        
        Args:
            stage_name: Name of the stage being executed
            command: Command to execute
            
        Returns:
            StageResponse object with execution results
        """
        print(f"\n{'='*60}")
        print(f"Stage: {stage_name}")
        print(f"{'='*60}\n")
        
        self.log_writer.write_stage_start(stage_name)
        self.log_writer.write_command(command)
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )
            
            success = result.returncode == 0
            response = StageResponse(
                stage_name=stage_name,
                success=success,
                stdout=result.stdout,
                stderr=result.stderr
            )
            
            self.log_writer.write_output(result.stdout, result.stderr, success)
            self.log_writer.write_stage_end(stage_name, success)
            
            return response
            
        except Exception as e:
            error_msg = f"Exception during stage execution: {str(e)}"
            print(f"Error: {error_msg}", file=sys.stderr)
            
            response = StageResponse(
                stage_name=stage_name,
                success=False,
                stderr=error_msg
            )
            
            self.log_writer.write_output("", error_msg, False)
            self.log_writer.write_stage_end(stage_name, False)
            
            return response
    
    def run_feature_stage(self) -> StageResponse:
        """Execute the feature planning stage."""
        command = self.command_builder.build_feature_command(self.user_input)
        response = self.run_stage("Feature Planning", command)

        if response.success:
            self.spec_path = response.parse_spec_path()
            if self.spec_path:
                print(f"✓ Spec file created: {self.spec_path}")
            else:
                print("⚠ Warning: Could not extract spec file path from output")

            # Validate that only planning occurred (no implementation)
            self._validate_planning_only(response)

        return response

    def _validate_planning_only(self, response: StageResponse) -> None:
        """Validate that the feature stage only created the spec file, not implementation.

        Args:
            response: The response from the feature planning stage
        """
        import re

        # Look for indicators that implementation occurred
        implementation_indicators = [
            r'Create src/[\w.-]+\.py',
            r'✓ Create src/',
            r'chmod \+x.*src/',
            r'Make.*executable',
            r'Run.*script',
            r'Execute.*command',
        ]

        warnings = []
        for pattern in implementation_indicators:
            if re.search(pattern, response.stdout, re.IGNORECASE):
                warnings.append(f"Detected potential implementation activity: matched pattern '{pattern}'")

        if warnings:
            print("\n⚠️  WARNING: Feature planning stage may have performed implementation:")
            for warning in warnings:
                print(f"   - {warning}")
            print("   The feature stage should ONLY create the spec file.")
            print("   Implementation should happen in the BUILD stage.")
            print("   This may cause issues with the workflow.\n")
    
    def run_branch_stage(self) -> StageResponse:
        """Execute the branch creation stage."""
        if not self.spec_path:
            print("⚠ Warning: No spec path available, skipping branch stage")
            return StageResponse(
                stage_name="Branch Creation",
                success=False,
                stderr="No spec path available from feature stage"
            )
        
        command = self.command_builder.build_branch_command(self.spec_path)
        response = self.run_stage("Branch Creation", command)
        
        if response.success:
            self.branch_name = response.parse_branch_name()
            if self.branch_name:
                print(f"✓ Branch created: {self.branch_name}")
            else:
                print("⚠ Warning: Could not extract branch name from output")
        
        return response
    
    def run_build_stage(self) -> StageResponse:
        """Execute the implementation stage."""
        if not self.spec_path:
            print("⚠ Warning: No spec path available, skipping build stage")
            return StageResponse(
                stage_name="Implementation",
                success=False,
                stderr="No spec path available from feature stage"
            )
        
        command = self.command_builder.build_build_command(self.spec_path)
        response = self.run_stage("Implementation", command)
        
        if response.success:
            print(f"✓ Implementation completed")
        
        return response
    
    def run_document_stage(self) -> StageResponse:
        """Execute the documentation stage."""
        command = self.command_builder.build_document_command()
        response = self.run_stage("Documentation", command)
        
        if response.success:
            print(f"✓ Documentation updated")
        
        return response
    
    def run_pr_stage(self) -> StageResponse:
        """Execute the pull request creation stage."""
        command = self.command_builder.build_pr_command()
        response = self.run_stage("Pull Request", command)
        
        if response.success:
            print(f"✓ Pull request created")
        
        return response
    
    def run_workflow(self) -> bool:
        """Execute the complete SDLC workflow.
        
        Returns:
            True if all stages completed successfully, False otherwise
        """
        print(f"\n{'#'*60}")
        print(f"SDLC Workflow - ID: {self.workflow_id}")
        print(f"{'#'*60}\n")
        print(f"User Input: {self.user_input}")
        print(f"Log File: {self.log_file}")
        
        self.log_writer.write_header(self.workflow_id, self.user_input)
        
        # Stage 1: Feature Planning
        feature_response = self.run_feature_stage()
        if not feature_response.success:
            print(f"\n✗ Workflow failed at Feature Planning stage")
            self.log_writer.write_footer(False)
            return False
        
        # Stage 2: Branch Creation
        branch_response = self.run_branch_stage()
        if not branch_response.success:
            print(f"\n✗ Workflow failed at Branch Creation stage")
            self.log_writer.write_footer(False)
            return False
        
        # Stage 3: Implementation
        build_response = self.run_build_stage()
        if not build_response.success:
            print(f"\n✗ Workflow failed at Implementation stage")
            self.log_writer.write_footer(False)
            return False
        
        # Stage 4: Documentation
        document_response = self.run_document_stage()
        if not document_response.success:
            print(f"\n⚠ Warning: Documentation stage failed, continuing...")
        
        # Stage 5: Pull Request
        pr_response = self.run_pr_stage()
        if not pr_response.success:
            print(f"\n⚠ Warning: Pull Request stage failed")
            # Don't fail the workflow if PR creation fails
        
        # Workflow complete
        success = (feature_response.success and 
                  branch_response.success and 
                  build_response.success)
        
        self.log_writer.write_footer(success)
        
        print(f"\n{'#'*60}")
        print(f"Workflow {'✓ Completed Successfully' if success else '✗ Failed'}")
        print(f"{'#'*60}\n")
        print(f"Log file: {self.log_file}")
        
        if self.spec_path:
            print(f"Spec file: {self.spec_path}")
        if self.branch_name:
            print(f"Branch: {self.branch_name}")
        
        return success


def main():
    """Main entry point for SDLC automation tool."""
    if len(sys.argv) < 2:
        print("Usage: ./src/sdlc.py <feature-description>", file=sys.stderr)
        print("       uv run src/sdlc.py <feature-description>", file=sys.stderr)
        print("\nExample: ./src/sdlc.py \"add timestamp logging to webhook events\"", file=sys.stderr)
        sys.exit(1)
    
    user_input = " ".join(sys.argv[1:])
    
    # Check if copilot CLI is available
    try:
        subprocess.run(
            ["copilot", "--version"],
            capture_output=True,
            check=True
        )
    except FileNotFoundError:
        print("Error: copilot command not found.", file=sys.stderr)
        print("Please ensure GitHub Copilot CLI is installed and authenticated.", file=sys.stderr)
        print("Install: pip install github-copilot-cli", file=sys.stderr)
        print("Authenticate: copilot auth login", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError:
        print("Error: copilot command failed.", file=sys.stderr)
        print("Please ensure GitHub Copilot CLI is authenticated.", file=sys.stderr)
        print("Authenticate: copilot auth login", file=sys.stderr)
        sys.exit(1)
    
    # Generate workflow ID and run orchestrator
    workflow_id = generate_workflow_id()
    orchestrator = WorkflowOrchestrator(workflow_id, user_input)
    
    try:
        success = orchestrator.run_workflow()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nWorkflow interrupted by user", file=sys.stderr)
        orchestrator.log_writer.write_footer(False)
        sys.exit(130)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}", file=sys.stderr)
        orchestrator.log_writer.write_footer(False)
        sys.exit(1)


if __name__ == "__main__":
    main()
