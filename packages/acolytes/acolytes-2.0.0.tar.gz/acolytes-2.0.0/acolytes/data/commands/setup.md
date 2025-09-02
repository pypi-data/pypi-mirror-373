---
command: setup
description: ♾️  Setup project with Acolytes for Claude Code | Optional: --update
---

## ⚡ MANDATORY COMMAND FLOW

This system provides intelligent project setup with Acolytes for Claude Code's +50 specialized agents, supporting both existing projects and new project creation from expert consultation.

## Usage

```
/setup          # Initial complete setup for new projects OR existing projects
/setup --update # Update existing setup (new modules, refresh agents)
```

## 🚨 **MANDATORY EXECUTION RULE**

**PARALLEL EXECUTION = ONE MESSAGE WITH MULTIPLE TASK CALLS**

When this document says "parallel execution" or "agents (parallel)" it means:

- ✅ ONE single message with multiple Task calls
- ❌ NOT separate sequential messages

**Correct Example - ONE MESSAGE with multiple Task calls:**

```
Claude's single message contains:
• Task(@setup.codebase, prompt="Analyze /src/ directory and create architecture.md")
• Task(@setup.context, prompt="Analyze README and create vision.md")
• Task(@setup.infrastructure, prompt="Analyze configs and create team-preferences.md")
```

**All three Task calls in the SAME message - never separate messages.**

### **IMMUTABLE RULES – NO EXCEPTIONS**

1. **NEVER** analyze without creating documentation
2. **ALWAYS** create Database & MCP first (Phase 1)
3. **ALWAYS** create ALL required files and documentation
4. **NEVER** ask whether to create — just create
5. **ALL** documentation, code, comments, SQLite in English
6. **ALWAYS** use MULTIPLE TASK CALLS IN ONE MESSAGE for parallel execution

## 🎯 UNIFIED FLOW FOR BOTH PROJECT TYPES

### 1️⃣ **PHASE 1: ENVIRONMENT & DATABASE SETUP**

**WHAT YOU (CLAUDE) MUST DO**: Validate the development environment, create the SQLite database with all required tables, and configure MCP connection. Follow the steps below to establish the complete system foundation.

````yaml
ENVIRONMENT_CHECK:
  - Execute: uv run python ~/.claude/scripts/environment_check.py
  - Validates: Python 3.8+, Git 2.0+, Node 18+, uv package manager
  - Creates environment report in .claude/project/environment-status.md
  - Auto-fixes common issues where possible

DATABASE_AND_MCP:
  1. Initialize database schema:
    - Execute: cat ~/.claude/scripts/init_db.sql | sqlite3 .claude/memory/project.db
    - Database will auto-create: agents_catalog (52 agents), jobs table with initial job, sessions, messages, etc.
    - Initial job 'Project Setup' automatically created with high priority
    - All tables, indexes, triggers, and constraints ready

  2. Configure MCP SQLite:
    - Run: uv run python ~/.claude/scripts/setup_mcp.py
    - After this step, restart Claude CLI: exit, then run `claude --dangerously-skip-permissions -c`

  3. Initialize code-index MCP silently (NO COMMENTARY):
    - Execute: mcp__code-index__set_project_path(project_root)
    - Effect: enables faster searches for setup agents
    - Do NOT announce or comment on this indexing
    - Setup agents will use the index automatically
---

### 2️⃣ **PHASE 2: ANALYSIS & DOCUMENTATION**

**WHAT YOU (CLAUDE) MUST DO**: For existing projects, invoke the four setup agents in PARALLEL to analyze and document the project. For new projects, conduct the SMART REQUIREMENTS INTERVIEW following the conditional system, skip rules, and validation rules EXACTLY as specified - this interview adapts based on user type and project maturity. Study the interview system carefully before starting.

#### **FOR EXISTING PROJECTS**

