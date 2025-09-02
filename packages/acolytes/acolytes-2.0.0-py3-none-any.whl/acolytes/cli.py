#!/usr/bin/env python
"""
Main CLI interface for acolytes
"""

import click
import sys
from pathlib import Path
from colorama import init, Fore, Style

# Initialize colorama for cross-platform colors
init()

from .commands import (
    init_command,
    update_command, 
    doctor_command,
    repair_command,
    list_command,
    backup_command,
    clean_command
)

@click.command()
@click.option('--init', 'cmd_init', is_flag=True, help='Initialize Acolytes system')
@click.option('--update', 'cmd_update', is_flag=True, help='Update to latest version')
@click.option('--doctor', 'cmd_doctor', is_flag=True, help='Diagnose system issues')
@click.option('--repair', 'cmd_repair', is_flag=True, help='Repair configuration')
@click.option('--list', 'cmd_list', is_flag=True, help='List available agents')
@click.option('--backup', 'cmd_backup', is_flag=True, help='Backup current installation')
@click.option('--clean', 'cmd_clean', is_flag=True, help='Clean orphaned files')
@click.option('--version', 'cmd_version', is_flag=True, help='Show version')
def main(cmd_init, cmd_update, cmd_doctor, cmd_repair, cmd_list, cmd_backup, cmd_clean, cmd_version):
    """
    Acolytes for Claude Code - Multi-agent system manager
    """
    
    # Header
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"  Acolytes for Claude Code")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    # Execute command
    if cmd_init:
        init_command.run()
    elif cmd_update:
        update_command.run()
    elif cmd_doctor:
        doctor_command.run()
    elif cmd_repair:
        repair_command.run()
    elif cmd_list:
        list_command.run()
    elif cmd_backup:
        backup_command.run()
    elif cmd_clean:
        clean_command.run()
    elif cmd_version:
        from . import __version__
        print(f"Version: {__version__}")
    else:
        # Show help if no command
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
    
    print()

if __name__ == "__main__":
    main()