---
command: clean  
description: ♾️  Clean - Remove build artifacts and cache files from current project
---

# Clean Command

Cleans build artifacts, cache files, and temporary development files from the current project directory. Safe cleaning that preserves dependencies and critical files.

## Usage
```
/clean
```

## What it cleans

### Python Projects
- `__pycache__/` directories
- `*.pyc`, `*.pyo`, `*.pyd` files
- `.pytest_cache/`
- `.mypy_cache/`
- `.coverage` files
- `.tox/`
- `dist/`, `build/`
- `*.egg-info/`
- `.eggs/`

### Java Projects (Maven/Gradle)
- `target/` (Maven)
- `build/` (Gradle)

### JavaScript/Node.js Projects
- `dist/`, `build/`
- `.next/` (Next.js)
- `.nuxt/` (Nuxt.js)
- `coverage/`

### Laravel/PHP Projects
- `bootstrap/cache/config.php`
- `bootstrap/cache/routes.php`
- `bootstrap/cache/services.php`
- `storage/framework/cache/data/`
- `storage/framework/views/`

### .NET Projects
- `bin/` directories
- `obj/` directories

### Rust Projects
- `target/` directory

### Go Projects
- `*.exe` files (local builds)

## What it NEVER touches
- `node_modules/` (dependencies)
- `vendor/` (PHP dependencies)
- `packages/` (package directories)
- `.git/` (version control)
- Configuration files
- Source code files
- Global system paths

## Implementation
Uses the universal project cleaner script: `acolytes/data/scripts/clean_project.py`

Auto-detects project type based on files present:
- `package.json` → JavaScript
- `pyproject.toml`/`setup.py` → Python  
- `pom.xml`/`build.gradle` → Java
- `composer.json` → Laravel/PHP
- `*.csproj`/`*.sln` → .NET
- `Cargo.toml` → Rust
- `go.mod` → Go

## Example Output
```
🧹 Cleaning development artifacts from current directory...
⚠️  Will NOT touch: node_modules, vendor, packages, .git, etc.

🔍 Detected project types: python, javascript

✅ Project cleaned:
  📁 __pycache__/
  📁 dist/
  📄 .coverage
  📁 build/

🎉 Removed 4 items from current project
```