```yaml
PARALLEL_ANALYSIS:
  mode: REAL PARALLEL
  agents:
    - @setup.codebase
    - @setup.context
    - @setup.environment
    - @setup.infrastructure
  execution: MULTIPLE TASK CALLS IN ONE MESSAGE

DOCUMENTATION_CREATION:
  location: .claude/project/
  assignment:
    setup.context: "vision.md + project-context.md"
    setup.codebase: "architecture.md + technical-decisions.md"
    setup.infrastructure: "team-preferences.md"
    setup.environment: "contributes to technical-decisions.md"
  files:
    - vision.md (project purpose and goals)
    - architecture.md (technical decisions and structure)
    - technical-decisions.md (rationale for tech choices)
    - team-preferences.md (coding standards and practices)
    - project-context.md (specific project details)
  format: English markdown with consistent structure
  note: "roadmap.md is NOT created here - only for existing projects. New projects get roadmap.md from plan.strategy"
````

#### **FOR NEW PROJECTS**

```yaml
PROJECT_MATURITY_CLASSIFICATION:
  question: "What type of project is this?"
  options:
    mvp: "Minimum Viable Product - prove concept quickly with basic features"
    startup: "Startup project - balance speed and scalability for growth"
    enterprise: "Enterprise application - security, compliance, and scale from start"
    proof_of_concept: "Technical proof of concept - experiment with technologies"
    production_ready: "Production-ready application - robust, maintainable, long-term"
  storage: "Save as {{project_maturity}} variable in CLAUDE.md template"
  impact: "Influences all technical decisions: stack complexity, testing strategy, deployment approach"

USER_CLASSIFICATION:
  question: "What's your development approach?"
  options:
    vibe_coder: "I focus on product vision and user experience - you implement all technical aspects"
    programmer: "I write code myself and want to understand/control technical implementation decisions"
  storage: "Save as {{user_exp_code}} variable in CLAUDE.md template"
  validation: "Confirm classification based on early responses - user might self-classify incorrectly"
  adjustment: "Allow reclassification if responses don't match initial choice"

