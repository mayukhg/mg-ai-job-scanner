import logging
import datetime
from pathlib import Path
from typing import List, Dict, Any

from ..analyzer.trending import TrendStorageManager
from ..analyzer.a2a_messaging import BaseAgent, AgentEventBus, AgentMessage
from .source_extractor import SourceExtractor
from .notebooklm_client import NotebookLMClient

logger = logging.getLogger("tutor.agent")

class AgentTutor(BaseAgent):
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
        event_bus: AgentEventBus,
        notebook_client: NotebookLMClient = None,
        source_extractor: SourceExtractor = None
    ):
        super().__init__("agent_tutor", event_bus)
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
                
                # D. Compile the brief
                brief_path = self._compile_notebook_ingestion_brief(topic_name, sources)
                
                # E. Generate Explainers (Audio, Mindmap, Video storyboard)
                assets = self.notebook_client.generate_multimedia_assets(notebook["notebook_id"], topic_name)
                
                # F. Persist learning workspace state to SQLite
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
                    "video_script": assets["video_script"],
                    "brief_path": str(brief_path)
                })
                
            except Exception as e:
                logger.error(f"Agent Tutor failed to compile resources for '{topic_name}': {e}", exc_info=True)
                
        # 3. Simulate email delivery trigger
        if created_assets:
            self._dispatch_study_plan_email(week_identifier, created_assets)
            
        return created_assets

    def _compile_notebook_ingestion_brief(self, topic_name: str, sources: List[Dict[str, Any]]) -> Path:
        """
        Compiles research sources, engineering blogs, and threat landscapes into a hyper-dense
        markdown brief formatted with structural anchors to maximize NotebookLM retrieval efficiency.
        """
        logger.info(f"Compiling NotebookLM Ingestion Brief for '{topic_name}'...")
        
        project_root = Path(__file__).resolve().parent.parent.parent
        briefs_dir = project_root / "data" / "tutor" / "briefs"
        briefs_dir.mkdir(parents=True, exist_ok=True)
        
        semantic_key = self.db.generate_semantic_key(topic_name)
        brief_path = briefs_dir / f"brief_{semantic_key}.md"
        
        brief_content = [
            f"# Ingestion Source Brief: {topic_name}",
            f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"\n## [EXECUTIVE SUMMARY]",
            f"This brief provides a foundational context sheet for continuous upskilling on **{topic_name}**.",
            f"It integrates leading scientific insights and production-grade developer paradigms.",
            f"\n## [CORE TECH STACK ANALYSIS]",
            f"Focus Area: {topic_name}",
            "Key Architectural Components:",
            "- Decoupled orchestrators and specialized execution lanes.",
            "- In-memory database persistence (SQLite schema models).",
            "- Strict validation routines and error wrappers.",
            f"\n## [SYSTEM DESIGN SCENARIOS]",
            "When defending systems designed using this stack, developers must anticipate:",
            "1. Token latency spikes under heavy recursive prompt iterations.",
            "2. State schema misalignment across stateless/ephemeral serverless boundaries.",
            "3. Credentials lifecycle leakage in untrusted CI pipelines.",
            f"\n## [ACADEMIC & OPEN-SOURCE RESEARCH SOURCES]"
        ]
        
        for idx, src in enumerate(sources):
            brief_content.extend([
                f"\n### Source {idx + 1}: {src['title']}",
                f"- **Reference URL**: {src['url']}",
                f"- **Insight Snippet**: {src['snippet']}"
            ])
            
        brief_content.append("\n---\n*Pre-structured for optimal NotebookLM Context-Window QA Retrieval by CIE Agent Tutor.*")
        
        try:
            with open(brief_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(brief_content))
            logger.info(f"Successfully compiled anchored brief at: {brief_path.name}")
        except Exception as e:
            logger.error(f"Failed to write upskilling brief file: {e}")
            
        return brief_path

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
                f"📄 INGESTION BRIEF (Local path): {item['brief_path']}",
                f"🎙️ AUDIO OVERVIEW (Podcast): {item['audio_url']}",
                f"📊 MERMAID MINDMAP DIAGRAM:\n{item['mindmap']}\n",
                f"--------------------------------------------------------------------------------"
            ])
            
        body_lines.append("\nKeep learning, keep engineering!\n— Agent Tutor")
        logger.info("Successfully simulated upskilling email dispatch.")
        logger.debug("\n".join(body_lines))

    def on_message(self, message: AgentMessage):
        logger.info(f"[{self.agent_id}] Received A2A event: '{message.event_type}' from '{message.sender_id}'")
        if message.event_type == "UPSKILLING_REQUIRED":
            topic = message.payload.get("topic")
            logger.info(f"[{self.agent_id}] REACTIVE TRIGGER: Compiling upskilling brief for target topic: '{topic}' due to assessment score...")
            
            try:
                sources = self.extractor.extract_sources(topic)
                brief_path = self._compile_notebook_ingestion_brief(topic, sources)
                logger.info(f"[{self.agent_id}] Reactive brief successfully generated at: {brief_path.name}")
                
                # Direct message to Portfolio Architect to build TDD workspace
                self.send_message(
                    recipient_id="agent_portfolio_architect",
                    event_type="UPSKILLING_BRIEF_COMPILED",
                    payload={"topic": topic, "brief_path": str(brief_path)}
                )
            except Exception as e:
                logger.error(f"[{self.agent_id}] Failed reactive upskilling: {e}")
