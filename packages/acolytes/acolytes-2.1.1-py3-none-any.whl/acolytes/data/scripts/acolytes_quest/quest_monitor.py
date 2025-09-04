#!/usr/bin/env python3
"""
QUEST MONITOR - Eternal monitoring loop for Acolyte Quests System
Used by both leaders and workers to stay alive and check for their turn
"""

import argparse
import sys
import time
import json
import logging
from pathlib import Path
from typing import List, Set

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent))
from acolyte_quest_core import quest_core

# Setup logging
logger = logging.getLogger('QuestMonitor')

class QuestMonitor:
    """Monitors quests and returns control when it's agent's turn"""
    
    def __init__(self, role: str, quest_id: int = None, agent_name: str = None):
        """
        Initialize monitor
        
        Args:
            role: 'leader' or 'worker'
            quest_id: Specific quest ID (for leaders)
            agent_name: Agent name (required for workers)
        """
        self.role = role
        self.quest_id = quest_id
        self.agent_name = agent_name
        self.sleep_interval = 20  # seconds
        self.max_loops_before_check = 5  # After 5 loops (100s), tell agent to check manually
        self.stored_quest_ids: Set[int] = set()
        
        if role == 'leader' and quest_id:
            self.stored_quest_ids.add(quest_id)
        
    def monitor_leader(self):
        """Monitor loop for leader agents - checks ALL quests where leader is involved"""
        if self.quest_id:
            print(f"[LEADER] Monitoring specific quest {self.quest_id}")
        else:
            print(f"[LEADER] {self.agent_name} monitoring ALL quests")
        print(f"[SLEEP] Checking every {self.sleep_interval} seconds...")
        
        loop_count = 0
        while True:
            loop_count += 1
            
            # After 2 loops, give instructions to agent
            if loop_count > self.max_loops_before_check:
                print(f"\n{'='*70}")
                print(f"[TIMEOUT] Monitor exiting after {loop_count-1} checks (100 seconds)")
                print(f"\n[CRITICAL] YOU MUST IMMEDIATELY RUN THE MONITOR AGAIN!")
                if self.quest_id:
                    print(f"python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role leader --quest {self.quest_id} --agent {self.agent_name}")
                else:
                    print(f"python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role leader --agent {self.agent_name}")
                print(f"\n[WHY]: Workers still processing. This is NORMAL.")
                print(f"[ACTION]: Keep monitoring until workers respond. DO NOT STOP.")
                print(f"{'='*70}\n")
                break
            
            # ALWAYS check ALL quests where this agent appears
            all_quests = quest_core.get_all_quests()
            
            # Find quests where I'm involved (as leader OR worker)
            my_quests = []
            for q in all_quests:
                # Check if I'm the current agent (my turn)
                if q.get('current_agent') == self.agent_name:
                    my_quests.append(q)
                # Or if I'm in recruited list and quest is active
                elif self.agent_name in str(q.get('recruited', '')) and q.get('status') != 'completed':
                    my_quests.append(q)
            
            # Process found quests
            if not my_quests:
                print(f"[NO-QUESTS] No active quests for {self.agent_name}")
            else:
                print(f"[FOUND] {len(my_quests)} quest(s) involving {self.agent_name}")
                
                # Check each quest
                for quest in my_quests:
                    quest_id = quest.get('quest_id')
                    status = quest.get('status')
                    current_agent = quest.get('current_agent')
                    
                    # It's my turn!
                    if current_agent == self.agent_name:
                        print(f"\n[ALERT] YOUR TURN! Quest {quest_id}")
                        print(f"[STATUS] {status}")
                        
                        # Determine my role in this quest
                        context = quest.get('context', {})
                        if isinstance(context, str):
                            try:
                                context = json.loads(context)
                            except:
                                context = {}
                        
                        leader = context.get('leader', '')
                        if leader == self.agent_name:
                            print(f"[ROLE] You are the LEADER of quest {quest_id}")
                            print(f"\n[TIP] Use: quest_conversation.py --quest {quest_id}")
                        else:
                            print(f"[ROLE] You are a WORKER in quest {quest_id} (leader: {leader})")
                            print(f"\n[TIP] Use: quest_conversation.py --quest {quest_id} --accept")
                        
                        # Store this quest
                        self.stored_quest_ids.add(quest_id)
                        break  # Exit to handle this quest
                    else:
                        print(f"[WAIT] Quest {quest_id}: waiting for {current_agent}")
                
                # If we found a quest needing attention, exit
                if any(q.get('current_agent') == self.agent_name for q in my_quests):
                    break
            
            # Sleep before next check
            print(f"[SLEEP-{self.agent_name}] Sleeping {self.sleep_interval}s at {time.strftime('%H:%M:%S')}")
            time.sleep(self.sleep_interval)
            print(f"[WAKE-{self.agent_name}] Awake at {time.strftime('%H:%M:%S')}, checking again...")
    
    def monitor_worker(self):
        """Monitor loop for worker agents"""
        print(f"[WORKER] Worker {self.agent_name} scanning for quests...")
        print(f"[SLEEP] Checking every {self.sleep_interval} seconds...")
        
        loop_count = 0
        while True:
            loop_count += 1
            
            # After 2 loops, give instructions to agent
            if loop_count > self.max_loops_before_check:
                print(f"\n{'='*70}")
                print(f"[TIMEOUT] Monitor exiting after {loop_count-1} checks (100 seconds)")
                print(f"\n[CRITICAL] YOU MUST IMMEDIATELY RUN THE MONITOR AGAIN!")
                print(f"python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role worker --agent {self.agent_name}")
                print(f"\n[WHY]: No tasks assigned yet. This is NORMAL.")
                print(f"[ACTION]: Keep monitoring until tasks arrive. DO NOT STOP.")
                print(f"{'='*70}\n")
                break
            
            # Get ALL quests (including completed) to check status
            all_quests = quest_core.get_all_quests()
            
            # Find ALL quests where I'm involved (to track completion)
            involved_quests = [q for q in all_quests if self.agent_name in str(q.get('recruited', ''))]
            
            # Check if ALL my quests are completed
            if involved_quests:
                all_completed = all(q.get('status') == 'completed' for q in involved_quests)
                if all_completed:
                    print(f"[COMPLETED] All {len(involved_quests)} quests are done!")
                    print("[EXIT] Worker shutting down - all work complete")
                    break
            
            # Find quests where this worker is current_agent (needs action)
            my_quests = [q for q in all_quests if q['current_agent'] == self.agent_name and q['status'] != 'completed']
            
            if my_quests:
                # Store quest IDs
                for quest in my_quests:
                    self.stored_quest_ids.add(quest['quest_id'])
                
                print(f"\n[ALERT] WORKER TURN! Found {len(my_quests)} quest(s)")
                print(f"[INFO] Quest IDs: {[q['quest_id'] for q in my_quests]}")
                
                # Show first quest details
                first_quest = my_quests[0]
                print(f"\nProcessing quest {first_quest['quest_id']}: {first_quest['quest_name']}")
                print(f"Mission: {first_quest['mission'][:100]}...")
                
                if first_quest['broadcast']:
                    try:
                        broadcast = json.loads(first_quest['broadcast']) if isinstance(first_quest['broadcast'], str) else first_quest['broadcast']
                        print(f"Instructions from: {broadcast.get('from', 'Unknown')}")
                    except:
                        pass
                
                print(f"\n[SAVE] Stored quest IDs for tracking: {list(self.stored_quest_ids)}")
                print("\n[TIP] Returning control to agent for work...")
                print(f"Use: quest_conversation.py --quest {first_quest['quest_id']}")
                print(f"Then do your work and: quest_respond.py --quest {first_quest['quest_id']} --to @leader --msg 'Done...'")
                break
            
            # Check if all stored quests are completed
            if self.stored_quest_ids:
                active_stored = []
                for qid in self.stored_quest_ids:
                    quest = quest_core.get_quest(qid)
                    if quest and quest['status'] != 'completed':
                        active_stored.append(qid)
                
                if not active_stored:
                    print(f"[OK] All stored quests completed: {list(self.stored_quest_ids)}")
                    print("[BYE] Worker shutting down")
                    break
                else:
                    print(f"[MONITOR-WORKER-{self.agent_name}] Loop {loop_count}: Monitoring {len(active_stored)} active quest(s): {active_stored}")
            else:
                print(f"[MONITOR-WORKER-{self.agent_name}] Loop {loop_count}: No quests assigned yet...")
            
            print(f"[SLEEP-WORKER-{self.agent_name}] Sleeping {self.sleep_interval}s at {time.strftime('%H:%M:%S')}")
            time.sleep(self.sleep_interval)
            print(f"[WAKE-WORKER-{self.agent_name}] Awake at {time.strftime('%H:%M:%S')}, checking again...")
    
    def run(self):
        """Main monitoring loop"""
        try:
            if self.role == 'leader':
                self.monitor_leader()
            else:
                self.monitor_worker()
        except KeyboardInterrupt:
            print("\n[STOP] Monitoring interrupted by user")
        except Exception as e:
            print(f"[ERROR] Monitor error: {e}")
        finally:
            quest_core.disconnect()
            if self.stored_quest_ids:
                print(f"[STATS] Worked on quests: {list(self.stored_quest_ids)}")

