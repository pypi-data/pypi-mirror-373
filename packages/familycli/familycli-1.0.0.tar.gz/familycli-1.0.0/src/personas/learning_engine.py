
from sqlalchemy.exc import SQLAlchemyError
from src.database.db_manager import DatabaseManager
from src.database.models import LearningData


def add_learning_data(persona_id, interaction_context, user_feedback=None, updated_instructions=None):
	db = DatabaseManager()
	session = db.get_session()
	try:
		# Analyze conversation context for personality evolution
		evolution = analyze_conversation_for_evolution(interaction_context, user_feedback)
		learning = LearningData(
			persona_id=persona_id,
			interaction_context=interaction_context,
			user_feedback=user_feedback,
			updated_instructions=updated_instructions or evolution
		)
		session.add(learning)
		session.commit()
		return learning
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()

def analyze_conversation_for_evolution(context, feedback):
	# Production-grade: Use LLM to analyze and evolve persona instructions
	from src.llm.universal_llm_manager import UniversalLLMManager
	import asyncio
	llm_manager = UniversalLLMManager()
	prompt = f"Analyze this conversation context and feedback. Suggest updated instructions for the persona to improve responses.\nContext: {context}\nFeedback: {feedback}"
	try:
		result = asyncio.run(llm_manager.route_request_to_provider(
			llm_manager.default_provider,
			[{"role": "user", "content": prompt}],
			stream=False
		))
		return result.strip()
	except Exception:
		return None


def get_learning_data_for_persona(persona_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		# Context memory: return sorted learning data for persona
		return session.query(LearningData).filter_by(persona_id=persona_id).order_by(LearningData.learning_id.desc()).all()
	finally:
		session.close()

def update_learning_data(learning_id, **kwargs):
	db = DatabaseManager()
	session = db.get_session()
	try:
		learning = session.query(LearningData).filter_by(learning_id=learning_id).first()
		if not learning:
			raise ValueError('Learning data not found.')
		for key, value in kwargs.items():
			if hasattr(learning, key):
				setattr(learning, key, value)
		session.commit()
		return learning
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()
