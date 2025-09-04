---
command: commit
description: ♾️  Smart commit with auto-changelog, version bump and git tagging | Optional: --wip (quick save), --push (auto push), --validate (CI/CD checks)
---

# Smart Git Commit with Auto-Versioning

I'll create an intelligent commit with automatic emoji selection, changelog update, and semantic version management. This is a complete workflow that handles everything from commit to release tagging.

## Complete Automated Workflow

When you run `/commit`, the following happens automatically:

1. **Pre-Analysis**: Verify repository status and analyze all changes
2. **Smart Commit**: Create commit with emoji and conventional format
3. **Version Detection**: Determine version bump type from commit
4. **Auto-Changelog**: Invoke @docs.specialist to update CHANGELOG.md with correct version
5. **Version Update**: Execute bump2version to update all version files
6. **Tag Creation**: Create annotated git tag (e.g., v1.0.1)

The entire process is automated based on your changes and commit type.

## Emoji Classification System

I'll automatically select the most appropriate emoji based on file changes and commit type:

### Core Types

- ✨ `feat`: New feature
- 🐛 `fix`: Bug fix
- 📝 `docs`: Documentation
- 💄 `style`: Formatting/style
- ♻️ `refactor`: Code refactoring
- ⚡️ `perf`: Performance improvements
- ✅ `test`: Tests
- 🔧 `chore`: Tooling, configuration

### Extended Classification

- 🚀 `ci`: CI/CD improvements
- 🗑️ `revert`: Reverting changes
- 🧪 `test`: Add a failing test
- 🚨 `fix`: Fix compiler/linter warnings
- 🔒️ `fix`: Fix security issues
- 👥 `chore`: Add or update contributors
- 🚚 `refactor`: Move or rename resources
- 🏗️ `refactor`: Make architectural changes
- 🔀 `chore`: Merge branches
- 📦️ `chore`: Add or update compiled files or packages
- ➕ `chore`: Add a dependency
- ➖ `chore`: Remove a dependency
- 🌱 `chore`: Add or update seed files
- 🧑‍💻 `chore`: Improve developer experience
- 🧵 `feat`: Add or update code related to multithreading or concurrency
- 🔍️ `feat`: Improve SEO
- 🏷️ `feat`: Add or update types
- 💬 `feat`: Add or update text and literals
- 🌐 `feat`: Internationalization and localization
- 👔 `feat`: Add or update business logic
- 📱 `feat`: Work on responsive design
- 🚸 `feat`: Improve user experience / usability
- 🩹 `fix`: Simple fix for a non-critical issue
- 🥅 `fix`: Catch errors
- 👽️ `fix`: Update code due to external API changes
- 🔥 `fix`: Remove code or files
- 🎨 `style`: Improve structure/format of the code
- 🚑️ `fix`: Critical hotfix
- 🎉 `chore`: Begin a project
- 🔖 `chore`: Release/Version tags
- 🚧 `wip`: Work in progress
- 💚 `fix`: Fix CI build
- 📌 `chore`: Pin dependencies to specific versions
- 👷 `ci`: Add or update CI build system
- 📈 `feat`: Add or update analytics or tracking code
- ✏️ `fix`: Fix typos
- ⏪️ `revert`: Revert changes
- 📄 `chore`: Add or update license
- 💥 `feat`: Introduce breaking changes
- 🍱 `assets`: Add or update assets
- ♿️ `feat`: Improve accessibility
- 💡 `docs`: Add or update comments in source code
- 🗃️ `db`: Perform database related changes
- 🔊 `feat`: Add or update logs
- 🔇 `fix`: Remove logs
- 🤡 `test`: Mock things
- 🥚 `feat`: Add or update an easter egg
- 🙈 `chore`: Add or update .gitignore file
- 📸 `test`: Add or update snapshots
- ⚗️ `experiment`: Perform experiments
- 🚩 `feat`: Add, update, or remove feature flags
- 💫 `ui`: Add or update animations and transitions
- ⚰️ `refactor`: Remove dead code
- 🦺 `feat`: Add or update code related to validation
- ✈️ `feat`: Improve offline support

