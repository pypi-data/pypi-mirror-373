
import asyncio
import logging
from src.database.db_manager import DatabaseManager
from src.database.models import StreamSession
from datetime import datetime, timezone
from sqlalchemy.exc import SQLAlchemyError
from typing import List, Dict, Any, AsyncGenerator

logger = logging.getLogger(__name__)

# Stream prioritization queue
class StreamPriorityQueue:
	def __init__(self):
		self.queue = asyncio.PriorityQueue()

	async def put(self, priority: int, stream_task: Any):
		await self.queue.put((priority, stream_task))

	async def get(self):
		return await self.queue.get()

	def empty(self):
		return self.queue.empty()

# Adaptive streaming and bandwidth optimization
async def adaptive_stream(tokens: List[str], min_delay=0.01, max_delay=0.2):
	for token in tokens:
		yield token
		await asyncio.sleep(min_delay + (max_delay - min_delay) * (len(token) / 10))


# Concurrent response handling with error handling
async def handle_concurrent_streams(streams: List[Dict[str, Any]], priority_map: Dict[int, int]):
	queue = StreamPriorityQueue()
	for stream in streams:
		priority = priority_map.get(stream['persona_id'], 10)
		await queue.put(priority, stream)
	results = []
	while not queue.empty():
		_, stream = await queue.get()
		try:
			async for token in adaptive_stream(stream['tokens']):
				results.append((stream['persona_id'], token))
		except Exception as e:
			results.append((stream['persona_id'], f"[STREAM ERROR] {e}"))
	return results

def start_stream(session_id, persona_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		stream = StreamSession(
			session_id=session_id,
			persona_id=persona_id,
			stream_status='active',
			created_at=datetime.now(timezone.utc)
		)
		session.add(stream)
		session.commit()
		return stream
	except SQLAlchemyError as e:
		session.rollback()
		raise RuntimeError(f"Failed to start stream: {e}")
	finally:
		session.close()

def complete_stream(stream_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		stream = session.query(StreamSession).filter_by(stream_id=stream_id).first()
		if not stream:
			raise ValueError('Stream session not found.')
		stream.stream_status = 'completed'
		stream.completed_at = datetime.now(timezone.utc)
		session.commit()
		return stream
	except SQLAlchemyError as e:
		session.rollback()
		raise RuntimeError(f"Failed to complete stream: {e}")
	finally:
		session.close()

def interrupt_stream(stream_id):
	db = DatabaseManager()
	session = db.get_session()
	try:
		stream = session.query(StreamSession).filter_by(stream_id=stream_id).first()
		if not stream:
			raise ValueError('Stream session not found.')
		stream.stream_status = 'interrupted'
		session.commit()
		return stream
	except SQLAlchemyError as e:
		session.rollback()
		raise RuntimeError(f"Failed to interrupt stream: {e}")
	finally:
		session.close()

# Stream recovery
def recover_interrupted_streams():
	db = DatabaseManager()
	session = db.get_session()
	try:
		interrupted = session.query(StreamSession).filter_by(stream_status='interrupted').all()
		for stream in interrupted:
			stream.stream_status = 'active'
		session.commit()
		return interrupted
	except SQLAlchemyError as e:
		session.rollback()
		raise RuntimeError(f"Failed to recover streams: {e}")
	finally:
		session.close()


