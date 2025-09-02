#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import sqlite3
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


def compute_quality_score(accomplishments, errors, breakthrough=None, decisions=None, bugs_fixed=None):
    """
    Compute session quality score based on content and outcomes.
    
    Args:
        accomplishments (list): List of accomplishment strings
        errors (list): List of error strings  
        breakthrough (str, optional): Breakthrough moment text
        decisions (list, optional): List of decision strings
        bugs_fixed (list, optional): List of bug fix strings
        
    Returns:
        int: Quality score from 1-10
        
    Advanced Scoring System:
        - Base score: 4 (neutral starting point - must earn higher scores)
        - Accomplishments: +0.5 per item (max +4)
        - Bugs fixed: +0.7 per bug (max +3) - bugs are valuable
        - Decisions: +0.3 per decision (max +2) - strategic value
        - Errors: -0.5 per error (max -3)
        - Breakthrough: +1 if >50 chars (substantial insight)
        - Rich content: +1 if total >800 chars
        - Perfect bonus: +1 if no errors and 3+ accomplishments
        - Final range: 1-10 (clamped)
    """
    score = 4.0  # neutral base - must earn good scores
    
    # Accomplishments contribution (valuable work done)
    if accomplishments:
        score += min(4.0, len(accomplishments) * 0.5)
    
    # Bugs fixed bonus (fixing bugs is high value)
    if bugs_fixed:
        score += min(3.0, len(bugs_fixed) * 0.7)
    
    # Decisions bonus (strategic thinking matters)
    if decisions:
        score += min(2.0, len(decisions) * 0.3)
    
    # Errors penalty (but learning from errors is ok)
    if errors:
        # Less penalty if we also fixed bugs (learning process)
        penalty_multiplier = 0.3 if bugs_fixed else 0.5
        score -= min(3.0, len(errors) * penalty_multiplier)
    
    # Breakthrough bonus (significant insights are rare and valuable)
    if breakthrough and len(breakthrough) > 50:
        score += 1.0
        # Extra bonus for really insightful breakthroughs
        if len(breakthrough) > 150:
            score += 0.5
    
    # Rich content bonus - detailed documentation is valuable
    total_content_length = 0
    total_content_length += sum(len(str(x)) for x in accomplishments) if accomplishments else 0
    total_content_length += sum(len(str(x)) for x in bugs_fixed) if bugs_fixed else 0
    total_content_length += sum(len(str(x)) for x in decisions) if decisions else 0
    total_content_length += len(breakthrough or "")
    
    if total_content_length > 800:
        score += 1.0
    elif total_content_length > 500:
        score += 0.5
    
    # Perfect session bonus (no errors + productive)
    if not errors and accomplishments and len(accomplishments) >= 3:
        score += 1.0
    
    # Special case: All bugs fixed, no new errors = excellent session
    if bugs_fixed and len(bugs_fixed) >= 2 and not errors:
        score += 0.5
    
    # Clamp to valid range [1, 10] and round to integer
    return max(1, min(10, round(score)))


def backup_database():
    """Create database backup with timestamp and maintain max 10 files"""
    try:
        # Use the project database
        db_path = get_project_db_path()
        if not db_path.exists():
            print("WARNING: Database does not exist, skipping backup")
            return False
        
        # Create backup directory in PROJECT
        backup_dir = db_path.parent / "backup"
        backup_dir.mkdir(exist_ok=True)
        
        # Create backup filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        backup_filename = f"project_{timestamp}.db"
        backup_path = backup_dir / backup_filename
        
        # Copy database to backup
        shutil.copy2(db_path, backup_path)
        
        # Clean old backups - keep only 10 most recent
        backup_files = sorted(backup_dir.glob("project_*.db"), key=lambda f: f.stat().st_mtime)
        if len(backup_files) > 10:
            files_to_delete = backup_files[:-10]
            for old_file in files_to_delete:
                old_file.unlink()
        
        return True
    except Exception as e:
        print(f"ERROR: Critical backup failure: {e}")
        return False


def parse_arguments():
    """Parse command line arguments for enhanced fields"""
    args = sys.argv[1:]
    
    # Build argument dictionary
    parsed = {}
    i = 0
    while i < len(args):
        if args[i].startswith('-'):
            key = args[i][1:]  # Remove leading dash
            if i + 1 < len(args) and not args[i + 1].startswith('-'):
                parsed[key] = args[i + 1]
                i += 2
            else:
                i += 1
        else:
            i += 1
    
    # Check for required fields (at least some content needed)
    if not parsed:
        print(json.dumps({
            "error": "No arguments provided",
            "usage": "script.py -primary_request '...' -technical_concepts '...' ..."
        }))
        return None
    
    return parsed


