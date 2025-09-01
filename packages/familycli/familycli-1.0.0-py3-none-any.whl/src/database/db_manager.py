
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError
from .models import Base
from sqlalchemy.pool import NullPool
from src.config.config_manager import ConfigManager

class DatabaseManager:
	"""
	Production-grade database manager with connection pooling, batch commit, and config integration.
	Usage:
		db = DatabaseManager()
		session = db.get_session()
		...
		db.bulk_commit([obj1, obj2])
		db.close()
	"""
	def __init__(self, db_url=None, pool_size=None, max_overflow=None):
		config = ConfigManager().load('db_manager')
		if db_url is None:
			db_url = config.get('db_url', self._get_default_db_url())
		pool_size = pool_size if pool_size is not None else int(config.get('pool_size', 5))
		max_overflow = max_overflow if max_overflow is not None else int(config.get('max_overflow', 10))
		from sqlalchemy.pool import QueuePool
		self.engine = create_engine(
			db_url,
			poolclass=QueuePool,
			pool_size=pool_size,
			max_overflow=max_overflow,
			future=True
		)
		self.SessionLocal = scoped_session(sessionmaker(bind=self.engine, autoflush=False, autocommit=False, future=True))

		# Automatically create tables if they don't exist
		self.create_all_tables()
	def bulk_commit(self, objects):
		"""
		Commit a batch of ORM objects efficiently.
		Args:
			objects (list): List of SQLAlchemy ORM objects to add and commit.
		"""
		session = self.get_session()
		try:
			session.add_all(objects)
			session.commit()
		except SQLAlchemyError as e:
			session.rollback()
			print(f"[DB ERROR] Bulk commit failed: {e}")
			raise
		finally:
			session.close()

	def _get_default_db_url(self):
		user_dir = os.path.expanduser('~/.familyai')
		os.makedirs(user_dir, exist_ok=True)
		db_path = os.getenv('FAMILYCLI_DB_PATH', os.path.join(user_dir, 'familycli.db'))
		return f'sqlite:///{db_path}'

	def create_all_tables(self):
		try:
			Base.metadata.create_all(self.engine)
		except SQLAlchemyError as e:
			print(f"[DB ERROR] Failed to create tables: {e}")
			raise

	def drop_all_tables(self):
		try:
			Base.metadata.drop_all(self.engine)
		except SQLAlchemyError as e:
			print(f"[DB ERROR] Failed to drop tables: {e}")
			raise

	def get_session(self):
		return self.SessionLocal()

	def close(self):
		self.SessionLocal.remove()
		self.engine.dispose()

# Utility for CLI/database initialization
def initialize_database():
	"""
	Initialize the database and create all tables. Use at app startup.
	"""
	db = DatabaseManager()
	db.create_all_tables()
	db.close()
