#!/usr/bin/env python3
"""
Database migration script for v1.1 features.
Adds support for memory, rich personas, family tree, and more.
"""

import sys
import os
from sqlalchemy import create_engine, text
from familycli.database.db_manager import DatabaseManager
from familycli.config.user_config_manager import user_config

def run_migration():
    """Run database migration for v1.1 features."""
    print("🔄 Running Family AI CLI v1.1 Database Migration...")

    try:
        # Get database path
        config = user_config.load_user_settings()
        db_path = config.get('database_path', '~/.familyai/familyai.db')
        db_path = os.path.expanduser(db_path)

        # Create engine
        engine = create_engine(f'sqlite:///{db_path}')

        with engine.connect() as conn:
            # Add new columns to personas table
            print("📝 Adding new columns to personas table...")

            # Check if personas table exists
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='personas'"))
            if not result.fetchone():
                print("  ⚠️  Personas table does not exist yet. Skipping column additions.")
                print("  ℹ️  Tables will be created on first run.")
            else:
                # Check if columns already exist
                result = conn.execute(text("PRAGMA table_info(personas)"))
                existing_columns = [row[1] for row in result.fetchall()]

                new_columns = [
                    ("knowledge_domain", "TEXT"),
                    ("quirks", "JSON"),
                    ("memory_seeds", "JSON"),
                    ("active", "BOOLEAN DEFAULT 1")
                ]

                for col_name, col_type in new_columns:
                    if col_name not in existing_columns:
                        try:
                            conn.execute(text(f"ALTER TABLE personas ADD COLUMN {col_name} {col_type}"))
                            print(f"  ✅ Added column: {col_name}")
                        except Exception as e:
                            print(f"  ⚠️  Could not add column {col_name}: {e}")
                            # Continue with other columns

            # Create new tables
            print("🏗️  Creating new tables...")

            # Persona Memory table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS persona_memory (
                    memory_id INTEGER PRIMARY KEY,
                    persona_id INTEGER NOT NULL,
                    memory_type TEXT,
                    memory_key TEXT,
                    memory_value TEXT,
                    confidence INTEGER DEFAULT 100,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (persona_id) REFERENCES personas (persona_id)
                )
            """))
            print("  ✅ Created persona_memory table")

            # Family Tree table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS family_tree (
                    tree_id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    tree_name TEXT DEFAULT 'Family Tree',
                    root_persona_id INTEGER,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (root_persona_id) REFERENCES personas (persona_id)
                )
            """))
            print("  ✅ Created family_tree table")

            # Persona Packs table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS persona_packs (
                    pack_id INTEGER PRIMARY KEY,
                    pack_name TEXT NOT NULL,
                    description TEXT,
                    author TEXT,
                    version TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    pack_data JSON
                )
            """))
            print("  ✅ Created persona_packs table")

            # User Feedback table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    feedback_id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    session_id INTEGER,
                    message_id INTEGER,
                    rating INTEGER,
                    feedback_type TEXT,
                    comment TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id),
                    FOREIGN KEY (session_id) REFERENCES sessions (session_id),
                    FOREIGN KEY (message_id) REFERENCES messages (message_id)
                )
            """))
            print("  ✅ Created user_feedback table")

            # Scenes table
            conn.execute(text("""
                CREATE TABLE IF NOT EXISTS scenes (
                    scene_id INTEGER PRIMARY KEY,
                    user_id INTEGER NOT NULL,
                    scene_name TEXT NOT NULL,
                    description TEXT,
                    participating_personas JSON,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """))
            print("  ✅ Created scenes table")

            # Update existing personas with default values
            print("🔄 Updating existing personas with default values...")
            
            # Check if personas table exists before updating
            result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='personas'"))
            if result.fetchone():
                try:
                    conn.execute(text("""
                        UPDATE personas
                        SET active = 1
                        WHERE active IS NULL
                    """))
                    print("  ✅ Updated existing personas")
                except Exception as e:
                    print(f"  ⚠️  Could not update personas: {e}")
            else:
                print("  ℹ️  Personas table does not exist yet. Skipping updates.")

            conn.commit()
            print("✅ Migration completed successfully!")
            print("🎉 Your database is now ready for Family AI CLI v1.1 features!")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
