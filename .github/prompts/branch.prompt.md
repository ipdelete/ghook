# Branch Command

Create and checkout a new git branch with a descriptive name based on the issue class and work described in the spec document.

## Variables
spec_path: $ARGUMENTS

## Instructions

1. **Read the spec document**
   
   Read the spec file provided in the `spec_path` variable to understand:
   - The type of work (feature, bug fix, chore, refactor, etc.)
   - The core purpose and scope of the work
   - Key aspects that should be reflected in the branch name

2. **Determine the issue class**
   
   Based on the spec content, identify the appropriate issue class:
   - `feature` - New functionality or capabilities
   - `bug` - Bug fixes or corrections
   - `chore` - Maintenance tasks, dependency updates, tooling
   - `refactor` - Code restructuring without changing behavior
   - `docs` - Documentation changes
   - `test` - Test additions or improvements
   - `perf` - Performance improvements

3. **Generate a concise branch name**
   
   Create a branch name following this format: `{class}/{concise-description}`
   
   Guidelines:
   - Use kebab-case for the description (lowercase with hyphens)
   - Keep the description concise but meaningful (2-5 words ideal)
   - Focus on the "what" not the "how"
   - Avoid redundant words like "add", "implement" in feature branches
   - Maximum 50 characters total
   
   Examples:
   - `feature/webhook-logging`
   - `bug/signature-verification`
   - `chore/update-dependencies`
   - `refactor/event-handlers`
   - `docs/api-reference`
   - `test/integration-coverage`

4. **Check if branch already exists**
   
   Verify the branch name doesn't conflict with existing branches:
   ```bash
   git branch -a | grep "branch-name"
   ```
   
   If it exists, append a numeric suffix: `{class}/{description}-2`

5. **Ensure working directory is clean**
   
   Check for uncommitted changes that might cause issues:
   ```bash
   git status --short
   ```
   
   If there are uncommitted changes, inform the user and ask if they want to:
   - Stash changes and proceed
   - Commit changes first
   - Abort branch creation

6. **Create and checkout the branch**
   
   Create the new branch from the current HEAD:
   ```bash
   git checkout -b branch-name
   ```

7. **Confirm success**
   
   Display the current branch and status:
   ```bash
   git branch --show-current
   git status
   ```

## Report

Output only:
- The created branch name
- Confirmation that you're now on the new branch

Example output:
```
Created and checked out branch: feature/webhook-logging
```

## Notes

- The command assumes you want to branch from the current HEAD (typically main/master)
- If you need to branch from a different base, checkout that branch first
- Branch names should be descriptive enough to understand the work at a glance
- Keep branch names concise to make them easy to work with in commands
