#!/usr/bin/env python3
"""
ACOLYTE QUEST MONITOR DEBUG - Real-time monitoring with detailed logging
=========================================================================

Monitors the Acolyte Quest System showing:
- Database state in real-time
- Turn violations and errors
- Message flow between agents
- Quest logs with timestamps

Usage: python quest_monitor_debug.py [quest_id] [--log-only]
"""

import sqlite3
import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import argparse

# Import core for database path
from acolyte_quest_core import DB_PATH, TABLE_NAME, LOG_DIR


class QuestMonitorDebug:
    def __init__(self):
        self.db_path = str(DB_PATH)
        self.log_dir = LOG_DIR
        self.refresh_interval = 1  # Update every second for debugging
        self.last_update = {}  # Track last update time for each quest
        
    def clear_screen(self):
        """Clear screen for update"""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def get_active_quests(self) -> List[Dict]:
        """Get all active quests from database"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT quest_id, quest_name, quest_phase, status, 
                   current_agent, recruited, broadcast, mission,
                   datetime(created_at, 'unixepoch', 'localtime') as created,
                   datetime(updated_at, 'unixepoch', 'localtime') as updated
            FROM {TABLE_NAME}
            WHERE status NOT IN ('completed', 'failed', 'timeout')
            ORDER BY quest_id DESC
        """)
        
        quests = cursor.fetchall()
        conn.close()
        return [dict(q) for q in quests]
        
    def get_quest_details(self, quest_id: int) -> Optional[Dict]:
        """Get specific quest details"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT *, 
                   datetime(created_at, 'unixepoch', 'localtime') as created,
                   datetime(updated_at, 'unixepoch', 'localtime') as updated
            FROM {TABLE_NAME} 
            WHERE quest_id = ?
        """, (quest_id,))
        
        quest = cursor.fetchone()
        conn.close()
        return dict(quest) if quest else None
        
    def read_quest_log(self, quest_id: int, last_n_lines: int = 20) -> List[str]:
        """Read the last N lines from quest log file"""
        log_file = self.log_dir / f'quest_{quest_id}.log'
        if not log_file.exists():
            return ["No log file found"]
            
        try:
            with open(log_file, 'r') as f:
                lines = f.readlines()
                return lines[-last_n_lines:] if len(lines) > last_n_lines else lines
        except Exception as e:
            return [f"Error reading log: {e}"]
            
    def format_time_ago(self, timestamp_str: str) -> str:
        """Format time elapsed since timestamp"""
        if not timestamp_str:
            return "never"
        try:
            past = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
            now = datetime.now()
            diff = now - past
            
            if diff.total_seconds() < 60:
                return f"{int(diff.total_seconds())}s ago"
            elif diff.total_seconds() < 3600:
                return f"{int(diff.total_seconds() // 60)}m ago"
            else:
                return f"{int(diff.total_seconds() // 3600)}h ago"
        except:
            return timestamp_str
            
    def detect_violations(self, quest: Dict) -> List[str]:
        """Detect turn-based violations and issues"""
        violations = []
        
        # Parse broadcast to check for violations
        try:
            broadcast = json.loads(quest['broadcast']) if quest['broadcast'] else []
            if not isinstance(broadcast, list):
                broadcast = [broadcast] if broadcast else []
                
            # Check for turn violations - someone sending twice in a row
            if len(broadcast) > 1:
                last_sender = None
                for msg in broadcast:
                    if isinstance(msg, dict):
                        msg_from = msg.get('from')
                        
                        # Check if same agent sent twice in a row (violation)
                        if last_sender and msg_from == last_sender:
                            violations.append(f"VIOLATION: {msg_from} sent twice without waiting for response")
                        last_sender = msg_from
                        
        except:
            pass
            
        # Check if quest is stuck (no updates for > 5 minutes)
        if quest['updated']:
            try:
                last_update = datetime.strptime(quest['updated'], '%Y-%m-%d %H:%M:%S')
                if (datetime.now() - last_update).total_seconds() > 300:
                    violations.append(f"WARNING: Quest stuck for {self.format_time_ago(quest['updated'])}")
            except:
                pass
                
        return violations
        
    def display_dashboard(self, quest_id: Optional[int] = None):
        """Display main monitoring dashboard"""
        self.clear_screen()
        
        print("=" * 100)
        print("ACOLYTE QUEST MONITOR DEBUG - REAL-TIME SYSTEM ANALYSIS".center(100))
        print("=" * 100)
        print(f"[TIME] {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}".center(100))
        print("=" * 100)
        
        if quest_id:
            self.display_quest_detail(quest_id)
        else:
            self.display_all_quests()
            
    def display_all_quests(self):
        """Display all active quests with status"""
        quests = self.get_active_quests()
        
        if not quests:
            print("\n[EMPTY] No active quests")
            return
            
        print("\n[QUESTS] ACTIVE QUESTS:\n")
        
        for quest in quests:
            quest_id = quest['quest_id']
            status = quest['status']
            current = quest['current_agent']
            updated = self.format_time_ago(quest['updated'])
            
            # Status emoji and colors
            status_display = {
                'working': '\033[92m[*] WORKING\033[0m',    # Green
                'waiting': '\033[93m[~] WAITING\033[0m',    # Yellow
                'reviewing': '\033[96m[?] REVIEWING\033[0m', # Cyan
                'completed': '\033[94m[+] COMPLETED\033[0m', # Blue
                'failed': '\033[91m[!] FAILED\033[0m'        # Red
            }.get(status, f'\033[90m[?] {status.upper()}\033[0m')
            
            # Format current agent with color
            turn_display = f"\033[95m--> {current}\033[0m" if current else "\033[90m[No turn]\033[0m"
            
            print(f"  Quest #{quest_id}: {quest['quest_name']}")
            print(f"     Status: {status_display} | Next Turn: {turn_display} | Updated: {updated}")
            
            # Check for violations
            violations = self.detect_violations(quest)
            if violations:
                for v in violations:
                    print(f"     [WARN] {v}")
                    
            # Show last log entry
            log_lines = self.read_quest_log(quest_id, 1)
            if log_lines and log_lines[0].strip():
                last_log = log_lines[0].strip()
                if '|' in last_log:
                    timestamp, content = last_log.split('|', 1)
                    print(f"     [LOG] Last log: {content[:80]}")
                    
            print()
            
    def display_quest_detail(self, quest_id: int):
        """Display detailed quest information with logs"""
        quest = self.get_quest_details(quest_id)
        
        if not quest:
            print(f"\n[ERROR] Quest #{quest_id} not found")
            return
            
        # Header
        print(f"\n🎯 QUEST #{quest_id}: {quest['quest_name']}")
        print(f"📊 Status: {quest['status']} | Phase: {quest['quest_phase']}")
        print(f"🎯 Mission: {quest['mission']}")
        print(f"[TIME] Created: {quest['created']} | Updated: {quest['updated']}")
        
        # Agents and turns
        try:
            recruited = json.loads(quest['recruited'])
            current = quest['current_agent']
            
            print(f"\n👥 AGENTS:")
            for agent in recruited:
                if agent == current:
                    print(f"   ➡️ {agent} [CURRENT TURN]")
                else:
                    print(f"      {agent}")
        except:
            pass
            
        # Conversation
        try:
            broadcast = json.loads(quest['broadcast']) if quest['broadcast'] else []
            if not isinstance(broadcast, list):
                broadcast = [broadcast] if broadcast else []
                
            if broadcast:
                print(f"\n💬 CONVERSATION ({len(broadcast)} messages):")
                for i, msg in enumerate(broadcast[-5:], 1):  # Last 5 messages
                    if isinstance(msg, dict):
                        print(f"   [{msg.get('timestamp', 'unknown')[:19]}]")
                        print(f"   {msg.get('from', '?')} → {msg.get('to', '?')}")
                        message_preview = msg.get('message', '')[:100]
                        if len(msg.get('message', '')) > 100:
                            message_preview += "..."
                        print(f"   [MSG] {message_preview}")
                        print()
        except:
            pass
            
        # Violations
        violations = self.detect_violations(quest)
        if violations:
            print("\n[!] VIOLATIONS DETECTED:")
            for v in violations:
                print(f"   • {v}")
                
        # Quest log
        print(f"\n📜 QUEST LOG (last 10 entries):")
        log_lines = self.read_quest_log(quest_id, 10)
        for line in log_lines:
            if line.strip():
                # Format log line
                if '|' in line:
                    parts = line.strip().split('|', 1)
                    if len(parts) == 2:
                        timestamp, content = parts
                        # Color code by type
                        if '[VIOLATION]' in content:
                            print(f"   🔴 {timestamp[-12:]} | {content.strip()}")
                        elif '[ERROR]' in content:
                            print(f"   🟠 {timestamp[-12:]} | {content.strip()}")
                        elif '[MESSAGE]' in content:
                            print(f"   🟢 {timestamp[-12:]} | {content.strip()}")
                        elif '[TURN]' in content:
                            print(f"   🔄 {timestamp[-12:]} | {content.strip()}")
                        else:
                            print(f"   ⚪ {timestamp[-12:]} | {content.strip()}")
                else:
                    print(f"   {line.strip()}")
                    
    def monitor_loop(self, quest_id: Optional[int] = None):
        """Main monitoring loop"""
        print("Starting monitor... Press Ctrl+C to exit")
        time.sleep(1)
        
        try:
            while True:
                self.display_dashboard(quest_id)
                
                # Instructions
                print("\n" + "=" * 100)
                if quest_id:
                    print(f"[>>] Monitoring Quest #{quest_id} | Ctrl+C to exit | Refreshing every {self.refresh_interval}s")
                else:
                    print(f"[>>] Monitoring all quests | Use 'python quest_monitor_debug.py <quest_id>' for specific quest")
                    print(f"[~] Refreshing every {self.refresh_interval}s | Ctrl+C to exit")
                    
                time.sleep(self.refresh_interval)
                
        except KeyboardInterrupt:
            print("\n\n👋 Monitor stopped")
            
    def show_log_only(self, quest_id: int):
        """Show only the log file content"""
        log_file = self.log_dir / f'quest_{quest_id}.log'
        
        if not log_file.exists():
            print(f"[ERROR] Log file not found: {log_file}")
            return
            
        print(f"📜 LOG FILE: {log_file}")
        print("=" * 100)
        
        try:
            with open(log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        print(line.rstrip())
        except Exception as e:
            print(f"Error reading log: {e}")


def main():
    parser = argparse.ArgumentParser(description='Monitor Acolyte Quest System with debug info')
    parser.add_argument('quest_id', nargs='?', type=int, help='Specific quest ID to monitor')
    parser.add_argument('--log-only', action='store_true', help='Show only the log file')
    parser.add_argument('--interval', type=int, default=1, help='Refresh interval in seconds')
    
    args = parser.parse_args()
    
    monitor = QuestMonitorDebug()
    monitor.refresh_interval = args.interval
    
    if args.log_only and args.quest_id:
        monitor.show_log_only(args.quest_id)
    else:
        monitor.monitor_loop(args.quest_id)


if __name__ == "__main__":
    main()