#!/usr/bin/env python3
"""
Memory Compaction Script for Acolytes for Claude Code
Reduces memory size by removing redundant/old information while preserving critical knowledge
Usage: python compact_memory.py [agent-name]
"""
import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / 'memory' / 'project.db'

# Size limits in KB for each memory type
MEMORY_LIMITS = {
    'knowledge': 50,      # Core info, debe ser compacto
    'structure': 200,     # Puede ser grande (muchos archivos)
    'patterns': 30,       # Lista de patrones
    'dependencies': 40,   # Lista de deps
    'quality': 30,        # Métricas
    'operations': 20,     # Config
    'context': 100,       # Historia y decisiones
    'domain': 50          # Conocimiento especializado
}

def get_timestamp():
    """Get current timestamp in local time"""
    return datetime.now().strftime('%Y-%m-%d %H:%M')

def get_memory_size_kb(content):
    """Calculate memory size in KB"""
    return len(json.dumps(content)) / 1024

def compact_structure_memory(content):
    """Compact structure memory - keep only important files"""
    if 'file_tree' not in content:
        return content
    
    file_tree = content.get('file_tree', {})
    
    # If it's already compacted format, return as is
    if 'core_files' in file_tree:
        return content
    
    # Filter only important files (>100 lines or critical)
    core_files = {}
    total_files = 0
    total_lines = 0
    file_types = {}
    
    for file_path, file_info in file_tree.items():
        total_files += 1
        lines = file_info.get('lines', 0)
        total_lines += lines
        
        # Count file types
        ext = Path(file_path).suffix
        file_types[ext] = file_types.get(ext, 0) + 1
        
        # Keep important files
        if lines > 100 or file_info.get('critical', False):
            core_files[file_path] = file_info
    
    # Create compacted structure
    content['file_tree'] = {
        'summary': f"{total_files} files total, showing {len(core_files)} core files",
        'core_files': core_files,
        'statistics': {
            'total_files': total_files,
            'total_lines': total_lines,
            'by_type': file_types
        }
    }
    
    return content

def compact_context_memory(content):
    """Compact context memory - keep recent + milestones"""
    if 'history' not in content and 'decisions' not in content:
        return content
    
    history = content.get('history', [])
    decisions = content.get('decisions', [])
    
    # Keep last 10 history items
    recent_history = history[-10:] if len(history) > 10 else history
    
    # Keep important decisions (first 5 + last 5)
    if len(decisions) > 10:
        important_decisions = decisions[:5] + decisions[-5:]
    else:
        important_decisions = decisions
    
    content['history'] = recent_history
    content['decisions'] = important_decisions
    content['total_history_count'] = len(history)
    content['compacted_at'] = get_timestamp()
    
    # Remove old/redundant fields
    fields_to_remove = ['old_history', 'archived_decisions', 'temp_notes']
    for field in fields_to_remove:
        content.pop(field, None)
    
    return content

def compact_dependencies_memory(content):
    """Compact dependencies - remove versions unless critical"""
    if 'external' not in content:
        return content
    
    external = content.get('external', {})
    
    # If it's a dict with versions, convert to list
    if isinstance(external, dict):
        # Keep only package names, not versions
        package_list = list(external.keys())
        
        # Keep critical version constraints if any
        critical_versions = {}
        for pkg, version in external.items():
            # Keep version if it has constraints (>=, <=, ~, ^)
            if any(op in str(version) for op in ['>=', '<=', '~', '^', '>']):
                critical_versions[pkg] = version
        
        content['external'] = package_list[:30]  # Keep top 30 packages
        if critical_versions:
            content['critical_versions'] = critical_versions
        content['total_packages'] = len(external)
    
    return content

def compact_patterns_memory(content):
    """Compact patterns - remove resolved anti-patterns"""
    if 'anti_patterns_found' in content:
        # Keep only unresolved anti-patterns
        anti_patterns = content.get('anti_patterns_found', [])
        if isinstance(anti_patterns, list):
            # Filter out patterns marked as resolved
            unresolved = [p for p in anti_patterns if not isinstance(p, dict) or not p.get('resolved', False)]
            content['anti_patterns_found'] = unresolved[:5]  # Keep max 5
    
    # Limit design patterns list
    if 'design_patterns' in content:
        patterns = content.get('design_patterns', [])
        if len(patterns) > 10:
            content['design_patterns'] = patterns[:10]
            content['total_patterns'] = len(patterns)
    
    return content

def compact_quality_memory(content):
    """Compact quality metrics - keep only latest"""
    # Remove historical metrics
    fields_to_keep = ['test_coverage', 'code_quality', 'performance_metrics', 'security_analysis']
    
    compacted = {}
    for field in fields_to_keep:
        if field in content:
            value = content[field]
            # If it's a list of metrics, keep only the latest
            if isinstance(value, list) and len(value) > 0:
                compacted[field] = value[-1]
            else:
                compacted[field] = value
    
    compacted['last_updated'] = get_timestamp()
    return compacted

