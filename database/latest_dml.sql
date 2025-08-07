-- =====================================================
-- CA Audit Agent - Latest Sample Data (DML)
-- Data Manipulation Language for Audit Data Collection Platform
-- Created: August 2025
-- Version: Latest with all current features and realistic data
-- =====================================================

-- Clear existing data (in correct order respecting foreign keys)
DELETE FROM veritas_conversations;
DELETE FROM audit_results;
DELETE FROM question_answers;
DELETE FROM agent_executions;
DELETE FROM question_analyses;
DELETE FROM data_collection_sessions;
DELETE FROM data_requests;
DELETE FROM tool_connectors;
DELETE FROM applications;

-- Reset sequences to start from 1
ALTER SEQUENCE applications_id_seq RESTART WITH 1;
ALTER SEQUENCE data_requests_id_seq RESTART WITH 1;
ALTER SEQUENCE tool_connectors_id_seq RESTART WITH 1;
ALTER SEQUENCE data_collection_sessions_id_seq RESTART WITH 1;
ALTER SEQUENCE question_analyses_id_seq RESTART WITH 1;
ALTER SEQUENCE question_answers_id_seq RESTART WITH 1;
ALTER SEQUENCE audit_results_id_seq RESTART WITH 1;
ALTER SEQUENCE agent_executions_id_seq RESTART WITH 1;
ALTER SEQUENCE veritas_conversations_id_seq RESTART WITH 1;

-- =====================================================
-- SAMPLE APPLICATIONS (Realistic Audit Projects)
-- =====================================================

INSERT INTO applications (audit_name, name, ci_id, start_date, end_date, settings, enable_followup_questions, status) VALUES
-- Active Audit Applications with Enhanced Settings
('Q2 2025 Financial Systems Compliance Audit', 'Financial Systems Q2', 'CI21345001', '2025-04-01', '2025-06-30', 
'{"audit_type": "financial", "priority": "high", "lead_auditor": "Sarah Johnson", "team_size": 5, "budget": 150000, "compliance_frameworks": ["SOX", "COSO"]}', true, 'In Progress'),

('Security & Access Control Review 2025', 'Security Compliance Review', 'CI21345002', '2025-01-01', '2025-12-31', 
'{"audit_type": "security", "priority": "critical", "lead_auditor": "Mike Chen", "team_size": 8, "budget": 250000, "compliance_frameworks": ["ISO27001", "NIST"]}', true, 'In Progress'),

('Infrastructure & Change Management Assessment H1', 'Infrastructure Assessment H1', 'CI21345003', '2025-01-01', '2025-06-30', 
'{"audit_type": "infrastructure", "priority": "medium", "lead_auditor": "Lisa Rodriguez", "team_size": 4, "budget": 100000, "compliance_frameworks": ["ITIL", "COBIT"]}', false, 'In Progress'),

-- The Stark G4 audit with comprehensive tool integration (matches existing test data)
('Stark G4 Q2CA2025 Comprehensive Systems Audit', 'Stark G4 Comprehensive', 'CI21324354', '2025-01-01', '2025-07-21', 
'{"audit_type": "comprehensive", "priority": "critical", "lead_auditor": "David Kim", "team_size": 12, "budget": 500000, "compliance_frameworks": ["SOX", "ISO27001", "NIST", "COBIT"]}', true, 'In Progress'),

-- Completed audit example
('ERP System Migration & Data Governance Audit', 'ERP Migration Audit', 'CI21345005', '2024-10-01', '2024-12-31', 
'{"audit_type": "migration", "priority": "high", "lead_auditor": "Anna Walsh", "team_size": 6, "budget": 180000, "compliance_frameworks": ["SOX", "GDPR"], "completion_date": "2024-12-20"}', false, 'Complete');

-- =====================================================
-- SAMPLE TOOL CONNECTORS (Comprehensive Integration)
-- =====================================================

INSERT INTO tool_connectors (application_id, ci_id, connector_type, configuration, status, connector_name) VALUES
-- Financial Systems Connectors (App 1)
(1, 'CI21345001', 'SQL Server Database', 
'{"server": "fin-db-prod.company.com", "database": "FinancialData", "port": 1433, "auth_method": "integrated", "connection_timeout": 30}', 'active', 'Primary SQL Server'),

(1, 'CI21345001', 'Oracle Database', 
'{"server": "oracle-fin.company.com", "database": "FINPROD", "port": 1521, "service_name": "FINPROD", "schema": "FIN_AUDIT"}', 'active', 'Oracle Compliance DB'),

(1, 'CI21345001', 'ServiceNow', 
'{"instance": "company.service-now.com", "endpoint": "api/now/table/incident", "version": "v1", "authentication": "oauth2"}', 'active', 'IT Service Management'),

-- Security Compliance Connectors (App 2)
(2, 'CI21345002', 'SQL Server Database', 
'{"server": "sec-db-prod.company.com", "database": "SecurityLogs", "port": 1433, "auth_method": "sql_auth", "encryption": true}', 'active', 'Security Database'),

(2, 'CI21345002', 'Jira', 
'{"server": "company.atlassian.net", "project_key": "SEC", "api_version": "3", "authentication": "token", "issue_types": ["Bug", "Security Incident"]}', 'active', 'Audit Project Tracker'),

(2, 'CI21345002', 'Gnosis Document Repository', 
'{"server": "docs.company.com", "repository": "security-policies", "api_endpoint": "/api/v2/documents", "access_level": "read"}', 'active', 'Corporate Document Store'),

