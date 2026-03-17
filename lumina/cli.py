"""Command-line interface for Lumina."""

import asyncio
import sys
from pathlib import Path
from typing import Optional
import argparse
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from lumina import Lumina
from lumina.utils.config import LuminaConfig, set_config
from lumina.utils.logger import setup_logging

console = Console()


def print_banner():
    """Print Lumina banner."""
    banner = """
    ╔═══════════════════════════════════════╗
    ║                                       ║
    ║        🌟  LUMINA v1.1.0  🌟         ║
    ║   Lightweight AI Agent Framework      ║
    ║                                       ║
    ╚═══════════════════════════════════════╝
    """
    console.print(banner, style="bold cyan")


async def run_task(agent: Lumina, task: str) -> None:
    """Run a single task."""
    try:
        result = await agent.run(task)
        
        console.print("\n")
        console.print(Panel(
            Markdown(result),
            title="[bold green]Result[/bold green]",
            border_style="green"
        ))
    except KeyboardInterrupt:
        console.print("\n[yellow]Task interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {str(e)}")


async def interactive_mode(agent: Lumina) -> None:
    """Run agent in interactive mode."""
    console.print("\n[cyan]Interactive mode started. Type 'exit' to quit.[/cyan]\n")
    
    while True:
        try:
            user_input = Prompt.ask("[bold blue]You[/bold blue]")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("[yellow]Goodbye![/yellow]")
                break
            
            if user_input.lower() == 'reset':
                agent.reset()
                console.print("[green]Agent state reset[/green]")
                continue
            
            if not user_input.strip():
                continue
            
            # Run task
            result = await agent.run(user_input)
            
            console.print("\n")
            console.print(Panel(
                Markdown(result),
                title="[bold magenta]Lumina[/bold magenta]",
                border_style="magenta"
            ))
            console.print("\n")
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Goodbye![/yellow]")
            break
        except Exception as e:
            console.print(f"\n[bold red]Error:[/bold red] {str(e)}\n")


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Lumina - Lightweight AI Agent Framework"
    )
    parser.add_argument(
        "task",
        nargs="?",
        help="Task to execute (omit for interactive mode)"
    )
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run setup wizard"
    )
    parser.add_argument(
        "--wizard",
        action="store_true",
        help="Run setup wizard (alias for --setup)"
    )
    parser.add_argument(
        "--provider",
        type=str,
        choices=["openai", "anthropic", "google", "groq"],
        help="LLM provider to use"
    )
    parser.add_argument(
        "--model",
        type=str,
        help="Model to use"
    )
    parser.add_argument(
        "--temperature",
        type=float,
        help="Temperature for generation (0.0-2.0)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        help="Maximum iterations for task execution"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--no-memory",
        action="store_true",
        help="Disable memory system"
    )
    
    args = parser.parse_args()
    
    # Handle setup wizard
    if args.setup or args.wizard:
        from lumina.wizard import run_wizard
        success = run_wizard()
        sys.exit(0 if success else 1)
    
    # Load config
    config = LuminaConfig.from_env()
    
    # Override with CLI args
    if args.provider:
        config.provider = args.provider
    if args.model:
        config.model = args.model
    if args.temperature:
        config.temperature = args.temperature
    if args.max_iterations:
        config.max_iterations = args.max_iterations
    if args.verbose:
        config.verbose = True
    if args.debug:
        config.debug = True
    if args.no_memory:
        config.enable_memory = False
    
    set_config(config)
    
    # Setup logging
    setup_logging(verbose=config.verbose or config.debug, log_file=config.log_dir / "lumina.log")
    
    # Print banner
    print_banner()
    
    # Initialize agent
    try:
        # Validate config
        config.validate()
        agent = Lumina(config=config, enable_memory=config.enable_memory)
    except ValueError as e:
        console.print(f"\n[bold red]Configuration Error:[/bold red]")
        console.print(f"[yellow]{str(e)}[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]Failed to initialize Lumina:[/bold red] {str(e)}")
        console.print("\n[cyan]Try running setup wizard:[/cyan]")
        console.print("[cyan]  python -m lumina.wizard[/cyan]\n")
        sys.exit(1)
    
    # Run task or interactive mode
    if args.task:
        await run_task(agent, args.task)
    else:
        await interactive_mode(agent)


def cli_main():
    """CLI entry point wrapper."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
        sys.exit(0)


if __name__ == "__main__":
    cli_main()
