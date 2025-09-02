import os
import json
import pytest
from unittest.mock import patch, mock_open, MagicMock
import sys
from io import StringIO
from pydantic import ValidationError

# Assuming the test file is structured to import from the production code module
from ara_cli.ara_config import (
    ensure_directory_exists,
    read_data,
    save_data,
    ARAconfig,
    ConfigManager,
    DEFAULT_CONFIG_LOCATION,
    LLMConfigItem,
    handle_unrecognized_keys,
)


@pytest.fixture
def default_config_data():
    """Provides the default configuration as a dictionary."""
    return ARAconfig().model_dump()


@pytest.fixture
def valid_config_dict():
    """A valid, non-default configuration dictionary for testing."""
    return {
        "ext_code_dirs": [{"source_dir": "./app"}],
        "glossary_dir": "./custom_glossary",
        "doc_dir": "./custom_docs",
        "local_prompt_templates_dir": "./custom_prompts",
        "custom_prompt_templates_subdir": "custom_subdir",
        "local_ara_templates_dir": "./custom_templates/",
        "ara_prompt_given_list_includes": ["*.py", "*.md", "*.json"],
        "llm_config": {
            "gpt-4o-custom": {
                "provider": "openai",
                "model": "openai/gpt-4o",
                "temperature": 0.5,
                "max_tokens": 4096
            }
        },
        "default_llm": "gpt-4o-custom"
    }


@pytest.fixture
def corrupted_config_dict():
    """A config dictionary with various type errors to test validation and fixing."""
    return {
        "ext_code_dirs": "should_be_a_list",
        "glossary_dir": 123,
        "llm_config": {
            "bad-model": {
                "provider": "test",
                "model": "test/model",
                "temperature": "not_a_float"
            }
        },
        "default_llm": 999
    }


@pytest.fixture(autouse=True)
def reset_config_manager():
    """Ensures a clean state for each test by resetting the singleton and caches."""
    ConfigManager.reset()
    yield
    ConfigManager.reset()

# --- Test Pydantic Models ---

class TestLLMConfigItem:
    def test_valid_temperature(self):
        """Tests that a valid temperature is accepted."""
        config = LLMConfigItem(provider="test", model="test/model", temperature=0.7)
        assert config.temperature == 0.7

    def test_invalid_temperature_too_high_raises_error(self):
        """Tests that temperature > 1.0 raises a ValidationError."""
        with pytest.raises(ValidationError, match="Input should be less than or equal to 1"):
            LLMConfigItem(provider="test", model="test/model", temperature=1.5)

    def test_invalid_temperature_too_low_raises_error(self):
        """Tests that temperature < 0.0 raises a ValidationError."""
        with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
            LLMConfigItem(provider="test", model="test/model", temperature=-0.5)


class TestARAconfig:
    def test_default_values_are_correct(self):
        """Tests that the model initializes with correct default values."""
        config = ARAconfig()
        assert config.ext_code_dirs == [{"source_dir": "./src"}, {"source_dir": "./tests"}]
        assert config.glossary_dir == "./glossary"
        assert config.default_llm == "gpt-5"
        assert "gpt-5" in config.llm_config

    @patch('sys.stdout', new_callable=StringIO)
    def test_check_critical_fields_with_empty_list_reverts_to_default(self, mock_stdout):
        """Tests that an empty list for a critical field is reverted to its default."""
        config = ARAconfig(ext_code_dirs=[])
        assert len(config.ext_code_dirs) == 2
        assert config.ext_code_dirs[0] == {"source_dir": "./src"}
        assert "Warning: Value for 'ext_code_dirs' is missing or empty. Using default." in mock_stdout.getvalue()

    @patch('sys.stdout', new_callable=StringIO)
    def test_check_critical_fields_with_empty_string_reverts_to_default(self, mock_stdout):
        """Tests that an empty string for a critical field is reverted to its default."""
        config = ARAconfig(glossary_dir="")
        assert config.glossary_dir == "./glossary"
        assert "Warning: Value for 'glossary_dir' is missing or empty. Using default." in mock_stdout.getvalue()

    @patch('sys.stdout', new_callable=StringIO)
    def test_validator_with_empty_llm_config(self, mock_stdout):
        """Tests validator when llm_config is empty, setting default and extraction to None."""
        config = ARAconfig(llm_config={})
        assert config.llm_config == {}
        assert config.default_llm is None
        assert config.extraction_llm is None
        assert "Warning: 'llm_config' is empty" in mock_stdout.getvalue()

    @patch('sys.stdout', new_callable=StringIO)
    def test_validator_with_invalid_default_llm(self, mock_stdout):
        """Tests that an invalid default_llm is reverted to the first available model."""
        config = ARAconfig(default_llm="non_existent_model")
        first_llm = next(iter(config.llm_config))
        assert config.default_llm == first_llm
        output = mock_stdout.getvalue()
        assert "Warning: The configured 'default_llm' ('non_existent_model') does not exist" in output
        assert f"-> Reverting to the first available model: '{first_llm}'" in output

    @patch('sys.stdout', new_callable=StringIO)
    def test_validator_with_invalid_extraction_llm(self, mock_stdout):
        """Tests that an invalid extraction_llm is reverted to the default_llm."""
        config = ARAconfig(default_llm="gpt-4o", extraction_llm="non_existent_model")
        assert config.extraction_llm == "gpt-4o"
        output = mock_stdout.getvalue()
        assert "Warning: The configured 'extraction_llm' ('non_existent_model') does not exist" in output
        assert "-> Reverting to the 'default_llm' value: 'gpt-4o'" in output

