-- =====================================================
-- CA Audit Agent - Sample Data (DML)
-- Data Manipulation Language for Audit Data Collection Platform
-- =====================================================

-- Clear existing data (in correct order respecting foreign keys)
DELETE FROM audit_results;
DELETE FROM agent_executions;
DELETE FROM question_analyses;
DELETE FROM data_collection_sessions;
DELETE FROM data_requests;
DELETE FROM tool_connectors;
DELETE FROM applications;

-- Reset sequences
ALTER SEQUENCE applications_id_seq RESTART WITH 1;
ALTER SEQUENCE data_requests_id_seq RESTART WITH 1;
ALTER SEQUENCE tool_connectors_id_seq RESTART WITH 1;
ALTER SEQUENCE question_analyses_id_seq RESTART WITH 1;
ALTER SEQUENCE data_collection_sessions_id_seq RESTART WITH 1;
ALTER SEQUENCE agent_executions_id_seq RESTART WITH 1;
ALTER SEQUENCE audit_results_id_seq RESTART WITH 1;

-- =====================================================
-- SAMPLE APPLICATIONS
-- =====================================================

INSERT INTO applications (audit_name, name, ci_id, start_date, end_date, enable_followup_questions, settings) VALUES
-- Active Audit Applications
('Q2 2025 Financial Systems Audit', 'Financial Systems Q2', 'CI12345001', '2025-04-01', '2025-06-30', true, '{"audit_type": "financial", "priority": "high", "lead_auditor": "Sarah Johnson"}'),
('Security Compliance Review 2025', 'Security Compliance', 'CI12345002', '2025-01-01', '2025-12-31', true, '{"audit_type": "security", "priority": "critical", "lead_auditor": "Mike Chen"}'),
('Infrastructure Assessment H1', 'Infrastructure H1', 'CI12345003', '2025-01-01', '2025-06-30', false, '{"audit_type": "infrastructure", "priority": "medium", "lead_auditor": "Lisa Rodriguez"}'),
('Data Governance Review', 'Data Governance', 'CI12345004', '2025-03-01', '2025-08-31', true, '{"audit_type": "governance", "priority": "high", "lead_auditor": "David Kim"}'),
-- Completed Audit Applications
('ERP System Migration Audit', 'ERP Migration', 'CI12345005', '2024-10-01', '2024-12-31', false, '{"audit_type": "migration", "priority": "high", "lead_auditor": "Anna Walsh", "status": "completed"}');

-- =====================================================
-- SAMPLE TOOL CONNECTORS
-- =====================================================

INSERT INTO tool_connectors (application_id, ci_id, connector_type, configuration, status) VALUES
-- Financial Systems Connectors
(1, 'CI12345001', 'SQL Server DB', '{"server": "fin-db-prod.company.com", "database": "FinancialData", "port": 1433, "auth_method": "integrated"}', 'active'),
(1, 'CI12345001', 'Oracle DB', '{"server": "oracle-fin.company.com", "database": "FINPROD", "port": 1521, "service_name": "FINPROD"}', 'active'),
(1, 'CI12345001', 'ServiceNow', '{"instance": "company.service-now.com", "endpoint": "api/now/table/incident", "version": "v1"}', 'active'),

-- Security Compliance Connectors
(2, 'CI12345002', 'SQL Server DB', '{"server": "sec-db-prod.company.com", "database": "SecurityLogs", "port": 1433, "auth_method": "sql_auth"}', 'active'),
(2, 'CI12345002', 'Jira', '{"server": "company.atlassian.net", "project_key": "SEC", "api_version": "3"}', 'active'),
(2, 'CI12345002', 'Gnosis Document Repository', '{"server": "docs.company.com", "repository": "security-policies", "api_endpoint": "/api/v2/documents"}', 'active'),

-- Infrastructure Connectors
(3, 'CI12345003', 'Oracle DB', '{"server": "infra-oracle.company.com", "database": "INFRAPROD", "port": 1521, "service_name": "INFRAPROD"}', 'active'),
(3, 'CI12345003', 'ServiceNow', '{"instance": "company.service-now.com", "endpoint": "api/now/cmdb/ci", "version": "v1"}', 'active'),

