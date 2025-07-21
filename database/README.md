# Database Scripts for CA Audit Agent

This directory contains the complete database schema and sample data for the CA Audit Agent application.

## Files Overview

- **`ddl.sql`** - Data Definition Language (Schema Creation)
- **`dml.sql`** - Data Manipulation Language (Sample Data)
- **`README.md`** - This documentation file

## Quick Setup

### 1. Create Database Schema
```sql
-- Run the DDL script to create all tables, indexes, and constraints
\i database/ddl.sql
```

### 2. Load Sample Data
```sql
-- Run the DML script to populate tables with realistic sample data
\i database/dml.sql
```

### 3. Verify Setup
```sql
-- Check that all tables were created
SELECT schemaname, tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename;

-- Verify data was loaded
SELECT 'applications' as table_name, COUNT(*) as records FROM applications
UNION ALL SELECT 'data_requests', COUNT(*) FROM data_requests
UNION ALL SELECT 'question_analyses', COUNT(*) FROM question_analyses
ORDER BY table_name;
```

## Database Schema Overview

### Core Tables

1. **applications** - Main audit application records
   - Primary key for all audit activities
   - Contains audit name, CI ID, date ranges, settings

2. **data_requests** - File upload and question parsing
   - Links to applications
   - Stores Excel file parsing results and extracted questions

3. **tool_connectors** - External system configurations
   - Defines connections to SQL Server, Oracle, Jira, etc.
   - Stores connection configurations and status

4. **question_analyses** - AI-powered question analysis
   - Links questions to recommended tools
   - Stores AI prompts and reasoning

5. **data_collection_sessions** - Progress tracking
   - Monitors data collection execution
   - Tracks progress and logs

6. **agent_executions** - Individual AI executions
   - Records each question processing attempt
   - Stores prompts and results

7. **audit_results** - Final audit outputs
   - Links to completed analyses
   - Tracks document generation

### Relationships

```
applications (1) → (many) data_requests
applications (1) → (many) tool_connectors  
applications (1) → (many) question_analyses
applications (1) → (many) data_collection_sessions
applications (1) → (many) agent_executions
applications (1) → (many) audit_results

tool_connectors (1) → (many) agent_executions
data_collection_sessions (1) → (many) audit_results
```

## Sample Data Included

### Applications (5 records)
- Financial Systems Q2 Audit
- Security Compliance Review  
- Infrastructure Assessment
- Data Governance Review
- ERP Migration Audit (completed)

### Tool Connectors (11 records)
- SQL Server DB connections
- Oracle DB connections
- ServiceNow integrations
- Jira project connections
- QTest configurations
- Gnosis document repositories

### Question Data
- 15+ sample questions across different audit categories
- AI analysis results with tool recommendations
- Agent execution records with realistic results
- Progress tracking data for active sessions

## Key Features

### Constraints and Validation
- Foreign key relationships maintain data integrity
- Check constraints ensure valid connector types and statuses
- Unique constraints prevent duplicate question analyses

### Performance Optimizations
- Indexes on frequently queried columns
- Optimized for application-based data retrieval
- JSON column indexing for question and configuration data

### Data Types
- **JSON columns** for flexible configuration and question storage
- **TEXT columns** for large content (prompts, results)
- **TIMESTAMP columns** for audit trails
- **INTEGER sequences** for primary keys

## Useful Queries

### Application Overview
```sql
SELECT 
    a.audit_name,
    COUNT(DISTINCT qa.id) as questions_analyzed,
    COUNT(DISTINCT ae.id) as executions_completed,
    dcs.status as session_status,
    dcs.progress
FROM applications a
LEFT JOIN question_analyses qa ON a.id = qa.application_id
LEFT JOIN agent_executions ae ON a.id = ae.application_id  
LEFT JOIN data_collection_sessions dcs ON a.id = dcs.application_id
GROUP BY a.id, a.audit_name, dcs.status, dcs.progress
ORDER BY a.created_at DESC;
```

### Question Analysis Results
```sql
SELECT 
    a.audit_name,
    qa.original_question,
    qa.tool_suggestion,
    ae.status as execution_status
FROM applications a
JOIN question_analyses qa ON a.id = qa.application_id
LEFT JOIN agent_executions ae ON qa.application_id = ae.application_id 
    AND qa.question_id = ae.question_id
ORDER BY a.id, qa.question_id;
```

### Connector Status
```sql
SELECT 
    a.audit_name,
    tc.connector_type,
    tc.status,
    COUNT(ae.id) as executions_using_connector
FROM applications a
JOIN tool_connectors tc ON a.id = tc.application_id
LEFT JOIN agent_executions ae ON tc.id = ae.connector_id
GROUP BY a.audit_name, tc.connector_type, tc.status
ORDER BY a.audit_name, tc.connector_type;
```

## Maintenance

### Clean Up Test Data
```sql
-- Remove all data but keep schema
DELETE FROM audit_results;
DELETE FROM agent_executions;
DELETE FROM question_analyses;
DELETE FROM data_collection_sessions;
DELETE FROM data_requests;
DELETE FROM tool_connectors;
DELETE FROM applications;

-- Reset sequences
ALTER SEQUENCE applications_id_seq RESTART WITH 1;
-- ... (repeat for all sequences)
```

### Backup Data
```sql
-- Export specific application data
COPY (
    SELECT * FROM applications WHERE id = 1
) TO '/path/to/backup/applications.csv' CSV HEADER;
```

## Development Notes

- All tables use CASCADE delete to maintain referential integrity
- JSON columns contain structured data that matches frontend expectations
- Timestamp columns use proper timezone handling
- Foreign keys prevent orphaned records
- Sample data represents realistic audit scenarios

## Production Considerations

1. **Indexes**: Additional indexes may be needed based on query patterns
2. **Partitioning**: Consider partitioning large tables by date ranges
3. **Archiving**: Implement data retention policies for completed audits
4. **Monitoring**: Add logging tables for database operations
5. **Security**: Implement row-level security for multi-tenant scenarios