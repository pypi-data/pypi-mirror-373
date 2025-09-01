
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from src.auth.user_manager import register_user, login_user, get_logged_in_user, logout_user
from src.personas.persona_manager import create_persona, get_personas_by_user
from src.chat.session_manager import create_session, get_sessions_by_user
from src.chat.chat_engine import send_message, get_messages_for_session

console = Console()
app = typer.Typer()

def welcome_screen():
	logo = r"""
	 ____              _ _         _    _ ___ 
	|  _ \ __ _ _ __ (_) | _____ | |  | |_ _|
	| |_) / _` | '_ \| | |/ / _ \| |  | || | 
	|  __/ (_| | | | | |   <  __/| |__| || | 
	|_|   \__,_|_| |_|_|_|\_\___| \____/|___|
	"""
	console.print(Panel(logo, title="Family AI CLI", subtitle="Welcome!", style="bold magenta"))

@app.command()
def signup():
	username = Prompt.ask("Enter username")
	password = Prompt.ask("Enter password", password=True)
	try:
		user = register_user(username, password)
		console.print(f"[green]User {username} registered successfully![/green]")
	except Exception as e:
		console.print(f"[red]Error: {e}[/red]")

@app.command()
def login():
	username = Prompt.ask("Enter username")
	password = Prompt.ask("Enter password", password=True)
	try:
		user = login_user(username, password)
		console.print(f"[green]Logged in as {username}![green]")
		# Show dashboard after login
		main_menu()
	except Exception as e:
		console.print(f"[red]Error: {e}[red]")

@app.command()
def logout():
	logout_user()
	console.print("[yellow]Logged out.[/yellow]")

@app.command()
def main_menu():
	user = get_logged_in_user()
	if not user:
		console.print("[red]Please login first.[/red]")
		return

	# Load default personas if none exist
	from src.personas.persona_manager import load_default_personas_for_user
	load_default_personas_for_user(user.user_id)

	# Ensure API keys are set up for LLM responses
	ensure_api_keys_configured()

	# Show WhatsApp-like main menu
	show_whatsapp_style_menu(user.user_id)

def show_whatsapp_style_menu(user_id):
	"""Show WhatsApp-style main menu with chat options"""
	sessions = get_sessions_by_user(user_id)

	while True:
		console.print("\n" + "="*50)
		console.print("[bold cyan]💬 Family AI Chat[/bold cyan]")
		console.print("="*50)

		if sessions:
			# Show recent sessions like WhatsApp chat list
			console.print("[bold yellow]📱 Recent Chats:[/bold yellow]")
			for i, session in enumerate(sessions[-5:], 1):  # Show last 5 sessions
				last_active = session.last_active.strftime("%m/%d %H:%M") if session.last_active else "Never"
				session_type_icon = "👥" if session.session_type == "family" else "👤"
				console.print(f"  {i}. {session_type_icon} {session.session_name} - {last_active}")
			console.print()

		# Main menu options
		console.print("[bold green]🚀 Quick Actions:[/bold green]")
		console.print("1. 👥 Start Family Group Chat")
		console.print("2. 👤 Chat with Individual Persona")
		console.print("3. 📱 Continue Recent Chat" + (" (if available)" if not sessions else ""))
		console.print("4. ⚙️  Settings & Management")
		console.print("5. 🚪 Logout")
		console.print("6. ❌ Exit")

		choice = Prompt.ask("\n[bold cyan]Choose an option[/bold cyan]", choices=["1","2","3","4","5","6"])

		if choice == "1":
			start_family_group_chat(user_id)
		elif choice == "2":
			start_individual_chat(user_id)
		elif choice == "3":
			if sessions:
				continue_recent_chat(user_id, sessions)
			else:
				console.print("[yellow]No recent chats available. Starting a new family chat...[/yellow]")
				start_family_group_chat(user_id)
		elif choice == "4":
			settings_and_management_menu(user_id)
		elif choice == "5":
			logout()
			break
		elif choice == "6":
			console.print("[yellow]👋 Goodbye![/yellow]")
			break

