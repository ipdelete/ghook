# Document Command

Document changes made in the current branch by updating README.md, GitHub instructions, and CHANGELOG.md with relevant information about new features, fixes, or changes.

## Instructions

1. **Analyze changes in the current branch**
   
   Gather information about what was changed:
   ```bash
   git branch --show-current
   git log origin/master..HEAD --format="%s%n%b"
   git diff origin/master...HEAD --stat
   git diff origin/master...HEAD --name-only
   ```

2. **Find associated spec document**
   
   Look for related spec files that describe the feature:
   ```bash
   ls -1 specs/ | grep -i "keywords-from-branch"
   ```
   
   If found, read the spec to understand the feature's purpose and details.

3. **Read current documentation**
   
   Review existing documentation to understand structure and style:
   - Read `README.md` to see current quick start and testing sections
   - Read `.github/github-instructions.md` to see current workflow documentation
   - Read `CHANGELOG.md` to see changelog format (if it exists)

4. **Update README.md**
   
   Add or update sections based on changes:
   - If new features affect quick start, update the Quick Start section
   - If new configuration is added, document it in the appropriate section
   - If new testing scenarios are added, update the Testing section
   - Keep README focused on the essential "getting started" information
   - Maintain existing formatting and style

5. **Update .github/github-instructions.md**
   
   Add detailed technical documentation:
   - Add new features to relevant sections (Setup, Development Workflow, Testing, etc.)
   - Document new environment variables in the appropriate configuration section
   - Add troubleshooting tips for common issues related to changes
   - Update code examples if APIs or workflows have changed
   - Maintain the comprehensive technical documentation style

6. **Update CHANGELOG.md**
   
   Add an entry for the changes following Keep a Changelog format:
   
   ```markdown
   ## [Unreleased]
   
   ### Added
   - New features or capabilities added
   
   ### Changed
   - Changes to existing functionality
   
   ### Fixed
   - Bug fixes
   
   ### Removed
   - Removed features or functionality
   ```
   
   Guidelines:
   - Add entries to the `[Unreleased]` section at the top
   - Use past tense for entries (e.g., "Added webhook logging")
   - Group changes by type (Added, Changed, Fixed, Removed)
   - Be concise but descriptive
   - Include important technical details users need to know
   - If CHANGELOG.md is empty, create the initial structure with an Unreleased section

7. **Verify documentation quality**
   
   Review the updates:
   - Ensure all new features are documented
   - Check that code examples are accurate
   - Verify configuration options are explained
   - Ensure formatting is consistent
   - Check that links are valid (if any were added)

## Report

Output a summary of documentation updates:
- Which files were updated
- What sections were added or modified
- Key points documented

Example:
```
Updated documentation for repository cloning feature:

README.md:
- Added cloning configuration to Quick Start

.github/github-instructions.md:
- Added "Repository Cloning" section under Development Workflow
- Documented CLONE_REPOS, CLONE_BASE_DIR, and CLONE_UPDATE_EXISTING environment variables
- Added troubleshooting section for gh CLI issues

CHANGELOG.md:
- Added "Repository Cloning on Issue Creation" to Unreleased section
```

## Notes

- Focus on user-facing documentation, not internal code comments
- README.md should be concise for quick reference
- .github/github-instructions.md should be comprehensive for contributors
- CHANGELOG.md should follow semantic versioning principles
- If changes are internal refactoring with no user impact, update may be minimal
- Always maintain existing documentation structure and style
- Consider the audience: beginners for README, developers for github-instructions
