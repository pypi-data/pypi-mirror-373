#!/usr/bin/env python3
"""
SQLite helper for agents and Claude to manage the database
Usage: python agent_db.py [command] [args]

Commands:
  init                      - Initialize database with schema
  create-agent [name] --module [module] [--sub-module [sub]]  - Create acolyte with catalog entry
  update-memory [agent] [type] [content] - Update specific memory
  get-memory [agent] [type] - Get specific memory content
  list-agents              - List all agents
  query [sql]              - Run read-only query
  execute [sql]            - Run write operation
  search-agents [query]    - Search agents semantically by tags/tech_stack (e.g., "JWT authentication")
"""
import sqlite3
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

def get_timestamp():
    """Get current timestamp in local time format"""
    return datetime.now().strftime('%Y-%m-%d %H:%M')

# Try to find project database in current working directory first
# If not found, fall back to global database
cwd_db = Path.cwd() / '.claude' / 'memory' / 'project.db'
global_db = Path.home() / '.claude' / 'memory' / 'project.db'

if cwd_db.exists():
    DB_PATH = cwd_db
elif global_db.exists():
    DB_PATH = global_db
else:
    # Create in current directory if neither exists
    DB_PATH = cwd_db
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
MEMORY_TYPES = ['knowledge', 'structure', 'patterns', 'interfaces', 
                'dependencies', 'schemas', 'quality', 'operations', 
                'context', 'domain', 'security', 'errors', 
                'performance', 'history']

def query(sql, params=None):
    """Read-only query"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(sql, params or [])
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return json.dumps(results, indent=2)

def execute(sql, params=None):
    """Write operation with auto-timestamp"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(sql, params or [])
    conn.commit()
    affected = cursor.rowcount
    last_id = cursor.lastrowid
    conn.close()
    return json.dumps({"affected": affected, "id": last_id})

