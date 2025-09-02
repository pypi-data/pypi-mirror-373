import importlib.resources
from typing import Dict, Optional
from pathlib import Path
from rich.console import Console

console = Console()

def load_templates(custom_template_paths: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    templates = {}
    package = 'enhance_this'
    
    # Load built-in templates
    built_in_styles = ["detailed", "concise", "creative", "technical", "json", "bullets", "summary", "formal", "casual"]
    for style in built_in_styles:
        try:
            # Use importlib.resources.files to get a path-like object
            # and then read the text content. This is the recommended approach
            # for compatibility with both files and directories within packages.
            content = importlib.resources.files(package).joinpath(f'templates/{style}.txt').read_text(encoding='utf-8')
            templates[style] = content
        except FileNotFoundError:
            # This should not happen with built-in templates
            console.print(f"[red]✖[/red] Built-in template for style '{style}' not found.")

    # Load custom templates from config
    if custom_template_paths:
        for style, path_str in custom_template_paths.items():
            if not path_str:
                continue
            try:
                path = Path(path_str).expanduser()
                if path.is_file():
                    templates[style] = path.read_text(encoding='utf-8')
                else:
                    console.print(f"[yellow]⚠[/yellow] Custom template for style '{style}' not found at: {path_str}")
            except Exception as e:
                console.print(f"[red]✖[/red] Error loading custom template for style '{style}': {e}")

    return templates

class PromptEnhancer:
    def __init__(self, custom_template_paths: Optional[Dict[str, str]] = None):
        self.templates = load_templates(custom_template_paths)

    def enhance(self, user_prompt: str, style: str) -> str:
        if style not in self.templates:
            available_styles = list(self.templates.keys())
            raise ValueError(f"Unknown style: '{style}'. Available styles: {available_styles}")
        
        template = self.templates[style]
        return template.format(user_prompt=user_prompt)
