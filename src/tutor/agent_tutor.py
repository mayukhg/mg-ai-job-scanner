import logging
import datetime
from pathlib import Path
from typing import List, Dict, Any

from ..analyzer.trending import TrendStorageManager
from .source_extractor import SourceExtractor
from .notebooklm_client import NotebookLMClient

logger = logging.getLogger("tutor.agent")

class AgentTutor:
    """
    Agent Tutor coordinates the continuous upskilling workflow:
    1. Detects new weekly trending topics registered in SQLite.
    2. Runs deduplication.
    3. Crawls scholarly and developer sources.
    4. Deploys source-grounded Google Notebooks (NotebookLM / Gemini Caches).
    5. Coordinates the generation of explainers and mails out a Weekly Study Plan.
    """
    def __init__(
        self, 
        storage_manager: TrendStorageManager,
        notebook_client: NotebookLMClient = None,
        source_extractor: SourceExtractor = None
    ):
        self.db = storage_manager
        self.notebook_client = notebook_client or NotebookLMClient()
        self.extractor = source_extractor or SourceExtractor()
        
    def execute_weekly_upskilling(self, week_identifier: str) -> List[Dict[str, Any]]:
        """
        Runs the full upskilling pipeline: Ingestion ➔ Deduplication ➔ Source Loading ➔
        Asset Creation ➔ Storage Persistence.
        """
        logger.info(f"Initiating Agent Tutor execution cycle for week: {week_identifier}...")
        
        # 1. Fetch unmapped topics (Deduplication check)
        unmapped = self.db.get_unmapped_topics()
        if not unmapped:
            logger.info("Deduplication complete: No new learning topics detected this week. Learning state is synchronized.")
            return []
            
        logger.info(f"Found {len(unmapped)} new trending skills requiring upskilling notebooks.")
        created_assets = []
        
        # 2. Iterate and deploy
        for topic_name, semantic_key in unmapped:
            logger.info(f"Processing study workspace for topic: '{topic_name}'...")
            
            try:
                # A. Extract technical sources
                sources = self.extractor.extract_sources(topic_name)
                
                # B. Create Notebook <<Topic-Date>>
                date_str = datetime.datetime.now().strftime("%Y%m%d")
                notebook = self.notebook_client.create_notebook(topic_name, date_str)
                
                # C. Ingest sources into Notebook
                self.notebook_client.ingest_sources(notebook["notebook_id"], sources)
                
                # D. Generate Explainers (Audio, Mindmap, Video storyboard)
                assets = self.notebook_client.generate_multimedia_assets(notebook["notebook_id"], topic_name)
                
                # E. Persist learning workspace state to SQLite
                self.db.record_notebook_generation(
                    topic_name=topic_name,
                    notebook_id=notebook["notebook_id"],
                    notebook_url=notebook["notebook_url"],
                    audio_url=assets["audio_url"],
                    mindmap=assets["mindmap"],
                    video_script=assets["video_script"]
                )
                
                created_assets.append({
                    "topic": topic_name,
                    "notebook_url": notebook["notebook_url"],
                    "audio_url": assets["audio_url"],
                    "mindmap": assets["mindmap"],
                    "video_script": assets["video_script"]
                })
                
            except Exception as e:
                logger.error(f"Agent Tutor failed to compile resources for '{topic_name}': {e}", exc_info=True)
                
        # 3. Simulate email delivery trigger
        if created_assets:
            self._dispatch_study_plan_email(week_identifier, created_assets)
            
        return created_assets

    def _dispatch_study_plan_email(self, week_identifier: str, assets: List[Dict[str, Any]]):
        """Builds SMTP delivery notifications for the compiled weekly study plan."""
        subject = f"Your Study Plan for the week of {week_identifier}"
        logger.info(f"Composing notification message: '{subject}'...")
        
        body_lines = [
            f"Hello Mayukh,",
            f"\nHere is your custom continuous upskilling study plan built dynamically from your scanner:",
            f"--------------------------------------------------------------------------------"
        ]
        
        for item in assets:
            body_lines.extend([
                f"\n🎓 TOPIC: {item['topic']}",
                f"🔗 STUDY NOTEBOOK: {item['notebook_url']}",
                f"🎙️ AUDIO OVERVIEW (Podcast): {item['audio_url']}",
                f"📊 MERMAID MINDMAP DIAGRAM:\n{item['mindmap']}\n",
                f"--------------------------------------------------------------------------------"
            ])
            
        body_lines.append("\nKeep learning, keep engineering!\n— Agent Tutor")
        logger.info("Successfully simulated upskilling email dispatch.")
        logger.debug("\n".join(body_lines))
