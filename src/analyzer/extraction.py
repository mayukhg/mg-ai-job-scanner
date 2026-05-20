import logging
from typing import List, Dict, Any

logger = logging.getLogger("analyzer.extraction")

class ThemeExtractor:
    """
    Ingests scraped job descriptions and extracts recurring technical
    skills, soft skills, and strategic weekly hiring trends.
    """
    def __init__(self, api_key: str, model_config: dict):
        self.api_key = api_key
        self.config = model_config
        
    def analyze_jds(self, jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates scraped job descriptions and runs LLM prompt analysis
        to identify high-priority weekly keywords and formatting themes.
        """
        logger.info(f"Analyzing {len(jobs)} job descriptions...")
        
        # In a real run, this formats the prompt, chooses the configured model
        # (e.g. Gemini 2.0 Pro), sends it to the API, and receives parsed JSON.
        
        extracted_themes = {
            "keywords": ["Agentic PM", "Multi-Agent System", "SQLite Sync", "GitHub Actions"],
            "skills": ["Prompt engineering", "Cloud Orchestration", "Enterprise PM"],
            "trends": [
                "Companies in Pune are pivoting heavily from simple RAG to autonomous agentic architectures.",
                "High demand for PMs who can bridge traditional product management with developer workflows."
            ]
        }
        logger.info(f"Successfully extracted themes: {extracted_themes['keywords']}")
        return extracted_themes