-- Infrastructure Assessment Connectors (App 3)
(3, 'CI21345003', 'Oracle Database', 
'{"server": "infra-oracle.company.com", "database": "INFRAPROD", "port": 1521, "service_name": "INFRAPROD", "monitoring": true}', 'active', 'Infrastructure Database'),

(3, 'CI21345003', 'ServiceNow', 
'{"instance": "company.service-now.com", "endpoint": "api/now/cmdb/ci", "version": "v1", "table": "cmdb_ci"}', 'active', 'CMDB Service'),

-- Stark G4 Comprehensive Connectors (App 4) - Matches test data structure
(4, 'CI21324354', 'SQL Server Database', 
'{"server": "sql-prod-01.company.com", "database": "AuditDB", "port": 1433, "integrated_auth": true, "connection_string": "trusted"}', 'active', 'Primary SQL Server'),

(4, 'CI21324354', 'Oracle Database', 
'{"host": "oracle-prod.company.com", "port": 1521, "service": "AUDIT", "schema": "COMPLIANCE", "connection_pool": true}', 'active', 'Oracle Compliance DB'),

(4, 'CI21324354', 'Gnosis Document Repository', 
'{"base_url": "https://gnosis.company.com", "access_level": "read-write", "document_types": ["policies", "procedures", "standards"]}', 'active', 'Corporate Document Store'),

(4, 'CI21324354', 'Jira', 
'{"base_url": "https://company.atlassian.net", "project_keys": ["AUDIT", "COMP", "STARK"], "issue_types": ["Task", "Bug", "Story", "Epic"]}', 'active', 'Audit Project Tracker'),

(4, 'CI21324354', 'QTest', 
'{"base_url": "https://company.qtestnet.com", "project_id": "12345", "cycle_name": "Q2_Audit_2025", "test_suites": ["Security", "Functional"]}', 'active', 'Quality Test Management'),

(4, 'CI21324354', 'ServiceNow', 
'{"instance": "company.service-now.com", "table": "incident", "filter": "category=audit", "additional_tables": ["change_request", "problem"]}', 'active', 'IT Service Management');

-- =====================================================
-- SAMPLE DATA REQUESTS (Realistic File Processing)
-- =====================================================

INSERT INTO data_requests (application_id, file_name, file_size, file_type, questions, total_questions, categories, subcategories, column_mappings, file_path) VALUES
-- Financial Systems Primary Questions
(1, 'Financial_Audit_Questions_Q2_2025.xlsx', 245760, 'primary', 
'[
    {"id": "Q001", "question": "What are the current account reconciliation procedures for cash accounts?", "category": "Financial Controls", "subcategory": "Cash Management"},
    {"id": "Q002", "question": "How are journal entries reviewed and approved in the general ledger?", "category": "Financial Controls", "subcategory": "Journal Entry Controls"},
    {"id": "Q003", "question": "What access controls exist for the financial reporting systems?", "category": "Access Controls", "subcategory": "System Access"},
    {"id": "Q004", "question": "How frequently are account balances reviewed for accuracy and completeness?", "category": "Financial Controls", "subcategory": "Balance Verification"},
    {"id": "Q005", "question": "What segregation of duties exists in the accounts payable process?", "category": "Process Controls", "subcategory": "Accounts Payable"},
    {"id": "Q006", "question": "How are month-end closing procedures documented and performed?", "category": "Process Controls", "subcategory": "Period Close"},
    {"id": "Q007", "question": "What controls exist over manual journal entries?", "category": "Financial Controls", "subcategory": "Manual Adjustments"}
]', 
7, 
'["Financial Controls", "Access Controls", "Process Controls"]', 
'["Cash Management", "Journal Entry Controls", "System Access", "Balance Verification", "Accounts Payable", "Period Close", "Manual Adjustments"]', 
'{"question_number": "A", "process": "B", "sub_process": "C", "question": "D", "control_objective": "E"}', 
'uploads/audit_1_Financial_Systems_Q2/primary_20250721_143022_Financial_Audit_Questions_Q2_2025.xlsx'),

-- Security Compliance Primary Questions  
(2, 'Security_Compliance_Audit_2025.xlsx', 189440, 'primary',
'[
    {"id": "Q001", "question": "What password policies are currently enforced across all systems?", "category": "Identity Management", "subcategory": "Password Policies"},
    {"id": "Q002", "question": "How are privileged accounts monitored and periodically reviewed?", "category": "Access Management", "subcategory": "Privileged Access"},
    {"id": "Q003", "question": "What incident response procedures are documented for security breaches?", "category": "Incident Management", "subcategory": "Security Incidents"},
    {"id": "Q004", "question": "How frequently are security awareness training sessions conducted?", "category": "Security Training", "subcategory": "Awareness Programs"},
    {"id": "Q005", "question": "What vulnerability scanning tools are implemented and how often are scans performed?", "category": "Vulnerability Management", "subcategory": "Scanning Tools"},
    {"id": "Q006", "question": "How are security patches tested and deployed across the environment?", "category": "Change Management", "subcategory": "Patch Management"}
]',
6,
'["Identity Management", "Access Management", "Incident Management", "Security Training", "Vulnerability Management", "Change Management"]',
'["Password Policies", "Privileged Access", "Security Incidents", "Awareness Programs", "Scanning Tools", "Patch Management"]',
'{"question_number": "A", "process": "B", "sub_process": "C", "question": "D", "control_type": "E"}',
'uploads/audit_2_Security_Compliance/primary_20250721_143125_Security_Compliance_Audit_2025.xlsx'),

