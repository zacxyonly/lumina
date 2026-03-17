"""Interactive setup wizard for Lumina configuration."""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

console = Console()

# Provider configurations
PROVIDERS_INFO = {
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4-turbo-preview", "gpt-4", "gpt-3.5-turbo"],
        "key_url": "https://platform.openai.com/api-keys",
        "env_key": "OPENAI_API_KEY",
        "default_model": "gpt-4-turbo-preview"
    },
    "anthropic": {
        "name": "Anthropic Claude",
        "models": ["claude-3-5-sonnet-20241022", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
        "key_url": "https://console.anthropic.com/settings/keys",
        "env_key": "ANTHROPIC_API_KEY",
        "default_model": "claude-3-5-sonnet-20241022"
    },
    "google": {
        "name": "Google Gemini",
        "models": ["gemini-1.5-pro", "gemini-pro"],
        "key_url": "https://makersuite.google.com/app/apikey",
        "env_key": "GOOGLE_API_KEY",
        "default_model": "gemini-1.5-pro"
    },
    "groq": {
        "name": "Groq",
        "models": ["mixtral-8x7b-32768", "llama2-70b-4096"],
        "key_url": "https://console.groq.com/keys",
        "env_key": "GROQ_API_KEY",
        "default_model": "mixtral-8x7b-32768"
    }
}


def print_welcome():
    """Print welcome message."""
    welcome = """
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║     🌟  LUMINA Setup Wizard v1.1.0  🌟          ║
    ║     Lightweight AI Agent Framework               ║
    ║                                                   ║
    ║  Welcome! Let's configure your Lumina setup.     ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """
    console.print(welcome, style="bold cyan")


def show_provider_options():
    """Display available LLM providers."""
    console.print("\n[bold]Available LLM Providers:[/bold]\n")
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan")
    table.add_column("Provider", style="green")
    table.add_column("Models", style="yellow")
    
    for idx, (key, info) in enumerate(PROVIDERS_INFO.items(), 1):
        models = ", ".join(info["models"][:2]) + "..."
        table.add_row(str(idx), info["name"], models)
    
    console.print(table)


def select_provider() -> str:
    """Interactive provider selection."""
    show_provider_options()
    
    while True:
        choice = Prompt.ask(
            "\n[bold blue]Select provider (1-4)[/bold blue]",
            choices=["1", "2", "3", "4"]
        )
        
        providers = list(PROVIDERS_INFO.keys())
        return providers[int(choice) - 1]


def configure_provider(provider: str) -> Dict[str, Any]:
    """Configure selected provider."""
    info = PROVIDERS_INFO[provider]
    
    console.print(f"\n[bold green]Configuring {info['name']}[/bold green]")
    console.print(f"📝 Get your API key: [link]{info['key_url']}[/link]")
    
    # Get API key
    api_key = Prompt.ask(
        f"\n[bold blue]Enter your {info['name']} API key[/bold blue]",
        password=True
    )
    
    if not api_key.strip():
        console.print("[red]❌ API key cannot be empty[/red]")
        return configure_provider(provider)
    
    # Select model
    console.print(f"\n[bold]Available models for {info['name']}:[/bold]")
    for idx, model in enumerate(info["models"], 1):
        console.print(f"  {idx}. {model}")
    
    model_choice = Prompt.ask(
        "[bold blue]Select model (1-3)[/bold blue]",
        choices=[str(i) for i in range(1, len(info["models"]) + 1)],
        default="1"
    )
    
    model = info["models"][int(model_choice) - 1]
    
    return {
        "provider": provider,
        "api_key": api_key,
        "model": model,
        "env_key": info["env_key"]
    }


def configure_agent_settings() -> Dict[str, Any]:
    """Configure agent settings."""
    console.print("\n[bold]Agent Settings Configuration[/bold]")
    
    settings = {
        "temperature": float(Prompt.ask(
            "[bold blue]Temperature (0.0-2.0, default 0.7)[/bold blue]",
            default="0.7"
        )),
        "max_iterations": int(Prompt.ask(
            "[bold blue]Max iterations (default 10)[/bold blue]",
            default="10"
        )),
        "max_tokens": int(Prompt.ask(
            "[bold blue]Max tokens (default 4000)[/bold blue]",
            default="4000"
        )),
        "enable_memory": Confirm.ask(
            "[bold blue]Enable memory system?[/bold blue]",
            default=True
        ),
        "allow_code_execution": Confirm.ask(
            "[bold blue]Allow code execution?[/bold blue]",
            default=True
        ),
    }
    
    return settings


def configure_optional_settings() -> Dict[str, Any]:
    """Configure optional provider keys."""
    console.print("\n[bold]Optional: Configure Additional Provider Keys[/bold]")
    console.print("[dim]You can add more providers later in .env file[/dim]\n")
    
    settings = {}
    
    add_more = Confirm.ask(
        "Add another provider key?",
        default=False
    )
    
    if add_more:
        remaining = {k: v for k, v in PROVIDERS_INFO.items()}
        
        while add_more:
            show_provider_options()
            choice = Prompt.ask(
                "[bold blue]Select provider (1-4)[/bold blue]",
                choices=["1", "2", "3", "4"]
            )
            
            providers = list(PROVIDERS_INFO.keys())
            provider = providers[int(choice) - 1]
            
            info = PROVIDERS_INFO[provider]
            api_key = Prompt.ask(
                f"[bold blue]Enter {info['name']} API key (or skip)[/bold blue]",
                password=True,
                default=""
            )
            
            if api_key.strip():
                settings[info["env_key"]] = api_key
            
            add_more = Confirm.ask("Add another provider?", default=False)
    
    return settings


