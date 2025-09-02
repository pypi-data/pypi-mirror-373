"""
Quarter Lib - A comprehensive library for various productivity integrations.

This package provides modules for:
- Todoist integration
- Notion API
- Google Calendar integration  
- Monica CRM integration
- Voice recording and transcription
- File utilities
- Database connections (MySQL and HTTP-based)
- Akeyless secret management
- Logging utilities
"""

__version__ = "2.0.0"

# Import main modules for convenience
from . import akeyless
from . import database
from . import file_helper
from . import google
from . import google_calendar
from . import logging
from . import models
from . import monica
from . import notion
from . import todoist
from . import transcriber
from . import voice_recorder

__all__ = [
    "akeyless",
    "database", 
    "file_helper",
    "google",
    "google_calendar",
    "logging",
    "models",
    "monica",
    "notion",
    "todoist",
    "transcriber",
    "voice_recorder",
]
