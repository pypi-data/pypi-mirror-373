# Acolytes for Claude Code Agents Routing Rules

## 🎯 Agent Routing Rules

**Critical:** Use these IF/THEN rules for precise agent selection. Each rule eliminates ambiguity and ensures 0% routing errors.

### 🎮 Coordinators (Strategy/Architecture)

| 🎆 **Domain**                  | 📝 **IF (technical conditions)**                                                    | 🎯 **THEN (agent)**          | 🚀 **Priority** |
| :----------------------------- | :---------------------------------------------------------------------------------- | :--------------------------- | :-------------: |
| **Backend Architecture**       | Choosing microservices/monolith; service mesh; service boundaries; scaling strategy | `coordinator.backend`        |   🎯 **Solo**   |
| **Data Architecture**          | Selecting SQL/NoSQL/Vector; data modeling; partitioning/sharding; E2E data flows    | `@coordinator.database`      |   🎯 **Solo**   |
| **DevOps Strategy**            | High-level CI/CD design; GitOps; releases; promotion policies                       | `coordinator.devops`         |   🎯 **Solo**   |
| **Frontend Architecture**      | Micro-frontends; design system; choosing React/Vue/Angular; global state            | `coordinator.frontend`       |   🎯 **Solo**   |
| **Infrastructure Multi-cloud** | AWS/Azure/GCP; load balancing, CDN, autoscaling; DR/BCP                             | `coordinator.infrastructure` |   🎯 **Solo**   |
| **Migration**                  | Modernization/rehosting/re-platforming; migration plans                             | `coordinator.migration`      |   🎯 **Solo**   |
| **Security Strategy**          | IAM/RBAC; compliance (SOC2/PCI/HIPAA); incident response                            | `coordinator.security`       |   🎯 **Solo**   |
| **Testing Strategy**           | Automation strategy; quality gates; test data management                            | `coordinator.testing`        |   🎯 **Solo**   |

#### 🎆 **Golden Rule**

**IF choosing between technologies OR cross-domain decisions → Coordinator first; Specialist after (sequential).**

### 💻 Frontend Routing

| 🎆 **Domain**          | 📝 **IF (technical conditions)**                                                                                     | 🎯 **THEN (agent)**                                    | 🚀 **Priority**                |
| :--------------------- | :------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------- | :----------------------------- |
| **Angular**            | Angular 17+, NgRx, Angular Material/PrimeNG, complex forms                                                          | `@frontend.angular`                                    |     🎯 **Solo**                |
| **React**              | React 18+/Next.js, UI libs (MUI/Chakra/shadcn), React Query/Zustand                                                 | `@frontend.react`                                      |     🎯 **Solo**                |
| **Vue**                | Vue 3/Nuxt, Composition API, Pinia, Vuetify                                                                         | `@frontend.vue`                                        |     🎯 **Solo**                |
| **Mobile**             | React Native (New Architecture)/Flutter 3.24+/Expo SDK 52+/Capacitor 7+; app store publishing; EAS workflows      | `@frontend.mobile`                                     |     🎯 **Solo**                |
| **FE Architecture**    | Deciding framework/micro-frontends/design system/global state                                                       | `@coordinator.frontend` → `{angular/react/vue}`       | 🔄 **Sequential** (coordinator first) |

### 🖥️ Backend Routing

| 🎆 **Domain**           | 📝 **IF (technical conditions)**                                                           | 🎯 **THEN (agent)**                             | 🚀 **Priority**                       |
| :---------------------- | :----------------------------------------------------------------------------------------- | :---------------------------------------------- | :------------------------------------ |
| **Node.js**             | Express/Nest/Fastify; real-time (Socket.io); Prisma; JS microservices                     | `@backend.nodejs`                               |         🎯 **Solo**                   |
| **Python**              | Django/FastAPI/Flask; Celery/asyncio; data/ML backend                                      | `@backend.python`                               |         🎯 **Solo**                   |
| **Laravel/PHP**         | Laravel 11+, Eloquent, Livewire/Inertia, admin panels                                      | `@backend.laravel`                              |         🎯 **Solo**                   |
| **Go**                  | Gin/Echo/Fiber; gRPC; concurrency; performance                                             | `@backend.go`                                   |         🎯 **Solo**                   |
| **Java**                | Spring Boot/Cloud; enterprise/legacy; Gradle/Maven                                         | `@backend.java`                                 |         🎯 **Solo**                   |
| **Rust**                | Actix/Rocket/Axum; WASM; performance and memory safety                                     | `@backend.rust`                                 |         🎯 **Solo**                   |
| **API Architecture**    | REST/GraphQL/gRPC/WebSocket; versioning; gateways; governance                              | `@backend.api`                                  |         🎯 **Solo**                   |
| **Serverless/Edge**     | Lambda/Vercel/Netlify/Workers; FaaS; events                                                | `@backend.serverless`                           |         🎯 **Solo**                   |
| **BE Architecture**     | Choose pattern (micro/mono), partition services, SLAs, mesh                                | `@coordinator.backend` → `backend.{stack}`     | 🔄 **Sequential** (coordinator first) |

