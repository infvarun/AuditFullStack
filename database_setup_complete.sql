-- Complete Database Setup Script for CA Audit Agent
-- Created: August 2025
-- For local PostgreSQL database setup

-- Drop existing tables if they exist (in correct order due to foreign keys)
DROP TABLE IF EXISTS agent_executions CASCADE;
DROP TABLE IF EXISTS question_answers CASCADE;
DROP TABLE IF EXISTS question_analyses CASCADE;
DROP TABLE IF EXISTS tool_connectors CASCADE;
DROP TABLE IF EXISTS data_requests CASCADE;
DROP TABLE IF EXISTS audit_results CASCADE;
DROP TABLE IF EXISTS data_collection_sessions CASCADE;
DROP TABLE IF EXISTS applications CASCADE;

-- 1. Applications Table (Main audit projects)
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    audit_name TEXT NOT NULL,
    name TEXT NOT NULL,
    ci_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    settings JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    enable_followup_questions BOOLEAN DEFAULT FALSE,
    status VARCHAR(50) DEFAULT 'In Progress'
);

-- 2. Data Requests Table (File uploads and question parsing)
CREATE TABLE data_requests (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id),
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT NOT NULL DEFAULT 'primary',
    questions JSON NOT NULL,
    total_questions INTEGER NOT NULL,
    categories JSON NOT NULL,
    subcategories JSON NOT NULL,
    column_mappings JSON NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    file_path TEXT,
    CONSTRAINT unique_application_file_type UNIQUE (application_id, file_type)
);

-- 3. Question Analyses Table (AI-powered question analysis)
CREATE TABLE question_analyses (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id),
    question_id TEXT NOT NULL,
    original_question TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    ai_prompt TEXT NOT NULL,
    tool_suggestion TEXT NOT NULL,
    connector_reason TEXT NOT NULL,
    connector_to_use TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    connector_id INTEGER,
    CONSTRAINT unique_application_question UNIQUE (application_id, question_id)
);

-- 4. Tool Connectors Table (External system integrations)
CREATE TABLE tool_connectors (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id),
    ci_id TEXT NOT NULL,
    connector_type TEXT NOT NULL,
    configuration JSON NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    connector_name VARCHAR(255),
    CONSTRAINT unique_ci_connector_type UNIQUE (ci_id, connector_type)
);

-- 5. Question Answers Table (AI agent execution results)
CREATE TABLE question_answers (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id),
    question_id VARCHAR(50) NOT NULL,
    answer TEXT,
    findings JSONB,
    risk_level VARCHAR(20) DEFAULT 'Low',
    compliance_status VARCHAR(50) DEFAULT 'Compliant',
    data_points INTEGER DEFAULT 0,
    execution_details JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT question_answers_application_id_question_id_key UNIQUE (application_id, question_id)
);

-- 6. Agent Executions Table (Execution tracking)
CREATE TABLE agent_executions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES applications(id),
    question_id VARCHAR(255) NOT NULL,
    tool_type VARCHAR(100) NOT NULL,
    connector_id INTEGER NOT NULL REFERENCES tool_connectors(id),
    prompt TEXT NOT NULL,
    result TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tool_used VARCHAR(100),
    execution_details JSONB
);

-- 7. Audit Results Table (Final audit compilation)
CREATE TABLE audit_results (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id),
    session_id INTEGER REFERENCES data_collection_sessions(id),
    question_id TEXT NOT NULL,
    question TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL,
    document_path TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- 8. Data Collection Sessions Table (Session management)
CREATE TABLE data_collection_sessions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id),
    status TEXT NOT NULL DEFAULT 'pending',
    progress INTEGER NOT NULL DEFAULT 0,
    logs JSON NOT NULL DEFAULT '[]',
    started_at TIMESTAMP WITHOUT TIME ZONE,
    completed_at TIMESTAMP WITHOUT TIME ZONE
);

-- Create indexes for performance
CREATE INDEX idx_applications_ci_id ON applications(ci_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_question_analyses_application_id ON question_analyses(application_id);
CREATE INDEX idx_question_analyses_question_id ON question_analyses(question_id);
CREATE INDEX idx_question_answers_application_id ON question_answers(application_id);
CREATE INDEX idx_question_answers_question_id ON question_answers(question_id);
CREATE INDEX idx_tool_connectors_application_id ON tool_connectors(application_id);
CREATE INDEX idx_tool_connectors_ci_id ON tool_connectors(ci_id);
CREATE INDEX idx_tool_connectors_status ON tool_connectors(status);
CREATE INDEX idx_agent_executions_application_id ON agent_executions(application_id);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);

-- Insert demo data for testing
INSERT INTO applications (audit_name, name, ci_id, start_date, end_date, enable_followup_questions, status) VALUES
('Security Compliance Review 2025', 'Security Compliance Review', 'CI21345002', '2024-12-31', '2025-12-30', true, 'In Progress'),
('Infrastructure Assessment H1', 'Infrastructure Assessment', 'CI21345003', '2024-12-31', '2025-06-29', false, 'In Progress'),
('Stark G4 Q2CA2025', 'Stark G4', 'CI21324354', '2024-01-01', '2025-07-21', true, 'In Progress');

-- Insert demo tool connectors for CI21324354
INSERT INTO tool_connectors (application_id, ci_id, connector_type, configuration, status, connector_name) VALUES
(3, 'CI21324354', 'SQL Server Database', '{"server": "sql-prod-01.company.com", "database": "AuditDB", "integrated_auth": true}', 'active', 'Primary SQL Server'),
(3, 'CI21324354', 'Oracle Database', '{"host": "oracle-prod.company.com", "port": 1521, "service": "AUDIT", "schema": "COMPLIANCE"}', 'active', 'Oracle Compliance DB'),
(3, 'CI21324354', 'Gnosis Document Repository', '{"base_url": "https://gnosis.company.com", "access_level": "read-write", "document_types": ["policies", "procedures"]}', 'active', 'Corporate Document Store'),
(3, 'CI21324354', 'Jira', '{"base_url": "https://company.atlassian.net", "project_keys": ["AUDIT", "COMP"], "issue_types": ["Task", "Bug", "Story"]}', 'active', 'Audit Project Tracker'),
(3, 'CI21324354', 'QTest', '{"base_url": "https://company.qtestnet.com", "project_id": "12345", "cycle_name": "Q2_Audit_2025"}', 'active', 'Quality Test Management'),
(3, 'CI21324354', 'ServiceNow', '{"instance": "company.service-now.com", "table": "incident", "filter": "category=audit"}', 'active', 'IT Service Management');

-- Display setup completion message
\echo 'Database setup completed successfully!'
\echo 'Tables created:'
\echo '  - applications (audit projects)'
\echo '  - data_requests (file uploads)'
\echo '  - question_analyses (AI analysis)'
\echo '  - tool_connectors (system integrations)'
\echo '  - question_answers (execution results)'
\echo '  - agent_executions (execution tracking)'
\echo '  - audit_results (final compilation)'
\echo '  - data_collection_sessions (session management)'
\echo ''
\echo 'Demo data inserted for 3 applications with CI21324354 having 6 active connectors'
\echo 'Ready for CA Audit Agent application!'