def start_family_group_chat(user_id):
	"""Start a family group chat with multiple personas"""
	console.print("\n[bold green]👥 Starting Family Group Chat[/bold green]")

	# Validate API keys before allowing chat creation
	if not require_api_keys_for_chat():
		return

	# Check available personas
	from src.personas.persona_manager import get_personas_by_user
	personas = get_personas_by_user(user_id)

	if len(personas) < 2:
		console.print("[yellow]⚠️  You need at least 2 personas for a group chat.[/yellow]")
		console.print("[dim]Let's create some family members first...[/dim]")
		persona_menu(user_id)
		return

	# Create or select group session
	session_name = Prompt.ask("Enter group chat name", default="Family Chat")
	session = create_session(user_id, session_name, "family")

	console.print(f"[green]✅ Created group chat '{session_name}' with {len(personas)} family members![/green]")
	console.print(f"[cyan]👥 Members: {', '.join([p.name for p in personas[:5]])}{'...' if len(personas) > 5 else ''}[/cyan]")

	chat_loop(session['session_id'], user_id)

def start_individual_chat(user_id):
	"""Start a chat with a single persona"""
	console.print("\n[bold green]👤 Individual Chat[/bold green]")

	# Validate API keys before allowing chat creation
	if not require_api_keys_for_chat():
		return

	# Show available personas
	from src.personas.persona_manager import get_personas_by_user
	personas = get_personas_by_user(user_id)

	if not personas:
		console.print("[yellow]⚠️  No personas available.[/yellow]")
		console.print("[dim]Let's create some family members first...[/dim]")
		persona_menu(user_id)
		return

	# Let user select a persona
	console.print("[bold cyan]Select a family member to chat with:[/bold cyan]")
	for i, persona in enumerate(personas, 1):
		console.print(f"  {i}. {persona.name} ({persona.age}) - {persona.description[:50]}...")

	try:
		choice = int(Prompt.ask("Enter number")) - 1
		if 0 <= choice < len(personas):
			selected_persona = personas[choice]
			session_name = f"Chat with {selected_persona.name}"
			session = create_session(user_id, session_name, "individual")

			console.print(f"[green]✅ Starting chat with {selected_persona.name}![/green]")
			chat_loop(session['session_id'], user_id)
		else:
			console.print("[red]Invalid selection.[/red]")
	except ValueError:
		console.print("[red]Please enter a valid number.[/red]")

def continue_recent_chat(user_id, sessions):
	"""Continue a recent chat session"""
	console.print("\n[bold green]📱 Continue Recent Chat[/bold green]")

	# Validate API keys before allowing chat continuation
	if not require_api_keys_for_chat():
		return

	# Show recent sessions
	console.print("[bold cyan]Select a recent chat:[/bold cyan]")
	recent_sessions = sessions[-10:]  # Last 10 sessions

	for i, session in enumerate(recent_sessions, 1):
		last_active = session.last_active.strftime("%m/%d %H:%M") if session.last_active else "Never"
		session_type_icon = "👥" if session.session_type == "family" else "👤"
		console.print(f"  {i}. {session_type_icon} {session.session_name} - {last_active}")

	try:
		choice = int(Prompt.ask("Enter number")) - 1
		if 0 <= choice < len(recent_sessions):
			selected_session = recent_sessions[choice]
			console.print(f"[green]✅ Continuing chat: {selected_session.session_name}[/green]")

			# Show recent history
			show_recent_history(selected_session.session_id, user_id)
			chat_loop(selected_session.session_id, user_id)
		else:
			console.print("[red]Invalid selection.[/red]")
	except ValueError:
		console.print("[red]Please enter a valid number.[/red]")

