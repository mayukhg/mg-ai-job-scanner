import os
import sqlite3
import json
import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Tuple

logger = logging.getLogger("analyzer.trending")

class TrendStorageManager:
    """
    Manages persistence, versioning, and relational mapping of weekly job
    market trending topics and generated learning assets inside SQLite.
    """
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        # Ensure target data directories exist
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize_database()

    def _get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def _initialize_database(self):
        """Initializes tables for versioned trending topics and generated notebooks."""
        logger.info(f"Initializing sqlite database at {self.db_path}...")
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Create trending_topics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS trending_topics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week_identifier TEXT NOT NULL,
                    topic_name TEXT UNIQUE NOT NULL,
                    semantic_key TEXT UNIQUE NOT NULL,
                    importance_score REAL,
                    source_job_urls TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # 2. Create generated_notebooks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS generated_notebooks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic_name TEXT NOT NULL,
                    notebook_id TEXT NOT NULL,
                    notebook_url TEXT NOT NULL,
                    audio_explainer_url TEXT,
                    mindmap_mermaid TEXT,
                    video_script TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(topic_name) REFERENCES trending_topics(topic_name)
                );
            """)
            conn.commit()

    def generate_semantic_key(self, topic: str) -> str:
        """Normalizes topic strings to ensure robust deduplication."""
        # Convert to lowercase, remove punctuation/whitespaces, replace with single underscore
        normalized = topic.lower().strip()
        normalized = re.sub(r'[^a-z0-9\s-]', '', normalized)
        normalized = re.sub(r'[\s-]+', '_', normalized)
        return normalized

    def save_weekly_trends(self, week_identifier: str, extracted_themes: Dict[str, Any], job_urls: List[str] = None) -> List[str]:
        """
        Ingests extracted themes (keywords/skills), processes them into versioned 
        trending topics, and stores new distinct topics in SQLite.
        """
        urls_json = json.dumps(job_urls or [])
        inserted_topics = []
        
        # We look for keywords/skills that represent target study topics
        candidates = extracted_themes.get("keywords", []) + extracted_themes.get("skills", [])
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            for topic in candidates:
                topic_name = str(topic).strip()
                if not topic_name:
                    continue
                    
                semantic_key = self.generate_semantic_key(topic_name)
                
                try:
                    # Ingest topic. If it already exists, ignore (preserving original version)
                    cursor.execute("""
                        INSERT INTO trending_topics 
                        (week_identifier, topic_name, semantic_key, importance_score, source_job_urls)
                        VALUES (?, ?, ?, ?, ?)
                    """, (week_identifier, topic_name, semantic_key, 1.0, urls_json))
                    inserted_topics.append(topic_name)
                    logger.info(f"Successfully recorded new trending topic: '{topic_name}'")
                except sqlite3.IntegrityError:
                    # Already exists, which is perfectly normal for recurring keywords
                    logger.debug(f"Topic semantic key '{semantic_key}' already indexed. Skipping registration.")
                    
            conn.commit()
        return inserted_topics

    def get_unmapped_topics(self) -> List[Tuple[str, str]]:
        """
        Fetches versioned trending topics that have not yet had a NotebookLM 
        learning notebook generated (Deduplication Check).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.topic_name, t.semantic_key
                FROM trending_topics t
                LEFT JOIN generated_notebooks n ON t.topic_name = n.topic_name
                WHERE n.id IS NULL
            """)
            return cursor.fetchall()

    def record_notebook_generation(
        self, 
        topic_name: str, 
        notebook_id: str, 
        notebook_url: str, 
        audio_url: str = None, 
        mindmap: str = None, 
        video_script: str = None
    ) -> bool:
        """Saves the details of generated learning assets to establish state history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO generated_notebooks 
                    (topic_name, notebook_id, notebook_url, audio_explainer_url, mindmap_mermaid, video_script)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (topic_name, notebook_id, notebook_url, audio_url, mindmap, video_script))
                conn.commit()
                logger.info(f"Persisted generated notebook state for topic: '{topic_name}'")
                return True
            except sqlite3.IntegrityError as e:
                logger.error(f"Failed to record notebook for '{topic_name}': {e}")
                return False
