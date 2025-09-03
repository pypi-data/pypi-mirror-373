# System Architecture

## Architecture Pattern
- **Style**: [MONOLITH|MICROSERVICES|MODULAR_MONOLITH]
- **Pattern**: [MVC|CLEAN|LAYERED|HEXAGONAL]
- **Data Flow**: [UNIDIRECTIONAL|BIDIRECTIONAL]

## Project Structure
```
[PROJECT_NAME]/
├── src/
│   ├── [FRONTEND_DIR]/     # Frontend components
│   ├── [BACKEND_DIR]/      # Backend services
│   ├── shared/             # Shared utilities
│   └── types/              # Type definitions
├── tests/                  # Test files
├── docs/                   # Documentation
└── config/                 # Configuration files
```

## Module Boundaries
### Core Modules
- **[MODULE_1]**: [RESPONSIBILITY]
- **[MODULE_2]**: [RESPONSIBILITY]
- **[MODULE_3]**: [RESPONSIBILITY]

### Supporting Modules
- **[MODULE_4]**: [RESPONSIBILITY]
- **[MODULE_5]**: [RESPONSIBILITY]

## API Design
- **API Style**: [REST|GRAPHQL|RPC]
- **Endpoint Structure**: `/api/v1/[resource]`
- **Authentication**: [AUTH_METHOD]
- **Response Format**: JSON
- **Error Handling**: Consistent error responses

## Database Schema
### Core Entities
- **[ENTITY_1]**: [DESCRIPTION]
- **[ENTITY_2]**: [DESCRIPTION]
- **[ENTITY_3]**: [DESCRIPTION]

### Relationships
- [ENTITY_1] → [ENTITY_2]: [RELATIONSHIP_TYPE]
- [ENTITY_2] → [ENTITY_3]: [RELATIONSHIP_TYPE]

## Security Architecture
- **Authentication Flow**: [FLOW_DESCRIPTION]
- **Authorization**: [RBAC|PERMISSIONS]
- **Data Encryption**: [AT_REST|IN_TRANSIT]
- **Input Validation**: [VALIDATION_STRATEGY]

## Performance Considerations
- **Caching Strategy**: [CACHING_APPROACH]
- **Database Optimization**: [INDEXING|QUERIES]
- **CDN Usage**: [CDN_STRATEGY]
- **Code Splitting**: [SPLITTING_STRATEGY]

## Data Flow Diagrams
- **User Request Flow**: [FLOW_DESCRIPTION]
- **Authentication Flow**: [AUTH_FLOW]
- **Error Handling Flow**: [ERROR_FLOW]
- **Data Processing Flow**: [DATA_FLOW]

## Integration Points
- **External APIs**: [API_LIST_WITH_PURPOSE]
- **Webhook Endpoints**: [WEBHOOK_SPECS]
- **Background Jobs**: [JOB_QUEUE_STRATEGY]
- **Third-party Services**: [SERVICE_INTEGRATIONS]

## Development Standards
- **Code Style**: [STYLE_GUIDE]
- **Naming Conventions**: [CONVENTION_TYPE]
- **File Organization**: [ORGANIZATION_PATTERN]
- **Component Patterns**: [PATTERN_APPROACH]