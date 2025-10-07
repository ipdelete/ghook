# Cleanup Command

Clean up after a PR has been merged by switching to the default branch, pulling latest changes, and deleting the merged feature branch (both locally and remotely).

## Instructions

1. **Check current branch**
   
   Verify which branch you're on:
   ```bash
   git branch --show-current
   ```
   
   If there are uncommitted changes, inform the user and ask if they want to:
   - Commit changes first
   - Stash changes
   - Abort cleanup

2. **Determine the default branch**
   
   Get the default branch name (usually `main` or `master`):
   ```bash
   git symbolic-ref refs/remotes/origin/HEAD | sed 's@^refs/remotes/origin/@@'
   ```
   
   If this fails, check both `main` and `master`:
   ```bash
   git rev-parse --verify main 2>/dev/null || git rev-parse --verify master
   ```

3. **Store the feature branch name**
   
   Before switching, save the current branch name for deletion later:
   ```bash
   FEATURE_BRANCH=$(git branch --show-current)
   ```
   
   If already on the default branch, inform the user that no cleanup is needed.

4. **Switch to default branch**
   
   Switch to the default branch:
   ```bash
   git checkout main
   # or
   git checkout master
   ```

5. **Pull latest changes**
   
   Update the default branch with latest changes from remote:
   ```bash
   git pull
   ```

6. **Delete local feature branch**
   
   Delete the feature branch locally:
   ```bash
   git branch -d <feature-branch-name>
   ```
   
   If the branch hasn't been merged, use `-D` flag (force delete):
   ```bash
   git branch -D <feature-branch-name>
   ```
   
   Ask the user for confirmation before force deleting.

7. **Delete remote feature branch**
   
   Delete the feature branch from the remote repository:
   ```bash
   git push origin --delete <feature-branch-name>
   ```
   
   If the remote branch has already been deleted (common after PR merge on GitHub), this will fail gracefully - log the message and continue.

8. **Confirm cleanup**
   
   Display the final status:
   ```bash
   git status
   git branch -a | grep <feature-branch-name>
   ```
   
   Verify the branch is deleted both locally and remotely.

## Report

Output a summary of cleanup actions:
- Default branch switched to
- Number of commits pulled
- Feature branch deleted (local and remote)
- Current status

Example output:
```
Switched to: master
Pulled 5 commits from remote
Deleted branch: feature/repository-cloning (local and remote)
✅ Cleanup complete
```

## Notes

- This command is intended to be run after a PR has been merged
- The feature branch will be deleted both locally and remotely
- If the branch hasn't been merged, you'll be asked to confirm force deletion
- If the remote branch is already deleted (GitHub auto-delete), the error is ignored
- Any uncommitted changes should be handled before running this command
- You cannot delete a branch you're currently on (command switches to default branch first)
