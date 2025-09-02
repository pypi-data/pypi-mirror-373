import json
from pathlib import Path
from typing import List, Dict, Any
from .config import get_config_dir

HISTORY_FILE = get_config_dir() / "history.json"

def save_enhancement(original_prompt: str, enhanced_prompt: str, style: str, model: str):
    """Saves a new enhancement to the history."""
    entry = {
        "original_prompt": original_prompt,
        "enhanced_prompt": enhanced_prompt,
        "style": style,
        "model": model,
    }
    
    history = load_history()
    history.append(entry)
    
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def load_history() -> List[Dict[str, Any]]:
    """Loads the enhancement history."""
    if not HISTORY_FILE.exists():
        return []
    
    try:
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []
