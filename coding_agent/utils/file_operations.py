"""
File operations module for the Coding Agent.
This module handles reading, writing, and editing files relative to a project root.
"""

import os
import re
from typing import Optional, List, Dict, Any, Tuple
# Import the logger
from coding_agent.utils.logging import logger


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
        logger.debug(f"Reading file: {abs_file_path} (relative: {file_path})")
        with open(abs_file_path, "r", encoding="utf-8") as file:
            content = file.read()
        logger.debug(f"Successfully read file: {abs_file_path}")
        return content
    except FileNotFoundError:
        err_msg = f"Error reading file: File not found at {file_path}"
        logger.error(err_msg)
        return err_msg
    except ValueError as e: # Catch path traversal error
        err_msg = f"Error reading file {file_path}: {str(e)}"
        logger.error(err_msg)
        return err_msg
    except Exception as e:
        err_msg = f"Error reading file {file_path}: {str(e)}"
        logger.error(err_msg)
        return err_msg


def read_file_lines(project_root: str, file_path: str, from_line: int, to_line: int) -> str:
    """
    Read specific lines from a file relative to the project root.

    Args:
        project_root: The absolute path to the project's root directory.
        file_path: Path to the file to read, relative to the project root.
        from_line: Starting line number (1-indexed, inclusive).
        to_line: Ending line number (1-indexed, inclusive).

    Returns:
        The contents of the specified lines as a string or an error message.
    """
    try:
        abs_file_path = _resolve_path(project_root, file_path)
        logger.debug(f"Reading lines {from_line}-{to_line} from file: {abs_file_path} (relative: {file_path})")
        
        # Validate line numbers
        if from_line < 1 or to_line < 1:
            err_msg = f"Line numbers must be 1 or greater. Got from_line={from_line}, to_line={to_line}"
            logger.error(err_msg)
            return f"Error reading file lines: {err_msg}"
        
        if from_line > to_line:
            err_msg = f"from_line ({from_line}) cannot be greater than to_line ({to_line})"
            logger.error(err_msg)
            return f"Error reading file lines: {err_msg}"
        
        with open(abs_file_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
        
        # Check if the requested lines exist
        total_lines = len(lines)
        if from_line > total_lines:
            err_msg = f"from_line ({from_line}) exceeds file length ({total_lines} lines)"
            logger.error(err_msg)
            return f"Error reading file lines: {err_msg}"
        
        # Adjust to_line if it exceeds file length
        actual_to_line = min(to_line, total_lines)
        if to_line > total_lines:
            logger.warning(f"to_line ({to_line}) exceeds file length ({total_lines}), adjusting to {actual_to_line}")
        
        # Extract the requested lines (convert to 0-indexed)
        selected_lines = lines[from_line-1:actual_to_line]
        content = ''.join(selected_lines)
        
        logger.debug(f"Successfully read lines {from_line}-{actual_to_line} from file: {abs_file_path}")
        return content
        
    except FileNotFoundError:
        err_msg = f"Error reading file lines: File not found at {file_path}"
        logger.error(err_msg)
        return err_msg
    except ValueError as e: # Catch path traversal error
        err_msg = f"Error reading file lines {file_path}: {str(e)}"
        logger.error(err_msg)
        return err_msg
    except Exception as e:
        err_msg = f"Error reading file lines {file_path}: {str(e)}"
        logger.error(err_msg)
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
        logger.debug(f"Writing to file: {abs_file_path} (relative: {file_path})")

        # Ensure directory exists
        directory = os.path.dirname(abs_file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

        with open(abs_file_path, "w", encoding="utf-8") as file:
            file.write(content)
        logger.debug(f"Successfully wrote to file: {abs_file_path}")
        return f"Successfully wrote to {file_path}"
    except ValueError as e: # Catch path traversal error
        err_msg = f"Error writing to file {file_path}: {str(e)}"
        logger.error(err_msg)
        return err_msg
    except Exception as e:
        err_msg = f"Error writing to file {file_path}: {str(e)}"
        logger.error(err_msg)
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
        logger.debug(f"Editing file: {file_path} within project root {project_root}")
        # Read the file using the project_root context
        content = read_file(project_root, file_path)

        if isinstance(content, str) and not content.startswith("Error"):
            new_content = content.replace(old_string, new_string)
            logger.debug(f"Replacing content in file: {file_path}")
            # Write the file back using the project_root context
            return write_file(project_root, file_path, new_content)
        else:
            logger.error(f"Cannot edit file {file_path}, read operation failed: {content}")
            return content # Return the error message from read_file
    except Exception as e:
        err_msg = f"Error editing file {file_path}: {str(e)}"
        logger.error(err_msg)
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
        logger.debug(f"Listing directory: {abs_dir_path} (relative: {directory_path})")
        files = os.listdir(abs_dir_path)
        logger.debug(f"Found {len(files)} items in directory: {directory_path}")
        return files
    except FileNotFoundError:
        err_msg = f"Error listing directory: Directory not found at {directory_path}"
        logger.error(err_msg)
        return [err_msg]
    except ValueError as e: # Catch path traversal error
        err_msg = f"Error listing directory {directory_path}: {str(e)}"
        logger.error(err_msg)
        return [err_msg]
    except Exception as e:
        err_msg = f"Error listing directory {directory_path}: {str(e)}"
        logger.error(err_msg)
        return [err_msg]


def search_text(project_root: str, search_term: str, file_extensions: Optional[List[str]] = None, 
                case_sensitive: bool = False, regex_mode: bool = False, max_results: int = 100) -> Dict[str, Any]:
    """
    Search for text across files in the project and return file paths and line numbers.

    Args:
        project_root: The absolute path to the project's root directory.
        search_term: The text to search for.
        file_extensions: List of file extensions to search (e.g., ['.py', '.js']). If None, searches all text files.
        case_sensitive: Whether the search should be case-sensitive.
        regex_mode: Whether to treat search_term as a regular expression.
        max_results: Maximum number of results to return.

    Returns:
        Dictionary containing:
        - 'total_matches': Total number of matches found
        - 'files_searched': Number of files searched
        - 'results': List of dictionaries with 'file_path', 'line_number', 'line_content', 'match_start', 'match_end'
        - 'error': Error message if any
    """
    results = {
        'total_matches': 0,
        'files_searched': 0,
        'results': [],
        'error': None
    }

    try:
        logger.info(f"Searching for '{search_term}' in project root: {project_root}")
        
        # Default file extensions to search if none provided
        if file_extensions is None:
            file_extensions = ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.h', '.go', '.rs', '.php', '.rb', 
                             '.md', '.txt', '.json', '.yaml', '.yml', '.xml', '.html', '.css', '.sql', '.sh', '.bat']

        # Prepare search pattern
        if regex_mode:
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                pattern = re.compile(search_term, flags)
            except re.error as e:
                results['error'] = f"Invalid regex pattern: {str(e)}"
                return results
        else:
            # Escape special regex characters for literal search
            escaped_term = re.escape(search_term)
            flags = 0 if case_sensitive else re.IGNORECASE
            pattern = re.compile(escaped_term, flags)

        # Walk through the project directory
        for root, dirs, files in os.walk(project_root):
            # Skip hidden directories and common build/cache directories
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['__pycache__', 'node_modules', 'build', 'dist', 'target']]
            
            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue
                    
                file_path = os.path.join(root, file)
                relative_path = os.path.relpath(file_path, project_root)
                
                # Check file extension
                _, ext = os.path.splitext(file.lower())
                if ext not in file_extensions:
                    continue

                try:
                    results['files_searched'] += 1
                    
                    # Read file and search
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            matches = list(pattern.finditer(line))
                            
                            for match in matches:
                                if results['total_matches'] >= max_results:
                                    logger.warning(f"Search reached maximum results limit ({max_results})")
                                    results['error'] = f"Search stopped at {max_results} results limit"
                                    return results
                                
                                results['results'].append({
                                    'file_path': relative_path,
                                    'line_number': line_num,
                                    'line_content': line.rstrip('\n\r'),
                                    'match_start': match.start(),
                                    'match_end': match.end(),
                                    'matched_text': match.group()
                                })
                                results['total_matches'] += 1

                except (UnicodeDecodeError, PermissionError) as e:
                    # Skip binary files or files we can't read
                    logger.debug(f"Skipping file {relative_path}: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Error searching file {relative_path}: {str(e)}")
                    continue

        logger.info(f"Search completed: {results['total_matches']} matches found in {results['files_searched']} files")
        return results

    except Exception as e:
        error_msg = f"Error during text search: {str(e)}"
        logger.error(error_msg)
        results['error'] = error_msg
        return results
