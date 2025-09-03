#!/usr/bin/env python3
"""
Agent Health Check System for Acolytes for Claude Code
Implements the health checking system as defined in .claude/commands/agent-health.md
"""

import os
import json
import glob
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class AgentHealthChecker:
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.agents_dir = self.project_root / ".claude" / "agents"
        self.memory_dir = self.project_root / ".claude" / "memory"
        self.agents_memory_dir = self.memory_dir / "agents"
        
        # Ensure memory directories exist
        self.agents_memory_dir.mkdir(parents=True, exist_ok=True)
        (self.agents_memory_dir / "health").mkdir(exist_ok=True)
        (self.agents_memory_dir / "metrics").mkdir(exist_ok=True)
        
    def find_all_acolytes(self) -> List[str]:
        """Find all acolyte files."""
        agent_files = glob.glob(str(self.agents_dir / "*.md"))
        agents = []
        
        for agent_file in agent_files:
            agent_name = Path(agent_file).stem
            # Skip README and other non-agent files
            if agent_name.lower() != "readme":
                agents.append(agent_name)
        
        return sorted(agents)
    
    def get_agent_metadata(self, agent_name: str, key: str) -> Optional[Any]:
        """Get metadata for an agent from memory."""
        metadata_file = self.agents_memory_dir / "health" / f"{agent_name}_metadata.json"
        
        if not metadata_file.exists():
            return None
            
        try:
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                return metadata.get(key)
        except Exception:
            return None
    
    def set_agent_metadata(self, agent_name: str, key: str, value: Any):
        """Set metadata for an agent in memory."""
        metadata_file = self.agents_memory_dir / "health" / f"{agent_name}_metadata.json"
        
        metadata = {}
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
            except Exception:
                metadata = {}
        
        metadata[key] = value
        metadata['last_updated'] = datetime.datetime.now().isoformat()
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_agent_age_days(self, agent_name: str) -> float:
        """Get the age of an agent in days."""
        created_date = self.get_agent_metadata(agent_name, "created_date")
        
        if not created_date:
            # Try to get file modification time
            agent_file = self.agents_dir / f"{agent_name}.md"
            if agent_file.exists():
                mtime = datetime.datetime.fromtimestamp(agent_file.stat().st_mtime)
                self.set_agent_metadata(agent_name, "created_date", mtime.isoformat())
                created_date = mtime.isoformat()
            else:
                return 0.0
        
        if isinstance(created_date, str):
            created_date = datetime.datetime.fromisoformat(created_date.replace('Z', '+00:00'))
        
        return (datetime.datetime.now() - created_date).days
    
    def count_project_files(self) -> int:
        """Count total files in the project (excluding .git)."""
        count = 0
        for root, dirs, files in os.walk(self.project_root):
            # Skip .git and other hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.git')]
            count += len(files)
        return count
    
    def analyze_agent_file(self, agent_name: str) -> Dict[str, Any]:
        """Analyze an agent file for completeness and quality."""
        agent_file = self.agents_dir / f"{agent_name}.md"
        
        if not agent_file.exists():
            return {
                "exists": False,
                "lines": 0,
                "has_yaml_header": False,
                "has_content": False,
                "quality_indicators": []
            }
        
        content = agent_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Basic analysis
        analysis = {
            "exists": True,
            "lines": len(lines),
            "has_yaml_header": content.startswith('---'),
            "has_content": len(content.strip()) > 100,
            "quality_indicators": []
        }
        
        # Quality indicators
        if '[TODO]' in content:
            analysis["quality_indicators"].append("has_todos")
        if 'Expert' in content or 'specialist' in content.lower():
            analysis["quality_indicators"].append("has_expertise")
        if '```' in content:
            analysis["quality_indicators"].append("has_code_examples")
        if len(lines) > 500:
            analysis["quality_indicators"].append("comprehensive")
        elif len(lines) > 100:
            analysis["quality_indicators"].append("substantial")
        else:
            analysis["quality_indicators"].append("minimal")
            
        return analysis
    
    def quick_health_check(self, agent_name: str) -> Dict[str, Any]:
        """Perform quick health check on an agent."""
        # Get current project state
        current_file_count = self.count_project_files()
        last_known_count = self.get_agent_metadata(agent_name, "file_count") or current_file_count
        
        # Analyze agent file
        agent_analysis = self.analyze_agent_file(agent_name)
        
        # Calculate drift based on file count changes
        file_drift = abs(current_file_count - last_known_count) * 3
        
        # Time-based drift
        days_old = self.get_agent_age_days(agent_name)
        time_drift = days_old * 0.5
        
        # Quality-based drift
        quality_drift = 0
        if 'has_todos' in agent_analysis["quality_indicators"]:
            quality_drift += 30
        if 'minimal' in agent_analysis["quality_indicators"]:
            quality_drift += 20
        if not agent_analysis["has_content"]:
            quality_drift += 40
        
        total_drift = file_drift + time_drift + quality_drift
        
        # Determine health status
        if total_drift < 20:
            health = "healthy"
        elif total_drift < 50:
            health = "degraded"
        else:
            health = "critical"
        
        # Update metadata
        self.set_agent_metadata(agent_name, "file_count", current_file_count)
        self.set_agent_metadata(agent_name, "last_health_check", datetime.datetime.now().isoformat())
        
        return {
            "agent": agent_name,
            "health": health,
            "drift_score": round(total_drift, 1),
            "quick_check": True,
            "recommendation": self.get_recommendation(total_drift),
            "analysis": agent_analysis,
            "days_old": round(days_old, 1),
            "file_count_delta": current_file_count - last_known_count
        }
    
    def get_recommendation(self, drift_score: float) -> str:
        """Get recommendation based on drift score."""
        if drift_score < 20:
            return "Agent is healthy - no action needed"
        elif drift_score < 35:
            return "Monitor closely - consider light refresh"
        elif drift_score < 50:
            return "Schedule upgrade within 1 week"
        elif drift_score < 70:
            return "Upgrade recommended within 2-3 days"
        else:
            return "URGENT: Immediate upgrade required"
    
    def check_all_agents(self) -> Dict[str, Any]:
        """Perform health check on all acolytes."""
        agents = self.find_all_acolytes()
        results = []
        
        print(f"Found {len(agents)} acolytes to check...")
        
        for agent in agents:
            print(f"Checking {agent}...")
            health = self.quick_health_check(agent)
            results.append(health)
        
        # Calculate summary statistics
        total_agents = len(results)
        healthy_count = len([r for r in results if r["health"] == "healthy"])
        degraded_count = len([r for r in results if r["health"] == "degraded"])
        critical_count = len([r for r in results if r["health"] == "critical"])
        
        average_drift = sum(r["drift_score"] for r in results) / total_agents if total_agents > 0 else 0
        average_age = sum(r["days_old"] for r in results) / total_agents if total_agents > 0 else 0
        
        upgrade_needed = [r for r in results if r["drift_score"] > 40]
        
        dashboard = {
            "total_agents": total_agents,
            "healthy": healthy_count,
            "degraded": degraded_count,
            "critical": critical_count,
            "average_drift": round(average_drift, 1),
            "average_age": round(average_age, 1),
            "upgrade_needed": upgrade_needed,
            "results": results
        }
        
        # Save results to memory
        results_file = self.agents_memory_dir / "health" / "current_scores.json"
        with open(results_file, 'w') as f:
            json.dump(dashboard, f, indent=2, default=str)
        
        return dashboard
    
    def print_dashboard(self, dashboard: Dict[str, Any]):
        """Print the health dashboard."""
        total = dashboard["total_agents"]
        healthy = dashboard["healthy"]
        degraded = dashboard["degraded"]
        critical = dashboard["critical"]
        
        healthy_pct = (healthy / total * 100) if total > 0 else 0
        degraded_pct = (degraded / total * 100) if total > 0 else 0
        critical_pct = (critical / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 60)
        print("               AGENT HEALTH DASHBOARD")
        print("=" * 60)
        print(f" Total Agents: {total}")
        print()
        print(f" [OK] Healthy: {healthy} ({healthy_pct:.0f}%)")
        print(f" [WARN] Degraded: {degraded} ({degraded_pct:.0f}%)")
        print(f" [CRIT] Critical: {critical} ({critical_pct:.0f}%)")
        print()
        print(f" Average Drift: {dashboard['average_drift']}/100")
        print(f" Average Age: {dashboard['average_age']} days")
        print("=" * 60)
        
        if dashboard["upgrade_needed"]:
            print(" AGENTS NEEDING UPGRADE:")
            for agent in dashboard["upgrade_needed"]:
                status_icon = "[CRIT]" if agent["health"] == "critical" else "[WARN]"
                print(f" {status_icon} {agent['agent']} (drift: {agent['drift_score']})")
            print("=" * 60)
            print(" Recommended Action:")
            print(" Run: /agent-health --all --upgrade")
        else:
            print(" All agents are in good health!")
        
        print("=" * 60)
    
    def print_detailed_results(self, results: List[Dict[str, Any]]):
        """Print detailed results for each agent."""
        print("\n" + "=" * 80)
        print("                    DETAILED AGENT HEALTH REPORT")
        print("=" * 80)
        
        for result in sorted(results, key=lambda x: x["drift_score"], reverse=True):
            status_icon = {
                "healthy": "[OK]",
                "degraded": "[WARN]",
                "critical": "[CRIT]"
            }.get(result["health"], "[?]")
            
            print(f"\n{status_icon} {result['agent']}")
            print(f"   Status: {result['health'].upper()}")
            print(f"   Drift Score: {result['drift_score']}/100")
            print(f"   Age: {result['days_old']} days")
            print(f"   Lines: {result['analysis']['lines']}")
            print(f"   Quality: {', '.join(result['analysis']['quality_indicators'])}")
            print(f"   Recommendation: {result['recommendation']}")
            
            if result["analysis"]["quality_indicators"]:
                quality_notes = []
                if 'has_todos' in result["analysis"]["quality_indicators"]:
                    quality_notes.append("[X] Contains TODO items")
                if 'minimal' in result["analysis"]["quality_indicators"]:
                    quality_notes.append("[!] Minimal content")
                if 'comprehensive' in result["analysis"]["quality_indicators"]:
                    quality_notes.append("[+] Comprehensive documentation")
                if 'has_code_examples' in result["analysis"]["quality_indicators"]:
                    quality_notes.append("[+] Contains code examples")
                
                if quality_notes:
                    print(f"   Notes: {'; '.join(quality_notes)}")

def main():
    """Main execution function."""
    project_root = os.getcwd()
    checker = AgentHealthChecker(project_root)
    
    print("Acolytes Health Check System")
    print("=" * 50)
    
    # Run health check on all agents
    dashboard = checker.check_all_agents()
    
    # Print dashboard
    checker.print_dashboard(dashboard)
    
    # Print detailed results
    checker.print_detailed_results(dashboard["results"])
    
    print(f"\n[INFO] Health data saved to: {checker.agents_memory_dir / 'health' / 'current_scores.json'}")
    print("[DONE] Health check complete!")

if __name__ == "__main__":
    main()