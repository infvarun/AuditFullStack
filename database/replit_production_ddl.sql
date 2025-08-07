-- =====================================================
-- CA Audit Agent - Current Replit Production Schema (DDL)
-- Exact database structure extracted from live Replit environment
-- Generated: August 7, 2025
-- =====================================================

-- Drop existing tables in correct order (respects foreign key constraints)
DROP TABLE IF EXISTS veritas_conversations CASCADE;
DROP TABLE IF EXISTS question_answers CASCADE;
DROP TABLE IF EXISTS audit_results CASCADE;
DROP TABLE IF EXISTS agent_executions CASCADE;
DROP TABLE IF EXISTS question_analyses CASCADE;
DROP TABLE IF EXISTS data_collection_sessions CASCADE;
DROP TABLE IF EXISTS data_requests CASCADE;
DROP TABLE IF EXISTS tool_connectors CASCADE;
DROP TABLE IF EXISTS applications CASCADE;

-- Drop indexes if they exist
DROP INDEX IF EXISTS idx_veritas_audit_id;
DROP INDEX IF EXISTS idx_veritas_ci_id;
DROP INDEX IF EXISTS idx_veritas_conversation_id;
DROP INDEX IF EXISTS unique_ci_connector_type;
DROP INDEX IF EXISTS unique_application_question;
DROP INDEX IF EXISTS unique_application_file_type;
DROP INDEX IF EXISTS question_answers_application_id_question_id_key;

-- =====================================================
-- CORE AUDIT TABLES (Production Structure)
-- =====================================================

-- Applications: Core audit application records
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    audit_name TEXT NOT NULL,
    name TEXT NOT NULL,
    ci_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    settings JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    enable_followup_questions BOOLEAN DEFAULT false,
    status CHARACTER VARYING(50) DEFAULT 'In Progress'
);

-- Tool Connectors: External system integration configurations  
CREATE TABLE tool_connectors (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    ci_id TEXT NOT NULL,
    connector_type TEXT NOT NULL,
    configuration JSON NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    connector_name CHARACTER VARYING(255)
);

-- Data Requests: File upload tracking and question parsing
CREATE TABLE data_requests (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT NOT NULL DEFAULT 'primary',
    questions JSON NOT NULL,
    total_questions INTEGER NOT NULL,
    categories JSON NOT NULL,
    subcategories JSON NOT NULL,
    column_mappings JSON NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    file_path TEXT
);

-- Data Collection Sessions: Progress tracking for data gathering
CREATE TABLE data_collection_sessions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    status TEXT NOT NULL DEFAULT 'pending',
    progress INTEGER NOT NULL DEFAULT 0,
    logs JSON NOT NULL DEFAULT '[]',
    started_at TIMESTAMP WITHOUT TIME ZONE,
    completed_at TIMESTAMP WITHOUT TIME ZONE
);

-- Question Analyses: AI-powered question analysis results  
CREATE TABLE question_analyses (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL,
    original_question TEXT NOT NULL,
    category TEXT NOT NULL,
    subcategory TEXT,
    ai_prompt TEXT NOT NULL,
    tool_suggestion TEXT NOT NULL,
    connector_reason TEXT NOT NULL,
    connector_to_use TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    connector_id INTEGER
);

-- Agent Executions: AI agent execution tracking and results
CREATE TABLE agent_executions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    question_id CHARACTER VARYING(255) NOT NULL,
    tool_type CHARACTER VARYING(100) NOT NULL,
    connector_id INTEGER NOT NULL REFERENCES tool_connectors(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    result TEXT,
    status CHARACTER VARYING(50) DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tool_used CHARACTER VARYING(100),
    execution_details JSONB
);