def init_database():
    """Initialize database with schema from init_db.sql"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    sql_file = Path(__file__).parent / 'init_db.sql'
    
    if not sql_file.exists():
        return json.dumps({"error": "init_db.sql not found"})
    
    conn = sqlite3.connect(DB_PATH)
    with open(sql_file, 'r') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    return json.dumps({"success": True, "message": f"Database initialized at {DB_PATH}"})

def create_agent(name, module=None, sub_module=None):
    """Create agent with 14 empty memory records and add to agents_catalog"""
    timestamp = get_timestamp()
    conn = sqlite3.connect(DB_PATH)
    
    # Ensure name starts with @
    if not name.startswith('@'):
        name = '@' + name
    
    # Module is required for acolytes
    if not module:
        conn.close()
        return json.dumps({"error": "Module parameter is required for acolytes"})
    
    try:
        # Check if agent already exists in agents_catalog
        cursor = conn.execute("SELECT 1 FROM agents_catalog WHERE name = ?", (name,))
        if cursor.fetchone():
            conn.close()
            return json.dumps({"error": f"Agent '{name}' already exists in agents_catalog"})
        # Start explicit transaction
        conn.execute("BEGIN TRANSACTION")
        # Insert ONLY into agents_catalog (no more acolytes table)
        conn.execute(
            "INSERT INTO agents_catalog (name, type, module, sub_module) VALUES (?, 'acolyte', ?, ?)",
            (name, module, sub_module)
        )
        # Insert 14 empty memory records using agent_name directly
        for memory_type in MEMORY_TYPES:
            conn.execute(
                "INSERT INTO agents_memory (agent_name, memory_type, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (name, memory_type, '{}', timestamp, timestamp)
            )
        # Commit the transaction
        conn.commit()
        return json.dumps({
            "success": True, 
            "agent_name": name,
            "module": module,
            "sub_module": sub_module,
            "memories_created": len(MEMORY_TYPES),
            "catalog_entry": "created"
        })
        
    except sqlite3.IntegrityError as e:
        conn.rollback()
        return json.dumps({"error": f"Database integrity error: {str(e)}"})
    except Exception as e:
        conn.rollback()
        return json.dumps({"error": f"Unexpected error: {str(e)}"})
    finally:
        conn.close()

def update_memory(agent_name, memory_type, content):
    """Update specific memory for an agent using agent name"""
    if memory_type not in MEMORY_TYPES:
        return json.dumps({"error": f"Invalid memory_type. Must be one of: {MEMORY_TYPES}"})
    # Ensure agent_name starts with @
    if not agent_name.startswith('@'):
        agent_name = '@' + agent_name
    timestamp = get_timestamp()
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Update memory directly using agent_name (no ID lookup needed)
        cursor = conn.execute(
            "UPDATE agents_memory SET content = ?, updated_at = ? WHERE agent_name = ? AND memory_type = ?",
            (json.dumps(content) if isinstance(content, dict) else content, timestamp, agent_name, memory_type)
        )
        if cursor.rowcount == 0:
            return json.dumps({"error": f"Memory type '{memory_type}' not found for agent '{agent_name}'"})
        conn.commit()
        return json.dumps({"success": True, "agent": agent_name, "memory_type": memory_type, "updated_at": timestamp})
    except Exception as e:
        conn.rollback()
        return json.dumps({"error": str(e)})
    finally:
        conn.close()

def add_interaction(agent_name, interaction_type, request, response, 
                   files_touched=None,
                   delegated_to=None, outcome='success'):
    """Add a new interaction to agent's history memory
    This appends to the history array in the history memory type
    """
    timestamp = get_timestamp()
    conn = sqlite3.connect(DB_PATH)
    # Ensure agent_name starts with @
    if not agent_name.startswith('@'):
        agent_name = '@' + agent_name
    try:
        # Get current history memory (interactions was renamed to history)
        cursor = conn.execute("""
            SELECT content FROM agents_memory 
            WHERE agent_name = ? AND memory_type = 'history'
        """, (agent_name,))
        row = cursor.fetchone()
        if not row:
            # Create history memory if doesn't exist
            content = {"history": []}
            conn.execute(
                "INSERT INTO agents_memory (agent_name, memory_type, content, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                (agent_name, 'history', json.dumps(content), timestamp, timestamp)
            )
        else:
            content = json.loads(row[0]) if row[0] else {"history": []}
        # Ensure history array exists
        if 'history' not in content:
            content['history'] = []
        # Add new interaction
        new_interaction = {
            "timestamp": timestamp,
            "type": interaction_type,
            "request": request,
            "response": response,
            "outcome": outcome
        }
        # Add optional fields if provided
        if files_touched:
            new_interaction["files_touched"] = files_touched
        if delegated_to:
            new_interaction["delegated_to"] = delegated_to
        # Append to history
        content['history'].append(new_interaction)
        
        # Keep only last 100 interactions in storage (but return only last 10 when reading)
        if len(content['history']) > 100:
            content['history'] = content['history'][-100:]
        
        # Update the memory
        cursor = conn.execute(
            "UPDATE agents_memory SET content = ?, updated_at = ? WHERE agent_name = ? AND memory_type = 'history'",
            (json.dumps(content), timestamp, agent_name)
        )
        conn.commit()
        return json.dumps({
            "success": True, 
            "agent": agent_name, 
            "interaction_logged": timestamp,
            "total_interactions": len(content['history'])
        })
    except Exception as e:
        conn.rollback()
        return json.dumps({"error": str(e)})
    finally:
        conn.close()

def get_memory(agent_name, memory_type, limit=None):
    """Get specific memory content for an agent
    For 'history' memory, only returns last 10 entries by default
    """
    if memory_type not in MEMORY_TYPES:
        return json.dumps({"error": f"Invalid memory_type. Must be one of: {MEMORY_TYPES}"})
    # Ensure agent_name starts with @
    if not agent_name.startswith('@'):
        agent_name = '@' + agent_name
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    cursor = conn.execute("""
        SELECT content, updated_at
        FROM agents_memory
        WHERE agent_name = ? AND memory_type = ?
    """, (agent_name, memory_type))
    
    row = cursor.fetchone()
    conn.close()
    
    if row:
        content = json.loads(row['content']) if row['content'] else {}
        
        # Special handling for history - only return last 10
        if memory_type == 'history' and isinstance(content, dict) and 'history' in content:
            if isinstance(content['history'], list):
                # Store total count BEFORE slicing
                total_interactions = len(content['history'])
                # Only return last 10 interactions
                content['history'] = content['history'][-10:]
                content['showing_last'] = 10
                content['total_count'] = total_interactions
        return json.dumps({
            "agent": agent_name,
            "memory_type": memory_type,
            "content": content,
            "updated_at": row['updated_at']
        })
    else:
        return json.dumps({"error": f"Memory not found for agent '{agent_name}' type '{memory_type}'"})

def update_health(agent_name, drift_score, status, memory_size_kb=None, 
                  file_count_current=None, needs_compaction=False,
                  largest_memory_type=None, recommendations=None):
    """Update agent health record"""
    timestamp = get_timestamp()
    conn = sqlite3.connect(DB_PATH)
    # Ensure agent_name starts with @
    if not agent_name.startswith('@'):
        agent_name = '@' + agent_name
    
    # Verify agent exists
    cursor = conn.execute("SELECT name FROM agents_catalog WHERE name = ?", (agent_name,))
    agent = cursor.fetchone()
    if not agent:
        conn.close()
        return json.dumps({"error": f"Agent '{agent_name}' not found in catalog"})
    
    # Get current session_id
    cursor = conn.execute("SELECT id FROM sessions WHERE ended_at IS NULL ORDER BY created_at DESC LIMIT 1")
    session = cursor.fetchone()
    session_id = session[0] if session else None
    
    # Determine memory warning level
    memory_warning = None
    if memory_size_kb:
        if memory_size_kb > 2000:
            memory_warning = "critical"
        elif memory_size_kb > 1000:
            memory_warning = "large"
    
    # Insert new health record (maintains history)
    conn.execute("""
        INSERT INTO agent_health (
            agent_name, session_id, drift_score, status, memory_size_kb,
            memory_size_warning, largest_memory_type, needs_compaction,
            file_count_current, recommendations, checked_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        agent_name, session_id, drift_score, status, memory_size_kb,
        memory_warning, largest_memory_type, needs_compaction,
        file_count_current, recommendations, timestamp
    ))
    
    conn.commit()
    health_id = cursor.lastrowid
    conn.close()
    
    return json.dumps({
        "success": True,
        "health_id": health_id,
        "agent": agent_name,
        "status": status,
        "drift_score": drift_score,
        "memory_warning": memory_warning
    })

