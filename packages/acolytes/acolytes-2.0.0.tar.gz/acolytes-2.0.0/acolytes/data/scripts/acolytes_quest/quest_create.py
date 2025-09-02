#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
QUEST CREATE - Creates a new quest in the Acolyte Quests System
Only used by leader agents (acolytes) to initiate quests
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
        description='Create a new quest in the Acolyte Quests System'
    )
    
    parser.add_argument(
        '--mission', '-m',
        required=True,
        help='The mission/task description'
    )
    
    parser.add_argument(
        '--agents', '-a',
        required=True,
        help='Comma-separated list of agents (leader first)'
    )
    
    parser.add_argument(
        '--phase', '-p',
        default='1/1',
        help='Quest phase (e.g., "1/6" for phase 1 of 6)'
    )
    
    args = parser.parse_args()
    
    try:
        # Parse agents
        agents = quest_core.parse_agents(args.agents)
        
        if len(agents) < 1:
            print("[ERROR] Error: At least one agent required (the leader)")
            sys.exit(1)
        
        # Create quest
        quest_id = quest_core.create_quest(
            mission=args.mission,
            agents=agents,
            phase=args.phase
        )
        
        # Return quest_id for agent to store
        print(f"\n[SAVE] STORE THIS: quest_id={quest_id}")
        
    except Exception as e:
        print(f"[ERROR] Error creating quest: {e}")
        sys.exit(1)
    finally:
        quest_core.disconnect()

if __name__ == "__main__":
    main()