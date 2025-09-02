from typing import List, Dict, Optional, Any
from pydantic import BaseModel, ValidationError, Field, model_validator
import json
import os
from os.path import exists, dirname
from os import makedirs
from functools import lru_cache
import sys
import warnings

DEFAULT_CONFIG_LOCATION = "./ara/.araconfig/ara_config.json"

class LLMConfigItem(BaseModel):
    provider: str
    model: str
    temperature: float = Field(ge=0.0, le=1.0)
    max_tokens: Optional[int] = None
    max_completion_tokens: Optional[int] = None

class ARAconfig(BaseModel):
    ext_code_dirs: List[Dict[str, str]] = Field(default_factory=lambda: [
        {"source_dir": "./src"},
        {"source_dir": "./tests"}
    ])
    global_dirs: Optional[List[Dict[str, str]]] = Field(default=[])
    glossary_dir: str = "./glossary"
    doc_dir: str = "./docs"
    local_prompt_templates_dir: str = "./ara/.araconfig"
    custom_prompt_templates_subdir: Optional[str] = "custom-prompt-modules"
    local_ara_templates_dir: str = "./ara/.araconfig/templates/"
    ara_prompt_given_list_includes: List[str] = Field(default_factory=lambda: [
        "*.businessgoal",
        "*.vision",
        "*.capability",
        "*.keyfeature",
        "*.epic",
        "*.userstory",
        "*.example",
        "*.feature",
        "*.task",
        "*.py",
        "*.md",
        "*.png",
        "*.jpg",
        "*.jpeg",
    ])
    llm_config: Dict[str, LLMConfigItem] = Field(default_factory=lambda: {
        "gpt-5": LLMConfigItem(
            provider="openai",
            model="openai/gpt-5",
            temperature=1,
            max_completion_tokens=16000
        ),
        "gpt-5-mini": LLMConfigItem(
            provider="openai",
            model="openai/gpt-5-mini-2025-08-07",
            temperature=1
        ),
        "gpt-4o": LLMConfigItem(
            provider="openai",
            model="openai/gpt-4o",
            temperature=0.8,
            max_tokens=16000
        ),
        "gpt-4.1": LLMConfigItem(
            provider="openai",
            model="openai/gpt-4.1",
            temperature=0.8,
            max_tokens=16000
        ),
        "o3-mini": LLMConfigItem(
            provider="openai",
            model="openai/o3-mini",
            temperature=1.0,
            max_tokens=8000
        ),
        "opus-4": LLMConfigItem(
            provider="anthropic",
            model="anthropic/claude-opus-4-20250514",
            temperature=0.5,
            max_tokens=32000
        ),
        "sonnet-4": LLMConfigItem(
            provider="anthropic",
            model="anthropic/claude-sonnet-4-20250514",
            temperature=0.5,
            max_tokens=32000
        ),
        "together-ai-llama-2": LLMConfigItem(
            provider="together_ai",
            model="together_ai/togethercomputer/llama-2-70b",
            temperature=0.8,
            max_tokens=4000
        ),
        "groq-llama-3": LLMConfigItem(
            provider="groq",
            model="groq/llama3-70b-8192",
            temperature=0.8,
            max_tokens=4000
        )
    })
    default_llm: Optional[str] = None
    extraction_llm: Optional[str] = None

    @model_validator(mode='after')
    def check_critical_fields(self) -> 'ARAconfig':
        """Check for empty critical fields and validate default_llm and extraction_llm."""
        critical_fields = {
            'ext_code_dirs': [{"source_dir": "./src"}, {"source_dir": "./tests"}],
            'local_ara_templates_dir': "./ara/.araconfig/templates/",
            'local_prompt_templates_dir': "./ara/.araconfig",
            'glossary_dir': "./glossary"
        }

        for field, default_value in critical_fields.items():
            current_value = getattr(self, field)
            if not current_value:
                print(f"Warning: Value for '{field}' is missing or empty. Using default.")
                setattr(self, field, default_value)
        
        if not self.llm_config:
            print("Warning: 'llm_config' is empty. 'default_llm' and 'extraction_llm' cannot be set.")
            self.default_llm = None
            self.extraction_llm = None
            return self

        first_available_llm = next(iter(self.llm_config))

        if not self.default_llm:
            print(f"Warning: 'default_llm' is not set. Defaulting to the first available model: '{first_available_llm}'.")
            self.default_llm = first_available_llm
        elif self.default_llm not in self.llm_config:
            print(f"Warning: The configured 'default_llm' ('{self.default_llm}') does not exist in 'llm_config'.")
            print(f"-> Reverting to the first available model: '{first_available_llm}'.")
            self.default_llm = first_available_llm

        if not self.extraction_llm:
            print(f"Warning: 'extraction_llm' is not set. Setting it to the same as 'default_llm': '{self.default_llm}'.")
            self.extraction_llm = self.default_llm
        elif self.extraction_llm not in self.llm_config:
            print(f"Warning: The configured 'extraction_llm' ('{self.extraction_llm}') does not exist in 'llm_config'.")
            print(f"-> Reverting to the 'default_llm' value: '{self.default_llm}'.")
            self.extraction_llm = self.default_llm
            
        return self

