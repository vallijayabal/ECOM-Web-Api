"""
Application configuration management using Pydantic Settings.
Re-exported from core package for convenience.
"""

from app.core import Settings, get_settings

__all__ = ["Settings", "get_settings"]