## Semantic Version Bump Detection

Following [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) (SemVer), the commit emoji and type automatically determine the version bump:

**PATCH** (1.0.0 → 1.0.1) - Backward compatible bug fixes:

- 🐛 `fix:` Bug fixes
- 🩹 `fix:` Simple fixes
- 🚑️ `fix:` Critical hotfixes
- ✏️ `fix:` Typo corrections
- 🔇 `fix:` Remove logs
- 👽️ `fix:` External API updates
- 🥅 `fix:` Catch errors

**MINOR** (1.0.0 → 1.1.0) - Backward compatible new functionality:

- ✨ `feat:` New features
- ⚡️ `perf:` Performance improvements (if adds new capabilities)
- 🚸 `feat:` UX improvements (new features)
- 🏷️ `feat:` Add types (if public API)
- 🔊 `feat:` Add logs (if part of public API)
- 🦺 `feat:` Add validation (new feature)
- 🚩 `feat:` Add feature flags
- 📈 `feat:` Add analytics
- ♿️ `feat:` Add accessibility features
- 🌐 `feat:` Add internationalization
- 👔 `feat:` Add business logic
- ✈️ `feat:` Add offline support

**MAJOR** (1.0.0 → 2.0.0) - Backward incompatible changes:

- 💥 `feat:` Breaking changes (explicit)
- 🏗️ `refactor:` Architectural changes (only if breaking)
- 🗑️ `revert:` Major reversions (only if breaking)
- 🔥 `fix:` Remove code/files (if public API)

**NO VERSION BUMP** - Changes that don't affect functionality:

- 📝 `docs:` Documentation only
- 💄 `style:` Code formatting (no logic changes)
- ♻️ `refactor:` Code refactoring (non-breaking)
- ✅ `test:` Adding/updating tests
- 🔧 `chore:` Build/config changes
- 🎨 `style:` Code structure improvements
- 🚧 `wip:` Work in progress (with --wip flag)
- ➕ `chore:` Add dependencies (internal only)
- ➖ `chore:` Remove dependencies (internal only)
- 📌 `chore:` Pin dependencies
- 🙈 `chore:` Update .gitignore
- 👥 `chore:` Update contributors
- 📄 `chore:` Update license
- 🚚 `refactor:` Move/rename files (non-breaking)
- ⚰️ `refactor:` Remove dead code (non-breaking)
- 🧪 `test:` Add failing tests
- 🤡 `test:` Mock things
- 📸 `test:` Add snapshots

## Execution Process

### Step 1: Repository Analysis & WIP Cleanup

```bash
# Verify we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "Error: Not a git repository"
    echo "This command requires git version control"
    exit 1
fi

# Check for WIP commits and clean them up
echo "Checking for WIP commits to consolidate..."
WIP_COUNT=0
while true; do
    # Get the last commit message
    LAST_MSG=$(git log -1 --pretty=%s 2>/dev/null)

    # Check if it starts with 🚧 WIP:
    if [[ "$LAST_MSG" == "🚧 WIP:"* ]]; then
        echo "Found WIP commit: $LAST_MSG"
        WIP_COUNT=$((WIP_COUNT + 1))
        # Soft reset to keep changes but remove the WIP commit
        git reset --soft HEAD~1
    else
        break
    fi
done

if [ $WIP_COUNT -gt 0 ]; then
    echo "Consolidated $WIP_COUNT WIP commit(s) into working directory"
    echo "All changes are preserved and will be included in the new commit"
fi

# Check if we have changes to commit
if ! git diff --cached --quiet || ! git diff --quiet; then
    echo "Changes detected:"
    git status --short
else
    echo "No changes to commit"
    exit 0
fi

# Show detailed changes
git diff --cached --stat
git diff --stat
```

### Step 2: Change Analysis

I'll analyze the changes to determine:

