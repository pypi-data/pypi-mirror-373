#!/usr/bin/env python
"""
List command for acolytes CLI - Lists all global agents from ~/.claude/agents/
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import yaml
from colorama import Fore, Style, init

# Initialize colorama for Windows compatibility
init(autoreset=True)

@dataclass
class AgentInfo:
    """Information about an agent."""
    name: str
    description: str
    category: str
    is_acolyte: bool = False
    tools: List[str] = None
    model: str = None
    color: str = None

def get_agents_directory() -> Path:
    """Get the agents directory path."""
    # Try different possible locations
    possible_paths = [
        Path.home() / ".claude" / "agents",
        Path.cwd() / ".claude" / "agents",
        Path(__file__).parent.parent.parent.parent / ".claude" / "agents"
    ]
    
    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path
    
    # Fallback to user's home directory
    return Path.home() / ".claude" / "agents"

def parse_agent_file(file_path: Path) -> Optional[AgentInfo]:
    """Parse an agent markdown file to extract metadata."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract YAML frontmatter
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1].strip()
                try:
                    metadata = yaml.safe_load(yaml_content)
                except yaml.YAMLError:
                    metadata = {}
            else:
                metadata = {}
        else:
            metadata = {}
        
        # Extract basic info
        name = metadata.get('name', file_path.stem)
        
        # Skip internal agents (setup.*, plan.*)
        internal_prefixes = ('setup.', 'plan.')
        if name.startswith(internal_prefixes):
            return None
        
        description = metadata.get('description', 'No description available')
        tools = metadata.get('tools', [])
        model = metadata.get('model', 'Unknown')
        color = metadata.get('color', 'default')
        
        # Determine category from name
        category = determine_category(name)
        
        # Check if it's a project-specific acolyte
        is_acolyte = name.startswith('acolyte.')
        
        return AgentInfo(
            name=name,
            description=description,
            category=category,
            is_acolyte=is_acolyte,
            tools=tools if isinstance(tools, list) else [],
            model=model,
            color=color
        )
    
    except Exception as e:
        print(f"{Fore.YELLOW}Warning: Could not parse {file_path.name}: {e}{Style.RESET_ALL}")
        return None

def determine_category(name: str) -> str:
    """Determine agent category based on name prefix."""
    if name.startswith('backend.'):
        return 'Backend'
    elif name.startswith('frontend.'):
        return 'Frontend'
    elif name.startswith('database.'):
        return 'Database'
    elif name.startswith('service.'):
        return 'Service'
    elif name.startswith('coordinator.'):
        return 'Coordinator'
    elif name.startswith('ops.'):
        return 'Operations'
    elif name.startswith('audit.'):
        return 'Audit'
    elif name.startswith('analyst.'):
        return 'Analyst'
    elif name.startswith('business.'):
        return 'Business'
    elif name.startswith('test.'):
        return 'Testing'
    elif name.startswith('setup.'):
        return 'Setup'
    elif name.startswith('plan.'):
        return 'Planning'
    elif name.startswith('docs.'):
        return 'Documentation'
    elif name.startswith('acolyte.'):
        return 'Project Acolytes'
    else:
        return 'Other'

def get_category_color(category: str) -> str:
    """Get color for category display."""
    category_colors = {
        'Backend': Fore.BLUE,
        'Frontend': Fore.CYAN,
        'Database': Fore.GREEN,
        'Service': Fore.MAGENTA,
        'Coordinator': Fore.YELLOW,
        'Operations': Fore.RED,
        'Audit': Fore.LIGHTRED_EX,
        'Analyst': Fore.LIGHTBLUE_EX,
        'Business': Fore.LIGHTGREEN_EX,
        'Testing': Fore.LIGHTMAGENTA_EX,
        'Setup': Fore.LIGHTYELLOW_EX,
        'Planning': Fore.LIGHTCYAN_EX,
        'Documentation': Fore.WHITE,
        'System': Fore.LIGHTWHITE_EX,
        'Project Acolytes': Fore.LIGHTRED_EX,
        'Other': Fore.RESET
    }
    return category_colors.get(category, Fore.RESET)

def safe_print(text: str) -> None:
    """Print text safely, handling Windows console encoding issues."""
    try:
        print(text)
    except (UnicodeEncodeError, OSError):
        # Strip color codes if there are encoding issues
        import re
        clean_text = re.sub(r'\x1b\[[0-9;]*m', '', text)
        print(clean_text)

