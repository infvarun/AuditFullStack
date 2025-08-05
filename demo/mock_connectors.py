#!/usr/bin/env python3
"""
Mock Connectors for Demo

This module provides realistic mock endpoints that simulate various data sources
for demonstration purposes. Each connector returns authentic-looking data that
would come from real enterprise systems.
"""

import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid

@dataclass
class User:
    user_id: str
    username: str
    full_name: str
    email: str
    department: str
    role: str
    last_login: str
    account_status: str
    permissions: List[str]
    created_date: str

@dataclass
class Document:
    doc_id: str
    title: str
    category: str
    version: str
    last_updated: str
    owner: str
    content_summary: str
    approval_status: str
    tags: List[str]

@dataclass
class JiraTicket:
    ticket_id: str
    summary: str
    status: str
    priority: str
    assignee: str
    reporter: str
    created: str
    updated: str
    resolution: Optional[str]
    components: List[str]

@dataclass
class TestCase:
    test_id: str
    name: str
    status: str
    test_type: str
    execution_date: str
    result: str
    defects_found: int
    coverage_area: str
    tester: str

@dataclass
class ServiceTicket:
    ticket_id: str
    title: str
    category: str
    status: str
    priority: str
    requester: str
    assigned_to: str
    created_date: str
    resolved_date: Optional[str]
    resolution_time_hours: Optional[int]