1. **File types**: Configuration, source code, documentation, assets
2. **Change patterns**: New files, deletions, modifications, renames
3. **Content analysis**: Feature additions, bug fixes, refactoring, etc.
4. **Scope detection**: Components or areas affected

### Step 3: Smart Emoji Selection

Based on file analysis, I'll select the most appropriate emoji:

- **package.json/requirements.txt changes**: ➕ (add dependency) or ➖ (remove dependency) → Usually NO bump
- **.gitignore changes**: 🙈 (update .gitignore) → NO bump
- **CI/CD files**: 🚀 (CI improvements) or 👷 (CI build system) → Usually NO bump
- **Documentation files**: 📝 (docs) or 💡 (code comments) → NO bump
- **Test files**: ✅ (tests), 🧪 (failing test), 📸 (snapshots), 🤡 (mocks) → NO bump
- **Security fixes**: 🔒️ (security issues) → PATCH bump
- **Performance**: ⚡️ (performance improvements) → PATCH (fix) or MINOR (new capability)
- **UI/UX**: 💄 (style) → NO bump, 📱 (responsive) → MINOR, 🚸 (UX) → MINOR, 💫 (animations) → NO bump
- **Database**: 🗃️ (database changes) → Depends on impact
- **Breaking changes**: 💥 (breaking changes) → MAJOR bump
- **Critical fixes**: 🚑️ (critical hotfix) → PATCH bump
- **Code structure**: 🎨 (structure) → NO bump, ♻️ (refactor) → NO bump, ⚰️ (dead code) → NO bump
- **Assets**: 🍱 (assets) → Usually NO bump
- **Accessibility**: ♿️ (accessibility) → MINOR bump (new feature)
- **Logs**: 🔊 (add logs) → MINOR if public API, 🔇 (remove logs) → PATCH if fixing bug
- **Feature flags**: 🚩 (feature flags) → MINOR bump
- **Validation**: 🦺 (validation) → MINOR bump (new feature)
- **Offline support**: ✈️ (offline support) → MINOR bump (new feature)

### Step 4: Stage Changes

```bash
# If nothing is staged, I'll stage all changes (including untracked)
if git diff --cached --quiet; then
    echo "No files staged. Staging all changes..."
    git add -A
fi

# Show what will be committed
git diff --cached --name-status
```

### Step 5: Prepare Commit Message

I'll prepare a conventional commit message with emoji (but NOT execute it yet):

**Format**: `emoji type(scope): description`

- **Emoji**: Automatically selected from 110+ classification
- **Type**: Conventional commit type (feat, fix, docs, etc.)
- **Scope**: Component or area affected (optional)
- **Description**: Clear description in present tense
- **Session ID**: Included in footer for traceability

```bash
# Get current session ID from SQLite database
SESSION_ID=$(cd .claude && python -c "
import sqlite3
import os
db_path = os.path.join('memory', 'project.db')
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.execute('SELECT session_id FROM sessions ORDER BY created_at DESC LIMIT 1')
    result = cursor.fetchone()
    print(result[0] if result else 'unknown')
    conn.close()
except Exception as e:
    print('unknown')
")

# Prepare the commit message (NOT executed yet)
COMMIT_MESSAGE="✨ feat(auth): add OAuth2 integration with GitHub

session: $SESSION_ID"
```

### Step 6: Update Changelog

BEFORE creating the actual commit, I'll invoke @docs.specialist with the planned message to:

- Analyze the planned commit message
- Update CHANGELOG.md with technical details
- Add the new version entry
- Stage the updated CHANGELOG.md

### Step 7: Automatic Version Bump

Based on the commit type, bump2version will:

- Detect version bump type (patch/minor/major)
- Update all version files automatically (pyproject.toml, etc.)
- **NO commit, NO tag** (controlled by .bumpversion.cfg)

```bash
# Execute version bump based on commit type
# This ONLY updates version files, does NOT commit or tag
bump2version [patch|minor|major] --no-commit --no-tag
```

### Step 8: Create Single Atomic Commit

Now I'll create ONE single commit with ALL changes:

