#!/usr/bin/env python3
"""
Enhanced Veritas GPT Agent with Folder-Based Tool Integration

This module provides an intelligent GPT agent that can:
1. Access CI-specific tool folders automatically
2. Read and analyze tool data files (Excel, text, etc.)
3. Provide context-aware responses using real audit data
4. Execute tool-specific queries for detailed information
"""

import os
import pandas as pd
import json
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

class VeritasGPTAgent:
    """Enhanced Veritas GPT Agent with folder-based tool integration"""
    
    def __init__(self, tools_path: str = "server/tools", openai_api_key: str = None):
        self.tools_path = tools_path
        self.llm = ChatOpenAI(
            api_key=openai_api_key,
            model="gpt-4o",  # Using latest GPT-4o model
            temperature=0.1,
            max_tokens=4000
        )
        
        # Define available tools and their file mappings
        self.tool_mappings = {
            "sql_server": {
                "folder": "SQL_Server",
                "files": ["User_Role.xlsx", "Study.xlsx", "Access_Log.xlsx"],
                "description": "SQL Server database with user roles, studies, and access logs"
            },
            "oracle_db": {
                "folder": "Oracle", 
                "files": ["User_Role.xlsx", "Study.xlsx"],
                "description": "Oracle database with user roles and study data"
            },
            "gnosis": {
                "folder": "Gnosis",
                "files": ["Support_Plan.txt", "Design_Document.txt", "Work_Instructions.txt"],
                "description": "Gnosis document repository with support plans, design docs, and instructions"
            },
            "jira": {
                "folder": "Jira",
                "files": ["jira_tickets.xlsx"],
                "description": "Jira issue tracking system with tickets and project data"
            },
            "qtest": {
                "folder": "QTest",
                "files": ["test_executions.xlsx"],
                "description": "QTest quality assurance system with test execution results"
            },
            "service_now": {
                "folder": "ServiceNow",
                "files": ["change_requests.xlsx"],
                "description": "ServiceNow ITSM platform with change requests and service data"
            }
        }
    
    def get_ci_folder_path(self, ci_id: str) -> str:
        """Get the path to the CI-specific folder"""
        return os.path.join(self.tools_path, ci_id)
    
    def get_available_tools(self, ci_id: str) -> List[Dict[str, Any]]:
        """Get list of available tools for a CI"""
        ci_folder = self.get_ci_folder_path(ci_id)
        available_tools = []
        
        if not os.path.exists(ci_folder):
            return available_tools
            
        for tool_key, tool_info in self.tool_mappings.items():
            tool_folder = os.path.join(ci_folder, tool_info["folder"])
            if os.path.exists(tool_folder):
                files_found = []
                for file_name in tool_info["files"]:
                    file_path = os.path.join(tool_folder, file_name)
                    if os.path.exists(file_path):
                        file_size = os.path.getsize(file_path)
                        files_found.append({
                            "name": file_name,
                            "path": file_path,
                            "size": file_size
                        })
                
                if files_found:
                    available_tools.append({
                        "tool": tool_key,
                        "description": tool_info["description"],
                        "folder": tool_folder,
                        "files": files_found
                    })
        
        return available_tools
    
    def read_excel_file(self, file_path: str) -> Optional[pd.DataFrame]:
        """Read Excel file and return DataFrame"""
        try:
            return pd.read_excel(file_path)
        except Exception as e:
            print(f"Error reading Excel file {file_path}: {e}")
            return None
    
    def read_text_file(self, file_path: str) -> Optional[str]:
        """Read text file and return content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading text file {file_path}: {e}")
            return None
    
    def get_tool_data_summary(self, ci_id: str, tool_key: str) -> Dict[str, Any]:
        """Get summary of data available in a specific tool"""
        tool_info = self.tool_mappings.get(tool_key)
        if not tool_info:
            return {"error": f"Unknown tool: {tool_key}"}
        
        ci_folder = self.get_ci_folder_path(ci_id)
        tool_folder = os.path.join(ci_folder, tool_info["folder"])
        
        if not os.path.exists(tool_folder):
            return {"error": f"Tool folder not found: {tool_folder}"}
        
        summary = {
            "tool": tool_key,
            "description": tool_info["description"],
            "files": []
        }
        
        for file_name in tool_info["files"]:
            file_path = os.path.join(tool_folder, file_name)
            if os.path.exists(file_path):
                file_info = {
                    "name": file_name,
                    "size": os.path.getsize(file_path),
                    "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                }
                
                # Get data preview
                if file_name.endswith('.xlsx'):
                    df = self.read_excel_file(file_path)
                    if df is not None:
                        file_info["rows"] = len(df)
                        file_info["columns"] = list(df.columns)
                        file_info["sample_data"] = df.head(3).to_dict('records')
                elif file_name.endswith('.txt'):
                    content = self.read_text_file(file_path)
                    if content:
                        file_info["lines"] = len(content.split('\n'))
                        file_info["preview"] = content[:500] + "..." if len(content) > 500 else content
                
                summary["files"].append(file_info)
        
        return summary
    
    def search_tool_data(self, ci_id: str, query: str, tools: List[str] = None) -> Dict[str, Any]:
        """Search for data across specified tools or all available tools"""
        if tools is None:
            available_tools = self.get_available_tools(ci_id)
            tools = [tool["tool"] for tool in available_tools]
        
        search_results = {
            "query": query,
            "tools_searched": tools,
            "results": []
        }
        
        for tool_key in tools:
            tool_data = self.get_tool_data_summary(ci_id, tool_key)
            if "error" not in tool_data:
                # Analyze tool data with LLM for relevance to query
                tool_analysis = self.analyze_tool_data_for_query(tool_data, query)
                if tool_analysis.get("relevant", False):
                    search_results["results"].append({
                        "tool": tool_key,
                        "relevance_score": tool_analysis.get("score", 0),
                        "relevant_files": tool_analysis.get("relevant_files", []),
                        "summary": tool_analysis.get("summary", ""),
                        "data": tool_data
                    })
        
        # Sort by relevance score
        search_results["results"].sort(key=lambda x: x["relevance_score"], reverse=True)
        return search_results
    
    def analyze_tool_data_for_query(self, tool_data: Dict[str, Any], query: str) -> Dict[str, Any]:
        """Use LLM to analyze if tool data is relevant to the query"""
        try:
            system_prompt = """You are an expert data analyst. Analyze the provided tool data to determine its relevance to the user's query.

