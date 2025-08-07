-- FIX FOR CONNECTOR TYPE CONSTRAINT ERROR
-- This script removes any restrictive check constraints on connector_type
-- and allows all current production connector types

-- Drop any existing check constraint on connector_type
ALTER TABLE tool_connectors 
DROP CONSTRAINT IF EXISTS chk_connector_type;

-- Add a new constraint that allows all current production connector types
ALTER TABLE tool_connectors 
ADD CONSTRAINT chk_connector_type 
CHECK (connector_type IN (
    'SQL Server DB',
    'Oracle DB', 
    'Gnosis Document Repository',
    'ServiceNow',
    'Jira',
    'QTest',
    -- Legacy format compatibility
    'sql_server',
    'oracle_db',
    'gnosis',
    'service_now',
    'jira',
    'qtest'
));

-- Verify the constraint was created successfully
SELECT conname, pg_get_constraintdef(oid) as constraint_definition 
FROM pg_constraint 
WHERE conname = 'chk_connector_type';