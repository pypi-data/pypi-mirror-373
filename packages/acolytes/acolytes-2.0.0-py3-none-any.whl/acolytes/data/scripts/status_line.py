#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
#     "tiktoken",
# ]
# ///

import json
import sys
import subprocess
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional



def get_git_branch():
    """Get current git branch if in a git repository."""
    try:
        result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_git_status():
    """Get detailed git status indicators like terminal."""
    try:
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            timeout=2
        )
        
        if result.returncode == 0:
            changes = result.stdout.strip()
            if changes:
                lines = changes.split('\n')
                
                # Count different types
                untracked = 0
                modified = 0
                deleted = 0
                added = 0
                
                for line in lines:
                    if len(line) >= 2:
                        status_code = line[:2]
                        if '?' in status_code:
                            untracked += 1
                        elif 'M' in status_code:
                            modified += 1
                        elif 'D' in status_code:
                            deleted += 1
                        elif 'A' in status_code:
                            added += 1
                
                # Build status string simple
                status_parts = []
                if untracked > 0:
                    status_parts.append(f'?{untracked}')
                if modified > 0:
                    status_parts.append(f'~{modified}')
                if deleted > 0:
                    status_parts.append(f'-{deleted}')
                if added > 0:
                    status_parts.append(f'+{added}')
                
                return ' ' + ' '.join(status_parts) if status_parts else ''
        
        return ''
        
    except Exception:
        pass
    return ""


def get_current_job():
    """Get current active job from SQLite"""
    try:
        import sqlite3
        db_path = Path.cwd() / '.claude' / 'memory' / 'project.db'
        if not db_path.exists():
            return None
        
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM jobs WHERE status = 'active' ORDER BY created_at DESC LIMIT 1")
        job = cursor.fetchone()
        conn.close()
        
        return job[0] if job else None
    except Exception:
        return None


def get_repo_name():
    """Get repository name from git remote origin"""
    try:
        result = subprocess.run(
            ['git', 'config', '--get', 'remote.origin.url'],
            capture_output=True,
            text=True,
            timeout=2
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            # Extract repo name from URL (handles both HTTPS and SSH)
            if url.endswith('.git'):
                url = url[:-4]
            repo_name = url.split('/')[-1]
            return repo_name
    except Exception:
        pass
    return None

def check_analytics_dashboard():
    """Check if Claude Code Templates analytics dashboard is running"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('localhost', 3333))
        sock.close()
        return result == 0
    except Exception:
        return False

def generate_status_line(input_data):
    """Generate the status line based on input data."""
    parts = []
    
    # Repository name first
    repo_name = get_repo_name()
    if repo_name:
        parts.append(f"\033[36m{repo_name}\033[0m")  # Cyan color with brackets
    
    # Model display name (no brackets)
    model_info = input_data.get('model', {})
    model_name = model_info.get('display_name', 'Claude')
    parts.append(f"\033[33m{model_name}\033[0m")  # Yellow color
    
    
    # Git branch and status
    git_branch = get_git_branch()
    if git_branch:
        git_status = get_git_status()
        git_info = f"{git_branch}"
        if git_status:
            git_info += f" {git_status}"
        parts.append(f"\033[32m{git_info}\033[0m")  # Green color
    
    # Current job
    current_job = get_current_job()
    if current_job:
        parts.append(f"\033[35m{current_job}\033[0m")  # Magenta color
    
    # Analytics dashboard status
    if check_analytics_dashboard():
        parts.append("\033[94mDashboard ON\033[0m")  # Light blue color
    
    # Current time (hour:minute)
    current_time = datetime.now().strftime('%H:%M')
    parts.append(f"{current_time}")  # White/default color
    
    return " | ".join(parts)


def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Generate status line
        status_line = generate_status_line(input_data)
        
        
        # Output the status line (first line of stdout becomes the status line)
        print(status_line)
        
        # Success
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully - output basic status
        print("\033[31m[Claude] Unknown\033[0m")
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully - output basic status
        print("\033[31m[Claude] Error\033[0m")
        sys.exit(0)


if __name__ == '__main__':
    main()