#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import argparse
import json
import sys
import sqlite3
import tempfile
import os
import subprocess
import platform
from pathlib import Path
from datetime import datetime

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


def ensure_session_log_dir(project_root=None):
    """Ensure acolytes directory exists and return path."""
    if project_root:
        base_dir = Path(project_root)
    else:
        # Always use project root, not current directory
        current_dir = Path.cwd()
        if current_dir.name == 'hooks':
            base_dir = current_dir.parent.parent  # Go up from .claude/hooks to project root
        else:
            base_dir = current_dir
    acolytes_dir = base_dir / '.claude' / 'memory' / 'acolytes'
    acolytes_dir.mkdir(parents=True, exist_ok=True)
    return acolytes_dir


def get_our_session_id(project_cwd):
    """Get our session ID from SQLite database."""
    if project_cwd:
        db_path = Path(project_cwd) / '.claude' / 'memory' / 'project.db'
    else:
        db_path = Path.cwd() / '.claude' / 'memory' / 'project.db'
    
    our_session_id = "unknown"
    
    if db_path.exists():
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            # Get current active session
            cursor.execute("SELECT id FROM sessions WHERE ended_at IS NULL ORDER BY created_at DESC LIMIT 1")
            result = cursor.fetchone()
            if result:
                our_session_id = result[0]
            conn.close()
        except (sqlite3.Error, OSError, IOError):
            pass
    
    return our_session_id


def log_subagent_completion(input_data, session_id):
    """Log subagent completion details to acolytes directory."""
    try:
        project_cwd = input_data.get("cwd", "")
        our_session_id = get_our_session_id(project_cwd)
        
        # Get acolytes directory
        log_dir = ensure_session_log_dir(project_cwd if project_cwd else None)
        
        # Store only non-sensitive fields for debugging
        raw_input = {k: input_data[k] for k in ("cwd", "session_id", "transcript_path") if k in input_data}
        
        # Extract subagent info from transcript (Claude Code sends transcript_path)
        transcript_path = input_data.get("transcript_path", "")
        subagent_name = "unknown"
        task_description = ""
        completion_status = "completed"
        output_summary = ""
        
        if transcript_path and Path(transcript_path).exists():
            try:
                # Read the last few lines of transcript to get subagent info
                with open(transcript_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    
                # Look for the most recent Task tool call - search entire transcript
                task_tool_id = None
                for line in reversed(lines):  # Check ALL lines from end
                    try:
                        line_content = line.strip()
                        if not line_content:
                            continue
                            
                        # Look for Task tool call patterns
                        if '"name":"Task"' in line_content and '"subagent_type"' in line_content:
                            entry = json.loads(line_content)
                            
                            # Extract from message.content array
                            if entry.get("message", {}).get("content"):
                                for item in entry["message"]["content"]:
                                    if item.get("type") == "tool_use" and item.get("name") == "Task":
                                        params = item.get("input", {})
                                        if "subagent_type" in params:
                                            subagent_name = params["subagent_type"]
                                            task_description = params.get("description", "")
                                            task_tool_id = item.get("id")  # Capture tool ID
                                            break
                                if subagent_name != "unknown":
                                    break
                                    
                    except (json.JSONDecodeError, KeyError):
                        continue
                        
                # Also look for tool result that matches our specific Task call
                if subagent_name != "unknown" and task_tool_id:
                    # Find the toolUseResult that matches our specific tool ID  
                    for line in reversed(lines[-200:]):  # Look in even more lines 
                        try:
                            line_content = line.strip()
                            # Look for lines that contain our tool ID and tool_result
                            if task_tool_id in line_content and '"tool_use_id"' in line_content and '"tool_result"' in line_content:
                                entry = json.loads(line_content)
                                
                                # Multiple ways to find the result
                                # Method 1: Check message.content array
                                if entry.get("message", {}).get("content"):
                                    for content_item in entry["message"]["content"]:
                                        if (content_item.get("tool_use_id") == task_tool_id and 
                                            content_item.get("type") == "tool_result"):
                                            tool_result_content = content_item.get("content", [])
                                            if tool_result_content and len(tool_result_content) > 0:
                                                text_content = tool_result_content[0].get("text", "")
                                                if text_content and len(text_content) > 5:
                                                    output_summary = text_content[:1000] + "..." if len(text_content) > 1000 else text_content
                                                    break
                                
                                # Method 2: Check direct toolUseResult
                                if not output_summary and entry.get("toolUseResult", {}).get("content"):
                                    content_list = entry["toolUseResult"]["content"]
                                    if content_list and len(content_list) > 0:
                                        text_content = content_list[0].get("text", "")
                                        if text_content and len(text_content) > 5:
                                            output_summary = text_content[:1000] + "..." if len(text_content) > 1000 else text_content
                                
                                if output_summary:
                                    break
                                    
                        except (json.JSONDecodeError, KeyError):
                            continue
                        
            except (OSError, IOError):
                pass
        
        # Create subagent completion entry
        subagent_entry = {
            "session_id": our_session_id,
            "claude_session_id": session_id,
            "timestamp": datetime.now().isoformat(),  # Local time without timezone suffix
            "subagent_name": subagent_name,
            "task_description": task_description,
            "completion_status": completion_status,
            "output_summary": output_summary,
            "event_type": "subagent_stop",
            "raw_claude_input": raw_input  # Store only whitelisted fields
        }
        
        # Save to acolytes log file
        log_file = log_dir / f"{our_session_id}_acolytes.json"
        
        # Read existing log or create new list
        acolytes_log = []
        if log_file.exists():
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    acolytes_log = json.load(f)
            except (json.JSONDecodeError, OSError, IOError):
                acolytes_log = []
        
        # Add subagent entry
        acolytes_log.append(subagent_entry)
        
        # Write back atomically to prevent corruption
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(log_dir)) as tf:
            json.dump(acolytes_log, tf, indent=2, ensure_ascii=False)
            tmp_name = tf.name
        
        # Atomic replace - either succeeds completely or fails completely
        os.replace(tmp_name, str(log_file))
            
        print(f"Subagent logged: {subagent_name} - {completion_status}")
            
    except Exception as e:
        print(f"Subagent logging error: {e}", file=sys.stderr)


