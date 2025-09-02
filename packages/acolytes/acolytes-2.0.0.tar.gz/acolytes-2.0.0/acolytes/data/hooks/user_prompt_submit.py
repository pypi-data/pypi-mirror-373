#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import argparse
import json
import sys
import sqlite3
import os
from pathlib import Path
from datetime import datetime


def generate_markdown_transcript(conversation_file, session_id):
    """Generate a beautiful Markdown transcript from the JSON conversation."""
    try:
        if not conversation_file.exists():
            return
        
        # Read the conversation
        with open(conversation_file, "r", encoding="utf-8") as f:
            conversation = json.load(f)
        
        if not conversation:
            return
        
        # Generate markdown content
        md_content = []
        md_content.append(f"# 💬 Conversación {session_id}")
        md_content.append("")
        
        # Add session metadata
        first_msg = conversation[0]
        timestamp = first_msg.get("timestamp", "")
        if timestamp:
            date_part = timestamp.split("T")[0] if "T" in timestamp else timestamp
            md_content.append(f"**📅 Fecha:** {date_part}")
        md_content.append(f"**🆔 Sesión:** `{session_id}`")
        md_content.append(f"**💭 Total mensajes:** {len(conversation)}")
        md_content.append("")
        md_content.append("---")
        md_content.append("")
        
        # Add conversation
        for i, message in enumerate(conversation, 1):
            msg_type = message.get("type", "unknown")
            content = message.get("content", "")
            timestamp = message.get("timestamp", "")
            
            # Format timestamp
            time_part = ""
            if timestamp:
                if "T" in timestamp:
                    time_part = timestamp.split("T")[1].split(".")[0] if "T" in timestamp else ""
                    time_part = f" {time_part}" if time_part else ""
            
            if msg_type == "user":
                username = os.getenv("USERNAME", "Usuario")  # Get Windows username
                md_content.append("<div style=\"text-align: right;\">")
                md_content.append("")
                md_content.append(f"### <span style=\"color: #007bff; text-transform: uppercase;\">♾️ {username}</span>{time_part}")
                md_content.append("")
                md_content.append(content)
                md_content.append("")
                md_content.append("</div>")
                md_content.append("")
                md_content.append("---")
                md_content.append("")
                
            elif msg_type == "assistant":
                md_content.append(f"### <span style=\"color: #d2691e; text-transform: uppercase;\">🤖 Claude</span>{time_part}")
                md_content.append("")
                md_content.append(content)
                md_content.append("")
                md_content.append("---")
                md_content.append("")
        
        # Write markdown file
        md_file = conversation_file.parent / f"{session_id}.md"
        with open(md_file, "w", encoding="utf-8") as f:
            f.write("\n".join(md_content))
            
    except Exception as e:
        print(f"Markdown generation error: {e}", file=sys.stderr)

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def ensure_session_log_dir(project_root=None):
    """Ensure chat directory exists and return path."""
    if project_root:
        base_dir = Path(project_root)
    else:
        # Always use local project directory
        current_dir = Path.cwd()
        if current_dir.name == 'hooks':
            base_dir = current_dir.parent.parent  # Go up from .claude/hooks to project root
        else:
            base_dir = current_dir
    
    # Always use local .claude/memory/chat
    chat_dir = base_dir / '.claude' / 'memory' / 'chat'
    chat_dir.mkdir(parents=True, exist_ok=True)
    return chat_dir


