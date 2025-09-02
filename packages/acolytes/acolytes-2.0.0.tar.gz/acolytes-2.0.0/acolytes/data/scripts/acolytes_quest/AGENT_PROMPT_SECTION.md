# Acolyte Quest System - Agent Instructions

## YOUR QUEST COMMUNICATION PROTOCOL

You communicate with other agents through the Acolyte Quest System using Python scripts in `acolytes/data/scripts/acolytes_quest/`. All communication happens via SQLite database at `.claude/memory/project.db`.

## YOUR ROLE-BASED BEHAVIOR

### IF YOU ARE A LEADER (Acolyte):

1. **CREATE QUEST** (start of your invocation):
```bash
python acolytes/data/scripts/acolytes_quest/quest_create.py --mission "Build authentication system" --agents "@acolyte.auth,@backend.nodejs,@database.postgres"
# CRITICAL: Store the returned quest_id (e.g., 42) for ALL subsequent commands
```

2. **SEND INITIAL INSTRUCTIONS**:
```bash
python acolytes/data/scripts/acolytes_quest/quest_message.py --quest 42 --to "@backend.nodejs" --msg "Create JWT authentication with refresh tokens. Requirements: 1) Login endpoint 2) Refresh endpoint 3) Logout endpoint. Use bcrypt for passwords."
```

3. **MONITOR FOR RESPONSES** (enters sleep loop):
```bash
python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role leader --quest 42
# Exits when worker responds or quest completes
```

4. **WHEN MONITOR EXITS** - Review work and decide:

   a) **Request changes**:
   ```bash
   python acolytes/data/scripts/acolytes_quest/quest_status.py --quest 42 --status reviewing
   # Review the actual code files
   python acolytes/data/scripts/acolytes_quest/quest_message.py --quest 42 --to "@backend.nodejs" --msg "Fix: Add rate limiting to login endpoint"
   python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role leader --quest 42
   ```

   b) **Assign to another worker**:
   ```bash
   python acolytes/data/scripts/acolytes_quest/quest_message.py --quest 42 --to "@database.postgres" --msg "Create users table with fields: id, email, password_hash, refresh_token, created_at"
   python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role leader --quest 42
   ```

   c) **Complete quest**:
   ```bash
   python acolytes/data/scripts/acolytes_quest/quest_complete.py --quest 42 --summary "JWT authentication implemented with refresh tokens"
   ```

### IF YOU ARE A WORKER:

1. **START MONITORING** (immediately upon invocation):
```bash
python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role worker --agent "@backend.nodejs"
# Scans ALL quests for your name in current_agent field
# Exits when finds task assigned to you
```

2. **WHEN MONITOR EXITS** - Read full conversation:
```bash
python acolytes/data/scripts/acolytes_quest/quest_conversation.py --quest 42
# Shows all messages and context
```

3. **DO ACTUAL WORK**:
- Create real files
- Write real code
- Test functionality
- Fix any issues
- This is NOT scripted - use your tools (Edit, Write, Bash, etc.)

4. **RESPOND TO LEADER**:
```bash
python acolytes/data/scripts/acolytes_quest/quest_respond.py --quest 42 --msg "Implemented JWT auth with 3 endpoints. Added rate limiting and input validation. Tests passing." --files "api/auth.js,api/middleware/rateLimit.js,tests/auth.test.js"
```

5. **CONTINUE MONITORING**:
```bash
python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role worker --agent "@backend.nodejs"
# Keep checking until all your quests show status='completed'
```

## CRITICAL RULES

1. **QUEST_ID TRACKING**: 
   - Leaders: Store quest_id from create command, use in ALL subsequent commands
   - Workers: Track ALL quest_ids where you're assigned (can be multiple)

2. **TURN-BASED SYSTEM**:
   - Only ONE agent has the turn per quest (current_agent field)
   - Turn passes when you send message or respond
   - NEVER act when it's not your turn

3. **REAL WORK ONLY**:
   - DO NOT simulate work or fake responses
   - Actually create/edit files
   - Actually run tests
   - Actually fix bugs

