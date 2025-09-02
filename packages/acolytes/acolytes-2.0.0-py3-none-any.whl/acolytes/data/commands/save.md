---
description: ♾️  Save - Comprehensive session capture with full technical context to SQLite database
---

# Save Command - COMPLETE CONTEXT PRESERVATION

Saves comprehensive session data to SQLite database with full technical context, code snippets, user messages, and detailed progress tracking.

## 🔇 SILENT EXECUTION RULE

**CRITICAL**: During /save execution, Claude must:

- Show ONLY: "=============================== 💾 Saving Enhanced Session... ===============================" at the start
- Execute ALL commands silently (no additional commentary)
- Show ONLY the final result summary
- NEVER add extra text between tool executions

## CODE INDEX REINDEXING

Before saving the session, Claude MUST silently execute:

```
mcp__code-index__set_project_path(current_project_path)
```

This ensures the code index is up-to-date for the next session (takes ~1 second).
The reindexing removes deleted files and adds new ones automatically.

## WHAT CLAUDE MUST ANALYZE -ENHANCED FIELDS

### 🎯 PRIMARY_REQUEST_AND_INTENT (Required)

Capture ALL of the user's explicit requests and intents in detail:

- Initial request that started the session
- How the request evolved during conversation
- Specific requirements and constraints mentioned
- User's ultimate goal

### 🔧 KEY_TECHNICAL_CONCEPTS (Required)

List all important technical elements:

- Technologies used (Python, SQLite, MCP, etc.)
- Frameworks and libraries
- Architectural patterns discussed
- Design decisions made

### 📁 FILES_AND_CODE_SECTIONS (Required)

Enumerate specific files with full context:

- File path
- Why this file is important
- Summary of changes made
- **Full code snippets** (not summaries)
- Before/after for edits

### 🐛 ERRORS_AND_FIXES (Required)

Detailed error documentation:

- Complete error messages
- Root cause analysis
- How you fixed each error
- **User feedback on the fix** (critical!)
- What you learned

### 🔍 PROBLEM_SOLVING (Required)

Document resolution journey:

- Problems identified
- Approaches tried
- What worked/didn't work
- Ongoing troubleshooting efforts

### 💬 ALL_USER_MESSAGES (Required)

**COMPLETE list of user messages** (not tool results):

- Preserves exact user language
- Captures tone and frustration
- Shows changing requirements
- Critical for understanding context

### 📋 PENDING_TASKS (Required)

Outstanding work clearly defined:

- Tasks explicitly requested but not completed
- Tasks discovered during work
- Priority order if mentioned

### 🔨 CURRENT_WORK (Required)

Precise description of immediate work:

- Exact file being edited
- Function/class being modified
- Line numbers if relevant
- Code snippet in progress

### ⚡ NEXT_STEP (Required)

Clear next action aligned with user intent:

- Must be DIRECTLY related to current work
- Include verbatim quote showing task origin
- No tangential work without confirmation

### 🏆 QUALITY_METRICS (From our system)

Keep our quality tracking:

- accomplishments (list)
- bugs_fixed (list)
- decisions (list)
- breakthrough_moment (string)
- quality_score (calculated)

## EXACT COMMAND FORMAT

````bash
uv run python ~/.claude/scripts/save_session.py \
  -primary_request "Full detailed capture of user's requests and evolution" \
  -technical_concepts "Python 3.11, SQLite, MCP servers, Click CLI" \
  -files_and_code "file1.py|Important because X|Added function Y|```python\ncode here\n```||file2.md|Documentation|Updated section Z|```markdown\ncontent\n```" \
  -errors_and_fixes "Error: No active session|Fixed by creating session with INSERT|User said 'ok create it first'" \
  -problem_solving "Identified session management issue. Tried reading from DB. Found no active session. Created new one." \
  -user_messages "Message 1||Message 2||Message 3" \
  -pending_tasks "Task 1||Task 2||Task 3" \
  -current_work "Editing save_session.py line 180-192 to handle datetime formats" \
  -next_step "Wait for user to provide alternative save document per their request: 'te voy a pasar un documento'" \
  -accomplishments "Fixed datetime parsing||Improved quality score||Created active session" \
  -bugs_fixed "Datetime format error||Missing session error" \
  -decisions "Use base score of 4||Keep claude_session_id field" \
  -breakthrough "One Claude session contains multiple Acolytes sessions" \
  -conversation_flow "Q: What was the issue? A: No active session. Q: How fixed? A: Created new session."
````

## FIELD SEPARATORS

- **Between items in a field**: `||` (double pipe)
- **Between file sections**: `||` (double pipe)
- **File internal separator**: `|` (single pipe for file components)
- **Code blocks**: Triple backticks with language

## WORKING EXAMPLE