def display_agent_list(agents_by_category: Dict[str, List[AgentInfo]]) -> None:
    """Display the formatted list of agents."""
    total_agents = sum(len(agents) for agents in agents_by_category.values())
    total_acolytes = sum(
        len([agent for agent in agents if agent.is_acolyte]) 
        for agents in agents_by_category.values()
    )
    
    safe_print(f"\n{Fore.CYAN}{'='*80}")
    safe_print(f"  ACOLYTES AGENT CATALOG")
    safe_print(f"{'='*80}{Style.RESET_ALL}")
    
    safe_print(f"\n{Fore.WHITE}[STATS] Summary:")
    safe_print(f"   Total Agents: {Fore.LIGHTGREEN_EX}{total_agents}{Style.RESET_ALL}")
    safe_print(f"   Global Agents: {Fore.LIGHTBLUE_EX}{total_agents - total_acolytes}{Style.RESET_ALL}")
    safe_print(f"   Project Acolytes: {Fore.LIGHTRED_EX}{total_acolytes}{Style.RESET_ALL}")
    safe_print(f"   Categories: {Fore.LIGHTYELLOW_EX}{len(agents_by_category)}{Style.RESET_ALL}")
    
    # Sort categories by importance
    category_order = [
        'Backend', 'Frontend', 'Database', 'Service', 'Coordinator',
        'Operations', 'Business', 'Testing', 'Audit', 'Analyst',
        'Setup', 'Planning', 'Documentation', 'System', 
        'Project Acolytes', 'Other'
    ]
    
    for category in category_order:
        if category not in agents_by_category:
            continue
            
        agents = agents_by_category[category]
        if not agents:
            continue
            
        category_color = get_category_color(category)
        safe_print(f"\n{category_color}{'-'*80}")
        safe_print(f"  {category.upper()} ({len(agents)} agents)")
        safe_print(f"{'-'*80}{Style.RESET_ALL}")
        
        # Sort agents by name
        agents.sort(key=lambda x: x.name)
        
        for agent in agents:
            # Agent name with special marking for acolytes
            agent_prefix = "[A] " if agent.is_acolyte else "[G] "
            agent_name = f"{Fore.WHITE}{agent_prefix}{agent.name}{Style.RESET_ALL}"
            
            # Description (truncated if too long)
            desc = agent.description
            if len(desc) > 100:
                desc = desc[:97] + "..."
            
            # Model and tools info
            model_info = f"({agent.model})" if agent.model else ""
            tools_count = f"[{len(agent.tools)} tools]" if agent.tools else "[0 tools]"
            
            safe_print(f"    {agent_name}")
            safe_print(f"      DESC: {Fore.LIGHTWHITE_EX}{desc}{Style.RESET_ALL}")
            safe_print(f"      INFO: {Fore.LIGHTBLACK_EX}{model_info} {tools_count}{Style.RESET_ALL}")
            safe_print("")

def run() -> None:
    """Main function to list all agents."""
    try:
        # Ensure stdout can handle unicode on Windows
        if sys.platform == 'win32':
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, errors='replace')
        
        agents_dir = get_agents_directory()
        
        if not agents_dir.exists():
            print(f"{Fore.RED}Error: Agents directory not found at {agents_dir}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Expected location: ~/.claude/agents/{Style.RESET_ALL}")
            sys.exit(1)
        
        # Collect all agent files
        agent_files = list(agents_dir.glob("*.md"))
        
        if not agent_files:
            print(f"{Fore.YELLOW}No agent files found in {agents_dir}{Style.RESET_ALL}")
            sys.exit(1)
        
        # Parse all agents
        agents_by_category: Dict[str, List[AgentInfo]] = {}
        
        for agent_file in agent_files:
            agent_info = parse_agent_file(agent_file)
            if agent_info:
                category = agent_info.category
                if category not in agents_by_category:
                    agents_by_category[category] = []
                agents_by_category[category].append(agent_info)
        
        # Display the results
        display_agent_list(agents_by_category)
        
        # Additional info
        safe_print(f"\n{Fore.CYAN}{'-'*80}")
        safe_print(f"  LEGEND")
        safe_print(f"{'-'*80}{Style.RESET_ALL}")
        safe_print(f"  [G]  Global Agent - System-wide specialized agent")
        safe_print(f"  [A]  Project Acolyte - Project-specific module agent")
        safe_print(f"\n{Fore.LIGHTBLACK_EX}Location: {agents_dir}{Style.RESET_ALL}")
        
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Operation cancelled by user{Style.RESET_ALL}")
        sys.exit(1)
    except Exception as e:
        try:
            print(f"{Fore.RED}Error: {e}{Style.RESET_ALL}")
        except:
            print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run()