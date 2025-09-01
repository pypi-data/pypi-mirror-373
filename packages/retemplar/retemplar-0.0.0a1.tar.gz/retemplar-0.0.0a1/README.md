# retemplar

> **Repo-as-Template engine for structural lifecycle management at scale**

Keep many repos in sync with a living template — without trampling local changes.

## Purpose

Organizations often have dozens or hundreds of repositories that share a common structure (CI workflows, lint configs, Dockerfiles, etc.). Over time, these repos **drift** from the original template. retemplar solves this by:

- Using any repo as a **living template** (Repo-as-Template, RAT)
- Letting other repos **adopt** that template version
- Applying **template-to-template deltas** as small, explainable PRs
- Supporting **managed paths**, **section-level rules**, and **inline blocks** to control ownership
- Recording provenance in a `.retemplar.lock` file

The result: consistent, auditable upgrades across your entire fleet of repos.

## Current Status

- **Phase**: MVP Implementation Complete ✅
- **Version**: 0.0.0a0 (Alpha)
- **Primary Doc**: [`docs/design-doc.md`](docs/design-doc.md)
- **Ready**: Core CLI + lockfile management + template engine

## Installation

```bash
# Install from source (development)
git clone <repo-url>
cd retemplar
pip install -e .
```

## Quick Start

### 1. Adopt a Template

Make your repo adopt another repo as a template:

```bash
# Adopt a local template
retemplar adopt --template rat:../my-template-repo

# Adopt a GitHub template at a specific tag
retemplar adopt --template rat:gh:org/template-repo@v1.0.0
```

This creates a `.retemplar.lock` file tracking the template relationship.

### 2. Plan Template Updates

See what changes would be applied when updating to a new template version:

```bash
# Preview upgrade to latest
retemplar plan --to rat:../my-template-repo

# Preview upgrade to specific version
retemplar plan --to rat:gh:org/template-repo@v1.1.0
```

### 3. Apply Changes

Apply the planned changes:

```bash
# Apply changes locally
retemplar apply --to rat:../my-template-repo

# Apply and create GitHub PR (when GitHub provider is ready)
retemplar apply --to rat:../my-template-repo --pr
```

### 4. Check for Drift

Detect when your repo has drifted from the template:

```bash
retemplar drift
```

## Configuration

### Lockfile (`.retemplar.lock`)

After running `adopt`, you'll get a lockfile like:

```yaml
schema_version: "1.0.0"
template:
  kind: rat
  repo: gh:org/template-repo
  ref: v1.0.0
version: rat@v1.0.0

managed_paths:
  - path: ".github/workflows/**"
    strategy: enforce
  - path: "pyproject.toml"
    strategy: patch
    rules:
      - path: "tool.ruff"
        action: enforce
      - path: "project.dependencies"
        action: preserve

ignore_paths:
  - "README.md"
  - "docs/**"
```

**Edit this file** to control what the template manages:

- `enforce`: Template always wins
- `preserve`: Local changes always win
- `merge`: Attempt 3-way merge
- `patch`: Section-level rules for structured files

### Inline Managed Blocks

For fine-grained control within files:

```python
# retemplar:begin id=imports
import os
import sys
# retemplar:end

# Your local code here
print("Hello world")

# retemplar:begin id=main-logic
def main():
    pass
# retemplar:end
```

**Modes:**

- Default: Template manages the block content
- `# retemplar:begin id=myblock mode=ignore`: Keep local content untouched
- `# retemplar:begin id=myblock mode=protect`: Create conflict for review

## Features

- ✅ **Repo-as-Template (RAT)**: Use any repo/tag as a living template
- ✅ **Incremental Updates**: Small, explainable template-to-template diffs
- ✅ **Ownership Control**: Path-level and section-level ownership rules
- ✅ **Drift Detection**: Detect conflicts between template and local changes
- ✅ **3-Way Merges**: Smart merging with conflict markers when needed
- ✅ **Inline Blocks**: Manage specific sections within files
- ✅ **Variable Substitution**: Template variables with persistence
- ✅ **Lockfile Tracking**: Full provenance and upgrade history
- 🚧 **GitHub Integration**: Use github link as reference

## Examples

### Template Upgrade Workflow

```bash
# Check current status
retemplar drift

# Plan upgrade
retemplar plan --to rat:gh:org/template@v2.0.0

# Review the changes, then apply
retemplar apply --to rat:gh:org/template@v2.0.0
```

### Managing Conflicts

When local and template changes conflict, you'll see:

```diff
<<<<<<< local
line-length = 120
=======
line-length = 88
>>>>>>> template
```

Resolve manually, then commit the resolution.

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Lint and format
ruff check --fix
ruff format
```
