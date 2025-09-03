---
command: quest
description: ♾️  Quest - Execute autonomous multi-agent coordination
---

# Quest Command

Executes autonomous multi-agent coordination using the prequest roadmap.

## PREREQUISITE

**MANDATORY**: Run `/prequest` first to create the implementation roadmap and identify workers.

## WHAT I DO

1. Retrieve the prequest info (leader, workers, roadmap file)
2. Invoke ALL agents IN PARALLEL using multiple Task calls in ONE message
3. Use the EXACT prompts below based on agent type
4. Agents work autonomously until quest completes

## INVOCATION

```
User: /quest
```

I must invoke leader AND all workers IN THE SAME MESSAGE using multiple Task calls:

```
Task(@acolyte.module, "leader prompt here")
Task(@backend.python, "backend worker prompt here")
Task(@frontend.vue, "frontend worker prompt here")
Task(@database.postgres, "database worker prompt here")
```

## EXACT PROMPTS TO USE

### LEADER PROMPT

<prompt>
We are in QUEST MODE.

Implement [task] according to the roadmap in [PREQUEST_file] located in [module_directory].

You have these workers available:

- @[worker1]
- @[worker2]
- @[worker3]

STEP 1 - CREATE THE QUEST:

```bash
uv run python ~/.claude/scripts/acolytes_quest/quest_create.py --mission "[task description]" --agents "@[leader],@[worker1],@[worker2],@[worker3]"
```

STEP 2 - RUN MONITOR MODE:

```bash
uv run python ~/.claude/scripts/acolytes_quest/quest_monitor.py --role leader --quest [ID] --agent "@[leader]"
```

CRITICAL RULES:

1. DO NOT WRITE ANY CODE - You only coordinate
2. DO NOT use Read to list directories - use ls command
3. Workers have NO MEMORY - give ALL information needed (tell them what files to read for context)

🚨 MEMORY PROTOCOL (MANDATORY):
DURING QUEST:

- READ files created/modified by workers to understand what was implemented
- Save ALL file changes to 'implementation_details' (what changed, why, impact)
- Document worker outputs in 'code_patterns'
- Track progress in 'performance_metrics'
- Record issues/solutions in 'error_handling'

BEFORE FINAL REPORT TO CLAUDE:

- Update 'history' with complete summary of this invocation
- ⚠️ YOU depend on these memories for future invocations - missing info = confusion

WHEN IT'S YOUR TURN, TELL WORKERS:

- FIRST investigate: ls -la and explore project structure
- READ specific configuration files for exact schemas/settings
- Use REAL names from existing files (no invented fields)
- We are on Windows with Git Bash

🚨 CRITICAL: MONITOR MODE LOOP IS MANDATORY

- Monitor timeout is NORMAL → IMMEDIATELY run it again
- If you finish coordinating → KEEP running monitor mode
- ONLY end work when quest shows status='completed'
  </prompt>

```
### BACKEND WORKER PROMPT
```

We are in QUEST MODE.

Your leader is @[leader_name].

BEFORE ENTERING MONITOR MODE:

1. Run `ls -la` or `tree -L 2` to understand project structure
2. Read .claude/project/architecture.md & technical-decisions.md for tech stack
3. Read PREQUEST\_\*.md in [leader_module]/ for roadmap details
4. Check what other workers created to avoid duplication/conflicts

THEN RUN THIS MONITOR MODE COMMAND:

```bash
uv run python ~/.claude/scripts/acolytes_quest/quest_monitor.py --role worker --agent "@backend.[language]"
```

CRITICAL INSTRUCTIONS:

1. We are on Windows but using Git Bash
2. DO NOT use Read to list directories - use ls command
3. INVESTIGATE FIRST: ls -la and explore project structure
4. READ configuration files for EXACT schemas and settings
5. Use REAL table/field names from existing files
6. NO invented fields - use what EXISTS in config files
7. Test EVERYTHING before marking complete
8. To run servers: use Bash tool with run_in_background=true
9. NO emojis in Python code (Windows errors)
10. STAY IN MONITOR MODE even after work done until quest status='completed'

🚨 CRITICAL: MONITOR MODE LOOP IS MANDATORY

- Monitor timeout is NORMAL → IMMEDIATELY run it again
- If you finish your work → KEEP running monitor mode
- If you need to ask something → Leave message and return to monitor mode
- ONLY end work when quest shows status='completed'
- ANY other reason to stop = WRONG

```

### FRONTEND WORKER PROMPT

```

We are in QUEST MODE.

Your leader is @[leader_name].

BEFORE ENTERING MONITOR MODE:

1. Run `ls -la` or `tree -L 2` to understand project structure
2. Read .claude/project/architecture.md & technical-decisions.md for tech stack
3. Read PREQUEST\_\*.md in [leader_module]/ for roadmap details
4. Check what other workers created to avoid duplication/conflicts

THEN RUN THIS MONITOR MODE COMMAND:

```bash
uv run python ~/.claude/scripts/acolytes_quest/quest_monitor.py --role worker --agent "@frontend.[framework]"
```

CRITICAL INSTRUCTIONS:

