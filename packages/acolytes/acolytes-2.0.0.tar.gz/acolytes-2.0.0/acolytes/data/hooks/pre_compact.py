#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "python-dotenv",
# ]
# ///

import json
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv is optional


# Save session functionality removed - sessions are saved manually via /save command


def main():
    try:
        # Read JSON input from stdin  
        stdin_input = sys.stdin.read().strip()
        
        if stdin_input:
            input_data = json.loads(stdin_input)
            trigger = input_data.get('trigger', 'unknown')
            custom_instructions = input_data.get('custom_instructions', '')
        else:
            # No input provided, assume manual
            trigger = 'manual'
            custom_instructions = ''
        
        # Provide feedback based on trigger type
        if trigger == "manual":
            message = "MANUAL COMPACTION DETECTED - User executed /compact command"
            if custom_instructions:
                message += f"\nCustom instructions: {custom_instructions[:100]}..."
            print(message)
            print("REMINDER: Claude must execute '/save' command before compaction proceeds!")
            print("Compaction will proceed after session save.")
        else:  # auto
            message = "AUTO COMPACTION DETECTED - Context window full, automatic compaction triggered"
            print(message)
            print("Compaction ready to proceed.")
        
        # Success - compaction will proceed
        sys.exit(0)
        
    except json.JSONDecodeError:
        # Fallback to manual if JSON parse fails
        print("MANUAL COMPACTION DETECTED - User executed /compact command")
        print("REMINDER: Claude must execute '/save' command before compaction proceeds!")
        print("Compaction will proceed after session save.")
        sys.exit(0)
    except Exception:
        # Handle any other errors gracefully
        print("MANUAL COMPACTION DETECTED - User executed /compact command")
        print("REMINDER: Claude must execute '/save' command before compaction proceeds!")
        print("Compaction will proceed after session save.")
        sys.exit(0)


if __name__ == '__main__':
    main()