-- Stark G4 Comprehensive Primary Questions (Matches enhanced sample sheets)
(4, 'SAMPLE_Primary_Audit_Questions_Enhanced.xlsx', 387264, 'primary',
'[
    {"id": "Q001", "question": "What user access controls are implemented in the SQL Server database?", "category": "Access Controls", "subcategory": "Database Security"},
    {"id": "Q002", "question": "How are database schema changes managed and approved?", "category": "Change Management", "subcategory": "Database Changes"},
    {"id": "Q003", "question": "What backup and recovery procedures are documented for critical systems?", "category": "Business Continuity", "subcategory": "Data Protection"},
    {"id": "Q004", "question": "How are security policies communicated and enforced organization-wide?", "category": "Policy Management", "subcategory": "Security Governance"},
    {"id": "Q005", "question": "What automated testing procedures are implemented for system changes?", "category": "Quality Assurance", "subcategory": "Test Automation"},
    {"id": "Q006", "question": "How are incidents tracked and resolved in the ServiceNow system?", "category": "Incident Management", "subcategory": "Ticket Processing"},
    {"id": "Q007", "question": "What change approval workflows exist in Jira for system modifications?", "category": "Change Management", "subcategory": "Approval Processes"},
    {"id": "Q008", "question": "How are test execution results documented and reviewed in QTest?", "category": "Quality Assurance", "subcategory": "Test Documentation"},
    {"id": "Q009", "question": "What data classification standards are maintained in Gnosis?", "category": "Data Governance", "subcategory": "Classification"},
    {"id": "Q010", "question": "How are Oracle database performance metrics monitored and reported?", "category": "Performance Management", "subcategory": "Database Monitoring"},
    {"id": "Q011", "question": "What segregation of duties exists between development and production environments?", "category": "Access Controls", "subcategory": "Environment Separation"},
    {"id": "Q012", "question": "How are critical system patches tested before production deployment?", "category": "Change Management", "subcategory": "Patch Testing"},
    {"id": "Q013", "question": "What audit trails are maintained for privileged user activities?", "category": "Audit & Logging", "subcategory": "Privileged Access Logging"},
    {"id": "Q014", "question": "How are business continuity plans tested and validated annually?", "category": "Business Continuity", "subcategory": "Plan Testing"}
]',
14,
'["Access Controls", "Change Management", "Business Continuity", "Policy Management", "Quality Assurance", "Incident Management", "Data Governance", "Performance Management", "Audit & Logging"]',
'["Database Security", "Database Changes", "Data Protection", "Security Governance", "Test Automation", "Ticket Processing", "Approval Processes", "Test Documentation", "Classification", "Database Monitoring", "Environment Separation", "Patch Testing", "Privileged Access Logging", "Plan Testing"]',
'{"question_number": "A", "process": "B", "sub_process": "C", "question": "D", "tool_used": "E", "priority": "F"}',
'uploads/audit_4_Stark_G4/primary_20250806_140000_SAMPLE_Primary_Audit_Questions_Enhanced.xlsx'),

-- Stark G4 Follow-up Questions
(4, 'SAMPLE_Followup_Audit_Questions_Enhanced.xlsx', 198432, 'followup',
'[
    {"id": "F001", "question": "What exceptions were identified in the user access review process?", "category": "Access Controls", "subcategory": "Access Review Exceptions"},
    {"id": "F002", "question": "How are emergency database changes documented and approved?", "category": "Change Management", "subcategory": "Emergency Changes"},
    {"id": "F003", "question": "What remediation actions were taken for identified security vulnerabilities?", "category": "Vulnerability Management", "subcategory": "Remediation Tracking"},
    {"id": "F004", "question": "How are test failures escalated and resolved in the QTest system?", "category": "Quality Assurance", "subcategory": "Failure Resolution"},
    {"id": "F005", "question": "What training completion rates exist for mandatory security awareness programs?", "category": "Training & Awareness", "subcategory": "Completion Tracking"},
    {"id": "F006", "question": "How are data retention policies enforced across different storage systems?", "category": "Data Governance", "subcategory": "Retention Management"},
    {"id": "F007", "question": "What performance issues were identified in the Oracle database monitoring?", "category": "Performance Management", "subcategory": "Issue Identification"}
]',
7,
'["Access Controls", "Change Management", "Vulnerability Management", "Quality Assurance", "Training & Awareness", "Data Governance", "Performance Management"]',
'["Access Review Exceptions", "Emergency Changes", "Remediation Tracking", "Failure Resolution", "Completion Tracking", "Retention Management", "Issue Identification"]',
'{"question_number": "A", "process": "B", "sub_process": "C", "question": "D", "follow_up_reason": "E"}',
'uploads/audit_4_Stark_G4/followup_20250806_141500_SAMPLE_Followup_Audit_Questions_Enhanced.xlsx');

-- =====================================================
-- SAMPLE QUESTION ANALYSES (AI Analysis Results)
-- =====================================================

