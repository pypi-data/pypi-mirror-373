"""
Init command for Acolytes - System initialization.

Initializes the Acolytes system with default configuration.
"""

import sys
import json
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
try:
    from importlib.resources import files
    use_importlib = True
except ImportError:
    # Fallback for older Python versions
    import pkg_resources
    use_importlib = False


def run() -> None:
    """Initialize Acolytes system."""
    print("🚀 Initializing Acolytes system...")
    
    try:
        # Step 1: Install uv if not present
        _install_uv_if_needed()
        
        # Step 2: Copy data files to ~/.claude/
        _copy_data_files()
        
        # Step 3: Generate settings.json
        _generate_settings_json()
        
        # Step 4: Create local project structure
        _create_local_project_structure()
        
        # Step 5: Show final status
        _show_final_status()
        
        print("✅ Initialization complete!")
        
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        sys.exit(1)


def _install_uv_if_needed() -> None:
    """Install uv if not present on the system."""
    print("🔍 Checking for uv installation...")
    
    # Check if uv is already installed
    try:
        subprocess.run(["uv", "--version"], check=True, capture_output=True, text=True)
        print("✅ uv is already installed")
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("📦 uv not found, installing...")
    
    system = platform.system().lower()
    
    try:
        if system == "windows":
            _install_uv_windows()
        else:
            _install_uv_unix()
        print("✅ uv installed successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not install uv automatically: {e}")
        print("💡 Please install uv manually from https://github.com/astral-sh/uv")


def _install_uv_windows() -> None:
    """Install uv on Windows using winget or PowerShell."""
    # Try winget first
    try:
        print("🔄 Attempting installation with winget...")
        subprocess.run(["winget", "install", "astral-sh.uv"], check=True, capture_output=True)
        return
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Fallback to PowerShell installer
    print("🔄 Attempting installation with PowerShell...")
    powershell_cmd = [
        "powershell", "-Command",
        "Invoke-RestMethod https://astral.sh/uv/install.ps1 | Invoke-Expression"
    ]
    subprocess.run(powershell_cmd, check=True)


def _install_uv_unix() -> None:
    """Install uv on Linux/Mac using curl."""
    print("🔄 Installing uv with curl...")
    curl_cmd = [
        "curl", "-LsSf", "https://astral.sh/uv/install.sh"
    ]
    sh_cmd = ["sh"]
    
    # Pipe curl output to sh
    curl_process = subprocess.Popen(curl_cmd, stdout=subprocess.PIPE)
    subprocess.run(sh_cmd, stdin=curl_process.stdout, check=True)
    curl_process.wait()


def _copy_data_files() -> None:
    """Copy data files to ~/.claude/ directory."""
    print("📂 Copying data files to ~/.claude/...")
    
    # Get target directory
    claude_dir = Path.home() / ".claude"
    claude_dir.mkdir(exist_ok=True)
    
    # Get package data directory
    try:
        if use_importlib:
            # Modern way using importlib.resources
            data_dir = Path(str(files('acolytes') / 'data'))
        else:
            # Fallback using pkg_resources
            data_dir = Path(pkg_resources.resource_filename('acolytes', 'data'))
    except Exception:
        # Fallback for development/editable installs
        current_dir = Path(__file__).parent.parent
        data_dir = current_dir / "data"
    
    if not data_dir.exists():
        raise FileNotFoundError(f"Data directory not found: {data_dir}")
    
    # Define directories to copy
    directories_to_copy = ['agents', 'commands', 'scripts', 'hooks', 'resources']
    total_files_copied = 0
    
    for dir_name in directories_to_copy:
        source_dir = data_dir / dir_name
        target_dir = claude_dir / dir_name
        
        if source_dir.exists():
            print(f"  📁 Copying {dir_name}/...")
            
            # Create target directory
            target_dir.mkdir(parents=True, exist_ok=True)
            
            # Copy files recursively
            files_copied = _copy_directory_contents(source_dir, target_dir)
            total_files_copied += files_copied
            print(f"    ✅ {files_copied} files copied")
        else:
            print(f"  ⚠️  Directory not found: {source_dir}")
    
    # Note: All agents (including setup.*, flags, plan) are now in the agents directory
    # No need for separate internal agents handling
    
    print(f"✅ Total files copied: {total_files_copied}")


