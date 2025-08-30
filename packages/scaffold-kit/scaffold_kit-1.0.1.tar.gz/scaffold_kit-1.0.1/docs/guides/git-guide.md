---
title: Git Conventions and Commands Reference
date: 2025-08-26
weight: 2
---

# Git Conventions and Commands Reference

This guide establishes standardized naming conventions for Git operations based
on the Conventional Commits specification and provides a comprehensive command
reference for common Git workflows.

## Git Conventions

Use standard naming conventions for Git operations based on the Conventional
Commits specification.

### Commit Messages

Commit messages should provide a concise summary of what changes were made and
why, using imperative form and lowercase formatting.

#### Rules

**Format:**

```bash
<tag>[(<scope>)][!]: <description>
# e.g., feat: add ignore parser
```

- **formatting**: lower case

- **form**: imperative

**Allowed Tags:**

| tag      | purpose                                     | version bump |
| -------- | ------------------------------------------- | ------------ |
| feat     | For adding or updating features             | minor        |
| fix      | For bug fixes                               | patch        |
| perf     | For performance improvements                | patch        |
| build    | For changes to build system or dependencies | none         |
| chore    | For non-code tasks                          | none         |
| ci       | For adding or updating CI/CD configuration  | none         |
| docs     | For adding or updating documentation        | none         |
| refactor | For code improvements                       | none         |
| style    | For code formatting                         | none         |
| test     | For adding or updating tests                | none         |

```toml
# pyproject.toml
[tool.semantic_release.commit_parser_options]
minor_tags = ["feat"]
patch_tags = ["fix", "perf"]
other_allowed_tags = [
  "build",
  "chore",
  "ci",
  "docs",
  "refactor",
  "style",
  "test",
]
allowed_tags = [
  "feat",
  "fix",
  "perf",
  "build",
  "chore",
  "ci",
  "docs",
  "refactor",
  "style",
  "test",
]
```

#### Examples

- `feat: add user authentication`

- `feat!: remove deprecated api endpoints`

- `feat(auth): implement oauth integration`

- `feat(parser)!: change config file format`

- `fix: resolve memory leak in cache`

- `fix!: correct breaking validation logic`

- `fix(api): handle null response errors`

- `fix(ui)!: update button component interface`

- `perf: optimize database queries`

- `perf!: restructure data processing pipeline`

- `perf(cache): improve memory usage`

- `perf(api)!: change response format for speed`

- `build: update webpack configuration`

- `build(deps): upgrade react to v18`

- `chore: clean up unused imports`

- `chore(config): update eslint rules`

- `ci: add automated testing workflow`

- `ci(deploy): configure production pipeline`

- `docs: update installation guide`

- `docs(api): add endpoint examples`

- `refactor: simplify user validation logic`

- `refactor(auth): extract common utilities`

- `style: format code with prettier`

- `style(components): fix indentation`

- `test: add unit tests for parser`

- `test(integration): cover auth flow`

### Branches

Branch names should follow a consistent format to clearly indicate the type of
work and briefly describe the changes, using kebab-case formatting.

#### Rules

**Format:**

```bash
<tag>/<description>
# e.g., feat/add-ignore-parser
```

for preparing releases

```bash
release/<MAJOR.MINOR.PATCH>
# e.g., release/1.2.3
```

- **formatting**: kebap-case

- **form**: imperative

**Allowed Tags:**

