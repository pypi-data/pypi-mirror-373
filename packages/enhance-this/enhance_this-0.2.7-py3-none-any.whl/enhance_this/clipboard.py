import pyperclip
from rich.console import Console
import platform

console = Console()

def copy_to_clipboard(text: str):
    """Copies the given text to the clipboard."""
    try:
        pyperclip.copy(text)
        console.print("[green]✔ Enhanced prompt copied to clipboard.[/green]")
    except pyperclip.PyperclipException as e:
        system = platform.system()
        if system == "Linux":
            console.print("[yellow]⚠[/yellow] Could not copy to clipboard. `xclip` or `xsel` may be required on Linux.\n"
                         "[dim]Install with: sudo apt-get install xclip or sudo yum install xclip[/dim]")
        elif system == "Windows":
            console.print("[yellow]⚠[/yellow] Could not copy to clipboard on Windows.\n"
                         "[dim]This may be due to missing clipboard permissions or system issues.[/dim]")
        elif system == "Darwin":  # macOS
            console.print("[yellow]⚠[/yellow] Could not copy to clipboard on macOS.\n"
                         "[dim]This may be due to missing clipboard permissions.[/dim]")
        else:
            console.print(f"[yellow]⚠[/yellow] Could not copy to clipboard on {system}.\n"
                         f"[dim]Error: {e}[/dim]")
    except Exception as e:
        console.print(f"[red]✖[/red] Unexpected error while copying to clipboard: {e}")