def parse_field_enhanced(text, separator="||"):
    """Parse field with separator, handling code blocks properly"""
    if not text:
        return []
    
    # Clean emojis
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    # Split by separator
    items = text.split(separator)
    
    # Clean and filter items
    cleaned = []
    for item in items:
        item = item.strip()
        if item and item.lower() not in ['none', 'n/a', 'nothing', 'empty']:
            cleaned.append(item)
    
    return cleaned


def parse_files_and_code(text):
    """Parse files_and_code field with special handling for code blocks"""
    if not text:
        return []
    
    files = []
    file_sections = text.split("||")
    
    for section in file_sections:
        if not section.strip():
            continue
            
        # Parse file components: path|importance|changes|code
        parts = section.split("|", 3)  # Max 4 parts
        if len(parts) >= 3:
            file_info = {
                "path": parts[0].strip(),
                "importance": parts[1].strip() if len(parts) > 1 else "",
                "changes": parts[2].strip() if len(parts) > 2 else "",
                "code": parts[3].strip() if len(parts) > 3 else ""
            }
            files.append(file_info)
    
    return files


def parse_errors_and_fixes(text):
    """Parse errors_and_fixes field with special structure"""
    if not text:
        return []
    
    errors = []
    error_sections = text.split("||")
    
    for section in error_sections:
        if not section.strip():
            continue
            
        # Parse error components: error|fix|user_feedback
        parts = section.split("|", 2)  # Max 3 parts
        if parts:
            error_info = {
                "error": parts[0].strip(),
                "fix": parts[1].strip() if len(parts) > 1 else "",
                "user_feedback": parts[2].strip() if len(parts) > 2 else ""
            }
            errors.append(error_info)
    
    return errors


def get_project_db_path():
    """Find the correct project database path"""
    # Try to find project database in current working directory first
    cwd_db = Path.cwd() / '.claude' / 'memory' / 'project.db'
    
    # If not found, look for .claude directory in parent directories
    current = Path.cwd()
    while current != current.parent:
        potential_db = current / '.claude' / 'memory' / 'project.db'
        if potential_db.exists():
            return potential_db
        current = current.parent
    
    # If still not found, check if we're in a subdirectory with .claude in parent
    if cwd_db.exists():
        return cwd_db
    
    # Default to current directory
    return Path.cwd() / ".claude" / "memory" / "project.db"

def get_current_session():
    """Get current active session"""
    try:
        # Use the project database
        db_path = get_project_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, job_id, created_at FROM sessions WHERE ended_at IS NULL ORDER BY created_at DESC LIMIT 1")
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise Exception("No active session found")
        return {'session_id': result[0], 'job_id': result[1], 'created_at': result[2]}
    except Exception as e:
        raise Exception(f"Failed to get session: {e}")