REQUIREMENTS_INTERVIEW:
  approach: "Information-driven interview - focus on what data is needed rather than specific questions"
  interview_style:
    vibe_coder: "Use simple language, focus on what the app does for users, avoid technical jargon"
    programmer: "Use technical terms, provide specific technology options, discuss implementation trade-offs"

  conditional_system:
    smart_skip: "Skip or simplify areas based on project_maturity + user_exp_code + early responses"
    intelligent_inference: "Fill gaps with logical assumptions when areas are skipped"
    adaptive_depth: "Adjust question complexity based on classification and domain detection"

  skip_rules:
    mvp_optimizations:
      - "IF project_maturity = 'mvp' → SKIP/SIMPLIFY areas 6,7,8,9,10 (performance, dev context, quality, deployment, business)"
      - "ASSUME: Basic hosting, small team, minimal SLAs, validate-first approach"

    proof_of_concept_optimizations:
      - "IF project_maturity = 'proof_of_concept' → SKIP areas 6,8,9,10,13 (performance, quality, deployment, business, constraints)"
      - "ASSUME: Experimental stack, no production concerns, learning-focused"

    vibe_coder_optimizations:
      - "IF user_exp_code = 'vibe_coder' → SIMPLIFY areas 4,7,13 (auth, dev context, constraints)"
      - "ASSUME: Standard solutions preferred, minimal technical complexity"

    domain_detection:
      - "IF no_user_accounts_detected → SKIP área 4 (auth)"
      - "IF standalone_app_detected → SIMPLIFY área 5 (integrations)"
      - "IF simple_content_detected → SIMPLIFY área 3 (data)"

    auto_domain_triggers:
      fintech: "IF mentions: payment, banking, crypto, finance, fintech → TRIGGER compliance_deep + licensing_ip"
      healthcare: "IF mentions: health, medical, patient, healthcare, HIPAA → TRIGGER compliance_deep + security_enhanced"
      education: "IF mentions: school, student, learning, education, FERPA → TRIGGER compliance_deep"
      ecommerce: "IF mentions: store, shop, cart, inventory, sales → ASSUME payment_integration + inventory_management"
      government: "IF mentions: government, public, civic, municipal → TRIGGER compliance_deep + security_enhanced"
      social: "IF mentions: social, community, chat, messaging → TRIGGER content_moderation + privacy_enhanced"

  incomplete_handling:
    strategy: "Allow partial completion and resume later with context preservation"
    minimum_viable: "Identify minimum information needed to generate basic recommendations (areas 1-6 minimum)"
    follow_up: "Generate follow-up questions for unclear or missing critical information"

    smart_resume:
      context_reconstruction: "Rebuild conditional triggers and skip rules from saved state"
      progressive_disclosure: "Show what was skipped and allow manual override if user wants detail"
      recovery_prompts: "Smart suggestions based on incomplete areas and detected domain"
      validation_replay: "Re-run cross-validation rules after resume to catch new conflicts"

  validation:
    consistency_check: "Validate that answers across areas are consistent (e.g., enterprise + simple features conflict)"
    feasibility_check: "Flag unrealistic combinations (e.g., complex features + tight timeline + MVP)"
    cost_reality_check: "Warn about expensive combinations early (e.g., enterprise + multiple integrations)"

    cross_validation_rules:
      - "IF project_maturity = 'mvp' AND complex_integrations > 3 → WARNING: 'Consider simplifying integrations for MVP'"
      - "IF user_exp_code = 'vibe_coder' AND custom_stack_preference → WARNING: 'Consider standard solutions'"
      - "IF timeline < 3_months AND project_maturity = 'enterprise' → ERROR: 'Timeline-scope mismatch'"
      - "IF project_maturity = 'proof_of_concept' AND production_requirements → WARNING: 'POC scope expanding beyond validation'"
      - "IF user_exp_code = 'programmer' AND no_technical_preferences → PROMPT: 'Clarify technical control preferences'"

  persistence_strategy: "Save answers to .claude/project/requirements-interview.md every 4-5 information areas to prevent context loss"
  persistence: .claude/project/requirements-interview.md

  persistence_advanced:
    checkpoint_triggers:
      - "After each conditional area is triggered"
      - "When validation warnings or errors are generated"
      - "If user takes break > 10 minutes (detect via response timing)"
      - "Before complex specialist consultations"
      - "After domain detection changes interview flow"

    smart_context_preservation:
      - "Save skip rules applied and rationale"
      - "Record validation warnings for future reference"
      - "Store domain detection results and triggered conditionals"

  information_areas:
    1. Core Product Identity:
       expected_info: "Product concept, problem solved, target users, and basic value proposition"
       purpose: "Define what the product is and who it serves"

    2. Application Scope:
       expected_info: "Platform type (web/mobile/desktop), user interactions, and core features"
       purpose: "Determine technical architecture and development approach"

    3. Data & Content:
       expected_info: "Type of data stored, user-generated content, expected scale, and data relationships"
       purpose: "Choose database technology and data architecture"

    # SAVE PROGRESS: Write areas 1-4 to requirements-interview.md

    4. User Authentication & Security:
       expected_info: "Login approach, user roles, sensitive data, and security requirements"
       purpose: "Design authentication system and security measures"

    5. Service Integrations & APIs:
       expected_info: "Core services (payments, auth, storage), communication (email, SMS, push), analytics (tracking, reporting), monitoring (logs, errors), social platforms, marketplace APIs, webhook systems, third-party SaaS integrations"
       purpose: "Design complete service integration architecture with failover and monitoring"

    6. Performance, Scale & SLA Requirements:
       expected_info: "Expected user volume, concurrent users, SLA requirements (uptime, response time), peak load patterns, geographical distribution, caching needs, CDN requirements, performance budgets"
       purpose: "Choose hosting, database, scaling strategies and define performance architecture with measurable targets"

    # SAVE PROGRESS: Write areas 5-8 to requirements-interview.md

    7. Development Context:
       expected_info: "Team size, technical skills, timeline, and maintenance plans"
       purpose: "Select appropriate technology complexity and development tools"

    8. Quality & Reliability:
       expected_info: "Testing needs, monitoring requirements, error handling preferences"
       purpose: "Design testing strategy and operational monitoring"

    9. Deployment & Operations:
       expected_info: "Hosting preferences, deployment automation, environment needs"
       purpose: "Configure infrastructure and DevOps pipeline"

    # SAVE PROGRESS: Write areas 9-13 and finalize requirements-interview.md

    10. Business Model:
        expected_info: "Revenue model, compliance requirements, business constraints"
        purpose: "Ensure technical choices align with business needs"

    11. User Experience:
        expected_info: "User technical level, device support, accessibility needs, design preferences"
        purpose: "Guide frontend technology and UX approach"

    12. Project Success:
        expected_info: "Success metrics, launch timeline, post-launch evolution plans"
        purpose: "Set appropriate technical foundation for growth"

    13. Technical Constraints & Legacy Systems:
        expected_info: "Legacy systems to integrate, existing tech stack, migration needs, compliance frameworks, technical debt, platform constraints"
        purpose: "Identify integration challenges and technical constraints early to avoid architectural conflicts"

