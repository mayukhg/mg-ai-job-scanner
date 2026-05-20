# onboard.py
# =====================================================================
# mg-ai-job-scanner — Interactive Onboarding CLI Entrypoint
# =====================================================================

import sys
import logging
from pathlib import Path

# Resolve project paths
project_root = Path(__file__).resolve().parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Set up logging for the CLI execution
logging.basicConfig(
    level=logging.WARNING, # Keep CLI clean by default
    format='%(asctime)s - %(levelname)s - %(message)s'
)

from src.onboarding import CareerOnboardingWizard

def main():
    try:
        wizard = CareerOnboardingWizard(project_root)
        wizard.run_interactive_wizard()
    except Exception as e:
        print(f"\nError: Onboarding failed to start: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
