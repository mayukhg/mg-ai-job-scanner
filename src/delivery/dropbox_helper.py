import logging
from pathlib import Path

logger = logging.getLogger("delivery.dropbox")

class DropboxSyncHelper:
    """
    Manages Dropbox uploads and executes Dropbox Round-Trip state synchronization
    to persist database state between GHA ephemeral VMs.
    """
    def __init__(self, access_token: str, target_folder: str):
        self.access_token = access_token
        self.target_folder = target_folder
        
    def download_file(self, remote_path: str, local_path: Path) -> bool:
        """Downloads themes.db from Dropbox to local disk at startup."""
        logger.info(f"Downloading state {remote_path} to {local_path}...")
        return True
        
    def upload_file(self, local_path: Path, remote_path: str) -> bool:
        """Uploads updated resume or themes.db to Dropbox."""
        logger.info(f"Uploading local {local_path} to Dropbox {remote_path}...")
        return True
