-- =====================================================
-- CA Audit Agent - Latest Database Schema (DDL)
-- Data Definition Language for Audit Data Collection Platform
-- Created: August 2025
-- Version: Latest with all current features
-- =====================================================

-- Drop existing tables in correct order (respects foreign key constraints)
DROP TABLE IF EXISTS veritas_conversations CASCADE;
DROP TABLE IF EXISTS context_documents CASCADE;
DROP TABLE IF EXISTS audit_results CASCADE;
DROP TABLE IF EXISTS agent_executions CASCADE;
DROP TABLE IF EXISTS question_analyses CASCADE;
DROP TABLE IF EXISTS data_collection_sessions CASCADE;
DROP TABLE IF EXISTS data_requests CASCADE;
DROP TABLE IF EXISTS tool_connectors CASCADE;
DROP TABLE IF EXISTS applications CASCADE;
DROP TABLE IF EXISTS sessions CASCADE;

-- Drop indexes if they exist
DROP INDEX IF EXISTS idx_applications_ci_id;
DROP INDEX IF EXISTS idx_applications_status;
DROP INDEX IF EXISTS idx_applications_created_at;
DROP INDEX IF EXISTS idx_data_requests_application_id;
DROP INDEX IF EXISTS idx_data_requests_file_type;
DROP INDEX IF EXISTS idx_data_requests_uploaded_at;
DROP INDEX IF EXISTS idx_tool_connectors_application_id;
DROP INDEX IF EXISTS idx_tool_connectors_ci_id;
DROP INDEX IF EXISTS idx_tool_connectors_connector_type;
DROP INDEX IF EXISTS idx_tool_connectors_status;
DROP INDEX IF EXISTS idx_question_analyses_application_id;
DROP INDEX IF EXISTS idx_question_analyses_question_id;
DROP INDEX IF EXISTS idx_question_analyses_tool_suggestion;
DROP INDEX IF EXISTS idx_data_collection_sessions_application_id;
DROP INDEX IF EXISTS idx_data_collection_sessions_status;
DROP INDEX IF EXISTS idx_agent_executions_application_id;
DROP INDEX IF EXISTS idx_agent_executions_question_id;
DROP INDEX IF EXISTS idx_agent_executions_tool_type;
DROP INDEX IF EXISTS idx_agent_executions_status;
DROP INDEX IF EXISTS idx_audit_results_application_id;
DROP INDEX IF EXISTS idx_audit_results_session_id;
DROP INDEX IF EXISTS idx_audit_results_category;
DROP INDEX IF EXISTS idx_context_documents_ci_id;
DROP INDEX IF EXISTS idx_context_documents_document_type;
DROP INDEX IF EXISTS idx_veritas_conversations_ci_id;
DROP INDEX IF EXISTS idx_veritas_conversations_conversation_id;
DROP INDEX IF EXISTS "IDX_session_expire";

-- =====================================================
-- SESSION MANAGEMENT (Required for Replit Auth)
-- =====================================================

CREATE TABLE sessions (
    sid VARCHAR NOT NULL COLLATE "default",
    sess JSON NOT NULL,
    expire TIMESTAMP(6) NOT NULL
);

ALTER TABLE sessions ADD CONSTRAINT sessions_pkey PRIMARY KEY (sid);

-- =====================================================
-- CORE AUDIT TABLES
-- =====================================================

