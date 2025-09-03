#!/usr/bin/env python3
"""
QUEST REVIEW - Mark quest as under review
Used by leaders when reviewing worker's completed work
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from acolyte_quest_core import quest_core

def main():
    parser = argparse.ArgumentParser(
        description='Mark quest as under review'
    )
    
    parser.add_argument(
        '--quest', '-q',
        type=int,
        required=True,
        help='Quest ID to review'
    )
    
    parser.add_argument(
        '--message', '-m',
        help='Optional review comment'
    )
    
    args = parser.parse_args()
    
    try:
        # Get quest to verify it exists and check status
        quest = quest_core.get_quest(args.quest)
        if not quest:
            print(f"[ERROR] Quest {args.quest} not found")
            sys.exit(1)
        
        # Check current status
        current_status = quest['status']
        if current_status == 'completed':
            print(f"[ERROR] Quest {args.quest} is already completed")
            sys.exit(1)
        
        # Change status to reviewing
        if quest_core.change_status(args.quest, 'reviewing'):
            print(f"[REVIEW] Quest {args.quest} marked as under review")
            print(f"[STATUS] {current_status} -> reviewing")
            
            if args.message:
                print(f"[NOTE] {args.message}")
            
            print("\n[ACTION] Review the work and decide:")
            print("  1. Request changes: quest_message.py --quest {} --to @worker --msg 'Fix...'".format(args.quest))
            print("  2. Complete quest: quest_complete.py --quest {} --summary 'Done'".format(args.quest))
            
        else:
            print("[ERROR] Failed to change status to reviewing")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)
    finally:
        quest_core.disconnect()

if __name__ == "__main__":
    main()