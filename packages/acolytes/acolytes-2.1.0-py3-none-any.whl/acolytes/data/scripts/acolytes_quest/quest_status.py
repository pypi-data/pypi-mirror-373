#!/usr/bin/env python3
"""
QUEST STATUS - Change quest status
Used by leaders to mark reviewing or other status changes
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from acolyte_quest_core import quest_core

def main():
    parser = argparse.ArgumentParser(
        description='Change quest status'
    )
    
    parser.add_argument(
        '--quest', '-q',
        type=int,
        required=True,
        help='Quest ID'
    )
    
    parser.add_argument(
        '--status', '-s',
        required=True,
        choices=['working', 'waiting', 'reviewing', 'completed', 'failed', 'timeout'],
        help='New status'
    )
    
    args = parser.parse_args()
    
    try:
        # Get quest first to show current status
        quest = quest_core.get_quest(args.quest)
        if not quest:
            print(f"[ERROR] Quest {args.quest} not found")
            sys.exit(1)
        
        old_status = quest['status']
        
        # Change status
        success = quest_core.change_status(args.quest, args.status)
        
        if success:
            print(f"[OK] Quest {args.quest} status changed")
            print(f"[STATS] {old_status} -> {args.status}")
            
            if args.status == 'reviewing':
                print("[REVIEW] Now reviewing work...")
            elif args.status == 'completed':
                print("[DONE] Quest completed!")
            elif args.status == 'failed':
                print("[ERROR] Quest marked as failed")
                
        else:
            print(f"[ERROR] Failed to change status")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)
    finally:
        quest_core.disconnect()

if __name__ == "__main__":
    main()