def main():
    parser = argparse.ArgumentParser(
        description='Monitor quests in eternal loop'
    )
    
    parser.add_argument(
        '--role', '-r',
        required=True,
        choices=['leader', 'worker'],
        help='Agent role'
    )
    
    parser.add_argument(
        '--quest', '-q',
        type=int,
        help='Quest ID (required for leaders)'
    )
    
    parser.add_argument(
        '--agent', '-a',
        help='Agent name (required for workers)'
    )
    
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=30,
        help='Sleep interval in seconds (default: 30)'
    )
    
    args = parser.parse_args()
    
    # Format agent name: remove quotes and ensure @ prefix
    if args.agent:
        # Remove surrounding quotes if present
        args.agent = args.agent.strip('"').strip("'")
        # Add @ prefix if not present
        if not args.agent.startswith('@'):
            args.agent = '@' + args.agent
    
    # Validation
    if args.role == 'leader' and not args.quest:
        print("[ERROR] Error: Leaders must specify --quest ID")
        sys.exit(1)
    
    # ALWAYS require agent name for EVERYONE
    if not args.agent:
        print("[ERROR] Error: You MUST specify --agent name (e.g., --agent '@sandbox-orchestrator')")
        sys.exit(1)
    
    # Create and run monitor
    monitor = QuestMonitor(
        role=args.role,
        quest_id=args.quest,
        agent_name=args.agent  # ALWAYS use the provided agent name
    )
    
    if args.interval:
        monitor.sleep_interval = args.interval
    
    monitor.run()

if __name__ == "__main__":
    main()