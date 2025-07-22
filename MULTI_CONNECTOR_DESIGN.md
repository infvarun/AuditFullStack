# Multi-Connector Architecture Design

## Problem Statement
Current design assumes one connector per tool type per CI (e.g., only one SQL Server per CI). In reality, organizations need multiple connectors of the same type:
- Production & Development SQL Servers
- Multiple Oracle databases (HR, Finance, Operations)
- Different Jira projects (Dev, QA, Security)
- Various ServiceNow instances (IT, HR, Facilities)

## Proposed Solution: Named Connectors with Specific Selection

### 1. Database Schema Changes

```sql
-- Enhanced tool_connectors table
CREATE TABLE tool_connectors (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    ci_id TEXT NOT NULL,
    connector_name TEXT NOT NULL,                -- "Production SQL Server", "HR Oracle DB"
    connector_type TEXT NOT NULL,               -- "SQL Server DB", "Oracle DB"
    configuration JSON NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT now(),
    UNIQUE(ci_id, connector_name)              -- Multiple per type, unique names per CI
);

-- Enhanced question_analyses table
ALTER TABLE question_analyses ADD COLUMN connector_id INTEGER;
-- connector_to_use now stores specific connector name, not just type
```

### 2. UI/UX Enhancements

#### Settings Page
- Allow creating multiple connectors per type
- Require unique, descriptive names: "Production SQL Server", "Dev SQL Server"
- Show connector type + name in listings

#### Step 3 (Question Analysis)
- **Current**: Shows "Available/Not Available" for tool type
- **Enhanced**: Shows dropdown of available connectors for selected tool type
- Example: Select "SQL Server DB" → Dropdown shows ["Production SQL Server", "Dev SQL Server", "Reporting SQL Server"]

### 3. Implementation Plan

#### Phase 1: Database Migration
```sql
-- Add connector_name column to existing table
ALTER TABLE tool_connectors ADD COLUMN connector_name TEXT;
UPDATE tool_connectors SET connector_name = connector_type || ' - ' || id;
ALTER TABLE tool_connectors ALTER COLUMN connector_name SET NOT NULL;

-- Remove old unique constraint, add new one
ALTER TABLE tool_connectors DROP CONSTRAINT IF EXISTS unique_ci_connector_type;
ALTER TABLE tool_connectors ADD CONSTRAINT unique_ci_connector_name UNIQUE(ci_id, connector_name);
```

#### Phase 2: Backend API Updates
```python
# POST /api/connectors - require connector_name
# GET /api/connectors/ci/{ciId} - return connectors with names
# Group by connector_type for frontend dropdown organization
```

#### Phase 3: Frontend Updates
```typescript
// Step 3: Enhanced connector selection
interface ConnectorSelection {
  toolType: string;           // "SQL Server DB"
  connectorId: number;        // Specific connector ID
  connectorName: string;      // "Production SQL Server"
}

// UI: Two-level selection
// 1. Tool Type dropdown: [SQL Server DB, Oracle DB, ...]
// 2. Connector dropdown: [Production SQL Server, Dev SQL Server, ...]
```

### 4. Example User Flow

1. **Settings**: Create connectors
   - "Production SQL Server" (SQL Server DB type)
   - "Dev SQL Server" (SQL Server DB type)
   - "HR Oracle DB" (Oracle DB type)

2. **Step 3**: Question analysis
   - Question about user access → Suggests "SQL Server DB"
   - User sees dropdown: ["Production SQL Server", "Dev SQL Server"]
   - User selects "Production SQL Server"
   - Analysis saves: toolSuggestion="SQL Server DB", connectorId=1, connectorName="Production SQL Server"

3. **Step 4**: Agent execution
   - Executes against specific "Production SQL Server" connector
   - No ambiguity about which database to query

### 5. Benefits

1. **Scalability**: Support unlimited connectors per type
2. **Clarity**: Users know exactly which system will be queried
3. **Flexibility**: Different questions can use different instances
4. **Traceability**: Audit logs show specific connectors used
5. **Realistic**: Matches actual enterprise environments

### 6. Migration Strategy

1. **Backward Compatibility**: Existing connectors get auto-generated names
2. **Gradual Rollout**: Old logic still works, new logic is additive
3. **User Communication**: Guide users to rename connectors meaningfully

## Implementation Priority: HIGH
This addresses a fundamental architectural limitation that will become more problematic as the system scales.