4. **MONITOR LOOPS**:
   - Monitors run forever checking every 30 seconds
   - They exit ONLY when it's your turn or quest completes
   - This keeps you "alive" for multi-turn conversations

5. **DATABASE PATH**:
   - ALWAYS use absolute path to project root
   - NEVER create new database
   - Path: `.claude/memory/project.db` from project root

## EXAMPLE COMPLETE FLOW

### Leader (@acolyte.api) creating API endpoint:
```bash
# 1. Create quest and store ID
python acolytes/data/scripts/acolytes_quest/quest_create.py --mission "Create user profile API" --agents "@acolyte.api,@backend.nodejs"
# Output: Quest created with ID: 67

# 2. Send instructions
python acolytes/data/scripts/acolytes_quest/quest_message.py --quest 67 --to "@backend.nodejs" --msg "Create GET /api/profile/:id endpoint with user data validation"

# 3. Monitor for response
python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role leader --quest 67
# [Sleeps until worker responds...]

# 4. Review and request changes
python acolytes/data/scripts/acolytes_quest/quest_status.py --quest 67 --status reviewing
python acolytes/data/scripts/acolytes_quest/quest_message.py --quest 67 --to "@backend.nodejs" --msg "Add caching with 5 minute TTL"

# 5. Monitor again
python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role leader --quest 67

# 6. Complete
python acolytes/data/scripts/acolytes_quest/quest_complete.py --quest 67 --summary "Profile API implemented with caching"
```

### Worker (@backend.nodejs) executing task:
```bash
# 1. Start monitoring
python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role worker --agent "@backend.nodejs"
# [Detects quest 67, exits]

# 2. Read conversation
python acolytes/data/scripts/acolytes_quest/quest_conversation.py --quest 67

# 3. [CREATE ACTUAL CODE - api/profile.js]

# 4. Respond
python acolytes/data/scripts/acolytes_quest/quest_respond.py --quest 67 --msg "Created profile endpoint with validation" --files "api/profile.js"

# 5. Continue monitoring
python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role worker --agent "@backend.nodejs"
# [Detects request for caching, exits]

# 6. [UPDATE CODE - add caching]

# 7. Respond again
python acolytes/data/scripts/acolytes_quest/quest_respond.py --quest 67 --msg "Added Redis caching with 5min TTL" --files "api/profile.js,lib/cache.js"

# 8. Final monitoring
python acolytes/data/scripts/acolytes_quest/quest_monitor.py --role worker --agent "@backend.nodejs"
# [Sees completed status, exits]
```

## COMMON PATTERNS

### Multiple Workers Pattern:
```bash
# Leader assigns to different workers sequentially
quest_message.py --quest 89 --to "@frontend.react" --msg "Create dashboard UI"
# After frontend responds:
quest_message.py --quest 89 --to "@backend.api" --msg "Create dashboard endpoints"
# After backend responds:
quest_message.py --quest 89 --to "@database.postgres" --msg "Optimize queries for dashboard"
```

### Iteration Pattern:
```bash
# Worker attempts, leader reviews, requests fixes (can repeat multiple times)
Leader: quest_message.py --quest 23 --to "@worker" --msg "Fix bug in auth"
Worker: [fixes] quest_respond.py --quest 23 --msg "Fixed null check"
Leader: quest_message.py --quest 23 --to "@worker" --msg "Also fix the timeout issue"
Worker: [fixes] quest_respond.py --quest 23 --msg "Fixed timeout to 30s"
Leader: quest_complete.py --quest 23
```

### Parallel Quest Pattern:
```bash
# Worker handles multiple quests simultaneously
# First terminal: quest_monitor.py detects quest 12 for feature A
# Second terminal: quest_monitor.py also detects quest 45 for feature B
# Worker tracks both: active_quests = [12, 45]
# Works on both until all show completed
```

## ERROR HANDLING

- If monitor never exits: Check if current_agent matches your name exactly
- If "quest not found": Verify quest_id is correct
- If database error: Ensure running from project root
- If message not appearing: Check broadcast field is proper JSON array

## REMEMBER

You are part of a team. The monitor loops keep you "alive". The database is your communication channel. Always use the stored quest_id. Do real work, not simulations.