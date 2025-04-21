"""
File operations module for the Coding Agent.
This module handles reading, writing, and editing files relative to a project root.
"""

import os
from typing import Optional, List, Dict, Any
# Import the logger
from coding_agent.utils.logging import app_logger


def _resolve_path(project_root: str, relative_path: str) -> str:
    """Resolve a relative path against the project root."""
    # Prevent path traversal attacks
    abs_path = os.path.abspath(os.path.join(project_root, relative_path))
    if not abs_path.startswith(os.path.abspath(project_root)):
        raise ValueError(f"Attempted path traversal: {relative_path}")
    return abs_path


def read_file(project_root: str, file_path: str) -> str:
    """
    Read the contents of a file relative to the project root.

    Args:
        project_root: The absolute path to the project's root directory.
        file_path: Path to the file to read, relative to the project root.

    Returns:
        The contents of the file as a string or an error message.
    """
    try:
        abs_file_path = _resolve_path(project_root, file_path)
        app_logger.debug(f"Reading file: {abs_file_path} (relative: {file_path})")
        with open(abs_file_path, "r", encoding="utf-8") as file:
            content = file.read()
        app_logger.debug(f"Successfully read file: {abs_file_path}")
        return content
    except FileNotFoundError:
        err_msg = f"Error reading file: File not found at {file_path}"
        app_logger.error(err_msg)
        return err_msg
    except ValueError as e: # Catch path traversal error
        err_msg = f"Error reading file {file_path}: {str(e)}"
        app_logger.error(err_msg)
        return err_msg
    except Exception as e:
        err_msg = f"Error reading file {file_path}: {str(e)}"
        app_logger.error(err_msg)
        return err_msg


def write_file(project_root: str, file_path: str, content: str) -> str:
    """
    Write content to a file relative to the project root.

    Args:
        project_root: The absolute path to the project's root directory.
        file_path: Path to the file to write, relative to the project root.
        content: Content to write to the file.

    Returns:
        Success message or error message.
    """
    try:
        abs_file_path = _resolve_path(project_root, file_path)
        app_logger.debug(f"Writing to file: {abs_file_path} (relative: {file_path})")

        # Ensure directory exists
        directory = os.path.dirname(abs_file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(abs_file_path, "w", encoding="utf-8") as file:
            file.write(content)
        app_logger.debug(f"Successfully wrote to file: {abs_file_path}")
        return f"Successfully wrote to {file_path}"
    except ValueError as e: # Catch path traversal error
        err_msg = f"Error writing to file {file_path}: {str(e)}"
        app_logger.error(err_msg)
        return err_msg
    except Exception as e:
        err_msg = f"Error writing to file {file_path}: {str(e)}"
        app_logger.error(err_msg)
        return err_msg


def edit_file(project_root: str, file_path: str, old_string: str, new_string: str) -> str:
    """
    Edit a file by replacing an old string with a new string, relative to the project root.

    Args:
        project_root: The absolute path to the project's root directory.
        file_path: Path to the file to edit, relative to the project root.
        old_string: String to replace.
        new_string: String to replace with.

    Returns:
        Success message or error message.
    """
    try:
        app_logger.debug(f"Editing file: {file_path} within project root {project_root}")
        # Read the file using the project_root context
        content = read_file(project_root, file_path)

        if isinstance(content, str) and not content.startswith("Error"):
            new_content = content.replace(old_string, new_string)
            app_logger.debug(f"Replacing content in file: {file_path}")
            # Write the file back using the project_root context
            return write_file(project_root, file_path, new_content)
        else:
            app_logger.error(f"Cannot edit file {file_path}, read operation failed: {content}")
            return content # Return the error message from read_file
    except Exception as e:
        err_msg = f"Error editing file {file_path}: {str(e)}"
        app_logger.error(err_msg)
        return err_msg


def list_directory(project_root: str, directory_path: str) -> List[str]:
    """
    List files and directories in a directory relative to the project root.

    Args:
        project_root: The absolute path to the project's root directory.
        directory_path: Path to the directory to list, relative to the project root.

    Returns:
        List of files and directories in the directory or an error message list.
    """
    try:
        abs_dir_path = _resolve_path(project_root, directory_path)
        app_logger.debug(f"Listing directory: {abs_dir_path} (relative: {directory_path})")
        files = os.listdir(abs_dir_path)
        app_logger.debug(f"Found {len(files)} items in directory: {directory_path}")
        return files
    except FileNotFoundError:
        err_msg = f"Error listing directory: Directory not found at {directory_path}"
        app_logger.error(err_msg)
        return [err_msg]
    except ValueError as e: # Catch path traversal error
        err_msg = f"Error listing directory {directory_path}: {str(e)}"
        app_logger.error(err_msg)
        return [err_msg]
    except Exception as e:
        err_msg = f"Error listing directory {directory_path}: {str(e)}"
        app_logger.error(err_msg)
        return [err_msg]