def _copy_directory_contents(source: Path, target: Path) -> int:
    """Copy directory contents recursively and return file count."""
    files_copied = 0
    
    for item in source.rglob('*'):
        if item.is_file():
            # Calculate relative path
            rel_path = item.relative_to(source)
            target_file = target / rel_path
            
            # Create parent directories if needed
            target_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy file
            shutil.copy2(item, target_file)
            files_copied += 1
    
    return files_copied


def _generate_settings_json() -> None:
    """Generate settings.json configuration file."""
    print("⚙️  Generating settings.json...")
    
    claude_dir = Path.home() / ".claude"
    settings_file = claude_dir / "settings.json"
    
    # Detect Python command
    python_cmd = _detect_python_command()
    
    # Check if uv is available
    uv_available = _is_uv_available()
    
    # Generate settings
    settings = _create_settings_config(python_cmd, uv_available)
    
    # Write settings file
    with open(settings_file, 'w', encoding='utf-8') as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Settings saved to {settings_file}")


def _detect_python_command() -> str:
    """Detect the best Python command to use."""
    # List of candidates: can be single command or command with args
    candidates = [
        ['python3', '--version'],
        ['python', '--version'],
        ['py', '-3', '--version'],  # Windows launcher with Python 3
        ['py', '--version']          # Windows launcher fallback
    ]
    
    for cmd_list in candidates:
        try:
            result = subprocess.run(cmd_list, 
                                  capture_output=True, text=True, check=True)
            # Check both stdout and stderr (some versions print to stderr)
            output = result.stdout + result.stderr
            if 'Python 3' in output:
                # Return the command part (without --version)
                if cmd_list[0] == 'py' and len(cmd_list) > 2:
                    return 'py -3'  # Return Windows launcher with -3 flag
                return cmd_list[0]
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    
    # Default fallback
    return 'python'


def _is_uv_available() -> bool:
    """Check if uv is available on the system."""
    try:
        subprocess.run(['uv', '--version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def _create_settings_config(python_cmd: str, uv_available: bool) -> Dict[str, Any]:
    """Create the settings configuration dictionary in Claude Code format."""
    
    # Base Python command
    if uv_available:
        base_cmd = "uv run python"
    else:
        base_cmd = python_cmd
    
    # Get the correct path format based on OS
    # IMPORTANT: The hooks are installed in ~/.claude/ (user's home directory)
    # Windows doesn't expand ~ correctly, so we need absolute paths
    if platform.system() == 'Windows':
        # Windows needs full absolute path with forward slashes
        claude_path = str(Path.home() / ".claude").replace('\\', '/')
        script_prefix = claude_path
    else:
        # Unix-like systems can use ~/ which will be expanded by the shell
        script_prefix = "~/.claude"
    
    settings = {
        "permissions": {
            "allow": [
                "Bash(mkdir:*)",
                "Bash(uv:*)",
                "Bash(find:*)",
                "Bash(mv:*)",
                "Bash(grep:*)",
                "Bash(npm:*)",
                "Bash(ls:*)",
                "Bash(cp:*)",
                "Write",
                "Edit",
                "Bash(chmod:*)",
                "Bash(touch:*)"
            ],
            "deny": []
        },
        "statusLine": {
            "type": "command",
            "command": f"{base_cmd} {script_prefix}/scripts/status_line.py",
            "padding": 0
        },
        "disableAllHooks": False,
        "hooks": {
            "SessionStart": [
                {
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"{base_cmd} {script_prefix}/hooks/session_start.py"
                        }
                    ]
                }
            ],
            "PostToolUse": [
            {
                "matcher": "",
                "hooks": [
                {
                    "type": "command",
                    "command": "uv run python C:/Users/bextia/.claude/hooks/post_tool_use.py"
                }
                ]
            },
            {
                "matcher": "TodoWrite",
                "hooks": [
                {
                    "type": "command",
                    "command": "uv run python C:/Users/bextia/.claude/hooks/post_tool_use.py --todowrite"
                }
                ]
            },
            {
                "matcher": "Edit|Write|MultiEdit|Update",
                "hooks": [
                {
                    "type": "command",
                    "command": "uv run python C:/Users/bextia/.claude/hooks/capture_code_changes.py"
                }
                ]
            }
            ],
            "PreCompact": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"{base_cmd} {script_prefix}/hooks/pre_compact.py"
                        }
                    ]
                }
            ],
            "PreToolUse": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"{base_cmd} {script_prefix}/hooks/pre_tool_use.py"
                        }
                    ]
                }
            ],
            "UserPromptSubmit": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"{base_cmd} {script_prefix}/hooks/user_prompt_submit.py"
                        }
                    ]
                }
            ],
            "Stop": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"{base_cmd} {script_prefix}/hooks/stop.py --sound"
                        }
                    ]
                }
            ],
            "SubagentStop": [
                {
                    "matcher": "",
                    "hooks": [
                        {
                            "type": "command",
                            "command": f"{base_cmd} {script_prefix}/hooks/subagent_stop.py --sound"
                        }
                    ]
                }
            ]
        }
    }
    
    return settings