CONDITIONAL_AREAS:
  risk_management:
    trigger: "IF project_maturity IN ['enterprise', 'production_ready']"
    expected_info: "Technical risks (security, scalability, vendor lock-in), legal risks (compliance, IP), business risks (market, timeline, budget), mitigation strategies"
    purpose: "Proactive risk identification and mitigation planning"

  stack_preferences:
    trigger: "IF user_exp_code = 'programmer' OR existing_team_detected = true"
    expected_info: "Preferred languages, frameworks, databases, cloud providers, existing team expertise, technology constraints, learning curve considerations"
    purpose: "Align technology choices with team capabilities and preferences"

  compliance_deep:
    trigger: "IF project_maturity = 'enterprise' OR domain IN ['fintech', 'healthcare', 'education'] OR handles_sensitive_data = true"
    expected_info: "Specific regulations (GDPR, HIPAA, PCI-DSS, FERPA), audit requirements, data residency, retention policies, access controls"
    purpose: "Ensure full regulatory compliance from architecture design"

  licensing_ip:
    trigger: "IF project_maturity IN ['enterprise', 'production_ready'] OR commercial_product = true"
    expected_info: "Open source policy, proprietary constraints, third-party license compatibility, patent considerations, IP ownership requirements"
    purpose: "Avoid legal issues and ensure license compliance"

SPECIALIST_CONSULTATION:
  process: Claude analyzes all answers from requirements-interview.md
  action: Consult relevant specialists based on responses
  execution:
    - Use Task tool for PARALLEL consultation when specialists are independent
    - Use sequential if one specialist's response is needed for another's question
    - Apply logic to determine dependencies between consultations
  examples:
    - "React + PostgreSQL + Auth0" → @frontend.react, @database.postgres, @service.auth (parallel)
    - "Vue + MongoDB + Stripe" → @frontend.vue, @database.mongodb, @business.payment (parallel)
  storage: Append specialist recommendations to requirements-interview.md

PLAN_STRATEGY_ORGANIZATION:
  agent: @plan.strategy
  input: All interview answers + specialist recommendations
  output:
    - Complete project plan with phases and timeline
    - Same 6 documentation files in .claude/project/
    - Jobs created in SQLite database
    - Roadmap.md fully populated with executable phases
