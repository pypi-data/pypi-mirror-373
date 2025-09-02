import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

DEFAULT_CONFIG = {
    "default_temperature": 0.7,
    "default_style": "detailed",
    "ollama_host": "http://localhost:11434",
    "timeout": 30,
    "max_tokens": 2000,
    "auto_copy": True,
    "display_colors": True,
    "auto_download_model": True,
    "enhancement_templates": {},
    "preferred_models": ["llama3.1:8b", "llama3", "mistral"],
}

def get_config_dir() -> Path:
    return Path.home() / ".enhance-this"

def get_config_path(config_path_str: Optional[str] = None) -> Path:
    if config_path_str:
        return Path(config_path_str)
    return get_config_dir() / "config.yaml"

def load_config(config_path_str: Optional[str] = None) -> Dict[str, Any]:
    config_path = get_config_path(config_path_str)
    config = DEFAULT_CONFIG.copy()

    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                user_config = yaml.safe_load(f)
            if user_config:
                config.update(user_config)
        except (yaml.YAMLError, IOError):
            pass  # Use default config if file is invalid

    # Discover custom templates
    custom_templates_dir = get_config_dir() / "templates"
    if custom_templates_dir.is_dir():
        for template_file in custom_templates_dir.glob("*.txt"):
            style_name = template_file.stem
            if style_name not in config["enhancement_templates"]:
                config["enhancement_templates"][style_name] = str(template_file)

    return config

def ensure_config_dir_exists():
    get_config_dir().mkdir(parents=True, exist_ok=True)

def create_default_config_if_not_exists():
    ensure_config_dir_exists()
    config_path = get_config_path()
    if not config_path.exists():
        with open(config_path, 'w') as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False)
    
    # Create a default custom template as an example
    custom_templates_dir = get_config_dir() / "templates"
    custom_templates_dir.mkdir(exist_ok=True)
    example_template_path = custom_templates_dir / "my_style.txt"
    if not example_template_path.exists():
        example_template_path.write_text("This is your custom prompt. The user prompt is: {user_prompt}")
