#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

"""
SESSION START HOOK - Job Context Loader

This hook runs when Claude Code starts a new session and:

1. Finds existing ACTIVE session (ended_at IS NULL) and continues it
2. Loads context from entire job (all sessions)
3. Shows file activity from last session
4. Shows accomplishments and progress
5. If no active session exists, shows available jobs
6. Builds context from session summaries (accomplishments, decisions, pending tasks)
7. Loads CLAUDE.md project rules

Flow:
- Session starts → Hook finds active session → Loads job context
- Shows accomplishments, decisions, bugs fixed from entire job
- Shows file modifications from last session
- Provides context for continuing work
"""

import json
import sys
import sqlite3
import subprocess
import shutil
import os
from datetime import datetime

# Import Path and create alias
from pathlib import Path as PathLib

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def backup_database():
    """Create database backup with timestamp and maintain max 10 files"""
    try:
        # Use explicit path construction to avoid any scope issues
        db_path = PathLib("sandbox/project.db")
        if not db_path.exists():
            return
        
        # Create backup directory
        backup_dir = PathLib(".claude/memory/backup")
        backup_dir.mkdir(exist_ok=True)
        
        # Create backup filename with timestamp (no seconds)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        backup_filename = f"project_{timestamp}.db"
        backup_path = backup_dir / backup_filename
        
        # Copy database to backup
        shutil.copy2(str(db_path), str(backup_path))
        
        # Clean old backups - keep only 10 most recent
        backup_files = sorted(backup_dir.glob("project_*.db"), key=lambda f: f.stat().st_mtime)
        if len(backup_files) > 10:
            files_to_delete = backup_files[:-10]  # Remove all but last 10
            for old_file in files_to_delete:
                old_file.unlink()
                
    except (OSError, PermissionError, IOError) as e:
        # Backup failed but continue - don't break session start
        try:
            os.makedirs(".claude/memory", exist_ok=True)
            with open(".claude/memory/backup_errors.log", "a", encoding="utf-8") as f:
                f.write(f"{datetime.now()}: Backup failed - {e}\n")
        except (OSError, PermissionError):
            # If we can't log, continue silently to avoid breaking session start
            pass


