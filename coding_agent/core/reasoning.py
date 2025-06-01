"""
Agent reasoning module for the Coding Agent.
This module defines the agent's reasoning and decision-making capabilities.
"""

from typing import Dict, List, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage
import json
import time
import os # Import os

from coding_agent.core.types import AgentState
from coding_agent.core.model_manager import model_manager
# Import the loggers
from coding_agent.utils.logging import logger
from coding_agent.utils.llm_logging import log_llm_request, log_llm_response


def create_agent():
    """
    Get the current agent instance from the model manager.

    Returns:
        The agent from the model manager
    """
    return model_manager.model


def analyze_task(state: AgentState) -> AgentState:
    """
    Analyze the task and create an initial plan.

    Args:
        state: The current state of the agent

    Returns:
        Updated state with analysis and plan
    """
    logger.info(f"Analyzing task: {state['task'][:50]}...")
    agent = create_agent()
    project_root = state['project_root']

    # Create a system message explaining the agent's capabilities
    system_message = f"""You are a coding agent operating within the project root directory: {project_root}.
You can read, write, and edit files relative to this root.
Your task is to understand user requests and develop a plan to implement them.
You will receive information about files already read and a task to perform.

Analyze the task and break it down into concrete steps.
Specify file paths *relative* to the project root ({project_root}).
"""

    # Create a prompt to analyze the task
    # Use relative paths for keys in files_content
    relative_files_content = {os.path.relpath(k, project_root) if os.path.isabs(k) else k: v
                              for k, v in state['files_content'].items()}

    task_analysis_prompt = f"""
Project Root: {project_root}
Task: {state['task']}

Available files (relative paths) and their content (if read):
{json.dumps(relative_files_content, indent=2)}

Analyze this task and create a step-by-step plan to complete it.
Think about:
1. What files need to be created, read, or modified? (Use relative paths)
2. What code needs to be written or changed?
3. How to implement the functionality in a clean, efficient way?

Provide the plan as a list of steps.
"""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": task_analysis_prompt}
    ]

    logger.debug("Sending task analysis prompt to agent")

    # Manually log the request before sending
    log_llm_request(messages)

    # Get response from the agent
    start_time = time.time()
    response = agent.invoke(messages)
    elapsed_time = time.time() - start_time

    # Manually log the response and timing
    logger.info(f"Task analysis LLM response time: {elapsed_time:.2f}s")
    log_llm_response(response)

    # Update state with the plan
    updated_state = state.copy()
    updated_state["thought_process"] = response.content

    # Extract a structured plan from the response
    plan_lines = [line.strip() for line in response.content.split("\n")
                 if line.strip() and (line.strip().startswith("-") or line.strip()[0].isdigit())]

    updated_state["current_plan"] = plan_lines if plan_lines else ["List project files", "Analyze files", "Implement changes", "Test solution"]

    logger.info(f"Task analysis complete, created plan with {len(updated_state['current_plan'])} steps")

    return updated_state