```bash
# Stage all modified files (original changes + CHANGELOG + version files)
git add -A

# Create the single atomic commit with everything
git commit -m "$COMMIT_MESSAGE"
```

This single commit includes:
- Your original code changes
- Updated CHANGELOG.md from @docs.specialist
- Updated version files from bump2version
- Proper emoji and conventional format

### Step 9: Create Version Tag

After the successful commit, create the version tag:

```bash
# Create annotated tag pointing to the commit
git tag -a v1.0.7 -m "Release version 1.0.7"
```

## Commit Examples

- `✨ feat(auth): add OAuth2 integration with GitHub` → Minor version bump
- `🐛 fix(api): resolve timeout issue in user endpoints` → Patch version bump
- `📝 docs(readme): update installation instructions` → No version bump
- `⚡️ perf(database): optimize query performance` → Patch version bump (bug fix) or Minor (new capability)
- `🔒️ fix(security): patch XSS vulnerability` → Patch version bump
- `💥 feat(api): breaking API changes` → Major version bump
- `♻️ refactor(components): extract reusable logic` → No version bump
- `➕ chore(deps): add lodash for utilities` → No version bump (internal dependency)
- `🎨 style(components): improve code structure` → No version bump
- `🚑️ fix(critical): patch memory leak` → Patch version bump
- `✅ test(auth): add unit tests for login` → No version bump
- `🔧 chore(config): update webpack configuration` → No version bump

## Requirements

- **bump2version** installed: `pip install bump2version`
- **.bumpversion.cfg** configured in project root with:
  - `commit = False` (bump2version should NOT commit)
  - `tag = False` (bump2version should NOT tag)
- **@docs.specialist** agent available

## Important Notes

**I will NEVER:**

- Add "Co-authored-by" or any Claude signatures
- Include "Generated with Claude Code" or similar messages
- Modify git config or user credentials
- Add any AI/assistant attribution to the commit

The commit will use only your existing git user configuration, maintaining full ownership and authenticity of your commits.

---

## Optional Command Arguments

You can customize the behavior with these optional arguments:

### `/commit --wip`

**Work In Progress** - Quick save of unfinished work:

- Adds 🚧 emoji and "WIP:" prefix automatically
- Skips ALL validations (tests, linting, build)
- NO version bump or changelog update
- Stages all changes automatically (git add -A)
- Perfect for end-of-day saves or branch switches

**Automatic WIP consolidation**: When you run `/commit` (without --wip), Claude automatically:

1. Detects all consecutive WIP commits
2. Consolidates them into the working directory
3. Creates a single proper commit with all changes

```bash
# Day 1: Quick save
/commit --wip
# Result: "🚧 WIP: working on authentication"

# Day 2: Another quick save
/commit --wip
# Result: "🚧 WIP: continuing auth implementation"

# Day 3: Ready to make proper commit
/commit
# Claude automatically:
# - Finds the 2 WIP commits
# - Consolidates them (git reset --soft)
# - Creates: "✨ feat: add complete authentication system"
```

### `/commit --push`

Automatically push to remote after successful commit:

- Creates commit with all normal workflow
- Executes `git push` to current branch
- Fails safely if push is rejected

```bash
# Commit and push to current branch
/commit --push

# Combine with other options
/commit --wip --push  # WIP commit + push
```

### `/commit --validate`

**Professional CI/CD validations** before committing:

- Invokes @test.quality agent for comprehensive testing
- Runs test suite, linting, type checking
- Build verification and security scans
- If any validation fails, commit is aborted

```bash
# Full validation before commit
/commit --validate

# Combine with other options
/commit --validate --push  # Validated commit + push
```

---

## Examples

**Quick saves:**

```bash
/commit --wip              # Quick WIP commit, no validations
/commit --wip --push       # WIP + push to share with team
```

**Professional workflow:**

```bash
/commit                    # Normal commit with emoji + changelog + version
/commit --validate         # Validate everything before commit
/commit --validate --push  # Validate, commit, and push
```

