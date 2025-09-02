#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUEST CHECK - Quick check if it's agent's turn (no loop)
Used to alternate with monitor to avoid timeout
"""

import argparse
import sys
import io
import json
import time
from pathlib import Path

# Force UTF-8 encoding for Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from acolyte_quest_core import quest_core

def check_leader(quest_id: int, agent_name: str):
    """Quick check for leader"""
    quest = quest_core.get_quest(quest_id)
    
    if not quest:
        print(f"[CHECK-LEADER-{agent_name}] Quest {quest_id} not found")
        return False
    
    status = quest['status']
    current = quest['current_agent']
    
    print(f"[CHECK-LEADER-{agent_name}] Quest {quest_id}: status={status}, current={current}")
    
    if status == 'completed':
        print(f"[COMPLETED] Quest {quest_id} is done!")
        return True
    
    if current == agent_name:
        print(f"[MY-TURN] It's {agent_name}'s turn on quest {quest_id}!")
        return True
    
    print(f"[WAITING] Still waiting for {current}...")
    return False

def check_worker(agent_name: str):
    """Quick check for worker"""
    quests = quest_core.get_all_quests()
    
    print(f"[CHECK-WORKER-{agent_name}] Found {len(quests)} total quests")
    
    for quest in quests:
        if quest['current_agent'] == agent_name and quest['status'] == 'waiting':
            print(f"[ASSIGNED] Quest {quest['quest_id']} assigned to {agent_name}!")
            print(f"[MISSION] {quest['mission'][:100]}...")
            return True
    
    print(f"[NO-TASKS] No tasks for {agent_name} yet")
    return False

def main():
    parser = argparse.ArgumentParser(description='Quick quest check')
    
    parser.add_argument('--role', '-r', required=True, choices=['leader', 'worker'])
    parser.add_argument('--quest', '-q', type=int, help='Quest ID (for leaders)')
    parser.add_argument('--agent', '-a', help='Agent name')
    parser.add_argument('--loop', '-l', type=int, default=1, help='Number of quick checks')
    
    args = parser.parse_args()
    
    # Determine agent name
    if args.agent:
        agent_name = args.agent
    elif args.role == 'leader':
        agent_name = '@sandbox-orchestrator'  # Default
    else:
        print("[ERROR] Worker requires --agent name")
        sys.exit(1)
    
    print(f"\n[QUEST-CHECK] {agent_name} checking at {time.strftime('%H:%M:%S')}")
    
    try:
        for i in range(args.loop):
            if i > 0:
                print(f"[MINI-SLEEP] Quick 2s sleep...")
                time.sleep(2)
            
            if args.role == 'leader':
                if not args.quest:
                    print("[ERROR] Leader requires --quest ID")
                    sys.exit(1)
                
                found = check_leader(args.quest, agent_name)
                if found:
                    print("[EXIT] Exiting check - action needed!")
                    sys.exit(0)
            else:
                found = check_worker(agent_name)
                if found:
                    print("[EXIT] Exiting check - task found!")
                    sys.exit(0)
        
        print(f"[DONE] Completed {args.loop} checks")
        
    except KeyboardInterrupt:
        print("\n[STOP] Check interrupted")
    except Exception as e:
        print(f"[ERROR] Check failed: {e}")
    finally:
        quest_core.disconnect()

if __name__ == '__main__':
    main()