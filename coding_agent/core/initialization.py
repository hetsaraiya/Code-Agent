"""
Initialization module for the Coding Agent.
This module provides functions to initialize the agent's state with file listings.
"""

import os
from typing import Dict, Any, List

from coding_agent.utils.file_operations import list_directory, read_file
from coding_agent.utils.logging import logger


def initialize_files_content(project_root: str, max_depth: int = 3) -> Dict[str, str]:
    """
    Initialize the files_content dictionary with a listing of all files in the project directory
    and optionally read key configuration files.
    
    Args:
        project_root: The absolute path to the project's root directory
        max_depth: Maximum directory depth to traverse (to prevent excessive recursion)
        
    Returns:
        Dict[str, str]: Dictionary with relative file paths as keys and contents/descriptions as values
    """
    logger.info(f"Initializing files_content for project root: {project_root}")
    files_content = {}
    
    # Helper function to recursively explore directories
    def explore_directory(dir_path: str, current_depth: int, rel_path: str = ""):
        # Stop if we've reached the maximum depth
        if current_depth > max_depth:
            return
        
        try:
            # List all files and directories in the current directory
            items = list_directory(project_root, rel_path or ".")
            
            # Add the directory listing to files_content
            if rel_path:
                files_content[rel_path] = f"Directory containing: {', '.join(items)}"
            else:
                files_content["."] = f"Project root containing: {', '.join(items)}"
            
            # Process each item
            for item in items:
                # Build the relative path for this item
                item_rel_path = os.path.join(rel_path, item) if rel_path else item
                
                # Check if it's a directory by trying to list it
                try:
                    # If this is a directory, recurse into it
                    subitems = list_directory(project_root, item_rel_path)
                    # This is a directory if we didn't get an error
                    if not (len(subitems) == 1 and isinstance(subitems[0], str) and subitems[0].startswith("Error")):
                        # It's a directory, recurse into it
                        explore_directory(os.path.join(dir_path, item), current_depth + 1, item_rel_path)
                        continue
                except Exception:
                    pass  # Not a directory or can't access, treat as a file
                
                # Read certain key files that might be useful for task analysis
                if item.lower() in ['readme.md', 'pyproject.toml', 'setup.py', 'requirements.txt', 'package.json', 
                                    '.env.example', 'dockerfile', 'docker-compose.yml', '.gitignore']:
                    # Read these files immediately for immediate context
                    content = read_file(project_root, item_rel_path)
                    if not content.startswith("Error"):
                        files_content[item_rel_path] = content
                        logger.debug(f"Read key file: {item_rel_path}")
                    else:
                        files_content[item_rel_path] = f"File exists but couldn't be read: {content}"
                else:
                    # For other files, just note their existence
                    _, ext = os.path.splitext(item.lower())
                    if ext in ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs', '.php', '.rb', '.md', '.txt', '.json', '.yaml', '.yml', '.ini', '.cfg']:
                        files_content[item_rel_path] = "File exists (content not loaded initially)"
        
        except Exception as e:
            logger.error(f"Error exploring directory {dir_path}: {str(e)}")
    
    # Start the recursive exploration from the project root
    explore_directory(project_root, 1)
    
    logger.info(f"Initialized files_content with {len(files_content)} entries")
    return files_content


def load_immediate_project_structure(project_root: str) -> Dict[str, str]:
    """
    Load just the immediate project structure without recursing deeply or reading files.
    This is a lighter alternative to initialize_files_content.
    
    Args:
        project_root: The absolute path to the project's root directory
        
    Returns:
        Dict[str, str]: Dictionary with relative file paths as keys and directory listings as values
    """
    logger.info(f"Loading immediate project structure for: {project_root}")
    files_content = {}
    
    try:
        # List root directory
        root_items = list_directory(project_root, ".")
        files_content["."] = f"Project root containing: {', '.join(root_items)}"
        
        # Get first level subdirectories
        for item in root_items:
            item_path = item
            try:
                # Try to list as a directory
                subitems = list_directory(project_root, item_path)
                
                # Check if this was successful (not an error message)
                if not (len(subitems) == 1 and isinstance(subitems[0], str) and subitems[0].startswith("Error")):
                    # It's a directory, add its listing
                    files_content[item_path] = f"Directory containing: {', '.join(subitems)}"
                    
                    # Read README.md if it exists in this directory
                    if "README.md" in subitems or "readme.md" in subitems:
                        readme = "README.md" if "README.md" in subitems else "readme.md"
                        readme_path = os.path.join(item_path, readme)
                        content = read_file(project_root, readme_path)
                        if not content.startswith("Error"):
                            files_content[readme_path] = content
            except Exception:
                # Not a directory or error, skip it
                pass
    
    except Exception as e:
        logger.error(f"Error loading project structure: {str(e)}")
    
    return files_content
