"""
File actions module for the Coding Agent.
This module defines actions that the agent can perform on files within the project context.
"""

from typing import Dict, List, Any
import os # Import os for path joining if needed, though utils handle it now

from coding_agent.core.types import AgentState
from coding_agent.utils.file_operations import read_file, write_file, edit_file, list_directory
# Import the logger
from coding_agent.utils.logging import app_logger


def read_file_action(state: AgentState) -> AgentState:
    """
    Read a file relative to the project root and update the state.

    Args:
        state: Current agent state, must contain 'project_root' and 'action_input' with 'file_path'.

    Returns:
        Updated state with file contents or error message.
    """
    action_input = state["action_input"]
    project_root = state["project_root"]
    file_path = action_input.get("file_path", "") # Expecting relative path

    if not file_path:
        app_logger.error("read_file_action called without file_path")
        updated_state = state.copy()
        updated_state["action_output"] = "Error: file_path parameter is missing for read_file action."
        return updated_state

    app_logger.info(f"Reading file: {file_path} relative to {project_root}")
    result = read_file(project_root, file_path)

    # Update the state with the file content or error
    updated_state = state.copy()
    # Store content using the relative path as the key
    updated_state["files_content"][file_path] = result

    if result.startswith("Error"):
        app_logger.error(f"Failed to read file {file_path}: {result}")
        updated_state["action_output"] = f"Read file {file_path}: Failed - {result}"
    else:
        app_logger.debug(f"Successfully read file {file_path}")
        # Optionally clear action_output on success or provide a success message
        updated_state["action_output"] = f"Successfully read content of {file_path}."

    return updated_state


def write_file_action(state: AgentState) -> AgentState:
    """
    Write to a file relative to the project root and update the state.

    Args:
        state: Current agent state, must contain 'project_root' and 'action_input' with 'file_path' and 'content'.

    Returns:
        Updated state with action result.
    """
    action_input = state["action_input"]
    project_root = state["project_root"]
    file_path = action_input.get("file_path", "") # Expecting relative path
    content = action_input.get("content", "")

    if not file_path:
        app_logger.error("write_file_action called without file_path")
        updated_state = state.copy()
        updated_state["action_output"] = "Error: file_path parameter is missing for write_file action."
        return updated_state

    app_logger.info(f"Writing to file: {file_path} relative to {project_root}")
    result = write_file(project_root, file_path, content)

    # Update the state
    updated_state = state.copy()
    # Store content using the relative path as the key, even on error for consistency
    updated_state["files_content"][file_path] = content if not result.startswith("Error") else f"Error writing: {result}"
    updated_state["action_output"] = f"Write file {file_path}: {result}"

    if result.startswith("Error"):
        app_logger.error(f"Failed to write to file {file_path}: {result}")
    else:
        app_logger.debug(f"Successfully wrote to file {file_path}")

    return updated_state


def edit_file_action(state: AgentState) -> AgentState:
    """
    Edit a file relative to the project root and update the state.

    Args:
        state: Current agent state, must contain 'project_root' and 'action_input' with 'file_path', 'old_string', 'new_string'.

    Returns:
        Updated state with edited file content or error message.
    """
    action_input = state["action_input"]
    project_root = state["project_root"]
    file_path = action_input.get("file_path", "") # Expecting relative path
    old_string = action_input.get("old_string", "")
    new_string = action_input.get("new_string", "")

    if not file_path:
        app_logger.error("edit_file_action called without file_path")
        updated_state = state.copy()
        updated_state["action_output"] = "Error: file_path parameter is missing for edit_file action."
        return updated_state

    app_logger.info(f"Editing file: {file_path} relative to {project_root}")
    app_logger.debug(f"Replacing string in file {file_path}")

    # edit_file now handles reading and writing internally using project_root
    result = edit_file(project_root, file_path, old_string, new_string)

    # Update the state
    updated_state = state.copy()
    updated_state["action_output"] = f"Edit file {file_path}: {result}"

    if result.startswith("Error"):
        app_logger.error(f"Failed to edit file {file_path}: {result}")
        # Update files_content with error if edit failed after read
        if "Could not read file content" not in result:
             updated_state["files_content"][file_path] = f"Error editing: {result}"
    else:
        app_logger.debug(f"Successfully edited file {file_path}")
        # Re-read the file content after successful edit to update state accurately
        new_content = read_file(project_root, file_path)
        updated_state["files_content"][file_path] = new_content if not new_content.startswith("Error") else f"Error re-reading after edit: {new_content}"


    return updated_state


def list_directory_action(state: AgentState) -> AgentState:
    """
    List a directory relative to the project root and update the state.

    Args:
        state: Current agent state, must contain 'project_root' and 'action_input' with 'directory_path'.

    Returns:
        Updated state with directory listing or error message.
    """
    action_input = state["action_input"]
    project_root = state["project_root"]
    directory_path = action_input.get("directory_path", ".") # Default to project root if not specified

    app_logger.info(f"Listing directory: {directory_path} relative to {project_root}")
    result = list_directory(project_root, directory_path)

    # Update the state
    updated_state = state.copy()
    # Format result for output
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], str) and result[0].startswith("Error"):
        output_message = f"List directory {directory_path}: Failed - {result[0]}"
        app_logger.error(f"Failed to list directory {directory_path}: {result[0]}")
    elif isinstance(result, list):
         output_message = f"List directory '{directory_path}': {', '.join(result) if result else 'Empty directory'}"
         app_logger.debug(f"Successfully listed directory {directory_path}")
    else: # Should not happen based on list_directory return type hint, but handle defensively
        output_message = f"List directory {directory_path}: Unexpected result type - {result}"
        app_logger.error(f"Unexpected result type from list_directory for {directory_path}: {result}")


    updated_state["action_output"] = output_message

    return updated_state
