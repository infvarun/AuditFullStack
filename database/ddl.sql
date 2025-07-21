-- =====================================================
-- CA Audit Agent - Database Schema (DDL)
-- Data Definition Language for Audit Data Collection Platform
-- =====================================================

-- Drop existing tables in correct order (respects foreign key constraints)
DROP TABLE IF EXISTS audit_results CASCADE;
DROP TABLE IF EXISTS agent_executions CASCADE;
DROP TABLE IF EXISTS question_analyses CASCADE;
DROP TABLE IF EXISTS data_collection_sessions CASCADE;
DROP TABLE IF EXISTS data_requests CASCADE;
DROP TABLE IF EXISTS tool_connectors CASCADE;
DROP TABLE IF EXISTS applications CASCADE;

-- =====================================================
-- CORE TABLES
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
    enable_followup_questions BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT now()
);

-- Data Requests: File upload tracking and question parsing
CREATE TABLE data_requests (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    file_type TEXT DEFAULT 'primary',
    file_path TEXT,
    questions JSON NOT NULL,
    total_questions INTEGER NOT NULL,
    categories JSON NOT NULL,
    subcategories JSON NOT NULL,
    column_mappings JSON NOT NULL,
    uploaded_at TIMESTAMP DEFAULT now()
);

-- Tool Connectors: External system integration configurations
CREATE TABLE tool_connectors (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    ci_id TEXT NOT NULL,
    connector_type TEXT NOT NULL,
    configuration JSON NOT NULL,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT now()
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
    created_at TIMESTAMP DEFAULT now(),
    UNIQUE(application_id, question_id)
);

-- Data Collection Sessions: Progress tracking for data gathering
CREATE TABLE data_collection_sessions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER REFERENCES applications(id) ON DELETE CASCADE,
    status TEXT DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    logs JSON DEFAULT '[]',
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

-- Agent Executions: AI agent execution tracking and results
CREATE TABLE agent_executions (
    id SERIAL PRIMARY KEY,
    application_id INTEGER NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    question_id VARCHAR NOT NULL,
    tool_type VARCHAR NOT NULL,
    connector_id INTEGER NOT NULL REFERENCES tool_connectors(id) ON DELETE CASCADE,
    prompt TEXT NOT NULL,
    result TEXT,
    status VARCHAR DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    created_at TIMESTAMP DEFAULT now()
);

-- =====================================================
-- INDEXES FOR PERFORMANCE
-- =====================================================

-- Applications indexes
CREATE INDEX idx_applications_ci_id ON applications(ci_id);
CREATE INDEX idx_applications_created_at ON applications(created_at);

-- Data Requests indexes
CREATE INDEX idx_data_requests_application_id ON data_requests(application_id);
CREATE INDEX idx_data_requests_file_type ON data_requests(file_type);
CREATE INDEX idx_data_requests_uploaded_at ON data_requests(uploaded_at);

-- Tool Connectors indexes
CREATE INDEX idx_tool_connectors_application_id ON tool_connectors(application_id);
CREATE INDEX idx_tool_connectors_ci_id ON tool_connectors(ci_id);
CREATE INDEX idx_tool_connectors_connector_type ON tool_connectors(connector_type);

-- Question Analyses indexes
CREATE INDEX idx_question_analyses_application_id ON question_analyses(application_id);
CREATE INDEX idx_question_analyses_question_id ON question_analyses(question_id);
CREATE INDEX idx_question_analyses_tool_suggestion ON question_analyses(tool_suggestion);

-- Data Collection Sessions indexes
CREATE INDEX idx_data_collection_sessions_application_id ON data_collection_sessions(application_id);
CREATE INDEX idx_data_collection_sessions_status ON data_collection_sessions(status);

-- Agent Executions indexes
CREATE INDEX idx_agent_executions_application_id ON agent_executions(application_id);
CREATE INDEX idx_agent_executions_question_id ON agent_executions(question_id);
CREATE INDEX idx_agent_executions_tool_type ON agent_executions(tool_type);
CREATE INDEX idx_agent_executions_status ON agent_executions(status);

-- Audit Results indexes
CREATE INDEX idx_audit_results_application_id ON audit_results(application_id);
CREATE INDEX idx_audit_results_session_id ON audit_results(session_id);
CREATE INDEX idx_audit_results_category ON audit_results(category);

-- =====================================================
-- CONSTRAINTS AND BUSINESS RULES
-- =====================================================

-- Ensure valid connector types
ALTER TABLE tool_connectors 
ADD CONSTRAINT chk_connector_type 
CHECK (connector_type IN (
    'SQL Server DB', 
    'Oracle DB', 
    'Gnosis Document Repository', 
    'Jira', 
    'QTest', 
    'ServiceNow'
));

-- Ensure valid file types
ALTER TABLE data_requests 
ADD CONSTRAINT chk_file_type 
CHECK (file_type IN ('primary', 'followup'));

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

-- Ensure progress is within valid range
ALTER TABLE data_collection_sessions 
ADD CONSTRAINT chk_progress_range 
CHECK (progress >= 0 AND progress <= 100);

-- =====================================================
-- COMMENTS FOR DOCUMENTATION
-- =====================================================

COMMENT ON TABLE applications IS 'Core audit application records with metadata and settings';
COMMENT ON TABLE data_requests IS 'File upload tracking with Excel parsing results and question extraction';
COMMENT ON TABLE tool_connectors IS 'External system integration configurations for data collection';
COMMENT ON TABLE question_analyses IS 'AI-powered question analysis with tool recommendations and reasoning';
COMMENT ON TABLE data_collection_sessions IS 'Progress tracking for automated data collection processes';
COMMENT ON TABLE agent_executions IS 'Individual AI agent executions with prompts and results';
COMMENT ON TABLE audit_results IS 'Final audit outcomes with document generation tracking';

-- Column comments for key fields
COMMENT ON COLUMN applications.ci_id IS 'Configuration Item ID for external system reference';
COMMENT ON COLUMN applications.enable_followup_questions IS 'Flag to enable secondary question file uploads';
COMMENT ON COLUMN data_requests.questions IS 'JSON array of parsed questions from Excel files';
COMMENT ON COLUMN data_requests.column_mappings IS 'JSON mapping of Excel columns to question fields';
COMMENT ON COLUMN tool_connectors.configuration IS 'JSON configuration for external system connections';
COMMENT ON COLUMN question_analyses.ai_prompt IS 'Generated AI prompt for question analysis';
COMMENT ON COLUMN question_analyses.connector_reason IS 'AI reasoning for tool recommendation';
COMMENT ON COLUMN data_collection_sessions.logs IS 'JSON array of execution logs and status updates';
COMMENT ON COLUMN agent_executions.result IS 'AI agent execution result or error message';

-- =====================================================
-- SCHEMA VALIDATION
-- =====================================================

-- Verify all tables were created successfully
SELECT 
    schemaname,
    tablename,
    tableowner
FROM pg_tables 
WHERE schemaname = 'public'
ORDER BY tablename;

-- Verify foreign key relationships
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
ORDER BY tc.table_name;