# main.py - MCP Server for sokrates library

# This script sets up an MCP server using the FastMCP framework to provide tools for prompt refinement and execution workflows.
# It includes several tools that can be used to refine prompts, execute them with external LLMs, break down tasks,
# generate ideas, perform code reviews, and list available models/providers.
#
# Main Purpose
# The primary purpose of this script is to create a robust MCP server that facilitates interaction with large language models
# through various prompt engineering workflows. It provides APIs for refining prompts, executing them externally,
# breaking down complex tasks, generating ideas, performing code reviews, and listing available models/providers.
#
# Parameters
# - `refine_prompt`: Refines a given prompt by enriching it with additional context.
#   - `prompt` (str): The input prompt to be refined.
#   - `refinement_type` (str, optional): Type of refinement ('code' or 'default'). Default is 'default'.
#   - `provider` (str, optional): Name of the provider to use for refinement. Default is 'default'.
#   - `model` (str, optional): Model name for refinement. Default is 'default'.
#
# - `refine_and_execute_external_prompt`: Refines a prompt and executes it with an external LLM.
#   - `prompt` (str): The input prompt to be refined and executed.
#   - `provider` (str, optional): Name of the provider to use for LLM interactions. Default is 'default'.
#   - `refinement_model` (str, optional): Model for refinement. Default is 'default'.
#   - `execution_model` (str, optional): Model for execution. Default is 'default'.
#   - `refinement_type` (str, optional): Type of refinement ('code' or 'default'). Default is 'default'.
#
# - `handover_prompt`: Hands over a prompt to an external LLM for processing.
#   - `prompt` (str): The prompt to be executed externally.
#   - `provider` (str, optional): Name of the provider to use for LLM interactions. Default is 'default'.
#   - `model` (str, optional): Model name for execution. Default is 'default'.
#   - `temperature` (float, optional): Temperature for the external execution. Default is 0.7.
#
# - `breakdown_task`: Breaks down a task into sub-tasks with complexity ratings.
#   - `task` (str): The full task description to break down.
#   - `provider` (str, optional): Name of the provider to use for LLM interactions. Default is 'default'.
#   - `model` (str, optional): Model name for processing. Default is 'default'.
#
# - `generate_random_ideas`: Generates random ideas on a random topic.
#   - `idea_count` (int, optional): Number of ideas to generate. Default is 1.
#   - `provider` (str, optional): Name of the provider to use for LLM interactions. Default is 'default'.
#   - `model` (str, optional): Model name for generation. Default is 'default'.
#   - `temperature` (float, optional): Temperature for idea generation. Default is 0.7.
#
# - `generate_ideas_on_topic`: Generates ideas on a specific topic.
#   - `topic` (str): The topic to generate ideas for.
#   - `provider` (str, optional): Name of the provider to use for LLM interactions. Default is 'default'.
#   - `model` (str, optional): Model name for generation. Default is 'default'.
#   - `idea_count` (int, optional): Number of ideas to generate. Default is 1.
#   - `temperature` (float, optional): Temperature for idea generation. Default is 0.7.
#
# - `generate_code_review`: Generates a code review in markdown format.
#   - `source_file_paths` (list): List of source file paths to be reviewed.
#   - `target_directory` (str): Directory to store the resulting review files.
#   - `provider` (str, optional): Name of the provider to use for LLM interactions. Default is 'default'.
#   - `model` (str, optional): Model name for code review generation. Default is 'default'.
#   - `review_type` (str, optional): Type of review ('style', 'security', 'performance', 'quality'). Default is 'quality'.
#
# - `list_available_models_for_provider`: Lists all available large language models for a specific provider.
#   - `provider_name` (str, optional): Name of the provider to list models for. Default is empty (uses default).
#
# - `list_available_providers`: Lists all configured and available API providers.
#
# Usage Examples
# ```python
# Refine a prompt
# await refine_prompt("Write a Python function to sort a list", refinement_type="code")
#
# # Refine and execute a prompt with an external LLM
# await refine_and_execute_external_prompt(
#     "Generate a summary of the following text: ...",
#     refinement_model="model1",
#     execution_model="model2"
# )
#
# # Hand over a prompt to an external LLM
# await handover_prompt("Translate this text to French: ...")
#
# # Break down a task into sub-tasks
# await breakdown_task("Implement user authentication system")
#
# # Generate random ideas
# await generate_random_ideas(idea_count=3)
#
# # Generate ideas on a topic
# await generate_ideas_on_topic("AI in healthcare", idea_count=5)
#
# # Generate code review
# await generate_code_review(
#     source_file_paths=["/path/to/file1.py", "/path/to/file2.py"],
#     target_directory="/path/to/reviews"
# )
#
# # List available models for a provider
# await list_available_models_for_provider("my-provider")
#
# # List all available providers
# await list_available_providers()
# ```
#