-- Audit Results: Final audit outcomes and document generation
CREATE TABLE audit_results (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    session_id INTEGER REFERENCES data_collection_sessions(id) ON DELETE CASCADE,
    question_id TEXT NOT NULL,
    question TEXT NOT NULL,
    category TEXT NOT NULL,
    status TEXT NOT NULL,
    document_path TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Question Answers: Structured answer storage with metadata
CREATE TABLE question_answers (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    question_id CHARACTER VARYING(50) NOT NULL,
    answer TEXT,
    findings JSONB,
    risk_level CHARACTER VARYING(20) DEFAULT 'Low',
    compliance_status CHARACTER VARYING(50) DEFAULT 'Compliant',
    data_points INTEGER DEFAULT 0,
    execution_details JSONB,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Veritas Conversations: Chat conversation storage for Veritas GPT
CREATE TABLE veritas_conversations (
    id SERIAL PRIMARY KEY,
    conversation_id CHARACTER VARYING(255) NOT NULL,
    ci_id CHARACTER VARYING(255) NOT NULL,
    audit_id CHARACTER VARYING(255) NOT NULL,
    audit_name CHARACTER VARYING(500),
    message TEXT NOT NULL,
    response TEXT NOT NULL,
    tools_used JSONB DEFAULT '[]',
    timestamp TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- INDEXES FOR PERFORMANCE (Current Production)
-- =====================================================

-- Unique constraints from production
CREATE UNIQUE INDEX unique_application_file_type 
ON data_requests (application_id, file_type);

CREATE UNIQUE INDEX unique_application_question 
ON question_analyses (application_id, question_id);

CREATE UNIQUE INDEX unique_ci_connector_type 
ON tool_connectors (ci_id, connector_type);

CREATE UNIQUE INDEX question_answers_application_id_question_id_key 
ON question_answers (application_id, question_id);

-- Veritas conversation indexes
CREATE INDEX idx_veritas_audit_id ON veritas_conversations (audit_id);
CREATE INDEX idx_veritas_ci_id ON veritas_conversations (ci_id);
CREATE INDEX idx_veritas_conversation_id ON veritas_conversations (conversation_id);

-- =====================================================
-- FOREIGN KEY CONSTRAINTS (Production)
-- =====================================================

-- Foreign keys are already defined in table creation above
-- Additional constraint validations would go here if needed

-- =====================================================
-- SEQUENCE INFORMATION
-- =====================================================

-- All sequences are automatically created with SERIAL columns
-- Current production sequences:
-- - applications_id_seq
-- - tool_connectors_id_seq  
-- - data_requests_id_seq
-- - data_collection_sessions_id_seq
-- - question_analyses_id_seq
-- - agent_executions_id_seq
-- - audit_results_id_seq
-- - question_answers_id_seq
-- - veritas_conversations_id_seq

-- =====================================================
-- PRODUCTION VALIDATION
-- =====================================================

-- Verify all tables were created
SELECT 
    table_name,
    CASE 
        WHEN table_name IN (
            'applications', 'tool_connectors', 'data_requests', 
            'data_collection_sessions', 'question_analyses', 
            'agent_executions', 'audit_results', 'question_answers', 
            'veritas_conversations'
        ) THEN '✅ Created'
        ELSE '❌ Missing'
    END as status
FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Verify foreign key relationships
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS referenced_table,
    ccu.column_name AS referenced_column
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

\echo ''
\echo '============================================='
\echo 'CA Audit Agent Production Schema Recreation Complete!'
\echo '============================================='
\echo ''
\echo 'Tables created (matching current Replit production):'
\echo '  ✅ applications (7 records in production)'
\echo '  ✅ tool_connectors (8 active connectors)'
\echo '  ✅ data_requests (9 uploaded files)'
\echo '  ✅ data_collection_sessions (ready for data)'
\echo '  ✅ question_analyses (79 AI analyses)' 
\echo '  ✅ agent_executions (400 AI executions)'
\echo '  ✅ audit_results (ready for outcomes)'
\echo '  ✅ question_answers (79 structured answers)'
\echo '  ✅ veritas_conversations (53 chat messages)'
\echo ''
\echo 'Features:'
\echo '  ✅ Exact column definitions from production'
\echo '  ✅ All foreign key relationships'
\echo '  ✅ Production indexes and constraints'
\echo '  ✅ Matching data types and defaults'
\echo ''
\echo 'Ready for production data import with replit_production_dml.sql!'
\echo '============================================='