-- Data Governance Connectors
(4, 'CI12345004', 'SQL Server DB', '{"server": "data-gov.company.com", "database": "DataCatalog", "port": 1433, "auth_method": "integrated"}', 'active'),
(4, 'CI12345004', 'QTest', '{"server": "company.qtestnet.com", "project_id": "12345", "api_version": "v3"}', 'active'),
(4, 'CI12345004', 'Gnosis Document Repository', '{"server": "docs.company.com", "repository": "data-governance", "api_endpoint": "/api/v2/documents"}', 'active');

-- =====================================================
-- SAMPLE DATA REQUESTS
-- =====================================================

INSERT INTO data_requests (application_id, file_name, file_size, file_type, file_path, questions, total_questions, categories, subcategories, column_mappings) VALUES
-- Financial Systems Data Request
(1, 'Financial_Audit_Questions_Q2_2025.xlsx', 245760, 'primary', 'uploads/audit_1_Financial_Systems_Q2/primary_20250721_143022_Financial_Audit_Questions_Q2_2025.xlsx', 
'[
    {"id": "Q001", "question": "What are the current account reconciliation procedures for cash accounts?", "category": "Financial Controls", "subcategory": "Cash Management"},
    {"id": "Q002", "question": "How are journal entries reviewed and approved?", "category": "Financial Controls", "subcategory": "Journal Entries"},
    {"id": "Q003", "question": "What access controls exist for the general ledger system?", "category": "Access Controls", "subcategory": "System Access"},
    {"id": "Q004", "question": "How often are account balances reviewed for accuracy?", "category": "Financial Controls", "subcategory": "Balance Review"},
    {"id": "Q005", "question": "What segregation of duties exists in the accounts payable process?", "category": "Process Controls", "subcategory": "Accounts Payable"}
]', 
5, 
'["Financial Controls", "Access Controls", "Process Controls"]', 
'["Cash Management", "Journal Entries", "System Access", "Balance Review", "Accounts Payable"]', 
'{"question_number": "A", "process": "B", "sub_process": "C", "question": "D"}'),

-- Security Compliance Data Request
(2, 'Security_Compliance_Audit_2025.xlsx', 189440, 'primary', 'uploads/audit_2_Security_Compliance/primary_20250721_143125_Security_Compliance_Audit_2025.xlsx',
'[
    {"id": "Q001", "question": "What password policies are currently enforced?", "category": "Identity Management", "subcategory": "Password Policies"},
    {"id": "Q002", "question": "How are privileged accounts monitored and reviewed?", "category": "Access Management", "subcategory": "Privileged Access"},
    {"id": "Q003", "question": "What incident response procedures are in place for security breaches?", "category": "Incident Management", "subcategory": "Security Incidents"},
    {"id": "Q004", "question": "How frequently are security awareness training sessions conducted?", "category": "Security Training", "subcategory": "Awareness Programs"},
    {"id": "Q005", "question": "What vulnerability scanning tools are used and how often?", "category": "Vulnerability Management", "subcategory": "Scanning Tools"}
]',
5,
'["Identity Management", "Access Management", "Incident Management", "Security Training", "Vulnerability Management"]',
'["Password Policies", "Privileged Access", "Security Incidents", "Awareness Programs", "Scanning Tools"]',
'{"question_number": "A", "process": "B", "sub_process": "C", "question": "D"}'),

