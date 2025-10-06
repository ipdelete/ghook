# Ship Command

This command stages all changes, commits them with an automatically generated message, and pushes to the remote repository.

## Instructions

1. **Check current git status**
   
   First, review what changes are present:
   ```bash
   git status
   ```

2. **Analyze the changes**
   
   Review the diff to understand what was changed:
   ```bash
   git diff --cached --stat
   git diff --stat
   ```

3. **Stage all changes**
   
   Add all modified and new files to staging:
   ```bash
   git add -A
   ```

4. **Generate and commit with relevant message**
   
   Analyze the staged changes and create a descriptive commit message that summarizes:
   - What files were added, modified, or deleted
   - The purpose or nature of the changes
   - Use conventional commit format when appropriate (feat:, fix:, docs:, etc.)
   
   Then commit with the generated message:
   ```bash
   git commit -m "generated message based on changes"
   ```

5. **Push to remote**
   
   Push the committed changes to the remote repository:
   ```bash
   git push
   ```

6. **Confirm success**
   
   Display the final git status and confirm the push was successful:
   ```bash
   git status
   ```

## Usage

Simply invoke `/ship` and the command will automatically analyze changes and generate an appropriate commit message without prompting.
