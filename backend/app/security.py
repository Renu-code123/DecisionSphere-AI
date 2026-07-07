import re
import logging
from fastapi import Request, HTTPException, status
from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import AuditLog

logger = logging.getLogger("security")

# Heuristics for prompt injection detection
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"bypass safety filters",
    r"you are now a bypass",
    r"dan mode",
    r"jailbreak",
    r"output raw system prompt",
    r"system instructions",
    r"ignore standard guidelines",
    r"do anything now",
    r"act as",
    r"forget what you were told"
]

def sanitize_input(text: str) -> str:
    """
    Sanitize text input by removing potentially dangerous HTML tags and scripting characters
    to prevent XSS and SQL injection (SQL injection is already mitigated via SQLAlchemy parameterized queries).
    """
    if not text:
        return ""
    # Strip HTML tags
    clean = re.sub(r'<[^>]*>', '', text)
    # Remove potentially dangerous character sequences
    clean = clean.replace("'", "''")  # Escape single quotes
    return clean

def detect_prompt_injection(text: str) -> bool:
    """
    Check if the user input shows signs of a prompt injection attempt using standard regex heuristics.
    """
    if not text:
        return False
        
    text_lower = text.lower()
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            return True
            
    return False

def audit_and_verify_injection(user_input: str, user_id: int = None, ip_address: str = None):
    """
    Checks user input for prompt injection, logs the event, and raises an exception if detected.
    """
    if detect_prompt_injection(user_input):
        db = SessionLocal()
        try:
            log_entry = AuditLog(
                user_id=user_id,
                action="prompt_injection",
                ip_address=ip_address,
                details=f"Prompt injection pattern detected in input: '{user_input[:100]}...'"
            )
            db.add(log_entry)
            db.commit()
        finally:
            db.close()
            
        logger.warning(f"Prompt injection attempt blocked from IP {ip_address}. Input: {user_input[:200]}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Potential prompt injection or safety policy violation detected."
        )