-- Infrastructure Assessment Data Request
(3, 'Infrastructure_Assessment_H1_2025.xlsx', 167936, 'primary', 'uploads/audit_3_Infrastructure_H1/primary_20250721_143220_Infrastructure_Assessment_H1_2025.xlsx',
'[
    {"id": "Q001", "question": "What is the current server capacity utilization?", "category": "Capacity Management", "subcategory": "Server Utilization"},
    {"id": "Q002", "question": "How are system backups performed and tested?", "category": "Data Protection", "subcategory": "Backup Procedures"},
    {"id": "Q003", "question": "What network monitoring tools are implemented?", "category": "Network Management", "subcategory": "Monitoring Tools"},
    {"id": "Q004", "question": "How are software patches managed and deployed?", "category": "Change Management", "subcategory": "Patch Management"}
]',
4,
'["Capacity Management", "Data Protection", "Network Management", "Change Management"]',
'["Server Utilization", "Backup Procedures", "Monitoring Tools", "Patch Management"]',
'{"question_number": "A", "process": "B", "sub_process": "C", "question": "D"}');

-- =====================================================
-- SAMPLE QUESTION ANALYSES (AI Results)
-- =====================================================

INSERT INTO question_analyses (application_id, question_id, original_question, category, subcategory, ai_prompt, tool_suggestion, connector_reason, connector_to_use) VALUES
-- Financial Systems Question Analyses
(1, 'Q001', 'What are the current account reconciliation procedures for cash accounts?', 'Financial Controls', 'Cash Management',
'Analyze the account reconciliation procedures for cash accounts. Focus on identifying control processes, frequency, approval workflows, and documentation requirements.',
'SQL Server DB', 'Cash reconciliation procedures are typically documented in financial systems databases with transaction logs and approval workflows.', 'SQL Server DB'),

(1, 'Q002', 'How are journal entries reviewed and approved?', 'Financial Controls', 'Journal Entries',
'Examine journal entry review and approval processes. Look for segregation of duties, approval hierarchies, and audit trails.',
'SQL Server DB', 'Journal entry approval processes are maintained in financial databases with detailed audit trails and approval records.', 'SQL Server DB'),

(1, 'Q003', 'What access controls exist for the general ledger system?', 'Access Controls', 'System Access',
'Review access control mechanisms for the general ledger system including user permissions, role-based access, and access monitoring.',
'ServiceNow', 'Access control information is typically managed through ITSM systems that track user permissions and system access.', 'ServiceNow'),

-- Security Compliance Question Analyses
(2, 'Q001', 'What password policies are currently enforced?', 'Identity Management', 'Password Policies',
'Examine current password policy enforcement including complexity requirements, expiration periods, and policy compliance monitoring.',
'Gnosis Document Repository', 'Password policies are typically documented in policy repositories with detailed requirements and compliance procedures.', 'Gnosis Document Repository'),

(2, 'Q002', 'How are privileged accounts monitored and reviewed?', 'Access Management', 'Privileged Access',
'Review privileged account monitoring processes including access reviews, activity logging, and periodic recertification procedures.',
'SQL Server DB', 'Privileged account activity and reviews are logged in security databases with detailed audit trails and monitoring records.', 'SQL Server DB'),

(2, 'Q003', 'What incident response procedures are in place for security breaches?', 'Incident Management', 'Security Incidents',
'Analyze incident response procedures for security breaches including escalation processes, communication protocols, and documentation requirements.',
'Jira', 'Security incident response procedures are managed through ticketing systems that track incidents, responses, and resolution processes.', 'Jira');

-- =====================================================
-- SAMPLE DATA COLLECTION SESSIONS
-- =====================================================

INSERT INTO data_collection_sessions (application_id, status, progress, logs, started_at, completed_at) VALUES
-- Completed Session
(1, 'completed', 100, 
'[
    {"timestamp": "2025-07-21T10:00:00Z", "message": "Data collection session started", "level": "info"},
    {"timestamp": "2025-07-21T10:05:00Z", "message": "Connected to SQL Server DB successfully", "level": "info"},
    {"timestamp": "2025-07-21T10:10:00Z", "message": "Processed 3 questions for Financial Controls", "level": "info"},
    {"timestamp": "2025-07-21T10:15:00Z", "message": "Connected to ServiceNow successfully", "level": "info"},
    {"timestamp": "2025-07-21T10:20:00Z", "message": "Processed 2 questions for Access Controls", "level": "info"},
    {"timestamp": "2025-07-21T10:25:00Z", "message": "Data collection completed successfully", "level": "success"}
]', 
'2025-07-21 10:00:00', '2025-07-21 10:25:00'),

