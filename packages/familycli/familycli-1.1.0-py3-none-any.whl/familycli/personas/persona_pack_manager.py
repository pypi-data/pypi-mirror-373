"""
Persona Pack Manager for v1.1
Handles installation and management of persona packs.
"""

import json
import os
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from sqlalchemy.exc import SQLAlchemyError
from familycli.database.db_manager import DatabaseManager
from familycli.database.models import PersonaPack, Persona
from familycli.personas.persona_manager import create_persona
from familycli.config.config_manager import UserDirectoryManager

logger = logging.getLogger(__name__)

class PersonaPackManager:
    """Manages persona packs for easy installation and sharing."""

    def __init__(self):
        self.db = DatabaseManager()
        self.user_dir_manager = UserDirectoryManager()
        self.packs_dir = Path(self.user_dir_manager.get_persona_packs_dir())
        self.packs_dir.mkdir(parents=True, exist_ok=True)

    def install_pack_from_file(self, pack_file_path: str, user_id: int) -> bool:
        """Install a persona pack from a JSON file."""
        try:
            with open(pack_file_path, 'r', encoding='utf-8') as f:
                pack_data = json.load(f)

            return self.install_pack(pack_data, user_id)
        except FileNotFoundError:
            logger.error(f"Pack file not found: {pack_file_path}")
            return False
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in pack file: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to install pack from file: {e}")
            return False

    def install_pack(self, pack_data: Dict[str, Any], user_id: int) -> bool:
        """Install a persona pack from data."""
        session = self.db.get_session()
        try:
            pack_name = pack_data.get('name', 'Unknown Pack')
            pack_description = pack_data.get('description', '')
            pack_author = pack_data.get('author', 'Unknown')
            pack_version = pack_data.get('version', '1.0')

            # Check if pack already exists
            existing_pack = session.query(PersonaPack).filter_by(
                pack_name=pack_name,
                author=pack_author
            ).first()

            if existing_pack:
                logger.info(f"Pack {pack_name} by {pack_author} already exists. Updating...")
                existing_pack.pack_data = pack_data
                existing_pack.version = pack_version
            else:
                # Create new pack
                pack = PersonaPack(
                    pack_name=pack_name,
                    description=pack_description,
                    author=pack_author,
                    version=pack_version,
                    pack_data=pack_data
                )
                session.add(pack)

            # Install personas from pack
            personas_data = pack_data.get('personas', [])
            installed_personas = []

            for persona_data in personas_data:
                try:
                    persona = create_persona(
                        user_id=user_id,
                        name=persona_data.get('name'),
                        age=persona_data.get('age'),
                        description=persona_data.get('description'),
                        backstory=persona_data.get('backstory'),
                        personality_traits=persona_data.get('personality_traits'),
                        tone=persona_data.get('tone'),
                        knowledge_domain=persona_data.get('knowledge_domain'),
                        quirks=persona_data.get('quirks'),
                        memory_seeds=persona_data.get('memory_seeds'),
                        llm_provider=persona_data.get('llm_provider'),
                        llm_model=persona_data.get('llm_model')
                    )
                    installed_personas.append(persona.name)
                    logger.info(f"Installed persona: {persona.name}")
                except Exception as e:
                    logger.error(f"Failed to install persona {persona_data.get('name')}: {e}")

            session.commit()

            if installed_personas:
                print(f"✅ Installed pack '{pack_name}' with {len(installed_personas)} personas:")
                for name in installed_personas:
                    print(f"  • {name}")
            else:
                print(f"⚠️  Pack '{pack_name}' installed but no personas were created.")

            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to install pack: {e}")
            return False
        finally:
            session.close()

    def create_pack_from_personas(self, user_id: int, persona_ids: List[int],
                                pack_name: str, description: str = "") -> Optional[str]:
        """Create a persona pack from existing personas."""
        session = self.db.get_session()
        try:
            personas = session.query(Persona).filter(
                Persona.user_id == user_id,
                Persona.persona_id.in_(persona_ids)
            ).all()

            if not personas:
                logger.error("No personas found to create pack")
                return None

            pack_data = {
                'name': pack_name,
                'description': description,
                'author': 'User',
                'version': '1.0',
                'created_at': str(session.execute("SELECT datetime('now')").scalar()),
                'personas': []
            }

            for persona in personas:
                persona_dict = {
                    'name': persona.name,
                    'age': persona.age,
                    'description': persona.description,
                    'backstory': persona.backstory,
                    'personality_traits': persona.personality_traits,
                    'tone': persona.tone,
                    'knowledge_domain': persona.knowledge_domain,
                    'quirks': persona.quirks,
                    'memory_seeds': persona.memory_seeds,
                    'llm_provider': persona.llm_provider,
                    'llm_model': persona.llm_model
                }
                pack_data['personas'].append(persona_dict)

            # Save pack to file
            pack_filename = f"{pack_name.lower().replace(' ', '_')}_v1.0.json"
            pack_file_path = self.packs_dir / pack_filename

            with open(pack_file_path, 'w', encoding='utf-8') as f:
                json.dump(pack_data, f, indent=2, ensure_ascii=False)

            # Also save to database
            db_pack = PersonaPack(
                pack_name=pack_name,
                description=description,
                author='User',
                version='1.0',
                pack_data=pack_data
            )
            session.add(db_pack)
            session.commit()

            return str(pack_file_path)
        except Exception as e:
            session.rollback()
            logger.error(f"Failed to create pack: {e}")
            return None
        finally:
            session.close()

    def list_installed_packs(self) -> List[Dict[str, Any]]:
        """List all installed persona packs."""
        session = self.db.get_session()
        try:
            packs = session.query(PersonaPack).all()
            return [{
                'pack_id': pack.pack_id,
                'name': pack.pack_name,
                'description': pack.description,
                'author': pack.author,
                'version': pack.version,
                'created_at': pack.created_at.isoformat() if pack.created_at else None
            } for pack in packs]
        finally:
            session.close()

    def get_pack_details(self, pack_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed information about a pack."""
        session = self.db.get_session()
        try:
            pack = session.query(PersonaPack).filter_by(pack_id=pack_id).first()
            if not pack:
                return None

            pack_data = pack.pack_data or {}
            personas = pack_data.get('personas', [])

            return {
                'pack_id': pack.pack_id,
                'name': pack.pack_name,
                'description': pack.description,
                'author': pack.author,
                'version': pack.version,
                'created_at': pack.created_at.isoformat() if pack.created_at else None,
                'total_personas': len(personas),
                'personas': [{
                    'name': p.get('name'),
                    'age': p.get('age'),
                    'description': p.get('description')
                } for p in personas]
            }
        finally:
            session.close()

    def export_pack(self, pack_id: int, export_path: Optional[str] = None) -> Optional[str]:
        """Export a pack to a JSON file."""
        session = self.db.get_session()
        try:
            pack = session.query(PersonaPack).filter_by(pack_id=pack_id).first()
            if not pack:
                return None

            if not export_path:
                export_path = self.packs_dir / f"{pack.pack_name.lower().replace(' ', '_')}_export.json"

            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(pack.pack_data, f, indent=2, ensure_ascii=False)

            return str(export_path)
        finally:
            session.close()

    def remove_pack(self, pack_id: int) -> bool:
        """Remove a persona pack."""
        session = self.db.get_session()
        try:
            pack = session.query(PersonaPack).filter_by(pack_id=pack_id).first()
            if not pack:
                return False

            session.delete(pack)
            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to remove pack: {e}")
            return False
        finally:
            session.close()

    def get_builtin_packs(self) -> List[Dict[str, Any]]:
        """Get list of built-in persona packs."""
        return [
            {
                'name': 'Family Classics',
                'description': 'Classic family members: Grandma, Grandpa, Mom, Dad, and kids',
                'personas': ['Grandma Rose', 'Grandpa Joe', 'Mom Sarah', 'Dad Mike', 'Sister Emma', 'Brother Alex']
            },
            {
                'name': 'Mythology Pack',
                'description': 'Greek mythology family: Zeus, Hera, Athena, Apollo',
                'personas': ['Zeus', 'Hera', 'Athena', 'Apollo', 'Ares', 'Artemis']
            },
            {
                'name': 'Anime Family',
                'description': 'Popular anime characters as family members',
                'personas': ['Naruto Uzumaki', 'Sakura Haruno', 'Sasuke Uchiha', 'Kakashi Hatake']
            },
            {
                'name': 'Superhero Family',
                'description': 'Superhero family members with powers and personalities',
                'personas': ['Captain Family', 'Wonder Mom', 'Flash Kid', 'Invisible Sister']
            }
        ]

    def install_builtin_pack(self, pack_name: str, user_id: int) -> bool:
        """Install a built-in persona pack."""
        builtin_packs = {
            'Family Classics': {
                'name': 'Family Classics',
                'description': 'Classic family members for everyday conversations',
                'author': 'Family AI CLI',
                'version': '1.0',
                'personas': [
                    {
                        'name': 'Grandma Rose',
                        'age': 75,
                        'description': 'Warm, caring grandmother who loves baking and storytelling',
                        'personality_traits': ['caring', 'wise', 'traditional', 'nurturing'],
                        'tone': 'gentle and warm',
                        'knowledge_domain': 'cooking and family history',
                        'quirks': ['tells family stories', 'offers homemade remedies', 'uses old-fashioned expressions'],
                        'memory_seeds': {'favorite_bake': 'chocolate chip cookies', 'family_tradition': 'Sunday dinners'}
                    },
                    {
                        'name': 'Grandpa Joe',
                        'age': 78,
                        'description': 'Wise grandfather who loves fixing things and sharing life lessons',
                        'personality_traits': ['wise', 'practical', 'patient', 'humorous'],
                        'tone': 'calm and experienced',
                        'knowledge_domain': 'repairs and history',
                        'quirks': ['tells dad jokes', 'fixes everything', 'shares war stories'],
                        'memory_seeds': {'favorite_tool': 'wrench', 'hobby': 'woodworking'}
                    },
                    {
                        'name': 'Mom Sarah',
                        'age': 42,
                        'description': 'Loving mother who balances work and family',
                        'personality_traits': ['caring', 'organized', 'supportive', 'empathetic'],
                        'tone': 'encouraging and understanding',
                        'knowledge_domain': 'child development and cooking',
                        'quirks': ['makes healthy snacks', 'gives life advice', 'worries about everything'],
                        'memory_seeds': {'favorite_meal': 'spaghetti', 'family_rule': 'homework before TV'}
                    },
                    {
                        'name': 'Dad Mike',
                        'age': 45,
                        'description': 'Fun-loving father who enjoys sports and outdoor activities',
                        'personality_traits': ['funny', 'active', 'protective', 'optimistic'],
                        'tone': 'enthusiastic and supportive',
                        'knowledge_domain': 'sports and outdoor activities',
                        'quirks': ['tells sports analogies', 'grills everything', 'sings off-key'],
                        'memory_seeds': {'favorite_sport': 'baseball', 'weekend_activity': 'family hikes'}
                    },
                    {
                        'name': 'Sister Emma',
                        'age': 16,
                        'description': 'Teenage sister who loves music and social media',
                        'personality_traits': ['creative', 'social', 'independent', 'funny'],
                        'tone': 'casual and trendy',
                        'knowledge_domain': 'music and pop culture',
                        'quirks': ['uses slang', 'takes selfies', 'listens to music constantly'],
                        'memory_seeds': {'favorite_artist': 'Taylor Swift', 'hobby': 'TikTok dancing'}
                    },
                    {
                        'name': 'Brother Alex',
                        'age': 14,
                        'description': 'Young brother who loves video games and science',
                        'personality_traits': ['curious', 'competitive', 'tech-savvy', 'energetic'],
                        'tone': 'excited and knowledgeable',
                        'knowledge_domain': 'video games and science',
                        'quirks': ['explains game strategies', 'builds model rockets', 'uses gaming lingo'],
                        'memory_seeds': {'favorite_game': 'Minecraft', 'dream_job': 'game developer'}
                    }
                ]
            }
        }

        pack_data = builtin_packs.get(pack_name)
        if not pack_data:
            logger.error(f"Built-in pack '{pack_name}' not found")
            return False

        return self.install_pack(pack_data, user_id)
