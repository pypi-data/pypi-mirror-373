#!/usr/bin/env python3
"""
MCP Core Setup for Acolytes for Claude Code
Ensures all core MCP servers are installed.

Core MCPs required:
- code-index: Fast code search and indexing
- server-fetch: External API interactions
- sequential-thinking: Complex reasoning chains
- playwright: Browser automation and testing
- context7: Advanced context management
"""
import sys
import subprocess
import logging
import shutil

# Configure logging - only errors will show
logging.basicConfig(level=logging.ERROR, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

def get_installed_mcps():
    """Get list of currently installed MCPs
    
    Note: shell=True used for simple trusted command 'claude mcp list'
    """
    try:
        result = subprocess.run(
            "claude mcp list",
            shell=True,  # Simple trusted command, no user input
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return result.stdout.lower()  # Convert to lowercase for easier checking
        return ""
    except Exception as e:
        logger.error(f"Failed to check MCPs: {e}")
        return ""

def install_mcp(name, install_command):
    """Install a missing MCP
    
    Note: shell=True is required here because the claude CLI command
    includes complex arguments with '--' separators that need shell parsing.
    The commands are trusted constants from CORE_MCPS dict, not user input.
    """
    try:
        # Execute the installation (shell=True needed for claude CLI syntax)
        result = subprocess.run(
            install_command,
            shell=True,  # Required for claude CLI's complex argument structure
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            return True
        else:
            logger.error(f"Failed to install {name}: {result.stderr}")
            return False
        
    except Exception as e:
        logger.error(f"Failed to install {name}: {e}")
        return False

def check_prerequisites():
    """Check that required executables are available"""
    required_tools = {
        'npx': 'Node.js npx (install Node.js from https://nodejs.org)',
        'uvx': 'UV tool (install with: pip install uv)',
        'claude': 'Claude CLI (required for MCP management)'
    }
    
    missing_tools = []
    for tool, description in required_tools.items():
        if not shutil.which(tool):
            missing_tools.append(f"  - {tool}: {description}")
    
    if missing_tools:
        print("ERROR: Missing required tools:")
        print("\n".join(missing_tools))
        print("\nPlease install the missing tools before running this script.")
        return False
    
    return True

def ensure_core_mcps():
    """Ensure all core MCPs are installed"""
    
    # Check prerequisites first
    if not check_prerequisites():
        return False
    
    # Core MCPs with their verified installation commands
    CORE_MCPS = {
        "sequential-thinking": "claude mcp add sequential-thinking -s user -- npx @modelcontextprotocol/server-sequential-thinking",
        "server-fetch": "claude mcp add server-fetch -s user -- uvx mcp-server-fetch",
        "playwright": "claude mcp add playwright -s user -- npx @playwright/mcp@latest",
        "context7": "claude mcp add context7 -s user -t sse https://mcp.context7.com/sse",
        "code-index": "claude mcp add code-index -s user -- uvx code-index-mcp"
    }
    
    # Get currently installed MCPs
    installed_list = get_installed_mcps()
    
    # Check which MCPs are missing
    missing = []
    for mcp_name, install_cmd in CORE_MCPS.items():
        if mcp_name not in installed_list:
            missing.append(mcp_name)
    
    # Install missing MCPs
    failed = []
    for mcp_name in missing:
        if not install_mcp(mcp_name, CORE_MCPS[mcp_name]):
            failed.append(mcp_name)
    
    # Log results only if there were issues
    if failed:
        logger.error(f"Failed to install: {', '.join(failed)}")
        return False
    
    # Print success message if all MCPs are ready
    if not missing:
        print("All MCPs verified")
    elif not failed:
        print(f"Installed {len(missing)} MCPs successfully")
    
    return True

if __name__ == "__main__":
    try:
        success = ensure_core_mcps()
        if success:
            print("COMPLETED")
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        sys.exit(1)