-- In Progress Session
(2, 'running', 60,
'[
    {"timestamp": "2025-07-21T11:00:00Z", "message": "Data collection session started", "level": "info"},
    {"timestamp": "2025-07-21T11:05:00Z", "message": "Connected to SQL Server DB successfully", "level": "info"},
    {"timestamp": "2025-07-21T11:10:00Z", "message": "Processed 2 questions for Identity Management", "level": "info"},
    {"timestamp": "2025-07-21T11:15:00Z", "message": "Connected to Jira successfully", "level": "info"},
    {"timestamp": "2025-07-21T11:20:00Z", "message": "Processing Incident Management questions", "level": "info"}
]',
'2025-07-21 11:00:00', NULL),

-- Pending Session
(3, 'pending', 0, '[]', NULL, NULL);

-- =====================================================
-- SAMPLE AGENT EXECUTIONS
-- =====================================================

INSERT INTO agent_executions (application_id, question_id, tool_type, connector_id, prompt, result, status) VALUES
-- Financial Systems Executions
(1, 'Q001', 'SQL Server DB', 1, 
'Query the financial database to retrieve account reconciliation procedures for cash accounts. Focus on: 1) Reconciliation frequency, 2) Approval requirements, 3) Documentation standards, 4) Control processes.',
'{"reconciliation_frequency": "Daily", "approval_required": true, "documentation": "Standard templates used", "control_processes": ["Manager approval", "Supporting documentation", "Exception reporting"]}',
'success'),

(1, 'Q002', 'SQL Server DB', 1,
'Retrieve journal entry review and approval processes from the financial system. Include: 1) Approval hierarchy, 2) Segregation of duties, 3) Audit trail requirements.',
'{"approval_hierarchy": "Two-level approval required", "segregation_duties": "Preparer and approver must be different", "audit_trail": "Complete audit trail maintained with timestamps"}',
'success'),

(1, 'Q003', 'ServiceNow', 3,
'Query ServiceNow CMDB to identify access controls for the general ledger system. Include: 1) User roles, 2) Permission levels, 3) Access monitoring.',
'{"user_roles": ["GL_Viewer", "GL_Editor", "GL_Admin"], "permission_levels": "Role-based with principle of least privilege", "access_monitoring": "Monthly access reviews conducted"}',
'success'),

-- Security Compliance Executions
(2, 'Q001', 'Gnosis Document Repository', 6,
'Retrieve current password policy documentation including complexity requirements, expiration settings, and enforcement procedures.',
'{"complexity_requirements": "Minimum 12 characters, mixed case, numbers, special chars", "expiration": "90 days", "enforcement": "Automated through Active Directory"}',
'success'),

(2, 'Q002', 'SQL Server DB', 4,
'Query security database for privileged account monitoring procedures including review frequency and access logging.',
'{"review_frequency": "Quarterly", "access_logging": "All privileged access logged and monitored", "recertification": "Annual recertification required"}',
'success'),

(2, 'Q003', 'Jira', 5,
'Search Jira for security incident response procedures and escalation processes.',
'{"response_time": "Within 4 hours for critical incidents", "escalation": "Defined escalation matrix with contact information", "documentation": "All incidents documented in Jira"}',
'success');

-- =====================================================
-- SAMPLE AUDIT RESULTS
-- =====================================================

INSERT INTO audit_results (application_id, session_id, question_id, question, category, status, document_path) VALUES
-- Financial Systems Results
(1, 1, 'Q001', 'What are the current account reconciliation procedures for cash accounts?', 'Financial Controls', 'completed', 'uploads/audit_1_Financial_Systems_Q2/results/Q001_cash_reconciliation_analysis.pdf'),
(1, 1, 'Q002', 'How are journal entries reviewed and approved?', 'Financial Controls', 'completed', 'uploads/audit_1_Financial_Systems_Q2/results/Q002_journal_entry_controls.pdf'),
(1, 1, 'Q003', 'What access controls exist for the general ledger system?', 'Access Controls', 'completed', 'uploads/audit_1_Financial_Systems_Q2/results/Q003_gl_access_controls.pdf'),