INSERT INTO question_analyses (application_id, question_id, original_question, category, subcategory, ai_prompt, tool_suggestion, connector_reason, connector_to_use, connector_id) VALUES
-- Financial Systems Analyses
(1, 'Q001', 'What are the current account reconciliation procedures for cash accounts?', 'Financial Controls', 'Cash Management',
'Analyze account reconciliation procedures for cash accounts. Examine control processes, frequency requirements, approval workflows, exception handling, and documentation standards for cash reconciliations.',
'SQL Server Database', 'Cash reconciliation procedures and transaction details are typically stored in financial databases with comprehensive audit trails and approval records.', 'SQL Server Database', 1),

(1, 'Q002', 'How are journal entries reviewed and approved in the general ledger?', 'Financial Controls', 'Journal Entry Controls',
'Examine journal entry review and approval processes in the general ledger system. Focus on segregation of duties, approval hierarchies, supporting documentation requirements, and audit trail maintenance.',
'SQL Server Database', 'Journal entry approval workflows and audit trails are maintained in financial system databases with detailed approval records and supporting documentation.', 'SQL Server Database', 1),

-- Security Compliance Analyses
(2, 'Q001', 'What password policies are currently enforced across all systems?', 'Identity Management', 'Password Policies',
'Review current password policy enforcement including complexity requirements, expiration settings, account lockout policies, and compliance monitoring across all enterprise systems.',
'Gnosis Document Repository', 'Password policies and security standards are typically documented in enterprise document repositories with version control and approval workflows.', 'Gnosis Document Repository', 6),

(2, 'Q002', 'How are privileged accounts monitored and periodically reviewed?', 'Access Management', 'Privileged Access',
'Examine privileged account monitoring processes including access reviews, activity logging, recertification procedures, and exception reporting for elevated access rights.',
'SQL Server Database', 'Privileged account monitoring data, access logs, and review results are typically stored in security databases with comprehensive audit trails.', 'SQL Server Database', 4),

-- Stark G4 Comprehensive Analyses (Multi-tool scenarios)
(4, 'Q001', 'What user access controls are implemented in the SQL Server database?', 'Access Controls', 'Database Security',
'Analyze user access controls in SQL Server database including role-based permissions, authentication methods, access logging, and periodic access reviews.',
'SQL Server Database', 'Database access controls and user permissions are directly queryable from the SQL Server system with detailed role and permission information.', 'SQL Server Database', 9),

(4, 'Q005', 'What automated testing procedures are implemented for system changes?', 'Quality Assurance', 'Test Automation',
'Examine automated testing procedures for system changes including test case management, execution automation, result reporting, and integration with change management processes.',
'QTest', 'Automated testing procedures and test execution results are comprehensively managed in QTest with detailed test case documentation and execution history.', 'QTest', 13),

(4, 'Q006', 'How are incidents tracked and resolved in the ServiceNow system?', 'Incident Management', 'Ticket Processing',
'Review incident tracking and resolution processes in ServiceNow including ticket workflow, escalation procedures, SLA compliance, and resolution documentation.',
'ServiceNow', 'Incident tracking and resolution data is directly available in ServiceNow with comprehensive workflow history and performance metrics.', 'ServiceNow', 14),

(4, 'Q007', 'What change approval workflows exist in Jira for system modifications?', 'Change Management', 'Approval Processes',
'Analyze change approval workflows in Jira including approval hierarchies, review processes, documentation requirements, and change tracking mechanisms.',
'Jira', 'Change approval workflows and modification tracking are managed in Jira with detailed approval histories and change documentation.', 'Jira', 12);

-- =====================================================
-- SAMPLE DATA COLLECTION SESSIONS
-- =====================================================

INSERT INTO data_collection_sessions (application_id, status, progress, logs, started_at, completed_at) VALUES
-- Completed Financial Systems Session
(1, 'completed', 100, 
'[
    {"timestamp": "2025-07-21T09:00:00Z", "message": "Data collection session initiated for Financial Systems Q2 audit", "level": "info"},
    {"timestamp": "2025-07-21T09:02:00Z", "message": "Connected to SQL Server Database (fin-db-prod.company.com)", "level": "info"},
    {"timestamp": "2025-07-21T09:05:00Z", "message": "Processing 5 Financial Controls questions", "level": "info"},
    {"timestamp": "2025-07-21T09:15:00Z", "message": "Retrieved cash reconciliation procedures and approval workflows", "level": "success"},
    {"timestamp": "2025-07-21T09:18:00Z", "message": "Connected to Oracle Database (oracle-fin.company.com)", "level": "info"},
    {"timestamp": "2025-07-21T09:25:00Z", "message": "Analyzed journal entry controls and segregation of duties", "level": "success"},
    {"timestamp": "2025-07-21T09:28:00Z", "message": "Connected to ServiceNow (company.service-now.com)", "level": "info"},
    {"timestamp": "2025-07-21T09:35:00Z", "message": "Retrieved access control information for financial systems", "level": "success"},
    {"timestamp": "2025-07-21T09:40:00Z", "message": "Data collection completed successfully - 7 questions processed", "level": "success"}
]', 
'2025-07-21 09:00:00', '2025-07-21 09:40:00'),

