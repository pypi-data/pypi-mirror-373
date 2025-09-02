# 🚀 Acolytes Quest System

## Overview

The Acolytes Quest System enables AI agents to communicate and collaborate through a persistent SQLite database using eternal monitoring loops. Agents stay "alive" by continuously checking for their turn, allowing real multi-agent conversations and task coordination.

## 📁 System Components

```
acolytes_quest/
├── acolyte_quest_core.py     # Core shared functions with logging
├── quest_create.py           # Create new quest (leader only)
├── quest_monitor.py          # Eternal monitoring loop
├── quest_message.py          # Send messages between agents
├── quest_conversation.py     # View conversation + accept task
├── quest_respond.py          # Worker responds to leader
├── quest_status.py           # Change quest status
├── quest_review.py           # Mark quest as under review
├── quest_complete.py         # Mark quest as completed
├── quest_monitor_simple.py   # Simple monitor without emojis
├── quest_monitor_debug.py    # Debug monitor with detailed logs
└── README.md                 # This file
```

## 🎯 Perfect Flow

### Leader Agent Flow (Acolyte)

```
1. CREATE QUEST
   python quest_create.py --mission "Build user dashboard" --agents "@leader,@worker1,@worker2" --phase "1/2"
   → Returns: quest_id=123
   → Leader has initial turn

2. SEND INITIAL INSTRUCTIONS
   python quest_message.py --quest 123 --to "@worker1" --msg "Implement backend API"
   → Turn passes to worker1, status becomes "waiting"

3. MONITOR FOR RESPONSES
   python quest_monitor.py --role leader --quest 123
   → Sleeps 30s checking for responses

4. WHEN WORKER RESPONDS
   → Monitor exits with worker's response
   python quest_conversation.py --quest 123 --accept
   → Read conversation and change status to "working"

5. REVIEW WORK
   python quest_review.py --quest 123
   → Status changes to "reviewing"
   → Leader reviews actual code files

6. DECIDE NEXT ACTION
   Option A: Request changes
   python quest_message.py --quest 123 --to "@worker1" --msg "Fix: Add error handling"

   Option B: Create next phase for worker2
   python quest_create.py --mission "Frontend implementation" --agents "@leader,@worker2" --phase "2/2"

   Option C: Complete quest
   python quest_complete.py --quest 123 --summary "Dashboard implemented successfully"
```

### Worker Agent Flow

```
1. MONITOR FOR TASKS
   python quest_monitor.py --role worker --agent "@worker1"
   → Scans ALL quests for their name
   → Exits when finds their name with status "waiting"

2. WHEN ASSIGNED TASK (monitor exits)
   python quest_conversation.py --quest 123 --accept
   → Reads full conversation
   → Changes status to "working" (accepting the task)

3. DO ACTUAL WORK
   → Create files, write code, test
   → Real implementation work
   → Use Edit, Write, Bash tools as needed

4. RESPOND TO LEADER
   python quest_respond.py --quest 123 --msg "Created dashboard API with 5 endpoints" --files "api/dashboard.js"
   → Turn passes back to leader
   → Status changes to "waiting"

5. BACK TO MONITORING
   python quest_monitor.py --role worker --agent "@worker1"
   → Returns to monitoring until all quests show "completed"
```

## 📝 Command Reference

### quest_create.py

**Purpose**: Create a new quest (leader only)

```bash
python quest_create.py --mission "Task description" --agents "@leader,@worker1,@worker2" [--phase "1/3"]

Options:
  --mission, -m   The task to be completed (required)
  --agents, -a    Comma-separated list of agents, leader first (required)
  --phase, -p     Quest phase like "1/6" (optional, default: "1/1")

Returns:
  quest_id that leader MUST store for monitoring
```

### quest_monitor.py

**Purpose**: Eternal loop checking for turn

```bash
# For leaders (monitoring specific quest)
python quest_monitor.py --role leader --quest 123 [--interval 30]

# For workers (scanning all quests)
python quest_monitor.py --role worker --agent "@backend.nodejs" [--interval 30]

Options:
  --role, -r      Agent role: "leader" or "worker" (required)
  --quest, -q     Quest ID (required for leaders)
  --agent, -a     Agent name (required for workers)
  --interval, -i  Sleep seconds between checks (default: 30)

Behavior:
  - Loops forever checking database
  - Exits when it's agent's turn
  - Leaders exit on response or completion
  - Workers exit when assigned task
```

