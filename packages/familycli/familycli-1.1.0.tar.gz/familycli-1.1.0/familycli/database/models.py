from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
	__tablename__ = 'users'
	user_id = Column(Integer, primary_key=True)
	username = Column(String(64), unique=True, nullable=False)
	password_hash = Column(String(128), nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow)
	last_login = Column(DateTime)
	personas = relationship('Persona', back_populates='user')
	llm_configs = relationship('LLMConfig', back_populates='user')
	sessions = relationship('Session', back_populates='user')
	family_trees = relationship('FamilyTree', back_populates='user')
	feedback = relationship('UserFeedback', back_populates='user')
	scenes = relationship('Scene', back_populates='user')

class Persona(Base):
	__tablename__ = 'personas'
	persona_id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
	name = Column(String(64), nullable=False)
	age = Column(Integer)
	description = Column(Text)
	backstory = Column(Text)
	personality_traits = Column(JSON)
	tone = Column(String(32))
	language_prefs = Column(String(32))
	llm_provider = Column(String(32))
	llm_model = Column(String(64))
	response_instructions = Column(Text)
	# New fields for rich persona templates
	knowledge_domain = Column(String(64))
	quirks = Column(JSON)  # List of quirks like ["tells stories", "uses emojis"]
	memory_seeds = Column(JSON)  # Persistent memory seeds
	active = Column(Boolean, default=True)
	user = relationship('User', back_populates='personas')
	relationships1 = relationship('Relationship', back_populates='persona1', foreign_keys='Relationship.persona1_id')
	relationships2 = relationship('Relationship', back_populates='persona2', foreign_keys='Relationship.persona2_id')
	learning_data = relationship('LearningData', back_populates='persona')
	stream_sessions = relationship('StreamSession', back_populates='persona')
	memories = relationship('PersonaMemory', back_populates='persona')

class LLMConfig(Base):
	__tablename__ = 'llm_configs'
	config_id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
	provider_name = Column(String(32), nullable=False)
	base_url = Column(String(256))
	api_key_encrypted = Column(String(256))
	model_mappings = Column(JSON)
	default_params = Column(JSON)
	user = relationship('User', back_populates='llm_configs')

class Relationship(Base):
	__tablename__ = 'relationships'
	relationship_id = Column(Integer, primary_key=True)
	persona1_id = Column(Integer, ForeignKey('personas.persona_id'), nullable=False)
	persona2_id = Column(Integer, ForeignKey('personas.persona_id'), nullable=False)
	relationship_type = Column(String(32), nullable=False)
	relationship_details = Column(Text)
	persona1 = relationship('Persona', foreign_keys=[persona1_id], back_populates='relationships1')
	persona2 = relationship('Persona', foreign_keys=[persona2_id], back_populates='relationships2')

class Session(Base):
	__tablename__ = 'sessions'
	session_id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
	session_name = Column(String(128), nullable=False)
	session_type = Column(String(32))
	created_at = Column(DateTime, default=datetime.utcnow)
	last_active = Column(DateTime, default=datetime.utcnow)
	user = relationship('User', back_populates='sessions')
	messages = relationship('Message', back_populates='session')
	stream_sessions = relationship('StreamSession', back_populates='session')

class Message(Base):
	__tablename__ = 'messages'
	message_id = Column(Integer, primary_key=True)
	session_id = Column(Integer, ForeignKey('sessions.session_id'), nullable=False)
	sender_id = Column(Integer, ForeignKey('personas.persona_id'))
	message_content = Column(Text, nullable=False)
	timestamp = Column(DateTime, default=datetime.utcnow)
	message_type = Column(String(32), default='text')
	streaming_complete = Column(Boolean, default=True)
	session = relationship('Session', back_populates='messages')

class LearningData(Base):
	__tablename__ = 'learning_data'
	learning_id = Column(Integer, primary_key=True)
	persona_id = Column(Integer, ForeignKey('personas.persona_id'), nullable=False)
	interaction_context = Column(Text)
	user_feedback = Column(Text)
	updated_instructions = Column(Text)
	persona = relationship('Persona', back_populates='learning_data')

class StreamSession(Base):
	__tablename__ = 'stream_sessions'
	stream_id = Column(Integer, primary_key=True)
	session_id = Column(Integer, ForeignKey('sessions.session_id'), nullable=False)
	persona_id = Column(Integer, ForeignKey('personas.persona_id'), nullable=False)
	stream_status = Column(String(32))
	created_at = Column(DateTime, default=datetime.utcnow)
	completed_at = Column(DateTime)
	session = relationship('Session', back_populates='stream_sessions')
	persona = relationship('Persona', back_populates='stream_sessions')

class PersonaMemory(Base):
	__tablename__ = 'persona_memory'
	memory_id = Column(Integer, primary_key=True)
	persona_id = Column(Integer, ForeignKey('personas.persona_id'), nullable=False)
	memory_type = Column(String(32))  # 'conversation', 'fact', 'preference', 'relationship'
	memory_key = Column(String(128))  # e.g., 'favorite_food', 'last_topic'
	memory_value = Column(Text)
	confidence = Column(Integer, default=100)  # 0-100
	last_updated = Column(DateTime, default=datetime.utcnow)
	persona = relationship('Persona', back_populates='memories')

class FamilyTree(Base):
	__tablename__ = 'family_tree'
	tree_id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
	tree_name = Column(String(128), default="Family Tree")
	root_persona_id = Column(Integer, ForeignKey('personas.persona_id'))
	created_at = Column(DateTime, default=datetime.utcnow)
	user = relationship('User', back_populates='family_trees')
	root_persona = relationship('Persona', foreign_keys=[root_persona_id])

class PersonaPack(Base):
	__tablename__ = 'persona_packs'
	pack_id = Column(Integer, primary_key=True)
	pack_name = Column(String(128), nullable=False)
	description = Column(Text)
	author = Column(String(64))
	version = Column(String(16))
	created_at = Column(DateTime, default=datetime.utcnow)
	pack_data = Column(JSON)  # Contains personas, relationships, etc.

class UserFeedback(Base):
	__tablename__ = 'user_feedback'
	feedback_id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
	session_id = Column(Integer, ForeignKey('sessions.session_id'))
	message_id = Column(Integer, ForeignKey('messages.message_id'))
	rating = Column(Integer)  # 1-5 stars
	feedback_type = Column(String(32))  # 'thumbs_up', 'thumbs_down', 'flag'
	comment = Column(Text)
	created_at = Column(DateTime, default=datetime.utcnow)
	user = relationship('User', back_populates='feedback')
	session = relationship('Session', foreign_keys=[session_id])
	message = relationship('Message', foreign_keys=[message_id])

class Scene(Base):
	__tablename__ = 'scenes'
	scene_id = Column(Integer, primary_key=True)
	user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
	scene_name = Column(String(128), nullable=False)
	description = Column(Text)
	participating_personas = Column(JSON)  # List of persona IDs
	created_at = Column(DateTime, default=datetime.utcnow)
	user = relationship('User', back_populates='scenes')
