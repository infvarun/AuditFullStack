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
    
    def __init__(self, tools_path: str = "server/tools", llm=None):
        # Ensure absolute path for tools directory
        if not os.path.isabs(tools_path):
            # Get the directory where this script is located and construct path from there
            current_dir = os.path.dirname(os.path.abspath(__file__))
            self.tools_path = os.path.join(current_dir, "tools")
        else:
            self.tools_path = tools_path
            
        # Use existing LangChain LLM from Flask app instead of creating new one
        if llm is None:
            raise ValueError("LLM instance is required. Pass the configured LangChain LLM from Flask app.")
        self.llm = llm
        
        # Define available tools - simplified approach, just folder names
        self.tool_mappings = {
            "sql_server": {
                "folder": "SQL_Server",
                "description": "SQL Server database system"
            },
            "oracle_db": {
                "folder": "Oracle", 
                "description": "Oracle database system"
            },
            "gnosis": {
                "folder": "Gnosis",
                "description": "Gnosis document management system"
            },
            "jira": {
                "folder": "Jira",
                "description": "Jira issue tracking system"
            },
            "qtest": {
                "folder": "QTest",
                "description": "QTest quality assurance system"
            },
            "service_now": {
                "folder": "ServiceNow",
                "description": "ServiceNow ITSM platform"
            }
        }
    
    def get_ci_folder_path(self, ci_id: str) -> str:
        """Get the path to the CI-specific folder"""
        return os.path.join(self.tools_path, ci_id)
    
    def get_available_tools(self, ci_id: str) -> List[Dict[str, Any]]:
        """Get list of available tools for a CI by scanning all files in tool folders"""
        ci_folder = self.get_ci_folder_path(ci_id)
        available_tools = []
        
        if not os.path.exists(ci_folder):
            return available_tools
            
        for tool_key, tool_info in self.tool_mappings.items():
            tool_folder = os.path.join(ci_folder, tool_info["folder"])
            if os.path.exists(tool_folder):
                # Scan ALL files in the tool folder
                files_found = []
                try:
                    for file_name in os.listdir(tool_folder):
                        file_path = os.path.join(tool_folder, file_name)
                        if os.path.isfile(file_path):  # Only include actual files
                            file_size = os.path.getsize(file_path)
                            files_found.append({
                                "name": file_name,
                                "path": file_path,
                                "size": file_size
                            })
                except Exception as e:
                    print(f"Error scanning tool folder {tool_folder}: {e}")
                    continue
                
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
        """Get summary of ALL data available in a specific tool folder"""
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
        
        # Read ALL files in the tool folder
        try:
            for file_name in os.listdir(tool_folder):
                file_path = os.path.join(tool_folder, file_name)
                if os.path.isfile(file_path):
                    file_info = {
                        "name": file_name,
                        "size": os.path.getsize(file_path),
                        "modified": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                    }
                    
                    # Get data preview based on file type
                    if file_name.endswith(('.xlsx', '.xls')):
                        df = self.read_excel_file(file_path)
                        if df is not None:
                            file_info["rows"] = len(df)
                            file_info["columns"] = list(df.columns)
                            file_info["sample_data"] = df.head(3).to_dict('records')
                    elif file_name.endswith(('.txt', '.doc', '.docx', '.md')):
                        content = self.read_text_file(file_path)
                        if content:
                            file_info["lines"] = len(content.split('\n'))
                            file_info["preview"] = content[:500] + "..." if len(content) > 500 else content
                    
                    summary["files"].append(file_info)
        except Exception as e:
            print(f"Error reading tool folder {tool_folder}: {e}")
            return {"error": f"Error reading tool folder: {str(e)}"}
        
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
            # Enhanced relevance detection for different tool types
            tool_name = tool_data.get("tool", "")
            query_lower = query.lower()
            
            # Database tools for access/user queries
            if any(keyword in query_lower for keyword in ["access", "user", "role", "permission", "sql", "database"]):
                if tool_name in ["sql_server", "oracle_db"]:
                    return {
                        "relevant": True,
                        "score": 9,
                        "relevant_files": [f["name"] for f in tool_data.get("files", [])],
                        "summary": f"Tool contains database access control data relevant to query: {tool_data.get('description', '')}"
                    }
            
            # Document management tools for documentation queries
            if any(keyword in query_lower for keyword in ["document", "documentation", "docs", "gnosis", "support", "design", "instruction"]):
                if tool_name == "gnosis":
                    return {
                        "relevant": True,
                        "score": 8,
                        "relevant_files": [f["name"] for f in tool_data.get("files", [])],
                        "summary": f"Tool contains documentation and support materials relevant to query: {tool_data.get('description', '')}"
                    }
            
            # Issue tracking tools for tickets/issues queries
            if any(keyword in query_lower for keyword in ["ticket", "issue", "bug", "jira", "tracking"]):
                if tool_name == "jira":
                    return {
                        "relevant": True,
                        "score": 8,
                        "relevant_files": [f["name"] for f in tool_data.get("files", [])],
                        "summary": f"Tool contains issue tracking data relevant to query: {tool_data.get('description', '')}"
                    }
            
            # Testing tools for test queries
            if any(keyword in query_lower for keyword in ["test", "testing", "qa", "qtest", "quality"]):
                if tool_name == "qtest":
                    return {
                        "relevant": True,
                        "score": 8,
                        "relevant_files": [f["name"] for f in tool_data.get("files", [])],
                        "summary": f"Tool contains quality assurance and testing data relevant to query: {tool_data.get('description', '')}"
                    }
            
            # Service management tools for change/service queries
            if any(keyword in query_lower for keyword in ["change", "service", "servicenow", "itsm", "request"]):
                if tool_name == "service_now":
                    return {
                        "relevant": True,
                        "score": 8,
                        "relevant_files": [f["name"] for f in tool_data.get("files", [])],
                        "summary": f"Tool contains service management data relevant to query: {tool_data.get('description', '')}"
                    }
            
            # For other queries, use LLM analysis
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
            
            # Add file metadata for context (avoiding complex data structures)
            for file_info in result["data"]["files"][:2]:  # Max 2 files per tool
                if "columns" in file_info:
                    context_sections.append(f"File: {file_info['name']} ({file_info.get('rows', 0)} rows)")
                    context_sections.append(f"Columns: {', '.join(file_info['columns'])}")
                elif "preview" in file_info:
                    context_sections.append(f"Document: {file_info['name']}")
                    context_sections.append(f"Preview: {file_info['preview'][:200]}")
        
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

def create_veritas_agent(llm) -> VeritasGPTAgent:
    """Factory function to create a Veritas GPT agent with existing LangChain LLM"""
    return VeritasGPTAgent(llm=llm)