
from sqlalchemy.exc import SQLAlchemyError
from src.database.db_manager import DatabaseManager
from src.database.models import Persona
from src.config.user_config_manager import user_config
import logging

logger = logging.getLogger(__name__)

def load_default_personas_for_user(user_id):
    """Load default personas from user config and create them in database if they don't exist."""
    try:
        # Ensure user config is initialized
        user_config.initialize_default_config()

        # Load personas from user config
        personas_config = user_config.load_personas()
        default_personas = personas_config.get('personas', [])

        # Check which personas already exist for this user
        existing_personas = get_personas_by_user(user_id)
        existing_names = {p.name for p in existing_personas}

        created_personas = []

        # Create personas that don't exist yet
        for persona_config in default_personas:
            if not persona_config.get('active', True):
                continue

            persona_name = persona_config.get('name')
            if persona_name not in existing_names:
                try:
                    persona = create_persona(
                        user_id=user_id,
                        name=persona_config.get('name'),
                        age=persona_config.get('age'),
                        description=persona_config.get('description'),
                        backstory=persona_config.get('backstory'),
                        personality_traits=persona_config.get('personality_traits'),
                        tone=persona_config.get('tone'),
                        language_prefs=persona_config.get('language_prefs'),
                        llm_provider=persona_config.get('llm_provider'),
                        llm_model=persona_config.get('llm_model'),
                        response_instructions=persona_config.get('response_instructions')
                    )
                    created_personas.append(persona)
                    logger.info(f"Created default persona: {persona_name}")
                except Exception as e:
                    logger.error(f"Failed to create default persona {persona_name}: {e}")

        return created_personas

    except Exception as e:
        logger.error(f"Failed to load default personas for user {user_id}: {e}")
        return []

def create_persona(user_id, name, age=None, description=None, backstory=None, personality_traits=None, tone=None, language_prefs=None, llm_provider=None, llm_model=None, response_instructions=None):
	db = DatabaseManager()
	session = db.get_session()
	try:
		persona = Persona(
			user_id=user_id,
			name=name,
			age=age,
			description=description,
			backstory=backstory,
			personality_traits=personality_traits,
			tone=tone,
			language_prefs=language_prefs,
			llm_provider=llm_provider,
			llm_model=llm_model,
			response_instructions=response_instructions
		)
		session.add(persona)
		session.commit()
		# Refresh to ensure all attributes are loaded before session closes
		session.refresh(persona)
		persona_id = persona.persona_id
		persona_name = persona.name
		return persona
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()

def get_personas_by_user(user_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		return session.query(Persona).filter_by(user_id=user_id).all()
	finally:
		session.close()

def get_persona_by_id(persona_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		return session.query(Persona).filter_by(persona_id=persona_id).first()
	finally:
		session.close()

def update_persona(persona_id, **kwargs):
	db = DatabaseManager()
	session = db.get_session()
	try:
		persona = session.query(Persona).filter_by(persona_id=persona_id).first()
		if not persona:
			raise ValueError('Persona not found.')
		for key, value in kwargs.items():
			if hasattr(persona, key):
				setattr(persona, key, value)
		session.commit()
		return persona
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()

def get_persona_by_id(persona_id):
	"""Get a persona by its ID"""
	db = DatabaseManager()
	session = db.get_session()
	try:
		return session.query(Persona).filter_by(persona_id=persona_id).first()
	except SQLAlchemyError as e:
		raise e
	finally:
		session.close()

def validate_and_assign_llm_provider(persona_id, provider_name=None):
	"""Validate and assign LLM provider to a persona, ensuring the provider has valid API keys."""
	from src.ui.cli_interface import validate_api_keys_for_chat

	# Get available providers with valid API keys
	valid_providers = validate_api_keys_for_chat()

	if not valid_providers:
		raise ValueError("No valid API keys configured for any LLM provider")

	# If no specific provider requested, use the first valid one
	if not provider_name:
		provider_name = valid_providers[0]

	# Validate the requested provider has valid API keys
	if provider_name not in valid_providers:
		raise ValueError(f"Provider '{provider_name}' does not have valid API keys. Available providers: {', '.join(valid_providers)}")

	# Get default model for the provider
	provider_models = {
		"groq": "llama-3.1-8b-instant",
		"openai": "gpt-4o-mini",
		"anthropic": "claude-3-5-haiku-20241022",
		"cerebras": "llama3.1-8b",
		"google": "gemini-1.5-flash"
	}

	model = provider_models.get(provider_name, "default")

	# Update the persona
	try:
		update_persona(persona_id, llm_provider=provider_name, llm_model=model)
		return {"provider": provider_name, "model": model}
	except Exception as e:
		raise ValueError(f"Failed to update persona LLM provider: {e}")

def get_persona_llm_provider(persona_id):
	"""Get the assigned LLM provider for a persona."""
	persona = get_persona_by_id(persona_id)
	if not persona:
		raise ValueError("Persona not found")

	return {
		"provider": persona.llm_provider,
		"model": persona.llm_model
	}

def ensure_personas_have_valid_providers(user_id):
	"""Ensure all personas have valid LLM providers assigned."""
	from src.ui.cli_interface import validate_api_keys_for_chat

	personas = get_personas_by_user(user_id)
	valid_providers = validate_api_keys_for_chat()

	if not valid_providers:
		return False, "No valid API keys configured"

	updated_personas = []

	for persona in personas:
		# Check if persona has a valid provider assigned
		if not persona.llm_provider or persona.llm_provider not in valid_providers:
			try:
				# Assign the first valid provider
				result = validate_and_assign_llm_provider(persona.persona_id, valid_providers[0])
				updated_personas.append({
					"name": persona.name,
					"provider": result["provider"],
					"model": result["model"]
				})
			except Exception as e:
				print(f"Warning: Could not assign provider to {persona.name}: {e}")

	return True, updated_personas

def delete_persona(persona_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		persona = session.query(Persona).filter_by(persona_id=persona_id).first()
		if not persona:
			raise ValueError('Persona not found.')
		session.delete(persona)
		session.commit()
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()
