# src/onboarding/onboarding_wizard.py
# =====================================================================
# mg-ai-job-scanner — Career Intelligence Engine Onboarding Wizard
# =====================================================================

import os
import sys
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, List

logger = logging.getLogger("onboarding.wizard")

class CareerOnboardingWizard:
    """
    Guides the user through an interactive, step-by-step setup to customize
    the Career Intelligence Engine. It configures settings.yaml and establishes
    a secure local .env file for credentials, preserving existing parameters.
    """
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_path = self.project_root / "config" / "settings.yaml"
        self.env_path = self.project_root / ".env"
        self.config = self._load_current_settings()

    def _load_current_settings(self) -> Dict[str, Any]:
        """Loads existing configuration or defaults if settings.yaml is missing."""
        if not self.config_path.exists():
            logger.warning(f"Settings file not found at {self.config_path}. Initializing default structure.")
            return {}
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.error(f"Error reading configuration file: {e}")
            return {}

    def _save_settings(self) -> bool:
        """Saves current configuration state back to config/settings.yaml."""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(self.config, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Updated system settings saved successfully to {self.config_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write settings to {self.config_path}: {e}")
            return False

    def _write_env_file(self, secrets: Dict[str, str]) -> bool:
        """Saves secure access keys to a local .env file, protecting them from git checkins."""
        try:
            existing_secrets = {}
            if self.env_path.exists():
                with open(self.env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            k, v = line.split('=', 1)
                            existing_secrets[k.strip()] = v.strip()

            # Merge new secrets with existing
            existing_secrets.update(secrets)

            with open(self.env_path, 'w', encoding='utf-8') as f:
                f.write("# .env — Local Secret Credentials for Career Intelligence Engine\n")
                f.write("# DO NOT COMMIT THIS FILE TO GITHUB\n\n")
                for k, v in existing_secrets.items():
                    f.write(f"{k}={v}\n")
            logger.info(f"Secure secrets written successfully to {self.env_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to write secure environment secrets: {e}")
            return False

    def _prompt_with_default(self, question: str, default: str) -> str:
        """Prompts the user in the CLI, using a sensible default if they press Enter."""
        try:
            user_input = input(f"{question} [{default}]: ").strip()
            return user_input if user_input else default
        except (KeyboardInterrupt, EOFError):
            print("\nSetup aborted. Preserving existing configurations.")
            sys.exit(0)

    def run_interactive_wizard(self):
        """Runs the multi-stage interactive onboarding CLI loop."""
        print("=" * 70)
        print("   🚀 WELCOME TO THE CAREER INTELLIGENCE ENGINE ONBOARDING WIZARD 🚀")
        print("=" * 70)
        print("This interactive guide configures your multi-agent job-hunting engine.")
        print("Press Enter at any prompt to accept the recommended default option.")
        print("-" * 70)

        # -----------------------------------------------------------------
        # STEP 1: CAREER PROFILE & TARGETS
        # -----------------------------------------------------------------
        print("\n[STEP 1/4] Career Profile & Application Targets")
        print("-" * 50)
        
        # Target Roles
        default_titles = self.config.get("scraper", {}).get("search", {}).get("titles", [
            "AI Product Manager", "Agentic AI Product Manager", "Director of Product Management"
        ])
        default_titles_str = ", ".join(default_titles)
        titles_input = self._prompt_with_default("Enter your target job titles (comma-separated)", default_titles_str)
        target_titles = [t.strip() for t in titles_input.split(",") if t.strip()]
        
        # Target Location
        default_loc = self.config.get("scraper", {}).get("search", {}).get("location", "Pune, India")
        target_loc = self._prompt_with_default("Enter your target job location (e.g. Pune, India / Remote)", default_loc)
        
        # Watchdog Company targets
        default_companies = self.config.get("watchdog", {}).get("target_companies", [
            "Anthropic", "OpenAI", "Cognition", "Perplexity", "LangChain"
        ])
        default_companies_str = ", ".join(default_companies)
        companies_input = self._prompt_with_default("Enter target stealth companies to watch (comma-separated)", default_companies_str)
        target_companies = [c.strip() for c in companies_input.split(",") if c.strip()]

        # Update Scraper & Watchdog settings dictionary
        if "scraper" not in self.config:
            self.config["scraper"] = {}
        if "search" not in self.config["scraper"]:
            self.config["scraper"]["search"] = {}
        self.config["scraper"]["search"]["titles"] = target_titles
        self.config["scraper"]["search"]["location"] = target_loc
        
        if "watchdog" not in self.config:
            self.config["watchdog"] = {}
        self.config["watchdog"]["target_companies"] = target_companies

        # -----------------------------------------------------------------
        # STEP 2: SCRAPER & AUTOMATION SETTINGS
        # -----------------------------------------------------------------
        print("\n[STEP 2/4] Scraper Settings & Cron Automation")
        print("-" * 50)
        
        # Scan Frequency
        freq_choice = self._prompt_with_default("Select scan frequency (weekly / monthly / quarterly)", "weekly").lower()
        days_map = {"weekly": 7, "monthly": 30, "quarterly": 90}
        frequency_days = days_map.get(freq_choice, 7)
        self.config["watchdog"]["check_frequency_days"] = frequency_days

        # Webscraper Tool Option
        default_scraper_provider = self.config.get("scraper", {}).get("provider", "apify")
        scraper_provider = self._prompt_with_default("Select scraper backend (apify / serpapi / custom_mock)", default_scraper_provider)
        self.config["scraper"]["provider"] = scraper_provider

        # Notification Email
        default_email = self.config.get("email", {}).get("recipient", "mayukhg@gmail.com")
        notification_email = self._prompt_with_default("Enter notification email address", default_email)
        if "email" not in self.config:
            self.config["email"] = {}
        self.config["email"]["recipient"] = notification_email

        # -----------------------------------------------------------------
        # STEP 3: AGENT MODULE PREFERENCES
        # -----------------------------------------------------------------
        print("\n[STEP 3/4] Intelligent Agent Customization")
        print("-" * 50)
        
        # Agent Tutor Learning formats
        print("Upskilling Explainer Formats preferred:")
        pref_audio = self._prompt_with_default("  Enable audio explainer podcasts? (yes/no)", "yes").lower() == "yes"
        pref_mindmap = self._prompt_with_default("  Enable visual Mermaid mindmaps? (yes/no)", "yes").lower() == "yes"
        
        if "tutor" not in self.config:
            self.config["tutor"] = {}
        self.config["tutor"]["generate_audio"] = pref_audio
        self.config["tutor"]["generate_mindmap"] = pref_mindmap

        # Agent Mock Interviewer Level
        default_diff = self.config.get("interviewer", {}).get("default_difficulty", "hard")
        diff_level = self._prompt_with_default("Select mock interview difficulty (easy / medium / hard)", default_diff)
        if "interviewer" not in self.config:
            self.config["interviewer"] = {}
        self.config["interviewer"]["default_difficulty"] = diff_level

        # Agent Portfolio Architect Project License
        default_license = self.config.get("portfolio", {}).get("default_license", "MIT")
        project_license = self._prompt_with_default("Select portfolio project license (MIT / Apache / GPL)", default_license)
        if "portfolio" not in self.config:
            self.config["portfolio"] = {}
        self.config["portfolio"]["default_license"] = project_license

        # -----------------------------------------------------------------
        # STEP 4: SECURE VAULT & SECRET KEYS
        # -----------------------------------------------------------------
        print("\n[STEP 4/4] Secure API Connections & Secret Credentials")
        print("-" * 50)
        print("Warning: These sensitive secrets are stored safely inside a local '.env'")
        print("file, which is git-ignored to prevent accidental exposure to GitHub.")
        
        gemini_key = self._prompt_with_default("Enter Google Gemini/AI Studio API Key", "MOCK_GEMINI_KEY_12345")
        github_pat = self._prompt_with_default("Enter GitHub Personal Access Token (PAT)", "MOCK_GITHUB_PAT_67890")
        dropbox_token = self._prompt_with_default("Enter Dropbox API Access Token", "MOCK_DROPBOX_TOKEN_54321")

        secrets_to_save = {
            "GEMINI_API_KEY": gemini_key,
            "GITHUB_PAT": github_pat,
            "DROPBOX_ACCESS_TOKEN": dropbox_token
        }

        # -----------------------------------------------------------------
        # PERSIST CONFIG & FINALIZE
        # -----------------------------------------------------------------
        print("\nWriting settings configurations...")
        settings_success = self._save_settings()
        env_success = self._write_env_file(secrets_to_save)

        if settings_success and env_success:
            print("\n" + "=" * 70)
            print("   🎉 ONBOARDING COMPLETED SUCCESSFULLY! CAREER ENGINE READY 🎉")
            print("=" * 70)
            print(f"1. System configuration saved to: {self.config_path.name}")
            print(f"2. Secure keys and access tokens stored in: {self.env_path.name}")
            print("\nYou can now trigger your weekly cron runner using:")
            print("   python src/main.py")
            print("=" * 70)
        else:
            print("\n❌ Setup finished with errors. Please check console logs.")

if __name__ == "__main__":
    # If run directly as a script
    project_dir = Path(__file__).resolve().parent.parent.parent
    wizard = CareerOnboardingWizard(project_dir)
    wizard.run_interactive_wizard()