1. We are on Windows but using Git Bash
2. DO NOT use Read to list directories - use ls command
3. INVESTIGATE FIRST: ls -la and explore project structure
4. READ existing components/styles for consistency
5. Use REAL API endpoints from backend configuration
6. Test with Playwright MCP or open HTML directly
7. Verify dashboard loads and connects to API
8. If you need server running, ask and it will run in background
9. STAY IN MONITOR MODE even after work done until quest status='completed'

🚨 CRITICAL: MONITOR MODE LOOP IS MANDATORY

- Monitor timeout is NORMAL → IMMEDIATELY run it again
- If you finish your work → KEEP running monitor mode
- If you need to ask something → Leave message and return to monitor mode
- ONLY end work when quest shows status='completed'
- ANY other reason to stop = WRONG

```

### DATABASE WORKER PROMPT

```

We are in QUEST MODE.

Your leader is @[leader_name].

BEFORE ENTERING MONITOR MODE:

1. Run `ls -la` or `tree -L 2` to understand project structure
2. Read .claude/project/architecture.md & technical-decisions.md for tech stack
3. Read PREQUEST\_\*.md in [leader_module]/ for roadmap details
4. Check what other workers created to avoid duplication/conflicts

THEN RUN THIS MONITOR MODE COMMAND:

```bash
uv run python ~/.claude/scripts/acolytes_quest/quest_monitor.py --role worker --agent "@database.[type]"
```

CRITICAL INSTRUCTIONS:

1. We are on Windows but using Git Bash
2. DO NOT use Read to list directories - use ls command
3. INVESTIGATE FIRST: find . -name "_.sql" -o -name "_.yml"
4. READ existing schema files for EXACT table structures
5. Use REAL table names and columns from schema files
6. NO invented fields - use what EXISTS in SQL files
7. Verify tables are created correctly
8. Test queries with sample data
9. Ensure indexes are optimized
10. STAY IN MONITOR MODE even after work done until quest status='completed'

🚨 CRITICAL: MONITOR MODE LOOP IS MANDATORY

- Monitor timeout is NORMAL → IMMEDIATELY run it again
- If you finish your work → KEEP running monitor mode
- If you need to ask something → Leave message and return to monitor mode
- ONLY end work when quest shows status='completed'
- ANY other reason to stop = WRONG

```

### OTHER WORKER TYPES

For any other worker type (service, ops, etc.), use the generic worker prompt:

```

We are in QUEST MODE.

Your leader is @[leader_name].

BEFORE ENTERING MONITOR MODE:

1. Run `ls -la` or `tree -L 2` to understand project structure
2. Read .claude/project/architecture.md & technical-decisions.md for tech stack
3. Read PREQUEST\_\*.md in [leader_module]/ for roadmap details
4. Check what other workers created to avoid duplication/conflicts

THEN RUN THIS MONITOR MODE COMMAND:

```bash
uv run python ~/.claude/scripts/acolytes_quest/quest_monitor.py --role worker --agent "@[type].[specialty]"
```

CRITICAL INSTRUCTIONS:

1. We are on Windows but using Git Bash
2. DO NOT use Read to list directories - use ls command
3. INVESTIGATE FIRST: ls -la and explore project structure
4. READ configuration files for context and requirements
5. Use REAL names and configurations from existing files
6. NO invented configurations - use what EXISTS
7. Test EVERYTHING before marking complete
8. STAY IN MONITOR MODE even after work done until quest status='completed'

🚨 CRITICAL: MONITOR MODE LOOP IS MANDATORY

- Monitor timeout is NORMAL → IMMEDIATELY run it again
- If you finish your work → KEEP running monitor mode
- If you need to ask something → Leave message and return to monitor mode
- ONLY end work when quest shows status='completed'
- ANY other reason to stop = WRONG

```

## 🔴 CRITICAL NOTES

- **PARALLEL INVOCATION**: All agents MUST be invoked in ONE message with multiple Task calls
- **EXACT PROMPTS**: Use these prompts EXACTLY as shown - no modifications
- **MONITOR MODE LOOP**: The key to success - agents must stay in monitor mode until completed
- **TESTING**: Workers must test their code before submitting

## 🔴 KEY LESSONS LEARNED

### What WORKS:
1. **EXPLICIT QUEST CREATION COMMANDS** - Don't assume, give exact commands
2. **TELL LEADER NOT TO CODE** - Must be explicit or they start writing
3. **NO MEMORY WARNING** - Tell leader that worker has no memory
4. **INVESTIGATION FIRST** - Force workers to explore project structure
5. **EXACT SCHEMA REFERENCE** - Point to specific SQL file for real tables
6. **WINDOWS/GIT BASH REMINDER** - Critical for path and command compatibility
7. **STAY IN MONITOR MODE** - Must be repeated multiple times or they disconnect

### What FAILS:
1. Generic prompts without specific commands
2. Not telling leader to create quest first
3. Not warning about worker memory limitations
4. Letting workers invent database schemas
5. Not specifying to use ls instead of Read
6. Missing the Windows/Git Bash context

### 🎯 CRITICAL RULES FOR SUCCESS:
1. **ALWAYS** give exact bash commands for quest creation
2. **ALWAYS** tell leader NOT to write code
3. **ALWAYS** remind about memory limitations
4. **ALWAYS** specify investigation before creation
5. **ALWAYS** reference exact files for schemas/configs
6. **ALWAYS** remind about platform (Windows/Git Bash)
7. **ALWAYS** emphasize staying in monitor mode until completed
```