def get_agent_health(agent_name=None):
    """Get health status for agent(s)"""
    sql = """
        SELECT 
            h.agent_name, h.drift_score, h.status, h.memory_size_kb,
            h.memory_size_warning, h.needs_compaction, h.checked_at,
            h.recommendations
        FROM agent_health h
        JOIN agents_catalog ac ON h.agent_name = ac.name
    """
    params = []
    
    if agent_name:
        if not agent_name.startswith('@'):
            agent_name = '@' + agent_name
        sql += " WHERE h.agent_name = ?"
        params.append(agent_name)
    
    sql += " ORDER BY h.checked_at DESC"
    
    return query(sql, params)

def search_agents_semantic(search_query, limit=5):
    """Search agents using semantic matching with tags, tech_stack, role and scenarios
    
    Args:
        search_query: Text to search for (e.g., "JWT authentication implementation")
        limit: Maximum number of results to return (default: 5)
    
    Returns:
        JSON with ranked list of matching agents with scores and reasons
    """
    if not search_query or not search_query.strip():
        return json.dumps({"error": "search_query is required and cannot be empty"})
    
    query_lower = search_query.lower().strip()
    query_words = set(query_lower.split())
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Get all agents with their searchable content
    cursor = conn.execute("""
        SELECT name, type, module, sub_module, 
               role, tech_stack, scenarios, tags, connections
        FROM agents_catalog
    """)
    
    agents = cursor.fetchall()
    conn.close()
    
    if not agents:
        return json.dumps({"error": "No active agents found in catalog"})
    
    results = []
    
    for agent in agents:
        score = 0
        reasons = []
        
        # Parse JSON fields safely
        try:
            tags = json.loads(agent['tags'] or '[]') if agent['tags'] else []
            tech_stack = json.loads(agent['tech_stack'] or '[]') if agent['tech_stack'] else []
            scenarios = json.loads(agent['scenarios'] or '[]') if agent['scenarios'] else []
            role = json.loads(agent['role'] or '[]') if agent['role'] else []
        except (json.JSONDecodeError, TypeError):
            tags = []
            tech_stack = []
            scenarios = []
            role = []
        
        # Convert to strings for matching
        tags_text = ' '.join(tags).lower() if tags else ''
        tech_stack_text = ' '.join(tech_stack).lower() if tech_stack else ''
        scenarios_text = ' '.join(scenarios).lower() if scenarios else ''
        role_text = ' '.join(role).lower() if role else ''
        module_text = f"{agent['module'] or ''} {agent['sub_module'] or ''}".lower()
        
        # Score calculation with different weights
        
        # 1. Exact tag matches (highest weight: 50 points each)
        for tag in tags:
            if isinstance(tag, str) and tag.lower() in query_lower:
                score += 50
                reasons.append(f"exact tag: '{tag}'")
        
        # 2. Partial tag word matches (40 points each)
        tag_words = set(tags_text.split())
        matching_tag_words = query_words.intersection(tag_words)
        for word in matching_tag_words:
            score += 40
            reasons.append(f"tag match: '{word}'")
        
        # 3. Tech stack matches (30 points each)
        tech_stack_words = set(tech_stack_text.split())
        matching_tech_words = query_words.intersection(tech_stack_words)
        for word in matching_tech_words:
            score += 30
            reasons.append(f"tech_stack: '{word}'")
        
        # 4. Role/description matches (20 points each)
        role_words = set(role_text.split())
        matching_role_words = query_words.intersection(role_words)
        for word in matching_role_words:
            score += 20
            reasons.append(f"role: '{word}'")
        
        # 4b. Scenarios matches (20 points each)
        scenarios_words = set(scenarios_text.split())
        matching_scenarios_words = query_words.intersection(scenarios_words)
        for word in matching_scenarios_words:
            score += 20
            reasons.append(f"scenario: '{word}'")
        
        # 5. Module/sub_module matches (15 points each)
        module_words = set(module_text.split())
        matching_module_words = query_words.intersection(module_words)
        for word in matching_module_words:
            if word:  # Skip empty strings
                score += 15
                reasons.append(f"module: '{word}'")
        
        # 6. Bonus for multiple criteria matches
        criteria_matched = sum([
            bool(matching_tag_words),
            bool(matching_tech_words), 
            bool(matching_role_words),
            bool(matching_scenarios_words),
            bool(matching_module_words)
        ])
        if criteria_matched >= 2:
            score += 25  # Bonus for multi-criteria match
            reasons.append("multi-criteria match bonus")
        
        # Only include agents with non-zero scores
        if score > 0:
            results.append({
                "name": agent['name'],
                "type": agent['type'],
                "module": agent['module'],
                "sub_module": agent['sub_module'],
                "role": agent['role'],
                "score": score,
                "reasons": reasons[:3]  # Limit to top 3 reasons for readability
            })
    
    # Sort by score (descending) and limit results
    results.sort(key=lambda x: x['score'], reverse=True)
    results = results[:limit]
    
    # Add ranking information
    for i, result in enumerate(results, 1):
        result['rank'] = i
    
    return json.dumps({
        "query": search_query,
        "total_matches": len(results),
        "results": results
    }, indent=2)

