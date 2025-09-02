"""
Update command for Acolytes - System update.

Updates the Acolytes system to the latest version.
"""

import os
import shutil
import zipfile
import hashlib
import tempfile
import requests
from datetime import datetime
from pathlib import Path
from typing import Set, Dict, Tuple
from tqdm import tqdm


def run() -> None:
    """Update Acolytes system."""
    print("🔄 Checking for updates...")
    
    # Define paths
    claude_dir = Path.home() / ".claude"
    agents_dir = claude_dir / "agents"
    backup_dir = claude_dir / "backups"
    
    # Ensure directories exist
    claude_dir.mkdir(exist_ok=True)
    backup_dir.mkdir(exist_ok=True)
    
    try:
        # Step 1: Download latest version
        print("📥 Downloading latest version from GitHub...")
        temp_dir = download_latest_version()
        
        # Step 2: Create backup
        print("💾 Creating backup of current agents...")
        backup_path = create_backup(agents_dir, backup_dir)
        print(f"✅ Backup created at: {backup_path}")
        
        # Step 3: Compare and update files
        print("🔍 Analyzing changes...")
        changes = compare_and_update_files(temp_dir, agents_dir)
        
        # Step 4: Show changelog
        show_changelog(changes)
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        if changes["updated"] or changes["added"]:
            print("✅ Update completed successfully!")
        else:
            print("✅ System is already up to date!")
            
    except Exception as e:
        print(f"❌ Update failed: {str(e)}")
        raise


def download_latest_version() -> Path:
    """Download latest version from GitHub with progress bar."""
    url = "https://github.com/unmasSk/acolytes/archive/main.zip"
    
    # Create temporary directory
    temp_dir = Path(tempfile.mkdtemp(prefix="acolytes_update_"))
    zip_path = temp_dir / "acolytes-main.zip"
    
    try:
        # Download with progress bar
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        
        with open(zip_path, 'wb') as file, tqdm(
            desc="Downloading",
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    pbar.update(len(chunk))
        
        # Extract zip file
        print("📦 Extracting archive...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        
        # Remove zip file
        zip_path.unlink()
        
        # Find the extracted directory
        extracted_dir = temp_dir / "acolytes-main"
        if not extracted_dir.exists():
            # Try to find any directory that was extracted
            dirs = [d for d in temp_dir.iterdir() if d.is_dir()]
            if dirs:
                extracted_dir = dirs[0]
            else:
                raise FileNotFoundError("Could not find extracted directory")
        
        return extracted_dir
        
    except Exception as e:
        # Cleanup on error
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        raise e


def create_backup(agents_dir: Path, backup_dir: Path) -> Path:
    """Create backup of current agents directory."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"agents_{timestamp}"
    
    if agents_dir.exists():
        shutil.copytree(agents_dir, backup_path)
    else:
        # Create empty backup directory if no agents exist
        backup_path.mkdir(exist_ok=True)
    
    return backup_path


def calculate_file_hash(file_path: Path) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (IOError, OSError):
        return ""


def is_local_acolyte_file(filename: str) -> bool:
    """Check if file is a local acolyte agent (should not be updated)."""
    return filename.startswith("acolyte.") and filename.endswith(".md")


def compare_and_update_files(source_dir: Path, target_dir: Path) -> Dict[str, Set[str]]:
    """Compare files and update only changed ones."""
    changes = {
        "updated": set(),
        "added": set(),
        "skipped": set(),
        "unchanged": set()
    }
    
    # Find source agents directory
    source_agents_dir = None
    for root, dirs, files in os.walk(source_dir):
        if "agents" in dirs:
            source_agents_dir = Path(root) / "agents"
            break
    
    if not source_agents_dir or not source_agents_dir.exists():
        # Try .claude/agents path
        source_agents_dir = source_dir / ".claude" / "agents"
        if not source_agents_dir.exists():
            raise FileNotFoundError("Could not find agents directory in downloaded archive")
    
    # Ensure target directory exists
    target_dir.mkdir(exist_ok=True)
    
    # Process each file in source
    for source_file in source_agents_dir.glob("*.md"):
        filename = source_file.name
        target_file = target_dir / filename
        
        # Skip local acolyte files
        if is_local_acolyte_file(filename):
            changes["skipped"].add(filename)
            continue
        
        # Calculate hashes
        source_hash = calculate_file_hash(source_file)
        target_hash = calculate_file_hash(target_file) if target_file.exists() else ""
        
        # Compare and update if needed
        if not target_file.exists():
            # New file
            shutil.copy2(source_file, target_file)
            changes["added"].add(filename)
        elif source_hash != target_hash:
            # File changed
            shutil.copy2(source_file, target_file)
            changes["updated"].add(filename)
        else:
            # File unchanged
            changes["unchanged"].add(filename)
    
    return changes


def show_changelog(changes: Dict[str, Set[str]]) -> None:
    """Display changelog of updates."""
    print("\n📋 Update Summary:")
    print("=" * 50)
    
    if changes["added"]:
        print(f"🆕 Added ({len(changes['added'])} files):")
        for filename in sorted(changes["added"]):
            print(f"   + {filename}")
        print()
    
    if changes["updated"]:
        print(f"🔄 Updated ({len(changes['updated'])} files):")
        for filename in sorted(changes["updated"]):
            print(f"   ~ {filename}")
        print()
    
    if changes["skipped"]:
        print(f"⏭️  Skipped local acolytes ({len(changes['skipped'])} files):")
        for filename in sorted(changes["skipped"]):
            print(f"   - {filename}")
        print()
    
    if changes["unchanged"]:
        print(f"✅ Unchanged ({len(changes['unchanged'])} files):")
        for filename in sorted(changes["unchanged"]):
            print(f"   = {filename}")
        print()
    
    total_processed = len(changes["added"]) + len(changes["updated"]) + len(changes["unchanged"])
    total_skipped = len(changes["skipped"])
    
    print(f"📊 Total: {total_processed} processed, {total_skipped} skipped")
    
    if changes["updated"] or changes["added"]:
        print("\n🎉 Update successful! Your agents have been updated to the latest version.")
    else:
        print("\n✨ All agents are already up to date!")