-- In Progress Security Session
(2, 'running', 75,
'[
    {"timestamp": "2025-07-21T10:30:00Z", "message": "Data collection session started for Security Compliance Review", "level": "info"},
    {"timestamp": "2025-07-21T10:32:00Z", "message": "Connected to Gnosis Document Repository", "level": "info"},
    {"timestamp": "2025-07-21T10:38:00Z", "message": "Retrieved password policies and security standards", "level": "success"},
    {"timestamp": "2025-07-21T10:42:00Z", "message": "Connected to SQL Server Database (sec-db-prod.company.com)", "level": "info"},
    {"timestamp": "2025-07-21T10:50:00Z", "message": "Processing privileged account monitoring data", "level": "info"},
    {"timestamp": "2025-07-21T10:55:00Z", "message": "Connected to Jira (company.atlassian.net)", "level": "info"},
    {"timestamp": "2025-07-21T11:00:00Z", "message": "Analyzing security incident response procedures", "level": "info"}
]',
'2025-07-21 10:30:00', NULL),

-- Completed Stark G4 Session (Comprehensive multi-tool execution)
(4, 'completed', 100,
'[
    {"timestamp": "2025-08-06T14:00:00Z", "message": "Comprehensive data collection session started for Stark G4 audit", "level": "info"},
    {"timestamp": "2025-08-06T14:02:00Z", "message": "Connected to SQL Server Database (sql-prod-01.company.com)", "level": "info"},
    {"timestamp": "2025-08-06T14:10:00Z", "message": "Retrieved database access controls and user permissions", "level": "success"},
    {"timestamp": "2025-08-06T14:15:00Z", "message": "Connected to Oracle Database (oracle-prod.company.com)", "level": "info"},
    {"timestamp": "2025-08-06T14:25:00Z", "message": "Analyzed database performance metrics and monitoring data", "level": "success"},
    {"timestamp": "2025-08-06T14:30:00Z", "message": "Connected to QTest (company.qtestnet.com)", "level": "info"},
    {"timestamp": "2025-08-06T14:40:00Z", "message": "Retrieved automated testing procedures and execution results", "level": "success"},
    {"timestamp": "2025-08-06T14:45:00Z", "message": "Connected to Jira (company.atlassian.net)", "level": "info"},
    {"timestamp": "2025-08-06T14:55:00Z", "message": "Analyzed change approval workflows and modification tracking", "level": "success"},
    {"timestamp": "2025-08-06T15:00:00Z", "message": "Connected to ServiceNow (company.service-now.com)", "level": "info"},
    {"timestamp": "2025-08-06T15:10:00Z", "message": "Retrieved incident tracking and resolution procedures", "level": "success"},
    {"timestamp": "2025-08-06T15:15:00Z", "message": "Connected to Gnosis Document Repository", "level": "info"},
    {"timestamp": "2025-08-06T15:25:00Z", "message": "Retrieved data classification standards and governance policies", "level": "success"},
    {"timestamp": "2025-08-06T15:30:00Z", "message": "Comprehensive data collection completed - 14 primary + 7 follow-up questions processed", "level": "success"}
]',
'2025-08-06 14:00:00', '2025-08-06 15:30:00'),

-- Pending Infrastructure Session
(3, 'pending', 0, '[]', NULL, NULL);

-- =====================================================
-- SAMPLE AGENT EXECUTIONS (Realistic AI Results)
-- =====================================================

INSERT INTO agent_executions (application_id, question_id, tool_type, connector_id, prompt, result, status, tool_used, execution_details) VALUES
-- Financial Systems Executions
(1, 'Q001', 'SQL Server Database', 1, 
'Query the financial database to retrieve comprehensive account reconciliation procedures for cash accounts. Analyze: 1) Reconciliation frequency and timing, 2) Approval requirements and hierarchy, 3) Documentation standards and templates, 4) Exception handling procedures, 5) Control monitoring and reporting.',
'{"executive_summary": "Cash account reconciliations are performed daily with a two-level approval process. Standard templates are used with comprehensive exception reporting and quarterly control monitoring.", "analysis": {"confidence": 0.92, "risk_level": "Low", "compliance_status": "Compliant"}, "findings": {"reconciliation_frequency": "Daily for all major cash accounts", "approval_hierarchy": "Preparer -> Reviewer -> Manager approval required", "documentation": "Standardized templates with supporting documentation requirements", "exceptions": "Automated exception reporting with 24-hour resolution requirement", "monitoring": "Monthly control testing with quarterly management reporting"}, "data_points": 847, "toolsUsed": ["SQL Server Database"]}',
'success', 'SQL Server Database', 
'{"query_execution_time": 2.3, "records_analyzed": 847, "data_sources": ["gl_reconciliations", "cash_accounts", "approval_workflows"], "confidence_factors": {"data_completeness": 0.95, "data_accuracy": 0.90, "control_coverage": 0.91}}'),

(1, 'Q002', 'SQL Server Database', 1,
'Examine journal entry review and approval processes in the general ledger system. Focus on: 1) Approval hierarchy and segregation of duties, 2) Supporting documentation requirements, 3) Audit trail maintenance, 4) Exception approval processes.',
'{"executive_summary": "Journal entries require two-level approval with strict segregation of duties. Complete audit trails are maintained with supporting documentation for all entries above materiality thresholds.", "analysis": {"confidence": 0.89, "risk_level": "Low", "compliance_status": "Compliant"}, "findings": {"approval_process": "Two-level approval: preparer cannot approve own entries", "segregation_duties": "Role-based access prevents conflicts of interest", "documentation": "Supporting docs required for entries >$10,000", "audit_trail": "Complete audit trail with timestamps and user tracking", "exceptions": "CFO approval required for material adjustments"}, "data_points": 1205, "toolsUsed": ["SQL Server Database"]}',
'success', 'SQL Server Database',
'{"query_execution_time": 3.1, "records_analyzed": 1205, "data_sources": ["journal_entries", "approval_logs", "user_roles"], "confidence_factors": {"data_completeness": 0.92, "data_accuracy": 0.88, "control_coverage": 0.87}}'),

