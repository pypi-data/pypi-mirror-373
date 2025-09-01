"""
Scene Manager for v1.1
Handles storytelling scenes and multi-persona roleplay.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.exc import SQLAlchemyError
from familycli.database.db_manager import DatabaseManager
from familycli.database.models import Scene, Persona
from familycli.chat.chat_engine import ChatEngine

logger = logging.getLogger(__name__)

class SceneManager:
    """Manages storytelling scenes and multi-persona interactions."""

    def __init__(self):
        self.db = DatabaseManager()
        self.chat_engine = ChatEngine()

    def create_scene(self, user_id: int, scene_name: str, description: str,
                    participating_personas: List[int]) -> Optional[int]:
        """Create a new scene with participating personas."""
        session = self.db.get_session()
        try:
            # Verify all personas exist and belong to user
            personas = session.query(Persona).filter(
                Persona.user_id == user_id,
                Persona.persona_id.in_(participating_personas),
                Persona.active == True
            ).all()

            if len(personas) != len(participating_personas):
                logger.error("Some personas not found or inactive")
                return None

            scene = Scene(
                user_id=user_id,
                scene_name=scene_name,
                description=description,
                participating_personas=participating_personas
            )
            session.add(scene)
            session.commit()
            session.refresh(scene)
            return scene.scene_id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to create scene: {e}")
            return None
        finally:
            session.close()

    def get_user_scenes(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all scenes for a user."""
        session = self.db.get_session()
        try:
            scenes = session.query(Scene).filter_by(user_id=user_id).all()

            result = []
            for scene in scenes:
                # Get persona details
                persona_ids = scene.participating_personas or []
                personas = session.query(Persona).filter(
                    Persona.persona_id.in_(persona_ids)
                ).all()

                result.append({
                    'scene_id': scene.scene_id,
                    'scene_name': scene.scene_name,
                    'description': scene.description,
                    'participating_personas': [{
                        'persona_id': p.persona_id,
                        'name': p.name,
                        'description': p.description
                    } for p in personas],
                    'created_at': scene.created_at.isoformat() if scene.created_at else None
                })

            return result
        finally:
            session.close()

    def start_scene_session(self, scene_id: int, user_id: int) -> Optional[int]:
        """Start a chat session for a scene."""
        from familycli.chat.session_manager import create_session

        session = self.db.get_session()
        try:
            scene = session.query(Scene).filter_by(scene_id=scene_id, user_id=user_id).first()
            if not scene:
                return None

            # Create a session for this scene
            session_name = f"Scene: {scene.scene_name}"
            chat_session = create_session(user_id, session_name, "scene")

            # Store scene context in session
            if chat_session:
                # You might want to add scene_id to session model in future
                pass

            return chat_session['session_id'] if chat_session else None
        finally:
            session.close()

    def get_builtin_scenes(self) -> List[Dict[str, Any]]:
        """Get list of built-in scenes."""
        return [
            {
                'name': 'Family Dinner',
                'description': 'A lively family dinner where everyone shares stories and debates',
                'scenario': 'The family is gathered around the dinner table for a Sunday dinner. Everyone is sharing stories from their week and debating various topics.',
                'suggested_personas': ['Grandma Rose', 'Grandpa Joe', 'Mom Sarah', 'Dad Mike', 'Sister Emma', 'Brother Alex']
            },
            {
                'name': 'Game Night',
                'description': 'Family game night with board games and friendly competition',
                'scenario': 'The family is playing board games in the living room. There\'s friendly competition, laughter, and playful banter.',
                'suggested_personas': ['Dad Mike', 'Mom Sarah', 'Sister Emma', 'Brother Alex']
            },
            {
                'name': 'Holiday Preparation',
                'description': 'Preparing for a family holiday with cooking and decorating',
                'scenario': 'The family is preparing for a holiday celebration. Everyone is helping with cooking, decorating, and sharing holiday memories.',
                'suggested_personas': ['Grandma Rose', 'Mom Sarah', 'Sister Emma', 'Brother Alex']
            },
            {
                'name': 'Backyard BBQ',
                'description': 'A casual backyard barbecue with outdoor activities',
                'scenario': 'The family is having a barbecue in the backyard. People are grilling, playing games, and enjoying the outdoors.',
                'suggested_personas': ['Grandpa Joe', 'Dad Mike', 'Brother Alex']
            },
            {
                'name': 'Movie Night',
                'description': 'Family movie night with popcorn and discussions',
                'scenario': 'The family is watching a movie together. Everyone has opinions about the film and shares related stories.',
                'suggested_personas': ['Mom Sarah', 'Dad Mike', 'Sister Emma', 'Brother Alex']
            },
            {
                'name': 'Study Session',
                'description': 'Helping with homework and learning together',
                'scenario': 'The kids are studying for school. Family members are helping with homework and sharing knowledge.',
                'suggested_personas': ['Grandma Rose', 'Grandpa Joe', 'Mom Sarah', 'Dad Mike']
            }
        ]

    def create_builtin_scene(self, scene_name: str, user_id: int) -> Optional[int]:
        """Create a built-in scene with appropriate personas."""
        builtin_scenes = {scene['name']: scene for scene in self.get_builtin_scenes()}

        if scene_name not in builtin_scenes:
            logger.error(f"Built-in scene '{scene_name}' not found")
            return None

        scene_data = builtin_scenes[scene_name]

        # Find personas that match the suggested names
        session = self.db.get_session()
        try:
            suggested_names = scene_data['suggested_personas']
            personas = session.query(Persona).filter(
                Persona.user_id == user_id,
                Persona.name.in_(suggested_names),
                Persona.active == True
            ).all()

            if not personas:
                logger.error(f"No matching personas found for scene '{scene_name}'")
                return None

            persona_ids = [p.persona_id for p in personas]

            return self.create_scene(
                user_id=user_id,
                scene_name=scene_name,
                description=scene_data['description'],
                participating_personas=persona_ids
            )
        finally:
            session.close()

    def get_scene_context(self, scene_id: int) -> Optional[Dict[str, Any]]:
        """Get context information for a scene."""
        session = self.db.get_session()
        try:
            scene = session.query(Scene).filter_by(scene_id=scene_id).first()
            if not scene:
                return None

            # Get participating personas
            persona_ids = scene.participating_personas or []
            personas = session.query(Persona).filter(
                Persona.persona_id.in_(persona_ids)
            ).all()

            # Get built-in scene data if it matches
            builtin_scenes = self.get_builtin_scenes()
            builtin_data = None
            for bs in builtin_scenes:
                if bs['name'] == scene.scene_name:
                    builtin_data = bs
                    break

            return {
                'scene_id': scene.scene_id,
                'scene_name': scene.scene_name,
                'description': scene.description,
                'scenario': builtin_data['scenario'] if builtin_data else scene.description,
                'participating_personas': [{
                    'persona_id': p.persona_id,
                    'name': p.name,
                    'description': p.description,
                    'personality_traits': p.personality_traits,
                    'tone': p.tone
                } for p in personas]
            }
        finally:
            session.close()

    def generate_scene_introduction(self, scene_context: Dict[str, Any]) -> str:
        """Generate an introduction message for the scene."""
        scene_name = scene_context['scene_name']
        scenario = scene_context['scenario']
        personas = scene_context['participating_personas']

        persona_names = [p['name'] for p in personas]

        introduction = f"""🌟 Welcome to the {scene_name} scene! 🌟

{scenario}

👥 Participating family members: {', '.join(persona_names)}

You can now chat naturally with the family in this scene setting. The AI family members will respond in character, staying true to the scene and their personalities.

Type your message to begin the scene, or use these commands:
• /scene_info - Show scene details
• /switch_persona - Talk to a specific family member
• /end_scene - Exit the scene

Start the conversation!"""

        return introduction

    def get_scene_suggestions(self, user_id: int) -> List[str]:
        """Get scene suggestions based on available personas."""
        session = self.db.get_session()
        try:
            # Get user's personas
            personas = session.query(Persona).filter_by(user_id=user_id, active=True).all()
            persona_names = [p.name.lower() for p in personas]

            suggestions = []

            # Check for family dinner scene
            family_keywords = ['grandma', 'grandpa', 'mom', 'dad', 'sister', 'brother']
            if any(keyword in name for keyword in family_keywords for name in persona_names):
                suggestions.append("Family Dinner - Perfect for your family setup!")

            # Check for game night
            if any(word in name for word in ['dad', 'brother', 'sister'] for name in persona_names):
                suggestions.append("Game Night - Great for competitive family fun!")

            # Check for study session
            if any(word in name for word in ['mom', 'dad', 'grandma', 'grandpa'] for name in persona_names):
                suggestions.append("Study Session - Educational family time!")

            return suggestions if suggestions else ["Try creating some family members first!"]

        finally:
            session.close()

    def delete_scene(self, scene_id: int, user_id: int) -> bool:
        """Delete a scene."""
        session = self.db.get_session()
        try:
            scene = session.query(Scene).filter_by(scene_id=scene_id, user_id=user_id).first()
            if not scene:
                return False

            session.delete(scene)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to delete scene: {e}")
            return False
        finally:
            session.close()
