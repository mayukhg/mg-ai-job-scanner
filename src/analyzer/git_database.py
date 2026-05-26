# src/analyzer/git_database.py
# =====================================================================
# mg-ai-job-scanner — Git-as-a-Database Memory State Persistence
# =====================================================================

import os
import json
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger("analyzer.git_database")

class GitDatabaseManager:
    """
    Implements a stateless-native memory layer using 'Git-as-a-Database'.
    Loads state history from an isolated branch (default: 'state-store') 
    and pushes updates back to the remote repository.
    """
    def __init__(self, project_root: Path, state_file_rel_path: str = "data/store/state_history.json", branch_name: str = "state-store"):
        self.project_root = project_root
        self.state_file_path = self.project_root / state_file_rel_path
        self.branch_name = branch_name
        self.state_file_rel_path = state_file_rel_path

    def _run_git_cmd(self, args: list, check: bool = True) -> subprocess.CompletedProcess:
        """Helper to run a git command inside the project root."""
        cmd = ["git"] + args
        try:
            return subprocess.run(cmd, cwd=str(self.project_root), capture_output=True, text=True, check=check)
        except subprocess.CalledProcessError as e:
            logger.error(f"Git command failed: {' '.join(cmd)}\nStderr: {e.stderr}")
            raise e

    def is_git_repo(self) -> bool:
        """Checks if the project root is in a valid Git repository."""
        try:
            res = self._run_git_cmd(["rev-parse", "--is-inside-work-tree"])
            return res.stdout.strip() == "true"
        except Exception:
            return False

    def load_state(self) -> Dict[str, Any]:
        """
        Pulls or extracts the state history file from the state-store branch.
        Falls back to local file if Git commands fail or not inside a Git repo.
        """
        logger.info("Git-as-a-Database: Initiating state load phase...")
        
        if not self.is_git_repo():
            logger.warning("Project is not in a Git repository. Falling back to local file persistence.")
            return self._load_local_state()

        try:
            # 1. Fetch remote branches to check for state-store
            logger.info("Fetching remote state storage branches...")
            self._run_git_cmd(["fetch", "origin"])

            # Check if remote branch exists
            branches = self._run_git_cmd(["branch", "-r"])
            remote_branch_exists = f"origin/{self.branch_name}" in branches.stdout

            if remote_branch_exists:
                logger.info(f"Detected remote state branch: {self.branch_name}. Pulling state file...")
                # Extract file contents directly from the remote branch without switching branches
                res = self._run_git_cmd(["show", f"origin/{self.branch_name}:{self.state_file_rel_path}"], check=False)
                if res.returncode == 0:
                    state_data = json.loads(res.stdout.strip())
                    logger.info("Successfully loaded system state from Git-as-a-Database remote!")
                    
                    # Ensure local directory exists and write it locally for current run
                    self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(self.state_file_path, 'w', encoding='utf-8') as f:
                        json.dump(state_data, f, indent=4)
                    return state_data
                else:
                    logger.warning(f"Could not read state file from branch origin/{self.branch_name}. Initializing fresh state.")
            else:
                logger.info(f"State branch '{self.branch_name}' not found on remote. Starting with fresh state history.")
                
        except Exception as e:
            logger.error(f"Failed to synchronize state from Git: {e}. Falling back to local file.")
            
        return self._load_local_state()

    def save_state(self, state_data: Dict[str, Any]) -> bool:
        """
        Saves and commits the system state back to the isolated 'state-store' branch,
        and pushes it to remote. Automatically handles branch transitions.
        """
        logger.info("Git-as-a-Database: Initiating state commit phase...")
        
        # 1. Write the state file locally first
        self.state_file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.state_file_path, 'w', encoding='utf-8') as f:
            json.dump(state_data, f, indent=4)
        logger.info(f"Wrote local state snapshot to {self.state_file_path.name}")

        if not self.is_git_repo():
            logger.info("Skipping Git commit phase: Not in a Git repository.")
            return True

        # Check if we are running in a CI/GHA environment where git operations are enabled
        # GHA sets GITHUB_ACTIONS=true
        is_ci = os.getenv("GITHUB_ACTIONS") == "true" or os.getenv("CIE_GIT_STORE_FORCE") == "true"
        
        if not is_ci:
            logger.info("Running locally. Skipping git remote sync to keep local workflow simple. (Set CIE_GIT_STORE_FORCE=true to force push).")
            return True

        original_branch = "main"
        try:
            # Determine current active branch to return back to
            res = self._run_git_cmd(["rev-parse", "--abbrev-ref", "HEAD"])
            original_branch = res.stdout.strip()
            
            # Configure bot user for committing in CI
            self._run_git_cmd(["config", "--local", "user.name", "cie-bot"])
            self._run_git_cmd(["config", "--local", "user.email", "cie-bot@users.noreply.github.com"])

            # 2. Check if state-store branch exists locally
            branches_local = self._run_git_cmd(["branch"])
            local_exists = self.branch_name in branches_local.stdout
            
            # 3. Switch to state-store branch (creating it if needed)
            if local_exists:
                logger.info(f"Switching to state branch: {self.branch_name}...")
                self._run_git_cmd(["checkout", self.branch_name])
            else:
                logger.info(f"Creating and switching to state branch: {self.branch_name}...")
                self._run_git_cmd(["checkout", "-b", self.branch_name])

            # Ensure directory exists in the checkout and write state
            state_in_branch = self.project_root / self.state_file_rel_path
            state_in_branch.parent.mkdir(parents=True, exist_ok=True)
            with open(state_in_branch, 'w', encoding='utf-8') as f:
                json.dump(state_data, f, indent=4)

            # 4. Stage and commit
            logger.info("Staging and committing new state data...")
            self._run_git_cmd(["add", self.state_file_rel_path])
            
            # Check if there are changes to commit
            status_res = self._run_git_cmd(["status", "--porcelain"])
            if status_res.stdout.strip():
                self._run_git_cmd(["commit", "-m", "chore(state): update system memory state snapshot [skip ci]"])
                # 5. Push remote
                logger.info(f"Pushing memory state to origin/{self.branch_name}...")
                self._run_git_cmd(["push", "origin", self.branch_name])
                logger.info("Successfully pushed system memory snapshot to Git remote!")
            else:
                logger.info("No state changes detected since last save. Skipping push.")

        except Exception as e:
            logger.error(f"Git-as-a-Database failed to write state: {e}")
            return False
        finally:
            # 6. ALWAYS return to original branch
            try:
                logger.info(f"Returning to active execution branch: {original_branch}...")
                self._run_git_cmd(["checkout", original_branch])
            except Exception as e:
                logger.error(f"Failed to switch back to original branch '{original_branch}': {e}")
        
        return True

    def _load_local_state(self) -> Dict[str, Any]:
        """Loads state from the local state file, returning an empty state if it does not exist."""
        if not self.state_file_path.exists():
            logger.info("Local state history file not found. Initializing empty state history.")
            return {
                "system_name": "Career Intelligence Engine (CIE)",
                "last_run_timestamp": None,
                "metrics": {
                    "total_runs": 0,
                    "total_jobs_scraped": 0,
                    "total_tutors_compiled": 0,
                    "total_scaffolds_deployed": 0
                },
                "history": []
            }
        try:
            with open(self.state_file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to read local state history: {e}")
            return {}