def settings_and_management_menu(user_id):
	"""Settings and management menu"""
	while True:
		console.print("\n[bold cyan]⚙️  Settings & Management[/bold cyan]")
		console.print("1. 👥 Manage Family Members (Personas)")
		console.print("2. 🔑 API Key Management")
		console.print("3. 📱 View All Chat Sessions")
		console.print("4. 🗑️  Delete Old Sessions")
		console.print("5. ⬅️  Back to Main Menu")

		choice = Prompt.ask("Choose an option", choices=["1","2","3","4","5"])

		if choice == "1":
			persona_menu(user_id)
		elif choice == "2":
			api_key_menu()
		elif choice == "3":
			view_sessions(user_id)
		elif choice == "4":
			console.print("[yellow]🚧 Delete sessions feature coming soon![/yellow]")
		elif choice == "5":
			break

def show_recent_history(session_id, user_id):
	"""Show the last 5 messages from the session (WhatsApp-like)"""
	try:
		from src.chat.chat_engine import ChatEngine
		from src.personas.persona_manager import get_persona_by_id

		chat_engine = ChatEngine()
		messages = chat_engine.get_messages_for_session(session_id)

		if messages:
			recent_messages = messages[-5:]  # Last 5 messages
			console.print("\n[dim]--- Recent conversation ---[/dim]")

			for msg in recent_messages:
				if msg.sender_id:  # AI message
					persona = get_persona_by_id(msg.sender_id)
					sender_name = persona.name if persona else "AI"
					formatted_msg = format_ai_response(f"{sender_name}: {msg.message_content}")
					console.print(formatted_msg)
				else:  # User message
					formatted_msg = format_user_message(msg.message_content)
					console.print(formatted_msg)

			console.print("[dim]--- End of recent conversation ---[/dim]\n")
		else:
			console.print("[dim]No previous messages in this session.[/dim]\n")

	except Exception as e:
		console.print(f"[red]Error loading conversation history: {e}[/red]")

@app.command()
def menu():
	"""Show the main menu - same as main_menu for convenience"""
	main_menu()

def persona_menu(user_id):
	"""Enhanced persona management menu"""
	while True:
		console.print(Panel(
			"[bold green]Persona Management[/bold green]\n"
			"1. Create Persona\n"
			"2. List Personas\n"
			"3. Manage LLM Providers\n"
			"4. Validate Persona Providers\n"
			"5. Back",
			title="Personas"
		))
		choice = Prompt.ask("Select option", choices=["1","2","3","4","5"])

		if choice == "1":
			create_new_persona_interactive(user_id)
		elif choice == "2":
			view_personas_detailed(user_id)
		elif choice == "3":
			manage_persona_llm_providers(user_id)
		elif choice == "4":
			validate_persona_providers(user_id)
		elif choice == "5":
			break

def view_personas_detailed(user_id):
	"""View personas with detailed information including LLM providers."""
	personas = get_personas_by_user(user_id)
	if personas:
		table = Table(title="Your Family Members")
		table.add_column("ID")
		table.add_column("Name")
		table.add_column("Age")
		table.add_column("Description")
		table.add_column("LLM Provider")
		table.add_column("Model")

		for persona in personas:
			provider = persona.llm_provider or "Not assigned"
			model = persona.llm_model or "Not assigned"
			table.add_row(
				str(persona.persona_id),
				persona.name,
				str(persona.age),
				(persona.description[:30] + "...") if persona.description and len(persona.description) > 30 else (persona.description or ""),
				provider,
				model
			)
		console.print(table)
	else:
		console.print("[yellow]No personas found.[/yellow]")

