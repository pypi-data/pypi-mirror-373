import pytest
from unittest.mock import patch, mock_open
from enhance_this.enhancer import PromptEnhancer, load_templates
from pathlib import Path

# Mock importlib.resources.files for Python 3.9+
@pytest.fixture
def mock_importlib_resources_files():
    with patch('importlib.resources.files') as mock_files:
        # Create a mock directory structure
        mock_template_dir = {
            'detailed.txt': 'Detailed template: {user_prompt}',
            'concise.txt': 'Concise template: {user_prompt}',
            'creative.txt': 'Creative template: {user_prompt}',
            'technical.txt': 'Technical template: {user_prompt}',
        }

        def mock_path_object(name):
            mock_path = Path(name) # Use a real Path object for some methods
            mock_path.is_file = lambda: name in mock_template_dir
            mock_path.read_text = lambda encoding='utf-8': mock_template_dir[name]
            return mock_path

        mock_files.return_value = type('MockPath', (object,), {
            '__truediv__': lambda self, name: mock_path_object(name),
            'is_file': lambda: True, # For the directory itself
        })()
        yield

# Mock importlib.resources.open_text for Python 3.8
@pytest.fixture
def mock_importlib_resources_open_text():
    with patch('importlib.resources.open_text') as mock_open_text:
        def _mock_open_text(package, filename):
            content = {
                'detailed.txt': 'Detailed template: {user_prompt}',
                'concise.txt': 'Concise template: {user_prompt}',
                'creative.txt': 'Creative template: {user_prompt}',
                'technical.txt': 'Technical template: {user_prompt}',
            }.get(filename)
            if content is None:
                raise FileNotFoundError
            mock_file = mock_open(read_data=content)()
            return mock_file
        mock_open_text.side_effect = _mock_open_text
        yield

@pytest.fixture(autouse=True)
def mock_template_loading(mock_importlib_resources_files, mock_importlib_resources_open_text):
    # This fixture ensures that template loading is mocked for all tests in this module
    pass

def test_load_templates_builtin():
    templates = load_templates()
    assert "detailed" in templates
    assert "concise" in templates
    assert "creative" in templates
    assert "technical" in templates
    assert templates["detailed"] == "Detailed template: {user_prompt}"

def test_load_templates_with_custom_templates(tmp_path):
    custom_template_file = tmp_path / "my_custom_template.txt"
    custom_template_file.write_text("My custom template: {user_prompt}")

    custom_template_paths = {
        "custom_style": str(custom_template_file),
        "detailed": str(custom_template_file), # Override built-in
        "non_existent": str(tmp_path / "non_existent.txt") # Non-existent path
    }

    templates = load_templates(custom_template_paths)
    assert "custom_style" in templates
    assert templates["custom_style"] == "My custom template: {user_prompt}"
    assert templates["detailed"] == "My custom template: {user_prompt}" # Check override
    assert "non_existent" not in templates # Non-existent should not be loaded

def test_prompt_enhancer_enhance():
    enhancer = PromptEnhancer()
    enhanced_prompt = enhancer.enhance("my simple prompt", "detailed")
    assert enhanced_prompt == "Detailed template: my simple prompt"

def test_prompt_enhancer_unknown_style():
    enhancer = PromptEnhancer()
    with pytest.raises(ValueError, match="Unknown style: unknown_style"):
        enhancer.enhance("my simple prompt", "unknown_style")

def test_load_templates_with_invalid_custom_path_type():
    custom_template_paths = {
        "invalid_style": 123 # Not a string
    }
    templates = load_templates(custom_template_paths)
    assert "invalid_style" not in templates

def test_load_templates_with_empty_custom_path_string():
    custom_template_paths = {
        "empty_path_style": "" # Empty string
    }
    templates = load_templates(custom_template_paths)
    assert "empty_path_style" not in templates
