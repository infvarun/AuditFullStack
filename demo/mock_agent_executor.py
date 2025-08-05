#!/usr/bin/env python3
"""
Mock Agent Executor for Demo

This module simulates the AI agent execution process that collects data
from mock connectors and generates realistic audit findings.
"""

import json
import time
import random
from datetime import datetime
from typing import Dict, List, Any, Optional
from mock_connectors import query_data, get_connector

class MockAgentExecutor:
    """
    Simulates AI agent execution for data collection and analysis
    """
    
    def __init__(self):
        self.execution_history = []
        
    def execute_data_collection(self, question_analysis: Dict[str, Any], 
                               progress_callback=None) -> Dict[str, Any]:
        """
        Execute data collection for a single question analysis
        
        Args:
            question_analysis: Analysis containing tool suggestions and prompts
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary containing execution results and findings
        """
        start_time = datetime.now()
        execution_id = f"EXEC_{int(time.time())}_{random.randint(1000, 9999)}"
        
        # Extract tool suggestions (handle both single and multiple tools)
        tools = question_analysis.get('toolSuggestion', [])
        if not isinstance(tools, list):
            tools = [tools]
        
        if progress_callback:
            progress_callback(f"Starting data collection for question: {question_analysis.get('questionId', 'Unknown')}")
        
        # Collect data from each tool
        collected_data = {}
        findings = []
        
        for i, tool in enumerate(tools):
            if progress_callback:
                progress_callback(f"Querying {tool} ({i+1}/{len(tools)})")
            
            # Simulate processing time
            time.sleep(random.uniform(0.5, 1.5))
            
            # Collect data based on tool type and question content
            tool_data = self._collect_tool_data(tool, question_analysis)
            collected_data[tool] = tool_data
            
            # Generate findings for this tool
            tool_findings = self._generate_findings(tool, tool_data, question_analysis)
            findings.extend(tool_findings)
        
        if progress_callback:
            progress_callback("Analyzing collected data and generating report")
        
        # Generate comprehensive analysis
        analysis_result = self._generate_analysis(collected_data, findings, question_analysis)
        
        execution_result = {
            'executionId': execution_id,
            'questionId': question_analysis.get('questionId', ''),
            'originalQuestion': question_analysis.get('originalQuestion', ''),
            'toolsUsed': tools,
            'startTime': start_time.isoformat(),
            'endTime': datetime.now().isoformat(),
            'duration': (datetime.now() - start_time).total_seconds(),
            'collectedData': collected_data,
            'findings': findings,
            'analysis': analysis_result,
            'status': 'completed',
            'dataPoints': sum(len(data) if isinstance(data, list) else 1 for data in collected_data.values()),
            'riskLevel': analysis_result.get('riskLevel', 'Low'),
            'complianceStatus': analysis_result.get('complianceStatus', 'Compliant')
        }
        
        self.execution_history.append(execution_result)
        
        if progress_callback:
            progress_callback(f"Data collection completed. Found {execution_result['dataPoints']} data points.")
        
        return execution_result
    
    def _collect_tool_data(self, tool: str, question_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Collect data from specific tool based on question context"""
        question_text = question_analysis.get('originalQuestion', '').lower()
        
        if tool == "SQL Server DB":
            if any(term in question_text for term in ['user', 'access', 'permission', 'login', 'account']):
                return query_data(tool, "users", status="Active")
            elif any(term in question_text for term in ['audit', 'log', 'activity', 'tracking']):
                return query_data(tool, "audit_logs", hours_back=168)  # Last week
            else:
                return query_data(tool, "users")[:10]  # Default sample
                
        elif tool == "Oracle DB":
            if any(term in question_text for term in ['transaction', 'financial', 'payment', 'expense']):
                return query_data(tool, "transactions", amount_threshold=1000)
            elif any(term in question_text for term in ['compliance', 'control', 'sox', 'gdpr']):
                return query_data(tool, "compliance")
            else:
                return query_data(tool, "transactions")[:15]
                
        elif tool == "Gnosis Document Repository":
            if any(term in question_text for term in ['policy', 'procedure', 'documentation']):
                return query_data(tool, "documents", category="Policy")
            elif any(term in question_text for term in ['security', 'access', 'control']):
                return query_data(tool, "documents", tags=["security"])
            elif any(term in question_text for term in ['compliance', 'audit']):
                return query_data(tool, "documents", tags=["compliance", "audit"])
            else:
                return query_data(tool, "documents", query=question_text.split()[:3])
                
        elif tool == "Jira":
            if any(term in question_text for term in ['security', 'vulnerability', 'incident']):
                return query_data(tool, "tickets", component="Security")
            elif any(term in question_text for term in ['critical', 'high priority']):
                return query_data(tool, "tickets", priority="High")
            elif any(term in question_text for term in ['open', 'unresolved']):
                return query_data(tool, "tickets", status="In Progress")
            else:
                return query_data(tool, "tickets")[:12]
                
        elif tool == "QTest":
            if any(term in question_text for term in ['test', 'testing', 'quality', 'qa']):
                return query_data(tool, "test_results", result="Pass")
            elif any(term in question_text for term in ['security', 'authentication']):
                return query_data(tool, "test_results", coverage_area="Authentication")
            elif any(term in question_text for term in ['fail', 'defect', 'issue']):
                return query_data(tool, "test_results", result="Fail")
            else:
                return query_data(tool, "test_results")[:10]
                
        elif tool == "ServiceNow":
            if any(term in question_text for term in ['incident', 'issue', 'problem']):
                return query_data(tool, "incidents", category="Incident")
            elif any(term in question_text for term in ['security', 'breach', 'violation']):
                return query_data(tool, "incidents", priority="High")
            elif any(term in question_text for term in ['service', 'request']):
                return query_data(tool, "incidents", category="Service Request")
            else:
                return query_data(tool, "incidents")[:10]
        
        return []
    
    def _generate_findings(self, tool: str, data: List[Dict[str, Any]], 
                          question_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate realistic findings based on collected data"""
        if not data:
            return [{
                'tool': tool,
                'finding': f"No relevant data found in {tool}",
                'severity': 'Info',
                'details': 'Data collection completed but no matching records were identified.'
            }]
        
        findings = []
        
        if tool == "SQL Server DB":
            active_users = [u for u in data if u.get('account_status') == 'Active']
            locked_users = [u for u in data if u.get('account_status') == 'Locked']
            
            findings.append({
                'tool': tool,
                'finding': f"User Account Analysis: {len(active_users)} active users, {len(locked_users)} locked accounts",
                'severity': 'Info',
                'details': f"Total users analyzed: {len(data)}. Account status distribution shows normal patterns.",
                'metrics': {
                    'total_users': len(data),
                    'active_users': len(active_users),
                    'locked_users': len(locked_users)
                }
            })
            
            if locked_users:
                findings.append({
                    'tool': tool,
                    'finding': f"Locked accounts require review: {len(locked_users)} accounts locked",
                    'severity': 'Medium',
                    'details': "Locked accounts should be reviewed for potential security incidents or administrative cleanup.",
                    'affected_accounts': [u['username'] for u in locked_users[:5]]
                })
        
        elif tool == "Oracle DB":
            if 'amount' in str(data[0]) if data else False:
                high_value = [t for t in data if t.get('amount', 0) > 10000]
                pending_approvals = [t for t in data if t.get('status') == 'Pending']
                
                findings.append({
                    'tool': tool,
                    'finding': f"Financial Transaction Review: {len(data)} transactions analyzed",
                    'severity': 'Info',
                    'details': f"High-value transactions: {len(high_value)}, Pending approvals: {len(pending_approvals)}",
                    'metrics': {
                        'total_transactions': len(data),
                        'high_value_transactions': len(high_value),
                        'pending_approvals': len(pending_approvals)
                    }
                })
            else:
                compliant = [r for r in data if r.get('status') == 'Compliant']
                non_compliant = [r for r in data if r.get('status') == 'Non-Compliant']
                
                findings.append({
                    'tool': tool,
                    'finding': f"Compliance Status: {len(compliant)} compliant controls, {len(non_compliant)} non-compliant",
                    'severity': 'High' if non_compliant else 'Info',
                    'details': f"Compliance assessment shows {len(compliant)}/{len(data)} controls in compliant status.",
                    'non_compliant_controls': [r['control_id'] for r in non_compliant[:3]]
                })
        
        elif tool == "Gnosis Document Repository":
            approved_docs = [d for d in data if d.get('approval_status') == 'Approved']
            draft_docs = [d for d in data if d.get('approval_status') == 'Draft']
            
            findings.append({
                'tool': tool,
                'finding': f"Document Review: {len(approved_docs)} approved documents, {len(draft_docs)} in draft",
                'severity': 'Info',
                'details': f"Document repository contains {len(data)} relevant documents. Approval status tracked.",
                'document_categories': list(set(d.get('category', 'Unknown') for d in data))
            })
        
        elif tool == "Jira":
            open_tickets = [t for t in data if t.get('status') in ['Open', 'In Progress']]
            high_priority = [t for t in data if t.get('priority') == 'High']
            
            findings.append({
                'tool': tool,
                'finding': f"Project Tracking: {len(open_tickets)} open tickets, {len(high_priority)} high priority",
                'severity': 'Medium' if high_priority else 'Info',
                'details': f"Issue tracking shows {len(data)} total tickets with {len(open_tickets)} still active.",
                'high_priority_tickets': [t['ticket_id'] for t in high_priority[:3]]
            })
        
        elif tool == "QTest":
            passed_tests = [t for t in data if t.get('result') == 'Pass']
            failed_tests = [t for t in data if t.get('result') == 'Fail']
            
            findings.append({
                'tool': tool,
                'finding': f"Quality Assurance: {len(passed_tests)} passed tests, {len(failed_tests)} failed tests",
                'severity': 'High' if failed_tests else 'Info',
                'details': f"Test execution results: {len(passed_tests)}/{len(data)} tests passed successfully.",
                'test_coverage': list(set(t.get('coverage_area', 'Unknown') for t in data))
            })
        
        elif tool == "ServiceNow":
            resolved_tickets = [t for t in data if t.get('status') == 'Resolved']
            critical_incidents = [t for t in data if t.get('priority') == 'Critical']
            
            findings.append({
                'tool': tool,
                'finding': f"Service Management: {len(resolved_tickets)} resolved tickets, {len(critical_incidents)} critical incidents",
                'severity': 'High' if critical_incidents else 'Info',
                'details': f"ITSM analysis shows {len(data)} service tickets with resolution tracking.",
                'avg_resolution_time': sum(t.get('resolution_time_hours', 0) for t in resolved_tickets) / max(len(resolved_tickets), 1)
            })
        
        return findings
    
    def _generate_analysis(self, collected_data: Dict[str, List], findings: List[Dict[str, Any]], 
                          question_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive analysis of all collected data"""
        
        # Determine overall risk level
        severity_counts = {}
        for finding in findings:
            severity = finding.get('severity', 'Info')
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        if severity_counts.get('High', 0) > 0:
            risk_level = 'High'
            compliance_status = 'Non-Compliant'
        elif severity_counts.get('Medium', 0) > 1:
            risk_level = 'Medium'
            compliance_status = 'Partially Compliant'
        else:
            risk_level = 'Low'
            compliance_status = 'Compliant'
        
        # Generate executive summary
        total_data_points = sum(len(data) for data in collected_data.values())
        tools_used = list(collected_data.keys())
        
        summary = f"Comprehensive audit analysis completed using {len(tools_used)} data sources. "
        summary += f"Analyzed {total_data_points} data points across {', '.join(tools_used)}. "
        
        if risk_level == 'High':
            summary += "Critical issues identified requiring immediate attention."
        elif risk_level == 'Medium':
            summary += "Some areas require improvement and monitoring."
        else:
            summary += "Overall compliance posture is satisfactory."
        
        # Generate recommendations
        recommendations = []
        if severity_counts.get('High', 0) > 0:
            recommendations.append("Address high-severity findings within 30 days")
            recommendations.append("Implement additional control monitoring")
        if severity_counts.get('Medium', 0) > 0:
            recommendations.append("Review and remediate medium-risk items")
            recommendations.append("Establish regular review cycles")
        
        recommendations.append("Continue regular monitoring and assessment")
        recommendations.append("Update documentation to reflect current state")
        
        return {
            'executiveSummary': summary,
            'riskLevel': risk_level,
            'complianceStatus': compliance_status,
            'totalDataPoints': total_data_points,
            'toolsAnalyzed': len(tools_used),
            'findingsSummary': {
                'total': len(findings),
                'by_severity': severity_counts
            },
            'recommendations': recommendations,
            'nextReviewDate': (datetime.now().replace(month=datetime.now().month + 3)).strftime("%Y-%m-%d"),
            'confidence': random.uniform(0.85, 0.98)  # Simulated confidence score
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """Get history of all executions"""
        return self.execution_history
    
    def get_execution_by_id(self, execution_id: str) -> Optional[Dict[str, Any]]:
        """Get specific execution by ID"""
        for execution in self.execution_history:
            if execution['executionId'] == execution_id:
                return execution
        return None
    
    def simulate_batch_execution(self, question_analyses: List[Dict[str, Any]], 
                                progress_callback=None) -> List[Dict[str, Any]]:
        """Simulate batch execution of multiple questions"""
        results = []
        total = len(question_analyses)
        
        for i, analysis in enumerate(question_analyses):
            if progress_callback:
                progress_callback(f"Processing question {i+1}/{total}: {analysis.get('questionId', 'Unknown')}")
            
            result = self.execute_data_collection(analysis, progress_callback)
            results.append(result)
            
            # Small delay between executions
            time.sleep(0.5)
        
        if progress_callback:
            progress_callback(f"Batch execution completed. Processed {len(results)} questions.")
        
        return results

# Global instance for demo
demo_agent = MockAgentExecutor()