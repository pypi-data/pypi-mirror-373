#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

"""
Capture Code Changes Hook
Tracks all file modifications made by Claude Code tools
Saves before/after snapshots of code changes
"""

import json
import sys
import sqlite3
import os
import time
import threading
from pathlib import Path
from datetime import datetime
import difflib

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def ensure_changes_dir():
    """Ensure code changes directory exists"""
    # Use same logic as stop.py to find project root
    current_dir = Path.cwd()
    if current_dir.name == 'hooks':
        base_dir = current_dir.parent.parent  # Go up from .claude/hooks to project root
    else:
        base_dir = current_dir
    changes_dir = base_dir / '.claude' / 'memory' / 'code_changes'
    changes_dir.mkdir(parents=True, exist_ok=True)
    return changes_dir


def read_file_safely(file_path):
    """Read file content safely, return None if doesn't exist"""
    try:
        path = Path(file_path)
        if path.exists():
            return path.read_text(encoding='utf-8')
    except Exception:
        pass
    return None


def create_diff(before, after, file_path):
    """Create a unified diff between two versions"""
    if before is None:
        return f"NEW FILE: {file_path}\n{after[:1000]}..."  # First 1000 chars
    
    if after is None:
        return f"DELETED FILE: {file_path}"
    
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile=f"{file_path} (before)",
        tofile=f"{file_path} (after)",
        lineterm=''
    )
    
    return ''.join(diff)


def get_session_id():
    """Get current session ID from database"""
    try:
        current_dir = Path.cwd()
        if current_dir.name == 'hooks':
            base_dir = current_dir.parent.parent
        else:
            base_dir = current_dir
        db_path = base_dir / '.claude' / 'memory' / 'project.db'
        
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM sessions WHERE ended_at IS NULL ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            conn.close()
            if result:
                return result[0]
    except Exception:
        pass
    return "session_unknown"