def create_new_persona_interactive(user_id):
	"""Interactive persona creation with LLM provider assignment."""
	name = Prompt.ask("Persona name")
	age = Prompt.ask("Age", default="30")
	description = Prompt.ask("Description", default="Family member")

	# Get valid providers for assignment
	valid_providers = validate_api_keys_for_chat()
	if valid_providers:
		console.print(f"[green]Available LLM providers: {', '.join(valid_providers)}[/green]")
		provider = Prompt.ask("Choose LLM provider", choices=valid_providers, default=valid_providers[0])

		# Get model for provider
		provider_models = {
			"groq": "llama-3.1-8b-instant",
			"openai": "gpt-4o-mini",
			"anthropic": "claude-3-5-haiku-20241022",
			"cerebras": "llama3.1-8b",
			"google": "gemini-1.5-flash"
		}
		model = provider_models.get(provider, "default")
	else:
		console.print("[yellow]⚠️  No valid API keys found. Persona will be created without LLM provider.[/yellow]")
		provider = None
		model = None

	persona = create_persona(user_id, name, int(age), description, llm_provider=provider, llm_model=model)
	console.print(f"[green]✅ Persona {name} created with provider {provider}![/green]")

def manage_persona_llm_providers(user_id):
	"""Manage LLM provider assignments for personas."""
	personas = get_personas_by_user(user_id)
	if not personas:
		console.print("[yellow]No personas found.[/yellow]")
		return

	# Show current assignments
	console.print("\n[bold cyan]Current LLM Provider Assignments:[/bold cyan]")
	for i, persona in enumerate(personas, 1):
		provider = persona.llm_provider or "Not assigned"
		model = persona.llm_model or "Not assigned"
		console.print(f"  {i}. {persona.name} → {provider} ({model})")

	# Let user select persona to modify
	try:
		choice = int(Prompt.ask("Select persona to modify (number)")) - 1
		if 0 <= choice < len(personas):
			selected_persona = personas[choice]

			# Get valid providers
			valid_providers = validate_api_keys_for_chat()
			if not valid_providers:
				console.print("[red]❌ No valid API keys configured. Cannot assign providers.[/red]")
				return

			console.print(f"[green]Available providers: {', '.join(valid_providers)}[/green]")
			new_provider = Prompt.ask("Choose new LLM provider", choices=valid_providers)

			# Update the persona
			from src.personas.persona_manager import validate_and_assign_llm_provider
			try:
				result = validate_and_assign_llm_provider(selected_persona.persona_id, new_provider)
				console.print(f"[green]✅ Updated {selected_persona.name} to use {result['provider']} ({result['model']})[/green]")
			except Exception as e:
				console.print(f"[red]❌ Failed to update provider: {e}[/red]")
		else:
			console.print("[red]Invalid selection.[/red]")
	except ValueError:
		console.print("[red]Please enter a valid number.[/red]")

def validate_persona_providers(user_id):
	"""Validate and fix persona LLM provider assignments."""
	console.print("\n[bold cyan]🔍 Validating Persona LLM Providers...[/bold cyan]")

	from src.personas.persona_manager import ensure_personas_have_valid_providers

	try:
		success, result = ensure_personas_have_valid_providers(user_id)

		if not success:
			console.print(f"[red]❌ Validation failed: {result}[/red]")
			return

		if not result:
			console.print("[green]✅ All personas already have valid LLM providers assigned.[/green]")
		else:
			console.print("[yellow]⚠️  Some personas had invalid providers. Updated assignments:[/yellow]")
			for update in result:
				console.print(f"  • {update['name']} → {update['provider']} ({update['model']})")
			console.print("[green]✅ All personas now have valid LLM providers.[/green]")

	except Exception as e:
		console.print(f"[red]❌ Error during validation: {e}[/red]")