### 💾 Database and Data Routing

| 🎆 **Domain**                      | 📝 **IF (technical conditions)**                                                                            | 🎯 **THEN (agent)**                                 | 🚀 **Priority**                         |
| :--------------------------------- | :------------------------------------------------------------------------------------------------------- | :-------------------------------------------------- | :-------------------------------------- |
| **Postgres (OLTP/TS/Geo)**         | GiST/GIN/BRIN indices; Timescale; Citus; OLTP; geospatial                                               | `@database.postgres`                                |         🎯 **Solo**                     |
| **pgvector (AI Search)**           | RAG with PostgreSQL; embeddings in Postgres; similarity search with SQL                                 | `@database.pgvector`                                |         🎯 **Solo**                     |
| **Postgres + Vector**              | OLTP + semantic search in same database                                                                 | `@database.postgres` ∥ `@database.pgvector`        | 🔄 **Parallel** (or Sequential by task) |
| **MongoDB**                        | Documents; aggregations; sharding; change streams                                                       | `@database.mongodb`                                 |         🎯 **Solo**                     |
| **MariaDB**                        | Galera/MaxScale; MySQL migration; ColumnStore analytics                                                 | `@database.mariadb`                                 |         🎯 **Solo**                     |
| **Redis**                          | Cache/JSON/Streams; rate-limiting; session store; pub/sub                                               | `@database.redis`                                   |         🎯 **Solo**                     |
| **SQLite (edge)**                  | Local-first; serverless; FTS5; WAL; Litestream                                                          | `@database.sqlite`                                  |         🎯 **Solo**                     |
| **Vector Databases (Multiple)**    | Vector database platforms: Weaviate, Pinecone, Qdrant, Chroma, Milvus, pgvector, MongoDB Atlas         | `@database.vectorial`                               |         🎯 **Solo**                     |
| **PostGIS**                        | GIS queries; routing; spatial analysis                                                                  | `@database.postgis`                                 |         🎯 **Solo**                     |
| **Data Architecture**              | DB selection; models; flows; analytical vs transactional                                                | `@coordinator.database` → `{db.*}`                 | 🔄 **Sequential** (coordinator first)   |

### 🧩 Services Routing

| 🎆 **Domain**                | 📝 **IF (technical conditions)**                                                      | 🎯 **THEN (agent)**                                | 🚀 **Priority**                |
| :--------------------------- | :------------------------------------------------------------------------------------ | :-------------------------------------------------- | :----------------------------- |
| **Auth**                     | OAuth2/JWT/SSO/MFA/RBAC; Auth0/Firebase Auth; OIDC/SAML flows                        | `@service.auth`                                     |         🎯 **Solo**            |
| **External Integrations**    | SDKs/3rd party APIs; rate-limiting; scraping (Playwright/Selenium)                   | `@service.integrations`                             |         🎯 **Solo**            |
| **Mixed Auth + SDK**         | OAuth/SSO + external API consumption                                                 | `@service.auth` → `@service.integrations`          | 🔄 **Sequential** (Auth first) |
| **AI/ML in Product**         | OpenAI/HF/LangChain; model deployment; fine-tuning; AI pipelines; chatbots           | `@service.ai`                                       |         🎯 **Solo**            |
| **Communication**            | Twilio/SendGrid; email/SMS/push; templates; webhooks                                 | `@service.communication`                            |         🎯 **Solo**            |
| **Data Infra (services)**    | Kafka/RabbitMQ; Airflow/ETL; Elasticsearch; queues/streaming                         | `@service.data`                                     |         🎯 **Solo**            |
| **Maps**                     | Mapbox GL/Navigation; geocoding/routing/geofencing                                   | `@service.mapbox`                                   |         🎯 **Solo**            |

### 💼 Business Routing