````bash
uv run python ~/.claude/scripts/save_session.py \
  -primary_request "User wanted to save lost session data from previous conversation that ended without context. Then study and fix save system issues including session creation, claude_session_id retrieval, datetime parsing, and quality score improvements. User explicitly demanded 'QUE hagas lo que te puto pido' when I misunderstood session relationships." \
  -technical_concepts "SQLite database at .claude/memory/project.db||Dual session system (Claude vs Acolytes)||JSONL transcript files||Quality score weighted algorithm||Python datetime parsing||UUID validation regex" \
  -files_and_code "save_session.py|Core save script|Fixed datetime parsing and claude_session_id|```python\nfor fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M']:\n    try:\n        start_time = datetime.strptime(session_data['created_at'], fmt)\n        break\n    except ValueError:\n        continue\n```||save.md|Documentation|Updated with examples|```markdown\nuv run python ~/.claude/scripts/save_session.py -session '...' -message '...'\n```" \
  -errors_and_fixes "No active session found|Created session_3b2b00092a6e with INSERT INTO sessions|User: 'ok lo primero es crear una session activa'||unconverted data remains: :05|Added multiple datetime format parsing|Worked immediately||Misunderstood session relationships|User corrected me forcefully about Claude vs Acolytes sessions|User: 'porque co;o esto peleandome contigo'" \
  -problem_solving "Identified 5 critical problems in save system. Created active session to enable saves. Fixed datetime parsing with multiple format support. Corrected claude_session_id to get latest JSONL by timestamp. Improved quality score from simple counting to weighted scoring. Ongoing: messages table schema inconsistency." \
  -user_messages "buenas!||en la ultima session que hay por favor guarda lo que te voy a pegar||porque no ha pillado el claude_session?||que da igual que pille siempre el ultimo que hay||porque co;o esto peleandome contigo, QUE hagas lo que te puto pido||pruebalo||bien ahora el quality score||ok no me gusta tanta puntuacion, pero ok. yo empezaria como base un 4||te voy a pasar un documento, que creo que es mejor que nuestro save ok?" \
  -pending_tasks "Review alternative save document||Update session_start.py hook for automatic session creation||Fix messages table schema inconsistency" \
  -current_work "Waiting for user to provide alternative save document they mentioned is better than current system" \
  -next_step "Review and analyze the alternative save document once provided. User said: 'te voy a pasar un documento, que creo que es mejor que nuestro save ok?'" \
  -accomplishments "Fixed claude_session_id to get latest JSONL||Understood Claude vs Acolytes session relationship||Created active session for testing||Improved quality score algorithm||Fixed datetime parsing error" \
  -bugs_fixed "Script gets correct JSONL file now||Datetime parsing handles multiple formats||Quality score uses intelligent weighting" \
  -decisions "Keep claude_session_id field for tracking||Use base score of 4 instead of 5||Weight bug fixes higher than accomplishments" \
  -breakthrough "Realizing one Claude session contains multiple Acolytes sessions making ID reuse correct behavior not a bug" \
  -conversation_flow "Q: What was main issue? A: Save system had multiple critical failures. Q: How were they fixed? A: Created active session, fixed datetime parsing, corrected session ID retrieval. Q: What's next? A: User wants to show alternative save document."
````

## OUTPUT FORMAT

After successful save, present results:

```markdown
====================================================================================

# 📊 Session Saved Successfully

## Session Information

- **Session ID**: {session_id}
- **Job**: {job_id}
- **Quality Score**: {quality_score}/10 ⭐
- **Duration**: {duration_minutes} minutes
- **Total Exchanges**: {total_exchanges}

## 🎯 Primary Request and Intent

{primary_request_formatted}

## 🔧 Key Technical Concepts

{technical_concepts_as_bullets}

## 📁 Files Modified ({file_count})

{files_with_summaries_and_snippets}

## 🐛 Errors Fixed ({error_count})

{errors_with_fixes_and_feedback}

## 💬 User Feedback Captured

{count} user messages preserved for context

## 📋 Pending Tasks ({pending_count})

{pending_tasks_as_bullets}

## 🔨 Current Work Status

{current_work_description}

## ⚡ Next Step

{next_step_with_quote}

## 🏆 Session Metrics

- **Accomplishments**: {accomplishment_count}
- **Bugs Fixed**: {bugs_count}
- **Decisions Made**: {decision_count}
- **Breakthrough**: {breakthrough_preview}

## 💾 Full Context Preserved

All code snippets, user messages, and technical details saved for perfect session continuity.

====================================================================================
```

## ❌ INVALID FORMATS (Will Be Rejected)

```bash
# Missing field separators
❌ -user_messages "message1 message2 message3"  # Need || between

# No code blocks for code
❌ -files_and_code "file.py|changed|added function foo"  # Need actual code

# Summarizing instead of full user messages
❌ -user_messages "User wanted save system fixed"  # Need verbatim messages

# Generic next step
❌ -next_step "Continue working on project"  # Need specific task with quote
```

## CRITICAL IMPROVEMENTS OVER OLD SYSTEM

1. **Full Code Preservation**: Actual snippets, not descriptions
2. **User Message History**: Complete context of user intent
3. **Error + Feedback**: What went wrong AND user's response
4. **File-Level Tracking**: Every file touched with reasons
5. **Current Work Precision**: Exact location in codebase
6. **Next Step Alignment**: Verbatim quotes prevent task drift

This enhanced format ensures ZERO context loss between sessions.