- _see [Commit Messages](#commit-messages)_

- release

#### Examples

- `feat/add-user-authentication`

- `feat/auth-implement-oauth-integration`

- `fix/resolve-memory-leak-cache`

- `fix/api-handle-null-responses`

- `perf/optimize-database-queries`

- `perf/cache-improve-memory-usage`

- `release/2.1.0`

- `build/update-webpack-config`

- `build/deps-upgrade-react`

- `chore/clean-unused-imports`

- `chore/config-update-eslint`

- `ci/add-automated-testing`

- `ci/deploy-configure-production`

- `docs/update-installation-guide`

- `docs/api-add-endpoint-examples`

- `refactor/simplify-validation-logic`

- `refactor/auth-extract-utilities`

- `style/format-with-prettier`

- `style/components-fix-indentation`

- `test/add-parser-unit-tests`

- `test/integration-cover-auth-flow`

## Commands Reference

### Branching

| task                                         | `git checkout` cmd                       | `git switch` / `git restore` cmd        |
| -------------------------------------------- | ---------------------------------------- | --------------------------------------- |
| Switch to an existing branch                 | `git checkout main`                      | `git switch main`                       |
| Create a new branch and switch to it         | `git checkout -b feat/add-ignore-parser` | `git switch -c feat/add-ignore-parser`  |
| Switch to previous branch                    | `git checkout -`                         | `git switch -`                          |
| Discard local changes to a file              | `git checkout -- README.md`              | `git restore README.md`                 |
| Restore a file from a specific commit        | `git checkout abc123 -- README.md`       | `git restore --source=abc123 README.md` |
| Restore all files to last commit state       | `git checkout -- .`                      | `git restore .`                         |
| Create a new branch from a commit            | `git checkout -b fix abc123`             | `git switch -c fix abc123`              |
| Detach HEAD at a specific commit (no branch) | `git checkout abc123`                    | `git switch --detach abc123`            |
| Cancel staged changes (unstage a file)       | `git reset HEAD README.md`               | `git restore --staged README.md`        |

### Committing

| task                                     | command                                    |
| ---------------------------------------- | ------------------------------------------ |
| Stage all changes                        | `git add .`                                |
| Stage specific file                      | `git add README.md`                        |
| Stage all modified files (not new)       | `git add -u`                               |
| Interactive staging                      | `git add -i` or `git add -p`               |
| Commit staged changes                    | `git commit -m "feat: add user auth"`      |
| Commit and stage all modified files      | `git commit -am "fix: resolve cache bug"`  |
| Amend last commit message                | `git commit --amend -m "new message"`      |
| Amend last commit with new changes       | `git commit --amend --no-edit`             |
| Create empty commit                      | `git commit --allow-empty -m "trigger ci"` |
| View commit history                      | `git log` or `git log --oneline`           |
| View specific number of commits          | `git log -5`                               |
| View changes in last commit              | `git show` or `git show HEAD`              |
| View changes in specific commit          | `git show abc123`                          |
| Unstage file (keep changes)              | `git reset HEAD README.md`                 |
| Unstage all files (keep changes)         | `git reset HEAD`                           |
| Undo last commit (keep changes staged)   | `git reset --soft HEAD~1`                  |
| Undo last commit (keep changes unstaged) | `git reset HEAD~1`                         |
| Undo last commit (discard changes)       | `git reset --hard HEAD~1`                  |
| Interactive rebase last 3 commits        | `git rebase -i HEAD~3`                     |

### Merging

| task                                      | command                              |
| ----------------------------------------- | ------------------------------------ |
| Merge branch with fast-forward            | `git merge feat/add-auth`            |
| Merge branch without fast-forward         | `git merge --no-ff feat/add-auth`    |
| Squash merge branch                       | `git merge --squash feat/add-auth`   |
| Abort merge during conflicts              | `git merge --abort`                  |
| Continue merge after resolving conflicts  | `git merge --continue`               |
| View merge conflicts                      | `git status` or `git diff`           |
| Mark conflict as resolved                 | `git add conflicted_file.py`         |
| Rebase current branch onto main           | `git rebase main`                    |
| Interactive rebase                        | `git rebase -i main`                 |
| Abort rebase                              | `git rebase --abort`                 |
| Continue rebase after resolving conflicts | `git rebase --continue`              |
| Skip current commit during rebase         | `git rebase --skip`                  |
| Cherry-pick specific commit               | `git cherry-pick abc123`             |
| Cherry-pick commit without committing     | `git cherry-pick --no-commit abc123` |
| View branches that have been merged       | `git branch --merged`                |
| View branches not yet merged              | `git branch --no-merged`             |
| Delete merged branch                      | `git branch -d feat/add-auth`        |
| Force delete unmerged branch              | `git branch -D feat/add-auth`        |