```

---

**⚠️ IMPORTANT**: After Phase 2, @setup.infrastructure will report any missing dependencies (🚨 MISSING DEPENDENCIES).
If dependencies are missing (npm install, Docker, database clients), ask the user for permission to install them.
Do NOT proceed to Phase 3 until critical dependencies are installed or user explicitly says to skip.

---

### 3️⃣ **PHASE 3: CLAUDE.MD CREATION**

**WHAT YOU (CLAUDE) MUST DO**: Generate a customized CLAUDE.md file using the template and documentation from Phase 2. Fill all template placeholders with project-specific information following the specifications below.

```yaml
CLAUDE_MD_GENERATION:
  source: Aggregated information from Phase 2
  template: ~/.claude/resources/templates/claude-template.md
  destination: [PROJECT_ROOT]/CLAUDE.md

  context_lite_generation:
    existing_projects: "{{context_lite}} → generated by @setup.context during Phase 2 analysis"
    new_projects: "{{context_lite}} → generated by Claude from interview + specialist recommendations"
    format: "3-4 paragraph executive summary (200-300 words max)"
    content:
      - "Project purpose and core value proposition"
      - "Key technical decisions and architecture approach"
      - "Current development phase and priorities"
      - "Critical constraints or special considerations"

  roadmap_handling:
    existing_projects: "{{roadmap_summary}} resolved in Phase 6 based on user roadmap decision"
    new_projects: "{{roadmap_summary}} from plan.strategy generated roadmap.md"

  user_placeholders:
    - {{project_maturity}} → from PROJECT_MATURITY_CLASSIFICATION
    - {{project_maturity_description}} → expanded description of maturity level
    - {{user_exp_code}} → from USER_CLASSIFICATION
    - {{user_exp_code_description}} → expanded description of user type
    - {{interaction_style}} → derived from user_exp_code (simple/technical language)
    - {{technical_depth}} → derived from user_exp_code (high/low technical detail)
    - {{decision_making_approach}} → derived from user_exp_code (autonomous/collaborative)

  project_placeholders:
    - {{project_name}} → from area 1 (Core Product Identity)
    - {{project_description}} → from vision.md summary
    - {{project_domain}} → detected from areas 1-2 (fintech, healthcare, etc.)
    - {{target_users}} → from area 1 (Core Product Identity)
    - {{tech_stack}} → from architecture.md primary technologies
    - {{architecture_approach}} → from architecture.md (monolith/microservices/etc.)
    - {{database_choice}} → from area 3 + specialist consultation
    - {{hosting_platform}} → from area 9 + specialist recommendations

  context_placeholder:
    - {{context_lite}} → executive summary (3-4 paragraphs, 200-300 words)

  documentation_summaries:
    - {{vision_summary}} → 1-line summary from vision.md
    - {{architecture_summary}} → 1-line summary from architecture.md
    - {{roadmap_summary}} → conditional: from roadmap.md if exists, else "resolved in Phase 6 based on roadmap decision"
    - {{tech_decisions_summary}} → 1-line summary from technical-decisions.md
    - {{team_preferences_summary}} → 1-line summary from team-preferences.md
    - {{project_context_summary}} → 1-line summary from project-context.md

  agent_placeholders:
    - {{agents}} → planned/detected acolytes array
    - {{agent_example}} → primary agent for project domain
    - {{first_agent}}, {{second_agent}}, {{third_agent}} → example agents for parallel execution
```

### 4️⃣ **PHASE 4: JOBS & AGENT CREATION**

**WHAT YOU (CLAUDE) MUST DO**: Invoke the acolytes-creator specialist to create acolyte agents for each detected or planned module. The specialist handles template filling, file creation, and database registration. Follow the process below based on project type.

#### **FOR EXISTING PROJECTS**

```yaml
ACOLYTE_CREATION:
  - Create project-specific agents based on detected modules
  - execution: MULTIPLE TASK CALLS IN ONE MESSAGE with @setup.acolytes-creator
  - Example: acolyte.api, acolyte.auth, acolyte.frontend

MODULE_DIVISION_RULES:
  - Single agent: modules with ≤30 files
  - Multiple agents: modules with >30 files split into submodule agents
  - Submodule agent examples: acolyte.api-auth, acolyte.api-endpoints, acolyte.rag-retrieval, acolyte.rag-indexing
  - Naming pattern: acolyte.[module]-[submodule]