class MockSQLServerConnector:
    """Mock SQL Server database connector"""
    
    def __init__(self):
        self.users = self._generate_users()
        self.audit_logs = self._generate_audit_logs()
        
    def _generate_users(self) -> List[User]:
        departments = ["IT", "Finance", "HR", "Operations", "Security", "Compliance"]
        roles = ["Administrator", "Manager", "Analyst", "Developer", "Auditor", "User"]
        statuses = ["Active", "Inactive", "Locked", "Pending"]
        
        users = []
        for i in range(50):
            user = User(
                user_id=f"USR{i+1000:04d}",
                username=f"user{i+1:03d}",
                full_name=f"Employee User{i+1:03d}",
                email=f"user{i+1:03d}@company.com",
                department=random.choice(departments),
                role=random.choice(roles),
                last_login=(datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S"),
                account_status=random.choice(statuses),
                permissions=random.sample(["READ", "WRITE", "DELETE", "ADMIN", "AUDIT"], random.randint(1, 3)),
                created_date=(datetime.now() - timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d")
            )
            users.append(user)
        return users
    
    def _generate_audit_logs(self) -> List[Dict[str, Any]]:
        actions = ["Login", "Logout", "File Access", "Data Export", "Config Change", "Password Reset"]
        results = ["Success", "Failed", "Blocked"]
        
        logs = []
        for i in range(200):
            log = {
                "log_id": f"LOG{i+1:06d}",
                "user_id": f"USR{random.randint(1000, 1049):04d}",
                "action": random.choice(actions),
                "timestamp": (datetime.now() - timedelta(hours=random.randint(0, 720))).strftime("%Y-%m-%d %H:%M:%S"),
                "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
                "result": random.choice(results),
                "details": f"System access from workstation {random.randint(1, 100)}"
            }
            logs.append(log)
        return logs
    
    def query_users(self, filter_criteria: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Query user data with optional filtering"""
        results = [asdict(user) for user in self.users]
        
        if filter_criteria:
            if "department" in filter_criteria:
                results = [u for u in results if u["department"] == filter_criteria["department"]]
            if "status" in filter_criteria:
                results = [u for u in results if u["account_status"] == filter_criteria["status"]]
            if "role" in filter_criteria:
                results = [u for u in results if u["role"] == filter_criteria["role"]]
        
        return results
    
    def query_audit_logs(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """Query audit logs from the last N hours"""
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        return [log for log in self.audit_logs 
                if datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S") >= cutoff_time]

class MockOracleConnector:
    """Mock Oracle database connector for enterprise data"""
    
    def __init__(self):
        self.financial_transactions = self._generate_financial_data()
        self.compliance_records = self._generate_compliance_data()
    
    def _generate_financial_data(self) -> List[Dict[str, Any]]:
        transaction_types = ["Purchase", "Payment", "Transfer", "Adjustment", "Refund"]
        departments = ["IT", "Finance", "HR", "Operations", "Marketing"]
        
        transactions = []
        for i in range(100):
            transaction = {
                "transaction_id": f"TXN{i+10000:06d}",
                "amount": round(random.uniform(100, 50000), 2),
                "type": random.choice(transaction_types),
                "department": random.choice(departments),
                "date": (datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
                "approved_by": f"MGR{random.randint(1, 10):03d}",
                "vendor": f"Vendor-{random.randint(1, 20)}",
                "status": random.choice(["Approved", "Pending", "Rejected"])
            }
            transactions.append(transaction)
        return transactions
    
    def _generate_compliance_data(self) -> List[Dict[str, Any]]:
        compliance_areas = ["SOX", "GDPR", "HIPAA", "PCI-DSS", "ISO27001"]
        statuses = ["Compliant", "Non-Compliant", "In Progress", "Not Assessed"]
        
        records = []
        for area in compliance_areas:
            for i in range(20):
                record = {
                    "control_id": f"{area}-CTRL-{i+1:03d}",
                    "area": area,
                    "description": f"{area} compliance control {i+1}",
                    "status": random.choice(statuses),
                    "last_assessment": (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d"),
                    "assessor": f"AUD{random.randint(1, 5):03d}",
                    "risk_level": random.choice(["Low", "Medium", "High"]),
                    "remediation_due": (datetime.now() + timedelta(days=random.randint(30, 180))).strftime("%Y-%m-%d") if random.choice([True, False]) else None
                }
                records.append(record)
        return records
    
    def query_transactions(self, department: str = None, amount_threshold: float = None) -> List[Dict[str, Any]]:
        """Query financial transactions"""
        results = self.financial_transactions.copy()
        
        if department:
            results = [t for t in results if t["department"] == department]
        if amount_threshold:
            results = [t for t in results if t["amount"] >= amount_threshold]
        
        return results
    
    def query_compliance_status(self, area: str = None) -> List[Dict[str, Any]]:
        """Query compliance records"""
        results = self.compliance_records.copy()
        
        if area:
            results = [r for r in results if r["area"] == area]
        
        return results

class MockGnosisConnector:
    """Mock Gnosis document repository connector"""
    
    def __init__(self):
        self.documents = self._generate_documents()
    
    def _generate_documents(self) -> List[Document]:
        categories = ["Policy", "Procedure", "Standard", "Guideline", "Manual"]
        statuses = ["Approved", "Draft", "Under Review", "Archived"]
        
        doc_titles = [
            "Information Security Policy", "Data Retention Policy", "Access Control Procedure",
            "Incident Response Plan", "Business Continuity Manual", "Risk Management Framework",
            "Vendor Management Procedure", "Change Management Policy", "Backup and Recovery Standard",
            "Employee Handbook", "Code of Conduct", "Privacy Policy", "Audit Policy",
            "IT Security Standards", "Compliance Manual", "Training Guidelines"
        ]
        
        documents = []
        for i, title in enumerate(doc_titles):
            doc = Document(
                doc_id=f"DOC{i+1000:04d}",
                title=title,
                category=random.choice(categories),
                version=f"{random.randint(1, 5)}.{random.randint(0, 9)}",
                last_updated=(datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d"),
                owner=f"Owner{random.randint(1, 10)}",
                content_summary=f"This document covers {title.lower()} requirements and procedures for organizational compliance.",
                approval_status=random.choice(statuses),
                tags=random.sample(["security", "compliance", "policy", "procedure", "training", "audit"], random.randint(2, 4))
            )
            documents.append(doc)
        return documents
    
    def search_documents(self, query: str = "", category: str = None, tags: List[str] = None) -> List[Dict[str, Any]]:
        """Search documents by query, category, or tags"""
        results = [asdict(doc) for doc in self.documents]
        
        if query:
            query_lower = query.lower()
            results = [d for d in results if query_lower in d["title"].lower() or query_lower in d["content_summary"].lower()]
        
        if category:
            results = [d for d in results if d["category"] == category]
        
        if tags:
            results = [d for d in results if any(tag in d["tags"] for tag in tags)]
        
        return results

class MockJiraConnector:
    """Mock Jira project management connector"""
    
    def __init__(self):
        self.tickets = self._generate_tickets()
    
    def _generate_tickets(self) -> List[JiraTicket]:
        statuses = ["Open", "In Progress", "Resolved", "Closed", "On Hold"]
        priorities = ["Low", "Medium", "High", "Critical"]
        components = ["Security", "Infrastructure", "Application", "Database", "Network"]
        
        ticket_summaries = [
            "Security vulnerability in authentication system",
            "Database performance optimization required",
            "Implement new access control features",
            "Update compliance documentation",
            "Fix backup system errors",
            "Upgrade security monitoring tools",
            "Review user access permissions",
            "Patch management deployment",
            "Network security assessment",
            "Data encryption implementation"
        ]
        
        tickets = []
        for i, summary in enumerate(ticket_summaries):
            ticket = JiraTicket(
                ticket_id=f"SEC-{i+100}",
                summary=summary,
                status=random.choice(statuses),
                priority=random.choice(priorities),
                assignee=f"dev{random.randint(1, 10)}@company.com",
                reporter=f"manager{random.randint(1, 5)}@company.com",
                created=(datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d"),
                updated=(datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
                resolution="Fixed" if random.choice([True, False]) else None,
                components=random.sample(components, random.randint(1, 2))
            )
            tickets.append(ticket)
        return tickets
    
    def query_tickets(self, status: str = None, priority: str = None, component: str = None) -> List[Dict[str, Any]]:
        """Query Jira tickets with filters"""
        results = [asdict(ticket) for ticket in self.tickets]
        
        if status:
            results = [t for t in results if t["status"] == status]
        if priority:
            results = [t for t in results if t["priority"] == priority]
        if component:
            results = [t for t in results if component in t["components"]]
        
        return results

class MockQTestConnector:
    """Mock QTest quality assurance connector"""
    
    def __init__(self):
        self.test_cases = self._generate_test_cases()
    
    def _generate_test_cases(self) -> List[TestCase]:
        test_types = ["Unit", "Integration", "Security", "Performance", "User Acceptance"]
        results = ["Pass", "Fail", "Blocked", "Not Executed"]
        coverage_areas = ["Authentication", "Authorization", "Data Validation", "API", "UI", "Database"]
        
        test_names = [
            "User login authentication test",
            "Password complexity validation",
            "Access control verification",
            "Data encryption validation",
            "Session management test",
            "Input sanitization check",
            "SQL injection prevention",
            "Cross-site scripting protection",
            "File upload security test",
            "Audit trail verification"
        ]
        
        test_cases = []
        for i, name in enumerate(test_names):
            test = TestCase(
                test_id=f"TC{i+1000:04d}",
                name=name,
                status=random.choice(["Active", "Inactive", "Under Review"]),
                test_type=random.choice(test_types),
                execution_date=(datetime.now() - timedelta(days=random.randint(0, 60))).strftime("%Y-%m-%d"),
                result=random.choice(results),
                defects_found=random.randint(0, 5),
                coverage_area=random.choice(coverage_areas),
                tester=f"tester{random.randint(1, 8)}@company.com"
            )
            test_cases.append(test)
        return test_cases
    
    def query_test_results(self, test_type: str = None, result: str = None, coverage_area: str = None) -> List[Dict[str, Any]]:
        """Query test cases with filters"""
        results = [asdict(test) for test in self.test_cases]
        
        if test_type:
            results = [t for t in results if t["test_type"] == test_type]
        if result:
            results = [t for t in results if t["result"] == result]
        if coverage_area:
            results = [t for t in results if t["coverage_area"] == coverage_area]
        
        return results

class MockServiceNowConnector:
    """Mock ServiceNow ITSM connector"""
    
    def __init__(self):
        self.tickets = self._generate_service_tickets()
    
    def _generate_service_tickets(self) -> List[ServiceTicket]:
        categories = ["Incident", "Service Request", "Change Request", "Problem"]
        statuses = ["New", "In Progress", "Resolved", "Closed", "On Hold"]
        priorities = ["Low", "Medium", "High", "Critical"]
        
        ticket_titles = [
            "Password reset request",
            "System outage investigation",
            "Software installation request",
            "Network connectivity issue",
            "Security incident response",
            "Hardware replacement request",
            "Access permission change",
            "Backup restoration request",
            "Performance degradation issue",
            "Security policy violation"
        ]
        
        tickets = []
        for i, title in enumerate(ticket_titles):
            resolved_date = None
            resolution_time = None
            if random.choice([True, False]):
                resolved_date = (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d")
                resolution_time = random.randint(1, 72)
            
            ticket = ServiceTicket(
                ticket_id=f"INC{i+10000:06d}",
                title=title,
                category=random.choice(categories),
                status=random.choice(statuses),
                priority=random.choice(priorities),
                requester=f"user{random.randint(1, 50):03d}@company.com",
                assigned_to=f"support{random.randint(1, 10)}@company.com",
                created_date=(datetime.now() - timedelta(days=random.randint(0, 90))).strftime("%Y-%m-%d"),
                resolved_date=resolved_date,
                resolution_time_hours=resolution_time
            )
            tickets.append(ticket)
        return tickets
    
    def query_incidents(self, category: str = None, status: str = None, priority: str = None) -> List[Dict[str, Any]]:
        """Query ServiceNow tickets with filters"""
        results = [asdict(ticket) for ticket in self.tickets]
        
        if category:
            results = [t for t in results if t["category"] == category]
        if status:
            results = [t for t in results if t["status"] == status]
        if priority:
            results = [t for t in results if t["priority"] == priority]
        
        return results

# Global instances for demo
mock_connectors = {
    "SQL Server DB": MockSQLServerConnector(),
    "Oracle DB": MockOracleConnector(),
    "Gnosis Document Repository": MockGnosisConnector(),
    "Jira": MockJiraConnector(),
    "QTest": MockQTestConnector(),
    "ServiceNow": MockServiceNowConnector()
}

def get_connector(connector_type: str):
    """Get mock connector instance by type"""
    return mock_connectors.get(connector_type)

def query_data(connector_type: str, query_type: str, **kwargs) -> List[Dict[str, Any]]:
    """
    Generic function to query data from mock connectors
    
    Args:
        connector_type: Type of connector (SQL Server DB, Oracle DB, etc.)
        query_type: Type of query (users, documents, tickets, etc.)
        **kwargs: Additional query parameters
    
    Returns:
        List of dictionaries containing query results
    """
    connector = get_connector(connector_type)
    if not connector:
        return []
    
    # Route queries to appropriate methods
    if connector_type == "SQL Server DB":
        if query_type == "users":
            return connector.query_users(kwargs)
        elif query_type == "audit_logs":
            return connector.query_audit_logs(kwargs.get("hours_back", 24))
            
    elif connector_type == "Oracle DB":
        if query_type == "transactions":
            return connector.query_transactions(
                kwargs.get("department"), 
                kwargs.get("amount_threshold")
            )
        elif query_type == "compliance":
            return connector.query_compliance_status(kwargs.get("area"))
            
    elif connector_type == "Gnosis Document Repository":
        if query_type == "documents":
            return connector.search_documents(
                kwargs.get("query", ""),
                kwargs.get("category"),
                kwargs.get("tags")
            )
            
    elif connector_type == "Jira":
        if query_type == "tickets":
            return connector.query_tickets(
                kwargs.get("status"),
                kwargs.get("priority"),
                kwargs.get("component")
            )
            
    elif connector_type == "QTest":
        if query_type == "test_results":
            return connector.query_test_results(
                kwargs.get("test_type"),
                kwargs.get("result"),
                kwargs.get("coverage_area")
            )
            
    elif connector_type == "ServiceNow":
        if query_type == "incidents":
            return connector.query_incidents(
                kwargs.get("category"),
                kwargs.get("status"),
                kwargs.get("priority")
            )
    
    return []