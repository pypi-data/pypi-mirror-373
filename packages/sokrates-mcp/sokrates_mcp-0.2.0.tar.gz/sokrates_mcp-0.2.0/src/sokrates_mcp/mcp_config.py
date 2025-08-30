# MCP Configuration Module
#
# This module provides configuration management for the MCP server.
# It loads configuration from a YAML file and sets default values if needed.
#
# Parameters:
# - config_file_path: Path to the YAML configuration file (default: ~/.sokrates-mcp/config.yml)
# - api_endpoint: API endpoint URL (default: http://localhost:1234/v1)
# - api_key: API key for authentication (default: mykey)
# - model: Model name to use (default: qwen/qwen3-4b-2507)
# - verbose: Enable verbose logging (default: False)
#
# Usage example:
#   config = MCPConfig(api_endpoint="https://api.example.com", model="my-model")
import os
import yaml
import logging
from urllib.parse import urlparse
from pathlib import Path
from sokrates import Config

DEFAULT_API_ENDPOINT = "http://localhost:1234/v1"
DEFAULT_API_KEY = "mykey"
DEFAULT_MODEL = "qwen/qwen3-4b-2507"
DEFAULT_PROVIDER_NAME = "default"
DEFAULT_PROVIDER_TYPE = "openai"
DEFAULT_PROVIDER_CONFIGURATION = {
                    "name": DEFAULT_PROVIDER_NAME,
                    "type": DEFAULT_PROVIDER_TYPE,
                    "api_endpoint": DEFAULT_API_ENDPOINT,
                    "api_key": DEFAULT_API_KEY,
                    "default_model": DEFAULT_MODEL
                }

