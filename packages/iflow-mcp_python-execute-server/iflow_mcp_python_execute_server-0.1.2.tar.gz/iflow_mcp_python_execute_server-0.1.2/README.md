# Python Execute Server

A Model Context Protocol (MCP) server that provides Python code execution capabilities for Large Language Models (LLMs).

## Features

- **Python Code Execution**: Execute Python code in a persistent REPL environment
- **Data Analysis Support**: Perform calculations and data analysis with full Python ecosystem
- **File Output**: Automatically save executed code to timestamped files
- **Workspace Integration**: Execute code within a designated workspace directory
- **Error Handling**: Comprehensive error reporting and exception handling
- **Output Capture**: Capture and return both stdout and execution results

## Tools Provided

- `python_repl_tool`: Execute Python code and perform data analysis or calculations with visible output

## Execution Features

### Code Execution
- Persistent REPL environment maintains state between executions
- Support for all Python standard library modules
- Data analysis and scientific computing capabilities
- Real-time output capture and display

### File Management
- Automatic code saving with unique timestamped filenames
- Organized file storage in workspace/python directory
- Code preservation for debugging and reference

### Output Handling
- Stdout capture for print statements and output
- Error detection and reporting
- Structured result formatting
- Multi-format result support

## Configuration Options

- `--workspace-path`: Set the workspace directory (default: ./workspace)

## Server Configuration

To use this server with MCP clients, add the following configuration to your MCP settings:

For development or when using `uv`:

```json
{
  "mcpServers": {
    "python-execute-server": {
      "command": "uv",
      "args": ["--directory", "directory_of_python-execute-server", "run", "python-execute-server", "--workspace-path", "/path/to/your/workspace"],
      "env": {}
    }
  }
}
```

## Usage Examples

### Basic Code Execution
```python
# Execute simple calculations
result = await python_repl_tool("print(2 + 2)")
# Output: Successfully executed code with Stdout: 4
```

### Data Analysis
```python
# Perform data analysis
code = """
import pandas as pd
import numpy as np

data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
df = pd.DataFrame(data)
print(df.describe())
"""
result = await python_repl_tool(code)
```

### Mathematical Calculations
```python
# Complex mathematical operations
code = """
import math
result = math.sqrt(16) + math.pi
print(f"Result: {result}")
"""
result = await python_repl_tool(code)
```

## REPL Environment

### Persistent State
- Variables and imports persist between executions
- Allows for multi-step data analysis workflows
- State maintained throughout session

### Library Support
- Full access to Python standard library
- Support for popular data science libraries (pandas, numpy, matplotlib, etc.)
- Extensible with additional package installations

### Error Handling
- Graceful error capture and reporting
- Exception details preserved and returned
- Non-blocking error handling

## File Output System

### Automatic Saving
- All executed code automatically saved to files
- Unique filenames with timestamp and random suffix
- Organized storage in workspace/python directory

### File Naming Convention
```
replaceChatId_{timestamp}_{random_number}.py
```

### Output Tracking
- File paths returned in execution results
- Support for multiple output formats
- Integration with file management systems

## Safety Features

- **Workspace Isolation**: Code execution contained within workspace
- **Error Containment**: Exceptions don't crash the server
- **Input Validation**: Code input validation and sanitization
- **Resource Management**: Proper cleanup and resource handling

## Use Cases

- **Data Analysis**: Statistical analysis and data processing
- **Mathematical Calculations**: Complex mathematical operations
- **Prototyping**: Quick code testing and validation
- **Educational**: Learning and experimenting with Python
- **Automation**: Script execution and task automation

## License

MIT License - see LICENSE file for details.