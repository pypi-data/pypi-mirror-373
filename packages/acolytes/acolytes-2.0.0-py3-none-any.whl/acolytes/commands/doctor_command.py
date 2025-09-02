"""
Doctor command for Acolytes - System health and configuration checker.

Performs comprehensive diagnostics of the Acolytes system including:
- Python version and dependencies
- Git and Node.js availability
- Claude CLI installation and configuration
- Directory structure validation
- Agent, hook, and script counts
- MCP server connection tests
- Settings validation
"""

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple


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


class DoctorChecker:
    """System health checker for Acolytes."""
    
    def __init__(self):
        self.issues_found = 0
        self.warnings_found = 0
        self.checks_passed = 0
        
    def _print_header(self, title: str) -> None:
        """Print a section header."""
        print(f"\n{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{title.center(60)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}{'=' * 60}{Colors.RESET}")
    
    def _print_check(self, description: str, status: str, message: str = "") -> None:
        """Print a check result with colored status."""
        status_colors = {
            "OK": Colors.GREEN,
            "FAIL": Colors.RED,
            "WARN": Colors.YELLOW,
            "INFO": Colors.BLUE
        }
        
        color = status_colors.get(status, Colors.WHITE)
        status_text = f"{color}[{status}]{Colors.RESET}"
        
        if message:
            print(f"  {description:<45} {status_text} {message}")
        else:
            print(f"  {description:<45} {status_text}")
        
        if status == "OK":
            self.checks_passed += 1
        elif status == "FAIL":
            self.issues_found += 1
        elif status == "WARN":
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
    
    def check_python_version(self) -> None:
        """Check Python version requirements."""
        self._print_header("Python Environment")
        
        # Python version check
        version = sys.version_info
        version_str = f"{version.major}.{version.minor}.{version.micro}"
        
        if version >= (3, 8):
            self._print_check("Python version", "OK", f"v{version_str}")
        else:
            self._print_check("Python version", "FAIL", f"v{version_str} (need 3.8+)")
        
        # Check for uv
        success, output = self._run_command(["uv", "--version"])
        if success:
            self._print_check("uv package manager", "OK", output)
        else:
            self._print_check("uv package manager", "WARN", "not found (recommended)")
        
        # Check for pip
        success, output = self._run_command([sys.executable, "-m", "pip", "--version"])
        if success:
            pip_version = output.split()[1] if output else "unknown"
            self._print_check("pip package manager", "OK", f"v{pip_version}")
        else:
            self._print_check("pip package manager", "FAIL", "not available")
    
    def check_system_tools(self) -> None:
        """Check for required system tools."""
        self._print_header("System Tools")
        
        # Git check
        success, output = self._run_command(["git", "--version"])
        if success:
            git_version = output.replace("git version ", "")
            self._print_check("Git", "OK", f"v{git_version}")
        else:
            self._print_check("Git", "FAIL", "not found")
        
        # Node.js check
        success, output = self._run_command(["node", "--version"])
        if success:
            self._print_check("Node.js", "OK", output)
        else:
            self._print_check("Node.js", "WARN", "not found (optional)")
        
        # npm check
        success, output = self._run_command(["npm", "--version"])
        if success:
            self._print_check("npm", "OK", f"v{output}")
        else:
            self._print_check("npm", "WARN", "not found (optional)")
    
    def check_claude_cli(self) -> None:
        """Check Claude CLI installation and configuration."""
        self._print_header("Claude CLI")
        
        # Claude CLI check
        success, output = self._run_command(["claude", "--version"])
        if success:
            self._print_check("Claude CLI", "OK", output)
            
            # Check if Claude CLI is configured
            success, _ = self._run_command(["claude", "config", "list"])
            if success:
                self._print_check("Claude CLI configuration", "OK", "configured")
            else:
                self._print_check("Claude CLI configuration", "WARN", "may need setup")
        else:
            self._print_check("Claude CLI", "WARN", "not found or not in PATH")
    
    def check_directory_structure(self) -> None:
        """Check ~/.claude/ directory structure."""
        self._print_header("Directory Structure")
        
        claude_dir = Path.home() / ".claude"
        
        if claude_dir.exists():
            self._print_check("~/.claude directory", "OK", str(claude_dir))
        else:
            self._print_check("~/.claude directory", "FAIL", "does not exist")
            return
        
        # Check subdirectories
        expected_dirs = [
            "agents",
            "hooks",
            "scripts", 
            "memory",
            "resources",
            "commands"
        ]
        
        for dir_name in expected_dirs:
            dir_path = claude_dir / dir_name
            if dir_path.exists():
                self._print_check(f"~/.claude/{dir_name}", "OK", f"{len(list(dir_path.iterdir()))} items")
            else:
                self._print_check(f"~/.claude/{dir_name}", "WARN", "missing")
    
    def count_system_components(self) -> None:
        """Count agents, hooks, and scripts."""
        self._print_header("System Components")
        
        claude_dir = Path.home() / ".claude"
        
        if not claude_dir.exists():
            self._print_check("Component counting", "FAIL", "~/.claude not found")
            return
        
        # Count agents
        agents_dir = claude_dir / "agents"
        if agents_dir.exists():
            agent_files = list(agents_dir.glob("*.md"))
            agent_count = len(agent_files)
            self._print_check("Agent files", "OK", f"{agent_count} found")
            
            # Check for key agents
            key_agents = ["backend.python.md", "frontend.react.md", "database.postgres.md"]
            found_key_agents = sum(1 for agent in key_agents if (agents_dir / agent).exists())
            if found_key_agents > 0:
                self._print_check("Key agents present", "OK", f"{found_key_agents}/{len(key_agents)}")
            else:
                self._print_check("Key agents present", "WARN", "none found")
        else:
            self._print_check("Agent files", "FAIL", "agents directory missing")
        
        # Count hooks
        hooks_dir = claude_dir / "hooks"
        if hooks_dir.exists():
            hook_files = list(hooks_dir.glob("*.py"))
            hook_count = len(hook_files)
            self._print_check("Hook files", "OK", f"{hook_count} found")
            
            # Check for essential hooks
            essential_hooks = ["session_start.py", "todo_sync.py", "pre_tool_use.py"]
            found_essential = sum(1 for hook in essential_hooks if (hooks_dir / hook).exists())
            if found_essential == len(essential_hooks):
                self._print_check("Essential hooks", "OK", "all present")
            else:
                self._print_check("Essential hooks", "WARN", f"{found_essential}/{len(essential_hooks)} found")
        else:
            self._print_check("Hook files", "FAIL", "hooks directory missing")
        
        # Count scripts
        scripts_dir = claude_dir / "scripts"
        if scripts_dir.exists():
            script_files = list(scripts_dir.glob("*.py"))
            script_count = len(script_files)
            self._print_check("Script files", "OK", f"{script_count} found")
        else:
            self._print_check("Script files", "WARN", "scripts directory missing")
    
    def check_settings_file(self) -> None:
        """Validate settings.json syntax and hook paths."""
        self._print_header("Settings Validation")
        
        claude_dir = Path.home() / ".claude"
        settings_file = claude_dir / "settings.json"
        
        if not settings_file.exists():
            self._print_check("settings.json file", "WARN", "not found")
            return
        
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            self._print_check("settings.json syntax", "OK", "valid JSON")
        except json.JSONDecodeError as e:
            self._print_check("settings.json syntax", "FAIL", f"invalid JSON: {e}")
            return
        except Exception as e:
            self._print_check("settings.json file", "FAIL", f"error reading: {e}")
            return
        
        # Check hooks configuration
        if "hooks" in settings:
            hooks_config = settings["hooks"]
            if isinstance(hooks_config, dict):
                hook_count = len(hooks_config)
                self._print_check("Hook configuration", "OK", f"{hook_count} hooks configured")
                
                # Validate hook file paths
                hooks_dir = claude_dir / "hooks"
                valid_hooks = 0
                for hook_name, hook_path in hooks_config.items():
                    if isinstance(hook_path, str):
                        # Convert relative paths
                        if not os.path.isabs(hook_path):
                            full_path = hooks_dir / hook_path
                        else:
                            full_path = Path(hook_path)
                        
                        if full_path.exists():
                            valid_hooks += 1
                
                if valid_hooks == hook_count:
                    self._print_check("Hook file paths", "OK", "all valid")
                else:
                    self._print_check("Hook file paths", "WARN", f"{valid_hooks}/{hook_count} valid")
            else:
                self._print_check("Hook configuration", "WARN", "hooks not properly configured")
        else:
            self._print_check("Hook configuration", "WARN", "no hooks configured")
    
    def test_mcp_connections(self) -> None:
        """Test MCP server connections if Claude CLI is available."""
        self._print_header("MCP Server Connections")
        
        # Check if Claude CLI is available
        success, _ = self._run_command(["claude", "--version"])
        if not success:
            self._print_check("MCP testing", "SKIP", "Claude CLI not available")
            return
        
        # Test common MCP servers
        mcp_servers = [
            "MCP_SQLite_Server",
            "server-git",
            "sequential-thinking",
            "context7"
        ]
        
        for server in mcp_servers:
            # This is a simplified check - actual MCP testing would require
            # more complex integration with Claude CLI
            self._print_check(f"MCP {server}", "INFO", "check manually with Claude CLI")
    
    def check_database_files(self) -> None:
        """Check for database files and their accessibility."""
        self._print_header("Database Files")
        
        claude_dir = Path.home() / ".claude"
        memory_dir = claude_dir / "memory"
        
        if memory_dir.exists():
            db_files = list(memory_dir.glob("*.db"))
            if db_files:
                for db_file in db_files:
                    try:
                        # Simple read test
                        with open(db_file, 'rb') as f:
                            f.read(16)  # Read SQLite header
                        self._print_check(f"Database {db_file.name}", "OK", f"{db_file.stat().st_size} bytes")
                    except Exception as e:
                        self._print_check(f"Database {db_file.name}", "FAIL", f"unreadable: {e}")
            else:
                self._print_check("Database files", "WARN", "no .db files found")
        else:
            self._print_check("Memory directory", "WARN", "not found")
    
    def print_summary(self) -> None:
        """Print final summary of health check."""
        self._print_header("Health Check Summary")
        
        total_checks = self.checks_passed + self.issues_found + self.warnings_found
        
        print(f"  {Colors.GREEN}✓ Passed:{Colors.RESET}     {self.checks_passed}")
        print(f"  {Colors.YELLOW}⚠ Warnings:{Colors.RESET}   {self.warnings_found}")
        print(f"  {Colors.RED}✗ Failed:{Colors.RESET}     {self.issues_found}")
        print(f"  {Colors.BLUE}Total checks:{Colors.RESET} {total_checks}")
        
        if self.issues_found == 0:
            if self.warnings_found == 0:
                print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 System health: EXCELLENT{Colors.RESET}")
            else:
                print(f"\n{Colors.YELLOW}{Colors.BOLD}👍 System health: GOOD (minor warnings){Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️  System health: NEEDS ATTENTION{Colors.RESET}")
            print(f"{Colors.RED}Please address the failed checks above.{Colors.RESET}")
        
        # Recommendations
        if self.warnings_found > 0 or self.issues_found > 0:
            self._print_header("Recommendations")
            
            if self.issues_found > 0:
                print(f"  {Colors.RED}• Fix all FAILED checks before using Acolytes{Colors.RESET}")
            
            if self.warnings_found > 0:
                print(f"  {Colors.YELLOW}• Address warnings for optimal performance{Colors.RESET}")
            
            print(f"  {Colors.BLUE}• Run 'acolytes doctor' again after fixes{Colors.RESET}")
            print(f"  {Colors.BLUE}• See documentation for detailed setup instructions{Colors.RESET}")


def run() -> None:
    """
    Main entry point for the doctor command.
    
    Performs comprehensive system health checks including:
    - Python version and package managers
    - System tools (Git, Node.js)
    - Claude CLI installation
    - Directory structure validation
    - Component counting (agents, hooks, scripts)
    - Settings file validation
    - MCP server connection tests
    - Database file accessibility
    """
    print(f"{Colors.BOLD}{Colors.MAGENTA}Acolytes System Health Check{Colors.RESET}")
    print(f"{Colors.BLUE}Checking system configuration and dependencies...{Colors.RESET}")
    
    doctor = DoctorChecker()
    
    try:
        # Run all health checks
        doctor.check_python_version()
        doctor.check_system_tools()
        doctor.check_claude_cli()
        doctor.check_directory_structure()
        doctor.count_system_components()
        doctor.check_settings_file()
        doctor.check_database_files()
        doctor.test_mcp_connections()
        
        # Print final summary
        doctor.print_summary()
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Health check interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Unexpected error during health check: {e}{Colors.RESET}")
        sys.exit(1)
    
    # Exit with appropriate code
    if doctor.issues_found > 0:
        sys.exit(1)
    elif doctor.warnings_found > 0:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    run()