| 🎆 **Domain**                    | 📝 **IF (technical conditions)**                                      | 🎯 **THEN (agent)**                                                       | 🚀 **Priority**                                    |
| :------------------------------- | :-------------------------------------------------------------------- | :------------------------------------------------------------------------- | :------------------------------------------------- |
| **Payments (transaction)**       | Stripe/PayPal/Square; 3DS; PCI; tokenization; fraud prevention       | `@business.payment`                                                        |         🎯 **Solo**                                |
| **Billing (invoices/taxes)**     | Invoices; taxes; dunning; revenue recognition                         | `@business.billing`                                                        |         🎯 **Solo**                                |
| **Subscriptions**                | Plans/usage-based; metering; churn; SaaS KPIs                         | `@business.subscription`                                                   |         🎯 **Solo**                                |
| **Complete Subscription**        | "Stripe subscription with invoicing and billing"                      | `@business.payment` ∥ `@business.billing` ∥ `@business.subscription`     | 🔄 **Parallel/Sequential** (coordinated by Claude) |

### ⚙️ Operations & DevOps Routing

| 🎆 **Domain**                   | 📝 **IF (technical conditions)**                                      | 🎯 **THEN (agent)**                          | 🚀 **Priority**                       |
| :------------------------------ | :--------------------------------------------------------------------- | :-------------------------------------------- | :------------------------------------ |
| **Git/Workflows**               | Branch strategies; hooks; LFS; PR reviews                             | `@ops.git`                                    |         🎯 **Solo**                   |
| **Monitoring/Observability**    | Prometheus/Grafana/ELK/APM; OTel; alerts                              | `@ops.monitoring`                             |         🎯 **Solo**                   |
| **Containers/K8s**              | Docker/Helm/Istio; ingress/registry; pod security                     | `@ops.containers`                             |         🎯 **Solo**                   |
| **Web Server/Proxy**            | Nginx/Apache/Caddy/HAProxy; TLS; LB; HTTP/3                           | `@ops.webserver`                              |         🎯 **Solo**                   |
| **CI/CD (tools)**               | Jenkins/GitLab CI/CircleCI/GHA; ArgoCD; pipelines                     | `@ops.cicd`                                   |         🎯 **Solo**                   |
| **IaC**                         | Terraform/Pulumi/Ansible/CFn; infrastructure automation               | `@ops.iac`                                    |         🎯 **Solo**                   |
| **Troubleshooting**             | Incidents; RCA; profiling; error tracking                             | `@ops.troubleshooting`                        |         🎯 **Solo**                   |
| **Performance**                 | Profiling; k6/JMeter; caching; DB tuning                              | `@ops.performance`                            |         🎯 **Solo**                   |
| **DevOps Strategy**             | Define standards, policies and CI/CD topology                         | `@coordinator.devops` → `{ops.*}`            | 🔄 **Sequential** (coordinator first) |

### 🔒 Anti-Ambiguity Rules (Operational Summary)

#### 1️⃣ **Strategy vs Execution**

- 🧠 IF task contains **"choose", "select", "compare", "decide", "architecture", "strategy"** → _Coordinator first_
- ⚙️ IF task contains **"implement", "configure", "optimize", "debug", "deploy", "code"** → _Specialist directly_
- 🔄 IF task contains **both strategy + implementation** → _Coordinator → Specialist_ (sequential)

#### 2️⃣ **RAG/Vector Search**

- 📊 IF RAG with PostgreSQL/existing OLTP → **database.pgvector**
- 📊 IF vector database (any platform) → **database.vectorial**
- 🤖 IF AI model integration/deployment → **service.ai**
- 🎨 IF RAG system design → **coordinator.database** → specific DB agent

#### 3️⃣ **Hybrid DB**

- 🔄 OLTP/Postgres + semantic search → _Postgres_ ∥ _pgvector_ in **parallel** (or sequential by dependency)

#### 4️⃣ **Auth vs Security Strategy**

- 🔐 IF **"implement authentication", "OAuth flows", "JWT", "login system"** → **service.auth**
- 🔒 IF **"security architecture", "compliance", "IAM strategy", "security policies"** → **coordinator.security**
- ⚙️ IF **"RBAC implementation"** → **service.auth** (tactical implementation)
- 🎨 IF **"design security model"** → **coordinator.security** → **service.auth** (sequential)

