#!/usr/bin/env python3
"""
QUEST MONITOR SIMPLE - Without emojis for Windows compatibility
"""

import sqlite3
import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path

# Import core for database path
from acolyte_quest_core import DB_PATH, TABLE_NAME

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def monitor_quest(quest_id=None):
    """Simple real-time monitor"""
    conn = sqlite3.connect(str(DB_PATH))
    
    print("Starting monitor... Press Ctrl+C to exit\n")
    
    try:
        while True:
            clear_screen()
            print("=" * 80)
            print(f"QUEST MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 80)
            
            if quest_id:
                # Monitor specific quest
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT quest_id, quest_name, status, current_agent, mission,
                           broadcast, recruited,
                           datetime(created_at, 'unixepoch', 'localtime') as created,
                           datetime(updated_at, 'unixepoch', 'localtime') as updated
                    FROM {TABLE_NAME}
                    WHERE quest_id = ?
                """, (quest_id,))
                
                quest = cursor.fetchone()
                if quest:
                    print(f"\nQUEST #{quest[0]}: {quest[1]}")
                    print(f"Status: {quest[2]} | Current Turn: {quest[3] or 'None'}")
                    print(f"Mission: {quest[4]}")
                    print(f"Created: {quest[7]} | Updated: {quest[8]}")
                    
                    # Show recruited agents
                    try:
                        recruited = json.loads(quest[6])
                        print(f"\nAGENTS: {', '.join(recruited)}")
                        current = quest[3]
                        for agent in recruited:
                            if agent == current:
                                print(f"  -> {agent} [CURRENT TURN]")
                            else:
                                print(f"     {agent}")
                    except:
                        pass
                    
                    # Show conversation
                    try:
                        broadcast = json.loads(quest[5]) if quest[5] else []
                        if not isinstance(broadcast, list):
                            broadcast = [broadcast] if broadcast else []
                        
                        print(f"\nCONVERSATION ({len(broadcast)} messages):")
                        for msg in broadcast[-5:]:  # Last 5 messages
                            if isinstance(msg, dict):
                                print(f"\n  [{msg.get('timestamp', '?')[:19]}]")
                                print(f"  {msg.get('from', '?')} -> {msg.get('to', '?')}")
                                message = msg.get('message', '')[:100]
                                if len(msg.get('message', '')) > 100:
                                    message += "..."
                                print(f"  Message: {message}")
                    except Exception as e:
                        print(f"Error parsing broadcast: {e}")
                else:
                    print(f"\nQuest #{quest_id} not found")
                    
            else:
                # Monitor all active quests
                cursor = conn.cursor()
                cursor.execute(f"""
                    SELECT quest_id, quest_name, status, current_agent,
                           datetime(updated_at, 'unixepoch', 'localtime') as updated
                    FROM {TABLE_NAME}
                    WHERE status NOT IN ('completed', 'failed', 'timeout')
                    ORDER BY quest_id DESC
                """)
                
                quests = cursor.fetchall()
                
                print("\nACTIVE QUESTS:")
                if quests:
                    for q in quests:
                        status_mark = {
                            'working': '[W]',
                            'waiting': '[.]',
                            'reviewing': '[R]'
                        }.get(q[2], '[?]')
                        
                        print(f"\n{status_mark} Quest #{q[0]}: {q[1]}")
                        print(f"    Status: {q[2]} | Turn: {q[3]} | Updated: {q[4]}")
                else:
                    print("\nNo active quests")
            
            print("\n" + "=" * 80)
            print("Refreshing every 1 second... Ctrl+C to exit")
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nMonitor stopped")
    finally:
        conn.close()

if __name__ == "__main__":
    quest_id = None
    if len(sys.argv) > 1:
        try:
            quest_id = int(sys.argv[1])
        except:
            print(f"Invalid quest ID: {sys.argv[1]}")
            sys.exit(1)
    
    monitor_quest(quest_id)