# Function to ensure the necessary directories exist
@lru_cache(maxsize=None)
def ensure_directory_exists(directory: str):
    """Creates a directory if it doesn't exist."""
    if not exists(directory):
        os.makedirs(directory)
        print(f"New directory created at {directory}")
    return directory

def handle_unrecognized_keys(data: dict) -> dict:
    """Removes unrecognized keys from the data and warns the user."""
    known_fields = set(ARAconfig.model_fields.keys())
    cleaned_data = {}
    for key, value in data.items():
        if key not in known_fields:
            print(f"Warning: Unrecognized configuration key '{key}' will be ignored.")
        else:
            cleaned_data[key] = value
    return cleaned_data


# Function to read the JSON file and return an ARAconfig model
@lru_cache(maxsize=1)
def read_data(filepath: str) -> ARAconfig:
    """
    Reads, validates, and repairs the configuration file.
    If the file doesn't exist, it creates a default one.
    If the file is invalid, it corrects only the broken parts.
    """

    def warn_on_duplicate_llm_dict_key(ordered_pairs):
        """Reject duplicate keys."""
        d = {}
        for k, v in ordered_pairs:
            if k in d:
                warnings.warn(f"Duplicate LLM configuration identifier '{k}'. The previous entry will be removed.", UserWarning)
            d[k] = v
        return d

    ensure_directory_exists(dirname(filepath))

    if not exists(filepath):
        print(f"Configuration file not found. Creating a default one at '{filepath}'.")
        default_config = ARAconfig()
        save_data(filepath, default_config)
        print("Please review the default configuration and re-run your command.")
        sys.exit(0)

    try:
        with open(filepath, "r", encoding="utf-8") as file:
            content = file.read()
            data = json.loads(content, object_pairs_hook=warn_on_duplicate_llm_dict_key)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in configuration file: {e}")
        print("Creating a new configuration with defaults...")
        default_config = ARAconfig()
        save_data(filepath, default_config)
        return default_config

    data = handle_unrecognized_keys(data)

    try:
        config = ARAconfig(**data)
        save_data(filepath, config)
        return config
    except ValidationError as e:
        print("--- Configuration Error Detected ---")
        print("Some settings in your configuration file are invalid. Attempting to fix them.")
        
        corrected_data = data.copy()
        defaults = ARAconfig().model_dump()
        
        error_fields = {err['loc'][0] for err in e.errors() if err['loc']}
        
        for field_name in error_fields:
            print(f"-> Field '{field_name}' is invalid and will be reverted to its default value.")
            if field_name in corrected_data:
                corrected_data[field_name] = defaults.get(field_name)

        print("--- End of Error Report ---")

        final_config = ARAconfig(**corrected_data)
        save_data(filepath, final_config)
        print(f"Configuration has been corrected and saved to '{filepath}'.")
        
        return final_config

# Function to save the modified configuration back to the JSON file
def save_data(filepath: str, config: ARAconfig):
    """Saves the Pydantic config model to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(config.model_dump(), file, indent=4)

# Singleton for configuration management
class ConfigManager:
    _config_instance = None

    @classmethod
    def get_config(cls, filepath=DEFAULT_CONFIG_LOCATION) -> ARAconfig:
        if cls._config_instance is None:
            cls._config_instance = read_data(filepath)
        return cls._config_instance
    
    @classmethod
    def reset(cls):
        """Reset the configuration instance (useful for testing)."""
        cls._config_instance = None
        read_data.cache_clear()