### quest_conversation.py

**Purpose**: View full conversation history AND optionally accept task

```bash
python quest_conversation.py --quest 123 [--raw] [--accept]

Options:
  --quest, -q   Quest ID to view (required)
  --raw, -r     Show raw JSON data (optional)
  --accept, -a  Accept task by changing status to "working" (optional)

Shows:
  - Quest details (mission, phase, status)
  - ALL messages in chronological order
  - Final result if completed

Effect of --accept:
  - Changes status from "waiting" to "working"
  - Used when agent starts working on their assigned task
```

### quest_message.py

**Purpose**: Send message to another agent (usually leader to worker)

```bash
python quest_message.py --quest 123 --to "@backend.nodejs" --msg "Instructions..."

Options:
  --quest, -q  Quest ID (required)
  --to, -t     Target agent (required)
  --msg, -m    Message content (required)
  --from, -f   Sender (optional, auto-detected)

Effect:
  - Appends message to conversation
  - Passes turn to target agent
  - Sets status to "waiting"
```

### quest_respond.py

**Purpose**: Worker responds to leader

```bash
python quest_respond.py --quest 123 --msg "Work completed..." [--files "file1.js,file2.py"]

Options:
  --quest, -q   Quest ID (required)
  --msg, -m     Response message (required)
  --to, -t      Target (optional, defaults to leader)
  --files       Comma-separated files created/modified (optional)

Effect:
  - Appends response to conversation
  - Passes turn back to leader
  - Worker should return to monitoring
```

### quest_review.py

**Purpose**: Mark quest as under review (leader only)

```bash
python quest_review.py --quest 123 [--message "Starting review"]

Options:
  --quest, -q    Quest ID to review (required)
  --message, -m  Optional review comment

Effect:
  - Changes status to "reviewing"
  - Used by leaders when reviewing worker's completed work
  - Provides clear tracing of review phase

After review, leader can:
  - Request changes via quest_message.py
  - Complete quest via quest_complete.py
```

### quest_status.py

**Purpose**: Change quest status (usually not needed directly)

```bash
python quest_status.py --quest 123 --status reviewing

Options:
  --quest, -q   Quest ID (required)
  --status, -s  New status (required)

Valid statuses:
  - working    : Someone is actively working
  - waiting    : Waiting for response
  - reviewing  : Leader is reviewing work
  - completed  : Quest finished successfully
  - failed     : Quest failed
  - timeout    : Quest timed out
```

### quest_complete.py

**Purpose**: Mark quest as completed with result

```bash
python quest_complete.py --quest 123 --summary "Successfully implemented" [--result '{"files": 5}']

Options:
  --quest, -q    Quest ID (required)
  --summary, -s  Summary of accomplishment (optional)
  --result, -r   JSON result data (optional)

Effect:
  - Sets status to "completed"
  - Saves final result
  - All agents monitoring this quest will exit
```

## 🔄 Database Schema

The system uses table `acolyte_quests` in `.claude/memory/project.db`:

```sql
quest_id       INTEGER PRIMARY KEY
quest_name     TEXT        -- "quest-20241230-143000"
quest_phase    TEXT        -- "1/3" (current phase)
mission        TEXT        -- Task description
recruited      TEXT        -- JSON array of agents
current_agent  TEXT        -- Who has the turn
status         TEXT        -- working/waiting/reviewing/completed
broadcast      TEXT        -- JSON array of ALL messages
context        TEXT        -- JSON context data
result         TEXT        -- JSON final result
created_at     INTEGER     -- Unix timestamp
updated_at     INTEGER     -- Unix timestamp
```

## 💡 Key Concepts

### Turn-Based System

- Only ONE agent has the turn at any time (`current_agent`)
- Turn passes when sending message or responding
- Prevents chaos and race conditions

### Conversation History

- `broadcast` field stores ARRAY of all messages
- Each message has: from, to, message, timestamp
- Full conversation preserved for context

### Quest Lifecycle

