import click
import questionary
import requests
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text
import sys
import difflib
import time
import random

from .config import load_config, create_default_config_if_not_exists
from .ollama_client import OllamaClient
from .enhancer import PromptEnhancer
from .clipboard import copy_to_clipboard
from .history import save_enhancement, load_history

@click.command()
@click.argument('prompt', required=False)
@click.option('-m', '--model', 'model_name', help='Ollama model to use (auto-selects optimal if not specified)')
@click.option('-t', '--temperature', type=click.FloatRange(0.0, 2.0), help='Temperature for generation (0.0-2.0)')
@click.option('-l', '--length', 'max_tokens', type=int, help='Max tokens for enhancement')
@click.option('-c', '--config', 'config_path', type=click.Path(), help='Configuration file path')
@click.option('-v', '--verbose', is_flag=True, help='Enable verbose output')
@click.option('-n', '--no-copy', is_flag=True, help="Don't copy to clipboard")
@click.option('-o', '--output', 'output_file', type=click.File('w'), help='Save enhanced prompt to file')
@click.option('-s', '--style', type=click.Choice(['detailed', 'concise', 'creative', 'technical', 'json', 'bullets', 'summary', 'formal', 'casual']), help='Enhancement style')
@click.option('--diff', is_flag=True, help='Show a diff between the original and enhanced prompt')
@click.option('--list-models', is_flag=True, help='List available Ollama models')
@click.option('--download-model', 'download_model_name', help='Download specific model from Ollama')
@click.option('--auto-setup', is_flag=True, help='Automatically setup Ollama with optimal model')
@click.option('--history', 'show_history', is_flag=True, help='Show enhancement history.')
@click.option('--interactive', 'is_interactive', is_flag=True, help='Start an interactive enhancement session.')
@click.option('--preload-model', is_flag=True, help='Preload a model to keep it in memory for faster responses.')
@click.version_option()
@click.help_option('-h', '--help')
def enhance(prompt, model_name, temperature, max_tokens, config_path, verbose, no_copy, output_file, style, diff, list_models, download_model_name, auto_setup, show_history, is_interactive, preload_model):
    """
    Enhances a simple prompt using Ollama AI models, displays the enhanced version,
    and automatically copies it to the clipboard.
    
    Note: Response speed and quality depend on your system specifications and the
    selected AI model. enhance-this provides the interface but cannot control
    underlying performance factors.
    """
    console = Console()
    config = load_config(config_path)
    client = OllamaClient(host=config['ollama_host'], timeout=config['timeout'])

    # Custom loading messages for better UX
    loading_messages = [
        "Initializing enhancement engine...",
        "Connecting to local AI model...",
        "Preparing prompt transformation...",
        "Loading language patterns...",
        "Setting up creative algorithms...",
        "Calibrating response parameters...",
        "Warming up neural pathways...",
        "Optimizing for maximum creativity...",
    ]

    if preload_model:
        available_models = client.list_models()
        if not available_models:
            console.print("[red]✖[/red] No models available to preload. Please run [bold]`enhance --auto-setup`[/bold] first.")
            sys.exit(1)

        preferred_models = config.get('preferred_models', ["llama3.1:8b", "llama3", "mistral"])
        model_to_preload = None
        for model in preferred_models:
            if model in available_models:
                model_to_preload = model
                break
        
        if not model_to_preload:
            model_to_preload = available_models[0]

        # Enhanced preloading with visual feedback
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(f"[cyan]Preloading model '{model_to_preload}'...", total=None)
            client.preload_model(model_to_preload)
            progress.update(task, description=f"[green]✔ Model '{model_to_preload}' preloaded successfully!")
            time.sleep(1)  # Brief pause for visual feedback
        return

    if show_history:
        history_entries = load_history()
        if not history_entries:
            console.print(Panel("[yellow]No history found.[/yellow]", title="History", border_style="yellow"))
            return

        choices = [
            {
                'name': f"{entry['original_prompt']} -> {entry['enhanced_prompt'][:50]}...",
                'value': entry
            }
            for entry in history_entries
        ]

        selected_entry = questionary.select(
            "Select a history entry to view:",
            choices=choices
        ).ask()

        if selected_entry:
            # Enhanced history display
            from rich.table import Table
            history_table = Table(title="History Details", border_style="green")
            history_table.add_column("Property", style="cyan", no_wrap=True)
            history_table.add_column("Value", style="magenta")
            
            history_table.add_row("Original Prompt", selected_entry['original_prompt'])
            history_table.add_row("Enhanced Prompt", selected_entry['enhanced_prompt'])
            history_table.add_row("Style", selected_entry['style'])
            history_table.add_row("Model", selected_entry['model'])
            
            console.print(history_table)

            if questionary.confirm("Copy enhanced prompt to clipboard?").ask():
                copy_to_clipboard(selected_entry['enhanced_prompt'])
                console.print("[green]✔ Copied to clipboard.[/green]")
        return

    if is_interactive:
        # Enhanced welcome message
        welcome_panel = Panel(
            "[bold green]Welcome to Interactive Mode![/bold green]\n"
            "Enhance your prompts in real-time with AI assistance.\n"
            "[dim]Type 'quit' or 'exit' to end the session.[/dim]",
            title="✨ Enhance This - Interactive Mode",
            border_style="bright_blue"
        )
        console.print(welcome_panel)

        enhancer = PromptEnhancer(config.get('enhancement_templates'))
        available_styles = list(enhancer.templates.keys())
        
        # Enhanced Ollama connection check
        try:
            if not client.is_running():
                console.print(Panel(
                    "[red]✖ Ollama service is not running or is unreachable.[/red]\n\n"
                    "[bold]Troubleshooting steps:[/bold]\n"
                    "1. Make sure Ollama is installed: [link]https://ollama.com/download[/link]\n"
                    "2. Start Ollama service: [cyan]ollama serve[/cyan]\n"
                    "3. Verify it's running: [cyan]curl http://localhost:11434[/cyan]",
                    title="Connection Error",
                    border_style="red"
                ))
                sys.exit(1)
        except Exception as e:
            console.print(Panel(
                f"[red]✖ Unexpected error while checking Ollama connection:[/red]\n{str(e)}",
                title="Connection Error",
                border_style="red"
            ))
            sys.exit(1)

        # Enhanced model check
        try:
            available_models = client.list_models()
        except Exception as e:
            console.print(Panel(
                f"[red]✖ Error retrieving model list:[/red]\n{str(e)}",
                title="Model Error",
                border_style="red"
            ))
            available_models = []

        if not available_models:
            console.print(Panel(
                "[red]✖ No models available.[/red]\n\n"
                "[bold]To resolve this:[/bold]\n"
                "1. Run [cyan]enhance --auto-setup[/cyan] (recommended)\n"
                "2. Or manually install a model: [cyan]ollama pull llama3.1:8b[/cyan]",
                title="Model Error",
                border_style="red"
            ))
            sys.exit(1)

        if model_name and model_name not in available_models:
            console.print(Panel(
                f"[red]✖ Model '{model_name}' not found.[/red]\n\n"
                f"[bold]Available models:[/bold]\n" +
                "\n".join([f"• {model}" for model in available_models]),
                title="Model Error",
                border_style="red"
            ))
            sys.exit(1)
        
        final_model = model_name or config.get('preferred_models', ["llama3.1:8b", "llama3", "mistral"])[0]

        console.print(f"[bold blue]🤖 Using model:[/bold blue] [cyan]{final_model}[/cyan]")
        
        current_prompt = ""
        enhanced_prompt = ""
        current_style = config.get('default_style', 'detailed')

        while True:
            try:
                if not current_prompt:
                    current_prompt = console.input("[bold cyan]Enter initial prompt: [/bold cyan]")
                    if current_prompt.lower() in ['quit', 'exit']:
                        break

                system_prompt = enhancer.enhance(current_prompt, current_style)
                
                # Enhanced loading experience with streaming
                enhanced_prompt = ""
                
                # Use Live for streaming output with a spinner
                with Live(console=console, auto_refresh=True, refresh_per_second=4) as live_display:
                    # Create initial display with spinner
                    from rich.spinner import Spinner
                    from rich.table import Table
                    
                    # Create initial display with spinner and panel
                    from rich.panel import Panel
                    
                    initial_panel = Panel(
                        "[cyan]Enhancing your prompt with AI model...[/cyan]\n"
                        "[dim]This may take a moment for larger models.[/dim]",
                        title="[bold blue]🚀 Enhancement in Progress[/bold blue]",
                        border_style="cyan",
                        expand=True,
                        padding=(1, 2)
                    )
                    
                    display_table = Table.grid(padding=1)
                    display_table.add_column(width=5)  # For spinner
                    display_table.add_column()
                    display_table.add_row(Spinner("dots", style="cyan"), initial_panel)
                    live_display.update(display_table)
                    
                    # Actual enhancement with streaming
                    chunk_count = 0
                    try:
                        for i, chunk in enumerate(client.generate_stream(final_model, system_prompt, 0.7, 2000)):
                            enhanced_prompt += chunk
                            chunk_count += 1
                            
                            # Update display with current content
                            if enhanced_prompt:
                                # Show streaming content with spinner
                                content_preview = enhanced_prompt
                                # Limit preview length but show more content
                                if len(content_preview) > 2000:
                                    content_preview = content_preview[:2000] + "\n... (content truncated for display)"
                                
                                # Create a better formatted display for streaming content
                                from rich.panel import Panel
                                from rich.text import Text
                                                    
                                # Create a panel with the streaming content
                                content_panel = Panel(
                                    Text(content_preview, style="magenta"),
                                    title=f"[cyan]Streaming Response[/cyan] [dim]Using 🤖: {final_model}[/dim]",
                                    border_style="green",
                                    expand=True,  # Allow panel to expand with content
                                    padding=(1, 2)
                                )
                                                    
                                # Create table with spinner and content panel
                                from rich.spinner import Spinner
                                display_table = Table.grid(padding=1)
                                display_table.add_column(width=5)  # For spinner
                                display_table.add_column()
                                display_table.add_row(
                                    Spinner("dots9", style="green"),
                                    content_panel
                                )
                                live_display.update(display_table)
                    except requests.exceptions.ConnectionError:
                        from rich.panel import Panel
                        console.print(Panel(
                            "[red]✖ Connection error with Ollama service.[/red]\n"
                            "[yellow]Please check if Ollama is running and try again.[/yellow]",
                            title="Connection Error",
                            border_style="red"
                        ))
                        continue
                    except requests.exceptions.Timeout:
                        from rich.panel import Panel
                        console.print(Panel(
                            "[red]✖ Request timed out.[/red]\n"
                            "[yellow]The model may still be loading. Please try again.[/yellow]",
                            title="Timeout Error",
                            border_style="red"
                        ))
                        continue
                    except KeyboardInterrupt:
                        from rich.panel import Panel
                        console.print(Panel(
                            "[yellow]⚠ Operation cancelled by user.[/yellow]\n\n"
                            "[dim]You can resume your session later.[/dim]",
                            title="Cancelled",
                            border_style="yellow"
                        ))
                        break
                    except Exception as e:
                        from rich.panel import Panel
                        console.print(Panel(
                            f"[red]✖ Error during enhancement:[/red]\n{str(e)}\n\n"
                            f"[yellow]Please try again or use a different model.[/yellow]",
                            title="Enhancement Error",
                            border_style="red"
                        ))
                        continue
                    
                    # Check if we received any content
                    if chunk_count == 0:
                        console.print("[yellow]⚠[/yellow] Warning: No response received from model.")
                    
                    # Show completion with enhanced visual feedback
                    completion_panel = Panel(
                        "[green]✨ Enhancement complete! AI response generated successfully.[/green]",
                        title="[bold green]✅ Success[/bold green]",
                        border_style="green",
                        expand=False,
                        padding=(1, 2)
                    )
                    
                    display_table = Table.grid(padding=1)
                    display_table.add_column(width=5)
                    display_table.add_column()
                    display_table.add_row("[green]✔[/green]", completion_panel)
                    live_display.update(display_table)
                    time.sleep(0.8)  # Longer pause for visual feedback
                
                # Enhanced prompt display
                console.print("\n[bold magenta]✨ Enhanced Prompt ✨[/bold magenta]")
                console.print(Panel(Markdown(enhanced_prompt), 
                                  title="Enhanced Output", 
                                  border_style="green",
                                  expand=False))

                action = console.input(
                    "[bold blue]Choose action:[/bold blue] "
                    "[bold](r)[/bold]efine, "
                    "[bold](s)[/bold]tyle, "
                    "[bold](c)[/bold]opy, "
                    "[bold](q)[/bold]uit: "
                ).lower()

                if action == 'r':
                    current_prompt = console.input("[bold cyan]Refine prompt: [/bold cyan]")
                elif action == 's':
                    console.print(f"[bold blue]Available styles:[/bold blue] {', '.join(available_styles)}")
                    new_style = console.input(f"[bold cyan]New style ({current_style}): [/bold cyan]")
                    if new_style in available_styles:
                        current_style = new_style
                    elif new_style:
                        console.print(f"[yellow]Invalid style. Sticking with {current_style}.[/yellow]")
                elif action == 'c':
                    try:
                        copy_to_clipboard(enhanced_prompt)
                    except Exception as e:
                        from rich.panel import Panel
                        console.print(Panel(
                            f"[red]✖ Error copying to clipboard:[/red]\n{str(e)}\n\n"
                            f"[yellow]You can manually copy the prompt above.[/yellow]",
                            title="Clipboard Error",
                            border_style="red"
                        ))
                elif action == 'q':
                    break
                else:
                    console.print("[yellow]Invalid action.[/yellow]")

            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Operation cancelled by user.[/yellow]")
                break
            except Exception as e:
                from rich.panel import Panel
                console.print(Panel(
                    f"[red]✖ Unexpected error in interactive mode:[/red]\n{str(e)}\n\n"
                    f"[yellow]Continuing session...[/yellow]",
                    title="Interactive Mode Error",
                    border_style="red"
                ))

        console.print(Panel("[bold green]Exiting interactive mode. Goodbye![/bold green] 👋", 
                          title="Session Ended", border_style="green"))
        return

    create_default_config_if_not_exists()
    
    # Enhanced Ollama connection check with better error handling
    try:
        if not client.is_running():
            console.print(Panel(
                "[red]✖ Ollama service is not running or is unreachable.[/red]\n\n"
                "[bold]Troubleshooting steps:[/bold]\n"
                "1. Make sure Ollama is installed: [link]https://ollama.com/download[/link]\n"
                "2. Start Ollama service: [cyan]ollama serve[/cyan]\n"
                "3. Verify it's running: [cyan]curl http://localhost:11434[/cyan]\n\n"
                "[yellow]Tip:[/yellow] On first run, try [cyan]enhance --auto-setup[/cyan] to automatically set up Ollama.",
                title="Connection Error",
                border_style="red"
            ))
            sys.exit(1)
    except Exception as e:
        from rich.panel import Panel
        console.print(Panel(
            f"[red]✖ Unexpected error while checking Ollama connection:[/red]\n{str(e)}\n\n"
            "[yellow]Please check your network connection and Ollama installation.[/yellow]",
            title="Connection Error",
            border_style="red"
        ))
        sys.exit(1)

    if list_models:
        try:
            models = client.list_models()
            if models:
                models_table = Table(title="Available Ollama Models", border_style="green")
                models_table.add_column("Model Name", style="cyan")
                for model in models:
                    models_table.add_row(model)
                console.print(models_table)
            else:
                console.print(Panel(
                    "[yellow]No Ollama models found.[/yellow]\n\n"
                    "[bold]To install a model:[/bold]\n"
                    "• Run [cyan]enhance --auto-setup[/cyan] (recommended)\n"
                    "• Or manually install: [cyan]ollama pull llama3.1:8b[/cyan]",
                    title="Models",
                    border_style="yellow"
                ))
        except Exception as e:
            from rich.panel import Panel
            console.print(Panel(
                f"[red]✖ Error listing models:[/red]\n{str(e)}",
                title="Model Error",
                border_style="red"
            ))
        return

    if download_model_name:
        console.print(f"[bold blue]📥 Starting download for '{download_model_name}'...[/bold blue]")
        try:
            success = client.download_model(download_model_name)
            if not success:
                console.print(Panel(
                    f"[red]✖ Failed to download model '{download_model_name}'.[/red]\n\n"
                    "[bold]Troubleshooting:[/bold]\n"
                    "• Check model name spelling\n"
                    "• Ensure internet connection\n"
                    "• Verify Ollama is running",
                    title="Download Error",
                    border_style="red"
                ))
        except Exception as e:
            from rich.panel import Panel
            console.print(Panel(
                f"[red]✖ Unexpected error downloading model:[/red]\n{str(e)}",
                title="Download Error",
                border_style="red"
            ))
        return
        
    available_models = []
    try:
        available_models = client.list_models()
    except Exception as e:
        from rich.panel import Panel
        console.print(Panel(
            f"[red]✖ Error retrieving model list:[/red]\n{str(e)}\n\n"
            "[yellow]Continuing with auto-setup...[/yellow]",
            title="Model Error",
            border_style="yellow"
        ))

    if auto_setup or not available_models:
        if not available_models:
            console.print(Panel(
                "[yellow]No models found. Starting auto-setup.[/yellow]\n"
                "[dim]This may take a few minutes to download the recommended model.[/dim]",
                title="Setup",
                border_style="yellow"
            ))
        else:
            console.print("[bold blue]Starting auto-setup...[/bold blue]")
        
        recommended_models = ["llama3.1:8b", "llama3", "mistral"]
        model_installed = False
        
        for model_to_try in recommended_models:
            try:
                if model_to_try not in available_models:
                    console.print(f"[bold blue]📥 Downloading recommended model:[/bold blue] [cyan]{model_to_try}[/cyan]")
                    if client.download_model(model_to_try):
                        available_models.append(model_to_try)
                        model_installed = True
                        break 
                else:
                    console.print(f"[green]✔[/green] Recommended model '[cyan]{model_to_try}[/cyan]' is already available.")
                    model_installed = True
                    break
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Error with model {model_to_try}: {e}")
                continue
        
        if not model_installed:
            console.print(Panel(
                "[red]✖ Auto-setup failed. Could not download a recommended model.[/red]\n\n"
                "[bold]Manual steps:[/bold]\n"
                "1. Check internet connection\n"
                "2. Try manually: [cyan]ollama pull llama3.1:8b[/cyan]\n"
                "3. Or visit: [link]https://ollama.com/library[/link]",
                title="Setup Error",
                border_style="red"
            ))
            sys.exit(1)

        if auto_setup:
             return

    if not prompt:
        ctx = click.get_current_context()
        click.echo(ctx.get_help())
        ctx.exit()

    if model_name:
        if model_name not in available_models:
            console.print(Panel(
                f"[red]✖ Model '{model_name}' not found.[/red]\n\n"
                f"[bold]Available models:[/bold]\n" +
                ("\n".join([f"• {model}" for model in available_models]) if available_models else "[yellow]No models available[/yellow]") +
                "\n\n[bold]To install models:[/bold]\n"
                "• Run [cyan]enhance --auto-setup[/cyan]\n"
                "• Or manually: [cyan]ollama pull <model-name>[/cyan]",
                title="Model Error",
                border_style="red"
            ))
            sys.exit(1)
        final_model = model_name
    else:
        preferred_models = config.get('preferred_models', ["llama3.1:8b", "llama3", "mistral"])
        final_model = None
        
        # Try to find a preferred model
        for model in preferred_models:
            if model in available_models:
                final_model = model
                break
        
        # If no preferred model found, use first available
        if not final_model:
            if available_models:
                final_model = available_models[0]
                console.print(Panel(
                    f"[yellow]Warning: Using '{final_model}' as it's the only available model.[/yellow]\n"
                    f"[dim]Configure preferred models in ~/.enhance-this/config.yaml[/dim]",
                    title="Model Selection",
                    border_style="yellow"
                ))
            else:
                console.print(Panel(
                    "[red]✖ No models available.[/red]\n\n"
                    "[bold]To resolve this:[/bold]\n"
                    "1. Run [cyan]enhance --auto-setup[/cyan] (recommended)\n"
                    "2. Or manually install a model: [cyan]ollama pull llama3.1:8b[/cyan]",
                    title="Model Error",
                    border_style="red"
                ))
                sys.exit(1)

        if verbose and model_name is None:
            console.print(f"[bold blue]No model specified.[/bold blue] Using best available model: [cyan]{final_model}[/cyan]")

    final_style = style or config.get('default_style', 'detailed')
    final_temperature = temperature if temperature is not None else config.get('default_temperature', 0.7)
    final_max_tokens = max_tokens or config.get('max_tokens', 2000)
    auto_copy_enabled = not no_copy and config.get('auto_copy', True)

    enhancer = PromptEnhancer(config.get('enhancement_templates'))

    system_prompt = enhancer.enhance(prompt, final_style)

    if verbose:
        console.print("\n[bold blue]🔧 System Prompt:[/bold blue]")
        console.print(Panel(system_prompt, title="System Prompt", border_style="dim"))

    enhanced_prompt = ""
    
    # Enhanced loading experience with dynamic messages and streaming
    console.print("[bold blue]🤖 Generating enhanced prompt...[/bold blue]")
    
    try:
        stream_generator = client.generate_stream(final_model, system_prompt, final_temperature, final_max_tokens)
        
        # Use Live for streaming output with a spinner
        with Live(console=console, auto_refresh=True, refresh_per_second=4) as live_display:
            # Create initial display with spinner
            from rich.spinner import Spinner
            from rich.table import Table
            
            # Create initial display with spinner and panel
            from rich.panel import Panel
            
            initial_panel = Panel(
                "[cyan]Loading model and generating response...[/cyan]\n"
                "[dim]This may take a moment for larger models.[/dim]",
                title="[bold blue]🧠 AI Generation in Progress[/bold blue]",
                border_style="cyan",
                expand=True,
                padding=(1, 2)
            )
            
            display_table = Table.grid(padding=1)
            display_table.add_column(width=5)  # For spinner
            display_table.add_column()
            display_table.add_row(Spinner("dots", style="cyan"), initial_panel)
            live_display.update(display_table)
            
            # Collect the output with streaming
            chunk_count = 0
            for i, chunk in enumerate(stream_generator):
                enhanced_prompt += chunk
                chunk_count += 1
                
                # Update display with current content
                if enhanced_prompt:
                    # Show streaming content with spinner
                    content_preview = enhanced_prompt
                    # Show full content without artificial limits for reasonable lengths
                    # Only add ellipsis for very long content to prevent display issues
                    if len(content_preview) > 2000:
                        content_preview = content_preview[:2000] + "\n... (content truncated for display)"
                    
                    # Create a better formatted display for streaming content
                    from rich.panel import Panel
                    from rich.text import Text
                    
                    # Create a panel with the streaming content
                    content_panel = Panel(
                        Text(content_preview, style="yellow"),
                        title=f"[cyan]Streaming Response[/cyan] [dim]Using 🤖: {final_model}[/dim]",
                        border_style="green",
                        expand=True,  # Allow panel to expand with content
                        padding=(1, 2)
                    )
                    
                    # Create table with spinner and content panel
                    from rich.spinner import Spinner
                    display_table = Table.grid(padding=1)
                    display_table.add_column(width=5)  # For spinner
                    display_table.add_column()
                    display_table.add_row(
                        Spinner("dots", style="green"),
                        content_panel
                    )
                    live_display.update(display_table)
            
            # Check if we received any content
            if chunk_count == 0:
                console.print("[yellow]⚠[/yellow] Warning: No response received from model.")
            
            # Show completion with enhanced visual feedback
            from rich.panel import Panel
            
            completion_panel = Panel(
                "[green]✨ Enhancement complete! AI response generated successfully.[/green]",
                title="[bold green]✅ Success[/bold green]",
                border_style="green",
                expand=False,
                padding=(1, 2)
            )
            
            display_table = Table.grid(padding=1)
            display_table.add_column(width=5)
            display_table.add_column()
            display_table.add_row("[green]✔[/green]", completion_panel)
            live_display.update(display_table)
            time.sleep(0.8)  # Longer pause for visual feedback
            
    except requests.exceptions.ConnectionError:
        from rich.panel import Panel
        console.print(Panel(
            "[red]✖ Connection error with Ollama service.[/red]\n\n"
            "[bold]Troubleshooting steps:[/bold]\n"
            "1. Make sure Ollama is installed: [cyan]https://ollama.com/download[/cyan]\n"
            "2. Start Ollama service: [cyan]ollama serve[/cyan]\n"
            "3. Verify it's running: [cyan]curl http://localhost:11434[/cyan]\n\n"
            "[yellow]Tip:[/yellow] On first run, try [cyan]enhance --auto-setup[/cyan] to automatically set up Ollama.",
            title="Connection Error",
            border_style="red"
        ))
        sys.exit(1)
    except requests.exceptions.Timeout:
        from rich.panel import Panel
        console.print(Panel(
            "[red]✖ Request timed out while communicating with Ollama.[/red]\n\n"
            "[yellow]This might happen if:[/yellow]\n"
            "• The model is still loading\n"
            "• The prompt is very complex\n"
            "• Your system is under heavy load\n\n"
            "[bold]Try:[/bold]\n"
            "• Increasing timeout in config (~/.enhance-this/config.yaml)\n"
            "• Using a smaller model\n"
            "• Restarting Ollama",
            title="Timeout Error",
            border_style="red"
        ))
        sys.exit(1)
    except KeyboardInterrupt:
        from rich.panel import Panel
        console.print(Panel(
            "[yellow]⚠ Operation cancelled by user.[/yellow]\n\n"
            "[dim]You can resume your work later.[/dim]",
            title="Cancelled",
            border_style="yellow"
        ))
        sys.exit(0)
    except Exception as e:
        from rich.panel import Panel
        console.print(Panel(
            f"[red]✖ Unexpected error during enhancement:[/red]\n{str(e)}\n\n"
            "[yellow]Please check the error and try again.[/yellow]",
            title="Enhancement Error",
            border_style="red"
        ))
        sys.exit(1)

    if enhanced_prompt:
        try:
            save_enhancement(prompt, enhanced_prompt, final_style, final_model)
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Warning: Could not save to history: {e}")
        
        # Enhanced success message
        success_panel = Panel(
            f"[green]✔[/green] Your prompt has been successfully enhanced!\n"
            f"[blue]Style:[/blue] {final_style} | [blue]Model:[/blue] {final_model}\n"
            f"[dim]Tokens generated: {len(enhanced_prompt)}[/dim]\n"
            f"[dim]Note: Response Speed/Quality depend on System's/AI-model's performance.[/dim]",
            title="Success",
            border_style="green"
        )
        console.print(success_panel)
        
        if diff:
            try:
                console.print("\n[bold yellow]↔️  Diff View ↔️[/bold yellow]")
                diff_result = difflib.unified_diff(
                    prompt.splitlines(keepends=True),
                    enhanced_prompt.splitlines(keepends=True),
                    fromfile='Original',
                    tofile='Enhanced',
                )
                for line in diff_result:
                    if line.startswith('+'):
                        console.print(f"[green]{line}[/green]", end="")
                    elif line.startswith('-'):
                        console.print(f"[red]{line}[/red]", end="")
                    elif line.startswith('@'):
                        console.print(f"[dim]{line}[/dim]", end="")
                    else:
                        console.print(line, end="")
            except Exception as e:
                console.print(f"[yellow]⚠[/yellow] Warning: Could not generate diff view: {e}")

        # Enhanced prompt display
        console.print("\n[bold magenta]✨ Enhanced Prompt ✨[/bold magenta]")
        try:
            console.print(Panel(Markdown(enhanced_prompt), 
                              title="Your Enhanced Prompt", 
                              border_style="green",
                              expand=False))
        except Exception as e:
            console.print(f"[yellow]⚠[/yellow] Warning: Could not render markdown: {e}")
            console.print(Panel(enhanced_prompt, 
                              title="Your Enhanced Prompt", 
                              border_style="green",
                              expand=False))

        if output_file:
            try:
                output_file.write(enhanced_prompt)
                console.print(f"\n[green]✔[/green] Saved to [cyan]{output_file.name}[/cyan]")
            except Exception as e:
                from rich.panel import Panel
                console.print(Panel(
                    f"[red]✖ Error saving to file:[/red]\n{str(e)}\n\n"
                    f"[yellow]Please check file permissions and path.[/yellow]",
                    title="File Error",
                    border_style="red"
                ))

        if auto_copy_enabled:
            try:
                copy_to_clipboard(enhanced_prompt)
            except Exception as e:
                from rich.panel import Panel
                console.print(Panel(
                    f"[red]✖ Unexpected error during clipboard copy:[/red]\n{str(e)}\n\n"
                    f"[yellow]You can manually copy the prompt above.[/yellow]",
                    title="Clipboard Error",
                    border_style="red"
                ))
    else:
        from rich.panel import Panel
        console.print(Panel(
            "[red]✖ Failed to generate enhanced prompt.[/red]\n\n"
            "[yellow]This might happen if:[/yellow]\n"
            "• The model is not responding\n"
            "• The prompt was invalid\n"
            "• There was a network issue\n\n"
            "[bold]Try:[/bold]\n"
            "• Checking Ollama status\n"
            "• Using a different model\n"
            "• Simplifying your prompt",
            title="Error",
            border_style="red"
        ))
        sys.exit(1)

if __name__ == '__main__':
    enhance()