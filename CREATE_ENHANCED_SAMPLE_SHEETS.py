#!/usr/bin/env python3
"""
Create Enhanced Sample Data Request Sheets for Stark G4 Audit
This script generates Excel files with realistic audit questions that leverage 
the file-based data connector system and demonstrate multi-tool integration.
"""

import pandas as pd
from datetime import datetime
import os

def create_primary_questions():
    """Create primary audit questions that leverage actual tool data"""
    
    primary_questions = [
        {
            'Question_ID': 'PQ001',
            'Category': 'Access Controls',
            'Subcategory': 'User Management',
            'Question': 'Review all active Database Admin users and their recent access patterns. Cross-reference with change management records to verify authorized activities.',
            'Suggested_Tools': 'SQL Server, ServiceNow',
            'Priority': 'High',
            'Expected_Evidence': 'User role listings, access logs, change request documentation'
        },
        {
            'Question_ID': 'PQ002', 
            'Category': 'Access Controls',
            'Subcategory': 'Privileged Access',
            'Question': 'Identify all users with Security_Admin roles across SQL Server and Oracle systems. Verify their access is documented and approved.',
            'Suggested_Tools': 'SQL Server, Oracle',
            'Priority': 'High',
            'Expected_Evidence': 'Role assignments, approval documentation'
        },
        {
            'Question_ID': 'PQ003',
            'Category': 'Change Management', 
            'Subcategory': 'System Changes',
            'Question': 'Analyze all change requests related to database configuration and security settings. Verify proper approval workflow and testing procedures.',
            'Suggested_Tools': 'ServiceNow, QTest',
            'Priority': 'Medium',
            'Expected_Evidence': 'Change requests, test execution records, approval chains'
        },
        {
            'Question_ID': 'PQ004',
            'Category': 'Access Controls',
            'Subcategory': 'Failed Access Attempts', 
            'Question': 'Review failed access attempts in system logs. Identify patterns and verify appropriate response procedures were followed.',
            'Suggested_Tools': 'SQL Server',
            'Priority': 'High',
            'Expected_Evidence': 'Access logs showing failed attempts, incident response records'
        },
        {
            'Question_ID': 'PQ005',
            'Category': 'Documentation',
            'Subcategory': 'System Architecture',
            'Question': 'Verify current system design documentation aligns with implemented security controls and compliance requirements.',
            'Suggested_Tools': 'Gnosis',
            'Priority': 'Medium', 
            'Expected_Evidence': 'Design documents, security control specifications'
        },
        {
            'Question_ID': 'PQ006',
            'Category': 'Change Management',
            'Subcategory': 'Issue Resolution',
            'Question': 'Review critical and high-priority issues reported in issue tracking system. Verify timely resolution and proper documentation.',
            'Suggested_Tools': 'Jira',
            'Priority': 'Medium',
            'Expected_Evidence': 'Issue tickets, resolution timelines, status reports'
        },
        {
            'Question_ID': 'PQ007',
            'Category': 'Access Controls',
            'Subcategory': 'Inactive Users',
            'Question': 'Identify inactive users with system access and verify account deactivation procedures. Cross-check with HR records and access logs.',
            'Suggested_Tools': 'SQL Server, Oracle, ServiceNow',
            'Priority': 'High',
            'Expected_Evidence': 'User status reports, deactivation records, access history'
        },
        {
            'Question_ID': 'PQ008',
            'Category': 'Quality Assurance',
            'Subcategory': 'Testing Coverage',
            'Question': 'Review test execution results for security-related test cases. Verify adequate coverage and defect resolution.',
            'Suggested_Tools': 'QTest, Jira',
            'Priority': 'Medium',
            'Expected_Evidence': 'Test execution reports, defect tracking, coverage analysis'
        },
        {
            'Question_ID': 'PQ009',
            'Category': 'Documentation',
            'Subcategory': 'Operational Procedures',
            'Question': 'Verify operational support procedures and incident response plans are current and properly documented.',
            'Suggested_Tools': 'Gnosis',
            'Priority': 'Medium',
            'Expected_Evidence': 'Support plans, work instructions, escalation procedures'
        },
        {
            'Question_ID': 'PQ010',
            'Category': 'Access Controls',
            'Subcategory': 'Data Access Patterns',
            'Question': 'Analyze user access patterns to sensitive resources (Database_Config, Security_Logs, Audit_Reports). Identify anomalies and verify business justification.',
            'Suggested_Tools': 'SQL Server, ServiceNow',
            'Priority': 'High',
            'Expected_Evidence': 'Access logs, business justification documents, anomaly reports'
        },
        {
            'Question_ID': 'PQ011',
            'Category': 'Change Management',
            'Subcategory': 'Emergency Changes',
            'Question': 'Review any emergency or expedited changes made to production systems. Verify proper authorization and post-implementation review.',
            'Suggested_Tools': 'ServiceNow, Jira',
            'Priority': 'High',
            'Expected_Evidence': 'Emergency change records, authorization documentation, review reports'
        },
        {
            'Question_ID': 'PQ012',
            'Category': 'Access Controls', 
            'Subcategory': 'Cross-System Access',
            'Question': 'Compare user roles and permissions between SQL Server and Oracle systems. Identify discrepancies and verify consistency with business requirements.',
            'Suggested_Tools': 'SQL Server, Oracle',
            'Priority': 'Medium',
            'Expected_Evidence': 'User role comparisons, business requirement documentation'
        },
        {
            'Question_ID': 'PQ013',
            'Category': 'Quality Assurance',
            'Subcategory': 'Defect Management', 
            'Question': 'Analyze defects related to security and access controls. Verify proper categorization, resolution, and testing validation.',
            'Suggested_Tools': 'Jira, QTest',
            'Priority': 'Medium',
            'Expected_Evidence': 'Defect reports, resolution documentation, validation test results'
        },
        {
            'Question_ID': 'PQ014',
            'Category': 'Documentation',
            'Subcategory': 'Compliance Framework',
            'Question': 'Review documented compliance requirements (SOX, GDPR, ISO 27001) and verify implementation evidence across all systems.',
            'Suggested_Tools': 'Gnosis, SQL Server, ServiceNow',
            'Priority': 'High',
            'Expected_Evidence': 'Compliance documentation, implementation evidence, audit trails'
        }
    ]
    
    return pd.DataFrame(primary_questions)

