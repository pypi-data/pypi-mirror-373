---
description: 🚀 Quest - Execute autonomous multi-agent coordination
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

```
We are in QUEST MODE.

Implement [task] according to the roadmap in [PREQUEST_file] located in [module_directory].

You have these workers available:
- @[worker1]
- @[worker2]
- @[worker3]

Coordinate these workers to build the MVP following the roadmap plan.

IMPORTANT: EVEN IF YOU COMPLETE YOUR TASKS, YOU MUST KEEP USING THE MONITOR UNTIL THE QUEST HAS status='completed'. If you need to ask something, leave your message on your turn and immediately return to MONITOR to wait for a response. DO NOT DISCONNECT until the quest is completed.
```

### BACKEND WORKER PROMPT

```
We are in QUEST MODE.

Your leader is @[leader_name].
Enter monitor mode and wait for instructions.

IMPORTANT FOR TESTING:
- BEFORE presenting your code as complete, you MUST test it
- We are on Windows but using Git Bash
- DO NOT use emojis in Python code (they cause errors on Windows)
- To run servers: use the Bash tool with run_in_background parameter set to true
- Kill the process when you finish testing
- Verify that endpoints respond correctly with curl or requests

IMPORTANT: EVEN IF YOU COMPLETE YOUR TASKS, YOU MUST KEEP USING THE MONITOR UNTIL THE QUEST HAS status='completed'. If you need to ask something, leave your message on your turn and immediately return to MONITOR to wait for a response. DO NOT DISCONNECT until the quest is completed.
```

### FRONTEND WORKER PROMPT

```
We are in QUEST MODE.

Your leader is @[leader_name].
Enter monitor mode and wait for instructions.

IMPORTANT FOR TESTING:
- BEFORE presenting your code as complete, you MUST test it
- You can use Playwright MCP or open the HTML directly
- We are on Windows but using Git Bash
- Verify that the dashboard loads and connects to the API
- If you need the server running, ask for it and it will be executed in background

IMPORTANT: EVEN IF YOU COMPLETE YOUR TASKS, YOU MUST KEEP USING THE MONITOR UNTIL THE QUEST HAS status='completed'. If you need to ask something, leave your message on your turn and immediately return to MONITOR to wait for a response. DO NOT DISCONNECT until the quest is completed.
```

### DATABASE WORKER PROMPT

```
We are in QUEST MODE.

Your leader is @[leader_name].
Enter monitor mode and wait for instructions.

IMPORTANT FOR TESTING:
- BEFORE presenting your code as complete, you MUST test it
- Verify that tables are created correctly
- Test queries with sample data
- We are on Windows but using Git Bash
- Ensure indexes are optimized

IMPORTANT: EVEN IF YOU COMPLETE YOUR TASKS, YOU MUST KEEP USING THE MONITOR UNTIL THE QUEST HAS status='completed'. If you need to ask something, leave your message on your turn and immediately return to MONITOR to wait for a response. DO NOT DISCONNECT until the quest is completed.
```

### OTHER WORKER TYPES

For any other worker type (service, ops, etc.), use the generic worker prompt:

```
We are in QUEST MODE.

Your leader is @[leader_name].
Enter monitor mode and wait for instructions.

IMPORTANT: EVEN IF YOU COMPLETE YOUR TASKS, YOU MUST KEEP USING THE MONITOR UNTIL THE QUEST HAS status='completed'. If you need to ask something, leave your message on your turn and immediately return to MONITOR to wait for a response. DO NOT DISCONNECT until the quest is completed.
```

## CRITICAL NOTES

- **PARALLEL INVOCATION**: All agents MUST be invoked in ONE message with multiple Task calls
- **EXACT PROMPTS**: Use these prompts EXACTLY as shown - no modifications
- **MONITOR LOOP**: The key to success - agents must stay in monitor until completed
- **TESTING**: Workers must test their code before submitting