def determine_next_action(state: AgentState) -> AgentState:
    """
    Determine the next action to take based on the current state.

    Args:
        state: The current state of the agent

    Returns:
        Updated state with the next action to take
    """
    logger.info("Determining next action")
    agent = create_agent()
    project_root = state['project_root']

    # Create a system message explaining the agent's capabilities
    system_message = f"""You are a coding agent operating within the project root directory: {project_root}.
You can perform the following actions. ALL file paths MUST be relative to the project root ({project_root}).
1. read_file - Read the contents of a file. Parameters: file_path (relative path)
2. read_file_lines - Read specific lines from a file. Parameters: file_path (relative path), from_line (integer), to_line (integer)
3. write_file - Write content to a file. Parameters: file_path (relative path), content
4. edit_file - Edit a file by replacing text. Parameters: file_path (relative path), old_string, new_string
5. list_directory - List files in a directory. Parameters: directory_path (relative path, use '.' for project root)
6. search_text - Search for text across files. Parameters: search_term (required), file_extensions (optional list), case_sensitive (optional bool), regex_mode (optional bool), max_results (optional int)
7. finish - Complete the task and provide a final answer. No parameters.

Based on the current state and plan, determine the *single* next action to take.
Return the action name and any parameters needed in JSON format.
Ensure file paths are relative to the project root.
"""

    # Use relative paths for keys in files_content
    relative_files_content = {os.path.relpath(k, project_root) if os.path.isabs(k) else k: v
                              for k, v in state['files_content'].items()}

    # Create a prompt for deciding the next action
    action_prompt = f"""
Project Root: {project_root}
Task: {state['task']}

Current plan:
{state['current_plan']}

Files content (relative paths, content truncated):
{json.dumps({k: (v[:200] + '...' if len(v) > 200 else v) for k, v in relative_files_content.items()}, indent=2)}

Previous action output:
{state.get('action_output', 'No previous actions')}

Determine the single next action to take. Choose from: read_file, write_file, edit_file, list_directory, finish.
Provide the action and its parameters (using relative paths) in the specified format.

Respond ONLY in this format:
```json
{{
  "action": "[action_name]",
  "parameters": {{
    "param1": "value1",
    "param2": "value2"
    // Ensure file_path and directory_path are relative to {project_root}
  }},
  "reasoning": "[your thought process for choosing this action]"
}}
```
"""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": action_prompt}
    ]

    logger.debug("Sending next action prompt to agent")

    # Manually log the request before sending
    log_llm_request(messages)

    # Get response from the agent
    start_time = time.time()
    response = agent.invoke(messages)
    elapsed_time = time.time() - start_time

    # Manually log the response and timing
    logger.info(f"Next action LLM response time: {elapsed_time:.2f}s")
    log_llm_response(response)

    # Parse the response to get the next action and parameters
    action_name = "finish" # Default action
    action_input = {}
    reasoning = "Could not parse action from LLM response."

    try:
        # Extract JSON block from the response
        json_match = response.content.strip()
        if json_match.startswith("```json"):
            json_match = json_match[7:]
        if json_match.endswith("```"):
            json_match = json_match[:-3]

        parsed_response = json.loads(json_match.strip())
        action_name = parsed_response.get("action", "finish")
        action_input = parsed_response.get("parameters", {})
        reasoning = parsed_response.get("reasoning", "No reasoning provided.")

        # Validate paths if present
        for key in ["file_path", "directory_path"]:
             if key in action_input:
                 path_value = action_input[key]
                 if os.path.isabs(path_value):
                     logger.warning(f"LLM provided an absolute path '{path_value}' for {key}. Attempting to use, but relative paths are expected.")
                     # Optionally, try to make it relative, but this might be risky
                     # try:
                     #    action_input[key] = os.path.relpath(path_value, project_root)
                     #    logger.info(f"Converted absolute path to relative: {action_input[key]}")
                     # except ValueError:
                     #    logger.error(f"Could not make path relative: {path_value}")


    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON response for next action: {e}\nResponse content:\n{response.content}")
        # Attempt simpler parsing as fallback (less reliable)
        action_lines = response.content.split("Action:", 1)
        if len(action_lines) > 1:
            action_part = action_lines[1].strip()
            action_name = action_part.split("\n", 1)[0].strip()
        reasoning_lines = response.content.split("Reasoning:", 1)
        if len(reasoning_lines) > 1:
            reasoning = reasoning_lines[1].strip()

    except Exception as e:
         logger.error(f"Unexpected error parsing action response: {e}\nResponse content:\n{response.content}")


    # Update state with the next action
    updated_state = state.copy()
    updated_state["next_action"] = action_name
    updated_state["action_input"] = action_input
    # Append reasoning to the overall thought process
    current_thought = updated_state.get('thought_process', '')
    updated_state["thought_process"] = f"{current_thought}\n\nNext Action Reasoning ({action_name}): {reasoning}"

    logger.info(f"Next action determined: {action_name}")
    if action_input:
        logger.debug(f"Action parameters: {action_input}")

    return updated_state


def generate_solution(state: AgentState) -> AgentState:
    """
    Generate the final solution based on the state.

    Args:
        state: The current state of the agent

    Returns:
        Updated state with the final answer
    """
    logger.info("Generating solution")
    agent = create_agent()
    project_root = state['project_root']

    # Create a system message explaining the agent's task
    system_message = f"""You are a coding agent that has just completed a task within the project root: {project_root}.
Your task is to generate a comprehensive explanation of the solution you've implemented, referencing file paths relative to the project root.
"""

    # Use relative paths for keys in files_content
    relative_files_content = {os.path.relpath(k, project_root) if os.path.isabs(k) else k: v
                              for k, v in state['files_content'].items()}

    # Create a prompt for generating the final answer
    solution_prompt = f"""
Project Root: {project_root}
Original Task: {state['task']}

Thought Process & Actions Taken:
{state.get('thought_process', '')}

Current files content (relative paths, content truncated):
{json.dumps({k: (v[:200] + '...' if len(v) > 200 else v) for k, v in relative_files_content.items()}, indent=2)}

Please generate a comprehensive explanation covering:
1. What changes were made and why (referencing relative file paths).
2. How the final solution addresses the original task.
3. Any potential further improvements or considerations.
"""

    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": solution_prompt}
    ]

    logger.debug("Sending solution generation prompt to agent")

    # Manually log the request before sending
    log_llm_request(messages)

    # Get response from the agent
    start_time = time.time()
    response = agent.invoke(messages)
    elapsed_time = time.time() - start_time

    # Manually log the response and timing
    logger.info(f"Solution generation LLM response time: {elapsed_time:.2f}s")
    log_llm_response(response)

    # Update state with the final answer
    updated_state = state.copy()
    updated_state["final_answer"] = response.content

    logger.info("Solution generated successfully")

    return updated_state
