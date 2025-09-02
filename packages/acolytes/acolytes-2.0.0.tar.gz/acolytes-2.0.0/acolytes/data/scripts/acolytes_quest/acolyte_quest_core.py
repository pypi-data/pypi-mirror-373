#!/usr/bin/env python3
"""
ACOLYTE QUEST CORE - Shared functions for the Acolyte Quests System
All quest scripts import this core module for database and utility functions
"""

import sqlite3
import json
import time
import sys
import os
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple

# Setup logging
# Create logs directory if it doesn't exist
LOG_DIR = Path('.claude/logs/quests')
try:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
except:
    LOG_DIR = Path('.')  # Fallback to current directory

# General logger for system events
handlers = [logging.StreamHandler()]
try:
    handlers.append(logging.FileHandler(LOG_DIR / 'system.log', mode='a'))
except:
    pass  # Fallback to console only

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=handlers
)
logger = logging.getLogger('AcolyteQuests')

# Database configuration
# FIXED: Use absolute path to project root database
import os
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.parent  # Go up to Acolytes root
DB_PATH = PROJECT_ROOT / ".claude" / "memory" / "project.db"

# Alternative: Use environment variable if set
if os.environ.get('ACOLYTES_ROOT'):
    DB_PATH = Path(os.environ['ACOLYTES_ROOT']) / ".claude" / "memory" / "project.db"

TABLE_NAME = "acolyte_quests"  # FIXED: Hardcoded to prevent SQL injection