def check_active_job_exists(cursor):
    """Check if there is currently an active job in the system
    
    Args:
        cursor: Database cursor to use for the query
    
    Returns:
        bool: True if an active job exists, False otherwise
    """
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = 'active'")
    active_count = cursor.fetchone()[0]
    return active_count > 0

def activate_job(job_id):
    """Activate a specific job, automatically pausing any currently active job
    
    Args:
        job_id: The ID of the job to activate
    
    Returns:
        JSON with activation status and details
    
    Ensures exactly one active job at all times by:
    1. Finding and pausing any currently active job
    2. Activating the specified job
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Start transaction for atomic operation
        cursor.execute("BEGIN TRANSACTION")
        
        # Check if the job exists
        cursor.execute("SELECT id, title, status FROM jobs WHERE id = ?", (job_id,))
        job = cursor.fetchone()
        
        if not job:
            conn.rollback()
            return {
                "success": False,
                "error": f"Job {job_id} not found"
            }
        
        if job[2] == 'active':
            conn.rollback()
            return {
                "success": False,
                "message": f"Job {job_id} is already active"
            }
        
        # Find and pause any currently active job
        cursor.execute("SELECT id, title FROM jobs WHERE status = 'active'")
        active_job = cursor.fetchone()
        
        if active_job:
            cursor.execute("""
                UPDATE jobs 
                SET status = 'paused', 
                    paused_at = datetime('now'),
                    pause_reason = ?
                WHERE id = ?
            """, (f"Switched to job {job_id}", active_job[0]))
        
        # Activate the specified job
        cursor.execute("""
            UPDATE jobs 
            SET status = 'active', 
                resumed_at = datetime('now'),
                pause_reason = NULL
            WHERE id = ?
        """, (job_id,))
        conn.commit()
        
        result = {
            "success": True,
            "activated_job": {
                "id": job_id,
                "title": job[1]
            }
        }
        
        if active_job:
            result["previously_active"] = {
                "id": active_job[0],
                "title": active_job[1],
                "status": "paused"
            }
        
        return result
        
    except Exception as e:
        conn.rollback()
        return {
            "success": False,
            "error": str(e)
        }
    finally:
        conn.close()

def cleanup_orphaned_jobs():
    """Clean up jobs that should be completed but are still marked as active"""
    conn = sqlite3.connect(DB_PATH)
    
    # Find jobs with no recent sessions (more than 24 hours old)
    cursor = conn.execute("""
        SELECT j.id FROM jobs j
        WHERE j.status = 'active' 
        AND NOT EXISTS (
            SELECT 1 FROM sessions s 
            WHERE s.job_id = j.id 
            AND datetime(s.created_at) > datetime('now', '-1 day')
        )
    """)
    
    orphaned_jobs = cursor.fetchall()
    
    if orphaned_jobs:
        # Mark them as paused with reason
        for job in orphaned_jobs:
            conn.execute("""
                UPDATE jobs SET 
                    status = 'paused',
                    paused_at = ?,
                    pause_reason = 'Auto-paused: No recent sessions detected'
                WHERE id = ?
            """, (get_timestamp(), job[0]))
        conn.commit()
        result = f"Cleaned up {len(orphaned_jobs)} orphaned jobs"
    else:
        result = "No orphaned jobs found"
    
    conn.close()
    return json.dumps({"message": result, "jobs_cleaned": len(orphaned_jobs)})

def create_job(title, description, priority="medium", estimated_hours=None, 
               required_skills=None, job_type=None, tech_stack=None, 
               phase=None, dependencies=None, success_criteria=None,
               status="paused", pause_reason="Awaiting start"):
    """Create a new job in the jobs table with detailed configuration
    
    Args:
        title: Job title
        description: Plain text description of the job
        priority: Priority level (high/medium/low)
        estimated_hours: Estimated hours for completion
        required_skills: Required skills for the job
        job_type: Type of job (foundation/feature/integration/deployment)
        tech_stack: Technologies involved
        phase: Project phase (foundation/core_development/integration/deployment)
        dependencies: Comma-separated list of job IDs this depends on
        success_criteria: Measurable success criteria
        status: Initial status (default: paused)
        pause_reason: Reason for pause if status is paused
    
    Returns:
        JSON with created job details
    
    Note: Following the rule that always 1 job must be active. 
    If creating as active, will pause other active jobs.
    """
    import uuid
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Start transaction for atomic operation
    cursor.execute("BEGIN TRANSACTION")
    
    # Generate unique job ID
    job_id = f"job_{uuid.uuid4().hex[:12]}"
    
    # Build description JSON with all metadata
    job_description = {
        "summary": description,
        "priority": priority,
        "estimated_hours": estimated_hours,
        "required_skills": required_skills.split(",") if required_skills else [],
        "job_type": job_type,
        "tech_stack": tech_stack,
        "phase": phase,
        "dependencies": dependencies.split(",") if dependencies else [],
        "success_criteria": success_criteria.split(";") if success_criteria else [],
        "created_by": "plan.strategy"
    }
    
    # Single check for active jobs to determine final status
    has_active_job = check_active_job_exists(cursor)
    
    if has_active_job:
        # There's already an active job
        if status == "active":
            # Force to paused if trying to create as active
            status = "paused"
            pause_reason = "Created as paused - another job is already active"
    else:
        # No active jobs exist
        if status == "paused":
            # Auto-activate if no other jobs are active
            status = "active"
            pause_reason = None
    
    # Insert the job
    timestamp = get_timestamp()
    
    try:
        cursor.execute("""
            INSERT INTO jobs (id, title, description, status, created_at, paused_at, pause_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            job_id,
            title,
            json.dumps(job_description),
            status,
            timestamp,
            timestamp if status == "paused" else None,
            pause_reason if status == "paused" else None
        ))
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "job_id": job_id,
            "title": title,
            "status": status,
            "phase": phase,
            "estimated_hours": estimated_hours,
            "message": f"Job '{title}' created successfully with ID: {job_id}"
        }
        
    except Exception as e:
        conn.rollback()  # Rollback transaction on error
        conn.close()
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create job: {str(e)}"
        }

