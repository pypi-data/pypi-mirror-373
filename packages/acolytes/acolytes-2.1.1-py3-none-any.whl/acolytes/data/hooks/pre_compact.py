#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

"""
Advanced PreCompact Hook with Blocking Capabilities
Based on GowayLee's implementation but simplified for Acolytes

Exit codes:
- 0: Allow compaction to proceed
- 1: Warning but continue (non-blocking)
- 2: Block compaction (prevents it from happening)
"""

import json
import sys
import sqlite3
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def check_unsaved_session():
    """Check if current session has been saved"""
    try:
        db_path = Path.cwd() / '.claude' / 'memory' / 'project.db'
        if not db_path.exists():
            return True  # No DB, assume saved
            
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check if there's an active session without save
        cursor.execute("""
            SELECT id, created_at 
            FROM sessions 
            WHERE ended_at IS NULL 
            ORDER BY created_at DESC 
            LIMIT 1
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            # Active session exists - check if it's been more than 5 minutes
            session_id, created_at = result
            created_time = datetime.fromisoformat(created_at)
            time_diff = datetime.now() - created_time
            
            # If session is more than 5 minutes old and not saved, warn
            if time_diff.total_seconds() > 300:  # 5 minutes
                return False  # Unsaved work
                
        return True  # No active session or recently created
        
    except Exception:
        return True  # On error, allow compaction


def check_active_quest():
    """Check if there's an active quest in progress"""
    try:
        db_path = Path.cwd() / '.claude' / 'memory' / 'acolytes' / 'quest.db'
        if not db_path.exists():
            return False  # No quest DB, no active quest
            
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Check for active quests
        cursor.execute("""
            SELECT COUNT(*) 
            FROM quests 
            WHERE status IN ('active', 'in_progress')
        """)
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
        
    except Exception:
        return False  # On error, assume no quest


def validate_trigger(trigger):
    """Validate the trigger type"""
    valid_triggers = ['manual', 'auto']
    return trigger in valid_triggers


def main():
    try:
        # Read JSON input from stdin  
        stdin_input = sys.stdin.read().strip()
        
        if stdin_input:
            input_data = json.loads(stdin_input)
            trigger = input_data.get('trigger', 'unknown')
            custom_instructions = input_data.get('custom_instructions', '')
        else:
            # No input provided, assume manual
            trigger = 'manual'
            custom_instructions = ''
        
        # Validate trigger
        if not validate_trigger(trigger):
            print(f"WARNING: Unknown trigger type: {trigger}")
            sys.exit(1)  # Warning but continue
        
        # Check for blocking conditions
        if trigger == "auto":
            # Automatic compaction - check for blockers
            
            # 1. Check for active quest
            if check_active_quest():
                print("BLOCKED: Active QUEST in progress!")
                print("Cannot compact during quest execution.")
                print("Wait for quest to complete or manually stop it.")
                sys.exit(2)  # BLOCK compaction
            
            # 2. Check for unsaved session
            if not check_unsaved_session():
                print("WARNING: Session may have unsaved work")
                print("Consider running /save before compacting")
                # Don't block, just warn
                sys.exit(1)  # Warning but continue
                
        elif trigger == "manual":
            # Manual compaction - user initiated
            print(f"MANUAL COMPACTION: User initiated")
            if custom_instructions:
                print(f"Instructions: {custom_instructions[:100]}...")
                
            # For manual, we trust the user knows what they're doing
            # But still check for active quest
            if check_active_quest():
                print("WARNING: Active QUEST in progress")
                print("Compaction may interrupt quest execution")
                # For manual, warn but don't block
                sys.exit(1)  # Warning but continue
        
        # All checks passed
        print("Compaction approved - proceeding")
        sys.exit(0)  # Allow compaction
        
    except json.JSONDecodeError:
        # Fallback for JSON errors
        print("WARNING: Could not parse input")
        sys.exit(1)  # Warning but continue
    except Exception as e:
        # Handle any other errors
        print(f"WARNING: Unexpected error: {e}")
        sys.exit(1)  # Warning but continue


if __name__ == '__main__':
    main()