#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUEST CONVERSATION - Read the full conversation history
Used by both leaders and workers to understand context
"""

import argparse
import sys
import io
from pathlib import Path

# Force UTF-8 encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from acolyte_quest_core import quest_core

def main():
    parser = argparse.ArgumentParser(
        description='Read quest conversation history'
    )
    
    parser.add_argument(
        '--quest', '-q',
        type=int,
        required=True,
        help='Quest ID'
    )
    
    parser.add_argument(
        '--raw', '-r',
        action='store_true',
        help='Show raw JSON data'
    )
    
    parser.add_argument(
        '--accept', '-a',
        action='store_true',
        help='Accept the task by changing status to working'
    )
    
    args = parser.parse_args()
    
    try:
        if args.raw:
            # Show raw quest data
            quest = quest_core.get_quest(args.quest)
            if not quest:
                print(f"[ERROR] Quest {args.quest} not found")
                sys.exit(1)
            
            import json
            # Convert Row to dict and format
            quest_dict = dict(quest)
            
            # Parse JSON fields for better display
            for field in ['recruited', 'broadcast', 'context', 'result']:
                if quest_dict.get(field):
                    try:
                        if isinstance(quest_dict[field], str):
                            quest_dict[field] = json.loads(quest_dict[field])
                    except:
                        pass
            
            print(json.dumps(quest_dict, indent=2, default=str))
        else:
            # Show formatted conversation
            conversation = quest_core.get_conversation(args.quest)
            print(conversation)
            
            # AUTO-ACCEPT: If status is waiting, change to working
            quest = quest_core.get_quest(args.quest)
            if quest:
                status = quest.get('status')
                
                # Auto-accept ONLY if waiting (someone accepting task)
                if status == 'waiting':
                    # Someone is reading the conversation = they're accepting the task
                    if quest_core.change_status(args.quest, 'working'):
                        print("\n[AUTO-ACCEPTED] Status automatically changed to working")
                        print("[NOTE] Task is now being worked on")
                    else:
                        print("\n[ERROR] Failed to change status to working")
                # If reviewing, the leader decides next step (no auto-change)
                
                # Manual accept with --accept flag (for compatibility)
                elif args.accept:
                    if status == 'waiting':
                        if quest_core.change_status(args.quest, 'working'):
                            print("\n[ACCEPTED] Status changed to working")
                            print("[NOTE] You are now working on this task")
                        else:
                            print("\n[ERROR] Failed to change status")
                    elif status == 'working':
                        print("\n[INFO] Already working on this task")
                    else:
                        print("\n[WARNING] Cannot accept - quest not in waiting status")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)
    finally:
        quest_core.disconnect()

if __name__ == "__main__":
    main()