def create_followup_questions():
    """Create follow-up questions for deeper investigation"""
    
    followup_questions = [
        {
            'Question_ID': 'FQ001',
            'Category': 'Access Controls',
            'Subcategory': 'User Management',
            'Question': 'For users identified with multiple failed access attempts, provide detailed timeline analysis and verify if security incidents were properly escalated.',
            'Suggested_Tools': 'SQL Server, ServiceNow, Jira',
            'Priority': 'High',
            'Expected_Evidence': 'Detailed access logs, incident records, escalation documentation'
        },
        {
            'Question_ID': 'FQ002',
            'Category': 'Change Management',
            'Subcategory': 'Change Impact',
            'Question': 'For database configuration changes, verify impact assessment was performed and rollback procedures were tested.',
            'Suggested_Tools': 'ServiceNow, QTest, Gnosis',
            'Priority': 'High', 
            'Expected_Evidence': 'Impact assessments, rollback test results, procedure documentation'
        },
        {
            'Question_ID': 'FQ003',
            'Category': 'Access Controls',
            'Subcategory': 'Segregation of Duties',
            'Question': 'Analyze user role combinations to identify potential segregation of duties violations, particularly for users with both Developer and Database_Admin roles.',
            'Suggested_Tools': 'SQL Server, Oracle',
            'Priority': 'High',
            'Expected_Evidence': 'Role analysis, segregation matrix, exception approvals'
        },
        {
            'Question_ID': 'FQ004',
            'Category': 'Quality Assurance',
            'Subcategory': 'Test Data Security',
            'Question': 'Verify test executions involving production data followed proper data masking and security protocols.',
            'Suggested_Tools': 'QTest, Gnosis',
            'Priority': 'Medium',
            'Expected_Evidence': 'Test data procedures, masking evidence, security protocols'
        },
        {
            'Question_ID': 'FQ005',
            'Category': 'Documentation',
            'Subcategory': 'Version Control',
            'Question': 'Verify system design documents and work instructions are version-controlled and reflect current system state.',
            'Suggested_Tools': 'Gnosis',
            'Priority': 'Low',
            'Expected_Evidence': 'Document version history, change control records'
        },
        {
            'Question_ID': 'FQ006',
            'Category': 'Change Management',
            'Subcategory': 'Post-Implementation Review',
            'Question': 'For completed changes, verify post-implementation reviews were conducted and lessons learned documented.',
            'Suggested_Tools': 'ServiceNow, Jira',
            'Priority': 'Medium',
            'Expected_Evidence': 'Post-implementation review reports, lessons learned documentation'
        },
        {
            'Question_ID': 'FQ007',
            'Category': 'Access Controls',
            'Subcategory': 'Periodic Access Review',
            'Question': 'Verify quarterly access reviews were performed for all privileged accounts and documented appropriately.',
            'Suggested_Tools': 'SQL Server, Oracle, ServiceNow',
            'Priority': 'High',
            'Expected_Evidence': 'Access review reports, sign-off documentation, remediation records'
        }
    ]
    
    return pd.DataFrame(followup_questions)

