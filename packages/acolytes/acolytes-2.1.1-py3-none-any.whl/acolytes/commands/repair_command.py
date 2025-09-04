"""
Repair command for Acolytes - System repair.

Repairs common configuration issues and corrupted files including:
- Fix settings.json with proper Python/uv detection
- Restore missing directories in ~/.claude/
- Restore missing core hooks from package data
- Fix file permissions on Unix systems
- Backup old configurations before changes
"""

import json
import os
import platform
import shutil
import stat
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import pkg_resources


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


class SystemRepairer:
    """System repair manager for Acolytes."""
    
    def __init__(self):
        self.repairs_made = 0
        self.warnings_found = 0
        self.backups_created = 0
        self.is_windows = platform.system() == "Windows"
        self.claude_dir = Path.home() / ".claude"
        
    def _print_header(self, title: str) -> None:
        """Print a section header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{title.center(60)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    
    def _print_action(self, description: str, status: str, message: str = "") -> None:
        """Print an action result with colored status."""
        status_colors = {
            "FIXED": Colors.GREEN,
            "RESTORED": Colors.GREEN,
            "CREATED": Colors.BLUE,
            "BACKED_UP": Colors.CYAN,
            "SKIP": Colors.YELLOW,
            "FAIL": Colors.RED,
            "WARN": Colors.YELLOW,
            "OK": Colors.GREEN,
            "INFO": Colors.WHITE
        }
        
        color = status_colors.get(status, Colors.WHITE)
        status_text = f"{color}[{status}]{Colors.RESET}"
        
        if message:
            print(f"  {description:<45} {status_text} {message}")
        else:
            print(f"  {description:<45} {status_text}")
        
        if status in ["FIXED", "RESTORED", "CREATED"]:
            self.repairs_made += 1
        elif status == "BACKED_UP":
            self.backups_created += 1
        elif status in ["WARN", "SKIP"]:
            self.warnings_found += 1
    
    def _run_command(self, cmd: List[str], capture_output: bool = True) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=10
            )
            return result.returncode == 0, result.stdout.strip()
        except (subprocess.TimeoutExpired, subprocess.SubprocessError, FileNotFoundError):
            return False, ""
    
    def _detect_python_commands(self) -> Dict[str, Optional[str]]:
        """Detect available Python and package manager commands."""
        commands = {
            "python": None,
            "pip": None,
            "uv": None
        }
        
        # Test Python commands
        python_candidates = ["python", "python3", "py"]
        for cmd in python_candidates:
            success, output = self._run_command([cmd, "--version"])
            if success and "Python" in output:
                commands["python"] = cmd
                break
        
        # Test uv
        success, output = self._run_command(["uv", "--version"])
        if success:
            commands["uv"] = "uv"
        
        # Test pip (prefer with detected python)
        if commands["python"]:
            success, _ = self._run_command([commands["python"], "-m", "pip", "--version"])
            if success:
                commands["pip"] = f"{commands['python']} -m pip"
        
        # Fallback to global pip
        if not commands["pip"]:
            success, _ = self._run_command(["pip", "--version"])
            if success:
                commands["pip"] = "pip"
        
        return commands
    
    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """Create a backup of a file with timestamp."""
        if not file_path.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = file_path.with_suffix(f".backup_{timestamp}{file_path.suffix}")
        
        try:
            shutil.copy2(file_path, backup_path)
            return backup_path
        except Exception as e:
            self._print_action(f"Backup {file_path.name}", "WARN", f"failed: {e}")
            return None
    
    def repair_settings_json(self) -> None:
        """Fix settings.json with proper Python/uv detection and valid JSON."""
        self._print_header("Settings.json Repair")
        
        settings_file = self.claude_dir / "settings.json"
        
        # Detect available commands
        commands = self._detect_python_commands()
        
        # Create backup if file exists
        if settings_file.exists():
            backup_path = self._create_backup(settings_file)
            if backup_path:
                self._print_action("Backup settings.json", "BACKED_UP", backup_path.name)
        
        # Try to load existing settings if valid
        existing_settings = {}
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    existing_settings = json.load(f)
                self._print_action("Parse existing settings", "OK", "JSON valid")
            except json.JSONDecodeError as e:
                self._print_action("Parse existing settings", "WARN", f"JSON invalid: {e}")
            except Exception as e:
                self._print_action("Read existing settings", "WARN", f"error: {e}")
        
        # Generate new settings with detected commands
        new_settings = {
            "hooks": {},
            "mcpServers": {
                "MCP_SQLite_Server": {
                    "command": commands.get("uv") or commands.get("python") or "python",
                    "args": []
                }
            }
        }
        
        # Add uv-specific configuration if available
        if commands.get("uv"):
            new_settings["mcpServers"]["MCP_SQLite_Server"]["args"] = [
                "run", "--with", "mcp-server-sqlite", "--", 
                "mcp-server-sqlite", "--db-path", str(self.claude_dir / "memory" / "project.db")
            ]
            self._print_action("Detected package manager", "INFO", "uv (preferred)")
        elif commands.get("python"):
            new_settings["mcpServers"]["MCP_SQLite_Server"]["args"] = [
                "-m", "mcp_server_sqlite", 
                "--db-path", str(self.claude_dir / "memory" / "project.db")
            ]
            self._print_action("Detected package manager", "INFO", f"pip with {commands['python']}")
        else:
            self._print_action("Detected package manager", "WARN", "none found")
        
        # Merge with existing hook configuration if valid
        if isinstance(existing_settings.get("hooks"), dict):
            new_settings["hooks"] = existing_settings["hooks"]
            self._print_action("Preserve hook configuration", "OK", f"{len(existing_settings['hooks'])} hooks")
        
        # Add core hooks configuration if missing
        core_hooks = [
            "session_start.py",
            "todo_sync.py", 
            "pre_tool_use.py",
            "post_tool_use.py",
            "stop.py",
            "subagent_stop.py",
            "user_prompt_submit.py",
            "pre_compact.py"
        ]
        
        hooks_dir = self.claude_dir / "hooks"
        hooks_added = 0
        
        for hook_file in core_hooks:
            hook_path = hooks_dir / hook_file
            if hook_path.exists() and hook_file not in new_settings["hooks"]:
                new_settings["hooks"][hook_file.replace(".py", "")] = f"hooks/{hook_file}"
                hooks_added += 1
        
        if hooks_added > 0:
            self._print_action("Added hook configuration", "FIXED", f"{hooks_added} hooks")
        
        # Preserve other existing settings
        for key, value in existing_settings.items():
            if key not in new_settings:
                new_settings[key] = value
        
        # Write new settings
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(new_settings, f, indent=2, ensure_ascii=False)
            self._print_action("Write settings.json", "FIXED", "JSON syntax corrected")
        except Exception as e:
            self._print_action("Write settings.json", "FAIL", f"error: {e}")
    
    def restore_directories(self) -> None:
        """Restore missing directories in ~/.claude/."""
        self._print_header("Directory Structure Repair")
        
        required_directories = [
            "agents",
            "hooks",
            "scripts", 
            "memory",
            "resources",
            "commands",
            "resources/rules",
            "resources/templates",
            "resources/sfx",
            "docs"
        ]
        
        # Create ~/.claude if it doesn't exist
        if not self.claude_dir.exists():
            try:
                self.claude_dir.mkdir(parents=True, exist_ok=True)
                self._print_action("Create ~/.claude", "CREATED", str(self.claude_dir))
            except Exception as e:
                self._print_action("Create ~/.claude", "FAIL", f"error: {e}")
                return
        
        # Create required subdirectories
        dirs_created = 0
        for dir_path in required_directories:
            full_path = self.claude_dir / dir_path
            
            if not full_path.exists():
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    dirs_created += 1
                    self._print_action(f"Create {dir_path}", "CREATED", str(full_path.relative_to(self.claude_dir)))
                except Exception as e:
                    self._print_action(f"Create {dir_path}", "FAIL", f"error: {e}")
            else:
                self._print_action(f"Directory {dir_path}", "OK", "exists")
        
        if dirs_created == 0:
            self._print_action("Directory structure", "OK", "all directories present")
        else:
            self._print_action("Directories restored", "FIXED", f"{dirs_created} created")
    
    def restore_hooks(self) -> None:
        """Restore missing hooks from package data."""
        self._print_header("Hook Restoration")
        
        hooks_dir = self.claude_dir / "hooks"
        
        if not hooks_dir.exists():
            self._print_action("Hook restoration", "SKIP", "hooks directory missing")
            return
        
        # Core hooks that should always be present
        core_hooks = [
            "session_start.py",
            "todo_sync.py",
            "pre_tool_use.py", 
            "post_tool_use.py",
            "stop.py",
            "subagent_stop.py",
            "user_prompt_submit.py",
            "pre_compact.py"
        ]
        
        hooks_restored = 0
        
        for hook_name in core_hooks:
            hook_path = hooks_dir / hook_name
            
            if hook_path.exists():
                self._print_action(f"Hook {hook_name}", "OK", "exists")
                continue
            
            # Try to restore from package data
            try:
                # Get the hook content from package data
                resource_path = f"acolytes/data/hooks/{hook_name}"
                
                if pkg_resources.resource_exists('acolytes', f'data/hooks/{hook_name}'):
                    hook_content = pkg_resources.resource_string('acolytes', f'data/hooks/{hook_name}')
                    
                    # Write the hook file
                    with open(hook_path, 'wb') as f:
                        f.write(hook_content)
                    
                    hooks_restored += 1
                    self._print_action(f"Restore {hook_name}", "RESTORED", "from package data")
                else:
                    self._print_action(f"Restore {hook_name}", "WARN", "not found in package")
                    
            except Exception as e:
                self._print_action(f"Restore {hook_name}", "FAIL", f"error: {e}")
        
        if hooks_restored == 0:
            self._print_action("Hook restoration", "OK", "all core hooks present")
        else:
            self._print_action("Hooks restored", "FIXED", f"{hooks_restored} restored")
    
    def fix_permissions(self) -> None:
        """Fix file permissions on Unix systems."""
        if self.is_windows:
            self._print_header("Permission Repair")
            self._print_action("Permission repair", "SKIP", "Windows system")
            return
        
        self._print_header("Permission Repair")
        
        # Files that should be executable
        executable_patterns = [
            "scripts/*.py",
            "hooks/*.py"
        ]
        
        permissions_fixed = 0
        
        for pattern in executable_patterns:
            for file_path in self.claude_dir.glob(pattern):
                if file_path.is_file():
                    current_perms = file_path.stat().st_mode
                    
                    # Check if file is executable by owner
                    if not (current_perms & stat.S_IXUSR):
                        try:
                            # Add execute permission for owner
                            new_perms = current_perms | stat.S_IXUSR
                            file_path.chmod(new_perms)
                            permissions_fixed += 1
                            self._print_action(f"Fix permissions", "FIXED", file_path.name)
                        except Exception as e:
                            self._print_action(f"Fix {file_path.name}", "FAIL", f"error: {e}")
                    else:
                        self._print_action(f"Permissions {file_path.name}", "OK", "executable")
        
        if permissions_fixed == 0:
            self._print_action("File permissions", "OK", "all files properly configured")
        else:
            self._print_action("Permissions fixed", "FIXED", f"{permissions_fixed} files")
    
    def validate_repair(self) -> None:
        """Validate that repairs were successful."""
        self._print_header("Repair Validation")
        
        # Check settings.json syntax
        settings_file = self.claude_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    json.load(f)
                self._print_action("settings.json validation", "OK", "valid JSON")
            except json.JSONDecodeError:
                self._print_action("settings.json validation", "FAIL", "still invalid JSON")
        else:
            self._print_action("settings.json validation", "WARN", "file missing")
        
        # Check directory structure
        required_dirs = ["agents", "hooks", "scripts", "memory", "resources"]
        missing_dirs = []
        
        for dir_name in required_dirs:
            if not (self.claude_dir / dir_name).exists():
                missing_dirs.append(dir_name)
        
        if missing_dirs:
            self._print_action("Directory validation", "WARN", f"missing: {', '.join(missing_dirs)}")
        else:
            self._print_action("Directory validation", "OK", "all required directories present")
        
        # Check core hooks
        core_hooks = ["session_start.py", "todo_sync.py", "pre_tool_use.py"]
        missing_hooks = []
        
        hooks_dir = self.claude_dir / "hooks"
        for hook in core_hooks:
            if not (hooks_dir / hook).exists():
                missing_hooks.append(hook)
        
        if missing_hooks:
            self._print_action("Hook validation", "WARN", f"missing: {', '.join(missing_hooks)}")
        else:
            self._print_action("Hook validation", "OK", "core hooks present")
    
    def print_summary(self) -> None:
        """Print final summary of repair operations."""
        self._print_header("Repair Summary")
        
        print(f"  {Colors.GREEN}Repairs made:{Colors.RESET}        {self.repairs_made}")
        print(f"  {Colors.CYAN}Backups created:{Colors.RESET}     {self.backups_created}")
        print(f"  {Colors.YELLOW}Warnings found:{Colors.RESET}      {self.warnings_found}")
        
        if self.repairs_made == 0:
            if self.warnings_found == 0:
                print(f"\n{Colors.GREEN}{Colors.BOLD}✅ System is healthy!{Colors.RESET}")
                print(f"{Colors.GREEN}No repairs were necessary.{Colors.RESET}")
            else:
                print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  Minor issues found{Colors.RESET}")
                print(f"{Colors.YELLOW}System functional but has warnings.{Colors.RESET}")
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🔧 Repair completed successfully{Colors.RESET}")
            print(f"{Colors.GREEN}System issues have been resolved.{Colors.RESET}")
            
            # Show recommendations
            print(f"\n{Colors.CYAN}Recommendations:{Colors.RESET}")
            print(f"  {Colors.CYAN}• Run 'acolytes doctor' to verify all repairs{Colors.RESET}")
            print(f"  {Colors.CYAN}• Test Claude CLI functionality after repairs{Colors.RESET}")
            
            if self.backups_created > 0:
                print(f"  {Colors.CYAN}• Backup files created - remove when satisfied with repairs{Colors.RESET}")


def run() -> None:
    """
    Main entry point for the repair command.
    
    Performs comprehensive system repair including:
    - Fix settings.json with proper Python/uv detection
    - Restore missing directories in ~/.claude/
    - Restore missing core hooks from package data
    - Fix file permissions on Unix systems
    - Backup old configurations before changes
    """
    print(f"{Colors.BOLD}{Colors.MAGENTA}Acolytes System Repair{Colors.RESET}")
    print(f"{Colors.BLUE}Diagnosing and fixing system issues...{Colors.RESET}")
    
    repairer = SystemRepairer()
    
    try:
        # Run all repair operations
        repairer.repair_settings_json()
        repairer.restore_directories()
        repairer.restore_hooks()
        repairer.fix_permissions()
        repairer.validate_repair()
        
        # Print final summary
        repairer.print_summary()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Repair interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error during repair: {e}{Colors.RESET}")
        sys.exit(1)
    
    # Exit with appropriate code
    if repairer.repairs_made > 0:
        sys.exit(0)  # Successful repairs
    elif repairer.warnings_found > 0:
        sys.exit(2)  # Warnings found
    else:
        sys.exit(0)  # System was already healthy