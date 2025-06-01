"""
File actions module for the Coding Agent.
This module defines actions that the agent can perform on files within the project context.
"""

from typing import Dict, List, Any
import os # Import os for path joining if needed, though utils handle it now

from coding_agent.core.types import AgentState
from coding_agent.utils.file_operations import read_file, write_file, edit_file, list_directory, read_file_lines, search_text
# Import the logger
from coding_agent.utils.logging import logger


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
        logger.error("read_file_action called without file_path")
        updated_state = state.copy()
        updated_state["action_output"] = "Error: file_path parameter is missing for read_file action."
        return updated_state

    logger.info(f"Reading file: {file_path} relative to {project_root}")
    result = read_file(project_root, file_path)

    # Update the state with the file content or error
    updated_state = state.copy()
    # Store content using the relative path as the key
    updated_state["files_content"][file_path] = result

    if result.startswith("Error"):
        logger.error(f"Failed to read file {file_path}: {result}")
        updated_state["action_output"] = f"Read file {file_path}: Failed - {result}"
    else:
        logger.debug(f"Successfully read file {file_path}")
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
        logger.error("write_file_action called without file_path")
        updated_state = state.copy()
        updated_state["action_output"] = "Error: file_path parameter is missing for write_file action."
        return updated_state

    logger.info(f"Writing to file: {file_path} relative to {project_root}")
    result = write_file(project_root, file_path, content)

    # Update the state
    updated_state = state.copy()
    # Store content using the relative path as the key, even on error for consistency
    updated_state["files_content"][file_path] = content if not result.startswith("Error") else f"Error writing: {result}"
    updated_state["action_output"] = f"Write file {file_path}: {result}"

    if result.startswith("Error"):
        logger.error(f"Failed to write to file {file_path}: {result}")
    else:
        logger.debug(f"Successfully wrote to file {file_path}")

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
        logger.error("edit_file_action called without file_path")
        updated_state = state.copy()
        updated_state["action_output"] = "Error: file_path parameter is missing for edit_file action."
        return updated_state

    logger.info(f"Editing file: {file_path} relative to {project_root}")
    logger.debug(f"Replacing string in file {file_path}")

    # edit_file now handles reading and writing internally using project_root
    result = edit_file(project_root, file_path, old_string, new_string)

    # Update the state
    updated_state = state.copy()
    updated_state["action_output"] = f"Edit file {file_path}: {result}"

    if result.startswith("Error"):
        logger.error(f"Failed to edit file {file_path}: {result}")
        # Update files_content with error if edit failed after read
        if "Could not read file content" not in result:
             updated_state["files_content"][file_path] = f"Error editing: {result}"
    else:
        logger.debug(f"Successfully edited file {file_path}")
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

    logger.info(f"Listing directory: {directory_path} relative to {project_root}")
    result = list_directory(project_root, directory_path)

    # Update the state
    updated_state = state.copy()
    # Format result for output
    if isinstance(result, list) and len(result) > 0 and isinstance(result[0], str) and result[0].startswith("Error"):
        output_message = f"List directory {directory_path}: Failed - {result[0]}"
        logger.error(f"Failed to list directory {directory_path}: {result[0]}")
    elif isinstance(result, list):
         output_message = f"List directory '{directory_path}': {', '.join(result) if result else 'Empty directory'}"
         logger.debug(f"Successfully listed directory {directory_path}")
    else: # Should not happen based on list_directory return type hint, but handle defensively
        output_message = f"List directory {directory_path}: Unexpected result type - {result}"
        logger.error(f"Unexpected result type from list_directory for {directory_path}: {result}")


    updated_state["action_output"] = output_message

    return updated_state