def remove_empty_fields(obj):
    """Recursively remove empty/null fields"""
    if isinstance(obj, dict):
        return {k: remove_empty_fields(v) for k, v in obj.items() 
                if v not in [None, '', [], {}, 'null', 'undefined']}
    elif isinstance(obj, list):
        return [remove_empty_fields(item) for item in obj if item not in [None, '', 'null']]
    return obj

def compact_agents_memory(agent_name):
    """Main compaction function for an agent"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Ensure agent_name starts with @
    if not agent_name.startswith('@'):
        agent_name = '@' + agent_name
    
    # Verify agent exists
    cursor = conn.execute("SELECT name FROM agents_catalog WHERE name = ?", (agent_name,))
    agent = cursor.fetchone()
    if not agent:
        return {"error": f"Agent '{agent_name}' not found in catalog"}
    
    # Get all memories for this agent
    cursor = conn.execute("""
        SELECT memory_type, content 
        FROM agents_memory 
        WHERE agent_name = ?
    """, (agent_name,))
    
    memories = cursor.fetchall()
    
    total_before = 0
    total_after = 0
    compacted_types = []
    
    for memory in memories:
        memory_type = memory['memory_type']
        content = json.loads(memory['content']) if memory['content'] else {}
        
        size_before = get_memory_size_kb(content)
        total_before += size_before
        
        # Apply compaction based on type
        if memory_type == 'structure':
            content = compact_structure_memory(content)
        elif memory_type == 'context':
            content = compact_context_memory(content)
        elif memory_type == 'dependencies':
            content = compact_dependencies_memory(content)
        elif memory_type == 'patterns':
            content = compact_patterns_memory(content)
        elif memory_type == 'quality':
            content = compact_quality_memory(content)
        
        # Remove empty fields from all types
        content = remove_empty_fields(content)
        
        size_after = get_memory_size_kb(content)
        total_after += size_after
        
        # Update if size reduced
        if size_after < size_before:
            conn.execute("""
                UPDATE agents_memory 
                SET content = ?, updated_at = ?
                WHERE agent_name = ? AND memory_type = ?
            """, (json.dumps(content), get_timestamp(), agent_name, memory_type))
            
            compacted_types.append({
                'type': memory_type,
                'before_kb': round(size_before, 1),
                'after_kb': round(size_after, 1),
                'saved_kb': round(size_before - size_after, 1)
            })
    
    conn.commit()
    
    # TODO: Update health record when agent_health table is refactored to use agent_name
    # if compacted_types:
    #     conn.execute("""
    #         UPDATE agent_health 
    #         SET needs_compaction = 0, 
    #             memory_size_kb = ?,
    #             memory_size_warning = CASE 
    #                 WHEN ? > 2000 THEN 'critical'
    #                 WHEN ? > 1000 THEN 'large'
    #                 ELSE NULL
    #             END
    #         WHERE agent_name = ?
    #     """, (total_after, total_after, total_after, agent_name))
    #     conn.commit()
    
    conn.close()
    
    return {
        'agent': agent_name,
        'total_before_kb': round(total_before, 1),
        'total_after_kb': round(total_after, 1),
        'total_saved_kb': round(total_before - total_after, 1),
        'reduction_percent': round((total_before - total_after) / total_before * 100, 1) if total_before > 0 else 0,
        'compacted_memories': compacted_types,
        'timestamp': get_timestamp()
    }

def auto_compact_if_needed(agent_name):
    """Check if agent needs compaction and do it automatically"""
    # TODO: Re-enable when agent_health table is refactored to use agent_name
    # conn = sqlite3.connect(DB_PATH)
    # conn.row_factory = sqlite3.Row
    # 
    # # Check agent health
    # cursor = conn.execute("""
    #     SELECT h.needs_compaction, h.memory_size_kb
    #     FROM agent_health h
    #     JOIN agents_catalog ac ON h.agent_name = ac.name
    #     WHERE ac.name = ?
    #     ORDER BY h.checked_at DESC
    #     LIMIT 1
    # """, (agent_name,))
    # 
    # health = cursor.fetchone()
    # conn.close()
    # 
    # if health and (health['needs_compaction'] or health['memory_size_kb'] > 1000):
    #     return compact_agents_memory(agent_name)
    
    return {'message': f"Agent health checks temporarily disabled during refactoring"}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python compact_memory.py [agent-name]")
        print("   or: python compact_memory.py --auto [agent-name]")
        sys.exit(1)
    
    if sys.argv[1] == '--auto' and len(sys.argv) > 2:
        # Auto mode - only compact if needed
        result = auto_compact_if_needed(sys.argv[2])
    else:
        # Force compact
        result = compact_agents_memory(sys.argv[1])
    
    print(json.dumps(result, indent=2))