def find_active_session():
    """Find existing active session (ended_at IS NULL) and return session info"""
    try:
        # Backup database first
        backup_database()
        
        db_path = PathLib("sandbox/project.db")
        if not db_path.exists():
            return None, "Database not found"
            
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Find active session (ended_at IS NULL)
        cursor.execute("""
            SELECT id, job_id, created_at, claude_session_id 
            FROM sessions 
            WHERE ended_at IS NULL 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        active_session = cursor.fetchone()
        
        if not active_session:
            # No active session found - show available jobs
            cursor.execute("SELECT id, title, status FROM jobs WHERE status = 'paused' ORDER BY created_at DESC LIMIT 3")
            paused_jobs = cursor.fetchall()
            
            conn.close()
            
            context_parts = [
                "WARNING: NO ACTIVE SESSION FOUND",
                "=" * 50,
                "",
                "No active session to continue. Run /save first to create new session.",
                "OR activate an existing job to create session manually:",
                ""
            ]
            
            if paused_jobs:
                context_parts.append("AVAILABLE JOBS:")
                for job in paused_jobs:
                    title = job[1] or "No title"
                    context_parts.append(f"   - {job[0]} - {title} ({job[2]})")
                context_parts.append("")
                context_parts.append("To activate: UPDATE jobs SET status='active' WHERE id='job-id'")
            else:
                context_parts.append("No jobs available.")
            
            context_parts.append("")
            context_parts.append("Session flow: /save creates new session automatically")
            context_parts.append("=" * 50)
            
            return None, "\n".join(context_parts)
        
        session_info = {
            'session_id': active_session[0],
            'job_id': active_session[1],
            'created_at': active_session[2],
            'claude_session_id': active_session[3]
        }
        
        conn.close()
        return session_info, None
        
    except sqlite3.Error as e:
        return None, f"Database error: {str(e)}"
    except (OSError, IOError) as e:
        return None, f"File system error: {str(e)}"


def get_git_status():
    """Get current git status information."""
    try:
        # Get current branch
        branch_result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        
        # Get uncommitted changes count
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if status_result.returncode == 0:
            changes = status_result.stdout.strip().split('\n') if status_result.stdout.strip() else []
            uncommitted_count = len(changes)
        else:
            uncommitted_count = 0
        
        return current_branch, uncommitted_count
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        # Git not available or timeout
        return None, None
    except OSError:
        # System error running git
        return None, None


def load_job_context_from_db(session_info):
    """Load context from active session and its job
    
    Context loading process:
    1. Use the ACTIVE SESSION info provided
    2. Load sessions from the same job for context
    3. Build context from session summaries (accomplishments, decisions, pending)
    4. Load tool logs from last session for file changes
    5. Show modified files from previous sessions
    6. Show current session info and job progress
    
    This provides Claude with context about what was done and which files were modified.
    """
    try:
        db_path = PathLib("sandbox/project.db")
        if not db_path.exists():
            return None
            
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        context_parts = []
        
        # Get job info from active session
        if not session_info or not session_info.get('job_id'):
            conn.close()
            return "No job associated with current session"
        
        job_id = session_info['job_id']
        
        # Replace underscores in job ID to avoid markdown
        safe_job_id = job_id.replace('_', '＿')
        context_parts.append(f"💼 Current Job: {safe_job_id}")
        context_parts.append("=" * 50)
        
        # Get last completed session from this job for priority
        cursor.execute("""
            SELECT id, next_step, breakthrough_moment, 
                   accomplishments, ended_at
            FROM sessions 
            WHERE job_id = ? AND ended_at IS NOT NULL
            ORDER BY created_at DESC 
            LIMIT 1
        """, (job_id,))
        
        last_session = cursor.fetchone()
        if last_session:
            # Show accomplishments from last session
            if last_session['accomplishments']:
                try:
                    accs = json.loads(last_session['accomplishments'])
                    if isinstance(accs, list) and accs:
                        context_parts.append("📝 Recent work:")
                        for acc in accs[:3]:  # Show max 3 from last session
                            # Replace underscores to avoid italic markdown
                            safe_acc = acc.replace('_', '＿')
                            context_parts.append(f"   • {safe_acc}")
                except (json.JSONDecodeError, TypeError):
                    pass
            
            if last_session['next_step']:
                # Replace underscores in next step text
                safe_priority = last_session['next_step'].replace('_', '＿')
                context_parts.append(f"🎯 Next step: {safe_priority}")
            
            if last_session['breakthrough_moment']:
                # Replace underscores in breakthrough text
                safe_breakthrough = last_session['breakthrough_moment'].replace('_', '＿')
                context_parts.append(f"💡 Breakthrough: {safe_breakthrough}")
        
        # Get total sessions count for this job
        cursor.execute("""
            SELECT COUNT(*) as count, MIN(created_at) as started
            FROM sessions 
            WHERE job_id = ?
        """, (job_id,))
        
        stats = cursor.fetchone()
        if stats and stats['count'] > 0:
            context_parts.append(f"📊 Stats: {stats['count']} sessions since {stats['started']}")
        
        # Get ALL session data in single query
        cursor.execute("""
            SELECT accomplishments, decisions, bugs_fixed, created_at, ended_at 
            FROM sessions 
            WHERE job_id = ?
            ORDER BY created_at ASC
        """, (job_id,))
        
        all_accomplishments = []
        all_decisions = []
        all_bugs_fixed = []
        sessions_completed = 0
        
        # Helper function to parse JSON safely
        def parse_json_list(json_str):
            try:
                data = json.loads(json_str)
                return data if isinstance(data, list) else []
            except (json.JSONDecodeError, TypeError):
                return []
        
        for row in cursor.fetchall():
            if row['ended_at']:  # Only count completed sessions
                sessions_completed += 1
                
            if row['accomplishments']:
                all_accomplishments.extend(parse_json_list(row['accomplishments']))
            
            if row['decisions']:
                all_decisions.extend(parse_json_list(row['decisions']))
                    
            if row['bugs_fixed']:
                all_bugs_fixed.extend(parse_json_list(row['bugs_fixed']))
        
        # Show comprehensive job progress
        if all_accomplishments:
            context_parts.append(f"✅ Accomplishments ({len(all_accomplishments)} total):")
            for acc in all_accomplishments[-5:]:  # Show last 5
                # Replace underscores to avoid italic markdown
                safe_acc = acc.replace('_', '＿')
                context_parts.append(f"   • {safe_acc}")
                
        if all_decisions:
            # Replace underscores in decisions to avoid italic markdown
            safe_decisions = [d.replace('_', '＿') for d in all_decisions[-3:]]
            context_parts.append(f"🔍 Decisions ({len(all_decisions)} total): {' | '.join(safe_decisions)}")
                
        if all_bugs_fixed:
            # Replace underscores in bugs to avoid italic markdown  
            safe_bugs = [b.replace('_', '＿') for b in all_bugs_fixed[-3:]]
            context_parts.append(f"🐛 Bugs fixed ({len(all_bugs_fixed)} total): {' | '.join(safe_bugs)}")
                
        context_parts.append(f"📈 Progress: {sessions_completed} done, 1 active")
        
        # Load detailed tool logs from last completed session
        if last_session:
            context_parts.append("=" * 50)
            context_parts.append("📋 Last Session Activity")
            
            # Get ALL tool logs from last session to build complete picture
            cursor.execute("""
                SELECT tool_name, file_affected, success, timestamp
                FROM tool_logs 
                WHERE session_id = ? AND file_affected IS NOT NULL AND success = 1
                ORDER BY timestamp DESC
            """, (last_session['id'],))
            
            tool_logs = cursor.fetchall()
            if tool_logs:
                # Build file operation summary
                file_operations = {}  # file -> {read, write, edit counts}
                
                for log in tool_logs:
                    if log['file_affected']:
                        # Replace underscores with similar Unicode char to avoid markdown italic
                        # Using U+FF3F FULLWIDTH LOW LINE which looks like _ but isn't markdown
                        file_name = os.path.basename(log['file_affected']).replace('_', '＿')
                        if file_name not in file_operations:
                            file_operations[file_name] = {'read': 0, 'write': 0, 'edit': 0}
                        
                        tool = log['tool_name'].lower()
                        if 'read' in tool:
                            file_operations[file_name]['read'] += 1
                        elif 'write' in tool:
                            file_operations[file_name]['write'] += 1
                        elif 'edit' in tool or 'multiedit' in tool:
                            file_operations[file_name]['edit'] += 1
                
                # Show concise summary
                # Group by operation type
                edited_files = [f for f, ops in file_operations.items() if ops['edit'] > 0]
                written_files = [f for f, ops in file_operations.items() if ops['write'] > 0]
                read_files = [f for f, ops in file_operations.items() if ops['read'] > 0 and ops['edit'] == 0 and ops['write'] == 0]
                
                if edited_files:
                    files_list = ', '.join(sorted(edited_files)[:5])
                    if len(edited_files) > 5:
                        files_list += f" +{len(edited_files) - 5}"
                    context_parts.append(f"📝 Edited ({len(edited_files)}): {files_list}")
                
                if written_files:
                    files_list = ', '.join(sorted(written_files)[:5])
                    if len(written_files) > 5:
                        files_list += f" +{len(written_files) - 5}"
                    context_parts.append(f"✍️  Created ({len(written_files)}): {files_list}")
                
                if read_files:
                    files_list = ', '.join(sorted(read_files)[:3])
                    if len(read_files) > 3:
                        files_list += f" +{len(read_files) - 3}"
                    context_parts.append(f"👁️  Read ({len(read_files)}): {files_list}")
                
                context_parts.append(f"📁 Total: {len(file_operations)} files")
        
        # No need to show message count - Claude can query if needed
        
        conn.close()
        return "\n".join(context_parts)
        
    except sqlite3.Error as e:
        return f"Database error loading job context: {str(e)}"
    except (OSError, IOError) as e:
        return f"File system error loading job context: {str(e)}"
    except json.JSONDecodeError as e:
        return f"JSON parsing error in session data: {str(e)}"


def load_development_context():
    """Load git status and development context."""
    try:
        # Check if it's a git repo
        repo_check = subprocess.run(
            ['git', 'rev-parse', '--is-inside-work-tree'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if repo_check.returncode != 0:
            return "📁 Not a git repository"
        
        # Get current branch
        branch_result = subprocess.run(
            ['git', 'rev-parse', '--abbrev-ref', 'HEAD'],
            capture_output=True,
            text=True,
            timeout=5
        )
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"
        
        # Get uncommitted changes details
        status_result = subprocess.run(
            ['git', 'status', '--porcelain'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if status_result.returncode == 0 and status_result.stdout.strip():
            changes = status_result.stdout.strip().split('\n')
            modified = sum(1 for c in changes if c.startswith(' M') or c.startswith('M'))
            added = sum(1 for c in changes if c.startswith('??'))
            deleted = sum(1 for c in changes if c.startswith(' D') or c.startswith('D'))
            
            details = []
            if modified > 0:
                details.append(f"{modified} modified")
            if added > 0:
                details.append(f"{added} untracked")
            if deleted > 0:
                details.append(f"{deleted} deleted")
                
            return f"🔀 Git Repository | Branch: {branch} | Changes: {', '.join(details)}"
        else:
            return f"🔀 Git Repository | Branch: {branch} | ✅ Clean"
            
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
        return "📁 Git not available"
    except OSError:
        return "📁 Git error"


def main():
    try:
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Extract fields  
        source = input_data.get('source', 'unknown')  # "startup", "resume", or "clear"
        
        # Build context parts
        context_parts = []
        
        # Set current date/time context
        current_time = datetime.now()
        context_parts.append("=" * 50)
        context_parts.append(f"📅 {current_time.strftime('%A, %B %d, %Y - %H:%M')}")
        # Format source properly
        source_display = {
            'clear': '/clear command',
            'startup': '/startup command', 
            'resume': '/resume command',
            'unknown': 'unknown source'
        }.get(source, f'{source} command')
        context_parts.append(f"📍 Triggered by: {source_display}")
        
        # FIRST: Find ACTIVE SESSION (don't create new)
        session_info, error_msg = find_active_session()
        
        if error_msg:
            # No active session found or error
            context_parts.append(error_msg)
        else:
            context_parts.append("=" * 50)
            # Replace underscores in session ID to avoid markdown issues
            safe_session_id = session_info['session_id'].replace('_', '＿')
            context_parts.append(f"💡 Current Session: {safe_session_id}")
            
            # Load context from active session and its job
            db_context = load_job_context_from_db(session_info)
            if db_context:
                context_parts.append(db_context)
        
        # Add git status at the END
        dev_context = load_development_context()
        if dev_context:
            context_parts.append("=" * 50)
            context_parts.append(dev_context)
        
        # Add MANDATORY instruction for Claude to read last sessions
        context_parts.append("=" * 50)
        context_parts.append("🔴 MANDATORY: Read the last 2 sessions from current job for complete context:")
        if session_info and 'job_id' in session_info:
            context_parts.append(f"sqlite3 .claude/memory/project.db \"SELECT * FROM sessions WHERE job_id = '{session_info['job_id']}' ORDER BY created_at DESC LIMIT 2\"")
        else:
            # Fallback to get sessions from active job
            context_parts.append("sqlite3 .claude/memory/project.db \"SELECT * FROM sessions WHERE job_id = (SELECT id FROM jobs WHERE status = 'active') ORDER BY created_at DESC LIMIT 2\"")
        context_parts.append("This ensures you understand recent work and decisions before proceeding.")
        
        # If we have any context, output it
        if context_parts:
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "SessionStart",
                    "additionalContext": "\n".join(context_parts)
                }
            }
            print(json.dumps(output))
            sys.exit(0)
        
        # Success
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Invalid JSON input from Claude Code - exit cleanly
        sys.exit(0)
    except (sqlite3.Error, OSError, IOError):
        # Database or file system errors - exit cleanly to not break Claude
        sys.exit(0)
    except KeyboardInterrupt:
        # User interrupted - exit cleanly
        sys.exit(1)


if __name__ == '__main__':
    main()