-- Security Compliance Executions  
(2, 'Q001', 'Gnosis Document Repository', 6,
'Retrieve and analyze current password policy documentation including complexity requirements, expiration settings, enforcement procedures, and compliance monitoring across all enterprise systems.',
'{"executive_summary": "Enterprise password policies meet industry standards with 12-character minimum, 90-day expiration, and automated enforcement through Active Directory. Compliance monitoring shows 98% adherence.", "analysis": {"confidence": 0.94, "risk_level": "Low", "compliance_status": "Compliant"}, "findings": {"complexity": "Minimum 12 characters, mixed case, numbers, special characters required", "expiration": "90-day password expiration with 14-day advance warning", "enforcement": "Automated through Active Directory with real-time policy checking", "exceptions": "Service accounts exempt with annual review requirement", "compliance": "98% user compliance with monthly reporting"}, "data_points": 156, "toolsUsed": ["Gnosis Document Repository"]}',
'success', 'Gnosis Document Repository',
'{"document_count": 156, "policy_version": "v3.2", "last_updated": "2025-06-15", "confidence_factors": {"policy_completeness": 0.96, "implementation_evidence": 0.92, "monitoring_coverage": 0.94}}'),

-- Stark G4 Multi-Tool Executions (Comprehensive realistic results)
(4, 'Q005', 'QTest', 12,
'Examine automated testing procedures for system changes including test case management, execution automation, result reporting, and integration with change management processes in QTest.',
'{"executive_summary": "Comprehensive automated testing framework implemented with 85% test automation coverage. QTest manages 2,847 test cases with automated execution and integration to Jira for change management.", "analysis": {"confidence": 0.91, "risk_level": "Medium", "compliance_status": "Mostly Compliant"}, "findings": {"automation_coverage": "85% of regression tests automated", "test_cases": "2,847 active test cases across 15 application modules", "execution_frequency": "Automated tests run nightly and on-demand for releases", "integration": "Direct integration with Jira for requirement traceability", "reporting": "Real-time dashboards with test metrics and trend analysis", "gaps": "15% manual testing still required for complex business scenarios"}, "data_points": 2847, "toolsUsed": ["QTest"]}',
'success', 'QTest',
'{"test_cycles": 156, "automation_scripts": 2421, "execution_history": "6 months", "confidence_factors": {"data_completeness": 0.94, "automation_coverage": 0.85, "integration_quality": 0.93}}'),

(4, 'Q006', 'ServiceNow', 13,
'Review incident tracking and resolution processes in ServiceNow including ticket workflow, escalation procedures, SLA compliance, and resolution documentation.',
'{"executive_summary": "ServiceNow incident management demonstrates strong SLA compliance at 94% with automated escalation and comprehensive resolution tracking. Average resolution time is 2.3 days for P2 incidents.", "analysis": {"confidence": 0.88, "risk_level": "Low", "compliance_status": "Compliant"}, "findings": {"sla_compliance": "94% SLA compliance across all incident priorities", "resolution_time": "Average 4 hours P1, 2.3 days P2, 5 days P3", "escalation": "Automated escalation at 50%, 75%, and 90% of SLA", "workflow": "Standardized ITIL-based workflow with approval gates", "documentation": "Mandatory resolution notes with root cause analysis", "metrics": "Real-time KPI dashboard with trend monitoring"}, "data_points": 3421, "toolsUsed": ["ServiceNow"]}',
'success', 'ServiceNow',
'{"incident_count": 3421, "time_period": "12 months", "sla_metrics": "real-time", "confidence_factors": {"data_completeness": 0.91, "process_compliance": 0.88, "resolution_quality": 0.85}}'),

(4, 'Q007', 'Jira', 11,
'Analyze change approval workflows in Jira for system modifications including approval hierarchies, review processes, documentation requirements, and change tracking mechanisms.',
'{"executive_summary": "Jira change management workflow enforces proper approval hierarchy with 97% compliance. All system modifications require business and technical approval with comprehensive audit trails.", "analysis": {"confidence": 0.93, "risk_level": "Low", "compliance_status": "Compliant"}, "findings": {"approval_hierarchy": "Business Owner -> Technical Lead -> Change Advisory Board", "compliance_rate": "97% of changes follow approved workflow", "documentation": "Mandatory impact assessment and rollback procedures", "tracking": "End-to-end change tracking with status visibility", "integration": "Integrated with deployment pipelines and testing systems", "audit_trail": "Complete approval history with timestamps and justifications"}, "data_points": 1876, "toolsUsed": ["Jira"]}',
'success', 'Jira',
'{"change_requests": 1876, "approval_stages": 4, "workflow_compliance": 0.97, "confidence_factors": {"data_completeness": 0.95, "process_adherence": 0.93, "audit_coverage": 0.91}}');

-- =====================================================
-- SAMPLE AUDIT RESULTS (Final Outcomes)
-- =====================================================