def save_change_record(tool_data):
    """Save a record of the code change"""
    try:
        tool_name = tool_data.get('tool_name', '')
        
        # Only process file modification tools
        if tool_name not in ['Write', 'Edit', 'MultiEdit', 'Update', 'NotebookEdit']:
            return
            
        tool_input = tool_data.get('tool_input', {})
        tool_result = tool_data.get('tool_result', {})
        tool_error = tool_data.get('tool_error')
        
        # Skip if there was an error
        if tool_error:
            return
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Extract file path based on tool
        file_path = None
        changes = []
        
        if tool_name == 'Write':
            file_path = tool_input.get('file_path', '')
            content = tool_input.get('content', '')
            before = read_file_safely(file_path)  # Might be None for new files
            changes.append({
                'file': file_path,
                'type': 'write',
                'before': before,
                'after': content,
                'diff': create_diff(before, content, file_path)
            })
            
        elif tool_name == 'Edit':
            file_path = tool_input.get('file_path', '')
            old_string = tool_input.get('old_string', '')
            new_string = tool_input.get('new_string', '')
            # Create a simple diff showing the change
            changes.append({
                'file': file_path,
                'type': 'edit',
                'before': old_string,
                'after': new_string,
                'diff': create_diff(old_string, new_string, file_path),
                'old_string': old_string[:100] + '...' if len(old_string) > 100 else old_string,
                'new_string': new_string[:100] + '...' if len(new_string) > 100 else new_string
            })
            
        elif tool_name == 'Update':
            # Update is similar to Edit
            file_path = tool_input.get('file_path', '')
            old_string = tool_input.get('old_string', '')
            new_string = tool_input.get('new_string', '')
            # For Update, the file has already been changed, so we need to reconstruct
            after = read_file_safely(file_path)
            before = after.replace(new_string, old_string) if after else old_string
            changes.append({
                'file': file_path,
                'type': 'update',
                'before': before,
                'after': after,
                'diff': create_diff(before, after, file_path),
                'old_string': old_string[:100] + '...' if len(old_string) > 100 else old_string,
                'new_string': new_string[:100] + '...' if len(new_string) > 100 else new_string
            })
            
        elif tool_name == 'MultiEdit':
            file_path = tool_input.get('file_path', '')
            edits = tool_input.get('edits', [])
            
            # Create a combined diff showing all changes
            combined_diff_parts = []
            for i, edit in enumerate(edits, 1):
                old_str = edit.get('old_string', '')
                new_str = edit.get('new_string', '')
                diff_part = create_diff(old_str, new_str, f"Edit {i}")
                if diff_part:
                    combined_diff_parts.append(diff_part)
            
            combined_diff = '\n'.join(combined_diff_parts) if combined_diff_parts else ''
            
            changes.append({
                'file': file_path,
                'type': 'multi_edit',
                'edits': edits,
                'diff': combined_diff,
                'edits_count': len(edits)
            })
            
        # Save to session JSON in chat directory
        if changes:
            # Get session ID and chat directory
            session_id = get_session_id()
            
            # Find chat directory (same logic as stop.py)
            current_dir = Path.cwd()
            if current_dir.name == 'hooks':
                base_dir = current_dir.parent.parent
            else:
                base_dir = current_dir
            chat_dir = base_dir / '.claude' / 'memory' / 'chat'
            chat_dir.mkdir(parents=True, exist_ok=True)
            
            # Build the change message with diff
            for change in changes:
                diff_text = change['diff'][:2000]  # Limit diff size for display
                
                # Create a code change message
                code_change_msg = {
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat(),
                    "content": f"Code change in {change['file']}:\n```diff\n{diff_text}\n```",
                    "type": "code_change",
                    "tool": tool_name
                }
                
                # Read existing session file with retry logic
                session_file = chat_dir / f"{session_id}.json"
                lock_file = chat_dir / f"{session_id}.lock"
                
                # Acquire lock with timeout
                max_retries = 50  # 5 seconds total
                for retry in range(max_retries):
                    if not lock_file.exists():
                        try:
                            # Create lock file atomically
                            lock_file.touch(exist_ok=False)
                            break
                        except FileExistsError:
                            pass
                    time.sleep(0.1)  # Wait 100ms before retry
                else:
                    # Timeout - skip this update
                    return
                
                try:
                    messages = []
                    if session_file.exists():
                        try:
                            with open(session_file, 'r', encoding='utf-8') as f:
                                messages = json.load(f)
                        except (json.JSONDecodeError, OSError):
                            messages = []
                    
                    # Add the code change message
                    messages.append(code_change_msg)
                    
                    # Write back atomically
                    temp_file = session_file.with_suffix('.tmp')
                    with open(temp_file, 'w', encoding='utf-8') as f:
                        json.dump(messages, f, indent=2, ensure_ascii=False)
                    temp_file.replace(session_file)
                    
                finally:
                    # Always release lock
                    if lock_file.exists():
                        lock_file.unlink()
                
            # Also save to database for easier querying
            save_to_database({'timestamp': datetime.now().isoformat(), 'tool': tool_name, 'session_id': session_id, 'changes': changes})
            
    except Exception as e:
        # Log error but don't break the tool
        print(f"Code change capture error: {e}", file=sys.stderr)


def save_to_database(change_data):
    """Save change record to SQLite database"""
    try:
        # Use same logic as stop.py to find project root
        current_dir = Path.cwd()
        if current_dir.name == 'hooks':
            base_dir = current_dir.parent.parent  # Go up from .claude/hooks to project root
        else:
            base_dir = current_dir
        db_path = base_dir / '.claude' / 'memory' / 'project.db'
        if not db_path.exists():
            return
            
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Create table if doesn't exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS code_changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                session_id TEXT,
                tool TEXT NOT NULL,
                file_path TEXT NOT NULL,
                change_type TEXT,
                diff_preview TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert change records
        for change in change_data['changes']:
            cursor.execute("""
                INSERT INTO code_changes (
                    timestamp, session_id, tool, file_path, 
                    change_type, diff_preview
                ) VALUES (?, ?, ?, ?, ?, ?)
            """, (
                change_data['timestamp'],
                change_data['session_id'],
                change_data['tool'],
                change['file'],
                change['type'],
                change['diff'][:500]  # Just preview in DB
            ))
        
        conn.commit()
        conn.close()
        
    except Exception:
        pass  # Fail silently


def main():
    try:
        # Read JSON input from stdin
        tool_data = json.load(sys.stdin)
        
        # Save the change record
        save_change_record(tool_data)
        
        # Always exit successfully to not interfere with tool
        sys.exit(0)
        
    except Exception:
        # Exit cleanly on any error
        sys.exit(0)


if __name__ == '__main__':
    main()