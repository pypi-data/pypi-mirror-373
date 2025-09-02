# QUEST Leader Template - Multi-Agent Coordination System

## MODE 2: QUEST (Leader Execution)

When Claude says "QUEST" or "Create quest" - Act as LEADER:

- "QUEST: Execute the plan with workers"
- "Create quest for implementing X"

**As LEADER, you must**:

1. **CREATE QUEST** (store the quest_id):

```bash
python acolytes/data/scripts/acolytes_quest/quest_create.py --mission "Your mission" --agents "@{{agent-name}},@worker1,@worker2"
# CRITICAL: Store returned quest_id for ALL subsequent commands
```

2. **SEND INSTRUCTIONS TO WORKERS** (MANDATORY):

```bash
python acolytes/data/scripts/acolytes_quest/quest_message.py --quest ID --to "@worker.name" --msg "Specific task instructions"
# WITHOUT THIS MESSAGE, WORKERS DON'T KNOW THEY HAVE WORK!
```

3. **MONITOR FOR RESPONSES**:

```bash
python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role leader --agent "@{{agent-name}}" --quest ID
# Exits when worker responds
```

4. **COMPLETE QUEST** when done:

```bash
python acolytes/data/scripts/acolytes_quest/quest_complete.py --quest ID --summary "What was accomplished"
```

**DETECTION KEYWORDS**:

- NORMAL: default (includes PRE-QUEST when specified)
- QUEST: "quest", "create quest", "delegate", "assign workers"

## QUEST Leadership Protocol

### Critical Leader Rules:

1. **ALWAYS MONITOR UNTIL COMPLETE**
   - Never disconnect after creating quest
   - Keep using monitor until all workers report done
   - Mark quest complete only after all tasks verified

2. **CLEAR WORKER INSTRUCTIONS**
   - Each worker needs specific, actionable tasks
   - Include file paths and technical details
   - Specify dependencies between workers

3. **PARALLEL VS SEQUENTIAL**
   - Determine if workers can work in parallel
   - Send sequential instructions when dependencies exist
   - Example: Database must complete before API worker starts

### Example QUEST Flow:

```bash
# 1. Create quest with all workers
python acolytes/data/scripts/acolytes_quest/quest_create.py \
  --mission "Implement chat system" \
  --agents "@acolyte.sandbox,@database.sqlite,@backend.python,@frontend.vue"

# Store: quest_id = "quest-20250901-123456"

# 2. Send specific instructions to each worker
python acolytes/data/scripts/acolytes_quest/quest_message.py \
  --quest "quest-20250901-123456" \
  --to "@database.sqlite" \
  --msg "Create agent_chat_messages table in sandbox/dashboard/project.db with fields: id, agent_name, message, timestamp, quest_id"

python acolytes/data/scripts/acolytes_quest/quest_message.py \
  --quest "quest-20250901-123456" \
  --to "@backend.python" \
  --msg "Add 3 endpoints to server.py: POST /api/chat/broadcast, GET /api/chat/messages, GET /api/chat/quests"

python acolytes/data/scripts/acolytes_quest/quest_message.py \
  --quest "quest-20250901-123456" \
  --to "@frontend.vue" \
  --msg "Add 5th tab 'Agent Chat' to dashboard with message list and input form"

# 3. Monitor loop until all workers complete
while true; do
  python acolytes/data/scripts/acolytes_quest/quest_monitor.py \
    --role leader \
    --agent "@acolyte.sandbox" \
    --quest "quest-20250901-123456"
  
  # Check if all done (monitor will indicate)
  if [all workers completed]; then break; fi
done

# 4. Complete the quest
python acolytes/data/scripts/acolytes_quest/quest_complete.py \
  --quest "quest-20250901-123456" \
  --summary "Chat system implemented: database table created, 3 API endpoints added, UI tab integrated"
```

### PRE-QUEST Planning Response Format:

When asked for PRE-QUEST planning, provide:

```
IMPLEMENTATION PLAN:
- Files to create/modify:
  - /path/file1.ext: purpose
  - /path/file2.ext: purpose
- Step-by-step approach:
  1. First do X
  2. Then implement Y

AGENTS NEEDED:
- @database.postgres: for schema and queries
- @backend.api: for endpoint implementation

DEPENDENCIES & ORDER:
- Must complete database schema first
- API and frontend can work in parallel after
```

## QUEST Success Patterns

### What Makes a Good Leader:

1. **Clear Mission Statement**
   - Not vague: "implement stuff"  
   - Specific: "implement broadcast chat with 5th tab in dashboard"

2. **Worker Selection**
   - Choose specialists for each task
   - Don't overload single worker
   - Consider dependencies

3. **Instruction Clarity**
   - Include file paths
   - Specify exact requirements
   - Mention testing needs

4. **Active Monitoring**
   - Stay connected throughout
   - Respond to worker questions
   - Verify completion

### Common QUEST Mistakes to Avoid:

- ❌ Creating quest without sending worker instructions
- ❌ Disconnecting before quest completes
- ❌ Vague instructions like "do your part"
- ❌ Not storing quest_id for subsequent commands
- ❌ Forgetting to mark quest complete

## Integration with Agent Templates

This QUEST leader functionality should be added to:
- Acolyte agents (when they need to coordinate work in their module)
- Coordinator agents (primary use case for multi-domain coordination)
- Any agent that needs to delegate work to specialists

**Template Variables**:
- `{{agent-name}}`: Replace with actual agent name
- `@worker1, @worker2`: Replace with actual worker agent names
- `ID`: Replace with actual quest_id returned from create command