-- Applications: Core audit application records
CREATE TABLE applications (
    id SERIAL PRIMARY KEY,
    audit_name TEXT NOT NULL,
    name TEXT NOT NULL,
    ci_id TEXT NOT NULL,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    settings JSON DEFAULT '{}',
    status TEXT DEFAULT 'In Progress',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
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
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Tool Connectors: External system integration configurations
CREATE TABLE tool_connectors (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    ci_id TEXT NOT NULL,
    connector_type TEXT NOT NULL,
    configuration JSON NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
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
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
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

-- =====================================================
-- VERITAS GPT & DOCUMENT MANAGEMENT TABLES  
-- =====================================================

-- Context Documents: Document upload and management for Veritas GPT
CREATE TABLE context_documents (
    id SERIAL PRIMARY KEY,
    ci_id TEXT NOT NULL,
    document_type TEXT NOT NULL, -- support_plan, design_diagram, additional_supplements, other
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    uploaded_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- Veritas Conversations: Chat conversation storage for Veritas GPT
CREATE TABLE veritas_conversations (
    id SERIAL PRIMARY KEY,
    ci_id TEXT NOT NULL,
    conversation_id TEXT NOT NULL,
    messages JSON NOT NULL DEFAULT '[]',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT NOW()
);

-- =====================================================
-- AI AGENT EXECUTION TABLES
-- =====================================================

-- Agent Executions: AI agent execution tracking and results
CREATE TABLE agent_executions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    question_id VARCHAR(255) NOT NULL,
    tool_type VARCHAR(100) NOT NULL,
    connector_id INTEGER NOT NULL REFERENCES tool_connectors(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    result TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tool_used VARCHAR(100),
    execution_details JSONB
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Session indexes
CREATE INDEX "IDX_session_expire" ON sessions (expire);

-- Applications indexes
CREATE INDEX idx_applications_ci_id ON applications(ci_id);
CREATE INDEX idx_applications_status ON applications(status);
CREATE INDEX idx_applications_created_at ON applications(created_at);

-- Data Requests indexes
CREATE INDEX idx_data_requests_application_id ON data_requests(application_id);
CREATE INDEX idx_data_requests_file_type ON data_requests(file_type);
CREATE INDEX idx_data_requests_uploaded_at ON data_requests(uploaded_at);

-- Tool Connectors indexes
CREATE INDEX idx_tool_connectors_application_id ON tool_connectors(application_id);
CREATE INDEX idx_tool_connectors_ci_id ON tool_connectors(ci_id);
CREATE INDEX idx_tool_connectors_connector_type ON tool_connectors(connector_type);
CREATE INDEX idx_tool_connectors_status ON tool_connectors(status);

-- Data Collection Sessions indexes
CREATE INDEX idx_data_collection_sessions_application_id ON data_collection_sessions(application_id);
CREATE INDEX idx_data_collection_sessions_status ON data_collection_sessions(status);

-- Question Analyses indexes
CREATE INDEX idx_question_analyses_application_id ON question_analyses(application_id);
CREATE INDEX idx_question_analyses_question_id ON question_analyses(question_id);
CREATE INDEX idx_question_analyses_tool_suggestion ON question_analyses(tool_suggestion);

-- Audit Results indexes
CREATE INDEX idx_audit_results_application_id ON audit_results(application_id);
CREATE INDEX idx_audit_results_session_id ON audit_results(session_id);
CREATE INDEX idx_audit_results_category ON audit_results(category);

-- Agent Executions indexes
CREATE INDEX idx_agent_executions_application_id ON agent_executions(application_id);
CREATE INDEX idx_agent_executions_question_id ON agent_executions(question_id);
CREATE INDEX idx_agent_executions_tool_type ON agent_executions(tool_type);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);

-- Context Documents indexes
CREATE INDEX idx_context_documents_ci_id ON context_documents(ci_id);
CREATE INDEX idx_context_documents_document_type ON context_documents(document_type);

-- Veritas Conversations indexes
CREATE INDEX idx_veritas_conversations_ci_id ON veritas_conversations(ci_id);
CREATE INDEX idx_veritas_conversations_conversation_id ON veritas_conversations(conversation_id);

-- =====================================================
-- UNIQUE CONSTRAINTS
-- =====================================================

-- Ensure unique application/question combinations
ALTER TABLE question_analyses 
ADD CONSTRAINT unique_application_question 
UNIQUE (application_id, question_id);

-- Ensure unique application/file_type combinations  
ALTER TABLE data_requests 
ADD CONSTRAINT unique_application_file_type 
UNIQUE (application_id, file_type);

-- Ensure unique ci_id/connector_type combinations
ALTER TABLE tool_connectors 
ADD CONSTRAINT unique_ci_connector_type 
UNIQUE (ci_id, connector_type);

-- Ensure unique ci_id/document_type/file_name combinations
ALTER TABLE context_documents 
ADD CONSTRAINT unique_ci_document_type 
UNIQUE (ci_id, document_type, file_name);

-- =====================================================
-- CHECK CONSTRAINTS AND BUSINESS RULES
-- =====================================================

-- Ensure valid connector types
ALTER TABLE tool_connectors 
ADD CONSTRAINT chk_connector_type 
CHECK (connector_type IN (
    'SQL Server Database', 
    'Oracle Database', 
    'Gnosis Document Repository', 
    'Jira', 
    'QTest', 
    'ServiceNow'
));

-- Ensure valid file types
ALTER TABLE data_requests 
ADD CONSTRAINT chk_file_type 
CHECK (file_type IN ('primary', 'followup'));

-- Ensure valid document types
ALTER TABLE context_documents 
ADD CONSTRAINT chk_document_type 
CHECK (document_type IN ('support_plan', 'design_diagram', 'additional_supplements', 'other'));

-- Ensure valid statuses
ALTER TABLE data_collection_sessions 
ADD CONSTRAINT chk_session_status 
CHECK (status IN ('pending', 'running', 'completed', 'failed'));

ALTER TABLE agent_executions 
ADD CONSTRAINT chk_execution_status 
CHECK (status IN ('pending', 'running', 'success', 'failed'));

ALTER TABLE audit_results 
ADD CONSTRAINT chk_result_status 
CHECK (status IN ('pending', 'completed', 'failed'));

ALTER TABLE applications 
ADD CONSTRAINT chk_application_status 
CHECK (status IN ('In Progress', 'Complete'));

-- Ensure progress is within valid range
ALTER TABLE data_collection_sessions 
ADD CONSTRAINT chk_progress_range 
CHECK (progress >= 0 AND progress <= 100);

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE sessions IS 'Session storage for Replit Auth authentication system';
COMMENT ON TABLE applications IS 'Core audit application records with metadata and settings';
COMMENT ON TABLE data_requests IS 'File upload tracking with Excel parsing results and question extraction';
COMMENT ON TABLE tool_connectors IS 'External system integration configurations for data collection';
COMMENT ON TABLE data_collection_sessions IS 'Progress tracking for automated data collection processes';
COMMENT ON TABLE question_analyses IS 'AI-powered question analysis with tool recommendations and reasoning';
COMMENT ON TABLE audit_results IS 'Final audit outcomes with document generation tracking';
COMMENT ON TABLE context_documents IS 'Document upload and management for Veritas GPT context-aware chat';
COMMENT ON TABLE veritas_conversations IS 'Chat conversation storage with message history and state persistence';
COMMENT ON TABLE agent_executions IS 'Individual AI agent executions with prompts, results, and execution tracking';

-- Key column comments
COMMENT ON COLUMN applications.ci_id IS 'Configuration Item ID for external system reference';
COMMENT ON COLUMN applications.status IS 'Audit status: In Progress or Complete';
COMMENT ON COLUMN data_requests.questions IS 'JSON array of parsed questions from Excel files';
COMMENT ON COLUMN data_requests.column_mappings IS 'JSON mapping of Excel columns to question fields';
COMMENT ON COLUMN tool_connectors.configuration IS 'JSON configuration for external system connections';
COMMENT ON COLUMN question_analyses.ai_prompt IS 'Generated AI prompt for question analysis';
COMMENT ON COLUMN question_analyses.connector_reason IS 'AI reasoning for tool recommendation';
COMMENT ON COLUMN data_collection_sessions.logs IS 'JSON array of execution logs and status updates';
COMMENT ON COLUMN agent_executions.result IS 'AI agent execution result or error message with analysis data';
COMMENT ON COLUMN agent_executions.execution_details IS 'JSONB with detailed execution metadata and confidence scores';
COMMENT ON COLUMN context_documents.document_type IS 'Document type: support_plan, design_diagram, additional_supplements, or other';
COMMENT ON COLUMN veritas_conversations.messages IS 'JSON array of conversation messages with timestamps and metadata';

-- =====================================================
-- SCHEMA VALIDATION QUERIES
-- =====================================================

-- Display created tables
SELECT 
    schemaname,
    tablename,
    tableowner,
    hasindexes,
    hasrules,
    hastriggers
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Display foreign key relationships
SELECT 
    tc.constraint_name,
    tc.table_name,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
    ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema = 'public'
ORDER BY tc.table_name;

-- Display indexes
SELECT 
    indexname,
    tablename,
    indexdef
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

\echo ''
\echo '============================================='
\echo 'CA Audit Agent Database Schema Created Successfully!'
\echo '============================================='
\echo ''
\echo 'Tables created:'
\echo '  ✅ sessions (Replit Auth support)'  
\echo '  ✅ applications (audit projects)'
\echo '  ✅ data_requests (file uploads & questions)'
\echo '  ✅ tool_connectors (system integrations)'
\echo '  ✅ data_collection_sessions (progress tracking)'
\echo '  ✅ question_analyses (AI analysis results)'
\echo '  ✅ audit_results (final outcomes)'
\echo '  ✅ context_documents (Veritas GPT docs)'
\echo '  ✅ veritas_conversations (chat history)'
\echo '  ✅ agent_executions (AI execution tracking)'
\echo ''
\echo 'Features:'
\echo '  ✅ Foreign key constraints'
\echo '  ✅ Unique constraints'
\echo '  ✅ Check constraints'
\echo '  ✅ Performance indexes'
\echo '  ✅ Business rule validation'
\echo ''
\echo 'Ready for data insertion with latest_dml.sql!'
\echo '============================================='