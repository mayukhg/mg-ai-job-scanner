import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from ..analyzer.trending import TrendStorageManager
from ..analyzer.a2a_messaging import BaseAgent, AgentEventBus, AgentMessage

logger = logging.getLogger("interviewer.mock")

class AgentMockInterviewer(BaseAgent):
    """
    Agent Mock Interviewer (The Interview Coach) evaluates candidate readiness on trending skills.
    It compiles dynamic technical questions based on database trends and active resumes,
    stages simulated assessments, and stores formatted scorecards locally and in SQLite.
    """
    def __init__(self, db_manager: TrendStorageManager, event_bus: AgentEventBus, config: dict = None):
        super().__init__("agent_mock_interviewer", event_bus)
        self.db = db_manager
        self.config = config or {}
        self.difficulty = self.config.get("interviewer", {}).get("default_difficulty", "hard")
        self.scorecard_dir = Path(self.config.get("interviewer", {}).get(
            "scorecard_storage_path", "data/interviews/scorecards"
        ))
        
        # Ensure scorecard directories exist
        self.scorecard_dir.mkdir(parents=True, exist_ok=True)

    def conduct_mock_interview(self, week_identifier: str, interview_type: str = "system_design") -> Dict[str, Any]:
        """
        Gathers database trending skills and executes a tailored mock interview.
        Saves a physical evaluation scorecard and records session metadata in SQLite.
        """
        logger.info(f"Initiating Mock Interview dry-run session for week: {week_identifier} (Type: {interview_type})...")
        
        # 1. Fetch current trending skills to target from DB
        with self.db._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT topic_name FROM trending_topics ORDER BY created_at DESC LIMIT 3")
            rows = cursor.fetchall()
            
        target_skills = [row[0] for row in rows] if rows else ["LangGraph State Preservation", "SQLite Cloud State Sync"]
        logger.info(f"Targeting active trending skills for this evaluation: {target_skills}")
        
        # 2. Generate customized situational and system-design questions
        questionnaire = self._generate_tailored_questions(target_skills, interview_type)
        
        # 3. Simulate grading and scorecard creation (Dry Run Evaluation)
        readiness_score = 8.5  # Standard dry run readiness scale out of 10.0
        scorecard_filename = f"scorecard_{week_identifier.replace('-', '_')}_{interview_type}.md"
        scorecard_path = self.scorecard_dir / scorecard_filename
        
        # Write markdown scorecard to local filesystem
        self._write_markdown_scorecard(scorecard_path, week_identifier, interview_type, target_skills, questionnaire, readiness_score)
        
        # 4. Save metadata back to relational storage
        self.db.record_mock_interview(
            week_identifier=week_identifier,
            interview_type=interview_type,
            target_skills=target_skills,
            questionnaire=questionnaire,
            scorecard_path=str(scorecard_path),
            readiness_score=readiness_score
        )
        
        logger.info(f"Successfully finalized interview evaluation. Scorecard persisted to {scorecard_path}")
        return {
            "week_identifier": week_identifier,
            "interview_type": interview_type,
            "skills_tested": target_skills,
            "scorecard_path": str(scorecard_path),
            "readiness_score": readiness_score
        }

    def _generate_tailored_questions(self, skills: List[str], interview_type: str) -> Dict[str, Any]:
        """Generates domain-specific interview questions based on active job market keywords."""
        questions = []
        for i, skill in enumerate(skills, 1):
            if "system_design" in interview_type:
                questions.append({
                    "id": i,
                    "question": f"How would you design a fault-tolerant agentic system incorporating '{skill}' under high concurrent traffic?",
                    "intent": f"Test structural understanding of {skill} limits, scale barriers, and memory locks."
                })
            else:
                questions.append({
                    "id": i,
                    "question": f"Describe a scenario where you implemented '{skill}' and had to negotiate resource trade-offs with stakeholders.",
                    "intent": f"Assess behavioral alignment, project metrics delivery, and AI PM leadership skills."
                })
        return {"questions": questions}

    def _write_markdown_scorecard(
        self, 
        filepath: Path, 
        week_id: str, 
        interview_type: str, 
        skills: List[str], 
        questionnaire: Dict[str, Any], 
        score: float
    ):
        """Generates a structured markdown file to log candidate evaluation details."""
        content = [
            f"# Career Intelligence Engine — Mock Interview Scorecard",
            f"\n* **Week Identifier**: {week_id}",
            f"* **Evaluation Type**: {interview_type.upper()}",
            f"* **Assigned Difficulty**: {self.difficulty.upper()}",
            f"* **Overall Readiness Rating**: `{score}/10.0` (PASSED)",
            f"\n## Targeted Competencies Assessed",
            "".join([f"\n* {skill}" for skill in skills]),
            f"\n## Generated Questions & Intent Analysis"
        ]
        
        for q in questionnaire["questions"]:
            content.extend([
                f"\n### Question {q['id']}: {q['question']}",
                f"* *Target Intent*: {q['intent']}",
                f"* *Simulated Response Assessment*: Exceptional understanding demonstrated. Correctly articulated the state retention lifecycle, race-condition mitigation, and database optimization vectors."
            ])
            
        content.extend([
            f"\n## Product Manager Feedback & Actionable Gaps",
            f"1. **Strengths**: Solid system design intuition, high technical precision concerning relational storage locks, and articulate reasoning.",
            f"2. **Gaps to Address**: Continue practicing high-availability failovers and deep multi-threaded lock queues."
        ])
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("\n".join(content))

    def on_message(self, message: AgentMessage):
        logger.info(f"[{self.agent_id}] Received A2A event: '{message.event_type}' from '{message.sender_id}'")
        if message.event_type == "RESUME_TUNED_FOR_TARGET":
            company = message.payload.get("company", "Target Company")
            role = message.payload.get("role", "AI Product Manager")
            import datetime
            week_id = datetime.datetime.now().strftime("%Y-W%U")
            
            logger.info(f"[{self.agent_id}] REACTIVE TRIGGER: Initiating mock interview session for target company '{company}' (Role: '{role}') due to resume update...")
            results = self.conduct_mock_interview(week_id, interview_type="system_design")
            
            if results["readiness_score"] < 9.0:
                logger.info(f"[{self.agent_id}] Readiness score {results['readiness_score']}/10.0 is under target threshold. Emitting A2A upskilling trigger...")
                self.send_message(
                    recipient_id="agent_tutor",
                    event_type="UPSKILLING_REQUIRED",
                    payload={"topic": "LangGraph State Sync", "weak_areas": ["state restoration"]}
                )
