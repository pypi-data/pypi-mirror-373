import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from enhance_this.cli import main
from enhance_this import config

@pytest.fixture
def runner():
    return CliRunner()

@pytest.fixture(autouse=True)
def mock_ollama_client():
    with patch('enhance_this.ollama_client.OllamaClient') as MockOllamaClient:
        instance = MockOllamaClient.return_value
        instance.is_running.return_value = True
        instance.list_models.return_value = ["llama2"]
        instance.download_model.return_value = True
        instance.generate_stream.return_value = iter(["Enhanced ", "Prompt"])
        yield instance

@pytest.fixture(autouse=True)
def mock_clipboard():
    with patch('enhance_this.clipboard.copy_to_clipboard') as mock_copy:
        yield mock_copy

@pytest.fixture(autouse=True)
def mock_config_file(tmp_path):
    # Create a temporary config directory and file for testing
    test_config_dir = tmp_path / ".enhance-this"
    test_config_dir.mkdir()
    test_config_file = test_config_dir / "config.yaml"
    
    # Patch get_config_path to return our temporary path
    original_get_config_path = config.get_config_path
    config.get_config_path = lambda *args, **kwargs: test_config_file
    yield test_config_file
    config.get_config_path = original_get_config_path # Restore original

    # Ensure a default config is created for tests that don't explicitly create one
    config.create_default_config_if_not_exists()

def test_cli_version(runner):
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "enhance-this version" in result.output

def test_cli_help(runner):
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "Usage: enhance [OPTIONS] [PROMPT]" in result.output

def test_cli_no_prompt(runner):
    result = runner.invoke(main, [])
    assert result.exit_code == 0 # Help message is shown, not an error
    assert "Usage: enhance [OPTIONS] [PROMPT]" in result.output

def test_cli_ollama_not_running(runner, mock_ollama_client):
    mock_ollama_client.is_running.return_value = False
    result = runner.invoke(main, ["test prompt"])
    assert result.exit_code == 1
    assert "Ollama service is not running or is unreachable." in result.output

def test_cli_list_models(runner, mock_ollama_client):
    mock_ollama_client.list_models.return_value = ["model1", "model2"]
    result = runner.invoke(main, ["--list-models"])
    assert result.exit_code == 0
    assert "Available Ollama models:" in result.output
    assert "- model1" in result.output
    assert "- model2" in result.output

def test_cli_download_model(runner, mock_ollama_client):
    result = runner.invoke(main, ["--download-model", "new_model"])
    assert result.exit_code == 0
    mock_ollama_client.download_model.assert_called_once_with("new_model")
    assert "Starting download for 'new_model'..." in result.output

def test_cli_auto_setup_no_models(runner, mock_ollama_client):
    mock_ollama_client.list_models.return_value = []
    result = runner.invoke(main, ["--auto-setup"])
    assert result.exit_code == 0
    mock_ollama_client.download_model.assert_called_once_with("llama3.1:8b")
    assert "No models found. Starting auto-setup." in result.output

def test_cli_auto_setup_model_exists(runner, mock_ollama_client):
    mock_ollama_client.list_models.return_value = ["llama3.1:8b"]
    result = runner.invoke(main, ["--auto-setup"])
    assert result.exit_code == 0
    mock_ollama_client.download_model.assert_not_called()
    assert "Recommended model 'llama3.1:8b' is already available." in result.output

def test_cli_enhance_success(runner, mock_ollama_client, mock_clipboard):
    result = runner.invoke(main, ["my test prompt"])
    assert result.exit_code == 0
    assert "✨ Enhanced Prompt ✨" in result.output
    assert "Enhanced Prompt" in result.output # From the streamed output
    mock_ollama_client.generate_stream.assert_called_once()
    mock_clipboard.assert_called_once_with("Enhanced Prompt")

def test_cli_enhance_no_copy(runner, mock_ollama_client, mock_clipboard):
    result = runner.invoke(main, ["my test prompt", "-n"])
    assert result.exit_code == 0
    mock_clipboard.assert_not_called()

def test_cli_enhance_output_file(runner, mock_ollama_client, tmp_path):
    output_file = tmp_path / "output.txt"
    result = runner.invoke(main, ["my test prompt", "-o", str(output_file)])
    assert result.exit_code == 0
    assert f"Saved to {output_file.name}" in result.output
    assert output_file.read_text() == "Enhanced Prompt"

def test_cli_enhance_diff_view(runner, mock_ollama_client):
    mock_ollama_client.generate_stream.return_value = iter(["This is the ", "enhanced output."])
    result = runner.invoke(main, ["This is the original input.", "--diff"])
    assert result.exit_code == 0
    assert "↔️  Diff View ↔️" in result.output
    assert "- This is the original input." in result.output
    assert "+ This is the enhanced output." in result.output

def test_cli_enhance_verbose(runner, mock_ollama_client):
    result = runner.invoke(main, ["my test prompt", "-v"])
    assert result.exit_code == 0
    assert "System Prompt:" in result.output
    mock_ollama_client.generate_stream.assert_called_once()

def test_cli_enhance_specific_model_not_found(runner, mock_ollama_client):
    mock_ollama_client.list_models.return_value = ["model_a"]
    result = runner.invoke(main, ["prompt", "-m", "non_existent_model"])
    assert result.exit_code == 1
    assert "Model 'non_existent_model' not found." in result.output

def test_cli_enhance_no_models_available(runner, mock_ollama_client):
    mock_ollama_client.list_models.return_value = []
    mock_ollama_client.download_model.return_value = False # Simulate download failure
    result = runner.invoke(main, ["prompt"])
    assert result.exit_code == 1
    assert "No models available. Please download a model first" in result.output

def test_cli_enhance_custom_style(runner, mock_ollama_client, mock_config_file):
    # Create a custom template file
    custom_template_path = mock_config_file.parent / "custom_template.txt"
    custom_template_path.write_text("Custom template for: {user_prompt}")

    # Update the config file to include the custom template
    with open(mock_config_file, 'a') as f:
        f.write("\nenhancement_templates:\n  my_custom_style: " + str(custom_template_path) + "\n")

    result = runner.invoke(main, ["my prompt", "-s", "my_custom_style"])
    assert result.exit_code == 0
    # The enhancer will use the custom template, so the generated prompt will reflect that
    mock_ollama_client.generate_stream.assert_called_once()
    # We need to mock the enhancer's behavior to reflect the custom template
    # For now, we'll just check that the command ran successfully.
    assert "✨ Enhanced Prompt ✨" in result.output

