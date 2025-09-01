import pytest
import os
import yaml
from pathlib import Path
from enhance_this import config

@pytest.fixture
def mock_config_path(tmp_path):
    # Create a temporary config directory and file for testing
    test_config_dir = tmp_path / ".enhance-this"
    test_config_dir.mkdir()
    test_config_file = test_config_dir / "config.yaml"
    
    # Patch get_config_path to return our temporary path
    original_get_config_path = config.get_config_path
    config.get_config_path = lambda *args, **kwargs: test_config_file
    yield test_config_file
    config.get_config_path = original_get_config_path # Restore original

def test_create_default_config_if_not_exists(mock_config_path):
    # Ensure config file does not exist initially
    assert not mock_config_path.exists()

    config.create_default_config_if_not_exists()
    assert mock_config_path.exists()

    loaded_config = yaml.safe_load(mock_config_path.read_text())
    assert loaded_config["default_temperature"] == 0.7
    assert "my_style" in loaded_config["enhancement_templates"]

def test_load_config_default(mock_config_path):
    # No config file exists, should load default config
    loaded_config = config.load_config()
    assert loaded_config["default_temperature"] == 0.7
    assert loaded_config["ollama_host"] == "http://localhost:11434"
    assert loaded_config["enhancement_templates"] == {}

def test_load_config_with_existing_file(mock_config_path):
    # Create a custom config file
    custom_settings = {
        "default_temperature": 0.9,
        "ollama_host": "http://my-ollama:11434",
        "new_setting": "value",
        "enhancement_templates": {"custom": "/tmp/custom.txt"}
    }
    mock_config_path.write_text(yaml.dump(custom_settings))

    loaded_config = config.load_config()
    assert loaded_config["default_temperature"] == 0.9
    assert loaded_config["ollama_host"] == "http://my-ollama:11434"
    assert loaded_config["new_setting"] == "value"
    assert loaded_config["enhancement_templates"] == {"custom": "/tmp/custom.txt"}

def test_load_config_with_invalid_file(mock_config_path):
    # Create an invalid config file
    mock_config_path.write_text("invalid yaml: - ")

    loaded_config = config.load_config()
    # Should fall back to default config
    assert loaded_config["default_temperature"] == 0.7
    assert loaded_config["ollama_host"] == "http://localhost:11434"
