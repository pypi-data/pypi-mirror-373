#!/usr/bin/env python3
"""
Safe project cleaning script for development artifacts.
Only removes cache, build, and temporary files from current directory.
NEVER touches dependencies like node_modules, vendor, packages, etc.
"""

import os
import shutil
import glob
from pathlib import Path


def get_project_dir():
    """Get the current project directory (where the user is working)"""
    return Path.cwd()


def clean_python_artifacts():
    """Clean Python cache and build artifacts"""
    project_dir = get_project_dir()
    patterns = [
        "__pycache__",
        "*.pyc", 
        "*.pyo",
        "*.pyd",
        ".pytest_cache",
        ".mypy_cache",
        ".coverage",
        ".tox",
        "dist",
        "build", 
        "*.egg-info",
        ".eggs"
    ]
    
    removed = []
    for pattern in patterns:
        # Handle directory patterns like __pycache__ recursively
        if pattern in ["__pycache__", ".pytest_cache", ".mypy_cache", ".tox", "dist", "build", ".eggs"]:
            # Use project_dir as base for searches
            search_pattern = str(project_dir / "**" / pattern)
            for item in glob.glob(search_pattern, recursive=True):
                # Skip items inside protected directories
                if any(protected in item for protected in ['.venv', 'venv', 'node_modules', 'vendor', '.git']):
                    continue
                if os.path.isdir(item):
                    shutil.rmtree(item, ignore_errors=True)
                    removed.append(f"DIR {item}/")
            # Also check project root directory
            direct_pattern = project_dir / pattern
            if direct_pattern.exists() and direct_pattern.is_dir():
                shutil.rmtree(direct_pattern, ignore_errors=True)
                removed.append(f"DIR {direct_pattern}/")
        else:
            # Handle file patterns
            search_pattern = str(project_dir / "**" / pattern)
            for item in glob.glob(search_pattern, recursive=True):
                # Skip items inside protected directories
                if any(protected in item for protected in ['.venv', 'venv', 'node_modules', 'vendor', '.git']):
                    continue
                if os.path.isfile(item):
                    os.remove(item)
                    removed.append(f"FILE {item}")
            # Also check project root directory
            direct_pattern = str(project_dir / pattern)
            for item in glob.glob(direct_pattern):
                if os.path.isfile(item):
                    os.remove(item)
                    removed.append(f"FILE {item}")
    return removed


def clean_java_artifacts():
    """Clean Java build artifacts (Maven/Gradle)"""
    project_dir = get_project_dir()
    patterns = ["target", "build"]
    removed = []
    
    for pattern in patterns:
        pattern_path = project_dir / pattern
        if pattern_path.exists() and pattern_path.is_dir():
            shutil.rmtree(pattern_path, ignore_errors=True)
            removed.append(f"DIR {pattern_path}/")
    
    return removed


def clean_js_artifacts():
    """Clean JavaScript build artifacts (NOT node_modules!)"""
    project_dir = get_project_dir()
    patterns = ["dist", "build", ".next", ".nuxt", "coverage"]
    removed = []
    
    for pattern in patterns:
        pattern_path = project_dir / pattern
        if pattern_path.exists() and pattern_path.is_dir():
            shutil.rmtree(pattern_path, ignore_errors=True)
            removed.append(f"DIR {pattern_path}/")
    
    return removed


def clean_laravel_artifacts():
    """Clean Laravel cache artifacts"""
    project_dir = get_project_dir()
    cache_paths = [
        "bootstrap/cache/config.php",
        "bootstrap/cache/routes.php", 
        "bootstrap/cache/services.php",
        "storage/framework/cache/data",
        "storage/framework/views"
    ]
    
    removed = []
    for path in cache_paths:
        full_path = project_dir / path
        if full_path.exists():
            if full_path.is_dir():
                shutil.rmtree(full_path, ignore_errors=True)
                removed.append(f"DIR {full_path}/")
            else:
                full_path.unlink()
                removed.append(f"FILE {full_path}")
    
    return removed


def clean_dotnet_artifacts():
    """Clean .NET build artifacts"""
    project_dir = get_project_dir()
    patterns = ["bin", "obj"]
    removed = []
    
    for pattern in patterns:
        search_pattern = str(project_dir / "**" / pattern)
        for item in glob.glob(search_pattern, recursive=True):
            if os.path.isdir(item):
                shutil.rmtree(item, ignore_errors=True)
                removed.append(f"DIR {item}/")
    
    return removed


def clean_rust_artifacts():
    """Clean Rust build artifacts"""
    project_dir = get_project_dir()
    target_path = project_dir / "target"
    if target_path.exists() and target_path.is_dir():
        shutil.rmtree(target_path, ignore_errors=True)
        return [f"DIR {target_path}/"]
    return []


def clean_go_artifacts():
    """Clean Go build cache (local only)"""
    project_dir = get_project_dir()
    removed = []
    # Only clean local go build files, not global cache
    search_pattern = str(project_dir / "*.exe")
    for item in glob.glob(search_pattern):
        os.remove(item)
        removed.append(f"FILE {item}")
    return removed


def detect_project_types():
    """Detect what type of project this is based on files present"""
    project_dir = get_project_dir()
    types = []
    
    # Python
    if any((project_dir / f).exists() for f in ["setup.py", "pyproject.toml", "requirements.txt", "Pipfile"]):
        types.append("python")
    
    # Java
    if any((project_dir / f).exists() for f in ["pom.xml", "build.gradle", "build.gradle.kts"]):
        types.append("java")
    
    # JavaScript/Node.js
    if any((project_dir / f).exists() for f in ["package.json", "yarn.lock", "package-lock.json"]):
        types.append("javascript")
    
    # Laravel/PHP
    if any((project_dir / f).exists() for f in ["composer.json", "artisan"]):
        types.append("laravel")
    
    # .NET
    if any(list(project_dir.glob(f)) for f in ["*.csproj", "*.sln", "*.fsproj", "*.vbproj"]):
        types.append("dotnet")
    
    # Rust
    if (project_dir / "Cargo.toml").exists():
        types.append("rust")
    
    # Go
    if any((project_dir / f).exists() for f in ["go.mod", "go.sum"]):
        types.append("go")
    
    return types


def main():
    """Main cleaning function"""
    import sys
    
    # Handle arguments
    quiet = "--quiet" in sys.argv
    
    if not quiet:
        print("Cleaning development artifacts from current directory...")
        print("Will NOT touch: node_modules, vendor, packages, .git, etc.")
        print()
    
    project_types = detect_project_types()
    if not project_types:
        if not quiet:
            print("No recognized project type found in current directory")
        return
    
    if not quiet:
        print(f"Detected project types: {', '.join(project_types)}")
        print()
    
    all_removed = []
    cleaners = {
        "python": clean_python_artifacts,
        "java": clean_java_artifacts, 
        "javascript": clean_js_artifacts,
        "laravel": clean_laravel_artifacts,
        "dotnet": clean_dotnet_artifacts,
        "rust": clean_rust_artifacts,
        "go": clean_go_artifacts
    }
    
    for project_type in project_types:
        if project_type in cleaners:
            removed = cleaners[project_type]()
            all_removed.extend(removed)
    
    if all_removed:
        print("Project cleaned:")
        for item in all_removed:
            print(f"  {item}")
        print(f"\nRemoved {len(all_removed)} items from current project")
    else:
        if not quiet:
            print("Already clean! No artifacts found")


if __name__ == "__main__":
    main()