import logging
from typing import List, Dict, Any
from ..analyzer.trending import TrendStorageManager
from ..analyzer.a2a_messaging import BaseAgent, AgentEventBus, AgentMessage

logger = logging.getLogger("scraper.watchdog")

class AgentOpportunityWatchdog(BaseAgent):
    """
    Agent Opportunity Watchdog (Stealth Job Scraper) programmatically monitors public-facing ATS
    endpoints (Greenhouse/Lever) of selected, high-growth AI target organizations.
    It bypasses aggregate feeds, compares entries against sqlite indexing, and saves fresh items.
    """
    def __init__(self, db_manager: TrendStorageManager, event_bus: AgentEventBus, config: dict = None):
        super().__init__("agent_opportunity_watchdog", event_bus)
        self.db = db_manager
        self.config = config or {}
        self.target_companies = self.config.get("watchdog", {}).get(
            "target_companies", ["Anthropic", "OpenAI", "Cognition", "Perplexity", "LangChain"]
        )
        
    def check_stealth_opportunities(self) -> List[Dict[str, Any]]:
        """
        Polls configured corporate applicant endpoints. Deduplicates discoveries
        against the sqlite storage manager, committing only fresh listings.
        """
        logger.info(f"Initiating Stealth Job Watchdog scanning cycle for target companies: {self.target_companies}...")
        
        # 1. Fetch raw opportunities (Simulated/Mock ATS Endpoint Fetching)
        raw_opportunities = self._fetch_ats_endpoints()
        new_discoveries = []
        
        # 2. Iterate, deduplicate, and record to DB
        for opp in raw_opportunities:
            company = opp["company_name"]
            title = opp["job_title"]
            url = opp["job_url"]
            
            logger.info(f"Analyzing ATS job entry: '{title}' at {company} ({url})")
            
            # Persist to relational DB (SQLite will trigger unique key constraints if URL already exists)
            success = self.db.record_stealth_opportunity(
                company_name=company,
                job_title=title,
                job_url=url,
                raw_payload=f"ATS provider: {opp['provider']}"
            )
            
            if success:
                logger.info(f"NEW STEALTH DISCOVERY: '{title}' at {company} has been persisted!")
                new_discoveries.append(opp)
            else:
                logger.debug(f"Opportunity '{title}' at {company} is already cataloged. Skipping alert.")
                
        logger.info(f"Stealth job scanning cycle complete. Discovered {len(new_discoveries)} new opportunities.")
        return new_discoveries
        
    def _fetch_ats_endpoints(self) -> List[Dict[str, Any]]:
        """Retrieves raw payloads from Greenhouse/Lever mock structures."""
        # Simulated Greenhouse/Lever API responses reflecting the configured companies
        return [
            {
                "company_name": "Anthropic",
                "job_title": "Member of Technical Staff, Agentic Platforms",
                "job_url": "https://boards.greenhouse.io/anthropic/jobs/mock_mts_agentic_01",
                "provider": "greenhouse"
            },
            {
                "company_name": "Cognition",
                "job_title": "Senior AI Product Engineer",
                "job_url": "https://jobs.lever.co/cognition/mock_sr_pe_02",
                "provider": "lever"
            },
            {
                "company_name": "Perplexity",
                "job_title": "Product Manager, Search Agent Experience",
                "job_url": "https://boards.greenhouse.io/perplexity/jobs/mock_pm_search_03",
                "provider": "greenhouse"
            }
        ]

    def on_message(self, message: AgentMessage):
        logger.info(f"[{self.agent_id}] Received A2A event: '{message.event_type}' from '{message.sender_id}'")
