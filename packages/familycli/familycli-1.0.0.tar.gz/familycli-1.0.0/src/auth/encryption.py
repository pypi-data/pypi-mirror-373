
import os
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet, InvalidToken
import bcrypt

_USER_DIR = os.path.expanduser('~/.familyai')
os.makedirs(_USER_DIR, exist_ok=True)
_KEY_PATH = os.path.join(_USER_DIR, 'encryption.key')
_API_KEY_STORE = os.path.join(_USER_DIR, 'api_keys.json')
import json
def store_api_key(provider: str, api_key: str):
	"""
	Hash and securely store API key for a provider in api_keys.json.
	"""
	encrypted = encrypt_api_key(api_key)
	if os.path.exists(_API_KEY_STORE):
		with open(_API_KEY_STORE, 'r') as f:
			keys = json.load(f)
	else:
		keys = {}
	keys[provider] = encrypted
	with open(_API_KEY_STORE, 'w') as f:
		json.dump(keys, f)

def get_api_key(provider: str):
	"""
	Retrieve and decrypt API key for a provider from api_keys.json.
	"""
	if not os.path.exists(_API_KEY_STORE):
		return None
	with open(_API_KEY_STORE, 'r') as f:
		keys = json.load(f)
	token = keys.get(provider)
	if not token:
		return None
	return decrypt_api_key(token)

def _get_or_create_key():
	if not os.path.exists(_KEY_PATH):
		key = Fernet.generate_key()
		os.makedirs(os.path.dirname(_KEY_PATH), exist_ok=True)
		with open(_KEY_PATH, 'wb') as f:
			f.write(key)
	else:
		with open(_KEY_PATH, 'rb') as f:
			key = f.read()
	return key

def get_fernet():
	key = _get_or_create_key()
	return Fernet(key)

def hash_password(password: str) -> str:
	salt = bcrypt.gensalt()
	hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
	return hashed.decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
	return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def encrypt_api_key(api_key: str) -> str:
	f = get_fernet()
	token = f.encrypt(api_key.encode('utf-8'))
	return token.decode('utf-8')

def decrypt_api_key(token: str) -> str:
	f = get_fernet()
	try:
		return f.decrypt(token.encode('utf-8')).decode('utf-8')
	except InvalidToken:
		raise ValueError('Invalid encryption token or key.')