def _create_local_project_structure() -> None:
    """Create local .claude/ structure in current project directory."""
    print("[LOCAL] Creating local project structure...")
    
    # Get current working directory
    project_dir = Path.cwd()
    claude_project_dir = project_dir / ".claude"
    
    # Create main .claude directory
    claude_project_dir.mkdir(exist_ok=True)
    
    # Create subdirectories
    directories = {
        'project': claude_project_dir / 'project',
        'memory': claude_project_dir / 'memory',
        'memory_chat': claude_project_dir / 'memory' / 'chat',
        'agents': claude_project_dir / 'agents'
    }
    
    for name, path in directories.items():
        path.mkdir(parents=True, exist_ok=True)
        if name == 'memory_chat':
            print("  [OK] Created memory/chat/")
        else:
            print(f"  [OK] Created {name}/")
    
    # Create initial session files - ALWAYS use these hardcoded IDs
    # This ensures hooks work even before database exists
    chat_dir = directories['memory_chat']
    
    # Find available filenames with uniqueness guard
    base_name = "session_ac01e7e4e110"
    json_file = chat_dir / f"{base_name}.json"
    md_file = chat_dir / f"{base_name}.md"
    
    # If files exist, find next available number
    counter = 1
    while json_file.exists() or md_file.exists():
        json_file = chat_dir / f"{base_name}_{counter}.json"
        md_file = chat_dir / f"{base_name}_{counter}.md"
        counter += 1
    
    # Create JSON file with ISO timestamp
    timestamp = datetime.utcnow().isoformat() + "Z"
    json_content = {
        "session_id": "session_ac01e7e4e110",
        "job_id": "job_5e770c0deba5e",
        "created_at": timestamp,
        "messages": []
    }
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(json_content, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Created {json_file.name}")
    
    # Create MD file
    md_content = f"""# Session: session_ac01e7e4e110

## Job: Project Setup (job_5e770c0deba5e)

### Session Start
- **Created**: {timestamp}
- **Purpose**: Acolytes for Claude Code initialization

### Notes
This is the initial session created during project setup.

---
"""
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    print(f"  [OK] Created {md_file.name}")
    
    print(f"  [PATH] Project structure created at: {claude_project_dir}")


def _show_final_status() -> None:
    """Show final status and requirements check."""
    print("\n📋 Final Status Check:")
    
    claude_dir = Path.home() / ".claude"
    
    # Check directory structure
    required_dirs = ['agents', 'commands', 'scripts', 'hooks', 'resources']
    for dir_name in required_dirs:
        dir_path = claude_dir / dir_name
        if dir_path.exists():
            file_count = len(list(dir_path.rglob('*')))
            print(f"  ✅ {dir_name}/ ({file_count} files)")
        else:
            print(f"  ❌ {dir_name}/ (missing)")
    
    # Check settings file
    settings_file = claude_dir / "settings.json"
    if settings_file.exists():
        print("  ✅ settings.json")
    else:
        print("  ❌ settings.json (missing)")
    
    # Check Python and uv
    python_cmd = _detect_python_command()
    uv_available = _is_uv_available()
    
    print(f"  ✅ Python: {python_cmd}")
    if uv_available:
        print("  ✅ uv: available")
    else:
        print("  ⚠️  uv: not available (recommended)")
    
    print("\n💡 Next steps:")
    print("  1. Go to the path to your project")
    print("  2. Run: claude --dangerously-skip-permissions")
    print("  3. Type: /setup")
    print("  4. Y déjate fluir...")