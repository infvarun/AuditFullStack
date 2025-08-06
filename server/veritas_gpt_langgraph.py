#!/usr/bin/env python3
"""
Enhanced Veritas GPT Agent with LangGraph Integration

This module provides an intelligent GPT agent that uses LangGraph for:
1. Advanced state management and conversation flow
2. Multi-step reasoning and tool orchestration
3. Persistent memory and context awareness
4. Graph-based workflow execution

Maintains compatibility with existing folder-based tool system and ChatOpenAI LLM.
"""

import os
import pandas as pd
import json
from typing import Dict, List, Any, Optional, Union, TypedDict, Annotated
from datetime import datetime
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# LangGraph imports
from langgraph.graph import Graph, StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

# Import the existing tool functionality
from veritas_gpt_enhanced import VeritasGPTAgent


class VeritasState(TypedDict):
    """State schema for Veritas GPT LangGraph workflow"""
    messages: Annotated[list[BaseMessage], add_messages]
    ci_id: str
    audit_id: str
    audit_name: str
    conversation_id: str
    user_message: str
    available_tools: List[Dict[str, Any]]
    relevant_tools: List[Dict[str, Any]]
    tool_data: Dict[str, Any]
    context_summary: str
    thinking_steps: List[str]
    tools_used: List[str]
    final_response: str


