
from sqlalchemy.exc import SQLAlchemyError
from src.database.db_manager import DatabaseManager
from src.database.models import Session
from datetime import datetime

def create_session(user_id, session_name, session_type):
	db = DatabaseManager()
	session = db.get_session()
	try:
		chat_session = Session(
			user_id=user_id,
			session_name=session_name,
			session_type=session_type,
			created_at=datetime.utcnow(),
			last_active=datetime.utcnow()
		)
		session.add(chat_session)
		session.flush()
		session.refresh(chat_session)
		session.commit()
		# Access all needed attributes before closing
		result = {
			'session_id': chat_session.session_id,
			'session_name': chat_session.session_name,
			'session_type': chat_session.session_type,
			'created_at': chat_session.created_at,
			'last_active': chat_session.last_active
		}
		return result
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()

def get_sessions_by_user(user_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		return session.query(Session).filter_by(user_id=user_id).all()
	finally:
		session.close()

def update_session_activity(session_id):
	"""Update the last_active timestamp for a session"""
	db = DatabaseManager()
	session = db.get_session()
	try:
		chat_session = session.query(Session).filter_by(session_id=session_id).first()
		if chat_session:
			chat_session.last_active = datetime.utcnow()
			session.commit()
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()

def get_session_by_id(session_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		return session.query(Session).filter_by(session_id=session_id).first()
	finally:
		session.close()

def update_session(session_id, **kwargs):
	db = DatabaseManager()
	session = db.get_session()
	try:
		chat_session = session.query(Session).filter_by(session_id=session_id).first()
		if not chat_session:
			raise ValueError('Session not found.')
		for key, value in kwargs.items():
			if hasattr(chat_session, key):
				setattr(chat_session, key, value)
		chat_session.last_active = datetime.utcnow()
		session.commit()
		return chat_session
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()

def delete_session(session_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		chat_session = session.query(Session).filter_by(session_id=session_id).first()
		if not chat_session:
			raise ValueError('Session not found.')
		session.delete(chat_session)
		session.commit()
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()