def main():
    """Generate enhanced sample audit question sheets"""
    
    print("🔧 Creating Enhanced Sample Audit Question Sheets...")
    
    # Create primary questions
    primary_df = create_primary_questions()
    print(f"✅ Created {len(primary_df)} primary questions")
    
    # Create follow-up questions  
    followup_df = create_followup_questions()
    print(f"✅ Created {len(followup_df)} follow-up questions")
    
    # Save to Excel files
    primary_file = 'SAMPLE_Primary_Audit_Questions_Enhanced.xlsx'
    followup_file = 'SAMPLE_Followup_Audit_Questions_Enhanced.xlsx'
    
    with pd.ExcelWriter(primary_file, engine='openpyxl') as writer:
        primary_df.to_excel(writer, sheet_name='Primary_Questions', index=False)
        
    with pd.ExcelWriter(followup_file, engine='openpyxl') as writer:
        followup_df.to_excel(writer, sheet_name='Followup_Questions', index=False)
    
    print(f"📄 Saved primary questions to: {primary_file}")
    print(f"📄 Saved follow-up questions to: {followup_file}")
    
    # Create summary
    print("\n📊 Enhanced Sample Questions Summary:")
    print(f"   • Primary Questions: {len(primary_df)}")
    print(f"   • Follow-up Questions: {len(followup_df)}")
    print(f"   • Multi-tool Questions: {len(primary_df[primary_df['Suggested_Tools'].str.contains(',')]) + len(followup_df[followup_df['Suggested_Tools'].str.contains(',')])}")
    print("\n🎯 Question Categories Coverage:")
    all_questions = pd.concat([primary_df, followup_df])
    for category in all_questions['Category'].unique():
        count = len(all_questions[all_questions['Category'] == category])
        print(f"   • {category}: {count} questions")
    
    print("\n🔧 Tool Integration Coverage:")
    all_tools = set()
    for tools in all_questions['Suggested_Tools']:
        all_tools.update([tool.strip() for tool in tools.split(',')])
    for tool in sorted(all_tools):
        count = len(all_questions[all_questions['Suggested_Tools'].str.contains(tool)])
        print(f"   • {tool}: {count} questions")

if __name__ == '__main__':
    main()