def format_ai_response(response: str) -> str:
	"""Format AI response with improved visual presentation."""
	import re
	from rich.panel import Panel
	from rich.text import Text
	from rich.markdown import Markdown

	# Extract persona name and message
	if ": " in response:
		persona_name, message = response.split(": ", 1)
	else:
		persona_name = "AI"
		message = response

	# Clean up the message
	message = message.strip()

	# Check if message contains markdown-like formatting
	from src.ui.markdown_renderer import is_markdown_content

	if is_markdown_content(message):
		try:
			# Render as markdown for rich formatting
			from src.ui.markdown_renderer import clean_markdown_content
			cleaned_message = clean_markdown_content(message)
			markdown_content = Markdown(cleaned_message)

			# Get persona-specific color
			persona_colors = {
				"Grandma Rose": "magenta",
				"Uncle Joe": "green",
				"Dad Mike": "blue",
				"Mom Sarah": "yellow",
				"Cousin Emma": "cyan",
				"Bhai": "bright_blue"
			}
			color = persona_colors.get(persona_name, "cyan")

			return Panel(
				markdown_content,
				title=f"[bold {color}]{persona_name}[/bold {color}]",
				border_style=color,
				padding=(0, 1)
			)
		except Exception:
			# Fallback to regular formatting if markdown fails
			pass

	# Regular text formatting with persona-specific colors
	persona_colors = {
		"Grandma Rose": "magenta",
		"Uncle Joe": "green",
		"Dad Mike": "blue",
		"Mom Sarah": "yellow",
		"Cousin Emma": "cyan",
		"Bhai": "bright_blue"
	}

	color = persona_colors.get(persona_name, "cyan")

	# Create a nicely formatted panel
	return Panel(
		Text(message, style=color),
		title=f"[bold {color}]{persona_name}[/bold {color}]",
		border_style=color,
		padding=(0, 1),
		expand=False
	)

def format_user_message(message: str) -> str:
	"""Format user message with consistent styling."""
	from rich.text import Text
	return Text(f"You: {message}", style="bold yellow")

def format_system_message(message: str, style: str = "dim") -> str:
	"""Format system messages with consistent styling."""
	from rich.text import Text
	return Text(message, style=style)

from src.auth.encryption import get_api_key, store_api_key

def start_chat_session(user_id):
	session_name = Prompt.ask("Session name")
	session_type = Prompt.ask("Session type", default="family")
	# Prompt for LLM provider and API key if missing
	provider = Prompt.ask("LLM provider (openai/groq/anthropic/cerebras/google)", default="openai")
	api_key = get_api_key(provider)
	if not api_key:
		api_key_input = Prompt.ask(f"Enter API key for {provider}", password=True)
		store_api_key(provider, api_key_input)
		console.print(f"[green]API key for {provider} stored securely.[green]")
	session = create_session(user_id, session_name, session_type)
	console.print(f"[green]Session {session_name} started![green]")
	chat_loop(session['session_id'], user_id)

def chat_loop(session_id, user_id=None):
	"""Production-grade chat loop with AI family members."""
	if user_id is None:
		user = get_logged_in_user()
		user_id = user.user_id if user else None
	from src.chat.chat_engine import ChatEngine
	from src.database.models import Session
	from src.database.db_manager import DatabaseManager
	import asyncio

	# Get session info
	db = DatabaseManager()
	db_session = db.get_session()
	try:
		chat_session = db_session.query(Session).filter_by(session_id=session_id).first()
		if not chat_session:
			console.print("[red]Session not found.[/red]")
			return
		user_id = chat_session.user_id
	finally:
		db_session.close()

	# Get user's personas
	personas = get_personas_by_user(user_id)
	if not personas:
		console.print("[yellow]No personas found. Please create some family members first.[/yellow]")
		return

	console.print(f"[bold green]💬 {chat_session.session_name}[/bold green]")
	console.print(f"[cyan]👥 Family members: {', '.join([p.name for p in personas])}[/cyan]")
	console.print("[dim]Type your message and press Enter. Use '/menu' for options, '/exit' to quit.[/dim]\n")

	chat_engine = ChatEngine()

	# Show recent messages
	recent_messages = chat_engine.get_messages_for_session(session_id, limit=5)
	if recent_messages:
		console.print("[dim]Recent messages:[/dim]")
		for msg in recent_messages:
			if msg.sender_id:
				persona = next((p for p in personas if p.persona_id == msg.sender_id), None)
				sender_name = persona.name if persona else "Unknown"
				console.print(f"[bold cyan]{sender_name}:[/bold cyan] {msg.message_content}")
			else:
				console.print(f"[bold yellow]You:[/bold yellow] {msg.message_content}")
		console.print()

	while True:
		try:
			message = Prompt.ask("[bold yellow]You[/bold yellow]")

			# Handle special commands
			if message.lower() in ["exit", "quit", "/exit", "/quit"]:
				console.print("[yellow]👋 Chat ended. Your conversation is saved![/yellow]")
				break
			elif message.lower() in ["/menu", "menu"]:
				show_chat_menu(session_id, user_id)
				continue
			elif message.lower() in ["/help", "help"]:
				show_chat_help()
				continue

			if not message.strip():
				continue

			# Send user message
			chat_engine.send_message(session_id, None, message)

			# Generate AI responses with better feedback
			console.print("[dim]💭 Family members are thinking...[/dim]")
			responses = asyncio.run(chat_engine.generate_ai_responses(session_id, message, user_id))

			if responses:
				for response in responses:
					# Enhanced message formatting with better visual separation
					formatted_response = format_ai_response(response)
					console.print(formatted_response)
			else:
				# Check if API keys are configured
				from src.auth.encryption import get_api_key
				import os

				api_key_found = False
				providers = ["groq", "openai", "anthropic", "cerebras", "google"]
				for provider in providers:
					try:
						encrypted_key = get_api_key(provider)
						env_key = os.getenv(f'{provider.upper()}_API_KEY')

						# Check if encrypted key is valid (not just exists)
						if encrypted_key and encrypted_key.strip() and len(encrypted_key.strip()) > 10:
							api_key_found = True
							break
						if env_key and env_key.strip() and len(env_key.strip()) > 10:
							api_key_found = True
							break
					except Exception as e:
						# If decryption fails, the key is invalid
						continue

				if not api_key_found:
					console.print("[red]⚠️  No API keys configured - AI responses are disabled[/red]")
					console.print("[yellow]📝 Please configure API keys using Settings & Management (option 4) to enable AI responses[/yellow]")
					console.print("[dim]   Supported providers: Groq, OpenAI, Anthropic, Cerebras, Google[/dim]")
				else:
					console.print("[dim]😴 Everyone seems busy right now...[/dim]")

			console.print()  # Add spacing

		except KeyboardInterrupt:
			console.print("\n[yellow]👋 Chat interrupted. Your conversation is saved![/yellow]")
			break
		except Exception as e:
			console.print(f"[red]❌ Error in chat: {e}[/red]")
			console.print("[dim]Try again or type '/exit' to quit.[/dim]")
			continue

def show_chat_menu(session_id, user_id):
	"""Show in-chat menu options"""
	console.print(Panel(
		"[bold cyan]Chat Options[/bold cyan]\n"
		"1. Switch to different session\n"
		"2. View conversation history\n"
		"3. Manage personas\n"
		"4. Continue chatting",
		title="Quick Menu"
	))

	choice = Prompt.ask("Select option", choices=["1","2","3","4"], default="4")

	if choice == "1":
		session_menu(user_id)
	elif choice == "2":
		show_full_history(session_id, user_id)
	elif choice == "3":
		persona_menu(user_id)
	# Choice 4 or default continues chatting

def show_chat_help():
	"""Show chat help information"""
	console.print(Panel(
		"[bold cyan]Chat Commands[/bold cyan]\n"
		"• Type normally to chat with family\n"
		"• '/menu' - Show quick options\n"
		"• '/exit' or '/quit' - End chat (saves conversation)\n"
		"• '/help' - Show this help\n"
		"• Ctrl+C - Quick exit\n\n"
		"[bold yellow]Tips:[/bold yellow]\n"
		"• Your conversation is automatically saved\n"
		"• Family members respond based on their personalities\n"
		"• Try asking questions or sharing stories!",
		title="Help"
	))

