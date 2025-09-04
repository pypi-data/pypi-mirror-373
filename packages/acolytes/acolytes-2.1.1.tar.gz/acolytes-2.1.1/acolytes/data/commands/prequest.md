---
command: prequest
description: ♾️  PreQuest - Create detailed roadmap for specific module implementation with worker agents
---

# PreQuest Command - DETAILED QUEST PLANNING

Creates a hyper-precise roadmap for a specific point from the main project roadmap, identifying required worker agents and detailed implementation steps.

## 🎯 PURPOSE

The `/prequest` command is a "TODO list on steroids" that:

- Takes a high-level roadmap point (e.g., "1.4 Dashboard Implementation")
- Delegates to the appropriate acolyte module owner
- Gets back a hyper-detailed implementation plan
- Identifies all worker agents needed
- Saves the plan for `/quest` execution

## 🔄 WORKFLOW

### 1. USER INVOKES PREQUEST

```
User: /prequest implement dashboard MVP
```

### 2. I ANALYZE THE REQUEST

I must:

1. Identify which module this belongs to (using agent routing)
2. Find the appropriate acolyte owner
3. Invoke that acolyte with PREQUEST MODE

### 3. ACOLYTE PROMPT FORMAT

I MUST use this EXACT prompt format:

```
PREQUEST MODE

Create a hyper-precise roadmap for: [specific task from user]

This corresponds to point [X.Y] from the main roadmap.

Requirements:
1. Break down into specific, executable steps
2. 🚨 If task has MULTIPLE PHASES → Divide into Phase 1, Phase 2, etc.
3. For EACH phase, identify needed workers SEPARATELY
4. BEFORE naming workers, use this command to find the right specialists:
   ```bash
   uv run python ~/.claude/scripts/agent_db.py search-agents "[capability needed]" 5
   ```
   Example: search-agents "time-series database" → finds @database.timescale
5. Include external consultants if needed (e.g., @coordinator.* for strategic decisions)
6. Define clear success criteria for each step
7. Specify testing requirements
8. Save as PREQUEST_[timestamp].md in your module directory

Return:
- Roadmap file path
- List of required workers
- Estimated complexity
```

### 4. ACOLYTE RESPONSE

The acolyte will:

1. Create detailed roadmap file: `PREQUEST_YYYYMMDD_HHMMSS.md`
2. Save in their module directory (e.g., `/sandbox/PREQUEST_*.md`)
3. Update their agent memory with the plan
4. Return worker list and file path

### 5. I STORE THE INFORMATION

I must remember:

- Prequest file path
- Module owner (leader)
- Worker agents identified
- This info is needed for `/quest` command

## 📝 EXAMPLE EXECUTION

### User Request:

```
/prequest implement authentication system
```

### My Analysis:

```
1. Authentication = auth module
2. Owner = @acolyte.auth
3. Invoke with PREQUEST MODE
```

### My Invocation:

```
@acolyte.auth, PREQUEST MODE

Create a hyper-precise roadmap for: implement authentication system

This corresponds to point 2.3 from the main roadmap.

Requirements:
1. Break down into specific, executable steps
2. Identify ALL worker agents needed (backend, frontend, database, etc.)
3. Define clear success criteria for each step
4. Specify testing requirements
5. Save as PREQUEST_[timestamp].md in your module directory

Return:
- Roadmap file path
- List of required workers
- Estimated complexity
```

### Acolyte Response:

```
✅ PreQuest created successfully!

📋 Roadmap: /auth/PREQUEST_20250901_143000.md
👥 Workers needed:
   - @backend.nodejs (API endpoints)
   - @database.postgres (user tables)
   - @frontend.react (login UI)
   - @service.auth (OAuth2 expertise)

🎯 Complexity: Medium (15 steps, ~3 hours)
```

## 🚨 CRITICAL RULES

1. **ALWAYS use PREQUEST MODE** in the prompt
2. **ALWAYS specify the module directory** for saving
3. **ALWAYS get worker list** from acolyte
4. **NEVER proceed to quest** without prequest
5. **ALWAYS save in agent memory** for persistence

## 💾 STORAGE

The prequest information is stored as:

- **File**: `[module]/PREQUEST_[timestamp].md` (e.g., `/sandbox/PREQUEST_20250901_143000.md`)
- **Database**: The acolyte may update their memories with references to the prequest in their 'history' or 'knowledge' memory types

## 🔗 RELATIONSHIP WITH /QUEST

The `/quest` command REQUIRES a prequest because:

- It needs the detailed roadmap
- It needs the worker list
- It needs the module owner as leader
- It uses the PREQUEST file as the implementation guide

## ❌ ERROR HANDLING

If prequest fails:

- Check if module has an acolyte owner
- Verify acolyte exists in agents_catalog
- Ensure module directory is writable
- Fall back to coordinator if no acolyte exists

## ✅ SUCCESS CRITERIA

A successful prequest:

1. Creates a detailed roadmap file
2. Identifies all necessary workers
3. Saves to module directory
4. Updates agent memory
5. Returns clear path for /quest execution
