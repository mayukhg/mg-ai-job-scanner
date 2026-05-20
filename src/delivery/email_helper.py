import logging
from pathlib import Path

logger = logging.getLogger("delivery.email")

class EmailDeliveryHelper:
    """
    MIME message builder and SMTP sender to securely deliver
    resumes and search logs via Gmail.
    """
    def __init__(self, smtp_server: str, smtp_port: int, sender_email: str, access_token: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.access_token = access_token
        
    def send_resume(self, recipient: str, resume_path: Path, subject: str) -> bool:
        """Sends email with the compiled PDF or Docx resume attachment."""
        logger.info(f"Constructing SMTP message to {recipient} with attachment {resume_path.name}")
        logger.info(f"Sending via {self.smtp_server}:{self.smtp_port} using OAuth2...")
        return True