-- Security Compliance Results
(2, 2, 'Q001', 'What password policies are currently enforced?', 'Identity Management', 'completed', 'uploads/audit_2_Security_Compliance/results/Q001_password_policy_review.pdf'),
(2, 2, 'Q002', 'How are privileged accounts monitored and reviewed?', 'Access Management', 'completed', 'uploads/audit_2_Security_Compliance/results/Q002_privileged_access_monitoring.pdf'),
(2, 2, 'Q003', 'What incident response procedures are in place for security breaches?', 'Incident Management', 'pending', 'uploads/audit_2_Security_Compliance/results/Q003_incident_response_procedures.pdf');

-- =====================================================
-- DATA VALIDATION QUERIES
-- =====================================================

-- Verify sample data was inserted correctly
SELECT 
    'applications' as table_name, 
    COUNT(*) as record_count 
FROM applications
UNION ALL
SELECT 
    'data_requests' as table_name, 
    COUNT(*) as record_count 
FROM data_requests
UNION ALL
SELECT 
    'tool_connectors' as table_name, 
    COUNT(*) as record_count 
FROM tool_connectors
UNION ALL
SELECT 
    'question_analyses' as table_name, 
    COUNT(*) as record_count 
FROM question_analyses
UNION ALL
SELECT 
    'data_collection_sessions' as table_name, 
    COUNT(*) as record_count 
FROM data_collection_sessions
UNION ALL
SELECT 
    'agent_executions' as table_name, 
    COUNT(*) as record_count 
FROM agent_executions
UNION ALL
SELECT 
    'audit_results' as table_name, 
    COUNT(*) as record_count 
FROM audit_results
ORDER BY table_name;

-- Show audit applications with their associated data
SELECT 
    a.id,
    a.audit_name,
    a.ci_id,
    COUNT(DISTINCT dr.id) as data_requests,
    COUNT(DISTINCT tc.id) as tool_connectors,
    COUNT(DISTINCT qa.id) as question_analyses,
    COUNT(DISTINCT ae.id) as agent_executions
FROM applications a
LEFT JOIN data_requests dr ON a.id = dr.application_id
LEFT JOIN tool_connectors tc ON a.id = tc.application_id
LEFT JOIN question_analyses qa ON a.id = qa.application_id
LEFT JOIN agent_executions ae ON a.id = ae.application_id
GROUP BY a.id, a.audit_name, a.ci_id
ORDER BY a.id;

-- =====================================================
-- HELPFUL QUERIES FOR DEVELOPMENT
-- =====================================================

-- Get complete audit application overview
/*
SELECT 
    a.audit_name,
    a.ci_id,
    a.start_date,
    a.end_date,
    dcs.status as session_status,
    dcs.progress,
    COUNT(DISTINCT qa.id) as analyzed_questions,
    COUNT(DISTINCT ae.id) as executed_questions,
    COUNT(DISTINCT ar.id) as completed_results
FROM applications a
LEFT JOIN data_collection_sessions dcs ON a.id = dcs.application_id
LEFT JOIN question_analyses qa ON a.id = qa.application_id
LEFT JOIN agent_executions ae ON a.id = ae.application_id
LEFT JOIN audit_results ar ON a.id = ar.application_id
GROUP BY a.id, a.audit_name, a.ci_id, a.start_date, a.end_date, dcs.status, dcs.progress
ORDER BY a.created_at DESC;
*/

-- Get question analysis results with tool recommendations
/*
SELECT 
    a.audit_name,
    qa.question_id,
    qa.original_question,
    qa.tool_suggestion,
    qa.connector_reason,
    ae.status as execution_status,
    ae.result as execution_result
FROM applications a
JOIN question_analyses qa ON a.id = qa.application_id
LEFT JOIN agent_executions ae ON qa.application_id = ae.application_id AND qa.question_id = ae.question_id
ORDER BY a.id, qa.question_id;
*/