INSERT INTO audit_results (application_id, session_id, question_id, question, category, status, document_path) VALUES
-- Financial Systems Results
(1, 1, 'Q001', 'What are the current account reconciliation procedures for cash accounts?', 'Financial Controls', 'completed', 
'uploads/audit_1_Financial_Systems_Q2/results/Q001_cash_reconciliation_analysis.pdf'),

(1, 1, 'Q002', 'How are journal entries reviewed and approved in the general ledger?', 'Financial Controls', 'completed', 
'uploads/audit_1_Financial_Systems_Q2/results/Q002_journal_entry_controls_analysis.pdf'),

-- Stark G4 Results
(4, 3, 'Q005', 'What automated testing procedures are implemented for system changes?', 'Quality Assurance', 'completed',
'uploads/audit_4_Stark_G4/results/Q005_automated_testing_analysis.pdf'),

(4, 3, 'Q006', 'How are incidents tracked and resolved in the ServiceNow system?', 'Incident Management', 'completed',
'uploads/audit_4_Stark_G4/results/Q006_incident_management_analysis.pdf'),

(4, 3, 'Q007', 'What change approval workflows exist in Jira for system modifications?', 'Change Management', 'completed',
'uploads/audit_4_Stark_G4/results/Q007_change_management_analysis.pdf');

-- =====================================================
-- SAMPLE QUESTION ANSWERS (Execution Results)
-- =====================================================

INSERT INTO question_answers (application_id, question_id, answer, findings, risk_level, compliance_status, data_points, execution_details) VALUES
-- Financial Systems Question Answers
(1, 'Q001', 'Cash account reconciliations are performed daily with comprehensive approval workflows and exception reporting mechanisms in place.',
'{"reconciliation_frequency": "Daily for all major cash accounts", "approval_hierarchy": "Preparer -> Reviewer -> Manager approval required", "documentation": "Standardized templates with supporting documentation requirements", "exceptions": "Automated exception reporting with 24-hour resolution requirement"}',
'Low', 'Compliant', 847,
'{"confidence": 0.92, "data_sources": ["gl_reconciliations", "cash_accounts", "approval_workflows"], "query_execution_time": 2.3}'),

(1, 'Q002', 'Journal entries require two-level approval with strict segregation of duties and complete audit trail maintenance.',
'{"approval_process": "Two-level approval: preparer cannot approve own entries", "segregation_duties": "Role-based access prevents conflicts of interest", "documentation": "Supporting docs required for entries >$10,000", "audit_trail": "Complete audit trail with timestamps and user tracking"}',
'Low', 'Compliant', 1205,
'{"confidence": 0.89, "data_sources": ["journal_entries", "approval_logs", "user_roles"], "query_execution_time": 3.1}'),

-- Security Compliance Question Answers
(2, 'Q001', 'Enterprise password policies meet industry standards with automated enforcement and 98% user compliance.',
'{"complexity": "Minimum 12 characters, mixed case, numbers, special characters required", "expiration": "90-day password expiration with 14-day advance warning", "enforcement": "Automated through Active Directory with real-time policy checking", "compliance": "98% user compliance with monthly reporting"}',
'Low', 'Compliant', 156,
'{"confidence": 0.94, "data_sources": ["policy_documents", "compliance_reports"], "document_count": 156}'),

-- Stark G4 Question Answers (Multi-tool execution results)
(4, 'Q005', 'Comprehensive automated testing framework with 85% test automation coverage and integration with change management systems.',
'{"automation_coverage": "85% of regression tests automated", "test_cases": "2,847 active test cases across 15 application modules", "execution_frequency": "Automated tests run nightly and on-demand for releases", "integration": "Direct integration with Jira for requirement traceability"}',
'Medium', 'Mostly Compliant', 2847,
'{"confidence": 0.91, "data_sources": ["qtest_cycles", "automation_scripts"], "test_cycles": 156}'),

(4, 'Q006', 'ServiceNow incident management demonstrates strong SLA compliance with automated escalation and comprehensive tracking.',
'{"sla_compliance": "94% SLA compliance across all incident priorities", "resolution_time": "Average 4 hours P1, 2.3 days P2, 5 days P3", "escalation": "Automated escalation at 50%, 75%, and 90% of SLA", "workflow": "Standardized ITIL-based workflow with approval gates"}',
'Low', 'Compliant', 3421,
'{"confidence": 0.88, "data_sources": ["incident_records", "sla_metrics"], "incident_count": 3421}');

-- =====================================================
-- SAMPLE VERITAS CONVERSATIONS (Current Schema)
-- =====================================================

INSERT INTO veritas_conversations (conversation_id, ci_id, audit_id, audit_name, message, response, tools_used) VALUES
-- Stark G4 Conversation with realistic data analysis
('conv_stark_20250806_001', 'CI21324354', '4', 'Stark G4 Comprehensive', 
'What testing data do you have for RunID 101?',
'Based on my analysis of the QTest data files, RunID 101 shows the following testing information:\n\n**Test Execution Summary:**\n- Test Run: Login Functionality Test Suite\n- Tester: Sarah Johnson\n- Status: **Failed**\n- Execution Date: 2025-07-15\n- Environment: UAT\n\n**Failure Details:**\n- 3 out of 8 test cases failed\n- Primary issue: Authentication timeout after 30 seconds\n- Failed test cases: TC_LOGIN_001, TC_LOGIN_005, TC_LOGIN_007\n- Root cause: Database connection pool exhaustion\n\n**Cross-Reference with Jira:**\nThis failure is linked to Jira defect JIRA-123 which documents the authentication timeout issue and includes remediation steps.',
'["QTest", "Jira"]'),

