import logging
import re
import idna

from typing import Set
from email_validator import validate_email, EmailNotValidError

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)

# Regular expressions for script detection
ARABIC_RE = re.compile(
    r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]"
)
LATIN_RE = re.compile(r"[A-Za-z\u00C0-\u00FF\u0100-\u017F\u0180-\u024F]")
HAN_RE = re.compile(r"[\u4E00-\u9FFF]")
HIRAGANA_RE = re.compile(r"[\u3040-\u309F]")
KATAKANA_RE = re.compile(r"[\u30A0-\u30FF]")


def validate_email_general(email: str) -> bool:
    """Validates basic email syntax and domain encoding."""
    try:
        validate_email(email, allow_smtputf8=True, check_deliverability=False)
        local_part, domain = email.split("@")
        idna.encode(domain)
        logging.info(f"Validated email: {email}")
        return True
    except (EmailNotValidError, ValueError, UnicodeError) as e:
        logging.warning(f"Invalid email detected: {email} | Error: {e}")
        return False


def get_char_script(char: str) -> str:
    """Detects the Unicode script of a given character."""
    if ARABIC_RE.match(char):
        return "Arabic"
    if LATIN_RE.match(char):
        return "Latin"
    if HAN_RE.match(char):
        return "Han"
    if HIRAGANA_RE.match(char):
        return "Hiragana"
    if KATAKANA_RE.match(char):
        return "Katakana"
    return "Other"


def validate_same_script_email(email: str) -> bool:
    """Ensures all significant characters in the email use the same script."""
    try:
        local_part, domain_part = email.split("@")
    except ValueError:
        return False

    significant_chars: str = "".join(
        c for c in (local_part + domain_part) if c not in {".", "-", "@"}
    )
    if not significant_chars:
        return False

    detected_scripts: Set[str] = {
        script
        for char in significant_chars
        if (script := get_char_script(char)) != "Other"
    }

    return len(detected_scripts) == 1