Return a JSON response with:
- relevant: boolean (true if tool data is relevant to the query)
- score: integer 1-10 (relevance score, 10 being most relevant)
- relevant_files: array of file names that are most relevant
- summary: string (brief explanation of relevance)

Consider the tool description, file names, column names, and sample data."""

            human_prompt = f"""Query: {query}

Tool Data: {json.dumps(tool_data, indent=2)}

Analyze relevance:"""

            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template(human_prompt)
            ])
            
            formatted_prompt = prompt.format_messages(query=query, tool_data=json.dumps(tool_data, indent=2))
            response = self.llm.invoke(formatted_prompt)
            
            return json.loads(response.content)
            
        except Exception as e:
            print(f"Error analyzing tool data relevance: {e}")
            return {"relevant": False, "score": 0, "relevant_files": [], "summary": "Analysis failed"}
    
    def generate_context_aware_response(self, ci_id: str, user_message: str, conversation_history: List[Dict] = None) -> Dict[str, Any]:
        """Generate a context-aware response using available tool data"""
        
        # Get available tools for this CI
        available_tools = self.get_available_tools(ci_id)
        
        if not available_tools:
            return {
                "response": f"I don't have access to tool data for CI {ci_id}. Please ensure the tool folders are properly set up.",
                "tools_used": [],
                "thinking_steps": ["No tool data available"]
            }
        
        # Search for relevant tool data
        search_results = self.search_tool_data(ci_id, user_message)
        
        thinking_steps = [
            f"Scanning {len(available_tools)} available tools",
            f"Found {len(search_results['results'])} relevant data sources",
            "Analyzing tool data for context",
            "Generating comprehensive response"
        ]
        
        # Build context from relevant tools
        context_sections = []
        tools_used = []
        
        for result in search_results["results"][:3]:  # Use top 3 most relevant tools
            tool_key = result["tool"]
            tools_used.append(tool_key)
            
            context_sections.append(f"**{tool_key.upper()} Data:**")
            context_sections.append(result["summary"])
            
            # Add specific file data for context
            for file_info in result["data"]["files"][:2]:  # Max 2 files per tool
                if "sample_data" in file_info:
                    context_sections.append(f"Sample from {file_info['name']}:")
                    context_sections.append(str(file_info["sample_data"][:3]))
                elif "preview" in file_info:
                    context_sections.append(f"Content from {file_info['name']}:")
                    context_sections.append(file_info["preview"][:300])
        
        # Create comprehensive system prompt
        system_prompt = f"""You are Veritas GPT, an expert audit analyst with access to comprehensive audit data for CI {ci_id}.

AVAILABLE TOOLS AND DATA:
{chr(10).join([f"- {tool['tool']}: {tool['description']}" for tool in available_tools])}

RELEVANT CONTEXT FOR THIS QUERY:
{chr(10).join(context_sections)}

INSTRUCTIONS:
1. Provide accurate, data-driven responses based on the available tool data
2. Reference specific data points and findings when relevant
3. If you need more specific data, suggest which tools to examine
4. Be comprehensive but concise
5. Highlight any potential audit concerns or compliance issues
6. Use professional audit terminology

CONVERSATION HISTORY:
{json.dumps(conversation_history[-5:] if conversation_history else [], indent=2)}"""

        try:
            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(system_prompt),
                HumanMessagePromptTemplate.from_template("{user_message}")
            ])
            
            formatted_prompt = prompt.format_messages(user_message=user_message)
            response = self.llm.invoke(formatted_prompt)
            
            return {
                "response": response.content,
                "tools_used": tools_used,
                "thinking_steps": thinking_steps,
                "context_summary": f"Analyzed data from {len(tools_used)} tools: {', '.join(tools_used)}",
                "available_tools": [tool["tool"] for tool in available_tools]
            }
            
        except Exception as e:
            return {
                "response": f"I encountered an error while analyzing the data: {str(e)}. However, I have access to data from these tools: {', '.join([tool['tool'] for tool in available_tools])}. Please try rephrasing your question.",
                "tools_used": [],
                "thinking_steps": thinking_steps + ["Error occurred during analysis"],
                "error": str(e)
            }

def create_veritas_agent(openai_api_key: str) -> VeritasGPTAgent:
    """Factory function to create a Veritas GPT agent"""
    return VeritasGPTAgent(openai_api_key=openai_api_key)