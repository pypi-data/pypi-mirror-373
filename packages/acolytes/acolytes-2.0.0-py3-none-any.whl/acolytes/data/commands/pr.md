---
command: pr
description: ♾️  Create pull request with analysis | No parameters
---

# 🔀 Pull Request Creation Command

Professional pull request creation with intelligent branch management and automated description generation.

## Usage

```bash
/pr                     # Create PR with analysis and confirmations
```

## Execution Flow

### Phase 1: Pre-flight Checks

```yaml
VALIDATIONS:
  - Check for uncommitted changes
  - Verify current branch is not main/master
  - Check if branch already exists on remote
  - Verify GitHub CLI (gh) is installed and authenticated

BRANCH_HANDLING:
  Current branch is main:
    - Create new feature branch
    - Move changes to new branch

  Current branch is feature:
    - Use existing branch
    - Push if not already pushed
```

### Phase 2: Analyze Changes

```yaml
ANALYSIS:
  # Get complete diff from base branch
  - mcp__server-git__git_diff with base branch
  - Identify all commits since branch diverged
  - Group changes by module/domain

PARALLEL_AGENT_INVOCATION:
  specialist-git:
    - Generate PR title
    - Create structured description
    - Suggest reviewers based on changes

  affected-module-agents:
    - Provide context about changes
    - Impact analysis
    - Testing suggestions

  changelog-specialist:
    - Determine version impact
    - Prepare release notes if applicable
```

### Phase 3: PR Creation

```yaml
PR_COMPONENTS:
  Title:
    - Format: "type(scope): description"
    - Example: "feat(auth): add OAuth2 provider support"

  Description:
    ## Summary
    - Bullet points of main changes
    - Why these changes were made

    ## Changes
    - Detailed list by module
    - Technical implementation notes

    ## Testing
    - How to test the changes
    - What was tested

    ## Impact
    - Breaking changes (if any)
    - Performance implications
    - Security considerations

    ## Checklist
    - [ ] Tests pass
    - [ ] Documentation updated
    - [ ] Lint clean
    - [ ] Ready for review

  Labels:
    - Auto-detect: enhancement, bug, documentation, etc.
    - Size: XS, S, M, L, XL based on changes

  Reviewers:
    - Based on CODEOWNERS if exists
    - Suggest based on module expertise
```

### Phase 4: GitHub Operations

```yaml
GITHUB_CLI_COMMANDS:
  # Push to remote if needed
  git push -u origin <branch-name>

  # Create PR with gh CLI
  gh pr create \
    --title "<title>" \
    --body "<description>" \
    --base <base-branch> \
    --head <current-branch> \
    --label "<labels>" \
    [--draft if specified]

  # Link to issues if mentioned
  gh pr edit <pr-number> --add-issue <issue-numbers>
```

## Command Implementation

```javascript
async function createPullRequest() {
  const baseBranch = "main"; // Always use main as base

  // Phase 1: Pre-flight checks
  const status = (await mcp__server) - git__git_status();

  if (status.hasUncommittedChanges) {
    return abort("Commit changes before creating PR");
  }

  const currentBranch = await getCurrentBranch();

  if (currentBranch === "main" || currentBranch === "master") {
    const newBranch = await promptBranchName();
    (await mcp__server) - git__git_create_branch(newBranch);
  }

  // Phase 2: Analysis
  const diff = (await mcp__server) - git__git_diff(`${baseBranch}...HEAD`);
  const commits =
    (await mcp__server) -
    git__git_log({
      range: `${baseBranch}..HEAD`,
    });

  // Parallel agent analysis
  const tasks = [
    "@specialist-git generate PR title and description",
    "@changelog-specialist analyze version impact",
    ...getAffectedModuleAgents(diff).map(
      (agent) => `@${agent} provide PR context`
    ),
  ];

  const results = await executeParallelTasks(tasks);

  // Phase 3: Build PR
  const pr = {
    title: results.git.title,
    body: buildPRDescription(results),
    labels: detectLabels(diff, commits),
  };

  // Show preview
  console.log("PR Preview:", pr);

  if (!(await confirm("Create this PR?"))) {
    return abort("PR creation cancelled");
  }

  // Phase 4: Create PR
  await bash(`git push -u origin ${currentBranch}`);

  const prUrl = await bash(`
    gh pr create \
      --title "${pr.title}" \
      --body "${pr.body}" \
      --base ${baseBranch} \
      ${pr.labels ? `--label "${pr.labels.join(",")}"` : ""}
  `);

  return success(`PR created: ${prUrl}`);
}
```

## Examples

### Standard PR creation:

```bash
/pr
# Output:
✓ Branch: feature/oauth-support
✓ Analyzing changes...
  - 15 files changed
  - 3 modules affected (auth, api, database)

📋 PR Preview:
Title: feat(auth): add OAuth2 provider support

Description:
## Summary
- Implemented OAuth2 authentication with Google and GitHub
- Added token refresh mechanism
- Updated user model for social logins

Create PR? (y/n): y
✅ PR created: https://github.com/user/repo/pull/123
```

## Error Handling

```yaml
COMMON_ERRORS:
  No commits:
    - Message: "No commits to create PR"
    - Suggest: Make changes and commit first

  Not authenticated:
    - Message: "GitHub CLI not authenticated"
    - Suggest: Run 'gh auth login'

  Remote exists:
    - Message: "PR already exists for this branch"
    - Show: Link to existing PR

  Conflicts:
    - Message: "Branch has conflicts with base"
    - Suggest: Merge or rebase base branch
```

## Integration with Other Commands

```yaml
Workflow:
  1. /commit      # Commit your changes
  2. /pr          # Create pull request
  3. /issue       # Report any bugs found in review

After PR Merge:
  - Automatic changelog update
  - Version bump if configured
  - Delete feature branch locally
```

## GitHub Integration Requirements

```yaml
Prerequisites:
  - GitHub CLI installed (gh)
  - Authenticated: gh auth login
  - Repository has GitHub remote

Optional:
  - CODEOWNERS file for auto-reviewers
  - .github/pull_request_template.md
  - GitHub Actions for CI/CD
```

---

_Command designed for Acolytes for Claude Code professional workflow_
