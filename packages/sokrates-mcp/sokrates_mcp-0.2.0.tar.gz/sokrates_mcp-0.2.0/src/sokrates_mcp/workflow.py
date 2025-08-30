from fastmcp import Context
from .mcp_config import MCPConfig
from sokrates import FileHelper, RefinementWorkflow, LLMApi, PromptRefiner, IdeaGenerationWorkflow
from sokrates.coding.code_review_workflow import run_code_review
from pathlib import Path
from typing import List
class Workflow:
  
  WORKFLOW_COMPLETION_MESSAGE = "Workflow completed."
  
  def __init__(self, config: MCPConfig):
    """Initialize the workflow with configuration.
    
    Args:
        config (MCPConfig): The MCP configuration object
    """
    self.config = config
    default_provider = self.config.get_default_provider()
    self.default_model = default_provider['default_model']
    self.default_api_endpoint = default_provider['api_endpoint']
    self.default_api_key = default_provider['api_key']

    self.prompt_refiner = PromptRefiner()
    
  def _get_model(self, provider, model=''):
    if not model or model == 'default':
      return provider['default_model']
    return model
  
  def _get_provider(self, provider_name: str = ''):
    if not provider_name or provider_name == 'default':
        provider = self.config.get_default_provider()
    else:
        provider = self.config.get_provider_by_name(provider_name)
    
    if not provider:
        raise ValueError(f"Provider '{provider_name}' not found in configuration")
    return provider
  
  def _initialize_refinement_workflow(self, provider_name: str = '', model: str = ''):
    provider = self._get_provider(provider_name)
    model = self._get_model(provider=provider, model=model)
    refinement_workflow = RefinementWorkflow(api_endpoint=provider['api_endpoint'], api_key=provider['api_key'], model=model)
    return refinement_workflow
    
  def load_refinement_prompt(self, refinement_type : str = 'default'):
    """Load a refinement prompt based on the refinement type.
    
    Args:
        refinement_type (str): Type of refinement ('code' or 'default'). Default is 'default'.
        
    Returns:
        str: The content of the refinement prompt file.
    """
    path=self.config.prompts_directory
    
    if refinement_type == 'code' or refinement_type == 'coding':
      refinement_prompt_file = str(Path(f"{path}/{self.config.refinement_coding_prompt_filename}").resolve())
    else:
      refinement_prompt_file = str(Path(f"{path}/{self.config.refinement_prompt_filename}").resolve())

    return FileHelper.read_file(refinement_prompt_file, verbose=False)
    
  async def refine_prompt(self, prompt: str, ctx: Context, provider: str, model: str, refinement_type: str = 'default') -> str:
    """Refine a given prompt by enriching it with additional context.
    
    Args:
        prompt (str): The input prompt to be refined.
        ctx (Context): The MCP context object.
        provider (str): Name of the provider to use for refinement.
        model (str): Model name for refinement.
        refinement_type (str, optional): Type of refinement ('code' or 'default'). Default is 'default'.
        
    Returns:
        str: The refined prompt.
    """
    refinement_prompt = self.load_refinement_prompt(refinement_type)
    workflow = self._initialize_refinement_workflow(provider_name=provider, model=model)
    
    await ctx.info(f"Prompt refinement and execution workflow started with refinement model: {workflow.model} . Waiting for the response from the LLM...")
    refined = workflow.refine_prompt(input_prompt=prompt, refinement_prompt=refinement_prompt)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return refined
  
  async def refine_and_execute_external_prompt(self, prompt: str, ctx: Context, provider: str, refinement_model: str, execution_model: str, refinement_type: str = 'default') -> str:
    """Refine a given prompt and execute it with an external LLM.
    
    Args:
        prompt (str): The input prompt to be refined and executed.
        ctx (Context): The MCP context object.
        provider (str): Name of the provider to use for LLM interactions.
        refinement_model (str): Model for refinement.
        execution_model (str): Model for execution.
        refinement_type (str, optional): Type of refinement ('code' or 'default'). Default is 'default'.
        
    Returns:
        str: The execution result of the refined prompt from the external LLM.
    """
    refinement_prompt = self.load_refinement_prompt(refinement_type)

    prov = self._get_provider(provider)
    refinement_model = self._get_model(provider=prov, model=refinement_model)
    execution_model = self._get_model(provider=prov, model=execution_model)

    workflow = self._initialize_refinement_workflow(provider_name=provider, model=execution_model)
    await ctx.info(f"Prompt refinement and execution workflow started with refinement model: {refinement_model} and execution model {execution_model} . Waiting for the responses from the LLMs...")
    result = workflow.refine_and_send_prompt(input_prompt=prompt, refinement_prompt=refinement_prompt, refinement_model=refinement_model, execution_model=execution_model)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result
  
  async def handover_prompt(self, prompt: str, ctx: Context, provider: str, model: str, temperature=0.7) -> str:
    """Hands over a prompt to an external LLM for processing.
    
    Args:
        prompt (str): The prompt to be executed externally.
        ctx (Context): The MCP context object.
        provider (str): Name of the provider to use for LLM interactions.
        model (str): Model name for execution.
        temperature (float, optional): Temperature to use for the external execution. Default is 0.7.
        
    Returns:
        str: The processed result from the external LLM.
    """
    refiner = PromptRefiner()
    
    prov = self._get_provider(provider)
    model = self._get_model(provider=prov, model=model)
    llm_api = LLMApi(api_endpoint=prov['api_endpoint'], api_key=prov['api_key'])

    result = llm_api.send(prompt,model=model, temperature=temperature)
    result = refiner.clean_response(result)
    
    await ctx.info(f"External Prompt execution workflow started with model: {model} . Waiting for the responses from the LLM...")
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result
  
  async def breakdown_task(self, task: str, ctx: Context, provider: str, model: str) -> str:
    """Breaks down a task into sub-tasks with complexity ratings.
    
    Args:
        task (str): The full task description to break down.
        ctx (Context): The MCP context object.
        provider (str): Name of the provider to use for LLM interactions.
        model (str): Model name for processing.
        
    Returns:
        str: A JSON string containing the list of sub-tasks with complexity ratings.
    """
    workflow = self._initialize_refinement_workflow(provider_name=provider, model=model)
    await ctx.info(f"Task break-down started with model: {workflow.model} . Waiting for the response from the LLM...")
    result = workflow.breakdown_task(task=task)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result
  
  async def generate_random_ideas(self, ctx: Context, provider: str, idea_count: int = 1, temperature: float = 0.7, model: str = None) -> str:
    """Generate random ideas on a random topic.
    
    Args:
        ctx (Context): The MCP context object.
        provider (str): Name of the provider to use for LLM interactions.
        idea_count (int, optional): Number of ideas to generate. Default is 1.
        temperature (float, optional): Temperature for idea generation. Default is 0.7.
        model (str, optional): Model name for generation. Default is 'default'.
        
    Returns:
        str: Generated ideas separated by ---.
    """
    prov = self._get_provider(provider)
    model = self._get_model(provider=prov, model=model)
    await ctx.info(f"Task `generate random ideas` started at provider: {prov['name']} with model: {model} , idea_count: {idea_count} and temperature: {temperature}. Waiting for the response from the LLM...")

    idea_generation_workflow = IdeaGenerationWorkflow(api_endpoint=prov['api_endpoint'],
      api_key=prov['api_key'],
      idea_count=idea_count,
      temperature=temperature,
      generator_llm_model=model,
      refinement_llm_model=model,
      execution_llm_model=model,
      topic_generation_llm_model=model
    )
    results = idea_generation_workflow.run()
    result_text = f"\n---\n".join(results)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result_text
  
  async def generate_ideas_on_topic(self, ctx: Context, topic: str, provider: str, model: str, idea_count: int = 1, temperature: float = 0.7) -> str:
    """Generate ideas on a specific topic.
    
    Args:
        ctx (Context): The MCP context object.
        topic (str): The topic to generate ideas for.
        provider (str): Name of the provider to use for LLM interactions.
        model (str): Model name for generation.
        idea_count (int, optional): Number of ideas to generate. Default is 1.
        temperature (float, optional): Temperature for idea generation. Default is 0.7.
        
    Returns:
        str: Generated ideas separated by ---.
    """
    prov = self._get_provider(provider)
    model = self._get_model(provider=prov, model=model)

    await ctx.info(f"Task `generate ideas on topic` started with topic: '{topic}' , model: {model} , idea_count: {idea_count} and temperature: {temperature}. Waiting for the response from the LLM...")
    idea_generation_workflow = IdeaGenerationWorkflow(api_endpoint=prov['api_endpoint'],
      api_key=prov['api_key'],
      topic=topic,
      idea_count=idea_count,
      temperature=temperature,
      generator_llm_model=model,
      refinement_llm_model=model,
      execution_llm_model=model,
      topic_generation_llm_model=model
    )
    results = idea_generation_workflow.run()
    result_text = f"\n---\n".join(results)
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result_text
  
  async def generate_code_review(self, ctx: Context, source_directory: str, source_file_paths: List[str], target_directory: str, provider: str, model:str, review_type:str):
    """Generate a code review in markdown format.
    
    Args:
        ctx (Context): The MCP context object.
        source_file_paths (list): List of source file paths to be reviewed.
        target_directory (str): Directory to store the resulting review files.
        provider (str): Name of the provider to use for LLM interactions.
        model (str): Model name for code review generation.
        review_type (str): Type of review ('style', 'security', 'performance', 'quality'). Default is 'quality'.
        
    Returns:
        str: Success message with path to generated files.
    """
    prov = self._get_provider(provider)
    model = self._get_model(provider=prov, model=model)

    await ctx.info(f"Generating code review of type: {review_type} - using model: {model} ...")
    run_code_review(file_paths=source_file_paths,
                    directory_path=source_directory,
                    output_dir=target_directory,
                    review_type=review_type,
                    api_endpoint=prov['api_endpoint'],
                    api_key=prov['api_key'],
                    model=model)
    # TODO: also include some basic info of the review results (e.g. the complete review file list)
    # so that the caller gains more information about the result and file locations
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return f"Successfully generated review files in {target_directory} ."
    
    
  async def list_available_providers(self, ctx: Context) -> str:
    """List all configured and available API providers.
    
    Args:
        ctx (Context): The MCP context object.
        
    Returns:
        str: Formatted list of configured providers.
    """
    providers = self.config.available_providers()
    result = "# Configured providers"
    for prov in providers:
      prov_string = f"-{prov['name']} : type: {prov['type']} - api_endpoint: {prov['api_endpoint']}"
      result = f"{result}\n{prov_string}"
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result

  async def list_available_models_for_provider(self, ctx: Context, provider_name: str = "") -> str:
    """List all available large language models for a specific provider.
    
    Args:
        ctx (Context): The MCP context object.
        provider_name (str, optional): Name of the provider to list models for. Default is empty (uses default).
        
    Returns:
        str: Formatted list of available models and API endpoint.
    """
    await ctx.info(f"Retrieving endpoint information and list of available models for configured provider {provider_name} ...")
    if not provider_name:
      provider = self.config.get_default_provider()
    else:
      provider = self.config.get_provider_by_name(provider_name)
    
    llm_api = LLMApi(api_endpoint=provider['api_endpoint'], api_key=provider['api_key'])
    models = llm_api.list_models()
    if not models:
      return "# No models available"

    api_headline = f"# Target API Endpoint\n{provider['api_endpoint']}\n"

    model_list = "\n".join([f"- {model}" for model in models])
    result = f"{api_headline}\n# List of available models\n{model_list}"
    await ctx.info(self.WORKFLOW_COMPLETION_MESSAGE)
    return result