#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
ID Generator for Sessions and Jobs

Generates unique hexadecimal IDs with prefixes:
- session_a1b2c3d4e5f6 (12 hex chars)
- job_a1b2c3d4e5f6 (12 hex chars)

Usage:
    python generate_id.py session
    python generate_id.py job
    python generate_id.py --type session
    python generate_id.py --type job
"""

import secrets
import sys
import argparse


def generate_session_id():
    """Generate session ID with format: session_a1b2c3d4e5f6"""
    return f"session_{secrets.token_hex(6)}"


def generate_job_id():
    """Generate job ID with format: job_a1b2c3d4e5f6"""
    return f"job_{secrets.token_hex(6)}"


def main():
    parser = argparse.ArgumentParser(description='Generate unique hexadecimal IDs')
    parser.add_argument('type', nargs='?', choices=['session', 'job'], 
                       help='Type of ID to generate (session or job)')
    parser.add_argument('--type', dest='type_flag', choices=['session', 'job'],
                       help='Type of ID to generate (alternative syntax)')
    
    args = parser.parse_args()
    
    # Determine ID type from positional or flag argument
    id_type = args.type or args.type_flag
    
    if not id_type:
        print("Error: Must specify ID type (session or job)", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    if id_type == 'session':
        print(generate_session_id())
    elif id_type == 'job':
        print(generate_job_id())


if __name__ == '__main__':
    main()