def save_to_database_enhanced(session_data, parsed_args):
    """Save enhanced session data to database"""
    try:
        # Parse all enhanced fields
        primary_request = parsed_args.get('primary_request', '')
        technical_concepts = parse_field_enhanced(parsed_args.get('technical_concepts', ''))
        files_and_code = parse_files_and_code(parsed_args.get('files_and_code', ''))
        errors_and_fixes = parse_errors_and_fixes(parsed_args.get('errors_and_fixes', ''))
        problem_solving = parsed_args.get('problem_solving', '')
        user_messages = parse_field_enhanced(parsed_args.get('user_messages', ''))
        pending_tasks = parse_field_enhanced(parsed_args.get('pending_tasks', ''))
        current_work = parsed_args.get('current_work', '')
        next_step = parsed_args.get('next_step', '')
        
        # Parse original fields (keeping for compatibility)
        accomplishments = parse_field_enhanced(parsed_args.get('accomplishments', ''))
        bugs_fixed = parse_field_enhanced(parsed_args.get('bugs_fixed', ''))
        decisions = parse_field_enhanced(parsed_args.get('decisions', ''))
        breakthrough = parsed_args.get('breakthrough', '')
        conversation_flow = parsed_args.get('conversation_flow', '')
        
        # Calculate duration
        for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:
            try:
                start_time = datetime.strptime(session_data['created_at'], fmt)
                break
            except ValueError:
                continue
        else:
            start_time = datetime.now()
        
        actual_duration = int((datetime.now() - start_time).total_seconds() / 60)
        
        # Calculate quality score
        quality_score = compute_quality_score(
            accomplishments=accomplishments,
            errors=[e['error'] for e in errors_and_fixes],
            breakthrough=breakthrough,
            decisions=decisions,
            bugs_fixed=bugs_fixed
        )
        
        # Get claude_session_id
        claude_session_id = None
        try:
            import os
            import hashlib
            
            current_dir = os.path.abspath(os.getcwd())
            sanitized_dir = current_dir.replace('\\', '-').replace('/', '-').replace(':', '-')
            
            if len(sanitized_dir) > 100:
                dir_hash = hashlib.sha256(current_dir.encode()).hexdigest()[:16]
                sanitized_dir = f"project-{dir_hash}"
            
            # Projects directory is in GLOBAL Claude directory
            # Check environment variable first, then fallback to ~/.claude
            claude_base = os.environ.get('CLAUDE_HOME')
            if not claude_base:
                claude_base = Path.home() / ".claude"
            else:
                claude_base = Path(claude_base)
            
            claude_projects_dir = claude_base / "projects" / sanitized_dir
            
            if claude_projects_dir.exists():
                jsonl_files = list(claude_projects_dir.glob("*.jsonl"))
                if jsonl_files:
                    most_recent = max(jsonl_files, key=lambda f: f.stat().st_mtime)
                    claude_session_id = most_recent.stem
                    if not re.match(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', claude_session_id):
                        if not re.match(r'^[a-zA-Z0-9_-]+$', claude_session_id):
                            claude_session_id = None
        except Exception as e:
            print(f"Warning: Could not get claude_session_id: {e}")
        
        # Save to database - use PROJECT database
        db_path = get_project_db_path()
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Update session with all fields
        cursor.execute("""
            UPDATE sessions SET
                primary_request = ?, technical_concepts = ?, files_and_code = ?,
                errors_and_fixes = ?, problem_solving = ?, user_messages = ?,
                pending_tasks = ?, current_work = ?, next_step = ?,
                accomplishments = ?, decisions = ?, bugs_fixed = ?, 
                breakthrough_moment = ?, 
                quality_score = ?, ended_at = ?, conversation_flow = ?
            WHERE id = ?
        """, (
            primary_request,
            json.dumps(technical_concepts),
            json.dumps(files_and_code),
            json.dumps(errors_and_fixes),
            problem_solving,
            json.dumps(user_messages),
            json.dumps(pending_tasks),
            current_work,
            next_step,
            json.dumps(accomplishments),  # REAL accomplishments
            json.dumps(decisions),
            json.dumps(bugs_fixed),
            breakthrough,
            quality_score,
            timestamp,
            conversation_flow or problem_solving,  # Use problem_solving as fallback if no conversation_flow
            session_data['session_id']
        ))
        
        # Process JSON chat file for messages table - FROM PROJECT
        json_file = db_path.parent.parent / "memory" / "chat" / f"{session_data['session_id']}.json"
        
        # Initialize total_exchanges with default value
        total_exchanges = len(user_messages) if user_messages else 0
        
        if json_file.exists():
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    chat_messages = json.load(f)
                
                # Calculate basic metrics
                total_messages = len(chat_messages)
                user_msgs = [m for m in chat_messages if m.get('type') == 'user']
                assistant_msgs = [m for m in chat_messages if m.get('type') == 'assistant']
                
                # Time metrics
                first_timestamp = chat_messages[0]['timestamp'] if chat_messages else timestamp
                last_timestamp = chat_messages[-1]['timestamp'] if chat_messages else timestamp
                
                # Calculate average message length
                avg_msg_length = sum(len(m.get('content', '')) for m in chat_messages) // total_messages if total_messages > 0 else 0
                
                # Calculate average response time
                response_times = []
                for i in range(1, len(chat_messages)):
                    if chat_messages[i]['type'] == 'assistant' and chat_messages[i-1]['type'] == 'user':
                        try:
                            t1 = datetime.fromisoformat(chat_messages[i-1]['timestamp'].replace('Z', '+00:00'))
                            t2 = datetime.fromisoformat(chat_messages[i]['timestamp'].replace('Z', '+00:00'))
                            response_times.append((t2 - t1).total_seconds())
                        except:
                            pass
                avg_response_time = int(sum(response_times) / len(response_times)) if response_times else 0
                
                # Content analysis
                all_content = ' '.join(m.get('content', '') for m in chat_messages)
                
                # Find commands
                import re
                commands = list(set(re.findall(r'/\w+', all_content)))
                
                # Find agent mentions
                agents = list(set(re.findall(r'@[\w\.-]+', all_content)))
                
                # Count errors
                error_keywords = ['error', 'failed', 'exception', 'traceback', 'failure']
                errors_count = sum(1 for keyword in error_keywords if keyword.lower() in all_content.lower())
                
                # Count code blocks
                code_blocks = len(re.findall(r'```', all_content))
                
                # Frustration level (0-10)
                frustration_words = ['PUTO', 'MIERDA', 'ASCO', 'capullo', 'joder', 'coño', '!!!', 'QUE ASCO', 'DOBLE']
                frustration_level = min(10, sum(2 for word in frustration_words if word in all_content))
                
                # Extract keywords (simple approach - most common significant words)
                words = re.findall(r'\b[a-zA-Z]{4,}\b', all_content.lower())
                from collections import Counter
                word_freq = Counter(words)
                common_words = {'that', 'this', 'with', 'from', 'have', 'been', 'will', 'your', 'what', 'when', 'there', 'would', 'which', 'their', 'about'}
                keywords = [word for word, _ in word_freq.most_common(10) if word not in common_words][:5]
                
                # Derived metrics
                try:
                    last_msg_time = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                    session_active = (datetime.now(last_msg_time.tzinfo) - last_msg_time).total_seconds() < 1800  # 30 min
                except:
                    session_active = False
                
                # Productivity ratio (code/commands vs chat)
                work_indicators = code_blocks + len(commands) + len(agents)
                productivity_ratio = work_indicators / total_messages if total_messages > 0 else 0
                
                # Complexity score (1-10)
                complexity_score = min(10, max(1, code_blocks + (avg_msg_length // 200) + len(commands)))
                
                # Interactions per hour
                try:
                    first_time = datetime.fromisoformat(first_timestamp.replace('Z', '+00:00'))
                    last_time = datetime.fromisoformat(last_timestamp.replace('Z', '+00:00'))
                    hours = (last_time - first_time).total_seconds() / 3600
                    interactions_per_hour = total_messages / hours if hours > 0 else total_messages
                except:
                    interactions_per_hour = 0
                
                # Insert into messages table
                cursor.execute("""
                    INSERT INTO messages (
                        session_id, total_messages, user_messages, assistant_messages,
                        first_timestamp, last_timestamp, duration_minutes, avg_message_length,
                        avg_response_time_seconds, commands_used, agents_mentioned, errors_count,
                        code_blocks_count, frustration_level, keywords, session_active,
                        productivity_ratio, complexity_score, interactions_per_hour, conversation,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session_data['session_id'], total_messages, len(user_msgs), len(assistant_msgs),
                    first_timestamp, last_timestamp, actual_duration, avg_msg_length,
                    avg_response_time, json.dumps(commands), json.dumps(agents), errors_count,
                    code_blocks, frustration_level, json.dumps(keywords), session_active,
                    productivity_ratio, complexity_score, interactions_per_hour, 
                    json.dumps(chat_messages), timestamp
                ))
            except Exception as e:
                print(f"Warning: Could not process chat JSON: {e}")
                # Fallback to simple insert
                cursor.execute("""
                    INSERT INTO messages (session_id, conversation, created_at)
                    VALUES (?, ?, ?)
                """, (session_data['session_id'], '[]', timestamp))
        else:
            # No JSON file, insert minimal record
            cursor.execute("""
                INSERT INTO messages (session_id, conversation, created_at)
                VALUES (?, ?, ?)
            """, (session_data['session_id'], '[]', timestamp))
        
        message_id = cursor.lastrowid
        
        # Create next session
        import secrets
        new_session_id = f"session_{secrets.token_hex(6)}"
        
        cursor.execute("""
            INSERT INTO sessions (id, job_id, created_at, claude_session_id)
            VALUES (?, ?, ?, ?)
        """, (new_session_id, session_data['job_id'], timestamp, claude_session_id))
        
        conn.commit()
        conn.close()
        
        return {
            'session_id': session_data['session_id'],
            'job_id': session_data['job_id'],
            'quality_score': quality_score,
            'duration_minutes': actual_duration,
            'total_exchanges': total_exchanges,
            'primary_request': primary_request,
            'technical_concepts_count': len(technical_concepts),
            'files_modified_count': len(files_and_code),
            'errors_fixed_count': len(errors_and_fixes),
            'user_messages_count': len(user_messages),
            'pending_tasks_count': len(pending_tasks),
            'accomplishments_count': len(accomplishments),
            'bugs_fixed_count': len(bugs_fixed),
            'decisions_count': len(decisions),
            'breakthrough': breakthrough[:100] + '...' if len(breakthrough) > 100 else breakthrough,
            'current_work': current_work,
            'next_step': next_step,
            'message_id': message_id,
            'timestamp': timestamp,
            'new_session_id': new_session_id,
            'next_session_ready': True
        }
        
    except Exception as e:
        raise Exception(f"Database save failed: {e}")


def main():
    """Main function for enhanced save"""
    try:
        # Backup database first
        backup_success = backup_database()
        if not backup_success:
            print(json.dumps({
                "error": "Failed to create database backup",
                "recommendation": "Check database file permissions and disk space"
            }))
            return 1
        
        # Parse enhanced arguments
        parsed_args = parse_arguments()
        if not parsed_args:
            return 1
        
        # Get current session
        session_data = get_current_session()
        
        # Save everything with enhanced fields
        result = save_to_database_enhanced(session_data, parsed_args)
        
        # Output result
        print(json.dumps(result, indent=2))
        return 0
        
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return 1


if __name__ == "__main__":
    exit(main())