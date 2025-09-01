"""
Persona Memory Manager for v1.1
Handles persistent memory, conversation continuity, and learning.
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from sqlalchemy.exc import SQLAlchemyError
from familycli.database.db_manager import DatabaseManager
from familycli.database.models import PersonaMemory, Persona

logger = logging.getLogger(__name__)

class MemoryManager:
    """Manages persona memory for conversation continuity and learning."""

    def __init__(self):
        self.db = DatabaseManager()

    def store_memory(self, persona_id: int, memory_type: str, memory_key: str,
                    memory_value: str, confidence: int = 100) -> bool:
        """Store a memory for a persona."""
        session = self.db.get_session()
        try:
            # Check if memory already exists
            existing = session.query(PersonaMemory).filter_by(
                persona_id=persona_id,
                memory_type=memory_type,
                memory_key=memory_key
            ).first()

            if existing:
                # Update existing memory
                existing.memory_value = memory_value
                existing.confidence = confidence
                existing.last_updated = datetime.utcnow()
            else:
                # Create new memory
                memory = PersonaMemory(
                    persona_id=persona_id,
                    memory_type=memory_type,
                    memory_key=memory_key,
                    memory_value=memory_value,
                    confidence=confidence
                )
                session.add(memory)

            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to store memory: {e}")
            return False
        finally:
            session.close()

    def retrieve_memory(self, persona_id: int, memory_type: str, memory_key: str) -> Optional[str]:
        """Retrieve a specific memory."""
        session = self.db.get_session()
        try:
            memory = session.query(PersonaMemory).filter_by(
                persona_id=persona_id,
                memory_type=memory_type,
                memory_key=memory_key
            ).first()

            return memory.memory_value if memory else None
        finally:
            session.close()

    def get_persona_memories(self, persona_id: int, memory_type: Optional[str] = None,
                           limit: int = 50) -> List[Dict[str, Any]]:
        """Get all memories for a persona, optionally filtered by type."""
        session = self.db.get_session()
        try:
            query = session.query(PersonaMemory).filter_by(persona_id=persona_id)

            if memory_type:
                query = query.filter_by(memory_type=memory_type)

            memories = query.order_by(PersonaMemory.last_updated.desc()).limit(limit).all()

            return [{
                'memory_id': m.memory_id,
                'type': m.memory_type,
                'key': m.memory_key,
                'value': m.memory_value,
                'confidence': m.confidence,
                'last_updated': m.last_updated.isoformat() if m.last_updated else None
            } for m in memories]
        finally:
            session.close()

    def update_memory_confidence(self, memory_id: int, confidence: int) -> bool:
        """Update confidence level of a memory."""
        session = self.db.get_session()
        try:
            memory = session.query(PersonaMemory).filter_by(memory_id=memory_id).first()
            if memory:
                memory.confidence = max(0, min(100, confidence))
                memory.last_updated = datetime.utcnow()
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to update memory confidence: {e}")
            return False
        finally:
            session.close()

    def delete_memory(self, memory_id: int) -> bool:
        """Delete a specific memory."""
        session = self.db.get_session()
        try:
            memory = session.query(PersonaMemory).filter_by(memory_id=memory_id).first()
            if memory:
                session.delete(memory)
                session.commit()
                return True
            return False
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to delete memory: {e}")
            return False
        finally:
            session.close()

    def learn_from_conversation(self, persona_id: int, user_message: str, persona_response: str) -> None:
        """Extract and store learnings from conversation."""
        try:
            # Extract preferences and facts from conversation
            learnings = self._extract_learnings(user_message, persona_response)

            for learning in learnings:
                self.store_memory(
                    persona_id=persona_id,
                    memory_type=learning['type'],
                    memory_key=learning['key'],
                    memory_value=learning['value'],
                    confidence=learning.get('confidence', 80)
                )
        except Exception as e:
            logger.error(f"Failed to learn from conversation: {e}")

    def _extract_learnings(self, user_message: str, persona_response: str) -> List[Dict[str, Any]]:
        """Extract learnings from conversation messages."""
        learnings = []

        # Simple pattern matching for common learnings
        user_lower = user_message.lower()
        response_lower = persona_response.lower()

        # Favorite foods
        if 'favorite food' in user_lower or 'love eating' in user_lower:
            # Extract food mentions
            foods = ['pizza', 'pasta', 'burger', 'chicken', 'rice', 'bread', 'cake', 'cookies']
            for food in foods:
                if food in user_lower:
                    learnings.append({
                        'type': 'preference',
                        'key': 'favorite_food',
                        'value': food,
                        'confidence': 90
                    })
                    break

        # Hobbies and interests
        if 'like to' in user_lower or 'enjoy' in user_lower or 'hobby' in user_lower:
            hobbies = ['reading', 'gaming', 'sports', 'music', 'drawing', 'cooking', 'dancing']
            for hobby in hobbies:
                if hobby in user_lower:
                    learnings.append({
                        'type': 'preference',
                        'key': 'hobby',
                        'value': hobby,
                        'confidence': 85
                    })
                    break

        # Emotional state
        if any(word in user_lower for word in ['sad', 'happy', 'excited', 'worried', 'angry']):
            emotion = 'happy' if 'happy' in user_lower or 'excited' in user_lower else \
                     'sad' if 'sad' in user_lower else \
                     'worried' if 'worried' in user_lower else \
                     'angry' if 'angry' in user_lower else 'neutral'

            learnings.append({
                'type': 'emotion',
                'key': 'current_mood',
                'value': emotion,
                'confidence': 75
            })

        return learnings

    def get_memory_context(self, persona_id: int, context_type: str = 'conversation') -> str:
        """Get relevant memory context for conversation."""
        memories = self.get_persona_memories(persona_id, memory_type=context_type, limit=10)

        if not memories:
            return ""

        context_parts = []
        for memory in memories:
            if memory['confidence'] > 70:  # Only high confidence memories
                context_parts.append(f"I remember you {memory['value']}")

        return " ".join(context_parts) if context_parts else ""

    def initialize_persona_memory_seeds(self, persona_id: int, memory_seeds: Dict[str, Any]) -> None:
        """Initialize persona with memory seeds from configuration."""
        for key, value in memory_seeds.items():
            self.store_memory(
                persona_id=persona_id,
                memory_type='seed',
                memory_key=key,
                memory_value=str(value),
                confidence=100
            )

    def get_memory_summary(self, persona_id: int) -> Dict[str, Any]:
        """Get a summary of persona's memory."""
        memories = self.get_persona_memories(persona_id)

        summary = {
            'total_memories': len(memories),
            'memory_types': {},
            'recent_memories': [],
            'high_confidence_memories': []
        }

        for memory in memories:
            mem_type = memory['type']
            summary['memory_types'][mem_type] = summary['memory_types'].get(mem_type, 0) + 1

            if memory['confidence'] >= 90:
                summary['high_confidence_memories'].append(memory)

        # Get 5 most recent memories
        summary['recent_memories'] = memories[:5] if memories else []

        return summary
