# src/analyzer/observability.py
# =====================================================================
# mg-ai-job-scanner — LLMOps Observability and Step Summary Generator
# =====================================================================

import os
import time
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger("analyzer.observability")

class AgentTrace:
    """Represents a single step execution trace of a CIE agent."""
    def __init__(self, agent_name: str, description: str):
        self.agent_name = agent_name
        self.description = description
        self.start_time = time.time()
        self.end_time = 0.0
        self.inputs = None
        self.outputs = None
        self.confidence_score = 1.0
        self.tokens_used = 0
        self.status = "PENDING"
        self.message = ""

    def complete(self, outputs: Any, confidence_score: float = 1.0, tokens_used: int = 0, message: str = "Success"):
        self.end_time = time.time()
        self.outputs = outputs
        self.confidence_score = confidence_score
        self.tokens_used = tokens_used
        self.status = "SUCCESS"
        self.message = message

    def fail(self, message: str):
        self.end_time = time.time()
        self.status = "FAILED"
        self.message = message

    @property
    def duration_seconds(self) -> float:
        end = self.end_time if self.end_time > 0.0 else time.time()
        return round(end - self.start_time, 2)

class LLMOpsTracker:
    """
    Orchestrates the tracing metrics for multi-agent loops.
    Compiles a clean markdown run summary file ('gha_run_summary.md') 
    and ASCII flows for injection into GHA step summaries.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.summary_path = self.project_root / "gha_run_summary.md"
        self.traces: List[AgentTrace] = []

    def start_trace(self, agent_name: str, description: str, inputs: Any = None) -> AgentTrace:
        """Starts a new trace recording for an agent."""
        trace = AgentTrace(agent_name, description)
        trace.inputs = inputs
        self.traces.append(trace)
        logger.info(f"[TRACE START] {agent_name}: {description}")
        return trace

    def generate_markdown_summary(self) -> str:
        """Compiles trace logs into structured markdown suitable for GHA `$GITHUB_STEP_SUMMARY`."""
        total_time = sum(t.duration_seconds for t in self.traces)
        total_tokens = sum(t.tokens_used for t in self.traces)
        
        md = []
        md.append("# 🤖 CIE Orchestrator Weekly Run Summary")
        md.append(f"**Execution Status**: ✅ Successful | **Total Time**: {round(total_time, 2)}s | **Total Estimated Tokens**: {total_tokens}")
        md.append("\n## 📊 Agent Pipeline Tracing Metrics\n")
        
        # Table Header
        md.append("| Agent / Stage | Description | Status | Duration | Confidence Score | Tokens |")
        md.append("|---|---|---|---|---|---|")
        
        for t in self.traces:
            status_emoji = "✅" if t.status == "SUCCESS" else "❌" if t.status == "FAILED" else "⏳"
            md.append(f"| **{t.agent_name}** | {t.description} | {status_emoji} {t.status} | {t.duration_seconds}s | {int(t.confidence_score*100)}% | {t.tokens_used} |")
            
        md.append("\n## ⛓️ Execution Flow Dependency Graph\n")
        md.append("```")
        md.append(self._generate_ascii_graph())
        md.append("```")
        
        md.append("\n## 🔍 Agent Step Logs (Telemetry Deep Dive)\n")
        
        for t in self.traces:
            md.append(f"<details>")
            md.append(f"<summary><b>{t.agent_name} Telemetry Summary</b> (Click to Expand)</summary>\n")
            md.append(f"**Inputs Given**:\n```json\n{self._format_json_summary(t.inputs)}\n```\n")
            md.append(f"**Outputs Resolved**:\n```json\n{self._format_json_summary(t.outputs)}\n```\n")
            md.append(f"**Execution Log Message**: {t.message}\n")
            md.append(f"</details>\n")
            
        md.append("\n---\n*Generated autonomously by **Career Intelligence Engine (CIE) LLMOps Tracer**.*")
        
        summary_content = "\n".join(md)
        
        # Write to file
        try:
            with open(self.summary_path, 'w', encoding='utf-8') as f:
                f.write(summary_content)
            logger.info(f"Successfully generated step summary markdown at {self.summary_path.name}")
        except Exception as e:
            logger.error(f"Failed to write step summary markdown: {e}")
            
        return summary_content

    def _generate_ascii_graph(self) -> str:
        """Draws a clean ASCII data-flow graph mapping agents' execution order."""
        graph = [
            " [Cron Weekly Trigger]",
            "          │",
            "          ▼"
        ]
        
        for idx, t in enumerate(self.traces):
            status_icon = "✔" if t.status == "SUCCESS" else "✘" if t.status == "FAILED" else "?"
            graph.append(f" ┌────────────────────────────────────────────────────────┐")
            graph.append(f" │ [{status_icon}] {t.agent_name:<16} │ Conf: {int(t.confidence_score*100):>3}% │ Time: {t.duration_seconds:>5}s │")
            graph.append(f" └────────────────────────────────────────────────────────┘")
            if idx < len(self.traces) - 1:
                graph.append(f"          │  Outputs pipe to next agent")
                graph.append(f"          ▼")
                
        return "\n".join(graph)

    def _format_json_summary(self, data: Any) -> str:
        """Safely serializes inputs/outputs to clean JSON for reports, truncating if too large."""
        if data is None:
            return "No input/output data registered."
        try:
            if isinstance(data, (dict, list)):
                raw_str = json.dumps(data, indent=2)
            else:
                raw_str = str(data)
            
            # Simple length limit to prevent summary bloating
            if len(raw_str) > 800:
                return raw_str[:800] + "\n... [TRUNCATED FOR TELEMETRY BREVITY] ..."
            return raw_str
        except Exception:
            return str(data)
