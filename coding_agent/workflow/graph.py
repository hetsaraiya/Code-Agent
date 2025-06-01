"""
Workflow module for the Coding Agent.
This module defines the LangGraph workflow for the coding agent.
"""

import langgraph.graph as lg
from typing import Dict, List, Any

from coding_agent.core.types import AgentState
from coding_agent.core.reasoning import analyze_task, determine_next_action, generate_solution
from coding_agent.actions.file_actions import (
    read_file_action,
    read_file_lines_action,
    write_file_action,
    edit_file_action,
    list_directory_action,
    search_text_action,
)
# Import the logger
from coding_agent.utils.logging import logger


def create_workflow():
    """
    Create the LangGraph workflow for the coding agent.
    
    Returns:
        The compiled workflow graph
    """
    logger.info("Creating workflow graph")
    
    # Define the conditional edges in the graph
    def decide_next_step(state: AgentState) -> str:
        """Decide the next step based on the current state."""
        next_action = state.get("next_action", "")
        logger.debug(f"Deciding next step based on action: {next_action}")
        
        if next_action == "finish":
            return "finish"
        elif next_action == "read_file":
            return "read_file"
        elif next_action == "read_file_lines":
            return "read_file_lines"
        elif next_action == "write_file":
            return "write_file"
        elif next_action == "edit_file":
            return "edit_file"
        elif next_action == "list_directory":
            return "list_directory"
        elif next_action == "search_text":
            return "search_text"
        else:
            return "determine_next_action"

    # Create the workflow graph
    workflow = lg.Graph()
    
    # Add nodes to the graph
    logger.debug("Adding nodes to workflow graph")
    workflow.add_node("analyze_task", analyze_task)
    workflow.add_node("determine_next_action", determine_next_action)
    workflow.add_node("read_file", read_file_action)
    workflow.add_node("read_file_lines", read_file_lines_action)
    workflow.add_node("write_file", write_file_action)
    workflow.add_node("edit_file", edit_file_action)
    workflow.add_node("list_directory", list_directory_action)
    workflow.add_node("search_text", search_text_action)
    workflow.add_node("generate_solution", generate_solution)
    
    # Add edges to the graph
    logger.debug("Adding edges to workflow graph")
    # Add entry point edge from START to the first node
    workflow.add_edge(lg.START, "analyze_task")
    
    workflow.add_edge("analyze_task", "determine_next_action")
    workflow.add_conditional_edges(
        "determine_next_action",
        decide_next_step,
        {
            "read_file": "read_file",
            "read_file_lines": "read_file_lines",
            "write_file": "write_file",
            "edit_file": "edit_file",
            "list_directory": "list_directory",
            "search_text": "search_text",
            "finish": "generate_solution",
        },
    )
    workflow.add_edge("read_file", "determine_next_action")
    workflow.add_edge("read_file_lines", "determine_next_action")
    workflow.add_edge("write_file", "determine_next_action")
    workflow.add_edge("edit_file", "determine_next_action")
    workflow.add_edge("list_directory", "determine_next_action")
    workflow.add_edge("search_text", "determine_next_action")
    
    # Compile the graph
    logger.info("Compiling workflow graph")
    return workflow.compile()