('conv_stark_20250806_002', 'CI21324354', '4', 'Stark G4 Comprehensive',
'Tell me about the Jira defect JIRA-123 status',
'Here are the details for Jira defect JIRA-123 related to the authentication timeout:\n\n**Defect Information:**\n- **Issue Key:** JIRA-123\n- **Title:** Authentication Timeout - Database Connection Pool Exhaustion\n- **Status:** In Progress\n- **Priority:** High\n- **Assignee:** Mike Chen (Senior Developer)\n- **Reporter:** Sarah Johnson (QA Lead)\n\n**Technical Details:**\n- Created: 2025-07-16 (day after test failure)\n- Environment: UAT, Production impact potential\n- Components: Authentication Service, Database Layer\n- Fix Version: Release 2.3.1\n\n**Resolution Progress:**\n- Database connection pool size increased from 50 to 100\n- Connection timeout adjusted from 30s to 60s\n- Code review completed for connection cleanup\n- Targeted completion: 2025-08-10\n\nThis defect is directly connected to the QTest RunID 101 failure and shows active remediation efforts.',
'["Jira"]'),

-- Financial Systems Conversation
('conv_fin_20250720_001', 'CI21345001', '1', 'Financial Systems Q2',
'What financial controls documentation do you have available?',
'I have comprehensive financial controls documentation available:\n\n**Key Control Areas Covered:**\n1. **Cash Management Controls**\n   - Daily reconciliation procedures\n   - Bank account monitoring\n   - Cash flow authorization limits\n\n2. **Journal Entry Controls**\n   - Two-level approval process\n   - Supporting documentation requirements\n   - Audit trail maintenance\n\n3. **Access Controls**\n   - Role-based permissions\n   - Segregation of duties matrix\n   - Periodic access reviews\n\nWould you like me to dive deeper into any specific control area or procedure?',
'["SQL Server Database", "Oracle Database"]');

-- =====================================================
-- DATA VALIDATION QUERIES
-- =====================================================

-- Verify record counts
SELECT 
    'applications' as table_name, COUNT(*) as record_count FROM applications
UNION ALL
SELECT 
    'tool_connectors' as table_name, COUNT(*) as record_count FROM tool_connectors
UNION ALL
SELECT 
    'data_requests' as table_name, COUNT(*) as record_count FROM data_requests
UNION ALL
SELECT 
    'question_analyses' as table_name, COUNT(*) as record_count FROM question_analyses
UNION ALL
SELECT 
    'data_collection_sessions' as table_name, COUNT(*) as record_count FROM data_collection_sessions
UNION ALL
SELECT 
    'question_answers' as table_name, COUNT(*) as record_count FROM question_answers
UNION ALL
SELECT 
    'agent_executions' as table_name, COUNT(*) as record_count FROM agent_executions
UNION ALL
SELECT 
    'audit_results' as table_name, COUNT(*) as record_count FROM audit_results
UNION ALL
SELECT 
    'veritas_conversations' as table_name, COUNT(*) as record_count FROM veritas_conversations
ORDER BY table_name;

-- Verify foreign key relationships
SELECT 
    a.audit_name,
    COUNT(tc.id) as connectors,
    COUNT(dr.id) as data_requests,
    COUNT(qa.id) as question_analyses,
    COUNT(qans.id) as question_answers,
    COUNT(dcs.id) as sessions
FROM applications a
LEFT JOIN tool_connectors tc ON a.id = tc.application_id
LEFT JOIN data_requests dr ON a.id = dr.application_id  
LEFT JOIN question_analyses qa ON a.id = qa.application_id
LEFT JOIN question_answers qans ON a.id = qans.application_id
LEFT JOIN data_collection_sessions dcs ON a.id = dcs.application_id
GROUP BY a.id, a.audit_name
ORDER BY a.id;

-- =====================================================
-- SUCCESS MESSAGE
-- =====================================================

\echo ''
\echo '============================================='
\echo 'CA Audit Agent Sample Data Loaded Successfully!'
\echo '============================================='
\echo ''
\echo 'Data Summary:'
\echo '  ✅ 5 Applications (Financial, Security, Infrastructure, Stark G4, ERP)'
\echo '  ✅ 14 Tool Connectors (Multi-system integration)'
\echo '  ✅ 4 Data Requests (28 total questions: 21 primary + 7 follow-up)'
\echo '  ✅ 8 Question Analyses (AI-powered recommendations)'
\echo '  ✅ 5 Question Answers (Execution results with findings)'
\echo '  ✅ 4 Data Collection Sessions (Including completed Stark G4)'
\echo '  ✅ 6 Agent Executions (Realistic multi-tool results)'
\echo '  ✅ 5 Audit Results (Final documented outcomes)'
\echo '  ✅ 3 Veritas Conversations (Chat messages with tool usage)'
\echo ''
\echo 'Featured Data:'
\echo '  🎯 Stark G4 (CI21324354): Complete 6-tool integration'
\echo '  🎯 Multi-tool test scenarios (QTest ↔ Jira cross-reference)'
\echo '  🎯 Realistic AI execution results with confidence scores'
\echo '  🎯 Comprehensive audit workflows and documentation'
\echo ''
\echo 'Ready for CA Audit Agent testing and development!'
\echo '============================================='