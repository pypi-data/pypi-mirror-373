#!/usr/bin/env python3
"""
QUEST COMPLETE - Mark quest as completed with final result
Used by leaders when all work is done and approved
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from acolyte_quest_core import quest_core

def main():
    parser = argparse.ArgumentParser(
        description='Complete a quest with final result'
    )
    
    parser.add_argument(
        '--quest', '-q',
        type=int,
        required=True,
        help='Quest ID'
    )
    
    parser.add_argument(
        '--result', '-r',
        help='Result message or JSON'
    )
    
    parser.add_argument(
        '--summary', '-s',
        help='Summary of what was accomplished'
    )
    
    args = parser.parse_args()
    
    try:
        # Get quest details
        quest = quest_core.get_quest(args.quest)
        if not quest:
            print(f"[ERROR] Quest {args.quest} not found")
            sys.exit(1)
        
        # Build result object
        result = {
            "quest_id": args.quest,
            "quest_name": quest['quest_name'],
            "mission": quest['mission'],
            "phase": quest['quest_phase'],
            "completed_at": datetime.now().isoformat(),
            "summary": args.summary or "Quest completed successfully"
        }
        
        # Add custom result if provided
        if args.result:
            try:
                # Try to parse as JSON
                if args.result.startswith('{') or args.result.startswith('['):
                    result['details'] = json.loads(args.result)
                else:
                    result['details'] = args.result
            except json.JSONDecodeError:
                result['details'] = args.result
        
        # Get recruited agents for summary
        if quest['recruited']:
            recruited = json.loads(quest['recruited']) if isinstance(quest['recruited'], str) else quest['recruited']
            result['team'] = recruited
        
        # Complete the quest
        success = quest_core.complete_quest(args.quest, result)
        
        if success:
            print(f"[DONE] Quest {args.quest} completed!")
            print(f"[INFO] Mission: {quest['mission']}")
            print(f"[TEAM] Team: {', '.join(result.get('team', []))}")
            print(f"[OK] Summary: {result['summary']}")
            print("\n[STATS] Full result saved to database")
            print("[SAVE] Leader should now save memories")
            
        else:
            print(f"[ERROR] Failed to complete quest")
            sys.exit(1)
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)
    finally:
        quest_core.disconnect()

if __name__ == "__main__":
    main()