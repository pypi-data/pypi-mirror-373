#!/usr/bin/env python3
"""
TODO Command - Advanced TODO management with AI integration and SQLite backend
"""
import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime, timedelta

# Use the new SQLite backend
DB_PATH = Path(".claude/memory/project.db")

def get_timestamp():
    """Get current timestamp"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def add_todo(task, priority='medium', due_date=None):
    """Add a new TODO with AI categorization"""
    if not DB_PATH.exists():
        print("[ERROR] Database not initialized. Run: python ~/.claude/scripts/agent_db.py init")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Get current session
    cursor.execute("SELECT id FROM sessions WHERE ended_at IS NULL ORDER BY created_at DESC LIMIT 1")
    session = cursor.fetchone()
    session_id = session[0] if session else None
    
    # Auto-detect category based on keywords
    category = detect_category(task)
    module = extract_module(task)
    files = extract_files(task)
    
    # Parse due date if provided
    if due_date:
        if due_date == 'today':
            due_date = datetime.now().strftime('%Y-%m-%d')
        elif due_date == 'tomorrow':
            due_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        elif due_date == 'week':
            due_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
    
    # Check for @mentions for assignment
    assigned_to = None
    if '@' in task:
        match = re.search(r'@(\S+)', task)
        if match:
            assigned_to = f"@{match.group(1)}"
            # Verify agent exists
            cursor.execute("SELECT name FROM agents_catalog WHERE name = ?", (assigned_to,))
            agent = cursor.fetchone()
            if not agent:
                print(f"[WARNING] Agent {assigned_to} not found in catalog")
    
    cursor.execute("""
        INSERT INTO todos (
            task, priority, status, created_at, session_id,
            category, module, related_files, due_date, 
            assigned_to, created_by
        ) VALUES (?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?, 'user')
    """, (
        task, priority, get_timestamp(), session_id,
        category, module,
        json.dumps(files) if files else None,
        due_date, assigned_to
    ))
    
    conn.commit()
    todo_id = cursor.lastrowid
    conn.close()
    
    print(f"[OK] TODO #{todo_id} created: {task}")
    print(f"   Category: {category}, Priority: {priority}")
    if module:
        print(f"   Module: {module}")
    if assigned_to:
        print(f"   Assigned to: {assigned_to}")
    if due_date:
        print(f"   Due: {due_date}")

def detect_category(content):
    """AI-powered category detection"""
    content_lower = content.lower()
    
    if any(word in content_lower for word in ['bug', 'fix', 'error', 'issue', 'broken']):
        return 'bug'
    elif any(word in content_lower for word in ['feature', 'add', 'implement', 'create new']):
        return 'feature'
    elif any(word in content_lower for word in ['refactor', 'improve', 'optimize', 'clean']):
        return 'refactor'
    elif any(word in content_lower for word in ['test', 'spec', 'coverage', 'unit test']):
        return 'test'
    elif any(word in content_lower for word in ['doc', 'readme', 'comment', 'documentation']):
        return 'docs'
    elif any(word in content_lower for word in ['maintain', 'update', 'upgrade', 'dependency']):
        return 'maintenance'
    else:
        return 'feature'

def extract_module(content):
    """Extract module from content using patterns"""
    patterns = [
        r'in\s+(\S+\.py)',           # in file.py
        r'module\s+(\S+)',            # module name
        r'component\s+(\S+)',         # component name
        r'(\S+)\s+module',            # name module
        r'\/(\w+)\/',                 # /module/
        r'\.claude\/agents\/(\S+)',  # .claude/agents/name
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).replace('.py', '').replace('.md', '')
    return None

def extract_files(content):
    """Extract related files from content"""
    files = []
    patterns = [
        r'([\/\w\-\.]+\.\w{2,4})',  # File paths with extension
        r'`([^`]+\.\w{2,4})`',       # Files in backticks
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, content)
        files.extend(matches)
    
    files = list(set(files))
    return [f for f in files if not f.startswith('http')] if files else None

def sync_with_claude():
    """Sync with Claude's internal TodoWrite - AUTOMATIC via hook"""
    print("[SYNC] Syncing with Claude's TodoWrite...")
    print("[INFO] The todo_sync.py hook automatically captures all TodoWrite calls!")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Show recently synced TODOs from Claude
    cursor.execute("""
        SELECT id, task, status, priority, assigned_to
        FROM todos 
        WHERE json_extract(context, '$.auto_synced') = true
        AND datetime(created_at) > datetime('now', '-5 minutes')
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    synced = cursor.fetchall()
    if synced:
        print(f"\n[STATS] Recently synced from Claude ({len(synced)} TODOs):")
        for todo_id, task, status, priority, assigned in synced:
            status_emoji = "[DONE]" if status == 'completed' else "[WIP]" if status == 'in_progress' else "[WAIT]"
            print(f"  {status_emoji} #{todo_id}: {task[:50]}...")
            if assigned:
                print(f"      → Assigned to: {assigned}")
    else:
        print("No recent Claude TODOs. Hook will auto-sync when Claude uses TodoWrite.")
    
    conn.close()

def smart_analyze():
    """AI-powered TODO analysis with pattern detection"""
    print("[AI] Smart TODO Analysis...")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    updates_made = 0
    
    # 1. Find uncategorized TODOs and categorize them
    cursor.execute("""
        SELECT id, task FROM todos 
        WHERE (category IS NULL OR module IS NULL)
        AND status != 'completed'
    """)
    
    for todo_id, task in cursor.fetchall():
        category = detect_category(task)
        module = extract_module(task)
        files = extract_files(task)
        
        updates = []
        params = []
        
        if category:
            updates.append("category = ?")
            params.append(category)
        if module:
            updates.append("module = ?")
            params.append(module)
        if files:
            updates.append("related_files = ?")
            params.append(json.dumps(files))
        
        if updates:
            params.append(todo_id)
            cursor.execute(f"UPDATE todos SET {', '.join(updates)} WHERE id = ?", params)
            updates_made += 1
    
    # 2. Detect dependencies between TODOs
    cursor.execute("""
        SELECT id, task FROM todos 
        WHERE status != 'completed'
        ORDER BY created_at DESC
    """)
    
    todos = cursor.fetchall()
    for i, (id1, task1) in enumerate(todos):
        # Check for explicit dependencies
        dep_patterns = [
            r'after\s+#(\d+)',
            r'requires\s+#(\d+)',
            r'depends\s+on\s+#(\d+)',
            r'blocked\s+by\s+#(\d+)',
        ]
        
        deps = []
        for pattern in dep_patterns:
            matches = re.findall(pattern, task1, re.IGNORECASE)
            deps.extend(matches)
        
        if deps:
            cursor.execute(
                "UPDATE todos SET dependencies = ? WHERE id = ?",
                (json.dumps(list(set(deps))), id1)
            )
            updates_made += 1
            print(f"[DEPS] Found dependencies for TODO #{id1}: {deps}")
    
    # 3. Suggest agent assignments based on module/category
    cursor.execute("""
        SELECT id, task, module, category FROM todos 
        WHERE assigned_to IS NULL 
        AND status = 'pending'
    """)
    
    for todo_id, task, module, category in cursor.fetchall():
        suggested_agent = None
        
        if module:
            # Check for module-specific agent
            agent_name = f"acolyte.{module}"
            cursor.execute("SELECT name FROM agents_catalog WHERE name = ?", (agent_name,))
            if cursor.fetchone():
                suggested_agent = agent_name
        
        if not suggested_agent and category:
            # Category-based suggestion
            category_agents = {
                'bug': 'error-detective',
                'test': 'test-automation-specialist',
                'docs': 'docs.specialist',
                'refactor': 'architecture-engineer',
                'feature': 'engineer-laravel',
                'maintenance': 'devops-troubleshooter'
            }
            suggested_agent = category_agents.get(category)
        
        if suggested_agent:
            print(f"[SUGGEST] Assign TODO #{todo_id} to {suggested_agent}")
            cursor.execute(
                "UPDATE todos SET ai_suggested = 1, context = ? WHERE id = ?",
                (json.dumps({'suggested_agent': suggested_agent}), todo_id)
            )
            updates_made += 1
    
    conn.commit()
    conn.close()
    
    print(f"[DONE] Smart analysis complete: {updates_made} updates made")

def delegate_todos():
    """Auto-delegate TODOs to appropriate agents"""
    print("[DELEGATE] Delegating TODOs to agents...")
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    delegated = 0
    
    # Find unassigned TODOs with suggestions or rules
    cursor.execute("""
        SELECT id, task, module, category, context 
        FROM todos 
        WHERE assigned_to IS NULL 
        AND status = 'pending'
        AND (ai_suggested = 1 OR module IS NOT NULL OR category IS NOT NULL)
    """)
    
    for todo_id, task, module, category, context_json in cursor.fetchall():
        assigned = None
        context = json.loads(context_json) if context_json else {}
        
        # First check AI suggestion
        if context.get('suggested_agent'):
            assigned = context['suggested_agent']
        
        # Then check module-based assignment
        elif module:
            agent_name = f"acolyte.{module}"
            cursor.execute("SELECT name FROM agents_catalog WHERE name = ?", (agent_name,))
            if cursor.fetchone():
                assigned = agent_name
        
        # Finally use category-based assignment
        elif category:
            category_agents = {
                'bug': 'error-detective',
                'test': 'test-automation-specialist',
                'docs': 'docs.specialist',
                'refactor': 'architecture-engineer',
                'feature': 'engineer-laravel',
                'maintenance': 'devops-troubleshooter'
            }
            assigned = category_agents.get(category)
        
        if assigned:
            cursor.execute("""
                UPDATE todos 
                SET assigned_to = ?,
                    updated_at = ?,
                    updated_by = 'system'
                WHERE id = ?
            """, (assigned, get_timestamp(), todo_id))
            
            print(f"[ASSIGNED] TODO #{todo_id} to {assigned}")
            print(f"   Task: {task[:60]}...")
            delegated += 1
    
    conn.commit()
    conn.close()
    
    print(f"[DONE] Delegated {delegated} TODOs to agents")

def complete_todo(todo_id):
    """Mark TODO as completed with subtask handling"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    timestamp = get_timestamp()
    
    # Get TODO details before completing
    cursor.execute("SELECT task, subtasks_total, subtasks_completed FROM todos WHERE id = ?", (todo_id,))
    todo = cursor.fetchone()
    
    if not todo:
        print(f"[ERROR] TODO #{todo_id} not found")
        conn.close()
        return
    
    task, total_sub, completed_sub = todo
    
    # Check if has incomplete subtasks
    if total_sub and total_sub > 0 and (not completed_sub or completed_sub < total_sub):
        print(f"[WARNING] TODO #{todo_id} has {total_sub - (completed_sub or 0)} incomplete subtasks")
        response = input("Complete anyway? (y/n): ")
        if response.lower() != 'y':
            conn.close()
            return
    
    # Mark as completed
    cursor.execute("""
        UPDATE todos 
        SET status = 'completed', 
            completed_at = ?,
            completed_by = 'user',
            updated_at = ?
        WHERE id = ?
    """, (timestamp, timestamp, todo_id))
    
    if cursor.rowcount > 0:
        # Update parent's subtask counter if this is a subtask
        cursor.execute("""
            SELECT id FROM todos 
            WHERE json_extract(context, '$.parent_id') = ?
        """, (str(todo_id),))
        
        parent = cursor.fetchone()
        if parent:
            cursor.execute("""
                UPDATE todos 
                SET subtasks_completed = (
                    SELECT COUNT(*) FROM todos 
                    WHERE json_extract(context, '$.parent_id') = ? 
                    AND status = 'completed'
                )
                WHERE id = ?
            """, (str(parent[0]), parent[0]))
        
        conn.commit()
        print(f"[COMPLETED] TODO #{todo_id}: {task[:50]}...")
    
    conn.close()

def list_todos(filter_type='pending'):
    """List TODOs with smart filtering and formatting"""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Build query based on filter
    where_clauses = {
        'all': "1=1",
        'pending': "status = 'pending'",
        'in_progress': "status = 'in_progress'",
        'completed': "status = 'completed'",
        'blocked': "status = 'blocked'",
        'today': "date(due_date) = date('now')",
        'overdue': "date(due_date) < date('now') AND status != 'completed'",
        'week': "date(due_date) <= date('now', '+7 days') AND status != 'completed'",
        'assigned': "assigned_to IS NOT NULL AND status != 'completed'",
        'unassigned': "assigned_to IS NULL AND status != 'completed'",
        'high': "priority IN ('high', 'critical') AND status != 'completed'",
        'synced': "json_extract(context, '$.auto_synced') = true",
        'delegated': "json_extract(context, '$.delegated_via') = 'Task tool'"
    }
    
    where_clause = where_clauses.get(filter_type, "status != 'completed'")
    
    cursor.execute(f"""
        SELECT 
            t.id, t.task, t.priority, t.status, t.category,
            t.assigned_to, t.due_date, t.created_at, t.module,
            t.subtasks_total, t.subtasks_completed,
            t.auto_created, t.ai_suggested, t.blocked_reason,
            t.assigned_to as agent_name
        FROM todos t
        WHERE {where_clause}
        ORDER BY 
            CASE 
                WHEN t.status = 'in_progress' THEN 0
                WHEN date(t.due_date) < date('now') THEN 1
                WHEN date(t.due_date) = date('now') THEN 2
                ELSE 3
            END,
            CASE t.priority 
                WHEN 'critical' THEN 1 
                WHEN 'high' THEN 2 
                WHEN 'medium' THEN 3 
                ELSE 4 
            END,
            t.created_at DESC
    """)
    
    todos = cursor.fetchall()
    
    if not todos:
        print(f"No TODOs found for filter: {filter_type}")
        conn.close()
        return
    
    print(f"\n[TODOS] {filter_type.upper()}: {len(todos)} items\n")
    
    # Group by status
    by_status = {}
    for todo in todos:
        status = todo['status']
        if status not in by_status:
            by_status[status] = []
        by_status[status].append(todo)
    
    # Display each status group
    for status in ['in_progress', 'pending', 'blocked', 'completed']:
        if status not in by_status:
            continue
        
        status_todos = by_status[status]
        
        # Compact status header
        print(f"{status.upper()}: {len(status_todos)}")
        
        for todo in status_todos:
            # Priority 
            pri = {'critical': '!!!', 'high': '!!', 'medium': '!', 'low': '.'}.get(todo['priority'], ' ')
            
            # Task (max 50 chars)
            task = todo['task'][:50] + '..' if len(todo['task']) > 50 else todo['task']
            
            # Simple one-line format
            line = f"  [{pri}] #{todo['id']:3} {task}"
            
            # Add critical info only
            if todo['assigned_to']:
                line += f" @{todo['assigned_to']}"
            if todo['due_date']:
                due = datetime.strptime(todo['due_date'], '%Y-%m-%d').date()
                today = datetime.now().date()
                if due < today:
                    line += " [OVERDUE]"
                elif due == today:
                    line += " [TODAY]"
            
            print(line)
    
    # Compact summary
    p = len([t for t in todos if t['status'] == 'pending'])
    i = len([t for t in todos if t['status'] == 'in_progress']) 
    print(f"\nTotal: {len(todos)} | Pending: {p} | In Progress: {i}")
    
    conn.close()


def session_end_todos():
    """Auto-create TODOs at session end based on analysis"""
    print("[SESSION] Analyzing session for auto-TODOs...")
    
    # This is handled by session_end.py hook
    # But we can manually trigger it here
    import subprocess
    try:
        result = subprocess.run(
            ['uv', 'run', '.claude/hooks/session_end.py'],
            capture_output=True,
            text=True,
            check=False  # Don't raise exception on non-zero exit
        )
        
        if result.returncode != 0:
            print(f"[ERROR] Session analysis failed: {result.stderr}")
        elif result.stdout:
            print(result.stdout)
        else:
            print("Session analysis complete. TODOs created if needed.")
    except FileNotFoundError:
        print("[ERROR] 'uv' command not found or session_end.py script missing")
    except subprocess.TimeoutExpired:
        print("[ERROR] Session analysis timed out")
    except Exception as e:
        print(f"[ERROR] Failed to run session analysis: {e}")

def update_status(todo_id, new_status):
    """Update TODO status with validation"""
    valid_statuses = ['pending', 'in_progress', 'completed', 'blocked', 'cancelled']
    
    if new_status not in valid_statuses:
        print(f"[ERROR] Invalid status. Must be one of: {', '.join(valid_statuses)}")
        return
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    timestamp = get_timestamp()
    updates = {
        'status': new_status,
        'updated_at': timestamp
    }
    
    # Add specific fields based on status
    if new_status == 'in_progress':
        updates['start_date'] = timestamp
    elif new_status == 'completed':
        updates['completed_at'] = timestamp
        updates['completed_by'] = 'user'
    
    # Build update query
    set_clause = ', '.join([f"{k} = ?" for k in updates.keys()])
    values = list(updates.values()) + [todo_id]
    
    cursor.execute(f"UPDATE todos SET {set_clause} WHERE id = ?", values)
    
    if cursor.rowcount > 0:
        conn.commit()
        print(f"[UPDATED] TODO #{todo_id} status: {new_status}")
    else:
        print(f"[ERROR] TODO #{todo_id} not found")
    
    conn.close()

# Main execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Advanced TODO Management')
    # SOLO manejamos list - los demás van por MCP
    parser.add_argument('action', nargs='?', default='list',
                       choices=['list'])  # Solo list está disponible
    parser.add_argument('args', nargs='*', help='Filter type for list')
    parser.add_argument('--filter', default='pending',
                       help='Filter for list command')
    
    args = parser.parse_args()
    
    # SOLO manejamos LIST - todo lo demás va por MCP/Claude
    if args.action == 'list':
        filter_type = args.args[0] if args.args else args.filter
        list_todos(filter_type)
    else:
        # Default: listar pendientes
        list_todos('pending')