AGENT_STRUCTURE:
  location: .claude/agents/acolyte.[module].md or .claude/agents/acolyte.[module]-[submodule].md
  creation: Claude delegates to @setup.acolytes-creator with module/submodule information
  memory_initialization: Agents create their own 14 memory records when first executed
```

#### **FOR NEW PROJECTS**

```yaml
PLAN_EXECUTION:
  - Create acolytes based on planned architecture
  - Agent creation guided by plan.strategy module structure and component boundaries
  - execution: MULTIPLE TASK CALLS IN ONE MESSAGE with @setup.acolytes-creator

MODULE_DIVISION_RULES:
  - Apply same 30-file rule for planned modules
  - Submodule agent creation: acolyte.api-auth, acolyte.payment-processing, acolyte.user-profile
```

### ⚠️ MANDATORY: Restart Required After Phase 4

**CRITICAL**: Tell user: "Exit Claude CLI (CTRL+C twice), then write in Terminal `claude --dangerously-skip-permissions -c`"
**EXPLAIN**: The `-c` flag resumes this same conversation where we left off (not a new session)
**WAIT**: For user confirmation before continuing to Phase 5. This restart is to integrate the acolytes into my system

### 5️⃣ **PHASE 5: DEEP ANALYSIS & INITIALIZATION**

**WHAT YOU (CLAUDE) MUST DO**: Invoke all created acolytes in parallel batches of 10 maximum. For existing projects, acolytes analyze their modules and populate memories with discovered information. For new projects, acolytes populate memories with planned architecture documentation. Each acolyte follows their internal template instructions.

```yaml
ACOLYTE_ACTIVATION:
  existing_projects:
    - Claude invokes all acolytes in parallel (max 10 per batch)
    - Each acolyte performs deep analysis of their assigned module
    - Fill their 14 memory records with comprehensive knowledge
    - Update agents_memory table in SQLite with discovered information

  new_projects:
    - Claude invokes acolytes to review .claude/project/ documentation
    - Acolytes populate memories with planned architecture and expectations
    - Set up knowledge base for future module implementation
    - Prepare memory structures for development phase
```

### 6️⃣ **PHASE 6: FINALIZATION**

**WHAT YOU (CLAUDE) MUST DO**: Confirm successful setup completion and present a comprehensive system summary. For existing projects, guide the user through roadmap decisions explaining the job system. For new projects, prepare for development phase. Follow the finalization steps below understanding that the system ALWAYS requires an active job.

```yaml
COMPLETION_SUMMARY:
  - Confirm all documentation created in .claude/project/
  - Verify SQLite database populated with agents and memories
  - Present system summary to user
  - List available agents with their expertise areas
  - Show next steps for development

JOB_SYSTEM_CRITICAL_RULES:
  - "'Acolyte for Claude Code' CANNOT function without an active job"
  - "Each job should contain 4-5 sessions maximum for optimal context"
  - "After 2+ months in one job, context window becomes problematic"
  - "Jobs group related work sessions for better memory persistence"
  - "NEVER close a job without opening another"

ROADMAP_DECISION:
  existing_projects:
    prompt: "Setup complete! What's your approach for this project?"
    options:
      no_roadmap: "Let's work organically - no structured roadmap needed"
      create_roadmap: "I want to plan objectives and create a development roadmap"

    no_roadmap_action:
      - Create roadmap.md with: "[X] NO STRUCTURED ROADMAP FOR THIS PROJECT, FOR NOW."
      - Keep setup job active (system REQUIRES active job - fundamental rule)
      - EXPLAIN to user:
        * "The system uses jobs to organize work and maintain context between sessions"
        * "Each job should contain ~3-4 sessions to avoid context overflow"
        * "You can create new jobs anytime - just tell me what you want to work on"
        * "Example: 'Create a job for implementing authentication' or 'Create a job for bug fixes'"
        * "Jobs are flexible - the roadmap is optional guidance, not obligation"
      - Ready for ad-hoc development with job-based organization

    create_roadmap_action:
      - Collect user objectives and ideas
      - Organize by priority and visual milestones (dopamine-driven)
      - Negotiate timeline and structure with user
      - Create roadmap.md with structured phases
      - Create jobs in SQLite (all paused except first)
      - Mark setup job as complete, activate first roadmap job
      - Update CLAUDE.md: Replace {{roadmap_summary}} with actual roadmap summary
      - EXPLAIN: "Each roadmap phase becomes a job, but you can create additional jobs anytime"

