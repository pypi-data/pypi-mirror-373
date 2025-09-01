
from sqlalchemy.exc import SQLAlchemyError
from src.database.db_manager import DatabaseManager
from src.database.models import Relationship

def create_relationship(persona1_id, persona2_id, relationship_type, relationship_details=None):
	db = DatabaseManager()
	session = db.get_session()
	try:
		rel = Relationship(
			persona1_id=persona1_id,
			persona2_id=persona2_id,
			relationship_type=relationship_type,
			relationship_details=relationship_details
		)
		session.add(rel)
		session.commit()
		return rel
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()

def get_relationships_for_persona(persona_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		return session.query(Relationship).filter((Relationship.persona1_id==persona_id)|(Relationship.persona2_id==persona_id)).all()
	finally:
		session.close()

def update_relationship(relationship_id, **kwargs):
	db = DatabaseManager()
	session = db.get_session()
	try:
		rel = session.query(Relationship).filter_by(relationship_id=relationship_id).first()
		if not rel:
			raise ValueError('Relationship not found.')
		for key, value in kwargs.items():
			if hasattr(rel, key):
				setattr(rel, key, value)
		session.commit()
		return rel
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()

def delete_relationship(relationship_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		rel = session.query(Relationship).filter_by(relationship_id=relationship_id).first()
		if not rel:
			raise ValueError('Relationship not found.')
		session.delete(rel)
		session.commit()
	except SQLAlchemyError as e:
		session.rollback()
		raise e
	finally:
		session.close()
