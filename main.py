"""
Main entry point for the Coding Agent.
This file serves as the primary entry point to run the Coding Agent project.
"""

import os
import sys
import argparse
from typing import Dict

# Add the project root to sys.path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from coding_agent.core.types import AgentState
from coding_agent.workflow.graph import create_workflow
from coding_agent.utils.model_utils import get_current_model_info, switch_model, list_available_models
# Import the logger
from coding_agent.utils.logging import app_logger
# Import file operations utilities directly
from coding_agent.utils.file_operations import list_directory, read_file


def initialize_files_content(project_root: str, max_depth: int = 2) -> Dict[str, str]:
    """
    Initialize the files_content dictionary with a listing of files in the project directory.
    
    Args:
        project_root: The absolute path to the project's root directory
        max_depth: Maximum directory depth to traverse
        
    Returns:
        Dict[str, str]: Dictionary with relative file paths as keys and contents/descriptions as values
    """
    app_logger.info(f"Initializing files_content for project root: {project_root}")
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
                        app_logger.debug(f"Read key file: {item_rel_path}")
                    else:
                        files_content[item_rel_path] = f"File exists but couldn't be read: {content}"
                else:
                    # For other files, just note their existence
                    _, ext = os.path.splitext(item.lower())
                    if ext in ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs', '.php', '.rb', '.md', '.txt', '.json', '.yaml', '.yml', '.ini', '.cfg']:
                        files_content[item_rel_path] = "File exists (content not loaded initially)"
        
        except Exception as e:
            app_logger.error(f"Error exploring directory {dir_path}: {str(e)}")
    
    # Start the recursive exploration from the project root
    explore_directory(project_root, 1)
    
    app_logger.info(f"Initialized files_content with {len(files_content)} entries")
    return files_content


def main():
    """
    Main entry point for the coding agent.
    Sets up and runs the LangGraph workflow.
    """
    # parse required project root path
    parser = argparse.ArgumentParser(description="Run Coding Agent on specified codebase")
    parser.add_argument('--path', '-p', help='Path to project root folder', required=True)
    args = parser.parse_args()
    project_root = os.path.abspath(args.path) # Ensure project_root is absolute
    app_logger.info(f"Starting Coding Agent with project root: {project_root}")
    print("🤖 Starting Coding Agent...")
    
    # Display current model information
    model_info = get_current_model_info()
    app_logger.info(f"Using AI provider: {model_info['provider']} (Model: {model_info['model_name']})")
    print(f"Using AI provider: {model_info['provider'].upper()} (Model: {model_info['model_name']})")
    
    # Option to switch model
    print("\nAvailable AI models:")
    models = list_available_models()
    for i, model in enumerate(models, 1):
        status = "✓ Available" if model.get("available", False) else "✗ Not available"
        reason = f" - {model.get('reason')}" if not model.get("available", False) else ""
        print(f"{i}. {model['provider'].upper()} ({model['model_name']}) {status}{reason}")
    
    print("\nTo switch models, enter the number of the model you want to use, or press Enter to continue.")
    choice = input("Your choice (or Enter to continue): ").strip()
    
    if choice and choice.isdigit():
        choice_idx = int(choice) - 1
        if 0 <= choice_idx < len(models):
            selected_model = models[choice_idx]
            if selected_model.get("available", False):
                switch_model(selected_model["provider"])
                app_logger.info(f"Switched to {selected_model['provider']} ({selected_model['model_name']})")
                print(f"\nSwitched to {selected_model['provider'].upper()} ({selected_model['model_name']})")
            else:
                error_msg = f"Cannot switch to {selected_model['provider']} - {selected_model.get('reason', 'Not available')}"
                app_logger.warning(error_msg)
                print(f"\n{error_msg}")
    
    # Get the workflow
    app = create_workflow()
    
    # Initialize the state
    task = input("\nEnter your coding task: ")
    app_logger.info(f"User task: {task}")
    
    # Pre-populate the files_content dictionary with project structure
    print("Scanning project directory structure...")
    files_content = initialize_files_content(project_root, max_depth=2)
    print(f"Found {len(files_content)} files and directories")
    
    initial_state: AgentState = {
        "messages": [],
        "task": task,
        "project_root": project_root, # Add project_root to state
        "files_content": files_content,  # Pre-populated files_content
        "current_plan": None,
        "thought_process": None,
        "next_action": None,
        "action_input": None,
        "action_output": None,
        "final_answer": None,
        "model_provider": get_current_model_info()["provider"],  # Track current provider
    }
    
    # Run the workflow
    print(f"\nExecuting task: {task}\n")
    app_logger.info(f"Starting workflow execution for task: {task}")
    
    # Stream the results
    switch_prompt_shown = False
    for step in app.stream(initial_state):
        node = step.get("current_node")
        state = step.get("state", {})
        
        if node:
            app_logger.debug(f"Executing workflow step: {node}")
        
        # Option to switch models during execution (only show once per step)
        if node and not switch_prompt_shown:
            # Check if user wants to switch models (non-blocking input check)
            print("\nPress 'm' + Enter at any time to change the AI model, or just press Enter to continue...")
            user_input = input("")
            
            if user_input.lower() == 'm':
                # Show model selection menu
                print("\nSwitch to a different AI model:")
                models = list_available_models()
                for i, model in enumerate(models, 1):
                    status = "✓ Available" if model.get("available", False) else "✗ Not available"
                    print(f"{i}. {model['provider'].upper()} ({model['model_name']}) {status}")
                
                choice = input("Your choice (or Enter to cancel): ").strip()
                if choice and choice.isdigit():
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(models):
                        selected_model = models[choice_idx]
                        if selected_model.get("available", False):
                            current_model = get_current_model_info()["provider"]
                            new_model = selected_model["provider"]
                            
                            if current_model != new_model:
                                switch_model(new_model)
                                app_logger.info(f"Switched from {current_model} to {new_model}")
                                print(f"Switched from {current_model.upper()} to {new_model.upper()}")
                                
                                # Update state to track model change
                                if isinstance(state, dict):
                                    state["model_provider"] = new_model
                            else:
                                print(f"Already using {current_model.upper()}")
            
            switch_prompt_shown = True
        else:
            # Reset the switch prompt flag at each new node
            switch_prompt_shown = (node == None)
        
        if switch_prompt_shown == False:
            print(f"Step: {node}")
            
            # Show more detailed information based on the node
            if node == "analyze_task" and state.get("current_plan"):
                app_logger.info("Plan generated")
                print("\nPlan:")
                for item in state.get("current_plan", []):
                    print(f"- {item}")
                print("")
            
            elif node in ["read_file", "write_file", "edit_file", "list_directory"]:
                action_output = state.get('action_output', '')
                app_logger.debug(f"Action output: {action_output}")
                # Only print output if it's not None or empty
                if action_output:
                    print(f"Action output: {action_output}")
            
            elif node == "generate_solution":
                app_logger.info("Solution generated")
                final_answer = state.get("final_answer", "")
                print("\n==== SOLUTION ====")
                print(final_answer)
                print("==================\n")
    
    app_logger.info("Task completed successfully")
    print("Task completed! 🎉")


if __name__ == "__main__":
    main()
