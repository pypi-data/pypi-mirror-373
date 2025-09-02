#!/usr/bin/env python3
import sqlite3
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = Path(".claude/memory/project.db")

def format_timestamp(ts):
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%H:%M:%S")
    except Exception:
        return ts

def show_recent_tools(filter_name=None, session_only=False, blocked_only=False):
    """Show recent tool usage"""
    if not DB_PATH.exists():
        print("[ERROR] Database not found")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query
    query = """
        SELECT 
            t.tool_name,
            t.tool_category,
            t.file_affected,
            t.result_summary,
            t.success,
            t.error_message,
            t.blocked_by_hook,
            t.hook_message,
            t.bytes_processed,
            t.timestamp,
            s.title as session_title
        FROM tool_logs t
        LEFT JOIN sessions s ON t.session_id = s.id
    """
    
    conditions = []
    params = []
    
    if filter_name:
        conditions.append("t.tool_name LIKE ?")
        params.append(f"%{filter_name}%")
    
    if session_only:
        # Get current session
        cursor.execute("SELECT id FROM sessions WHERE ended_at IS NULL ORDER BY created_at DESC LIMIT 1")
        session = cursor.fetchone()
        if session:
            conditions.append("t.session_id = ?")
            params.append(session[0])
    
    if blocked_only:
        conditions.append("t.blocked_by_hook = 1")
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    
    query += " ORDER BY t.timestamp DESC LIMIT 20"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    
    if not results:
        print("No tool usage found")
        conn.close()
        return
    
    print("=" * 80)
    print("TOOL USAGE LOG")
    print("=" * 80)
    
    for row in results:
        time = format_timestamp(row['timestamp'])
        status = "[BLOCKED]" if row['blocked_by_hook'] else "[SUCCESS]" if row['success'] else "[FAILED]"
        
        print(f"\n{time} {status} {row['tool_name']}")
        
        if row['tool_category']:
            print(f"  Category: {row['tool_category']}")
        
        if row['file_affected']:
            print(f"  File: {row['file_affected']}")
        
        if row['result_summary']:
            print(f"  Result: {row['result_summary']}")
        
        if row['error_message']:
            print(f"  Error: {row['error_message']}")
        
        if row['hook_message']:
            print(f"  Blocked: {row['hook_message']}")
        
        if row['bytes_processed']:
            kb = row['bytes_processed'] / 1024
            print(f"  Data: {kb:.1f} KB")
    
    conn.close()

def show_statistics():
    """Show tool usage statistics"""
    if not DB_PATH.exists():
        print("[ERROR] Database not found")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    print("=" * 80)
    print("TOOL USAGE STATISTICS")
    print("=" * 80)
    
    # Total tools used
    cursor.execute("SELECT COUNT(*) FROM tool_logs")
    total = cursor.fetchone()[0]
    print(f"\nTotal tool calls: {total}")
    
    # Success rate
    cursor.execute("""
        SELECT 
            COUNT(CASE WHEN success = 1 THEN 1 END) as successful,
            COUNT(CASE WHEN success = 0 AND blocked_by_hook = 0 THEN 1 END) as failed,
            COUNT(CASE WHEN blocked_by_hook = 1 THEN 1 END) as blocked
        FROM tool_logs
    """)
    row = cursor.fetchone()
    print(f"Successful: {row[0]}")
    print(f"Failed: {row[1]}")
    print(f"Blocked: {row[2]}")
    
    # Most used tools
    print("\nMost Used Tools:")
    cursor.execute("""
        SELECT tool_name, tool_category, COUNT(*) as count
        FROM tool_logs
        GROUP BY tool_name
        ORDER BY count DESC
        LIMIT 10
    """)
    
    for row in cursor.fetchall():
        category = f"({row[1]})" if row[1] else ""
        print(f"  {row[0]} {category}: {row[2]} calls")
    
    # Most modified files
    print("\nMost Accessed Files:")
    cursor.execute("""
        SELECT file_affected, COUNT(*) as count
        FROM tool_logs
        WHERE file_affected IS NOT NULL
        GROUP BY file_affected
        ORDER BY count DESC
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        # Shorten long paths
        file_path = row[0]
        if len(file_path) > 60:
            file_path = "..." + file_path[-57:]
        print(f"  {file_path}: {row[1]} times")
    
    # Data processed
    cursor.execute("""
        SELECT 
            SUM(bytes_processed) as total_bytes,
            AVG(bytes_processed) as avg_bytes
        FROM tool_logs
        WHERE bytes_processed IS NOT NULL
    """)
    row = cursor.fetchone()
    if row[0]:
        total_mb = row[0] / (1024 * 1024)
        avg_kb = row[1] / 1024 if row[1] else 0
        print("\nData Processed:")
        print(f"  Total: {total_mb:.1f} MB")
        print(f"  Average per tool: {avg_kb:.1f} KB")
    
    # Session breakdown
    print("\nBy Session:")
    cursor.execute("""
        SELECT 
            s.title,
            COUNT(t.id) as tool_count,
            s.created_at
        FROM sessions s
        LEFT JOIN tool_logs t ON s.id = t.session_id
        GROUP BY s.id
        ORDER BY s.created_at DESC
        LIMIT 5
    """)
    
    for row in cursor.fetchall():
        title = row[0] or "Untitled session"
        print(f"  {title}: {row[1]} tools")
    
    conn.close()

# Main execution
if __name__ == "__main__":
    args = sys.argv[1:] if len(sys.argv) > 1 else []
    
    if not args:
        # Show recent tools
        show_recent_tools()
    elif args[0] == "stats":
        show_statistics()
    elif args[0] == "session":
        show_recent_tools(session_only=True)
    elif args[0] == "blocked":
        show_recent_tools(blocked_only=True)
    else:
        # Filter by tool name
        show_recent_tools(filter_name=args[0])