"""
Types module for the Coding Agent.
This module defines the state types and interfaces used throughout the agent.
"""

from typing import Dict, List, Any, Optional, TypedDict


class AgentState(TypedDict):
    """State of the agent workflow."""
    messages: List[Dict[str, Any]]
    task: str
    project_root: str  # Add project root path
    files_content: Dict[str, str]
    current_plan: Optional[List[str]]
    thought_process: Optional[str]
    next_action: Optional[str]
    action_input: Optional[Dict[str, Any]]
    action_output: Optional[str]
    final_answer: Optional[str]
    model_provider: Optional[str] # Track current provider
