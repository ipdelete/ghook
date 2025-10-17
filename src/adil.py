#!/usr/bin/env -S uv run
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

import subprocess
import sys


def main():
    """ADIL: AI Developer Inner-Loop utility.
    Integrates GitHub Copilot CLI with project context from docs/prime.md.
    Constructs a combined prompt and invokes copilot with appropriate flags.
    """
    if len(sys.argv) < 2:
        print("Usage: ./src/adil.py <prompt>", file=sys.stderr)
        print("       uv run src/adil.py <prompt>", file=sys.stderr)
        print("\nExample: ./src/adil.py \"add support for pull request events\"", file=sys.stderr)
        sys.exit(1)
    
    user_prompt = " ".join(sys.argv[1:])
    full_prompt = f"follow docs/prime.md and {user_prompt}"
    
    try:
        subprocess.run(
            ["copilot", "-p", full_prompt, "--allow-all-tools", "--model", "claude-haiku-4.5"],
            check=True
        )
    except FileNotFoundError:
        print("Error: copilot command not found. Please ensure GitHub Copilot CLI is installed.", file=sys.stderr)
        sys.exit(1)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


if __name__ == "__main__":
    main()
