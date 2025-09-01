import pytest
from unittest.mock import patch, MagicMock
from enhance_this.ollama_client import OllamaClient
import requests
import json

@pytest.fixture
def mock_requests_session():
    with patch('requests.Session') as mock_session_class:
        mock_session_instance = MagicMock()
        mock_session_class.return_value = mock_session_instance
        yield mock_session_instance

@pytest.fixture
def ollama_client(mock_requests_session):
    return OllamaClient(host="http://localhost:11434", timeout=5)

def test_is_running_success(ollama_client, mock_requests_session):
    mock_requests_session.get.return_value.status_code = 200
    assert ollama_client.is_running()

def test_is_running_failure(ollama_client, mock_requests_session):
    mock_requests_session.get.side_effect = requests.RequestException
    assert not ollama_client.is_running()

def test_list_models_success(ollama_client, mock_requests_session):
    mock_response = MagicMock()
    mock_response.json.return_value = {"models": [{"name": "llama2"}, {"name": "mistral"}]}
    mock_requests_session.get.return_value = mock_response
    models = ollama_client.list_models()
    assert models == ["llama2", "mistral"]

def test_list_models_failure(ollama_client, mock_requests_session):
    mock_requests_session.get.side_effect = requests.RequestException
    models = ollama_client.list_models()
    assert models == []

def test_download_model_success(ollama_client, mock_requests_session):
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = [
        json.dumps({"status": "downloading", "total": 100, "completed": 50}).encode(),
        json.dumps({"status": "success", "total": 100, "completed": 100}).encode(),
    ]
    mock_requests_session.post.return_value = mock_response
    assert ollama_client.download_model("llama2")

def test_download_model_failure(ollama_client, mock_requests_session):
    mock_requests_session.post.side_effect = requests.RequestException
    assert not ollama_client.download_model("llama2")

def test_generate_stream_success(ollama_client, mock_requests_session):
    mock_response = MagicMock()
    mock_response.iter_lines.return_value = [
        json.dumps({"response": "Hello "}).encode(),
        json.dumps({"response": "World!", "done": True}).encode(),
    ]
    mock_requests_session.post.return_value = mock_response
    
    chunks = list(ollama_client.generate_stream("llama2", "prompt", 0.7, 200))
    assert chunks == ["Hello ", "World!"]

def test_generate_stream_timeout(ollama_client, mock_requests_session):
    mock_requests_session.post.side_effect = requests.exceptions.Timeout
    chunks = list(ollama_client.generate_stream("llama2", "prompt", 0.7, 200))
    assert chunks == []

def test_generate_stream_request_exception(ollama_client, mock_requests_session):
    mock_requests_session.post.side_effect = requests.RequestException
    chunks = list(ollama_client.generate_stream("llama2", "prompt", 0.7, 200))
    assert chunks == []

# Integration Test (requires Ollama running with llama2 model)
@pytest.mark.skip(reason="Integration test: requires Ollama running with llama2 model")
def test_integration_generate_stream_live():
    client = OllamaClient(host="http://localhost:11434", timeout=60) # Increased timeout for live test
    if not client.is_running():
        pytest.skip("Ollama is not running.")
    
    # Ensure llama2 is available, or download it
    if "llama2" not in client.list_models():
        print("\nllama2 model not found, attempting to download...")
        if not client.download_model("llama2"):
            pytest.fail("Failed to download llama2 model for integration test.")

    prompt = "Say hello world"
    full_response = "".join(list(client.generate_stream("llama2", prompt, 0.7, 50)))
    assert "hello world" in full_response.lower()
