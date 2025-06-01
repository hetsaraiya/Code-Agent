# Coding Agent

An intelligent coding agent powered by LangGraph that can read, analyze, and modify files in your codebase.

## Features

### File Operations
The agent supports several file operations:

1. **read_file** - Read the complete contents of a file
2. **read_file_lines** - Read specific lines from a file (NEW!)
3. **write_file** - Write content to a file
4. **edit_file** - Edit a file by replacing text
5. **list_directory** - List files in a directory

### Read File Lines Feature

The `read_file_lines` functionality allows the LLM to read specific line ranges from files, which is particularly useful for:

- Reading function definitions without loading entire files
- Examining specific code blocks or classes
- Analyzing error-prone sections of code
- Reviewing specific parts of large configuration files

#### Usage

The LLM can use this action with the following parameters:
- `file_path`: Relative path to the file (from project root)
- `from_line`: Starting line number (1-indexed, inclusive)
- `to_line`: Ending line number (1-indexed, inclusive)

#### Example

```json
{
  "action": "read_file_lines",
  "parameters": {
    "file_path": "src/main.py",
    "from_line": 10,
    "to_line": 25
  }
}
```

This will read lines 10-25 from `src/main.py` and store the result with a key like `src/main.py:10-25` in the agent's state.

#### Error Handling

The function includes comprehensive error handling:
- Validates that line numbers are positive integers
- Ensures `from_line ≤ to_line`
- Checks if the requested lines exist in the file
- Automatically adjusts `to_line` if it exceeds file length
- Provides clear error messages for debugging

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt` or use `uv`
3. Set up your AI model environment variables
4. Run with: `python main.py --path /path/to/your/project`

## Configuration

The agent supports multiple AI providers:
- OpenAI GPT models
- Anthropic Claude models  
- Google Gemini models

Configure your preferred provider via environment variables or select during runtime.

## Usage

```bash
python main.py --path /path/to/your/project
```

The agent will:
1. Scan your project structure
2. Ask for your coding task
3. Analyze the task and create a plan
4. Execute the necessary file operations
5. Provide a comprehensive solution

## Architecture

The agent uses LangGraph for workflow management and includes:
- **Core reasoning** for task analysis and planning
- **File actions** for all file operations
- **Workflow graph** for orchestrating the agent's behavior
- **Model management** for AI provider abstraction
- **Comprehensive logging** for debugging and monitoring

## Contributing

Feel free to contribute improvements, especially for:
- Additional file operations
- Better error handling
- Enhanced reasoning capabilities
- Support for more AI providers