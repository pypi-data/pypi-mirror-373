import requests
import json
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from typing import List, Dict, Any, Iterator
from requests.adapters import HTTPAdapter, Retry
import platform

console = Console()

class OllamaClient:
    def __init__(self, host: str, timeout: int):
        self.host = host
        self.timeout = timeout
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def is_running(self) -> bool:
        try:
            response = self.session.get(self.host, timeout=self.timeout)
            return response.status_code == 200
        except requests.exceptions.ConnectionError:
            # More specific handling for connection errors
            return False
        except requests.RequestException:
            return False

    def list_models(self) -> List[str]:
        try:
            response = self.session.get(f"{self.host}/api/tags", timeout=self.timeout)
            response.raise_for_status()
            models = response.json().get("models", [])
            return [model["name"] for model in models]
        except requests.exceptions.ConnectionError:
            console.print("[yellow]⚠[/yellow] Could not connect to Ollama service to list models.")
            return []
        except requests.exceptions.Timeout:
            console.print("[yellow]⚠[/yellow] Timeout while trying to list models from Ollama.")
            return []
        except requests.RequestException as e:
            console.print(f"[yellow]⚠[/yellow] Error listing models from Ollama: {e}")
            return []

    def download_model(self, model_name: str) -> bool:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            transient=True,
        ) as progress:
            task = progress.add_task(f"[cyan]Downloading {model_name}", total=None)
            try:
                response = self.session.post(
                    f"{self.host}/api/pull",
                    json={"name": model_name, "stream": True},
                    stream=True,
                    timeout=None  # No timeout for download
                )
                response.raise_for_status()
                
                total = 0
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        if "total" in data and "completed" in data:
                            if not progress.tasks[task].total:
                                progress.update(task, total=data["total"])
                            progress.update(task, completed=data["completed"])
                        if data.get("status") == "success":
                            if progress.tasks[task].total:
                                progress.update(task, completed=progress.tasks[task].total)
                            break
                console.print(f"[green]✔[/green] Model '{model_name}' downloaded successfully.")
                return True
            except requests.exceptions.ConnectionError:
                console.print(f"[red]✖[/red] Connection error while downloading model '{model_name}'.\n"
                             f"[yellow]Please check if Ollama is running.[/yellow]")
                return False
            except requests.exceptions.Timeout:
                console.print(f"[red]✖[/red] Timeout while downloading model '{model_name}'.\n"
                             f"[yellow]The download may still be in progress in the background.[/yellow]")
                return False
            except requests.RequestException as e:
                console.print(f"[red]✖[/red] Failed to download model '{model_name}': {e}")
                return False
            except json.JSONDecodeError:
                console.print(f"[red]✖[/red] Failed to parse response from Ollama while downloading '{model_name}'.")
                return False

    def preload_model(self, model_name: str):
        """Sends a request to Ollama to load a model and keep it alive."""
        try:
            console.print(f"Preloading model '{model_name}'...")
            response = self.session.post(
                f"{self.host}/api/chat",
                json={
                    "model": model_name,
                    "messages": [{"role": "user", "content": "Hi"}],
                    "keep_alive": -1, # Keep alive indefinitely
                },
                stream=False,
                timeout=self.timeout,
            )
            response.raise_for_status()
            console.print(f"[green]✔[/green] Model '{model_name}' preloaded successfully.")
        except requests.exceptions.ConnectionError:
            console.print(f"[red]✖[/red] Connection error while preloading model '{model_name}'.\n"
                         f"[yellow]Please check if Ollama is running.[/yellow]")
        except requests.exceptions.Timeout:
            console.print(f"[red]✖[/red] Timeout while preloading model '{model_name}'.\n"
                         f"[yellow]The model may still be loading.[/yellow]")
        except requests.RequestException as e:
            console.print(f"[red]✖[/red] Failed to preload model '{model_name}': {e}")

    def generate_stream(self, model: str, prompt: str, temperature: float, max_tokens: int) -> Iterator[str]:
        try:
                response = self.session.post(
                    f"{self.host}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": temperature,
                            "num_predict": max_tokens,
                        }
                    },
                    stream=True,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        yield data.get("response", "")
                        if data.get("done"):
                            break
        except requests.exceptions.ConnectionError:
            console.print(f"[red]✖[/red] Connection error with Ollama service.\n"
                         f"[yellow]Please check if Ollama is running.[/yellow]")
            raise
        except requests.exceptions.Timeout:
            console.print(f"[red]✖[/red] Ollama request timed out after {self.timeout} seconds.\n"
                         f"[yellow]Try increasing the timeout in your config or using a smaller model.[/yellow]")
            raise
        except requests.RequestException as e:
            console.print(f"[red]✖[/red] Error communicating with Ollama: {e}")
            raise