5. **Auth vs Integrations:** OAuth/SSO/JWT/MFA → **service.auth**; SDK/API consumption → **service.integrations**; if both, **Auth → Integrations** (sequential).
6. **Payments Suite:** Payment **business.payment**; invoices/taxes **business.billing**; recurrence **business.subscription**; if complete SaaS, invoke all three coordinated.
7. **Container Orchestration:** Docker/K8s → **ops.containers** ONLY; backend agents handle language-specific code, not infrastructure.
8. **Frontend vs Backend Confusion:**

   - IF **"React component", "Vue component", "UI element", "styling", "responsive design"** → **frontend.{framework}**
   - IF **"API endpoint", "database query", "business logic", "authentication middleware"** → **backend.{stack}**
   - IF **"full-stack feature"** → **backend.{stack}** → **frontend.{framework}** (sequential, backend first)

9. **Database Schema vs Query Optimization:**

   - IF **"design database", "create tables", "relationships", "migration"** → **database.{type}**
   - IF **"slow queries", "performance tuning", "indexes", "query optimization"** → **database.{type}** (same agent, different task)
   - IF **"choose database technology"** → **coordinator.database** → **database.{selected}**

10. **DevOps Strategy vs Tactical Implementation:**

    - IF **"CI/CD strategy", "deployment patterns", "release management"** → **coordinator.devops**
    - IF **"GitHub Actions workflow", "Docker compose", "Kubernetes manifest"** → **ops.{tool}**
    - IF **"implement monitoring"** → **ops.monitoring** directly

11. **API Design vs Integration:**

    - IF **"design REST API", "GraphQL schema", "API architecture"** → **backend.api**
    - IF **"consume external API", "third-party SDK", "webhook handling"** → **service.integrations**
    - IF **"API gateway configuration"** → **ops.webserver** or **coordinator.infrastructure**

12. **Testing Strategy vs Implementation:**

    - IF **"testing strategy", "quality gates", "test automation architecture"** → **coordinator.testing**
    - IF **"write unit tests", "configure Jest", "Cypress setup"** → **{specialist-agent}** (not test agent)
    - IF **"testing framework selection"** → **coordinator.testing** → **{specialist}**

13. **Security Architecture vs Implementation:**

    - IF **"security model", "compliance framework", "threat modeling"** → **coordinator.security**
    - IF **"implement 2FA", "OAuth setup", "JWT validation"** → **service.auth**
    - IF **"penetration testing", "vulnerability scan"** → **audit.security**

14. **Data Processing vs Storage:**

    - IF **"ETL pipeline", "data streaming", "message queues"** → **service.data**
    - IF **"database design", "data modeling", "storage optimization"** → **database.{type}**
    - IF **"analytics dashboard", "data visualization"** → **frontend.{framework}** + **service.data**

15. **Mobile vs Web Development:**

    - IF **"React Native", "Flutter", "iOS/Android", "app store"** → **frontend.mobile**
    - IF **"responsive web", "PWA", "browser compatibility"** → **frontend.{web-framework}**
    - IF **"mobile API", "push notifications"** → **backend.{stack}** + **service.communication**

16. **Infrastructure vs Application:**

    - IF **"server provisioning", "cloud architecture", "load balancing"** → **coordinator.infrastructure**
    - IF **"application deployment", "container orchestration"** → **ops.containers**
    - IF **"code optimization", "application performance"** → **{language-specialist}**

---

#### 1️⃣7️⃣ **Multi-Agent Workflows**

- 📜 **"Create user roles system"** → **coordinator.security** → **service.auth** → **database.{selected}** (sequential)
- 📦 **"Deploy web app in container"** → **ops.containers** ∥ **ops.webserver** (parallel)
- 🔍 **"GraphQL schema design"** → **backend.api** ONLY (no database involvement)
- ⚡ **"Optimize PostgreSQL performance"** → **database.postgres** ONLY (tactical optimization)
- 💳 **"Build e-commerce checkout"** → **business.payment** ∥ **business.billing** ∥ **frontend.{framework}** (parallel)
- 🔍 **"Implement search feature"** → **database.vectorial** → **backend.{stack}** → **frontend.{framework}** (sequential)

---

### 🎯 **Routing Quick Tips**

- **Strategy Decision** → Use **Coordinators** first
- **Direct Implementation** → Use **Specialists** directly
- **Multiple Domains** → Use **Parallel** execution
- **Sequential Dependencies** → Use **Sequential** workflow
- **Complex Features** → Follow **Multi-Agent Workflows**
