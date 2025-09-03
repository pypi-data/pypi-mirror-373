#!/usr/bin/env python3
"""
Environment Check and Setup for Acolytes for Claude Code
Validates and installs required dependencies for the Acolytes for Claude Code system.
"""
import sys
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Tuple

def find_or_create_project_root() -> Path:
    """Find project root or create .claude structure in current directory"""
    current = Path.cwd()
    
    # First, try to find existing .claude directory
    temp = current
    while temp != temp.parent:
        if (temp / ".claude").exists():
            return temp
        temp = temp.parent
    
    # If no .claude found, use current directory as project root
    # and CREATE the necessary structure for MCP to work
    project_root = current
    print(f"Creating .claude structure in: {project_root}")
    
    # Create only the essential directories for MCP
    (project_root / ".claude").mkdir(exist_ok=True)
    (project_root / ".claude" / "memory").mkdir(exist_ok=True)
    (project_root / ".claude" / "project").mkdir(exist_ok=True)
    (project_root / ".claude" / "agents").mkdir(exist_ok=True)
    
    return project_root

class EnvironmentChecker:
    def __init__(self):
        self.results = {}
        self.errors = []
        self.warnings = []
        self.system_info = {
            'os': platform.system(),
            'version': platform.version(),
            'architecture': platform.architecture()[0],
            'python_version': sys.version
        }
        
        # Find or create project root during initialization
        self.project_root = find_or_create_project_root()
        self.claude_dir = self.project_root / ".claude"
    
    def check_python_version(self) -> Tuple[bool, str]:
        """Check Python version (3.8+ required)"""
        version = sys.version_info
        required_major, required_minor = 3, 8
        
        if version.major >= required_major and version.minor >= required_minor:
            return True, f"Python {version.major}.{version.minor}.{version.micro} OK"
        else:
            return False, f"Python {version.major}.{version.minor}.{version.micro} FAIL (requires 3.8+)"
    
    def check_git_version(self) -> Tuple[bool, str]:
        """Check Git version (2.0+ required)"""
        try:
            # WARNING: shell=True is insecure due to potential command injection/path traversal
            # but needed for Windows Git Bash compatibility until a better solution is found
            use_shell = sys.platform == 'win32'
            result = subprocess.run('git --version' if use_shell else ['git', '--version'], 
                                  capture_output=True, text=True, timeout=10, shell=use_shell)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # Extract version number
                import re
                version_match = re.search(r'git version (\d+\.\d+)', version_str)
                if version_match:
                    version = float(version_match.group(1))
                    if version >= 2.0:
                        return True, f"{version_str} OK"
                    else:
                        return False, f"{version_str} FAIL (requires 2.0+)"
                return False, f"{version_str} FAIL (version format unknown)"
            else:
                return False, "Git not found FAIL"
        except subprocess.TimeoutExpired:
            return False, "Git check timed out FAIL"
        except FileNotFoundError:
            return False, "Git not installed FAIL"
    
    def check_nodejs_version(self) -> Tuple[bool, str]:
        """Check Node.js version (18+ required for MCPs)"""
        try:
            # WARNING: shell=True is insecure due to potential command injection/path traversal
            # but needed for Windows Git Bash compatibility until a better solution is found
            use_shell = sys.platform == 'win32'
            result = subprocess.run('node --version' if use_shell else ['node', '--version'], 
                                  capture_output=True, text=True, timeout=10, shell=use_shell)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # Extract major version
                version_num = version_str.replace('v', '').split('.')[0]
                version_major = int(version_num)
                if version_major >= 18:
                    return True, f"Node.js {version_str} OK"
                else:
                    return False, f"Node.js {version_str} FAIL (requires v18+)"
            else:
                return False, "Node.js not found FAIL"
        except subprocess.TimeoutExpired:
            return False, "Node.js check timed out FAIL"
        except (FileNotFoundError, ValueError):
            return False, "Node.js not installed FAIL"
    
    def check_sqlite3(self) -> Tuple[bool, str]:
        """Check SQLite3 CLI tool (required for database initialization)"""
        try:
            # WARNING: shell=True is insecure due to potential command injection/path traversal
            # but needed for Windows Git Bash compatibility until a better solution is found
            use_shell = sys.platform == 'win32'
            result = subprocess.run('sqlite3 --version' if use_shell else ['sqlite3', '--version'], 
                                  capture_output=True, text=True, timeout=10, shell=use_shell)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                # SQLite3 version format: "3.40.1 2022-12-28 14:03:47 ..."
                return True, f"SQLite3 {version_str.split()[0] if version_str else 'unknown version'} OK"
            else:
                return False, "SQLite3 not working FAIL"
        except subprocess.TimeoutExpired:
            return False, "SQLite3 check timed out FAIL"
        except FileNotFoundError:
            return False, "SQLite3 not installed FAIL (required for database)"
    
    def check_uv_package_manager(self) -> Tuple[bool, str]:
        """Check uv package manager"""
        try:
            # WARNING: shell=True is insecure due to potential command injection/path traversal
            # but needed for Windows Git Bash compatibility until a better solution is found
            use_shell = sys.platform == 'win32'
            result = subprocess.run('uv --version' if use_shell else ['uv', '--version'], 
                                  capture_output=True, text=True, timeout=10, shell=use_shell)
            if result.returncode == 0:
                version_str = result.stdout.strip()
                return True, f"uv {version_str} OK"
            else:
                return False, "uv not working FAIL"
        except subprocess.TimeoutExpired:
            return False, "uv check timed out FAIL"
        except FileNotFoundError:
            return False, "uv not installed FAIL"
    
    def check_permissions(self) -> Tuple[bool, str]:
        """Check file system permissions"""
        try:
            test_file = self.claude_dir / "test_permissions"
            
            # Test write permission
            test_file.parent.mkdir(exist_ok=True)
            test_file.write_text("permission test")
            test_file.unlink()
            
            return True, "File system permissions OK"
        except Exception as e:
            return False, f"Permission error FAIL: {str(e)}"
    
    def check_directory_structure(self) -> Tuple[bool, str]:
        """Verify Acolytes for Claude Code global installation"""
        # Check GLOBAL installation at ~/.claude, not local project
        home = Path.home()
        global_claude = home / ".claude"
        
        # Essential directories that must exist in global installation
        required_dirs = ["scripts", "agents", "resources/templates", "commands", "hooks"]
        missing = []
        
        for dir_name in required_dirs:
            if not (global_claude / dir_name).exists():
                missing.append(f"~/.claude/{dir_name}")
        
        # Essential scripts that must exist for the system to work
        essential_scripts = [
            "environment_check.py",
            "setup_mcp.py",
            "agent_db.py",
            "save_session.py",
            "compact_memory.py"
        ]
        
        missing_scripts = []
        for script in essential_scripts:
            if not (global_claude / "scripts" / script).exists():
                missing_scripts.append(script)
        
        if missing:
            return False, f"Missing global directories FAIL: {', '.join(missing)}"
        elif missing_scripts:
            return False, f"Missing essential scripts FAIL: {', '.join(missing_scripts)}"
        else:
            return True, f"Acolytes system installed OK at ~/.claude/ ({global_claude})"
    
    def install_uv_if_missing(self) -> bool:
        """Attempt to install uv package manager"""
        print("\nAttempting to install uv package manager...")
        
        try:
            if self.system_info['os'] == 'Windows':
                # Windows: Use pip with timeout
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 'uv'
                ], capture_output=True, text=True, timeout=60)
            else:
                # Unix: Use safer curl installer without shell injection
                # Download script first, then execute
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as temp_script:
                    curl_result = subprocess.run([
                        'curl', '-LsSf', 'https://astral.sh/uv/install.sh'
                    ], capture_output=True, text=True, timeout=30)
                    
                    if curl_result.returncode != 0:
                        print("Failed to download uv installer")
                        return False
                    
                    temp_script.write(curl_result.stdout)
                    temp_script.flush()
                    
                    # Execute downloaded script safely
                    result = subprocess.run([
                        'sh', temp_script.name
                    ], capture_output=True, text=True, timeout=60)
                
                # Cleanup
                import os
                try:
                    os.unlink(temp_script.name)
                except OSError:
                    pass
            
            if result.returncode == 0:
                print("uv installed successfully")
                return True
            else:
                print(f"Failed to install uv: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error installing uv: {e}")
            return False
    
    def run_full_check(self, auto_install: bool = True) -> Dict:
        """Run all environment checks"""
        print("Acolytes for Claude Code Environment Check")
        print("=" * 42)
        
        # System info
        print(f"System: {self.system_info['os']} {self.system_info['architecture']}")
        print()
        
        # Run checks
        checks = [
            ("Python Version", self.check_python_version),
            ("Git Version", self.check_git_version),
            ("Node.js Version", self.check_nodejs_version),
            ("SQLite3 CLI", self.check_sqlite3),
            ("UV Package Manager", self.check_uv_package_manager),
            ("File Permissions", self.check_permissions),
            ("Directory Structure", self.check_directory_structure)
        ]
        
        for name, check_func in checks:
            success, message = check_func()
            print(f"{name:20}: {message}")
            self.results[name] = {"success": success, "message": message}
        
        # Auto-install uv if missing and requested
        if not self.results["UV Package Manager"]["success"] and auto_install:
            if self.install_uv_if_missing():
                success, message = self.check_uv_package_manager()
                print(f"{'UV (retry)':20}: {message}")
                self.results["UV Package Manager"] = {"success": success, "message": message}
        
        # Summary
        print("\n" + "=" * 40)
        failed_checks = [name for name, result in self.results.items() if not result["success"]]
        
        if not failed_checks:
            print("All environment checks passed!")
            print("Acolytes for Claude Code ready for setup")
            print("\nCOMPLETED")
        else:
            print(f"{len(failed_checks)} checks failed:")
            for check in failed_checks:
                print(f"   - {check}: {self.results[check]['message']}")
            
            print("\nInstallation recommendations:")
            self._print_installation_help(failed_checks)
            print("\nFAILED")
        
        return self.results
    
    def _print_installation_help(self, failed_checks: List[str]):
        """Print installation help for failed checks"""
        system = self.system_info['os']
        
        for check in failed_checks:
            if "Git" in check:
                if system == "Windows":
                    print("   Git: Download from https://git-scm.com/download/win")
                elif system == "Darwin":  # macOS
                    print("   Git: brew install git")
                else:  # Linux
                    print("   Git: sudo apt install git  (or equivalent for your distro)")
            
            elif "Node.js" in check:
                if system == "Windows":
                    print("   Node.js: Download from https://nodejs.org (LTS version)")
                elif system == "Darwin":  # macOS
                    print("   Node.js: brew install node")
                else:  # Linux
                    print("   Node.js: curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash - && sudo apt-get install -y nodejs")
            
            elif "SQLite3" in check:
                if system == "Windows":
                    print("   SQLite3: Download from https://sqlite.org/download.html")
                    print("           Extract sqlite3.exe to a folder in your PATH")
                elif system == "Darwin":  # macOS
                    print("   SQLite3: brew install sqlite")
                else:  # Linux
                    print("   SQLite3: sudo apt install sqlite3  (or equivalent for your distro)")
            
            elif "UV Package Manager" in check:
                if system == "Windows":
                    print("   uv: pip install uv")
                else:
                    print("   uv: curl -LsSf https://astral.sh/uv/install.sh | sh")
            
            elif "Directory Structure" in check:
                print("   Directory: Make sure you're in a project with .claude directory")
                print("   Expected structure: .claude/ .claude/scripts/ .claude/agents/")

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Acolytes for Claude Code Environment Check")
    parser.add_argument("--no-install", action="store_true", 
                       help="Don't attempt to auto-install missing dependencies")
    parser.add_argument("--json", action="store_true", 
                       help="Output results in JSON format")
    
    args = parser.parse_args()
    
    checker = EnvironmentChecker()
    results = checker.run_full_check(auto_install=not args.no_install)
    
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    
    # Exit code: 0 if all passed, 1 if any failed
    all_passed = all(result["success"] for result in results.values())
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()