# --- Test Helper Functions ---

class TestEnsureDirectoryExists:
    @patch('sys.stdout', new_callable=StringIO)
    @patch("os.makedirs")
    @patch("ara_cli.ara_config.exists", return_value=False)
    def test_directory_creation_when_not_exists(self, mock_exists, mock_makedirs, mock_stdout):
        """Tests that a directory is created if it doesn't exist."""
        ensure_directory_exists.cache_clear()
        directory = "/tmp/new/dir"
        result = ensure_directory_exists(directory)
        
        mock_exists.assert_called_once_with(directory)
        mock_makedirs.assert_called_once_with(directory)
        assert result == directory
        assert f"New directory created at {directory}" in mock_stdout.getvalue()

    @patch("os.makedirs")
    @patch("ara_cli.ara_config.exists", return_value=True)
    def test_directory_no_creation_when_exists(self, mock_exists, mock_makedirs):
        """Tests that a directory is not created if it already exists."""
        ensure_directory_exists.cache_clear()
        directory = "/tmp/existing/dir"
        result = ensure_directory_exists(directory)
        
        mock_exists.assert_called_once_with(directory)
        mock_makedirs.assert_not_called()
        assert result == directory


class TestHandleUnrecognizedKeys:
    @patch('sys.stdout', new_callable=StringIO)
    def test_removes_unrecognized_keys_and_warns(self, mock_stdout):
        """Tests that unknown keys are removed and a warning is printed."""
        data = {"glossary_dir": "./glossary", "unknown_key": "some_value"}
        cleaned_data = handle_unrecognized_keys(data)
        
        assert "unknown_key" not in cleaned_data
        assert "glossary_dir" in cleaned_data
        assert "Warning: Unrecognized configuration key 'unknown_key' will be ignored." in mock_stdout.getvalue()

    @patch('sys.stdout', new_callable=StringIO)
    def test_no_action_for_valid_data(self, mock_stdout):
        """Tests that no changes are made when there are no unrecognized keys."""
        data = {"glossary_dir": "./glossary", "doc_dir": "./docs"}
        cleaned_data = handle_unrecognized_keys(data)
        
        assert cleaned_data == data
        assert mock_stdout.getvalue() == ""

# --- Test Core I/O and Logic ---

class TestSaveData:
    @patch("builtins.open", new_callable=mock_open)
    def test_save_data_writes_correct_json(self, mock_file, default_config_data):
        """Tests that the config is correctly serialized to a JSON file."""
        config = ARAconfig()
        save_data("config.json", config)

        mock_file.assert_called_once_with("config.json", "w", encoding="utf-8")
        handle = mock_file()
        written_data = ''.join(call.args[0] for call in handle.write.call_args_list)
        
        assert json.loads(written_data) == default_config_data