class VeritasGPTLangGraphAgent:
    """Enhanced Veritas GPT Agent with LangGraph workflow management"""
    
    def __init__(self, tools_path: str = "server/tools", llm=None):
        # Initialize base agent for tool functionality
        self.base_agent = VeritasGPTAgent(tools_path=tools_path, llm=llm)
        self.llm = llm
        
        # Initialize LangGraph components
        self.memory = MemorySaver()
        self.workflow = self._create_workflow()
        self.app = self.workflow.compile(checkpointer=self.memory)
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow for Veritas GPT"""
        
        # Define the workflow graph
        workflow = StateGraph(VeritasState)
        
        # Add nodes for each step in the process
        workflow.add_node("scan_tools", self._scan_available_tools)
        workflow.add_node("analyze_relevance", self._analyze_tool_relevance)
        workflow.add_node("gather_context", self._gather_tool_context)
        workflow.add_node("generate_response", self._generate_final_response)
        
        # Define the workflow edges
        workflow.set_entry_point("scan_tools")
        workflow.add_edge("scan_tools", "analyze_relevance")
        workflow.add_edge("analyze_relevance", "gather_context")
        workflow.add_edge("gather_context", "generate_response")
        workflow.add_edge("generate_response", END)
        
        return workflow
    
    def _scan_available_tools(self, state: VeritasState) -> VeritasState:
        """Scan and identify available tools for the CI"""
        try:
            available_tools = self.base_agent.get_available_tools(state["ci_id"])
            thinking_steps = state.get("thinking_steps", [])
            thinking_steps.append(f"Scanning {len(available_tools)} available tools")
            
            return {
                **state,
                "available_tools": available_tools,
                "thinking_steps": thinking_steps
            }
        except Exception as e:
            print(f"Error scanning tools: {e}")
            return {
                **state,
                "available_tools": [],
                "thinking_steps": state.get("thinking_steps", []) + ["Error scanning tools"]
            }
    
    def _analyze_tool_relevance(self, state: VeritasState) -> VeritasState:
        """Analyze which tools are relevant to the user's query"""
        try:
            search_results = self.base_agent.search_tool_data(state["ci_id"], state["user_message"])
            relevant_tools = search_results.get("results", [])
            
            thinking_steps = state.get("thinking_steps", [])
            thinking_steps.append(f"Found {len(relevant_tools)} relevant data sources")
            
            return {
                **state,
                "relevant_tools": relevant_tools,
                "thinking_steps": thinking_steps
            }
        except Exception as e:
            print(f"Error analyzing tool relevance: {e}")
            return {
                **state,
                "relevant_tools": [],
                "thinking_steps": state.get("thinking_steps", []) + ["Error analyzing tool relevance"]
            }
    
    def _gather_tool_context(self, state: VeritasState) -> VeritasState:
        """Gather detailed context from relevant tools"""
        try:
            tool_data = {}
            tools_used = []
            context_sections = []
            
            # Process top 3 most relevant tools
            for result in state["relevant_tools"][:3]:
                tool_key = result["tool"]
                tools_used.append(tool_key)
                
                # Get detailed tool data
                tool_summary = self.base_agent.get_tool_data_summary(state["ci_id"], tool_key)
                tool_data[tool_key] = tool_summary
                
                context_sections.append(f"**{tool_key.upper()} Data:**")
                context_sections.append(result["summary"])
                
                # Add file metadata for context
                if "files" in tool_summary:
                    for file_info in tool_summary["files"][:2]:
                        if "columns" in file_info:
                            context_sections.append(f"File: {file_info['name']} ({file_info.get('rows', 0)} rows)")
                            context_sections.append(f"Columns: {', '.join(file_info['columns'])}")
                        elif "preview" in file_info:
                            context_sections.append(f"Document: {file_info['name']}")
                            context_sections.append(f"Preview: {file_info['preview'][:200]}")
            
            thinking_steps = state.get("thinking_steps", [])
            thinking_steps.append("Analyzing tool data for context")
            
            context_summary = f"Analyzed data from {len(tools_used)} tools: {', '.join(tools_used)}"
            
            return {
                **state,
                "tool_data": tool_data,
                "tools_used": tools_used,
                "context_summary": context_summary,
                "thinking_steps": thinking_steps
            }
        except Exception as e:
            print(f"Error gathering tool context: {e}")
            return {
                **state,
                "tool_data": {},
                "tools_used": [],
                "context_summary": "Error gathering context",
                "thinking_steps": state.get("thinking_steps", []) + ["Error gathering tool context"]
            }
    
    def _generate_final_response(self, state: VeritasState) -> VeritasState:
        """Generate the final response using LLM with gathered context"""
        try:
            # Build context from gathered tool data
            context_sections = []
            
            for tool_key, tool_data in state["tool_data"].items():
                context_sections.append(f"**{tool_key.upper()} Data:**")
                context_sections.append(tool_data.get("description", ""))
                
                if "files" in tool_data:
                    for file_info in tool_data["files"][:2]:
                        if "columns" in file_info:
                            context_sections.append(f"File: {file_info['name']} ({file_info.get('rows', 0)} rows)")
                            context_sections.append(f"Columns: {', '.join(file_info['columns'])}")
                        elif "preview" in file_info:
                            context_sections.append(f"Document: {file_info['name']}")
                            context_sections.append(f"Preview: {file_info['preview'][:200]}")
            
            # Get conversation history from messages
            conversation_history = []
            messages = state.get("messages", [])
            for msg in messages[-10:]:  # Last 10 messages
                if isinstance(msg, HumanMessage):
                    conversation_history.append({"role": "user", "content": msg.content})
                elif isinstance(msg, AIMessage):
                    conversation_history.append({"role": "assistant", "content": msg.content})
            
            # Create comprehensive system prompt
            system_prompt = f"""You are Veritas GPT, an expert audit analyst with access to comprehensive audit data for CI {state["ci_id"]}.

AVAILABLE TOOLS AND DATA:
{chr(10).join([f"- {tool['tool']}: {tool['description']}" for tool in state["available_tools"]])}

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
{json.dumps(conversation_history[-5:], indent=2)}

Please analyze the context and provide a comprehensive response to the user's question."""

            # Clean up context to avoid issues
            clean_system_prompt = system_prompt.replace('"', "'").replace('\n', ' ').replace('\r', ' ')
            
            # Generate response using LLM
            prompt = ChatPromptTemplate.from_messages([
                SystemMessagePromptTemplate.from_template(clean_system_prompt),
                HumanMessagePromptTemplate.from_template("{user_message}")
            ])
            
            formatted_prompt = prompt.format_messages(user_message=state["user_message"])
            response = self.llm.invoke(formatted_prompt)
            
            thinking_steps = state.get("thinking_steps", [])
            thinking_steps.append("Generating comprehensive response")
            
            # Add response to messages
            updated_messages = state.get("messages", [])
            updated_messages.append(HumanMessage(content=state["user_message"]))
            updated_messages.append(AIMessage(content=response.content))
            
            return {
                **state,
                "final_response": response.content,
                "thinking_steps": thinking_steps,
                "messages": updated_messages
            }
            
        except Exception as e:
            print(f"Error generating response: {e}")
            # Fallback response
            fallback_response = f"""I have access to data from {len(state.get('available_tools', []))} tools but encountered an error during analysis.

Available tools: {', '.join([tool['tool'] for tool in state.get('available_tools', [])])}

Please rephrase your question and I'll provide a detailed analysis. Error: {str(e)[:100]}"""
            
            thinking_steps = state.get("thinking_steps", [])
            thinking_steps.append("Error occurred, providing fallback response")
            
            return {
                **state,
                "final_response": fallback_response,
                "thinking_steps": thinking_steps,
                "messages": state.get("messages", []) + [
                    HumanMessage(content=state["user_message"]),
                    AIMessage(content=fallback_response)
                ]
            }
    
    def generate_context_aware_response(self, ci_id: str, user_message: str, conversation_history: List[Dict] = None, conversation_id: str = None) -> Dict[str, Any]:
        """Generate a context-aware response using LangGraph workflow"""
        
        # Convert conversation history to messages
        messages = []
        if conversation_history:
            for msg in conversation_history[-10:]:  # Last 10 messages
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))
        
        # Generate conversation ID if not provided
        final_conversation_id = conversation_id or f"conv_{ci_id}_{int(datetime.now().timestamp())}"
        
        # Create initial state
        initial_state = VeritasState(
            messages=messages,
            ci_id=ci_id,
            audit_id="",  # Will be set by caller
            audit_name="",  # Will be set by caller
            conversation_id=final_conversation_id,
            user_message=user_message,
            available_tools=[],
            relevant_tools=[],
            tool_data={},
            context_summary="",
            thinking_steps=[],
            tools_used=[],
            final_response=""
        )
        
        # Configure thread for conversation persistence
        config = {"configurable": {"thread_id": final_conversation_id}}
        
        try:
            # Execute the LangGraph workflow
            final_state = self.app.invoke(initial_state, config=config)
            
            return {
                "response": final_state["final_response"],
                "tools_used": final_state["tools_used"],
                "thinking_steps": final_state["thinking_steps"],
                "context_summary": final_state["context_summary"],
                "available_tools": [tool["tool"] for tool in final_state["available_tools"]],
                "conversation_id": final_state["conversation_id"],
                "workflow_type": "langgraph"
            }
            
        except Exception as e:
            print(f"LangGraph workflow error: {e}")
            # Fallback to base agent
            return self.base_agent.generate_context_aware_response(
                ci_id=ci_id,
                user_message=user_message,
                conversation_history=conversation_history
            )


def create_veritas_langgraph_agent(llm) -> VeritasGPTLangGraphAgent:
    """Factory function to create a Veritas GPT LangGraph agent with existing LangChain LLM"""
    return VeritasGPTLangGraphAgent(llm=llm)