JOB_MANAGEMENT_FLEXIBILITY:
  - User can create jobs anytime regardless of roadmap
  - When creating new job, Claude asks: "Should I pause the current job and switch to the new one?"
  - Multiple jobs can exist simultaneously (active/paused/completed)
  - Roadmap is a guide, not an obligation - adapt as needed
  - Use @plan.strategy to update/create roadmaps for existing projects

ROADMAP_COMPLETION_HANDLING:
  - When all roadmap jobs complete, options:
    * Create new roadmap with @plan.strategy
    * Create ad-hoc job for next feature/phase
    * Continue organically with user-defined jobs
  - CRITICAL: Never leave system without active job

NEXT_STEPS:
  existing_projects: "System ready - job structure explained - development can begin"
  new_projects: "Ready to begin development following the generated roadmap and job structure"
```

## 📁 **STRUCTURE CREATED BY /setup**

```
[PROJECT_ROOT]/
├── CLAUDE.md                       # PROJECT INSTRUCTIONS
├── .claude/
│   ├── project/                    # PROJECT DOCUMENTATION (NEW!)
│   │   ├── vision.md               # Project vision and business context
│   │   ├── architecture.md         # Technical decisions
│   │   ├── roadmap.md              # Development phases
│   │   ├── technical-decisions.md  # Rationale for choices
│   │   ├── team-preferences.md     # Standards and practices
│   │   └── project-context.md      # Specific project details
│   ├── agents/                     # ACOLYTES
│   │   ├── acolyte.[module].md     # One per detected/planned module
│   │   └── ...
│   └── memory/                     # PERSISTENT MEMORY
│       ├── chat/                   # Chat related memory
│       ├── acolytes/               # Acolyte related memory
│       └── project.db              # SQLite with agent memories, jobs, setup data
```

## 📊 **NEW VS EXISTING PROJECT COMPARISON**

| Phase | Existing Project             | New Project                             |
| ----- | ---------------------------- | --------------------------------------- |
| 1     | Environment + Database setup | Environment + Database setup            |
| 2     | 4 setup agents analyze code  | 14 interview rounds + specialists       |
| 3     | CLAUDE.md creation           | CLAUDE.md creation                      |
| 4     | Acolyte creation             | Jobs + acolyte creation via plan.strat. |
| 5     | Deep module analysis         | Agent initialization                    |
| 6     | Finalization summary         | Finalization summary                    |

**Key Difference**: Existing projects analyze what exists; new projects plan what will be built.

---

## ❌ **COMMON ERRORS**

- ❌ Running setup agents sequentially instead of parallel
- ❌ Not creating .claude/project/ documentation
- ❌ Asking user about language preferences (always English)
- ❌ Not creating SQLite database first
- ❌ Creating documentation in wrong location

---

## 🎯 **EXAMPLE EXECUTION**

```bash
User: /setup

Claude:
1. [Phase 1] Environment + Database setup ✅
2. [Phase 2]
   - IF existing project: "Analyze this project using 4 setup agents IN PARALLEL"
   - IF new project: "Starting requirements interview - Business & Domain questions"
   - Check for missing dependencies and install if needed ⚠️
3. [Phase 3] Generate CLAUDE.md with project context ✅
4. [Phase 4] Create acolytes + jobs (if new project) ✅
5. [Phase 5] Initialize agent memories ✅
6. [Phase 6] "✅ Setup complete: Acolytes for Claude Code ready with full documentation"
```

---

**THIS IS THE OFFICIAL FLOW. NO INTERPRETATIONS.**