def list_available_agents():
    """List all available agents from catalog"""
    conn = sqlite3.connect(DB_PATH)
    
    try:
        # Get all agents from catalog (including acolytes with type='acolyte')
        cursor = conn.execute("""
            SELECT name, type, module, sub_module, role 
            FROM agents_catalog 
            ORDER BY type, module, name
        """)
        all_agents = cursor.fetchall()
        
        # Separate global agents from acolytes
        global_agents = []
        acolytes = []
        
        for agent in all_agents:
            if agent[1] == 'acolyte':
                acolytes.append({
                    "name": agent[0],
                    "module": agent[2],
                    "sub_module": agent[3]
                })
            else:
                global_agents.append({
                    "name": agent[0],
                    "type": agent[1],
                    "module": agent[2],
                    "sub_module": agent[3],
                    "role": agent[4]
                })
        
        result = {
            "global_agents": global_agents,
            "acolytes": acolytes,
            "total_global": len(global_agents),
            "total_dynamic": len(acolytes)
        }
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)})
    finally:
        conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        print("=" * 70)
        print("ACOLYTES FOR CLAUDE CODE - Database Management System")
        print("=" * 70)
        print("\nUsage: python agent_db.py [command] [args...]")
        print("\n" + "=" * 70)
        print("JOB MANAGEMENT COMMANDS")
        print("=" * 70)
        print("\n--job                     Job management commands")
        print("  Create new job:")
        print("    --title TEXT          Job title")
        print("    --description TEXT    Job summary/description")
        print("  Optional:")
        print("    --priority TEXT       Priority level (high/medium/low, default: medium)")
        print("    --estimated_hours NUM Estimated hours to complete")
        print("    --required_skills CSV Skills needed (comma-separated)")
        print("    --job_type TEXT       Type: foundation/feature/integration/deployment")
        print("    --tech_stack CSV      Technologies involved (comma-separated)")
        print("    --phase TEXT          Phase: foundation/core_development/integration/deployment")
        print("    --dependencies CSV    Dependent job IDs (comma-separated)")
        print("    --success_criteria SC Success criteria (semicolon-separated)")
        print("    --activate           Immediately activate this job (pauses current active job)")
        print("\n  Other job operations:")
        print("    --activate JOB_ID    Switch to a different job (pauses current)")
        print("    --list               Show last 10 jobs with status")
        print("\nExamples:")
        print('  agent_db.py --job --title "Add user auth" --description "Implement OAuth2"')
        print('  agent_db.py --job --title "Fix bugs" --description "Critical fixes" --activate')
        print('  agent_db.py --job --activate job_48330ca18339  # Switch to existing job')
        print('  agent_db.py --job --list  # Show recent jobs')
        print("\n" + "=" * 70)
        print("OTHER COMMANDS")
        print("=" * 70)
        print("\nCore: init, create-agent, update-memory, get-memory, query, execute")
        print("Agents: search-agents, update-health, get-health, add-interaction")
        print("Jobs: cleanup-jobs")
        sys.exit(1)
    
    command = sys.argv[1]
    
    try:
        if command == "init":
            print(init_database())
        
        elif command == "create-agent":
            if len(sys.argv) < 3:
                print("Usage: python agent_db.py create-agent [name] --module [module] [--sub-module [sub-module]]")
                print("Example: python agent_db.py create-agent @acolyte.auth --module auth")
                print("Example: python agent_db.py create-agent @acolyte.api-auth --module api --sub-module auth")
                sys.exit(1)
            
            name = sys.argv[2]
            module = None
            sub_module = None
            
            # Parse command line arguments
            i = 3
            while i < len(sys.argv):
                if sys.argv[i] == "--module" and i + 1 < len(sys.argv):
                    module = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == "--sub-module" and i + 1 < len(sys.argv):
                    sub_module = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            
            print(create_agent(name, module, sub_module))
        
        elif command == "update-memory":
            if len(sys.argv) < 5:
                print("Usage: python agent_db.py update-memory [agent-name] [memory-type] [content-json]")
                sys.exit(1)
            agent_name = sys.argv[2]
            memory_type = sys.argv[3]
            try:
                content = json.loads(sys.argv[4])
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"Invalid JSON: {e}"}))
                sys.exit(1)
            print(update_memory(agent_name, memory_type, content))
        
        elif command == "get-memory":
            if len(sys.argv) < 4:
                print("Usage: python agent_db.py get-memory [agent-name] [memory-type]")
                sys.exit(1)
            agent_name = sys.argv[2]
            memory_type = sys.argv[3]
            print(get_memory(agent_name, memory_type))
        
        elif command == "query":
            sql = sys.argv[2]
            try:
                params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"Invalid JSON params: {e}"}))
                sys.exit(1)
            print(query(sql, params))
        
        elif command == "execute":
            sql = sys.argv[2]
            try:
                params = json.loads(sys.argv[3]) if len(sys.argv) > 3 else None
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"Invalid JSON params: {e}"}))
                sys.exit(1)
            print(execute(sql, params))

        elif command == "update-health":
            # Parse arguments for health update
            import argparse
            parser = argparse.ArgumentParser()
            parser.add_argument('command')
            parser.add_argument('--agent_name', required=True)
            parser.add_argument('--drift_score', type=int, required=True)
            parser.add_argument('--status', required=True)
            parser.add_argument('--memory_size_kb', type=float, default=None)
            parser.add_argument('--file_count_current', type=int, default=None)
            parser.add_argument('--needs_compaction', type=bool, default=False)
            parser.add_argument('--largest_memory_type', default=None)
            parser.add_argument('--recommendations', default=None)
            
            args = parser.parse_args(sys.argv[1:])
            print(update_health(
                args.agent_name, args.drift_score, args.status,
                args.memory_size_kb, args.file_count_current, 
                args.needs_compaction, args.largest_memory_type,
                args.recommendations
            ))
        
        elif command == "get-health":
            health_agent_name: Optional[str] = sys.argv[2] if len(sys.argv) > 2 else None
            print(get_agent_health(health_agent_name))
        
        
        elif command == "timestamp":
            print(get_timestamp())
        
        # INTERACTIONS COMMAND
        elif command == "add-interaction":
            if len(sys.argv) < 5:
                print("Usage: python agent_db.py add-interaction [agent_name] [type] [request] [response]")
                print("Optional: --files [files] --delegated_to [agents] --outcome [outcome]")
                sys.exit(1)
            
            agent_name = sys.argv[2]
            interaction_type = sys.argv[3]
            request = sys.argv[4]
            response = sys.argv[5] if len(sys.argv) > 5 else ""
            
            # Parse optional arguments
            files_touched = None
            delegated_to = None
            outcome = 'success'
            
            i = 6
            while i < len(sys.argv):
                if sys.argv[i] == '--files' and i + 1 < len(sys.argv):
                    files_touched = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--delegated_to' and i + 1 < len(sys.argv):
                    delegated_to = sys.argv[i + 1]
                    i += 2
                elif sys.argv[i] == '--outcome' and i + 1 < len(sys.argv):
                    outcome = sys.argv[i + 1]
                    i += 2
                else:
                    i += 1
            
            print(add_interaction(
                agent_name, interaction_type, request, response,
                files_touched,
                delegated_to, outcome
            ))
        
        # SEARCH AGENTS COMMAND
        elif command == "search-agents":
            if len(sys.argv) < 3:
                print("Usage: python agent_db.py search-agents [search_query] [limit]")
                print("Example: python agent_db.py search-agents 'JWT authentication implementation' 5")
                sys.exit(1)
            search_query = sys.argv[2]
            limit = 5  # default
            if len(sys.argv) > 3:
                try:
                    limit = int(sys.argv[3])
                except ValueError:
                    print(json.dumps({"error": "limit must be an integer"}))
                    sys.exit(1)
            print(search_agents_semantic(search_query, limit))
        
        elif command == "list-agents":
            print(list_available_agents())
        
        elif command == "cleanup-jobs":
            print(cleanup_orphaned_jobs())
        
        elif command == "--job":
            import argparse
            parser = argparse.ArgumentParser(prog='agent_db.py --job')
            parser.add_argument('command', nargs='?')
            parser.add_argument('--title', required=False, help='Job title')
            parser.add_argument('--description', required=False, help='Job description')
            parser.add_argument('--priority', default='medium', help='Priority: high/medium/low')
            parser.add_argument('--estimated_hours', type=int, help='Estimated hours')
            parser.add_argument('--required_skills', help='Comma-separated skills')
            parser.add_argument('--job_type', help='foundation/feature/integration/deployment')
            parser.add_argument('--tech_stack', help='Technologies involved')
            parser.add_argument('--phase', help='foundation/core_development/integration/deployment')
            parser.add_argument('--dependencies', help='Comma-separated job IDs')
            parser.add_argument('--success_criteria', help='Semicolon-separated criteria')
            parser.add_argument('--activate', nargs='?', const=True, help='Activate job - can be True for new job or job_id for existing')
            parser.add_argument('--list', action='store_true', help='List last 10 jobs')
            
            # Remove the '--job' command from argv before parsing
            args = parser.parse_args(sys.argv[2:])
            
            # Check if this is listing jobs
            if args.list:
                # List last 10 jobs
                conn = sqlite3.connect(DB_PATH)
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("""
                    SELECT id, title, status, created_at, 
                           CASE 
                               WHEN status = 'active' THEN resumed_at
                               WHEN status = 'paused' THEN paused_at
                               ELSE completed_at
                           END as last_update
                    FROM jobs 
                    ORDER BY created_at DESC 
                    LIMIT 10
                """)
                jobs = [dict(row) for row in cursor.fetchall()]
                conn.close()
                
                result = {
                    "total_jobs": len(jobs),
                    "jobs": jobs
                }
                print(json.dumps(result, indent=2))
            # Check if this is just an activation of existing job
            elif args.activate and isinstance(args.activate, str) and args.activate.startswith('job_'):
                # This is: --job --activate job_xxx (activate existing job)
                result = activate_job(args.activate)
                print(json.dumps(result, indent=2))
            elif args.title and args.description:
                # This is creating a new job
                result = create_job(
                title=args.title,
                description=args.description,
                priority=args.priority,
                estimated_hours=args.estimated_hours,
                required_skills=args.required_skills,
                job_type=args.job_type,
                tech_stack=args.tech_stack,
                phase=args.phase,
                dependencies=args.dependencies,
                success_criteria=args.success_criteria,
                status='paused',
                pause_reason='Awaiting start'
            )
            
                # If --activate flag is set for new job, activate it
                if args.activate:
                    if result.get('success'):
                        activate_result = activate_job(result['job_id'])
                        # Merge both results
                        result['activated'] = True
                
                print(json.dumps(result, indent=2))
            else:
                print(json.dumps({
                    "error": "Must provide either --activate job_id OR --title and --description",
                    "usage": "agent_db.py --job --activate job_xxx OR agent_db.py --job --title '...' --description '...'"
                }))
        
        elif command == "--activate-deprecated":
            if len(sys.argv) < 3:
                print(json.dumps({
                    "error": "Missing job_id",
                    "usage": "python agent_db.py --activate JOB_ID"
                }))
                sys.exit(1)
            
            job_id = sys.argv[2]
            print(activate_job(job_id))

        else:
            print(f"Unknown command: {command}")
            print("Commands: init, create-agent, update-memory, get-memory, query, execute, update-health, get-health")
            print("Other Commands: search-agents")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)