class QuestCore:
    """Core functionality for Acolyte Quest System"""
    
    def __init__(self):
        """Initialize core with database path validation"""
        if not DB_PATH.exists():
            # Try to create the database directory
            DB_PATH.parent.mkdir(parents=True, exist_ok=True)
            logger.warning(f"Database not found at {DB_PATH}, will be created")
        self.db_path = str(DB_PATH)
        self.conn = None
        self.quest_loggers = {}  # Cache for quest-specific loggers
    
    def get_quest_logger(self, quest_id: int) -> logging.Logger:
        """
        Get or create a logger specific to a quest
        
        Args:
            quest_id: The quest ID
            
        Returns:
            Logger instance for this quest
        """
        if quest_id not in self.quest_loggers:
            # Create quest-specific logger
            quest_logger = logging.getLogger(f'Quest_{quest_id}')
            quest_logger.setLevel(logging.DEBUG)
            
            # Create quest-specific log file
            log_file = LOG_DIR / f'quest_{quest_id}.log'
            try:
                file_handler = logging.FileHandler(log_file, mode='a')
                file_handler.setFormatter(
                    logging.Formatter('%(asctime)s | %(message)s', '%Y-%m-%d %H:%M:%S')
                )
                quest_logger.addHandler(file_handler)
                
                # Also log to console
                console_handler = logging.StreamHandler()
                console_handler.setFormatter(
                    logging.Formatter(f'[Quest {quest_id}] %(message)s')
                )
                quest_logger.addHandler(console_handler)
                
                # Prevent propagation to avoid duplicate logs
                quest_logger.propagate = False
                
            except Exception as e:
                logger.error(f"Failed to create quest log file: {e}")
            
            self.quest_loggers[quest_id] = quest_logger
        
        return self.quest_loggers[quest_id]
    
    def log_quest_event(self, quest_id: int, event_type: str, message: str, 
                        agent: Optional[str] = None, extra_data: Optional[Dict] = None):
        """
        Log an event for a specific quest
        
        Args:
            quest_id: Quest ID
            event_type: Type of event (CREATE, MESSAGE, STATUS, ERROR, etc.)
            message: Event message
            agent: Agent involved (optional)
            extra_data: Additional data to log (optional)
        """
        quest_logger = self.get_quest_logger(quest_id)
        
        # Build log message
        log_parts = [f"[{event_type}]"]
        if agent:
            log_parts.append(f"[{agent}]")
        log_parts.append(message)
        
        if extra_data:
            log_parts.append(f"| Data: {json.dumps(extra_data, separators=(',', ':'))}")
        
        log_message = " ".join(log_parts)
        quest_logger.info(log_message)
    
    def safe_json_parse(self, data: Any, default: Any = None) -> Any:
        """
        Safely parse JSON data with validation
        
        Args:
            data: String or dict to parse
            default: Default value if parsing fails
            
        Returns:
            Parsed JSON or default value
        """
        if data is None:
            return default
            
        if isinstance(data, dict) or isinstance(data, list):
            return data
            
        if not isinstance(data, str):
            logger.warning(f"Invalid JSON type: {type(data)}")
            return default
            
        try:
            # Validate it's not too large (prevent DOS)
            if len(data) > 100000:  # 100KB limit
                logger.error("JSON data too large")
                return default
                
            parsed = json.loads(data)
            
            # Basic structure validation
            if not isinstance(parsed, (dict, list)):
                logger.warning(f"JSON parsed to unexpected type: {type(parsed)}")
                return default
                
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return default
        except Exception as e:
            logger.error(f"Unexpected error parsing JSON: {e}")
            return default
        
    def connect(self) -> sqlite3.Connection:
        """
        Establish database connection with optimal settings
        Returns: SQLite connection object
        """
        if self.conn:
            return self.conn
            
        try:
            self.conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,
                check_same_thread=False
            )
            # Optimize for concurrent access
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA synchronous=NORMAL")
            self.conn.execute("PRAGMA temp_store=MEMORY")
            self.conn.row_factory = sqlite3.Row
            
            # Ensure table exists
            self._ensure_table_exists()
            
            return self.conn
        except sqlite3.Error as e:
            raise RuntimeError(f"Database connection failed: {e}")
    
    def disconnect(self):
        """Close database connection safely"""
        if self.conn:
            try:
                self.conn.close()
                self.conn = None
            except sqlite3.Error:
                pass  # Ignore errors on close
    
    def _ensure_table_exists(self):
        """Create acolyte_quests table if it doesn't exist"""
        # Use parameterized query even though TABLE_NAME is hardcoded (best practice)
        self.conn.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                quest_id INTEGER PRIMARY KEY AUTOINCREMENT,
                quest_name TEXT NOT NULL,
                quest_phase TEXT DEFAULT '1/1',
                mission TEXT NOT NULL,
                recruited TEXT NOT NULL,  -- JSON array
                current_agent TEXT,
                status TEXT NOT NULL DEFAULT 'working',
                broadcast TEXT,  -- JSON object
                context TEXT,   -- JSON object
                result TEXT,    -- JSON object
                created_at INTEGER DEFAULT (strftime('%s', 'now')),
                updated_at INTEGER DEFAULT (strftime('%s', 'now'))
            )
        """)
        
        # Create indexes for better performance
        self.conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_current_agent 
            ON {TABLE_NAME}(current_agent)
        """)
        
        self.conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_status 
            ON {TABLE_NAME}(status)
        """)
        
        self.conn.execute(f"""
            CREATE INDEX IF NOT EXISTS idx_created_at 
            ON {TABLE_NAME}(created_at)
        """)
        
        self.conn.commit()
        logger.info(f"Table {TABLE_NAME} and indexes ready")
    
    def create_quest(self, mission: str, agents: List[str], 
                    phase: str = "1/1") -> int:
        """
        Create a new quest
        
        Args:
            mission: The task description
            agents: List of agent names (leader first)
            phase: Quest phase (e.g., "1/6")
            
        Returns:
            quest_id of created quest
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Generate quest name
        quest_name = f"quest-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Leader is first and gets initial turn to send instructions
        leader = agents[0]
        first_worker = agents[1] if len(agents) > 1 else leader
        
        # Initial broadcast as empty array (no messages yet)
        broadcast = []
        
        # Context with mission and leader
        context = {
            "mission": mission,
            "leader": leader,
            "phase": phase
        }
        
        cursor.execute(f"""
            INSERT INTO {TABLE_NAME} 
            (quest_name, quest_phase, mission, recruited, current_agent, 
             status, broadcast, context)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quest_name,
            phase,
            mission,
            json.dumps(agents),
            leader,  # Leader gets initial turn to send instructions
            'working',
            json.dumps(broadcast),
            json.dumps(context)
        ))
        
        conn.commit()
        quest_id = cursor.lastrowid
        
        # Log quest creation
        self.log_quest_event(quest_id, "CREATE", f"Quest created: {quest_name}", 
                           leader, {"mission": mission, "agents": agents, "phase": phase})
        self.log_quest_event(quest_id, "TURN", f"Initial turn assigned to leader", 
                           leader, {"status": "working"})
        
        print(f"[OK] Created quest {quest_id}: {quest_name}")
        print(f"Mission: {mission}")
        print(f"Recruited: {', '.join(agents)}")
        print(f"First turn: {leader} (leader sends initial instructions)")
        
        return quest_id
    
    def get_quest(self, quest_id: int) -> Optional[Dict[str, Any]]:
        """
        Get quest by ID
        
        Args:
            quest_id: The quest ID to retrieve
            
        Returns:
            Dict with quest data or None if not found
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT * FROM {TABLE_NAME} WHERE quest_id = ?
        """, (quest_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_quests_for_agent(self, agent_name: str, 
                            status_filter: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Get all quests where agent is current_agent
        
        Args:
            agent_name: Agent to search for
            status_filter: Optional list of statuses to include
            
        Returns:
            List of quest dictionaries
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        if status_filter:
            placeholders = ','.join('?' * len(status_filter))
            query = f"""
                SELECT * FROM {TABLE_NAME} 
                WHERE current_agent = ? 
                AND status IN ({placeholders})
                ORDER BY created_at DESC
            """
            params = [agent_name] + status_filter
        else:
            query = f"""
                SELECT * FROM {TABLE_NAME} 
                WHERE current_agent = ?
                AND status NOT IN ('completed', 'failed', 'timeout')
                ORDER BY created_at DESC
            """
            params = [agent_name]
        
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_active_quests(self) -> List[Dict[str, Any]]:
        """
        Get all active quests (for workers to scan)
        
        Returns:
            List of all non-completed quests
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT * FROM {TABLE_NAME}
            WHERE status NOT IN ('completed', 'failed', 'timeout')
            ORDER BY created_at DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_all_quests(self) -> List[Dict[str, Any]]:
        """
        Get ALL quests including completed ones
        
        Returns:
            List of all quests regardless of status
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(f"""
            SELECT * FROM {TABLE_NAME}
            ORDER BY created_at DESC
        """)
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_quest(self, quest_id: int, updates: Dict[str, Any], 
                    requesting_agent: Optional[str] = None) -> bool:
        """
        Update quest fields with validation
        
        Args:
            quest_id: Quest to update
            updates: Dict of field->value to update
            requesting_agent: Agent requesting the update (for validation)
            
        Returns:
            True if update succeeded
        """
        conn = self.connect()
        cursor = conn.cursor()
        
        # Get current quest state for validation
        current_quest = self.get_quest(quest_id)
        if not current_quest:
            self.log_quest_event(quest_id, "ERROR", "Quest not found for update")
            return False
        
        # VALIDATION 1: Prevent modifications to completed quests
        if current_quest['status'] == 'completed':
            self.log_quest_event(quest_id, "VIOLATION", 
                               f"Attempted to modify completed quest", 
                               requesting_agent)
            print(f"[ERROR] Quest {quest_id} is completed. No modifications allowed.")
            return False
        
        # VALIDATION 2: Check turn-based system if agent provided
        if requesting_agent and 'current_agent' in updates:
            # Check if it's the requesting agent's turn
            if current_quest['current_agent'] != requesting_agent:
                self.log_quest_event(quest_id, "VIOLATION", 
                                   f"Turn violation: Not {requesting_agent}'s turn", 
                                   requesting_agent, 
                                   {"current_agent": current_quest['current_agent']})
                print(f"[ERROR] Turn violation: {requesting_agent} tried to act but turn belongs to {current_quest['current_agent']}")
                return False
        
        # Log the update
        self.log_quest_event(quest_id, "UPDATE", 
                           f"Updating fields: {list(updates.keys())}", 
                           requesting_agent, updates)
        
        # Build UPDATE query dynamically
        set_clauses = []
        values = []
        
        for field, value in updates.items():
            set_clauses.append(f"{field} = ?")
            # JSON serialize if needed
            if field in ['broadcast', 'context', 'result', 'recruited']:
                values.append(json.dumps(value) if not isinstance(value, str) else value)
            else:
                values.append(value)
        
        # Always update timestamp
        set_clauses.append("updated_at = strftime('%s', 'now')")
        
        # Add quest_id for WHERE clause
        values.append(quest_id)
        
        query = f"""
            UPDATE {TABLE_NAME}
            SET {', '.join(set_clauses)}
            WHERE quest_id = ?
        """
        
        cursor.execute(query, values)
        conn.commit()
        
        success = cursor.rowcount > 0
        
        if success and 'current_agent' in updates:
            self.log_quest_event(quest_id, "TURN", 
                               f"Turn passed to {updates['current_agent']}", 
                               requesting_agent)
        
        return success
    
    def send_message(self, quest_id: int, from_agent: str, 
                    to_agent: str, message: str) -> bool:
        """
        Send a message between agents - APPENDS to conversation
        
        Args:
            quest_id: Quest context
            from_agent: Sender agent
            to_agent: Target agent
            message: Message content
            
        Returns:
            True if message sent successfully
        """
        # Get current quest state
        quest = self.get_quest(quest_id)
        if not quest:
            self.log_quest_event(quest_id, "ERROR", "Quest not found", from_agent)
            return False
        
        # VALIDATION: Check if quest is completed
        if quest['status'] == 'completed':
            self.log_quest_event(quest_id, "VIOLATION", 
                               "Cannot send message to completed quest", 
                               from_agent)
            print(f"[ERROR] Quest {quest_id} is completed. Cannot send messages.")
            return False
        
        # VALIDATION: Check if it's the sender's turn
        if quest['current_agent'] != from_agent:
            self.log_quest_event(quest_id, "VIOLATION", 
                               f"Turn violation: {from_agent} tried to send but turn is {quest['current_agent']}", 
                               from_agent)
            print(f"[ERROR] Turn violation: It's {quest['current_agent']}'s turn, not {from_agent}'s")
            return False
        
        # Parse existing broadcast as array
        current_broadcast = self.safe_json_parse(quest['broadcast'], [])
        if not isinstance(current_broadcast, list):
            # Convert old format to array if needed
            current_broadcast = [current_broadcast] if current_broadcast else []
        
        # Append new message
        new_message = {
            "from": from_agent,
            "to": to_agent,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        current_broadcast.append(new_message)
        
        # Log the message
        self.log_quest_event(quest_id, "MESSAGE", 
                           f"Message sent to {to_agent}", 
                           from_agent, 
                           {"message_preview": message[:100]})
        
        updates = {
            "current_agent": to_agent,
            "status": "waiting",  # Always waiting for response
            "broadcast": current_broadcast
        }
        
        return self.update_quest(quest_id, updates, from_agent)
    
    def change_status(self, quest_id: int, new_status: str) -> bool:
        """
        Change quest status
        
        Args:
            quest_id: Quest to update
            new_status: New status value
            
        Returns:
            True if status changed
        """
        valid_statuses = ['working', 'waiting', 'reviewing', 'completed', 'failed', 'timeout']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status: {new_status}. Must be one of {valid_statuses}")
        
        return self.update_quest(quest_id, {"status": new_status})
    
    def complete_quest(self, quest_id: int, result: Dict[str, Any]) -> bool:
        """
        Mark quest as completed with result
        
        Args:
            quest_id: Quest to complete
            result: Final result data
            
        Returns:
            True if quest completed
        """
        updates = {
            "status": "completed",
            "result": result,
            "current_agent": None
        }
        
        return self.update_quest(quest_id, updates)
    
    def get_conversation(self, quest_id: int) -> str:
        """
        Get formatted conversation history from broadcast
        
        Args:
            quest_id: Quest to get conversation for
            
        Returns:
            Formatted conversation string
        """
        quest = self.get_quest(quest_id)
        if not quest:
            return "Quest not found"
        
        output = []
        output.append(f"=== QUEST {quest_id}: {quest['quest_name']} ===")
        output.append(f"Mission: {quest['mission']}")
        output.append(f"Phase: {quest['quest_phase']}")
        output.append(f"Status: {quest['status']}")
        output.append(f"Current Agent: {quest['current_agent'] or 'None'}")
        output.append("")
        output.append("=== CONVERSATION ===")
        
        # Parse broadcast array for ALL messages
        if quest['broadcast']:
            broadcast = self.safe_json_parse(quest['broadcast'], [])
            
            # Handle both array and single message formats
            if not isinstance(broadcast, list):
                broadcast = [broadcast] if broadcast else []
            
            if broadcast:
                for i, msg in enumerate(broadcast, 1):
                    if isinstance(msg, dict):
                        output.append(f"\n--- Message {i} ---")
                        output.append(f"From: {msg.get('from', 'Unknown')}")
                        output.append(f"To: {msg.get('to', 'Unknown')}")
                        output.append(f"Message: {msg.get('message', 'No message')}")
                        if 'timestamp' in msg:
                            output.append(f"Time: {msg['timestamp']}")
            else:
                output.append("No messages yet")
        else:
            output.append("No messages yet")
        
        # Add result if completed
        if quest['status'] == 'completed' and quest['result']:
            output.append("")
            output.append("=== RESULT ===")
            result = self.safe_json_parse(quest['result'], quest['result'])
            if isinstance(result, (dict, list)):
                output.append(json.dumps(result, indent=2))
            else:
                output.append(str(result))
        
        return "\n".join(output)
    
    def parse_agents(self, agents_str: str) -> List[str]:
        """
        Parse agent string into list
        
        Args:
            agents_str: Comma-separated agents or JSON array
            
        Returns:
            List of agent names
        """
        # Try JSON first
        if agents_str.startswith('['):
            parsed = self.safe_json_parse(agents_str, None)
            if parsed and isinstance(parsed, list):
                # Validate each agent name
                valid_agents = []
                for agent in parsed:
                    if isinstance(agent, str) and agent.strip():
                        valid_agents.append(agent.strip())
                return valid_agents
        
        # Fall back to comma-separated
        return [a.strip() for a in agents_str.split(',') if a.strip()]


# Singleton instance for easy import
quest_core = QuestCore()