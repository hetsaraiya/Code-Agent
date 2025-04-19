"""
File operations module for the Coding Agent.
This module handles reading, writing, and editing files.
"""

import os
from typing import Optional, List, Dict, Any


def read_file(file_path: str) -> str:
    """
    Read the contents of a file.
    
    Args:
        file_path: Path to the file to read
        
    Returns:
        The contents of the file as a string
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


def write_file(file_path: str, content: str) -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file to write
        content: Content to write to the file
        
    Returns:
        Success message or error message
    """
    try:
        # Ensure file_path is absolute
        if not os.path.isabs(file_path):
            # Print a warning that we're converting to absolute path
            print(f"Warning: Converting relative path {file_path} to absolute path")
            file_path = os.path.abspath(file_path)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file {file_path}: {str(e)}"


def edit_file(file_path: str, old_string: str, new_string: str) -> str:
    """
    Edit a file by replacing an old string with a new string.
    
    Args:
        file_path: Path to the file to edit
        old_string: String to replace
        new_string: String to replace with
        
    Returns:
        Success message or error message
    """
    try:
        content = read_file(file_path)
        if isinstance(content, str) and not content.startswith("Error"):
            new_content = content.replace(old_string, new_string)
            return write_file(file_path, new_content)
        else:
            return content  # Return the error message from read_file
    except Exception as e:
        return f"Error editing file {file_path}: {str(e)}"


def list_directory(directory_path: str) -> List[str]:
    """
    List files and directories in a directory.
    
    Args:
        directory_path: Path to the directory to list
        
    Returns:
        List of files and directories in the directory
    """
    try:
        return os.listdir(directory_path)
    except Exception as e:
        return [f"Error listing directory {directory_path}: {str(e)}"]
