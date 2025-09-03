#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUEST MESSAGE - Send a message to another agent
Used by leaders to give instructions or request fixes
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
        description='Send a message to another agent in a quest'
    )
    
    parser.add_argument(
        '--quest', '-q',
        type=int,
        required=True,
        help='Quest ID'
    )
    
    parser.add_argument(
        '--to', '-t',
        required=True,
        help='Target agent name (e.g., @backend.api)'
    )
    
    parser.add_argument(
        '--from', '-f',
        dest='from_agent',
        help='From agent name (optional, will be detected from quest)'
    )
    
    parser.add_argument(
        '--msg', '-m',
        required=True,
        help='Message content'
    )
    
    args = parser.parse_args()
    
    try:
        # Get quest to determine sender if not specified
        quest = quest_core.get_quest(args.quest)
        if not quest:
            print(f"[ERROR] Quest {args.quest} not found")
            sys.exit(1)
        
        # Determine sender
        from_agent = args.from_agent
        if not from_agent:
            # Try to detect from context
            import json
            if quest['context']:
                context = json.loads(quest['context']) if isinstance(quest['context'], str) else quest['context']
                from_agent = context.get('leader', '@unknown')
            else:
                from_agent = '@unknown'
        
        # Send message
        success = quest_core.send_message(
            quest_id=args.quest,
            from_agent=from_agent,
            to_agent=args.to,
            message=args.msg
        )
        
        if success:
            print(f"[OK] Message sent to {args.to}")
            print(f"[MSG] Quest {args.quest} - turn passed to {args.to}")
            print(f"[NOTE] Message: {args.msg[:100]}...")
        else:
            print(f"[ERROR] Failed to send message. Enter in MONITOR MODE")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)
    finally:
        quest_core.disconnect()

if __name__ == "__main__":
    main()