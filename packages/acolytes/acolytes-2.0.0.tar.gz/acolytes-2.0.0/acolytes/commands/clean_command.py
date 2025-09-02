"""
Clean command for Acolytes - System cleanup and maintenance.

Performs comprehensive cleanup of the Acolytes system including:
- Removing orphaned .pyc and __pycache__ files
- Cleaning empty directories in ~/.claude/
- Removing duplicate agents (keeps newest)
- Fixing broken symlinks if any
- Shows what was cleaned with file counts
"""

import json
import os
import shutil
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'


class SystemCleaner:
    """System cleaner for Acolytes."""
    
    def __init__(self):
        self.files_removed = 0
        self.dirs_removed = 0
        self.duplicates_removed = 0
        self.symlinks_fixed = 0
        self.bytes_freed = 0
        
    def _print_header(self, title: str) -> None:
        """Print a section header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{title.center(60)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    
    def _print_action(self, description: str, status: str, message: str = "") -> None:
        """Print an action result with colored status."""
        status_colors = {
            "REMOVED": Colors.RED,
            "CLEANED": Colors.GREEN,
            "FIXED": Colors.YELLOW,
            "KEPT": Colors.BLUE,
            "SKIP": Colors.WHITE,
            "INFO": Colors.CYAN
        }
        
        color = status_colors.get(status, Colors.WHITE)
        status_text = f"{color}[{status}]{Colors.RESET}"
        
        if message:
            print(f"  {description:<45} {status_text} {message}")
        else:
            print(f"  {description:<45} {status_text}")
    
    def _format_bytes(self, bytes_count: int) -> str:
        """Format byte count in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f}{unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f}TB"
    
    def _get_file_size(self, file_path: Path) -> int:
        """Get file size safely."""
        try:
            return file_path.stat().st_size
        except (OSError, FileNotFoundError):
            return 0
    
    def clean_python_cache(self) -> None:
        """Remove orphaned .pyc files and __pycache__ directories."""
        self._print_header("Python Cache Cleanup")
        
        claude_dir = Path.home() / ".claude"
        
        if not claude_dir.exists():
            self._print_action("Python cache cleanup", "SKIP", "~/.claude not found")
            return
        
        pyc_files = []
        pycache_dirs = []
        
        # Find all .pyc files and __pycache__ directories
        for root, dirs, files in os.walk(claude_dir):
            root_path = Path(root)
            
            # Find .pyc files
            for file in files:
                if file.endswith('.pyc'):
                    pyc_file = root_path / file
                    pyc_files.append(pyc_file)
            
            # Find __pycache__ directories
            for dir_name in dirs[:]:  # Use slice to avoid modification during iteration
                if dir_name == '__pycache__':
                    pycache_dir = root_path / dir_name
                    pycache_dirs.append(pycache_dir)
        
        # Remove .pyc files
        removed_pyc = 0
        pyc_bytes = 0
        for pyc_file in pyc_files:
            try:
                file_size = self._get_file_size(pyc_file)
                pyc_file.unlink()
                removed_pyc += 1
                pyc_bytes += file_size
                self.files_removed += 1
                self.bytes_freed += file_size
            except Exception as e:
                self._print_action(f"Remove {pyc_file.name}", "SKIP", f"error: {e}")
        
        if removed_pyc > 0:
            self._print_action(".pyc files", "REMOVED", f"{removed_pyc} files ({self._format_bytes(pyc_bytes)})")
        else:
            self._print_action(".pyc files", "INFO", "none found")
        
        # Remove __pycache__ directories
        removed_cache_dirs = 0
        cache_bytes = 0
        for cache_dir in pycache_dirs:
            try:
                # Calculate directory size before removal
                dir_size = sum(self._get_file_size(f) for f in cache_dir.rglob('*') if f.is_file())
                shutil.rmtree(cache_dir)
                removed_cache_dirs += 1
                cache_bytes += dir_size
                self.dirs_removed += 1
                self.bytes_freed += dir_size
            except Exception as e:
                self._print_action(f"Remove {cache_dir.name}", "SKIP", f"error: {e}")
        
        if removed_cache_dirs > 0:
            self._print_action("__pycache__ directories", "REMOVED", f"{removed_cache_dirs} dirs ({self._format_bytes(cache_bytes)})")
        else:
            self._print_action("__pycache__ directories", "INFO", "none found")
    
    def clean_empty_directories(self) -> None:
        """Remove empty directories in ~/.claude/."""
        self._print_header("Empty Directory Cleanup")
        
        claude_dir = Path.home() / ".claude"
        
        if not claude_dir.exists():
            self._print_action("Empty directory cleanup", "SKIP", "~/.claude not found")
            return
        
        # Protected directories that should not be removed even if empty
        protected_dirs = {
            claude_dir / "agents",
            claude_dir / "hooks", 
            claude_dir / "scripts",
            claude_dir / "memory",
            claude_dir / "resources",
            claude_dir / "commands",
            claude_dir / "docs"
        }
        
        empty_dirs = []
        
        # Find empty directories (bottom-up to handle nested empty dirs)
        for root, dirs, files in os.walk(claude_dir, topdown=False):
            root_path = Path(root)
            
            # Skip if this is a protected directory
            if root_path in protected_dirs:
                continue
            
            # Check if directory is empty (no files and no subdirectories)
            try:
                if not any(root_path.iterdir()):  # Completely empty
                    empty_dirs.append(root_path)
                elif not files:  # No files, but check if all subdirs were removed
                    remaining_subdirs = [d for d in dirs if (root_path / d).exists()]
                    if not remaining_subdirs:
                        empty_dirs.append(root_path)
            except (OSError, PermissionError):
                continue
        
        # Remove empty directories
        removed_count = 0
        for empty_dir in empty_dirs:
            try:
                # Double-check it's still empty and not protected
                if empty_dir in protected_dirs:
                    continue
                
                if not any(empty_dir.iterdir()):
                    empty_dir.rmdir()
                    removed_count += 1
                    self.dirs_removed += 1
                    self._print_action(f"Empty directory", "REMOVED", str(empty_dir.relative_to(claude_dir)))
            except Exception as e:
                self._print_action(f"Remove {empty_dir.name}", "SKIP", f"error: {e}")
        
        if removed_count == 0:
            self._print_action("Empty directories", "INFO", "none found")
        else:
            self._print_action("Empty directories total", "CLEANED", f"{removed_count} removed")
    
    def remove_duplicate_agents(self) -> None:
        """Remove duplicate agents, keeping the newest version."""
        self._print_header("Duplicate Agent Cleanup")
        
        claude_dir = Path.home() / ".claude"
        agents_dir = claude_dir / "agents"
        
        if not agents_dir.exists():
            self._print_action("Duplicate agent cleanup", "SKIP", "agents directory not found")
            return
        
        # Group agents by base name (removing version suffixes)
        agent_groups: Dict[str, List[Path]] = defaultdict(list)
        
        for agent_file in agents_dir.glob("*.md"):
            # Extract base name by removing common version patterns
            base_name = agent_file.stem
            
            # Remove common version patterns: _v1, _v2, -old, -backup, -copy, etc.
            import re
            base_name = re.sub(r'[-_](v\d+|old|backup|copy|duplicate|\d+)$', '', base_name, flags=re.IGNORECASE)
            
            agent_groups[base_name].append(agent_file)
        
        # Find and remove duplicates
        duplicates_found = 0
        bytes_saved = 0
        
        for base_name, agent_files in agent_groups.items():
            if len(agent_files) <= 1:
                continue  # No duplicates
            
            # Sort by modification time (newest first)
            agent_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            newest_agent = agent_files[0]
            duplicates = agent_files[1:]
            
            self._print_action(f"Agent group '{base_name}'", "INFO", f"{len(agent_files)} versions found")
            
            for duplicate in duplicates:
                try:
                    file_size = self._get_file_size(duplicate)
                    duplicate.unlink()
                    duplicates_found += 1
                    bytes_saved += file_size
                    self.files_removed += 1
                    self.bytes_freed += file_size
                    self.duplicates_removed += 1
                    self._print_action(f"  Remove duplicate", "REMOVED", duplicate.name)
                except Exception as e:
                    self._print_action(f"  Remove {duplicate.name}", "SKIP", f"error: {e}")
            
            self._print_action(f"  Keep newest", "KEPT", newest_agent.name)
        
        if duplicates_found == 0:
            self._print_action("Duplicate agents", "INFO", "none found")
        else:
            self._print_action("Duplicate agents total", "CLEANED", f"{duplicates_found} removed ({self._format_bytes(bytes_saved)})")
    
    def fix_broken_symlinks(self) -> None:
        """Fix or remove broken symlinks."""
        self._print_header("Symlink Cleanup")
        
        claude_dir = Path.home() / ".claude"
        
        if not claude_dir.exists():
            self._print_action("Symlink cleanup", "SKIP", "~/.claude not found")
            return
        
        broken_symlinks = []
        
        # Find all symlinks
        for root, dirs, files in os.walk(claude_dir):
            root_path = Path(root)
            
            for item in files + dirs:
                item_path = root_path / item
                
                if item_path.is_symlink():
                    try:
                        # Check if symlink target exists
                        if not item_path.exists():
                            broken_symlinks.append(item_path)
                    except (OSError, RuntimeError):
                        broken_symlinks.append(item_path)
        
        # Handle broken symlinks
        fixed_count = 0
        for symlink in broken_symlinks:
            try:
                # For now, we'll just remove broken symlinks
                # In the future, we could try to fix them by finding the correct target
                symlink.unlink()
                fixed_count += 1
                self.symlinks_fixed += 1
                self._print_action(f"Broken symlink", "REMOVED", str(symlink.relative_to(claude_dir)))
            except Exception as e:
                self._print_action(f"Fix {symlink.name}", "SKIP", f"error: {e}")
        
        if fixed_count == 0:
            self._print_action("Broken symlinks", "INFO", "none found")
        else:
            self._print_action("Broken symlinks total", "FIXED", f"{fixed_count} removed")
    
    def clean_temp_files(self) -> None:
        """Clean temporary and backup files."""
        self._print_header("Temporary File Cleanup")
        
        claude_dir = Path.home() / ".claude"
        
        if not claude_dir.exists():
            self._print_action("Temp file cleanup", "SKIP", "~/.claude not found")
            return
        
        # Common temporary file patterns
        temp_patterns = [
            "*.tmp",
            "*.temp", 
            "*~",
            "*.bak",
            "*.backup",
            "*.orig",
            ".DS_Store",
            "Thumbs.db",
            "*.log.old",
            "*.log.*"  # Rotated log files
        ]
        
        temp_files = []
        
        for pattern in temp_patterns:
            temp_files.extend(claude_dir.rglob(pattern))
        
        # Remove temporary files
        removed_count = 0
        temp_bytes = 0
        
        for temp_file in temp_files:
            try:
                if temp_file.is_file():
                    file_size = self._get_file_size(temp_file)
                    temp_file.unlink()
                    removed_count += 1
                    temp_bytes += file_size
                    self.files_removed += 1
                    self.bytes_freed += file_size
                    self._print_action(f"Temp file", "REMOVED", temp_file.name)
            except Exception as e:
                self._print_action(f"Remove {temp_file.name}", "SKIP", f"error: {e}")
        
        if removed_count == 0:
            self._print_action("Temporary files", "INFO", "none found")
        else:
            self._print_action("Temporary files total", "CLEANED", f"{removed_count} files ({self._format_bytes(temp_bytes)})")
    
    def print_summary(self) -> None:
        """Print final summary of cleanup operation."""
        self._print_header("Cleanup Summary")
        
        print(f"  {Colors.GREEN}Files removed:{Colors.RESET}      {self.files_removed}")
        print(f"  {Colors.GREEN}Directories removed:{Colors.RESET} {self.dirs_removed}")
        print(f"  {Colors.YELLOW}Duplicates removed:{Colors.RESET}  {self.duplicates_removed}")
        print(f"  {Colors.BLUE}Symlinks fixed:{Colors.RESET}     {self.symlinks_fixed}")
        print(f"  {Colors.CYAN}Space freed:{Colors.RESET}        {self._format_bytes(self.bytes_freed)}")
        
        total_actions = self.files_removed + self.dirs_removed + self.symlinks_fixed
        
        if total_actions == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}System is already clean!{Colors.RESET}")
            print(f"{Colors.GREEN}No cleanup actions were necessary.{Colors.RESET}")
        elif total_actions < 10:
            print(f"\n{Colors.GREEN}{Colors.BOLD}Minor cleanup completed{Colors.RESET}")
            print(f"{Colors.GREEN}System maintenance performed successfully.{Colors.RESET}")
        else:
            print(f"\n{Colors.YELLOW}{Colors.BOLD}Major cleanup completed{Colors.RESET}")
            print(f"{Colors.YELLOW}Significant cleanup performed - system should run better now.{Colors.RESET}")
        
        # Show recommendations
        if self.bytes_freed > 1024 * 1024:  # More than 1MB freed
            print(f"\n{Colors.CYAN}Recommendation:{Colors.RESET}")
            print(f"  {Colors.CYAN}• Consider running cleanup regularly to maintain performance{Colors.RESET}")
            print(f"  {Colors.CYAN}• Monitor disk usage if you frequently modify agents{Colors.RESET}")


def run() -> None:
    """
    Main entry point for the clean command.
    
    Performs comprehensive system cleanup including:
    - Removing orphaned .pyc and __pycache__ files
    - Cleaning empty directories in ~/.claude/
    - Removing duplicate agents (keeps newest)
    - Fixing broken symlinks if any
    - Shows what was cleaned with file counts
    """
    print(f"{Colors.BOLD}{Colors.MAGENTA}Acolytes System Cleanup{Colors.RESET}")
    print(f"{Colors.BLUE}Cleaning orphaned files and optimizing system...{Colors.RESET}")
    
    cleaner = SystemCleaner()
    
    try:
        # Run all cleanup operations
        cleaner.clean_python_cache()
        cleaner.clean_temp_files()
        cleaner.clean_empty_directories()
        cleaner.remove_duplicate_agents()
        cleaner.fix_broken_symlinks()
        
        # Print final summary
        cleaner.print_summary()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Cleanup interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error during cleanup: {e}{Colors.RESET}")
        sys.exit(1)
    
    # Exit successfully
    sys.exit(0)


if __name__ == "__main__":
    run()