def show_full_history(session_id, user_id):
	"""Show complete conversation history"""
	try:
		from src.chat.chat_engine import ChatEngine
		from src.personas.persona_manager import get_persona_by_id

		chat_engine = ChatEngine()
		messages = chat_engine.get_messages_for_session(session_id)

		if not messages:
			console.print("[dim]No messages in this session yet.[/dim]")
			return

		console.print(f"\n[bold cyan]📜 Complete Conversation History ({len(messages)} messages)[/bold cyan]")
		console.print("[dim]" + "="*50 + "[/dim]")

		for msg in messages:
			timestamp = msg.timestamp.strftime("%H:%M") if msg.timestamp else ""
			if msg.sender_id:  # AI message
				persona = get_persona_by_id(msg.sender_id)
				sender_name = persona.name if persona else "AI"
				# Create a compact version for history
				console.print(f"[dim]{timestamp}[/dim] [bold cyan]{sender_name}:[/bold cyan] {msg.message_content}")
			else:  # User message
				console.print(f"[dim]{timestamp}[/dim] [bold yellow]You:[/bold yellow] {msg.message_content}")

		console.print("[dim]" + "="*50 + "[/dim]")
		Prompt.ask("Press Enter to continue")

	except Exception as e:
		console.print(f"[red]Error loading history: {e}[/red]")

def session_menu(user_id):
	"""Session management menu"""
	sessions = get_sessions_by_user(user_id)

	if not sessions:
		console.print("[yellow]No sessions found. Creating a new family chat session.[/yellow]")
		session = create_session(user_id, "Family Chat", "family")
		chat_loop(session['session_id'], user_id)
		return

	console.print(Panel("[bold cyan]Session Management[/bold cyan]\n1. Switch to existing session\n2. Create new session\n3. Back", title="Sessions"))
	choice = Prompt.ask("Select option", choices=["1","2","3"])

	if choice == "1":
		# Show sessions and let user select
		table = Table(title="Available Sessions")
		table.add_column("ID")
		table.add_column("Name")
		table.add_column("Type")
		table.add_column("Last Active")

		for s in sessions:
			table.add_row(str(s.session_id), s.session_name, s.session_type or "", str(s.last_active))
		console.print(table)

		session_id = Prompt.ask("Enter session ID to switch to")
		try:
			session_id = int(session_id)
			if any(s.session_id == session_id for s in sessions):
				chat_loop(session_id, user_id)
			else:
				console.print("[red]Invalid session ID.[/red]")
		except ValueError:
			console.print("[red]Please enter a valid session ID number.[/red]")

	elif choice == "2":
		start_chat_session(user_id)

def settings_menu(user_id):
	"""Settings and configuration menu"""
	console.print(Panel(
		"[bold cyan]Settings[/bold cyan]\n"
		"1. API Key Management\n"
		"2. Default Preferences\n"
		"3. Export/Import Data\n"
		"4. Back",
		title="Settings"
	))

	choice = Prompt.ask("Select option", choices=["1","2","3","4"])

	if choice == "1":
		api_key_menu()
	elif choice == "2":
		console.print("[yellow]Preferences coming soon![/yellow]")
	elif choice == "3":
		console.print("[yellow]Export/Import coming soon![/yellow]")

def api_key_menu():
	"""API key management menu"""
	from src.auth.encryption import get_api_key, store_api_key

	console.print(Panel(
		"[bold cyan]API Key Management[/bold cyan]\n"
		"1. Add/Update Groq API Key\n"
		"2. Add/Update OpenAI API Key\n"
		"3. Add/Update Anthropic API Key\n"
		"4. View Current Keys\n"
		"5. Back",
		title="API Keys"
	))

	choice = Prompt.ask("Select option", choices=["1","2","3","4","5"])

	if choice == "1":
		api_key = Prompt.ask("Enter Groq API key", password=True)
		store_api_key("groq", api_key)
		console.print("[green]Groq API key stored successfully![/green]")
	elif choice == "2":
		api_key = Prompt.ask("Enter OpenAI API key", password=True)
		store_api_key("openai", api_key)
		console.print("[green]OpenAI API key stored successfully![/green]")
	elif choice == "3":
		api_key = Prompt.ask("Enter Anthropic API key", password=True)
		store_api_key("anthropic", api_key)
		console.print("[green]Anthropic API key stored successfully![/green]")
	elif choice == "4":
		providers = ["groq", "openai", "anthropic", "cerebras", "google"]
		table = Table(title="API Key Status")
		table.add_column("Provider")
		table.add_column("Status")

		for provider in providers:
			key = get_api_key(provider)
			status = "✅ Configured" if key else "❌ Not set"
			table.add_row(provider.title(), status)
		console.print(table)

