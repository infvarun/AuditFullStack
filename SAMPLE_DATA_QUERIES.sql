-- Sample Data Queries for Stark G4 Q2CA2025 Audit
-- Run these queries in your DBeaver to explore the audit data

-- 1. Get the Stark audit application details (CORRECTED COLUMNS)
SELECT 
    id,
    audit_name,
    name,  -- alternative name field
    ci_id,
    start_date,
    end_date,
    status,
    enable_followup_questions,
    created_at
FROM applications 
WHERE audit_name LIKE '%Stark%' OR ci_id = 'CI21324354';

-- 2. Get data request files for Stark audit (Step 2 data)
SELECT 
    dr.id,
    dr.application_id,
    dr.file_name,
    dr.file_type,
    dr.total_questions,
    dr.categories,
    dr.uploaded_at,
    a.audit_name
FROM data_requests dr
JOIN applications a ON dr.application_id = a.id
WHERE a.ci_id = 'CI21324354'
ORDER BY dr.uploaded_at;

-- 3. Get question analyses for Stark audit (Step 3 AI analysis)
SELECT 
    qa.id,
    qa.application_id,
    qa.question_text,
    qa.suggested_tools,
    qa.confidence_score,
    qa.analysis_result,
    a.audit_name
FROM question_analyses qa
JOIN applications a ON qa.application_id = a.id
WHERE a.ci_id = 'CI21324354'
ORDER BY qa.id
LIMIT 10;

-- 4. Get tool connectors configured for Stark audit (CORRECTED COLUMNS)
SELECT 
    tc.id,
    tc.application_id,
    tc.type as tool_type,  -- corrected column name
    tc.name as connection_name,  -- corrected column name
    tc.status,
    tc.config,  -- corrected column name
    a.audit_name
FROM tool_connectors tc
JOIN applications a ON tc.application_id = a.id
WHERE a.ci_id = 'CI21324354'
ORDER BY tc.type;

-- 5. Get agent execution results (Step 4 execution data) - Sample
SELECT 
    ae.id,
    ae.application_id,
    ae.question_id,
    ae.tool_type,
    ae.status,
    ae.created_at,
    -- Parse JSON result to get key information
    json_extract_path_text(ae.result::json, 'analysis', 'executiveSummary') as executive_summary,
    json_extract_path_text(ae.result::json, 'analysis', 'riskLevel') as risk_level,
    json_extract_path_text(ae.result::json, 'analysis', 'complianceStatus') as compliance_status,
    a.audit_name
FROM agent_executions ae
JOIN applications a ON ae.application_id = a.id
WHERE a.ci_id = 'CI21324354'
ORDER BY ae.question_id
LIMIT 20;

-- 6. Get execution statistics for Stark audit
SELECT 
    a.audit_name,
    a.ci_id,
    COUNT(ae.id) as total_executions,
    COUNT(CASE WHEN ae.status = 'completed' THEN 1 END) as completed_executions,
    COUNT(CASE WHEN ae.status = 'failed' THEN 1 END) as failed_executions,
    ROUND(
        (COUNT(CASE WHEN ae.status = 'completed' THEN 1 END) * 100.0 / COUNT(ae.id)), 2
    ) as completion_percentage
FROM applications a
LEFT JOIN agent_executions ae ON a.id = ae.application_id
WHERE a.ci_id = 'CI21324354'
GROUP BY a.id, a.audit_name, a.ci_id;

-- 7. Get sample findings from execution results
SELECT 
    ae.question_id,
    ae.tool_type,
    json_extract_path_text(ae.result::json, 'findings', '0', 'finding') as first_finding,
    json_extract_path_text(ae.result::json, 'findings', '0', 'severity') as finding_severity,
    json_extract_path_text(ae.result::json, 'analysis', 'totalDataPoints') as data_points,
    a.audit_name
FROM agent_executions ae
JOIN applications a ON ae.application_id = a.id
WHERE a.ci_id = 'CI21324354' 
    AND ae.status = 'completed'
    AND ae.result IS NOT NULL
ORDER BY ae.question_id
LIMIT 15;

-- 8. Get all audits and their basic info (to see what other data you have)
SELECT 
    id,
    audit_name,
    ci_id,
    client_name,
    audit_period,
    status,
    created_at,
    (SELECT COUNT(*) FROM agent_executions WHERE application_id = applications.id) as execution_count,
    (SELECT COUNT(*) FROM data_requests WHERE application_id = applications.id) as data_request_count
FROM applications
ORDER BY created_at DESC;

-- 9. Quick CI lookup for all audits
SELECT DISTINCT ci_id, audit_name, client_name, status
FROM applications
ORDER BY ci_id;