#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUEST RESPOND - Worker responds to leader with completed work
Used by workers after completing their task
"""

import argparse
import sys
import json
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
        description='Respond to quest with completed work'
    )
    
    parser.add_argument(
        '--quest', '-q',
        type=int,
        required=True,
        help='Quest ID'
    )
    
    parser.add_argument(
        '--to', '-t',
        help='Target agent (optional, will use leader from context)'
    )
    
    parser.add_argument(
        '--from', '-f',
        dest='from_agent',
        help='Your agent name (optional, will use current_agent)'
    )
    
    parser.add_argument(
        '--msg', '-m',
        required=True,
        help='Response message with work summary'
    )
    
    parser.add_argument(
        '--files', 
        help='Comma-separated list of files created/modified'
    )
    
    args = parser.parse_args()
    
    try:
        # Get quest details
        quest = quest_core.get_quest(args.quest)
        if not quest:
            print(f"[ERROR] Quest {args.quest} not found")
            sys.exit(1)
        
        # Determine from_agent (current worker)
        from_agent = args.from_agent or quest['current_agent'] or '@unknown'
        
        # Determine to_agent (leader)
        to_agent = args.to
        if not to_agent:
            # Get leader from context
            if quest['context']:
                context = json.loads(quest['context']) if isinstance(quest['context'], str) else quest['context']
                to_agent = context.get('leader')
            
            # Or get from recruited list (first is usually leader)
            if not to_agent and quest['recruited']:
                recruited = json.loads(quest['recruited']) if isinstance(quest['recruited'], str) else quest['recruited']
                if recruited:
                    to_agent = recruited[0]
        
        if not to_agent:
            print("[ERROR] Error: Cannot determine target agent. Use --to to specify")
            sys.exit(1)
        
        # Build response message
        response_msg = args.msg
        
        # Add file list if provided
        if args.files:
            files_list = [f.strip() for f in args.files.split(',')]
            response_msg += f"\n\nFiles modified:\n" + "\n".join(f"- {f}" for f in files_list)
        
        # Send response (passes turn back to leader)
        success = quest_core.send_message(
            quest_id=args.quest,
            from_agent=from_agent,
            to_agent=to_agent,
            message=response_msg
        )
        
        if success:
            print(f"[OK] Response sent to {to_agent}")
            print(f"[MSG] Quest {args.quest} - turn passed back to leader")
            print(f"[NOTE] Message: {args.msg[:100]}...")
            
            if args.files:
                print(f"[FILES] Files reported: {args.files}")
            
            print(f"\n[SLEEP] Worker going back to monitoring...")
            print(f"Run: quest_monitor.py --role worker --agent {from_agent}")
            
        else:
            print(f"[ERROR] Failed to send response")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)
    finally:
        quest_core.disconnect()

if __name__ == "__main__":
    main()