class TestReadData:
    @patch('sys.stdout', new_callable=StringIO)
    @patch('ara_cli.ara_config.save_data')
    @patch('ara_cli.ara_config.ensure_directory_exists')
    @patch('ara_cli.ara_config.exists', return_value=False)
    def test_file_not_found_creates_default_and_exits(self, mock_exists, mock_ensure_dir, mock_save, mock_stdout):
        """Tests that a default config is created and the program exits if no config file is found."""
        with pytest.raises(SystemExit) as exc_info:
            read_data.cache_clear()
            read_data("config.json")

        assert exc_info.value.code == 0
        mock_ensure_dir.assert_called_once_with(os.path.dirname("config.json"))
        mock_save.assert_called_once()
        
        output = mock_stdout.getvalue()
        assert "Configuration file not found. Creating a default one at 'config.json'." in output
        assert "Please review the default configuration and re-run your command." in output

    @patch('ara_cli.ara_config.save_data')
    @patch('builtins.open')
    @patch('ara_cli.ara_config.ensure_directory_exists')
    @patch('ara_cli.ara_config.exists', return_value=True)
    def test_valid_config_is_loaded_and_resaved(self, mock_exists, mock_ensure_dir, mock_open_func, mock_save, valid_config_dict):
        """Tests that a valid config is loaded correctly and re-saved (to clean it)."""
        m = mock_open(read_data=json.dumps(valid_config_dict))
        mock_open_func.return_value = m()
        read_data.cache_clear()

        result = read_data("config.json")

        assert isinstance(result, ARAconfig)
        assert result.default_llm == "gpt-4o-custom"
        mock_save.assert_called_once()

    @patch('sys.stdout', new_callable=StringIO)
    @patch('ara_cli.ara_config.save_data')
    @patch('builtins.open', new_callable=mock_open, read_data="this is not json")
    @patch('ara_cli.ara_config.ensure_directory_exists')
    @patch('ara_cli.ara_config.exists', return_value=True)
    def test_invalid_json_creates_default_config(self, mock_exists, mock_ensure_dir, mock_open_func, mock_save, mock_stdout):
        """Tests that a JSON decoding error results in a new default configuration."""
        read_data.cache_clear()
        
        result = read_data("config.json")
        
        assert isinstance(result, ARAconfig)
        assert result.default_llm == "gpt-5"  # Should be the default config
        
        output = mock_stdout.getvalue()
        assert "Error: Invalid JSON in configuration file" in output
        assert "Creating a new configuration with defaults..." in output
        mock_save.assert_called_once()

    @patch('sys.stdout', new_callable=StringIO)
    @patch('ara_cli.ara_config.save_data')
    @patch('builtins.open')
    @patch('ara_cli.ara_config.ensure_directory_exists')
    @patch('ara_cli.ara_config.exists', return_value=True)
    def test_config_with_validation_errors_is_fixed(self, mock_exists, mock_ensure_dir, mock_open_func, mock_save, mock_stdout, corrupted_config_dict):
        """Tests that a config with invalid fields is automatically corrected to defaults."""
        m = mock_open(read_data=json.dumps(corrupted_config_dict))
        mock_open_func.return_value = m()
        read_data.cache_clear()
        
        defaults = ARAconfig()
        result = read_data("config.json")

        assert isinstance(result, ARAconfig)
        assert result.ext_code_dirs == defaults.ext_code_dirs
        assert result.glossary_dir == defaults.glossary_dir
        assert result.llm_config == defaults.llm_config
        assert result.default_llm == defaults.default_llm

        output = mock_stdout.getvalue()
        assert "--- Configuration Error Detected ---" in output
        assert "-> Field 'ext_code_dirs' is invalid and will be reverted to its default value." in output
        assert "-> Field 'glossary_dir' is invalid and will be reverted to its default value." in output
        assert "-> Field 'llm_config' is invalid and will be reverted to its default value." in output
        assert "Configuration has been corrected and saved" in output
        
        mock_save.assert_called_once_with("config.json", result)

    @patch('sys.stdout', new_callable=StringIO)
    @patch('ara_cli.ara_config.save_data')
    @patch('builtins.open')
    @patch('ara_cli.ara_config.ensure_directory_exists')
    @patch('ara_cli.ara_config.exists', return_value=True)
    def test_preserves_valid_fields_when_fixing_errors(self, mock_exists, mock_ensure_dir, mock_open_func, mock_save, mock_stdout):
        """Tests that valid, non-default values are preserved during a fix."""
        mixed_config = {
            "glossary_dir": "./my-custom-glossary",  # Valid, non-default
            "default_llm": 12345,                    # Invalid type
            "unrecognized_key": "will_be_ignored"    # Unrecognized
        }
        m = mock_open(read_data=json.dumps(mixed_config))
        mock_open_func.return_value = m()
        read_data.cache_clear()
        
        defaults = ARAconfig()
        result = read_data("config.json")

        assert result.glossary_dir == "./my-custom-glossary"
        assert result.default_llm == defaults.default_llm

        output = mock_stdout.getvalue()
        assert "Warning: Unrecognized configuration key 'unrecognized_key' will be ignored." in output
        assert "-> Field 'default_llm' is invalid" in output
        assert "-> Field 'glossary_dir' is invalid" not in output

        mock_save.assert_called_once()
        saved_config = mock_save.call_args[0][1]
        assert saved_config.glossary_dir == "./my-custom-glossary"
        assert saved_config.default_llm == defaults.default_llm

# --- Test Singleton Manager ---

class TestConfigManager:
    @patch('ara_cli.ara_config.read_data')
    def test_get_config_is_singleton(self, mock_read):
        """Tests that get_config returns the same instance on subsequent calls."""
        mock_read.return_value = MagicMock(spec=ARAconfig)
        
        config1 = ConfigManager.get_config()
        config2 = ConfigManager.get_config()
        
        assert config1 is config2
        mock_read.assert_called_once()

    @patch('ara_cli.ara_config.read_data')
    def test_reset_clears_instance_and_caches(self, mock_read):
        """Tests that the reset method clears the instance and underlying caches."""
        mock_read.return_value = MagicMock(spec=ARAconfig)

        ConfigManager.get_config()
        mock_read.assert_called_once()
        
        ConfigManager.reset()
        assert ConfigManager._config_instance is None
        mock_read.cache_clear.assert_called_once()

        ConfigManager.get_config()
        assert mock_read.call_count == 2 # Called again after reset

    @patch('ara_cli.ara_config.read_data')
    def test_get_config_with_custom_filepath(self, mock_read):
        """Tests that get_config can be called with a custom file path."""
        mock_read.return_value = MagicMock(spec=ARAconfig)
        custom_path = "/custom/path/config.json"
        
        ConfigManager.get_config(custom_path)
        
        mock_read.assert_called_once_with(custom_path)