def create_env_file(config: Dict[str, Any], env_path: Path = Path(".env")) -> bool:
    """Create .env file with configuration."""
    try:
        content = "# Lumina Configuration - Auto-generated by Setup Wizard\n"
        content += "# Generated at: " + str(Path.cwd()) + "\n\n"
        
        content += "# ===== Primary LLM Provider =====\n"
        content += f"LUMINA_PROVIDER={config['provider']}\n"
        content += f"LUMINA_MODEL={config['model']}\n\n"
        
        content += "# ===== API Keys =====\n"
        content += f"{config['env_key']}={config['api_key']}\n"
        
        # Add optional keys
        for key, value in config.get("optional_keys", {}).items():
            content += f"{key}={value}\n"
        
        content += "\n# ===== Agent Settings =====\n"
        content += f"LUMINA_TEMPERATURE={config['settings']['temperature']}\n"
        content += f"LUMINA_MAX_ITERATIONS={config['settings']['max_iterations']}\n"
        content += f"LUMINA_MAX_TOKENS={config['settings']['max_tokens']}\n"
        content += f"LUMINA_ENABLE_MEMORY={str(config['settings']['enable_memory']).lower()}\n"
        content += f"LUMINA_ALLOW_CODE_EXEC={str(config['settings']['allow_code_execution']).lower()}\n"
        
        content += "\n# ===== Logging =====\n"
        content += "LUMINA_VERBOSE=true\n"
        content += "LUMINA_DEBUG=false\n"
        
        # Write file
        if env_path.exists():
            if not Confirm.ask(f"\n[yellow].env already exists. Overwrite?[/yellow]", default=False):
                return False
        
        with open(env_path, "w") as f:
            f.write(content)
        
        return True
    
    except Exception as e:
        console.print(f"[red]Error creating .env file: {str(e)}[/red]")
        return False


def test_configuration(config: Dict[str, Any]) -> bool:
    """Test the configuration by initializing Lumina."""
    console.print("\n[bold cyan]Testing configuration...[/bold cyan]")
    
    try:
        from lumina.utils.config import LuminaConfig
        
        # Create config object
        test_config = LuminaConfig(
            provider=config["provider"],
            model=config["model"],
            openai_api_key=config["api_key"] if config["provider"] == "openai" else None,
            anthropic_api_key=config["api_key"] if config["provider"] == "anthropic" else None,
            google_api_key=config["api_key"] if config["provider"] == "google" else None,
            groq_api_key=config["api_key"] if config["provider"] == "groq" else None,
            temperature=config["settings"]["temperature"],
            max_iterations=config["settings"]["max_iterations"],
            max_tokens=config["settings"]["max_tokens"],
            enable_memory=config["settings"]["enable_memory"],
            allow_code_execution=config["settings"]["allow_code_execution"],
        )
        
        # Validate
        test_config.validate()
        console.print("[green]✅ Configuration test passed![/green]")
        return True
    
    except Exception as e:
        console.print(f"[red]❌ Configuration test failed: {str(e)}[/red]")
        return False


def run_wizard():
    """Run the complete setup wizard."""
    print_welcome()
    
    # Step 1: Select provider
    provider = select_provider()
    provider_config = configure_provider(provider)
    
    # Step 2: Agent settings
    agent_settings = configure_agent_settings()
    
    # Step 3: Optional settings
    optional_keys = configure_optional_settings()
    
    # Prepare full config
    full_config = {
        **provider_config,
        "settings": agent_settings,
        "optional_keys": optional_keys
    }
    
    # Step 4: Test configuration
    if not test_configuration(full_config):
        if not Confirm.ask("\n[yellow]Configuration test failed. Continue anyway?[/yellow]"):
            console.print("[red]Setup cancelled[/red]")
            return False
    
    # Step 5: Create .env file
    console.print("\n[bold cyan]Creating .env file...[/bold cyan]")
    if create_env_file(full_config):
        console.print("[green]✅ .env file created successfully![/green]")
    else:
        console.print("[red]❌ Failed to create .env file[/red]")
        return False
    
    # Success message
    console.print("\n" + "=" * 50)
    console.print("[bold green]✨ Setup Complete! ✨[/bold green]")
    console.print("=" * 50)
    
    summary = f"""
    **Provider:** {PROVIDERS_INFO[provider]["name"]}
    **Model:** {provider_config["model"]}
    **Temperature:** {agent_settings['temperature']}
    **Max Iterations:** {agent_settings['max_iterations']}
    **Memory:** {'Enabled' if agent_settings['enable_memory'] else 'Disabled'}
    
    **Next steps:**
    1. Run `python -m lumina.cli` to start Lumina
    2. Check `.env` file to modify settings
    3. Visit documentation: https://github.com/mundai/lumina
    """
    
    console.print(Panel(Markdown(summary), title="[bold]Setup Summary[/bold]", border_style="green"))
    
    return True


if __name__ == "__main__":
    success = run_wizard()
    sys.exit(0 if success else 1)
