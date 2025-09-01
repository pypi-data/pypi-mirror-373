"""
Family Tree Manager for v1.1
Handles family tree visualization and relationships.
"""

import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from sqlalchemy.exc import SQLAlchemyError
from familycli.database.db_manager import DatabaseManager
from familycli.database.models import FamilyTree, Persona, Relationship

logger = logging.getLogger(__name__)

class FamilyTreeManager:
    """Manages family tree structure and visualization."""

    def __init__(self):
        self.db = DatabaseManager()

    def create_family_tree(self, user_id: int, tree_name: str = "Family Tree",
                          root_persona_id: Optional[int] = None) -> Optional[int]:
        """Create a new family tree."""
        session = self.db.get_session()
        try:
            tree = FamilyTree(
                user_id=user_id,
                tree_name=tree_name,
                root_persona_id=root_persona_id
            )
            session.add(tree)
            session.commit()
            session.refresh(tree)
            return tree.tree_id
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to create family tree: {e}")
            return None
        finally:
            session.close()

    def get_family_tree(self, user_id: int, tree_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get family tree structure."""
        session = self.db.get_session()
        try:
            if tree_id:
                tree = session.query(FamilyTree).filter_by(tree_id=tree_id, user_id=user_id).first()
            else:
                tree = session.query(FamilyTree).filter_by(user_id=user_id).first()

            if not tree:
                return None

            # Get all personas for this user
            personas = session.query(Persona).filter_by(user_id=user_id, active=True).all()

            # Get relationships
            relationships = session.query(Relationship).filter(
                (Relationship.persona1_id.in_([p.persona_id for p in personas])) |
                (Relationship.persona2_id.in_([p.persona_id for p in personas]))
            ).all()

            # Build tree structure
            tree_structure = self._build_tree_structure(personas, relationships, tree.root_persona_id)

            return {
                'tree_id': tree.tree_id,
                'tree_name': tree.tree_name,
                'root_persona_id': tree.root_persona_id,
                'structure': tree_structure,
                'total_members': len(personas)
            }
        finally:
            session.close()

    def _build_tree_structure(self, personas: List[Persona], relationships: List[Relationship],
                            root_persona_id: Optional[int] = None) -> Dict[str, Any]:
        """Build hierarchical tree structure from personas and relationships."""
        # Create persona lookup
        persona_dict = {p.persona_id: p for p in personas}

        # Create relationship lookup
        relationship_dict = {}
        for rel in relationships:
            if rel.persona1_id not in relationship_dict:
                relationship_dict[rel.persona1_id] = []
            if rel.persona2_id not in relationship_dict:
                relationship_dict[rel.persona2_id] = []

            relationship_dict[rel.persona1_id].append({
                'persona_id': rel.persona2_id,
                'relationship_type': rel.relationship_type,
                'details': rel.relationship_details
            })
            relationship_dict[rel.persona2_id].append({
                'persona_id': rel.persona1_id,
                'relationship_type': self._get_reverse_relationship(rel.relationship_type),
                'details': rel.relationship_details
            })

        # Find root if not specified
        if not root_persona_id:
            # Try to find a grandparent or oldest family member
            for persona in personas:
                if persona.age and persona.age > 60:
                    root_persona_id = persona.persona_id
                    break
            else:
                # Default to first persona
                root_persona_id = personas[0].persona_id if personas else None

        if not root_persona_id:
            return {'nodes': [], 'edges': []}

        # Build tree starting from root
        visited = set()
        nodes = []
        edges = []

        def build_subtree(persona_id: int, level: int = 0):
            if persona_id in visited:
                return
            visited.add(persona_id)

            persona = persona_dict.get(persona_id)
            if not persona:
                return

            # Add node
            nodes.append({
                'id': persona_id,
                'name': persona.name,
                'age': persona.age,
                'description': persona.description,
                'level': level,
                'emoji': self._get_persona_emoji(persona)
            })

            # Add edges to children/relatives
            if persona_id in relationship_dict:
                for rel in relationship_dict[persona_id]:
                    if rel['persona_id'] not in visited:
                        edges.append({
                            'from': persona_id,
                            'to': rel['persona_id'],
                            'relationship': rel['relationship_type'],
                            'details': rel['details']
                        })
                        build_subtree(rel['persona_id'], level + 1)

        build_subtree(root_persona_id)

        return {
            'nodes': nodes,
            'edges': edges
        }

    def _get_reverse_relationship(self, relationship_type: str) -> str:
        """Get the reverse relationship type."""
        reverse_map = {
            'parent': 'child',
            'child': 'parent',
            'spouse': 'spouse',
            'sibling': 'sibling',
            'grandparent': 'grandchild',
            'grandchild': 'grandparent',
            'aunt/uncle': 'niece/nephew',
            'niece/nephew': 'aunt/uncle',
            'cousin': 'cousin'
        }
        return reverse_map.get(relationship_type, relationship_type)

    def _get_persona_emoji(self, persona: Persona) -> str:
        """Get appropriate emoji for persona based on age and description."""
        if not persona.age:
            return "👤"

        if persona.age < 13:
            return "👶" if persona.age < 5 else "👦" if "boy" in (persona.description or "").lower() else "👧"
        elif persona.age < 20:
            return "👨‍🎓" if "boy" in (persona.description or "").lower() else "👩‍🎓"
        elif persona.age < 40:
            return "👨" if "dad" in (persona.name or "").lower() or "father" in (persona.description or "").lower() else "👩"
        elif persona.age < 60:
            return "👨‍💼" if "man" in (persona.description or "").lower() else "👩‍💼"
        else:
            return "👴" if "grandpa" in (persona.name or "").lower() else "👵"

    def display_tree_cli(self, tree_data: Dict[str, Any]) -> str:
        """Generate CLI tree display."""
        if not tree_data or 'structure' not in tree_data:
            return "No family tree data available."

        nodes = tree_data['structure']['nodes']
        edges = tree_data['structure']['edges']

        if not nodes:
            return "No family members found."

        # Group nodes by level
        levels = {}
        for node in nodes:
            level = node['level']
            if level not in levels:
                levels[level] = []
            levels[level].append(node)

        # Build tree display
        display_lines = []
        display_lines.append(f"👨‍👩‍👧‍👦 {tree_data['tree_name']}")
        display_lines.append("=" * 40)

        max_level = max(levels.keys()) if levels else 0

        for level in range(max_level + 1):
            if level not in levels:
                continue

            level_nodes = levels[level]
            level_line = ""

            for node in level_nodes:
                emoji = node['emoji']
                name = node['name']
                age = f" ({node['age']})" if node['age'] else ""
                level_line += f"{emoji} {name}{age}    "

            display_lines.append(level_line.rstrip())

            # Add relationship indicators
            if level < max_level:
                connectors = []
                for node in level_nodes:
                    # Find children
                    children = [e for e in edges if e['from'] == node['id']]
                    if children:
                        connectors.append("│" if len(children) > 1 else "├")
                    else:
                        connectors.append(" ")

                if any(c.strip() for c in connectors):
                    display_lines.append(" ".join(connectors))

        return "\n".join(display_lines)

    def add_relationship(self, persona1_id: int, persona2_id: int,
                        relationship_type: str, details: Optional[str] = None) -> bool:
        """Add a relationship between two personas."""
        session = self.db.get_session()
        try:
            # Check if relationship already exists
            existing = session.query(Relationship).filter(
                ((Relationship.persona1_id == persona1_id) & (Relationship.persona2_id == persona2_id)) |
                ((Relationship.persona1_id == persona2_id) & (Relationship.persona2_id == persona1_id))
            ).first()

            if existing:
                # Update existing relationship
                existing.relationship_type = relationship_type
                existing.relationship_details = details
            else:
                # Create new relationship
                relationship = Relationship(
                    persona1_id=persona1_id,
                    persona2_id=persona2_id,
                    relationship_type=relationship_type,
                    relationship_details=details
                )
                session.add(relationship)

            session.commit()
            return True
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to add relationship: {e}")
            return False
        finally:
            session.close()

    def get_persona_relationships(self, persona_id: int) -> List[Dict[str, Any]]:
        """Get all relationships for a persona."""
        session = self.db.get_session()
        try:
            # Get relationships where persona is persona1 or persona2
            relationships = session.query(Relationship).filter(
                (Relationship.persona1_id == persona_id) |
                (Relationship.persona2_id == persona_id)
            ).all()

            result = []
            for rel in relationships:
                other_persona_id = rel.persona2_id if rel.persona1_id == persona_id else rel.persona1_id
                other_persona = session.query(Persona).filter_by(persona_id=other_persona_id).first()

                if other_persona:
                    result.append({
                        'persona_id': other_persona.persona_id,
                        'name': other_persona.name,
                        'relationship_type': rel.relationship_type,
                        'details': rel.relationship_details
                    })

            return result
        finally:
            session.close()

    def auto_detect_relationships(self, user_id: int) -> int:
        """Automatically detect and create relationships based on persona names and descriptions."""
        session = self.db.get_session()
        try:
            personas = session.query(Persona).filter_by(user_id=user_id, active=True).all()

            relationships_created = 0

            # Simple name-based relationship detection
            for persona in personas:
                name_lower = persona.name.lower()
                description_lower = (persona.description or "").lower()

                # Detect grandparents
                if any(word in name_lower for word in ['grandpa', 'grandma', 'gramps', 'nana']):
                    # Find potential children (parents)
                    for other in personas:
                        if other.persona_id != persona.persona_id:
                            other_name = other.name.lower()
                            if any(word in other_name for word in ['mom', 'dad', 'mother', 'father', 'mama', 'papa']):
                                if self.add_relationship(persona.persona_id, other.persona_id, 'parent'):
                                    relationships_created += 1

                # Detect parents
                elif any(word in name_lower for word in ['mom', 'dad', 'mother', 'father', 'mama', 'papa']):
                    # Find potential children
                    for other in personas:
                        if other.persona_id != persona.persona_id:
                            other_name = other.name.lower()
                            if any(word in other_name for word in ['son', 'daughter', 'kid', 'child']):
                                if self.add_relationship(persona.persona_id, other.persona_id, 'parent'):
                                    relationships_created += 1

                # Detect siblings
                elif any(word in name_lower for word in ['brother', 'sister', 'sis', 'bro']):
                    for other in personas:
                        if other.persona_id != persona.persona_id:
                            other_name = other.name.lower()
                            if any(word in other_name for word in ['brother', 'sister', 'sis', 'bro']):
                                if self.add_relationship(persona.persona_id, other.persona_id, 'sibling'):
                                    relationships_created += 1

            session.commit()
            return relationships_created
        except SQLAlchemyError as e:
            session.rollback()
            logger.error(f"Failed to auto-detect relationships: {e}")
            return 0
        finally:
            session.close()
