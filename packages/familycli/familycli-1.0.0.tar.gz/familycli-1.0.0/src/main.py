

#!/usr/bin/env python3
"""
Family AI CLI - Production-grade family chat simulation with AI personas.

A CLI application that allows users to create AI family member personas and have
natural conversations in a group chat format, supporting multiple LLM providers.
"""

import sys
import logging
from rich.console import Console
from rich.panel import Panel
from src.database.db_manager import initialize_database
from src.ui.cli_interface import main_menu, welcome_screen
from src.database.backup_utils import backup_database, log_event, notify_user
from src.auth.user_manager import get_logged_in_user
from src.config.user_config_manager import user_config
from src.personas.persona_manager import load_default_personas_for_user

# Configure logging to use .familyai directory
import os
_USER_DIR = os.path.expanduser('~/.familyai')
_LOG_FILE = os.path.join(_USER_DIR, 'logs', 'familycli.log')
os.makedirs(os.path.dirname(_LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(_LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
console = Console()

def setup_application():
    """Initialize the application, database, and user configuration."""
    try:
        console.print("[bold blue]Initializing Family AI CLI...[/bold blue]")

        # Check API keys
        import os
        api_keys_available = []
        if os.getenv('GROQ_API_KEY'):
            api_keys_available.append('Groq')
        if os.getenv('OPENAI_API_KEY'):
            api_keys_available.append('OpenAI')

        if api_keys_available:
            console.print(f"[green]✓ API keys found: {', '.join(api_keys_available)}[/green]")
        else:
            console.print("[yellow]⚠ No API keys found - AI responses will use fallback mode[/yellow]")
            console.print("[yellow]  See SETUP_API_KEYS.md for setup instructions[/yellow]")

        # Initialize database
        initialize_database()
        log_event("Database initialized successfully.")
        console.print("[green]✓ Database initialized[/green]")

        # Initialize user configuration
        user_config.initialize_default_config()
        console.print(f"[green]✓ User config initialized at {user_config.get_config_directory()}[/green]")

        # Load default personas for logged-in user
        user = get_logged_in_user()
        if user:
            created_personas = load_default_personas_for_user(user.user_id)
            if created_personas:
                console.print(f"[green]✓ Created {len(created_personas)} default personas[/green]")
            else:
                console.print("[yellow]• Default personas already exist or none created[/yellow]")

        return True
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        console.print(f"[red]✗ Failed to initialize: {e}[/red]")
        return False

def check_first_time_setup():
    """Check if this is the first time running the application."""
    user = get_logged_in_user()
    if not user:
        console.print(Panel(
            "[bold yellow]Welcome to Family AI CLI![/bold yellow]\n\n"
            "This appears to be your first time using the application.\n"
            "You'll need to create an account to get started.\n\n"
            "[dim]The application will guide you through the setup process.[/dim]",
            title="First Time Setup",
            style="yellow"
        ))
        return True
    return False

def main():
    """Main application entry point."""
    try:
        # Show creator info at startup
        console.print("[dim]Created by AIMLDev726[/dim]")
        console.print()

        # Show beta testing notice
        console.print(Panel(
            "[bold yellow]🚧 Beta Testing Release 🚧[/bold yellow]\n\n"
            "[cyan]Welcome to Family AI CLI v1.0.0![/cyan]\n\n"
            "This is our initial release and we're excited to have you test it! "
            "Your feedback helps us improve the experience for families everywhere.\n\n"
            "[bold green]Found an issue or have suggestions?[/bold green]\n"
            "• Visit: [link]https://github.com/AIMLDev726/ai-family-cli/issues[/link]\n"
            "• Click 'New Issue' to report bugs or request features\n"
            "• We appreciate your contribution to making this better!\n\n"
            "[dim]Thank you for being part of our beta testing community! 🙏[/dim]",
            title="Beta Release Notice",
            style="yellow",
            padding=(1, 2)
        ))
        console.print()

        # Show welcome screen
        welcome_screen()

        # Initialize application
        if not setup_application():
            console.print("[red]Failed to start application. Please check the logs.[/red]")
            sys.exit(1)

        # Check for first-time setup
        is_first_time = check_first_time_setup()

        if is_first_time:
            console.print("\n[bold cyan]Let's get you set up![/bold cyan]")
            console.print("You can create an account and start chatting with AI family members.")

        # Start the CLI application
        notify_user("Welcome to Family AI CLI!")
        main_menu()

    except KeyboardInterrupt:
        console.print("\n[yellow]Application interrupted by user.[/yellow]")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        console.print(f"[red]Unexpected error: {e}[/red]")
        console.print("[dim]Please check the logs for more details.[/dim]")
    finally:
        try:
            backup_database()
            log_event("Application shutdown.")
            console.print("[dim]Application shutdown complete.[/dim]")
            console.print("[dim]Thank you for beta testing Family AI CLI![/dim]")
            console.print("[dim]Share feedback: https://github.com/AIMLDev726/ai-family-cli/issues[/dim]")
            console.print("[dim]Created by AIMLDev726[/dim]")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
            console.print("[dim]Thank you for beta testing Family AI CLI![/dim]")
            console.print("[dim]Created by AIMLDev726[/dim]")

if __name__ == "__main__":
    main()