from typing import Annotated, Optional
from pydantic import Field
from .mcp_config import MCPConfig
from .workflow import Workflow
from fastmcp import FastMCP, Context
import logging
import os
import argparse

MCP_NAME = "sokrates-mcp"
VERSION = "0.2.0"
DEFAULT_PROVIDER_IDENTIFIER = "default"
DEFAULT_MODEL_IDENTIFIER = "default"
DEFAULT_REFINEMENT_TYPE = "default"
DEFAULT_CODE_REVIEW_TYPE = "quality"

config = MCPConfig()
workflow = Workflow(config)

# Configure logging for better visibility of fastmcp operations
log_file_path = os.path.expanduser("~/.sokrates-mcp/server.log")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
logging.basicConfig(level=logging.INFO, filename=log_file_path, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the MCP Server
mcp = FastMCP(
    name=MCP_NAME,
    instructions="A MCP server for using sokrates python library's tools: prompt refinement and improvement workflows.",
    version=VERSION
)

# -------------------------------------------------------------------------

@mcp.tool(
    name="refine_prompt",
    description="Refines a given prompt by enriching the prompt with additional context and improving clarity for further processing by large language models. A prompt received like this can be sent further directly after receiving the response. The refinement_type can be used to improve the results: e.g. for a coding task this should be set to the code type.",
    tags={"prompt","refinement"}
)
async def refine_prompt(prompt: Annotated[str, Field(description="Input prompt that should be refined")],
    ctx: Context,
    refinement_type: Annotated[str, Field(description="The type of the refinement. This could be 'code' (for refining coding tasks) or 'default' . The default type is: default", default=DEFAULT_REFINEMENT_TYPE)],
    provider: Annotated[str, Field(description="The name of the provider to use for the prompt refinement process. The default model name is 'default', which will pick the server's default provider configured.", default=DEFAULT_PROVIDER_IDENTIFIER)],
    model: Annotated[str, Field(description="The name of the model that should be used for the prompt refinement process. The default model name is 'default', which will pick the server's default model.", default=DEFAULT_MODEL_IDENTIFIER)],
    ) -> str:
    """
    Refines a given prompt by enriching the input prompt with additional context and improving clarity
    for further processing by large language models.

    Args:
        prompt (str): The input prompt to be refined.
        ctx (Context): The MCP context object.
        refinement_type (str, optional): Type of refinement ('code' or 'default'). Default is 'default'.
        provider (str, optional): Name of the provider to use for refinement. Default is 'default'.
        model (str, optional): Model name for refinement. Default is 'default'.

    Returns:
        str: The refined prompt.

    This function delegates the actual refinement work to the workflow.refine_prompt method.
    """
    return await workflow.refine_prompt(prompt=prompt, ctx=ctx, provider=provider, model=model, refinement_type=refinement_type)

# -------------------------------------------------------------------------

@mcp.tool(
    name="refine_and_execute_external_prompt",
    description="Refines a given prompt by enriching the input prompt with additional context and then executes the prompt with an external llm. It delivers back the exection result of the refined prompt on the external llm. The refinement_type can be used to improve the results: e.g. for a coding task this should be set to the code type.",
    tags={"prompt","refinement","external_processing"}
)
async def refine_and_execute_external_prompt(prompt: Annotated[str, Field(description="Input prompt that should be refined and then processed.")],
    ctx: Context,
    provider: Annotated[str, Field(description="The name of the provider to use for LLM interactions. The default model name is 'default', which will pick the server's default provider configured.", default=DEFAULT_PROVIDER_IDENTIFIER)],
    refinement_model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the prompt refinement process. The default refinement model name is 'default', which will pick the server's default model.", default=DEFAULT_MODEL_IDENTIFIER)],
    execution_model: Annotated[str, Field(description="[Optional] The name of the external model that should be used for the execution of the refined prompt. The default execution model name is 'default', which will pick the server's default model.", default=DEFAULT_MODEL_IDENTIFIER)],
    refinement_type: Annotated[str, Field(description="The type of the refinement. This could be 'code' (for refining coding tasks) or 'default' for any general refinement tasks. The default type is: default", default=DEFAULT_REFINEMENT_TYPE)],
    ) -> str:
    """
    Refines a given prompt and executes it with an external LLM.

    Args:
        prompt (str): The input prompt to be refined and executed.
        ctx (Context): The MCP context object.
        provider (str, optional): Name of the provider to use for LLM interactions. Default is 'default'.
        refinement_model (str, optional): Model for refinement. Default is 'default'.
        execution_model (str, optional): Model for execution. Default is 'default'.
        refinement_type (str, optional): Type of refinement ('code' or 'default'). Default is 'default'.

    Returns:
        str: The execution result of the refined prompt from the external LLM.

    This function first refines the prompt and then executes it with an external LLM.
    """
    return await workflow.refine_and_execute_external_prompt(prompt=prompt, ctx=ctx, provider=provider, refinement_model=refinement_model, execution_model=execution_model, refinement_type=refinement_type)

# -------------------------------------------------------------------------

@mcp.tool(
    name="handover_prompt",
    description="Hands over a prompt to an external llm for processing and delivers back the processed result.",
    tags={"prompt","refinement"}
)
async def handover_prompt(prompt: Annotated[str, Field(description="Prompt that should be executed externally.")],
    ctx: Context,
    provider: Annotated[str, Field(description="The name of the provider to use for LLM interactions. The default model name is 'default', which will pick the server's default provider configured.", default=DEFAULT_PROVIDER_IDENTIFIER)],
    temperature: Annotated[float, Field(description="[Optional] The temperature of the llm to use for generating the ideas. The default value is 0.7 .", default=0.7)],
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the external prompt processing. The default model name is 'default', which will pick the server's default model.", default=DEFAULT_MODEL_IDENTIFIER)],
    ) -> str:
    """
    Hands over a prompt to an external LLM for processing.

    Args:
        prompt (str): The prompt to be executed externally.
        ctx (Context): The MCP context object.
        provider (str, optional): Name of the provider to use for LLM interactions. Default is 'default'.
        model (str, optional): Model name for execution. Default is 'default'.
        temperature (float, optional): Temperature to use for the external execution. Default is 0.7.

    Returns:
        str: The processed result from the external LLM.

    This function delegates the prompt execution to an external LLM and returns the result.
    """
    return await workflow.handover_prompt(prompt=prompt, ctx=ctx, provider=provider, model=model)

# -------------------------------------------------------------------------

@mcp.tool(
    name="breakdown_task",
    description="Breaks down a task into sub-tasks back a json list of sub-tasks with complexity ratings.",
    tags={"prompt","task","breakdown"}
)
async def breakdown_task(task: Annotated[str, Field(description="The full task description to break down further.")],
    ctx: Context,
    provider: Annotated[str, Field(description="The name of the provider to use for LLM interactions. The default model name is 'default', which will pick the server's default provider configured.", default=DEFAULT_PROVIDER_IDENTIFIER)],
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the external prompt processing. The default model name is 'default', which will pick the server's default model.", default=DEFAULT_MODEL_IDENTIFIER)],
    ) -> str:
    """
    Breaks down a task into sub-tasks and returns a JSON list of sub-tasks with complexity ratings.

    Args:
        task (str): The full task description to break down.
        ctx (Context): The MCP context object.
        provider (str, optional): Name of the provider to use for LLM interactions. Default is 'default'.
        model (str, optional): Model name for processing. Default is 'default'.

    Returns:
        str: A JSON string containing the list of sub-tasks with complexity ratings.

    This function uses an LLM to analyze the task and break it down into manageable sub-tasks.
    """
    return await workflow.breakdown_task(task=task, ctx=ctx, provider=provider, model=model)

@mcp.tool(
    name="generate_random_ideas",
    description="Invents and generates a random topic an generates the provided count of ideas on the topic.",
    tags={"idea", "generator","invention","random"}
)
async def generate_random_ideas(ctx: Context,
    idea_count: Annotated[int, Field(description="[Optional] The number of ideas to generate. The default value is 1.", default=1)],
    provider: Annotated[str, Field(description="The name of the provider to use for LLM interactions. The default model name is 'default', which will pick the server's default provider configured.", default=DEFAULT_PROVIDER_IDENTIFIER)],
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the generation. The default model name is 'default', which will pick the server's default model.", default=DEFAULT_MODEL_IDENTIFIER)],
    temperature: Annotated[float, Field(description="[Optional] The temperature of the llm to use for generating the ideas. The default value is 0.7 .", default=0.7)]
    ) -> str:
    return await workflow.generate_random_ideas(ctx=ctx, provider=provider, model=model, idea_count=idea_count, temperature=temperature)

@mcp.tool(
    name="generate_ideas_on_topic",
    description="Generates the provided count of ideas on the provided topic.",
    tags={"idea","generator", "idea generation", "invention"}
)
async def generate_ideas_on_topic(
    ctx: Context,
    topic: Annotated[str, Field(description="The topic to generate ideas for.")],
    provider: Annotated[str, Field(description="The name of the provider to use for LLM interactions. The default model name is 'default', which will pick the server's default provider configured.", default=DEFAULT_PROVIDER_IDENTIFIER)],
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the generation. The default model name is 'default', which will pick the server's default model.", default=DEFAULT_MODEL_IDENTIFIER)],
    idea_count: Annotated[int, Field(description="[Optional] The number of ideas to generate. The default value is 1.", default=1)],
    temperature: Annotated[float, Field(description="The temperature of the llm to use for generating the ideas. The default value is 0.7 .", default=0.7)]
    ) -> str:
    return await workflow.generate_ideas_on_topic(ctx=ctx, provider=provider, model=model, topic=topic, idea_count=idea_count, temperature=temperature)

@mcp.tool(
    name="generate_code_review",
    description="Generates a code review in markdown format in a file on the local file system and returns the path to the code review. It supports multiple types of code reviews.",
    tags={"coding","review","markdown","file"}
)
async def generate_code_review(
    ctx: Context,
    source_directory: Annotated[str, Field(description="The absolute directory path containing source files to create reviews for. This should contain source files on the local filesystem.")],
    source_file_paths: Annotated[list, Field(description="A list of absolute source file paths that should be reviewed. The paths should be absolute paths in the local filesystem.")],
    target_directory: Annotated[str, Field(description="The directory to store the resulting review markdown files. This should point to the desired target path for the markdown files on the local filesystem.")],
    provider: Annotated[str, Field(description="The name of the provider to use for LLM interactions. The default model name is 'default', which will pick the server's default provider configured.", default=DEFAULT_PROVIDER_IDENTIFIER)],
    model: Annotated[str, Field(description="[Optional] The name of the model that should be used for the generation. The default model name is 'default', which will pick the server's default model.", default=DEFAULT_MODEL_IDENTIFIER)],
    review_type: Annotated[str, Field(description="[Optional] The type of review to execute. Choices are: 'style', 'security', 'performance', 'quality' . The default is 'quality'", default=DEFAULT_CODE_REVIEW_TYPE)]
    ) -> str:
    return await workflow.generate_code_review(ctx=ctx, provider=provider, model=model, review_type=review_type, source_directory=source_directory, source_file_paths=source_file_paths, target_directory=target_directory)

@mcp.tool(
    name="read_from_file",
    description="Read a file from the local disk at the given file path and return it's contents.",
    tags={"file","read","load","local"}
)
async def read_from_file(
    ctx: Context, 
    file_path: Annotated[str, Field(description="The source file path to use for reading the file. This should be an absolute file path on the disk.")], 
    ) -> str:
    return await workflow.read_from_file(ctx=ctx, file_path=file_path)

@mcp.tool(
    name="read_files_from_directory",
    description="Read files from the local disk from the given directory path and return the file contents. You can also provide a list of file extentsions to include optionally.",
    tags={"directory","read","load","local"}
)
async def read_files_from_directory(
    ctx: Context, 
    directory_path: Annotated[str, Field(description="The source directory path to use for reading the files. This should be an absolute file path on the disk.")],
    file_extensions: Annotated[list[str], Field(description="A list of file extensions to include when reading the files. For markdown files you could use ['.md']", default=None)],
    ) -> str:
    return await workflow.read_files_from_directory(ctx=ctx, directory_path=directory_path, file_extensions=file_extensions)

@mcp.tool(
    name="directory_tree",
    description="Provides a recursive directory file listing for the given directory path.",
    tags={"directory","list","local"}
)
async def directory_tree(
    ctx: Context, 
    directory_path: Annotated[str, Field(description="The source directory path to use for reading the files. This should be an absolute file path on the disk.")]
    ) -> str:
    return await workflow.directory_tree(ctx=ctx, directory_path=directory_path)


@mcp.tool(
    name="store_to_file",
    description="Store a file with the provided content to the local drive at the provided file path.",
    tags={"file","store","save","local"}
)
async def store_to_file(
    ctx: Context, 
    file_path: Annotated[str, Field(description="The target file path to use for storing the file. This should be an absolute file path on the disk.")],
    file_content: Annotated[str, Field(description="The content that should be written to the target file.")],
    ) -> str:
    return await workflow.store_to_file(ctx=ctx, file_path=file_path, file_content=file_content)

@mcp.tool(
    name="roll_dice",
    description="Rolls the given number of dice with the specified number of sides for the given number of times and returns the result. For example you can also instruct to throw a W12, which should then set the side_count to 12.",
    tags={"dice","roll","random"}
)
async def roll_dice(
    ctx: Context, 
    number_of_dice: Annotated[int, Field(description="The number of dice to to use for rolling.", default=1)],
    side_count: Annotated[int, Field(description="The number of sides of the dice to use for rolling.", default=6)],
    number_of_rolls: Annotated[int, Field(description="The count of dice rolls to execute.", default=1)]
    ) -> str:
    return await workflow.roll_dice(ctx=ctx, number_of_dice=number_of_dice, side_count=side_count, number_of_rolls=number_of_rolls)


@mcp.tool(
    name="list_available_models_for_provider",
    description="Lists all available large language models and the target api endpoint configured as provider for the sokrates-mcp server.",
    tags={"external","llm","models","list"}
)
async def list_available_models_for_provider(ctx: Context, provider_name: Annotated[str, Field(description="The provider name to list the available models for", default="")]) -> str:
    return await workflow.list_available_models_for_provider(ctx=ctx, provider_name=provider_name)

@mcp.tool(
    name="list_available_providers",
    description="Lists all configured and available API providers for large language models for the sokrates-mcp server.",
    tags={"external","llm","providers","list"}
)
async def list_available_providers(ctx: Context):
    return await workflow.list_available_providers(ctx=ctx)

def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Sokrates MCP Server')
    parser.add_argument('--transport', choices=['stdio', 'sse', 'http'], default='stdio',
                       help='Transport method (default: stdio)')
    parser.add_argument('--host', type=str, default="127.0.0.1",
                       help='host for HTTP and sse transport (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8000,
                       help='Port number for HTTP transport (default: 8000)')
    
    args = parser.parse_args()
    
    # Run the MCP server with specified transport and port
    if args.transport == 'stdio':
        mcp.run(transport=args.transport)
    else:
        mcp.run(transport=args.transport, port=args.port, host=args.host)

if __name__ == "__main__":
    main()
