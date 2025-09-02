"""
Backup command for Acolytes - System backup.

Creates backups of the current Acolytes installation.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


def run() -> None:
    """Backup Acolytes system with comprehensive functionality."""
    print("💾 Starting Acolytes system backup...")
    
    # Define paths
    claude_dir = Path.home() / ".claude"
    backup_root = Path.home() / ".claude_backups"
    
    if not claude_dir.exists():
        print("❌ ~/.claude directory not found. Nothing to backup.")
        return
    
    # Create backup directory if it doesn't exist
    backup_root.mkdir(exist_ok=True)
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = backup_root / f"backup_{timestamp}"
    
    try:
        # Show existing backups first
        print("\n📁 Existing backups:")
        list_existing_backups(backup_root)
        
        # Create the backup with progress
        print(f"\n🔄 Creating backup: {backup_dir.name}")
        file_count = copy_with_progress(claude_dir, backup_dir)
        
        # Calculate and show backup size
        backup_size = calculate_directory_size(backup_dir)
        human_size = format_bytes(backup_size)
        
        print(f"✅ Backup created successfully!")
        print(f"   📊 Files copied: {file_count:,}")
        print(f"   📏 Backup size: {human_size}")
        print(f"   📂 Location: {backup_dir}")
        
        # Cleanup old backups
        print("\n🧹 Cleaning up old backups...")
        cleanup_old_backups(backup_root, keep_count=5)
        
        # Show updated backup list
        print("\n📁 Current backups after cleanup:")
        list_existing_backups(backup_root)
        
    except Exception as e:
        print(f"❌ Backup failed: {str(e)}")
        # Clean up partial backup if it exists
        if backup_dir.exists():
            try:
                shutil.rmtree(backup_dir)
                print(f"🧹 Cleaned up partial backup: {backup_dir.name}")
            except Exception as cleanup_error:
                print(f"⚠️  Failed to cleanup partial backup: {cleanup_error}")
        raise


def copy_with_progress(source: Path, destination: Path) -> int:
    """Copy directory tree with progress indication.
    
    Args:
        source: Source directory to copy
        destination: Destination directory
        
    Returns:
        Number of files copied
    """
    file_count = 0
    
    def copy_function(src: str, dst: str) -> str:
        nonlocal file_count
        file_count += 1
        if file_count % 100 == 0:  # Show progress every 100 files
            print(f"   📄 Copied {file_count:,} files...", end="\r")
        return shutil.copy2(src, dst)
    
    # Use copytree with custom copy function for progress
    shutil.copytree(
        source,
        destination,
        copy_function=copy_function,
        ignore=shutil.ignore_patterns(
            '*.pyc', '__pycache__', '.DS_Store', 'Thumbs.db'
        )
    )
    
    print(f"   📄 Copied {file_count:,} files... Complete!")
    return file_count


def calculate_directory_size(directory: Path) -> int:
    """Calculate total size of directory in bytes.
    
    Args:
        directory: Directory to calculate size for
        
    Returns:
        Total size in bytes
    """
    total_size = 0
    
    try:
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = Path(dirpath) / filename
                try:
                    total_size += filepath.stat().st_size
                except (OSError, FileNotFoundError):
                    # Skip files that can't be accessed
                    continue
    except Exception:
        # Return 0 if we can't calculate size
        pass
    
    return total_size


def format_bytes(bytes_value: int) -> str:
    """Format bytes as human readable string.
    
    Args:
        bytes_value: Number of bytes
        
    Returns:
        Formatted string (e.g., '1.5 MB')
    """
    if bytes_value == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(bytes_value)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(size)} {units[unit_index]}"
    else:
        return f"{size:.1f} {units[unit_index]}"


def list_existing_backups(backup_root: Path) -> List[Tuple[str, str, str]]:
    """List existing backups with their sizes.
    
    Args:
        backup_root: Root directory containing backups
        
    Returns:
        List of tuples (backup_name, size, date)
    """
    if not backup_root.exists():
        print("   (No backups found)")
        return []
    
    backups = []
    
    try:
        # Get all backup directories
        backup_dirs = [
            d for d in backup_root.iterdir() 
            if d.is_dir() and d.name.startswith('backup_')
        ]
        
        if not backup_dirs:
            print("   (No backups found)")
            return []
        
        # Sort by modification time (newest first)
        backup_dirs.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        for backup_dir in backup_dirs:
            try:
                # Calculate size
                size_bytes = calculate_directory_size(backup_dir)
                size_formatted = format_bytes(size_bytes)
                
                # Extract date from directory name
                # backup_YYYYMMDD_HHMMSS -> YYYY-MM-DD HH:MM:SS
                name_parts = backup_dir.name.split('_')
                if len(name_parts) >= 3:
                    date_part = name_parts[1]
                    time_part = name_parts[2]
                    try:
                        date_formatted = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]} {time_part[:2]}:{time_part[2:4]}:{time_part[4:6]}"
                    except (IndexError, ValueError):
                        date_formatted = backup_dir.name
                else:
                    date_formatted = backup_dir.name
                
                backups.append((backup_dir.name, size_formatted, date_formatted))
                print(f"   📦 {backup_dir.name:<20} | {size_formatted:>10} | {date_formatted}")
                
            except Exception as e:
                print(f"   ⚠️  {backup_dir.name} (error reading: {e})")
        
    except Exception as e:
        print(f"   ❌ Error listing backups: {e}")
    
    return backups


def cleanup_old_backups(backup_root: Path, keep_count: int = 5) -> List[str]:
    """Remove old backups, keeping only the most recent ones.
    
    Args:
        backup_root: Root directory containing backups
        keep_count: Number of backups to keep (default: 5)
        
    Returns:
        List of removed backup names
    """
    removed_backups = []
    
    try:
        # Get all backup directories
        backup_dirs = [
            d for d in backup_root.iterdir()
            if d.is_dir() and d.name.startswith('backup_')
        ]
        
        if len(backup_dirs) <= keep_count:
            print(f"   ✅ No cleanup needed ({len(backup_dirs)} backups <= {keep_count} limit)")
            return removed_backups
        
        # Sort by modification time (oldest first for removal)
        backup_dirs.sort(key=lambda x: x.stat().st_mtime)
        
        # Remove oldest backups beyond the keep_count
        backups_to_remove = backup_dirs[:-keep_count]
        
        for backup_dir in backups_to_remove:
            try:
                size_bytes = calculate_directory_size(backup_dir)
                size_formatted = format_bytes(size_bytes)
                
                shutil.rmtree(backup_dir)
                removed_backups.append(backup_dir.name)
                print(f"   🗑️  Removed: {backup_dir.name} ({size_formatted})")
                
            except Exception as e:
                print(f"   ⚠️  Failed to remove {backup_dir.name}: {e}")
        
        if removed_backups:
            print(f"   ✅ Cleaned up {len(removed_backups)} old backup(s)")
        
    except Exception as e:
        print(f"   ❌ Error during cleanup: {e}")
    
    return removed_backups