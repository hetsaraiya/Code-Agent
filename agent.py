"""
Agent module for the Coding Agent.
This module defines the agent's reasoning and planning capabilities.
"""

from typing import Dict, List, Any, Optional, TypedDict, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI


class AgentState(TypedDict):
    """State of the agent workflow."""
    messages: List[Dict[str, Any]]
    task: str
    files_content: Dict[str, str]
    current_plan: Optional[List[str]]
    thought_process: Optional[str]
    next_action: Optional[str]
    action_input: Optional[Dict[str, Any]]
    action_output: Optional[str]
    final_answer: Optional[str]


def create_agent(model_name: str = "gpt-4"):
    """
    Create an agent with the specified model.
    
    Args:
        model_name: Name of the model to use
        
    Returns:
        The agent
    """
    return ChatOpenAI(model=model_name, temperature=0)


def analyze_task(state: AgentState) -> AgentState:
    """
    Analyze the task and create an initial plan.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with analysis and plan
    """
    agent = create_agent()
    
    # Create a system message explaining the agent's capabilities
    system_message = """You are a coding agent that can read, write, and edit files.
Your task is to understand user requests and develop a plan to implement them.
You will receive information about files in the system and a task to perform.

Analyze the task and break it down into concrete steps.
"""
    
    # Create a prompt to analyze the task
    task_analysis_prompt = f"""
Task: {state['task']}

Available files: {list(state['files_content'].keys())}

Analyze this task and create a step-by-step plan to complete it.
Think about:
1. What files need to be created, read, or modified?
2. What code needs to be written or changed?
3. How to implement the functionality in a clean, efficient way?
"""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": task_analysis_prompt}
    ]
    
    # Get response from the agent
    response = agent.invoke(messages)
    
    # Update state with the plan
    updated_state = state.copy()
    updated_state["thought_process"] = response.content
    
    # Extract a structured plan from the response
    # This is a simple implementation - you might want to make this more robust
    plan_lines = [line.strip() for line in response.content.split("\n") 
                  if line.strip() and (line.strip().startswith("-") or line.strip()[0].isdigit())]
    
    updated_state["current_plan"] = plan_lines if plan_lines else ["Analyze files", "Implement changes", "Test solution"]
    
    return updated_state


def determine_next_action(state: AgentState) -> AgentState:
    """
    Determine the next action to take based on the current state.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with the next action to take
    """
    agent = create_agent()
    
    # Create a system message explaining the agent's capabilities
    system_message = """You are a coding agent that can read, write, and edit files.
You can perform the following actions:
1. read_file - Read the contents of a file
2. write_file - Write content to a file
3. edit_file - Edit a file by replacing text
4. list_directory - List files in a directory
5. finish - Complete the task and provide a final answer

Based on the current state and plan, determine the next action to take.
Return the action name and any parameters needed.
"""
    
    # Create a prompt for deciding the next action
    action_prompt = f"""
Task: {state['task']}

Current plan: {state['current_plan']}

Files content:
{state['files_content']}

Previous actions and results:
{state.get('action_output', 'No previous actions')}

Determine the next action to take. Choose from:
1. read_file - Parameters: file_path
2. write_file - Parameters: file_path, content
3. edit_file - Parameters: file_path, old_string, new_string
4. list_directory - Parameters: directory_path
5. finish - No parameters, just provide a final_answer

Respond in this format:
Action: [action_name]
Parameters: [parameters as JSON]
Reasoning: [your thought process]
"""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": action_prompt}
    ]
    
    # Get response from the agent
    response = agent.invoke(messages)
    
    # Parse the response to get the next action and parameters
    # This is a simple implementation - you might want to make this more robust
    action_lines = response.content.split("Action:", 1)
    if len(action_lines) > 1:
        action_part = action_lines[1].strip()
        action_name = action_part.split("\n", 1)[0].strip()
    else:
        action_name = "finish"
    
    param_lines = response.content.split("Parameters:", 1)
    action_input = {}
    if len(param_lines) > 1:
        param_text = param_lines[1].split("Reasoning:", 1)[0].strip()
        # Simple parsing - in a real system you'd use proper JSON parsing with error handling
        if "file_path" in param_text:
            file_path = param_text.split("file_path", 1)[1].split(",", 1)[0].replace(":", "").strip().strip('"\'')
            action_input["file_path"] = file_path
        if "content" in param_text:
            content = param_text.split("content", 1)[1].split(",", 1)[0].replace(":", "").strip().strip('"\'')
            action_input["content"] = content
        if "old_string" in param_text:
            old_string = param_text.split("old_string", 1)[1].split(",", 1)[0].replace(":", "").strip().strip('"\'')
            action_input["old_string"] = old_string
        if "new_string" in param_text:
            new_string = param_text.split("new_string", 1)[1].split(",", 1)[0].replace(":", "").strip().strip('"\'')
            action_input["new_string"] = new_string
        if "directory_path" in param_text:
            directory_path = param_text.split("directory_path", 1)[1].split(",", 1)[0].replace(":", "").strip().strip('"\'')
            action_input["directory_path"] = directory_path
    
    reasoning_lines = response.content.split("Reasoning:", 1)
    reasoning = reasoning_lines[1].strip() if len(reasoning_lines) > 1 else "Moving to the next step in the plan."
    
    # Update state with the next action
    updated_state = state.copy()
    updated_state["next_action"] = action_name
    updated_state["action_input"] = action_input
    updated_state["thought_process"] = f"{updated_state.get('thought_process', '')}\n\nNext action reasoning: {reasoning}"
    
    return updated_state


def generate_solution(state: AgentState) -> AgentState:
    """
    Generate the final solution based on the state.
    
    Args:
        state: The current state of the agent
        
    Returns:
        Updated state with the final answer
    """
    agent = create_agent()
    
    # Create a system message explaining the agent's task
    system_message = """You are a coding agent that can read, write, and edit files.
Your task is to generate a comprehensive explanation of the solution you've implemented.
"""
    
    # Create a prompt for generating the final answer
    solution_prompt = f"""
Task: {state['task']}

Actions taken and their results:
{state.get('thought_process', '')}

Current files content:
{state['files_content']}

Please generate a comprehensive explanation of:
1. What changes you made and why
2. How the solution works
3. Any further improvements that could be made
"""
    
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": solution_prompt}
    ]
    
    # Get response from the agent
    response = agent.invoke(messages)
    
    # Update state with the final answer
    updated_state = state.copy()
    updated_state["final_answer"] = response.content
    
    return updated_state