def read_file_lines_action(state: AgentState) -> AgentState:
    """
    Read specific lines from a file relative to the project root and update the state.

    Args:
        state: Current agent state, must contain 'project_root' and 'action_input' with 'file_path', 'from_line', and 'to_line'.

    Returns:
        Updated state with file lines content or error message.
    """
    action_input = state["action_input"]
    project_root = state["project_root"]
    file_path = action_input.get("file_path", "")  # Expecting relative path
    from_line = action_input.get("from_line")
    to_line = action_input.get("to_line")

    if not file_path:
        logger.error("read_file_lines_action called without file_path")
        updated_state = state.copy()
        updated_state["action_output"] = "Error: file_path parameter is missing for read_file_lines action."
        return updated_state

    if from_line is None or to_line is None:
        logger.error("read_file_lines_action called without from_line or to_line")
        updated_state = state.copy()
        updated_state["action_output"] = "Error: from_line and to_line parameters are required for read_file_lines action."
        return updated_state

    try:
        from_line = int(from_line)
        to_line = int(to_line)
    except (ValueError, TypeError):
        logger.error("read_file_lines_action called with invalid line numbers")
        updated_state = state.copy()
        updated_state["action_output"] = "Error: from_line and to_line must be valid integers."
        return updated_state

    logger.info(f"Reading lines {from_line}-{to_line} from file: {file_path} relative to {project_root}")
    result = read_file_lines(project_root, file_path, from_line, to_line)

    # Update the state with the file content or error
    updated_state = state.copy()
    # Store content using a key that indicates the line range
    content_key = f"{file_path}:{from_line}-{to_line}"
    updated_state["files_content"][content_key] = result

    if result.startswith("Error"):
        logger.error(f"Failed to read lines {from_line}-{to_line} from file {file_path}: {result}")
        updated_state["action_output"] = f"Read file lines {file_path}:{from_line}-{to_line}: Failed - {result}"
    else:
        logger.debug(f"Successfully read lines {from_line}-{to_line} from file {file_path}")
        updated_state["action_output"] = f"Successfully read lines {from_line}-{to_line} from {file_path}."

    return updated_state


def search_text_action(state: AgentState) -> AgentState:
    """
    Search for text across files in the project and update the state.

    Args:
        state: Current agent state, must contain 'project_root' and 'action_input' with 'search_term'.
               Optional parameters: 'file_extensions', 'case_sensitive', 'regex_mode', 'max_results'.

    Returns:
        Updated state with search results.
    """
    action_input = state["action_input"]
    project_root = state["project_root"]
    search_term = action_input.get("search_term", "")

    if not search_term:
        logger.error("search_text_action called without search_term")
        updated_state = state.copy()
        updated_state["action_output"] = "Error: search_term parameter is missing for search_text action."
        return updated_state

    # Optional parameters with defaults
    file_extensions = action_input.get("file_extensions")  # None means search all supported extensions
    case_sensitive = action_input.get("case_sensitive", False)
    regex_mode = action_input.get("regex_mode", False)
    max_results = action_input.get("max_results", 100)

    logger.info(f"Searching for text: '{search_term}' in project root: {project_root}")
    
    # Perform the search
    search_results = search_text(
        project_root=project_root,
        search_term=search_term,
        file_extensions=file_extensions,
        case_sensitive=case_sensitive,
        regex_mode=regex_mode,
        max_results=max_results
    )

    # Update the state
    updated_state = state.copy()
    
    # Store search results in files_content with a special key
    search_key = f"search_results:{search_term}"
    updated_state["files_content"][search_key] = search_results

    # Create human-readable output
    if search_results.get('error'):
        updated_state["action_output"] = f"Search for '{search_term}': Failed - {search_results['error']}"
        logger.error(f"Search failed: {search_results['error']}")
    else:
        total_matches = search_results['total_matches']
        files_searched = search_results['files_searched']
        
        # Create summary
        summary_lines = [
            f"Search for '{search_term}' completed:",
            f"• {total_matches} matches found",
            f"• {files_searched} files searched"
        ]
        
        # Add results summary (first few matches)
        if total_matches > 0:
            summary_lines.append("\nMatches found in:")
            file_matches = {}
            for result in search_results['results']:
                file_path = result['file_path']
                if file_path not in file_matches:
                    file_matches[file_path] = []
                file_matches[file_path].append(result['line_number'])
            
            # Show first 10 files with matches
            for i, (file_path, line_numbers) in enumerate(list(file_matches.items())[:10]):
                if len(line_numbers) <= 3:
                    lines_str = ", ".join(map(str, line_numbers))
                else:
                    lines_str = f"{', '.join(map(str, line_numbers[:3]))} and {len(line_numbers)-3} more"
                summary_lines.append(f"  • {file_path} (lines: {lines_str})")
            
            if len(file_matches) > 10:
                summary_lines.append(f"  • ... and {len(file_matches)-10} more files")
        
        updated_state["action_output"] = "\n".join(summary_lines)
        logger.info(f"Search completed: {total_matches} matches in {len(file_matches) if 'file_matches' in locals() else 0} files")

    return updated_state