1. **Created** → Leader creates with mission
2. **Working** → Worker doing task
3. **Waiting** → Waiting for response
4. **Reviewing** → Leader reviewing work
5. **Completed/Failed** → Final state

### Multiple Quests

- Workers can handle multiple quests simultaneously
- Each worker tracks their assigned quest_ids
- Monitor continues until ALL quests completed

## 🚨 Important Notes

1. **Always run from project root** or scripts won't find database
2. **Leaders must store quest_id** returned from create
3. **Workers scan ALL quests** to find assignments
4. **Broadcast is cumulative** - all messages preserved
5. **Monitor runs forever** - use Ctrl+C to stop manually

## 📋 Example: Complete Workflow

```bash
# 1. Leader creates quest
cd acolytes/data/scripts/acolyte_quests
python quest_create.py --mission "Create login system" --agents "@acolyte.auth,@backend.nodejs"
# Output: quest_id=42

# 2. Leader starts monitoring
python quest_monitor.py --role leader --quest 42

# 3. Worker (in another terminal) monitors for tasks
python quest_monitor.py --role worker --agent "@backend.nodejs"
# Detects quest 42, shows instructions, exits

# 4. Worker reads full context
python quest_conversation.py --quest 42

# 5. Worker does actual work (creates login.js, auth.js, etc.)

# 6. Worker responds
python quest_respond.py --quest 42 --msg "Created JWT login system" --files "auth/login.js,auth/jwt.js"

# 7. Leader's monitor exits showing response

# 8. Leader reviews and completes
python quest_complete.py --quest 42 --summary "Login system implemented"

# 9. Both monitors detect completion and shut down
```

## 🔧 Troubleshooting

### "Database not found"

- Run scripts from project root where `.claude/` exists
- Or set environment variable: `export ACOLYTES_ROOT=/path/to/project`

### "Quest not found"

- Check quest_id is correct
- Verify database has the quest: `sqlite3 .claude/memory/project.db "SELECT * FROM acolyte_quests"`

### Monitor never exits

- Check if it's actually your turn in database
- Verify agent name matches exactly (including @)
- Check quest status isn't already completed

### Messages not appearing

- Ensure using quest_message.py or quest_respond.py (not direct DB edits)
- Check broadcast field is JSON array format
- Verify message was successfully sent (check return message)

## 📚 Advanced Usage

### Parallel Worker Coordination

Leader can assign different parts to multiple workers:

```bash
# Create with multiple workers
python quest_create.py --mission "Build app" --agents "@leader,@backend,@frontend,@database"

# Assign to backend first (automatic)
# Then leader assigns to frontend
python quest_message.py --quest 123 --to "@frontend" --msg "Create UI"
# Then to database
python quest_message.py --quest 123 --to "@database" --msg "Design schema"
```

### Quest Phases

Track progress through multi-phase projects:

```bash
python quest_create.py --mission "Phase 1: Setup" --agents "@leader,@worker" --phase "1/5"
# After completion, create next phase
python quest_create.py --mission "Phase 2: Implementation" --agents "@leader,@worker" --phase "2/5"
```

### Raw Data Access

For debugging or advanced processing:

```bash
python quest_conversation.py --quest 123 --raw
# Returns full JSON structure with all fields
```

## 🎭 Agent Invocation Prompts

When invoking agents in parallel for the Acolyte Quest System, use these exact prompts:

### For @sandbox-orchestrator (Leader):

```
Build a task management API in /sandbox with database integration. Requirements:
- RESTful API with CRUD operations  
- SQLite database connection
- Proper error handling
- Input validation

You have two workers available:
- @test-worker-python: handles Python code
- @test-worker-database: handles database/SQL code

Create a miniroadmap.md with your execution plan, then coordinate the workers to build this.
```

### For @test-worker-python (Worker):

```
Monitor for tasks from @sandbox-orchestrator.
```

### For @test-worker-database (Worker):

```
Monitor for tasks from @sandbox-orchestrator.
```

**Note**: Workers only need to be told to monitor. Their system prompts contain all the quest system instructions. The leader needs specific information about what task to coordinate.

---

**Version**: 1.0.0  
**Last Updated**: 2024-12-30  
**Database**: SQLite with `.claude/memory/project.db`  
**Python**: 3.11+ required
