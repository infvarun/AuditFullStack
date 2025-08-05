#!/usr/bin/env python3
"""
Demo Data Setup Script

Sets up realistic demo data in the PostgreSQL database including:
- Mock connector configurations
- Sample audit data
- Realistic question analyses with multi-tool selections
"""

import sys
import os
import psycopg2
import json
from datetime import datetime
from psycopg2.extras import RealDictCursor

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_db_connection():
    """Get database connection using environment variables"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('PGHOST', 'localhost'),
            database=os.getenv('PGDATABASE', 'postgres'),
            user=os.getenv('PGUSER', 'postgres'),
            password=os.getenv('PGPASSWORD', ''),
            port=os.getenv('PGPORT', '5432')
        )
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None

def setup_demo_connectors():
    """Setup demo connector configurations"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Demo CI ID
        ci_id = "CI21324354"  # Using the existing one from the app
        
        # Define demo connectors with realistic configurations
        demo_connectors = [
            {
                'connector_type': 'SQL Server DB',
                'ci_id': ci_id,
                'configuration': {
                    'server': 'sql-prod-01.company.com',
                    'database': 'AuditDB',
                    'port': 1433,
                    'connection_timeout': 30,
                    'query_timeout': 300,
                    'ssl_enabled': True,
                    'demo_mode': True,
                    'description': 'Primary SQL Server database for user accounts and audit logs'
                },
                'status': 'active'
            },
            {
                'connector_type': 'Oracle DB',
                'ci_id': ci_id,
                'configuration': {
                    'server': 'oracle-erp-01.company.com',
                    'database': 'ERPDB',
                    'port': 1521,
                    'service_name': 'ERPDB.company.com',
                    'connection_pool_size': 10,
                    'ssl_enabled': True,
                    'demo_mode': True,
                    'description': 'Oracle ERP database for financial transactions and compliance data'
                },
                'status': 'active'
            },
            {
                'connector_type': 'Gnosis Document Repository',
                'ci_id': ci_id,
                'configuration': {
                    'base_url': 'https://gnosis.company.com/api/v2',
                    'search_endpoint': '/documents/search',
                    'auth_type': 'oauth2',
                    'max_results': 100,
                    'content_types': ['policy', 'procedure', 'standard', 'guideline'],
                    'demo_mode': True,
                    'description': 'Document management system for policies and procedures'
                },
                'status': 'active'
            },
            {
                'connector_type': 'Jira',
                'ci_id': ci_id,
                'configuration': {
                    'base_url': 'https://company.atlassian.net',
                    'project_keys': ['SEC', 'AUDIT', 'COMP'],
                    'api_version': '3',
                    'max_results': 50,
                    'issue_types': ['Bug', 'Story', 'Task', 'Epic'],
                    'demo_mode': True,
                    'description': 'Jira project management for security and compliance issues'
                },
                'status': 'active'
            },
            {
                'connector_type': 'QTest',
                'ci_id': ci_id,
                'configuration': {
                    'base_url': 'https://qtest.company.com/api/v3',
                    'project_id': 12345,
                    'test_suites': ['Security', 'Compliance', 'Integration'],
                    'automation_enabled': True,
                    'report_formats': ['json', 'xml', 'html'],
                    'demo_mode': True,
                    'description': 'QTest quality assurance platform for test case management'
                },
                'status': 'active'
            },
            {
                'connector_type': 'ServiceNow',
                'ci_id': ci_id,
                'configuration': {
                    'instance_url': 'https://company.service-now.com',
                    'api_version': 'v1',
                    'tables': ['incident', 'change_request', 'service_request', 'problem'],
                    'max_records': 1000,
                    'include_attachments': False,
                    'demo_mode': True,
                    'description': 'ServiceNow ITSM platform for incident and service management'
                },
                'status': 'active'
            }
        ]
        
        # Insert demo connectors
        for connector in demo_connectors:
            # Check if connector already exists
            cursor.execute("""
                SELECT id FROM tool_connectors 
                WHERE connector_type = %s AND ci_id = %s
            """, (connector['connector_type'], connector['ci_id']))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing connector
                cursor.execute("""
                    UPDATE tool_connectors 
                    SET configuration = %s, status = %s
                    WHERE id = %s
                """, (
                    json.dumps(connector['configuration']),
                    connector['status'],
                    existing['id']
                ))
                print(f"Updated existing connector: {connector['connector_type']}")
            else:
                # Insert new connector
                cursor.execute("""
                    INSERT INTO tool_connectors 
                    (connector_type, ci_id, configuration, status, created_at)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    connector['connector_type'],
                    connector['ci_id'],
                    json.dumps(connector['configuration']),
                    connector['status'],
                    datetime.now()
                ))
                print(f"Created new connector: {connector['connector_type']}")
        
        conn.commit()
        print(f"Successfully setup {len(demo_connectors)} demo connectors for CI: {ci_id}")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error setting up demo connectors: {e}")
        return False
        
    finally:
        cursor.close()
        conn.close()

def setup_demo_questions():
    """Setup realistic demo questions with multi-tool analyses"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get the existing application ID
        cursor.execute("SELECT id FROM applications WHERE ci_id = %s", ("CI21324354",))
        app = cursor.fetchone()
        
        if not app:
            print("No application found with CI ID CI21324354")
            return False
        
        app_id = app['id']
        
        # Demo questions with realistic multi-tool scenarios
        demo_questions = [
            {
                'question_id': 'Q001',
                'original_question': 'Review user access controls and authentication policies to ensure compliance with security standards',
                'category': 'Security',
                'subcategory': 'Access Control',
                'tool_suggestion': ['SQL Server DB', 'Gnosis Document Repository'],  # Multi-tool
                'ai_prompt': 'Analyze user access controls by examining user account data in SQL Server and reviewing authentication policies in document repository. Identify any gaps between documented policies and actual user permissions.',
                'connector_reason': 'Selected SQL Server DB for user account analysis and Gnosis for policy documentation review to provide comprehensive access control assessment.'
            },
            {
                'question_id': 'Q002',
                'original_question': 'Evaluate incident response procedures and track security incident resolution',
                'category': 'Security',
                'subcategory': 'Incident Management',
                'tool_suggestion': ['Gnosis Document Repository', 'Jira', 'ServiceNow'],  # Multi-tool
                'ai_prompt': 'Review incident response procedures in documentation system, analyze security tickets in Jira, and examine incident records in ServiceNow to assess overall incident management effectiveness.',
                'connector_reason': 'Multi-tool approach needed: Gnosis for procedures, Jira for development-related security issues, ServiceNow for operational incidents.'
            },
            {
                'question_id': 'Q003',
                'original_question': 'Assess financial transaction controls and compliance with SOX requirements',
                'category': 'Compliance',
                'subcategory': 'Financial Controls',
                'tool_suggestion': ['Oracle DB', 'Gnosis Document Repository'],  # Multi-tool
                'ai_prompt': 'Examine financial transaction data in Oracle ERP system and review SOX compliance documentation to assess control effectiveness and identify any compliance gaps.',
                'connector_reason': 'Oracle DB contains financial transaction data while Gnosis holds SOX compliance policies and procedures for comprehensive assessment.'
            },
            {
                'question_id': 'Q004',
                'original_question': 'Review software testing processes and quality assurance coverage',
                'category': 'Quality',
                'subcategory': 'Testing',
                'tool_suggestion': ['QTest', 'Jira'],  # Multi-tool
                'ai_prompt': 'Analyze test case execution results in QTest and review related development issues in Jira to assess testing coverage and quality assurance effectiveness.',
                'connector_reason': 'QTest provides test execution data while Jira tracks related development issues and defects for complete quality assessment.'
            },
            {
                'question_id': 'Q005',
                'original_question': 'Examine change management processes and approval workflows',
                'category': 'Process',
                'subcategory': 'Change Management',
                'tool_suggestion': 'ServiceNow',  # Single tool
                'ai_prompt': 'Review change request records in ServiceNow to analyze change management process adherence, approval workflows, and success rates.',
                'connector_reason': 'ServiceNow is the primary system for change management processes and contains comprehensive change request data.'
            }
        ]
        
        # Insert or update demo questions
        for question in demo_questions:
            # Check if analysis already exists
            cursor.execute("""
                SELECT id FROM question_analyses 
                WHERE application_id = %s AND question_id = %s
            """, (app_id, question['question_id']))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing analysis
                cursor.execute("""
                    UPDATE question_analyses 
                    SET original_question = %s, category = %s, subcategory = %s,
                        tool_suggestion = %s, ai_prompt = %s, connector_reason = %s,
                        connector_to_use = %s
                    WHERE id = %s
                """, (
                    question['original_question'],
                    question['category'],
                    question['subcategory'],
                    json.dumps(question['tool_suggestion']),
                    question['ai_prompt'],
                    question['connector_reason'],
                    json.dumps(question['tool_suggestion']),  # Use same as tool_suggestion
                    existing['id']
                ))
                print(f"Updated existing question analysis: {question['question_id']}")
            else:
                # Insert new analysis
                cursor.execute("""
                    INSERT INTO question_analyses 
                    (application_id, question_id, original_question, category, subcategory,
                     tool_suggestion, ai_prompt, connector_reason, connector_to_use, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    app_id,
                    question['question_id'],
                    question['original_question'],
                    question['category'],
                    question['subcategory'],
                    json.dumps(question['tool_suggestion']),
                    question['ai_prompt'],
                    question['connector_reason'],
                    json.dumps(question['tool_suggestion']),  # Use same as tool_suggestion
                    datetime.now()
                ))
                print(f"Created new question analysis: {question['question_id']}")
        
        conn.commit()
        print(f"Successfully setup {len(demo_questions)} demo questions for application ID: {app_id}")
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"Error setting up demo questions: {e}")
        return False
        
    finally:
        cursor.close()
        conn.close()

def verify_demo_setup():
    """Verify that demo data was setup correctly"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Check connectors
        cursor.execute("SELECT COUNT(*) as count FROM tool_connectors WHERE ci_id = %s", ("CI21324354",))
        connector_count = cursor.fetchone()['count']
        
        # Check question analyses
        cursor.execute("""
            SELECT COUNT(*) as count FROM question_analyses qa
            JOIN applications app ON qa.application_id = app.id
            WHERE app.ci_id = %s
        """, ("CI21324354",))
        question_count = cursor.fetchone()['count']
        
        print(f"\nDemo Setup Verification:")
        print(f"- Connectors configured: {connector_count}")
        print(f"- Question analyses: {question_count}")
        
        # List connectors
        cursor.execute("SELECT connector_type, status FROM tool_connectors WHERE ci_id = %s", ("CI21324354",))
        connectors = cursor.fetchall()
        
        print(f"\nConfigured Connectors:")
        for conn in connectors:
            print(f"  - {conn['connector_type']}: {conn['status']}")
        
        # List questions
        cursor.execute("""
            SELECT qa.question_id, qa.category, qa.tool_suggestion
            FROM question_analyses qa
            JOIN applications app ON qa.application_id = app.id
            WHERE app.ci_id = %s
            ORDER BY qa.question_id
        """, ("CI21324354",))
        questions = cursor.fetchall()
        
        print(f"\nDemo Questions:")
        for q in questions:
            tools = json.loads(q['tool_suggestion']) if q['tool_suggestion'].startswith('[') else q['tool_suggestion']
            tool_display = ', '.join(tools) if isinstance(tools, list) else tools
            print(f"  - {q['question_id']} ({q['category']}): {tool_display}")
        
        return True
        
    except Exception as e:
        print(f"Error verifying demo setup: {e}")
        return False
        
    finally:
        cursor.close()
        conn.close()

def main():
    """Main setup function"""
    print("Setting up demo data for client presentation...")
    
    print("\n1. Setting up demo connectors...")
    if not setup_demo_connectors():
        print("Failed to setup demo connectors")
        return False
    
    print("\n2. Setting up demo questions...")
    if not setup_demo_questions():
        print("Failed to setup demo questions")
        return False
    
    print("\n3. Verifying demo setup...")
    if not verify_demo_setup():
        print("Failed to verify demo setup")
        return False
    
    print("\n✅ Demo data setup completed successfully!")
    print("\nYour audit application now has:")
    print("- 6 fully configured mock connectors")
    print("- 5 realistic audit questions with multi-tool analysis")
    print("- Ready for client demonstration")
    
    return True

if __name__ == '__main__':
    main()