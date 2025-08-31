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
from typing import Dict, List, Optional, Any

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
    
    def __init__(self, config_file_path: str = CONFIG_FILE_PATH, api_endpoint: str = DEFAULT_API_ENDPOINT, api_key: str = DEFAULT_API_KEY, model: str = DEFAULT_MODEL, verbose: bool = False):
        """Initialize MCP configuration.

        Args:
            config_file_path (str): Path to the YAML configuration file.
                                   Defaults to CONFIG_FILE_PATH.
            api_endpoint (str): API endpoint URL. Defaults to DEFAULT_API_ENDPOINT.
            api_key (str): API key for authentication. Defaults to DEFAULT_API_KEY.
            model (str): Model name to use. Defaults to DEFAULT_MODEL.
            verbose (bool): Enable verbose logging. Defaults to False.

        Side Effects:
            Initializes instance attributes with values from config file or defaults
            Sets up logging based on verbose parameter
        """
        self.logger = logging.getLogger(__name__)
        self.config_file_path = config_file_path
        # Validate config file path
        if not self._validate_config_file_path(config_file_path):
            raise ValueError(f"Invalid config file path: {config_file_path}")
        config_data = self._load_config_from_file(self.config_file_path)

        prompts_directory = config_data.get("prompts_directory", self.DEFAULT_PROMPTS_DIRECTORY)
        if not self._ensure_directory_exists(prompts_directory):
            raise ValueError(f"Invalid prompts directory: {prompts_directory}")
        self.prompts_directory = prompts_directory

        # Validate prompt files using helper method
        refinement_prompt_filename = config_data.get("refinement_prompt_filename", self.DEFAULT_REFINEMENT_PROMPT_FILENAME)
        self._validate_prompt_file_exists(prompts_directory, refinement_prompt_filename)
        self.refinement_prompt_filename = refinement_prompt_filename

        refinement_coding_prompt_filename = config_data.get("refinement_coding_prompt_filename", self.DEFAULT_REFINEMENT_CODING_PROMPT_FILENAME)
        self._validate_prompt_file_exists(prompts_directory, refinement_coding_prompt_filename)
        self.refinement_coding_prompt_filename = refinement_coding_prompt_filename
    

        self._configure_providers(config_data=config_data)
        self.logger.info(f"Configuration loaded from {self.config_file_path}:")
        self.logger.info(f"  Prompts Directory: {self.prompts_directory}")
        self.logger.info(f"  Refinement Prompt Filename: {self.refinement_prompt_filename}")
        self.logger.info(f"  Refinement Coding Prompt Filename: {self.refinement_coding_prompt_filename}")
        self.logger.info(f"  Default Provider: {self.default_provider}")
        for prov in self.providers:
            self.logger.info(f"Configured provider name: {prov['name']} , api_endpoint: {prov['api_endpoint']} , default_model: {prov['default_model']}")

    def _validate_prompt_file_exists(self, prompts_directory: str, filename: str) -> None:
        """Validate that a prompt file exists in the specified directory.
        
        Args:
            prompts_directory (str): Directory where prompt files are located
            filename (str): Name of the prompt file to check
            
        Raises:
            FileNotFoundError: If the prompt file does not exist
        """
        if not os.path.exists(os.path.join(prompts_directory, filename)):
            raise FileNotFoundError(f"Prompt file not found: {filename}")

    def _validate_config_file_path(self, config_file_path: str) -> bool:
        """Validate that the configuration file path is valid and accessible.
        
        Args:
            config_file_path (str): Path to the configuration file
            
        Returns:
            bool: True if path is valid and accessible, False otherwise
        """
        try:
            # Check if we can write to the directory
            dir_path = os.path.dirname(config_file_path) or "."
            if not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            # Test that we can actually access the file path
            Path(config_file_path).touch(exist_ok=True)
            return True
        except (OSError, IOError):
            return False

    def available_providers(self) -> List[Dict[str, Any]]:
        return [{'name': p['name'], 'api_endpoint': p['api_endpoint'], 'type': p['type']} for p in self.providers]

    def get_provider_by_name(self, provider_name: str) -> Dict[str, Any]:
        """Get a provider by its name.
        
        Args:
            provider_name (str): Name of the provider to find
            
        Returns:
            dict: Provider configuration dictionary
            
        Raises:
            IndexError: If no provider with the given name is found
        """
        for provider in self.providers:
            if provider['name'] == provider_name:
                return provider
        raise IndexError(f"Provider '{provider_name}' not found")

    def get_default_provider(self) -> Dict[str, Any]:
        return self.get_provider_by_name(self.default_provider)

    def _configure_providers(self, config_data: Dict[str, Any]) -> None:
        # configure defaults if not config_data could be loaded
        providers = config_data.get("providers", [])
        if not isinstance(providers, list):
            raise ValueError("'providers' must be a list in the configuration file")
        self.providers = providers
        if len(self.providers) < 1:
            # Validate defaults before use
            self._validate_provider(DEFAULT_PROVIDER_CONFIGURATION)
            self.providers = [DEFAULT_PROVIDER_CONFIGURATION]
            self.default_provider = DEFAULT_PROVIDER_NAME
            return
        
        provider_names = []
        for provider in self.providers:
            if provider.get("name") in provider_names:
                raise ValueError("Duplicate provider names in the config providers section")
            self._validate_provider(provider)
            provider_names.append(provider['name'])

        if not config_data.get('default_provider'):
            raise ValueError(f"No default_provider was configured at the root level of the config file in {self.config_file_path}")
        self.default_provider = config_data['default_provider']

    def _validate_provider(self, provider: Dict[str, Any]) -> None:
        self._validate_provider_name(provider.get("name", ""))
        self._validate_provider_type(provider.get("type", ""))
        self._validate_url(provider.get("api_endpoint", ""))
        self._validate_api_key(provider.get("api_key", ""))
        self._validate_model_name(provider.get("default_model", ""))

    def _validate_provider_name(self, provider_name: str) -> None:
        if len(provider_name) < 1:
            raise ValueError(f"The provider name: {provider_name} is not a valid provider name")

    def _validate_provider_type(self, provider_type: str) -> None:
        if not provider_type in self.PROVIDER_TYPES:
            raise ValueError(f"The provider type: {provider_type} is not supported by sokrates-mcp")

    def _validate_url(self, url: str) -> None:
        """Validate URL format.

        Args:
            url (str): URL to validate

        Raises:
            ValueError: If the URL is invalid
        """
        try:
            result = urlparse(url)
            if not (result.scheme in ['http', 'https'] and result.netloc):
                raise ValueError(f"Invalid API endpoint: {url}")
        except Exception as e:
            raise ValueError(f"Invalid API endpoint format: {url}") from e

    def _validate_api_key(self, api_key: str) -> None:
        """Validate API key format.

        Args:
            api_key (str): API key to validate

        Returns:
            bool: True if valid API key, False otherwise
        """
        if len(api_key) < 1:
            raise ValueError("The api key is empty")

    def _validate_model_name(self, model: str) -> None:
        """Validate model name format.

        Args:
            model (str): Model name to validate

        Returns:
            bool: True if valid model name, False otherwise
        """
        if len(model) < 1:
            raise ValueError("The model is empty")

    def _ensure_directory_exists(self, directory_path: str) -> bool:
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

    def _load_config_from_file(self, config_file_path: str) -> Dict[str, Any]:
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
                self.logger.warning(f"Config file not found at {config_file_path}. Using defaults (no config created).")
                return {}
        except yaml.YAMLError as e:
            self.logger.error(f"Error parsing YAML config file {config_file_path}: {e}")
        except OSError as e:
            self.logger.error(f"OS error reading config file {config_file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error reading config file {config_file_path}: {e}")
        return {}