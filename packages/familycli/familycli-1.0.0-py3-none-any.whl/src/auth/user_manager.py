
import os
import getpass
import json
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from src.database.db_manager import DatabaseManager
from src.database.models import User
from .encryption import hash_password, verify_password

_CRED_DIR = os.path.expanduser('~/.familyai')
_SESSION_FILE = os.path.join(_CRED_DIR, 'session.json')

def _ensure_cred_dir():
	os.makedirs(_CRED_DIR, exist_ok=True)

def register_user(username: str, password: str):
	_ensure_cred_dir()
	db = DatabaseManager()
	session = db.get_session()
	try:
		if session.query(User).filter_by(username=username).first():
			raise ValueError('Username already exists.')
		user = User(
			username=username,
			password_hash=hash_password(password),
			created_at=datetime.utcnow(),
			last_login=datetime.utcnow()
		)
		session.add(user)
		session.commit()
		_save_session(user.user_id)
		return user
	except IntegrityError:
		session.rollback()
		raise ValueError('Username already exists.')
	finally:
		session.close()

def login_user(username: str, password: str):
	_ensure_cred_dir()
	db = DatabaseManager()
	session = db.get_session()
	try:
		user = session.query(User).filter_by(username=username).first()
		if not user or not verify_password(password, user.password_hash):
			raise ValueError('Invalid username or password.')
		user.last_login = datetime.utcnow()
		session.commit()
		_save_session(user.user_id)
		return user
	finally:
		session.close()

def _save_session(user_id: int):
	session_data = {
		'user_id': user_id,
		'login_time': datetime.utcnow().isoformat()
	}
	with open(_SESSION_FILE, 'w') as f:
		json.dump(session_data, f)

def get_logged_in_user():
	if not os.path.exists(_SESSION_FILE):
		return None
	with open(_SESSION_FILE, 'r') as f:
		session_data = json.load(f)
	db = DatabaseManager()
	session = db.get_session()
	try:
		user = session.query(User).filter_by(user_id=session_data['user_id']).first()
		return user
	finally:
		session.close()

def logout_user():
	if os.path.exists(_SESSION_FILE):
		os.remove(_SESSION_FILE)
