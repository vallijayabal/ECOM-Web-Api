"""
Custom validators for common data types.
"""

import re
from typing import Optional


def validate_phone(phone: Optional[str]) -> Optional[str]:
    """Validate and clean a phone number."""
    if phone is None:
        return None

    # Remove spaces, dashes, parentheses
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)

    # Must start with + or digit, 7-15 digits
    if not re.match(r"^\+?\d{7,15}$", cleaned):
        raise ValueError("Invalid phone number format")

    return cleaned


def validate_hex_color(color: Optional[str]) -> Optional[str]:
    """Validate hex color code (#RRGGBB)."""
    if color is None:
        return None
    if not re.match(r"^#[0-9a-fA-F]{6}$", color):
        raise ValueError("Invalid hex color format. Expected #RRGGBB")
    return color.upper()


def validate_currency_code(code: str) -> str:
    """Validate ISO 4217 currency code."""
    if not re.match(r"^[A-Z]{3}$", code.upper()):
        raise ValueError("Invalid currency code. Expected 3-letter ISO code")
    return code.upper()


def sanitize_html(text: Optional[str]) -> Optional[str]:
    """Basic HTML sanitization to prevent XSS."""
    if text is None:
        return None

    # Remove script tags and their content
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    # Remove on* event handlers
    text = re.sub(r"\son\w+\s*=\s*[\"'][^\"']*[\"']", "", text, flags=re.IGNORECASE)

    return text