class MCPConfig:
    """Configuration management class for MCP server.

    This class handles loading configuration from a YAML file and provides
    default values for various parameters.

    Attributes:
        CONFIG_FILE_PATH (str): Default path to the configuration file
        DEFAULT_PROMPTS_DIRECTORY (str): Default directory for prompts
        DEFAULT_REFINEMENT_PROMPT_FILENAME (str): Default refinement prompt filename
        DEFAULT_REFINEMENT_CODING_PROMPT_FILENAME (str): Default refinement coding prompt filename
        PROVIDER_TYPES (list): List of supported provider types
    """
    CONFIG_FILE_PATH = os.path.expanduser("~/.sokrates-mcp/config.yml")
    DEFAULT_PROMPTS_DIRECTORY = Config().prompts_directory
    DEFAULT_REFINEMENT_PROMPT_FILENAME = "refine-prompt.md"
    DEFAULT_REFINEMENT_CODING_PROMPT_FILENAME = "refine-coding-v3.md"
    PROVIDER_TYPES = [
        "openai"
    ]
    
    def __init__(self, config_file_path=CONFIG_FILE_PATH, api_endpoint = DEFAULT_API_ENDPOINT, api_key = DEFAULT_API_KEY, model= DEFAULT_MODEL, verbose=False):
        """Initialize MCP configuration.

        Args:
            config_file_path (str): Path to the YAML configuration file.
                                   Defaults to CONFIG_FILE_PATH.
            api_endpoint (str): API endpoint URL. Defaults to DEFAULT_API_ENDPOINT.
            api_key (str): API key for authentication. Defaults to DEFAULT_API_KEY.
            model (str): Model name to use. Defaults to DEFAULT_MODEL.
            verbose (bool): Enable verbose logging. Defaults to False.

        Returns:
            None

        Side Effects:
            Initializes instance attributes with values from config file or defaults
            Sets up logging based on verbose parameter
        """
        self.logger = logging.getLogger(__name__)
        self.config_file_path = config_file_path
        config_data = self._load_config_from_file(self.config_file_path)

        prompts_directory = config_data.get("prompts_directory", self.DEFAULT_PROMPTS_DIRECTORY)
        if not self._ensure_directory_exists(prompts_directory):
            raise ValueError(f"Invalid prompts directory: {prompts_directory}")
        self.prompts_directory = prompts_directory

        refinement_prompt_filename = config_data.get("refinement_prompt_filename", self.DEFAULT_REFINEMENT_PROMPT_FILENAME)
        if not os.path.exists(os.path.join(prompts_directory, refinement_prompt_filename)):
            raise FileNotFoundError(f"Refinement prompt file not found: {refinement_prompt_filename}")
        self.refinement_prompt_filename = refinement_prompt_filename

        refinement_coding_prompt_filename = config_data.get("refinement_coding_prompt_filename", self.DEFAULT_REFINEMENT_CODING_PROMPT_FILENAME)
        if not os.path.exists(os.path.join(prompts_directory, refinement_coding_prompt_filename)):
            raise FileNotFoundError(f"Refinement coding prompt file not found: {refinement_coding_prompt_filename}")
        self.refinement_coding_prompt_filename = refinement_coding_prompt_filename
    

        self._configure_providers(config_data=config_data)
        self.logger.info(f"Configuration loaded from {self.config_file_path}:")
        self.logger.info(f"  Prompts Directory: {self.prompts_directory}")
        self.logger.info(f"  Refinement Prompt Filename: {self.refinement_prompt_filename}")
        self.logger.info(f"  Refinement Coding Prompt Filename: {self.refinement_coding_prompt_filename}")
        self.logger.info(f"  Default Provider: {self.default_provider}")
        for prov in self.providers:
            self.logger.info(f"Configured provider name: {prov["name"]} , api_endpoint: {prov["api_endpoint"]} , default_model: {prov["default_model"]}")

    def available_providers(self):
        return list(map(lambda prov: {'name': prov['name'], 'api_endpoint': prov['api_endpoint'], 'type': prov['type']}, self.providers))

    def get_provider_by_name(self, provider_name):
        providers = list(filter(lambda x: x['name'] == provider_name, self.providers))
        return providers[0]

    def get_default_provider(self):
        return self.get_provider_by_name(self.default_provider)

    def _configure_providers(self, config_data):
        # configure defaults if not config_data could be loaded
        self.providers = config_data.get("providers", {})
        if len(self.providers) < 1:
            self.providers = [
                DEFAULT_PROVIDER_CONFIGURATION
            ]
            self.default_provider = DEFAULT_PROVIDER_NAME
            return
        
        provider_names = []
        for provider in self.providers:
            if provider.get("name") in provider_names:
                raise ValueError("Duplicate provider names in the config providers section")
            self._validate_provider(provider)
            provider_names.append(provider['name'])

        if not config_data['default_provider']:
            raise ValueError(f"No default_provider was configured at the root level of the config file in {self.config_file_path}")
        self.default_provider = config_data['default_provider']

    def _validate_provider(self, provider):
        self._validate_provider_name(provider.get("name", ""))
        self._validate_provider_type(provider.get("type", ""))
        self._validate_url(provider.get("api_endpoint", ""))
        self._validate_api_key(provider.get("api_key", ""))
        self._validate_model_name(provider.get("default_model", ""))

    def _validate_provider_name(self, provider_name):
        if len(provider_name) < 1:
            raise ValueError(f"The provider name: {provider_name} is not a valid provider name")

    def _validate_provider_type(self, provider_type):
        if not provider_type in self.PROVIDER_TYPES:
            raise ValueError(f"The provider type: {provider_type} is not supported by sokrates-mcp")

    def _validate_url(self, url):
        """Validate URL format.

        Args:
            url (str): URL to validate

        Returns:
            bool: True if valid URL, False otherwise
        """
        try:
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except:
            raise ValueError(f"The api_endpoint: {url} is not a valid llm API endpoint")

    def _validate_api_key(self, api_key):
        """Validate API key format.

        Args:
            api_key (str): API key to validate

        Returns:
            bool: True if valid API key, False otherwise
        """
        if len(api_key) < 1:
            raise ValueError("The api key is empty")

    def _validate_model_name(self, model):
        """Validate model name format.

        Args:
            model (str): Model name to validate

        Returns:
            bool: True if valid model name, False otherwise
        """
        if len(model) < 1:
            raise ValueError("The model is empty")

    def _ensure_directory_exists(self, directory_path):
        """Ensure directory exists and is valid.

        Args:
            directory_path (str): Directory path to check/validate

        Returns:
            bool: True if directory exists or was created successfully, False otherwise
        """
        try:
            path = Path(directory_path)
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
            return path.is_dir()
        except Exception as e:
            self.logger.error(f"Error ensuring directory exists: {e}")
            return False

    def _load_config_from_file(self, config_file_path):
        """Load configuration data from a YAML file.

        Args:
            config_file_path (str): Path to the YAML configuration file

        Returns:
            dict: Parsed configuration data or empty dict if file doesn't exist
                  or cannot be parsed

        Side Effects:
            Logs error messages if file reading or parsing fails
        """
        try:
            # Ensure config directory exists
            Path(config_file_path).parent.mkdir(parents=True, exist_ok=True)

            if os.path.exists(config_file_path):
                with open(config_file_path, 'r') as f:
                    return yaml.safe_load(f) or {}
            else:
                self.logger.warning(f"Config file not found at {config_file_path}. Using defaults.")
                # Create empty config file
                with open(config_file_path, 'w') as f:
                    yaml.dump({}, f)
                return {}
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML config file {config_file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Error reading config file {config_file_path}: {e}")
        return {}