# sokrates-mcp

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Version: 0.4.1](https://img.shields.io/badge/version-0.4.1-green)](https://github.com/Kubementat/sokrates-mcp)

A MCP server offering tools for prompt refinement and execution workflows using the FastMCP framework and the `sokrates` python library.

## Features

- Multiple provider/APU support
- Available Model/Provider listing
- Prompt refinement with different types (code/default)
- External LLM processing
- Task breakdown into sub-tasks
- Create code reviews for Python source files
- Generate random ideas
- Generate ideas to a topic

Have a look at the [sokrates library](https://github.com/Kubementat/sokrates).

## Installation & Setup

### Prerequisites

Ensure you have:
* Python 3.10+
* uv (fast package installer)

### Install from PyPi
```bash
pip install sokrates-mcp

# or using uv (recommended)
## basic version: 
uv pip install sokrates-mcp
```

### Alternative - Local Configuration from git

1. Clone the repository if hosted:
```bash
git clone https://github.com/Kubementat/sokrates-mcp.git
cd sokrates-mcp
```

2. Install dependencies using pyproject.toml:
```bash
uv sync
```

### Setup Server Configuration File

#### Via git installed version
```bash
mkdir $HOME/.sokrates-mcp
cp config.yml.example $HOME/.sokrates-mcp/config.yml
# edit the according endpoints to your use case
vim $HOME/.sokrates-mcp/config.yml
```

#### From scratch
Create the configuration file:
```bash
mkdir $HOME/.sokrates-mcp
vim $HOME/.sokrates-mcp/config.yml
```

Then use this as template and adjust it to your use case:
```yaml
refinement_prompt_filename: refine-prompt.md
refinement_coding_prompt_filename: refine-coding-v3.md

# providers
default_provider: local
providers:
  - name: local
    type: openai
    api_endpoint: http://localhost:1234/v1
    api_key: "not-required"
    default_model: "qwen/qwen3-4b-2507"
  - name: external
    type: openai
    api_endpoint: http://CHANGEME/v1
    api_key: CHANGEME
    default_model: CHANGEME
```

### Setup as mcp server in other tools (Example for LM Studio)

#### For local Git installed version
```yaml
{
  "mcpServers": {
    "sokrates": {
      "command": "uv",
      "args": [
        "run",
        "sokrates-mcp"
      ],
      "cwd": "YOUR_PATH_TO_sokrates-mcp",
      "timeout": 600000
    }
  }
}
```

#### via uvx
```yaml
{
  "mcpServers": {
    "sokrates": {
      "command": "uvx",
      "args": [
        "sokrates-mcp"
      ]
    }
  }
}
```

## Usage Examples

### Starting the Server

```bash
# from local git repo
uv run sokrates-mcp

# without checking out the git repo
uvx sokrates-mcp
```

### Listing available command line options
```bash
# from local git repo
uv run sokrates-mcp --help

# without checking out the git repo
uvx sokrates-mcp --help
```

## Architecture & Technical Details

The server follows a modular design pattern:
1. Tools are registered in `main.py` using FastMCP decorators
2. Dependency management via pyproject.toml
3. Configuration files stored in `$HOME/.sokrates-mcp/` directory


## Contributing Guidelines

1. Fork the repository and create feature branches
2. Follow PEP8 style guide with 4-space indentation
3. Submit pull requests with:
   - Clear description of changes
   - Updated tests (see Testing section)
   - Documentation updates

## Available Tools

See the [main.py](src/sokrates_mcp/main.py) file for a list of all mcp tools in the server

## Project Structure

- `src/sokrates_mcp/main.py`: Sets up the MCP server and registers tools
- `src/sokrates_mcp/mcp_config.py`: Configuration management
- `src/sokrates_mcp/utils.py`: Helper and utility methods
- `src/sokrates_mcp/workflow.py`: Business logic for prompt refinement and execution
- `pyproject.toml`: Dependency management


**Common Error:**
If you see "ModuleNotFoundError: fastmcp", ensure:
1. Dependencies are installed (`uv sync`)
2. Python virtual environment is activated

## Changelog

**0.4.1 (Sep 2025)**
- fix roll_dice tool

**0.4.0 (Aug 2025)**
- adds new tools:
  - read_files_from_directory
  - directory_tree
  - logging refactoring in workflow.py

**0.3.0 (Aug 2025)**
- adds new tools:
    - roll_dice
    - read_from_file
    - store_to_file
- refactorings - code quality - still ongoing

**0.2.0 (Aug 2025)**
- First published version
- Update to latest sokrates library version
- bugfixes and cleanup
- multi provider/API support in the configuration file 

**0.1.5 (July 2025)**
- Updated README with comprehensive documentation
- Added tool descriptions and usage examples
- Improved project structure overview

**0.1.0 (March 7, 2025)**
- Initial release with refinement tools
- Basic FastMCP integration

Bug reports and feature requests: [GitHub Issues](https://github.com/Kubementat/sokrates-mcp/issues)