def view_sessions(user_id):
	sessions = get_sessions_by_user(user_id)
	table = Table(title="Sessions")
	table.add_column("ID")
	table.add_column("Name")
	table.add_column("Type")
	table.add_column("Last Active")
	for s in sessions:
		table.add_row(str(s.session_id), s.session_name, s.session_type or "", str(s.last_active))
	console.print(table)

def validate_api_keys_for_chat():
	"""Validate that at least one valid API key is configured before allowing chat creation."""
	from src.auth.encryption import get_api_key
	import os

	providers = ["groq", "openai", "anthropic", "cerebras", "google"]
	valid_providers = []

	for provider in providers:
		try:
			# Check encrypted key
			encrypted_key = get_api_key(provider)
			if encrypted_key and encrypted_key.strip() and len(encrypted_key.strip()) > 10:
				valid_providers.append(provider)
				continue

			# Check environment variable
			env_key = os.getenv(f'{provider.upper()}_API_KEY')
			if env_key and env_key.strip() and len(env_key.strip()) > 10:
				valid_providers.append(provider)
		except Exception:
			# If decryption fails, the key is invalid
			continue

	return valid_providers

def require_api_keys_for_chat():
	"""Check for valid API keys and redirect to configuration if none found."""
	valid_providers = validate_api_keys_for_chat()

	if not valid_providers:
		console.print("\n[red]❌ No valid API keys configured[/red]")
		console.print("[yellow]📝 Please configure API keys before starting a chat[/yellow]")
		console.print("[dim]   AI responses require at least one valid API key[/dim]")

		# Offer to configure API keys
		configure_now = Prompt.ask("\nWould you like to configure API keys now?", choices=["y", "n"], default="y")

		if configure_now.lower() == "y":
			api_key_menu()
			# Re-check after configuration
			valid_providers = validate_api_keys_for_chat()
			if not valid_providers:
				console.print("[red]❌ Still no valid API keys configured. Cannot start chat.[/red]")
				return False
			else:
				console.print(f"[green]✅ API keys configured for: {', '.join(valid_providers)}[/green]")
				return True
		else:
			console.print("[yellow]⚠️  Cannot start chat without API keys.[/yellow]")
			return False
	else:
		console.print(f"[green]✅ Valid API keys found for: {', '.join(valid_providers)}[/green]")
		return True

def ensure_api_keys_configured():
	"""Ensure API keys are configured for LLM responses"""
	try:
		from src.auth.encryption import get_api_key, store_api_key
		import os

		# Check if any API key is available
		providers = ["groq", "openai", "anthropic", "cerebras", "google"]
		has_api_key = False

		for provider in providers:
			if get_api_key(provider) or os.getenv(f'{provider.upper()}_API_KEY'):
				has_api_key = True
				break

		if not has_api_key:
			console.print("[yellow]⚠️  No API keys found. AI responses may not work properly.[/yellow]")
			console.print("[dim]You can add API keys later through Settings > API Key Management[/dim]")

		# If GROQ API key is in environment, store it
		groq_env_key = os.getenv('GROQ_API_KEY')
		if groq_env_key and not get_api_key('groq'):
			store_api_key('groq', groq_env_key)
			console.print("[green]✅ GROQ API key detected and stored![/green]")

	except Exception as e:
		console.print(f"[red]Error checking API keys: {e}[/red]")
