
import asyncio
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.exc import SQLAlchemyError
from src.database.db_manager import DatabaseManager
from src.database.models import Message, Persona, Session
from src.chat.llm_conversation_director import LLMConversationDirector
from src.personas.persona_manager import get_personas_by_user
from src.config.user_config_manager import user_config
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatEngine:
    """Production-grade chat engine with pure LLM-driven conversation management."""

    def __init__(self):
        self.conversation_director = LLMConversationDirector()
        self.db_manager = DatabaseManager()

    def send_message(self, session_id: int, sender_id: Optional[int], message_content: str,
                    message_type: str = 'text', streaming_complete: bool = True) -> Message:
        """Send a message to a chat session."""
        db = DatabaseManager()
        session = db.get_session()
        try:
            msg = Message(
                session_id=session_id,
                sender_id=sender_id,
                message_content=message_content,
                timestamp=datetime.utcnow(),
                message_type=message_type,
                streaming_complete=streaming_complete
            )
            session.add(msg)
            session.commit()
            session.refresh(msg)
            return msg
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to send message: {e}")
            raise RuntimeError(f"Failed to send message: {e}")
        except Exception as e:
            session.rollback()
            logger.error(f"Unexpected failure: {e}")
            raise RuntimeError(f"Unexpected failure: {e}")
        finally:
            session.close()

    def get_messages_for_session(self, session_id: int, limit: Optional[int] = None) -> List[Message]:
        """Get messages for a session with optional limit."""
        db = DatabaseManager()
        session = db.get_session()
        try:
            query = session.query(Message).filter_by(session_id=session_id).order_by(Message.timestamp)
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()

    def get_conversation_context(self, session_id: int, limit: int = 10) -> List[Dict[str, str]]:
        """Get recent conversation context for LLM."""
        messages = self.get_messages_for_session(session_id, limit)
        context = []

        for msg in messages[-limit:]:
            if msg.sender_id:
                # AI persona message
                context.append({
                    "role": "assistant",
                    "content": msg.message_content
                })
            else:
                # User message
                context.append({
                    "role": "user",
                    "content": msg.message_content
                })

        return context

    async def generate_ai_responses(self, session_id: int, user_message: str, user_id: int) -> List[str]:
        """
        Generate AI responses using pure LLM-driven conversation management.
        ALL decisions made by LLM - no hardcoded logic.
        """
        try:
            # Get personas for the user
            personas = get_personas_by_user(user_id)
            if not personas:
                logger.warning(f"No personas found for user {user_id}")
                return []

            # Get conversation history for context
            conversation_history = self.get_messages_for_session(session_id)

            # Build session context
            session_context = {
                'session_id': session_id,
                'user_id': user_id,
                'time_of_day': datetime.now().strftime("%H:%M"),
                'conversation_type': 'family_chat'
            }

            # Let LLM decide EVERYTHING about the conversation flow
            conversation_decision = await self.conversation_director.decide_conversation_flow(
                user_message, personas, conversation_history, session_context
            )

            # Generate responses based on LLM decisions
            responses = []
            responding_personas_info = conversation_decision.get("responding_personas", [])

            if not responding_personas_info:
                logger.warning("LLM decided no personas should respond")
                return []

            # Find actual persona objects for responders
            persona_map = {p.name: p for p in personas}

            # Generate responses for each selected persona
            for responder_info in responding_personas_info:
                persona_name = responder_info.get("name")
                persona = persona_map.get(persona_name)

                if not persona:
                    logger.warning(f"Persona {persona_name} not found")
                    continue

                try:
                    # Build enhanced conversation context for this response
                    conversation_context = {
                        'recent_history': self._format_recent_history(conversation_history),
                        'conversation_decision': conversation_decision,
                        'user_message': user_message,
                        'session_id': session_id,
                        'conversation_messages': self._format_conversation_for_llm(conversation_history),
                        'persona_name': persona.name
                    }

                    # Generate response using LLM
                    response_content = await self.conversation_director.generate_persona_response(
                        persona, user_message, responder_info, conversation_context
                    )

                    # Check if response is None (no API keys configured)
                    if response_content is None:
                        logger.warning(f"No API keys configured - skipping response from {persona.name}")
                        continue

                    # Save AI response to database
                    ai_message = self.send_message(
                        session_id=session_id,
                        sender_id=persona.persona_id,
                        message_content=response_content,
                        message_type='ai_response'
                    )

                    responses.append(f"{persona.name}: {response_content}")
                    logger.info(f"Generated response from {persona.name}: {response_content[:50]}...")

                except Exception as e:
                    logger.error(f"Failed to generate response for persona {persona.name}: {e}")
                    continue

            return responses

        except Exception as e:
            logger.error(f"Failed to generate AI responses: {e}")
            return []

    def _format_recent_history(self, messages: List[Message]) -> str:
        """Format recent conversation history for LLM context."""
        if not messages:
            return "No recent conversation history."

        # Get last 5 messages
        recent = messages[-5:]
        history_lines = []

        for msg in recent:
            if msg.sender_id:
                # AI persona message - need to get persona name
                try:
                    session = self.db_manager.get_session()
                    persona = session.query(Persona).filter_by(persona_id=msg.sender_id).first()
                    sender_name = persona.name if persona else "Family Member"
                    session.close()
                except:
                    sender_name = "Family Member"
            else:
                sender_name = "User"

            history_lines.append(f"{sender_name}: {msg.message_content}")

        return "\n".join(history_lines)

    def _format_conversation_for_llm(self, messages: List[Message]) -> List[Dict[str, str]]:
        """Format conversation history as LLM messages for better context."""
        if not messages:
            return []

        # Get last 10 messages for context
        recent = messages[-10:]
        llm_messages = []

        for msg in recent:
            if msg.sender_id:
                # AI persona message
                try:
                    session = self.db_manager.get_session()
                    persona = session.query(Persona).filter_by(persona_id=msg.sender_id).first()
                    persona_name = persona.name if persona else "Assistant"
                    session.close()
                except:
                    persona_name = "Assistant"

                llm_messages.append({
                    "role": "assistant",
                    "content": f"[{persona_name}]: {msg.message_content}"
                })
            else:
                # User message
                llm_messages.append({
                    "role": "user",
                    "content": msg.message_content
                })

        return llm_messages

    async def _select_responding_personas(self, personas: List[Persona], message: str, context: Dict) -> List[Persona]:
        """
        DEPRECATED: This method is replaced by LLMConversationDirector.
        Kept for backward compatibility only.
        """
        logger.warning("_select_responding_personas is deprecated. Use LLMConversationDirector instead.")

        # Simple fallback: return first persona
        return [personas[0]] if personas else []

    # DEPRECATED METHODS - Kept for backward compatibility only
    # All conversation logic is now handled by LLMConversationDirector



# Legacy function wrappers for backward compatibility
def send_message(session_id, sender_id, message_content, message_type='text', streaming_complete=True):
    """Legacy wrapper for send_message."""
    engine = ChatEngine()
    return engine.send_message(session_id, sender_id, message_content, message_type, streaming_complete)

def get_messages_for_session(session_id):
    """Legacy wrapper for get_messages_for_session."""
    engine = ChatEngine()
    return engine.get_messages_for_session(session_id)