def play_stop_sound():
    """Play work complete sound at 20% volume when subagent stops"""
    try:
        # Path to work complete sound
        sound_file = Path('~/.claude/resources/sfx/work-complete.wav')
        sound_file = sound_file.expanduser()
        
        if sound_file.exists():
            system = platform.system()
            
            if system == 'Windows':
                # Play the custom sound file at 20% volume using PowerShell
                ps_script = f'''
                Add-Type -AssemblyName PresentationCore
                $mediaPlayer = New-Object System.Windows.Media.MediaPlayer
                $mediaPlayer.Open([System.Uri]::new("{sound_file.resolve()}"))
                $mediaPlayer.Volume = 0.2
                Start-Sleep -Milliseconds 100
                $mediaPlayer.Play()
                Start-Sleep -Seconds 2
                $mediaPlayer.Stop()
                $mediaPlayer.Close()
                '''
                subprocess.run(
                    ['powershell', '-NoProfile', '-Command', ps_script],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW if system == 'Windows' else 0
                )
            elif system == 'Darwin':
                # Use afplay with reduced volume (0.2 = 20%)
                subprocess.run(
                    ['afplay', '-v', '0.2', str(sound_file.resolve())],
                    capture_output=True
                )
            else:
                # Try paplay (PulseAudio) first, then aplay (ALSA)
                try:
                    # PulseAudio with 20% volume (32768 * 0.2 = 6554)
                    subprocess.run(
                        ['paplay', '--volume=6554', str(sound_file.resolve())],
                        capture_output=True,
                        check=True
                    )
                except (subprocess.CalledProcessError, FileNotFoundError):
                    try:
                        # Fallback to ALSA aplay
                        subprocess.run(
                            ['aplay', str(sound_file.resolve())],
                            capture_output=True
                        )
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        pass  # No audio player available
    except Exception:
        # Silently fail if sound cannot play
        pass


def main():
    try:
        # Parse command line arguments
        parser = argparse.ArgumentParser()
        parser.add_argument(
            "--chat", action="store_true", help="Copy to acolytes log"
        )
        parser.add_argument(
            "--sound", action="store_true", help="Play sound when stopping"
        )
        args = parser.parse_args()

        # Read JSON input from stdin
        stdin_content = sys.stdin.read().strip()
        
        if not stdin_content:
            print("No input data provided", file=sys.stderr)
            sys.exit(0)
            
        input_data = json.loads(stdin_content)

        # Extract required fields
        claude_session_id = input_data.get("session_id", "")
        
        # Always log if --chat flag is provided (our default behavior)
        if args.chat:
            log_subagent_completion(input_data, claude_session_id)
        
        # Success
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Handle JSON decode errors gracefully
        print("Invalid JSON input", file=sys.stderr)
        sys.exit(0)
    except Exception as e:
        # Handle any other errors gracefully
        print(f"Subagent stop hook error: {e}", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()