def get_our_session_id(project_cwd):
    """Get our session ID from SQLite database."""
    if project_cwd:
        db_path = Path(project_cwd) / '.claude' / 'memory' / 'project.db'
    else:
        db_path = Path.cwd() / '.claude' / 'memory' / 'project.db'
    
    # Fallback to hardcoded session ID if DB doesn't exist
    our_session_id = "session_ac01e7e4e110"  # Default hardcoded session
    
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            # Get current active session
            cursor.execute("SELECT id FROM sessions WHERE ended_at IS NULL ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                our_session_id = result[0]
            conn.close()
        except (sqlite3.Error, OSError, IOError):
            pass
    
    return our_session_id


def log_user_prompt(session_id, input_data):
    """Log user prompt to conversation JSON."""
    try:
        project_cwd = input_data.get("cwd", "")
        our_session_id = get_our_session_id(project_cwd)
        
        # Get chat directory
        log_dir = ensure_session_log_dir(project_cwd if project_cwd else None)
        
        # Create user message entry
        user_message = {
            "session_id": our_session_id,
            "timestamp": datetime.now().isoformat() + "Z",
            "content": input_data.get("prompt", ""),
            "type": "user",
            "uuid": f"user_{datetime.now().timestamp()}"
        }
        
        # Save to conversation file
        conversation_file = log_dir / f"{our_session_id}.json"
        
        # Read existing conversation or create new list
        conversation = []
        if conversation_file.exists():
            try:
                with open(conversation_file, "r", encoding="utf-8") as f:
                    conversation = json.load(f)
            except (json.JSONDecodeError, OSError, IOError):
                conversation = []
        
        # Add user message
        conversation.append(user_message)
        
        # Write back
        with open(conversation_file, "w", encoding="utf-8") as f:
            json.dump(conversation, f, indent=2, ensure_ascii=False)
        
        # Generate markdown transcript
        generate_markdown_transcript(conversation_file, our_session_id)
            
    except Exception as e:
        print(f"User prompt logging error: {e}", file=sys.stderr)


def detect_work_type(prompt):
    """
    Detect if prompt suggests a new JOB (large multi-session work).
    Provides hints to Claude about potential work organization.
    """
    big_job_indicators = [
        "implement complete system",
        "total migration",
        "create from scratch",
        "complete refactor",
        "complete architecture", 
        "complete system",
        "build entire",
        "develop complete",
        "full implementation"
    ]
    
    prompt_lower = prompt.lower()
    
    # Check for obvious JOB indicators
    for indicator in big_job_indicators:
        if indicator in prompt_lower:
            # Hint to Claude about potential JOB
            print("POSSIBLE JOB DETECTED - Consider asking user:")
            print("Do you want to create a new JOB for this large task?")
            print("(Check active/paused jobs with /jobs)")
            return
    
    # If no JOB detected, Claude handles normally (TODOs, regular tasks)


def validate_prompt(prompt):
    """
    Validate the user prompt for security or policy violations.
    Returns tuple (is_valid, reason).
    """
    # Example validation rules (customize as needed)
    blocked_patterns = [
        # Add any patterns you want to block
        # Example: ('rm -rf /', 'Dangerous command detected'),
    ]
    
    prompt_lower = prompt.lower()
    
    for pattern, reason in blocked_patterns:
        if pattern.lower() in prompt_lower:
            return False, reason
    
    return True, None


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument('--validate', action='store_true', 
                          help='Enable prompt validation')
        parser.add_argument('--log-only', action='store_true',
                          help='Only log prompts, no validation or blocking')
        args = parser.parse_args()
        
        # Read JSON input from stdin
        input_data = json.loads(sys.stdin.read())
        
        # Extract session_id and prompt
        session_id = input_data.get('session_id', 'unknown')
        prompt = input_data.get('prompt', '')
        
        # Log the user prompt
        log_user_prompt(session_id, input_data)
        
        # Detect work type and provide hints to Claude
        detect_work_type(prompt)
        
        # Validate prompt if requested and not in log-only mode
        if args.validate and not args.log_only:
            is_valid, reason = validate_prompt(prompt)
            if not is_valid:
                # Exit code 2 blocks the prompt with error message
                print(f"Prompt blocked: {reason}", file=sys.stderr)
                sys.exit(2)
        
        # Add context information (optional)
        # You can print additional context that will be added to the prompt
        # Example: print(f"Current time: {datetime.now()}")
        
        # Success - prompt will be processed
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        sys.exit(0)


if __name__ == '__main__':
    main()