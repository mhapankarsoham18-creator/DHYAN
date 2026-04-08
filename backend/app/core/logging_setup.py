import logging
import re
from typing import Any, Dict

# Regex patterns for sensitive data
SENSITIVE_PATTERNS = {
    # Match standard Indian PAN format: 5 letters, 4 digits, 1 letter
    "pan": re.compile(r'\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b', re.IGNORECASE),
    # Match generic token-looking strings (e.g., Bearer XXXX, access_token=XXXX)
    "token": re.compile(r'(?i)(bearer\s+|token[\s=:]+|authorization[\s=:]+(?:bearer\s+)?)([a-zA-Z0-9_\-\.]+)', re.IGNORECASE),
    "password": re.compile(r'(?i)((?:password|passwd|pwd)[\s=:]+)([^\s,;]+)', re.IGNORECASE)
}

class MaskingFormatter(logging.Formatter):
    """
    A custom logging formatter that redacts sensitive PII and auth tokens
    before they are written to the console or logs.
    """
    def format(self, record: logging.LogRecord) -> str:
        original_msg = super().format(record)
        return mask_sensitive_data(original_msg)

def mask_sensitive_data(text: str) -> str:
    """Mask sensitive patterns in a string."""
    if not isinstance(text, str):
        return text
        
    masked_text = text
    # Mask PAN
    masked_text = SENSITIVE_PATTERNS["pan"].sub("[REDACTED_PAN]", masked_text)
    
    # Mask Tokens (replace group 1)
    def token_replacer(match: re.Match[str]) -> str:
        prefix = match.group(1)
        return f"{prefix}[REDACTED_TOKEN]"
        
    masked_text = SENSITIVE_PATTERNS["token"].sub(token_replacer, masked_text)
    
    # Mask Passwords
    masked_text = SENSITIVE_PATTERNS["password"].sub(token_replacer, masked_text)
    
    return masked_text

def sentry_before_send(event: Dict[str, Any], hint: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Sentry before_send hook to scrub PII from events before they leave the server.
    """
    # Scrub Request parameters, headers, cookies
    if "request" in event:
        request = event["request"]
        
        # Scrub Headers
        if "headers" in request:
            headers = request["headers"]
            for key in list(headers.keys()):
                if key.lower() in ("authorization", "x-api-key", "cookie"):
                    headers[key] = "[REDACTED]"
                    
        # Scrub Data (Body payload)
        if "data" in request and isinstance(request["data"], dict):
            data = request["data"]
            for key in ["password", "token", "access_token", "refresh_token", "pan", "pan_number"]:
                if key in data:
                    data[key] = "[REDACTED]"
                    
    # Note: Sentry already scrubs some defaults, but we add custom ones here
    return event

def setup_logging() -> None:
    """Initialize secure logging for the application"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        
    console_handler = logging.StreamHandler()
    formatter = MaskingFormatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
