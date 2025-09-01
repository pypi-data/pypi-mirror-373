
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
	user = relationship('User', back_populates='personas')
	relationships1 = relationship('Relationship', back_populates='persona1', foreign_keys='Relationship.persona1_id')
	relationships2 = relationship('Relationship', back_populates='persona2', foreign_keys='Relationship.persona2_id')
	learning_data = relationship('LearningData', back_populates='persona')
	stream_sessions = relationship('StreamSession', back_populates='persona')

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
