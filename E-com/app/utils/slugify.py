"""
Slug generation utility.
"""

from slugify import slugify as _slugify


def generate_slug(text: str) -> str:
    """Generate a URL-friendly slug from text."""
    return _slugify(text, max_length=255)
