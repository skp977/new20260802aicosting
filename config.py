"""
============================================================
FILE NAME
config.py

PURPOSE
Central configuration loader. Reads settings from .env and
exposes them through a single CONFIG dictionary.

INPUT
.env file in the project root

OUTPUT
CONFIG dict + get() helper

USED BY
All automation modules, mail services, WhatsApp, CRM

DEPENDENCIES
python-dotenv, os

LAST UPDATED
2026-08-02
============================================================
"""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")


def _as_bool(value, default=False):
    if value is None:
        return default

    return str(value).strip().lower() in {"1", "true", "yes", "on"}


CONFIG = {
    # Email (IMAP)
    "EMAIL_HOST": os.getenv("EMAIL_HOST", "imap.gmail.com"),
    "EMAIL_USER": os.getenv("EMAIL_USER", ""),
    "EMAIL_PASSWORD": os.getenv("EMAIL_PASSWORD", ""),
    "IMAP_PORT": int(os.getenv("IMAP_PORT", "993")),
    "IMAP_INBOX": os.getenv("IMAP_INBOX", "INBOX"),
    "IMAP_FOLDER_PROCESSED": os.getenv("IMAP_FOLDER_PROCESSED", "INBOX/Processed"),

    # Email (SMTP)
    "SMTP_HOST": os.getenv("SMTP_HOST", "smtp.gmail.com"),
    "SMTP_PORT": int(os.getenv("SMTP_PORT", "587")),
    "SMTP_USER": os.getenv("SMTP_USER", os.getenv("EMAIL_USER", "")),
    "SMTP_PASSWORD": os.getenv("SMTP_PASSWORD", os.getenv("EMAIL_PASSWORD", "")),

    # Internal
    "ADMIN_EMAIL": os.getenv("ADMIN_EMAIL", ""),
    "APP_NAME": os.getenv("APP_NAME", "PM Automation"),

    # WhatsApp / Waha
    "WAHA_API_URL": os.getenv("WAHA_API_URL", "http://127.0.0.1:3000"),
    "WAHA_SESSION": os.getenv("WAHA_SESSION", "default"),
    "WHATSAPP_PHONE": os.getenv("WHATSAPP_PHONE", ""),
    "WAHA_API_KEY": os.getenv("WAHA_API_KEY", ""),

    # Automation
    "AUTOMATION_ENABLED": _as_bool(os.getenv("AUTOMATION_ENABLED"), True),
    "AUTOMATION_POLL_SECONDS": int(os.getenv("AUTOMATION_POLL_SECONDS", "60")),
    "AUTOMATION_MARK_PROCESSED": _as_bool(
        os.getenv("AUTOMATION_MARK_PROCESSED"), False
    ),

    # AI itinerary (LLM providers, OpenAI-compatible)
    "AI_PROVIDER": os.getenv("AI_PROVIDER", "auto"),

    "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", ""),
    "DEEPSEEK_MODEL": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    "DEEPSEEK_BASE_URL": os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    "DEEPSEEK_TIMEOUT": int(os.getenv("DEEPSEEK_TIMEOUT", "60")),

    "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
    "OPENAI_MODEL": os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
    "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1"),
    "OPENAI_TIMEOUT": int(os.getenv("OPENAI_TIMEOUT", "60")),

    "ITINERARY_ENGINE": os.getenv("ITINERARY_ENGINE", "auto"),

    # Live web search (DuckDuckGo, keyless)
    "WEB_SEARCH_ENABLED": _as_bool(os.getenv("WEB_SEARCH_ENABLED"), True),
    "SEARCH_PROVIDER": os.getenv("SEARCH_PROVIDER", "duckduckgo"),
    "SEARCH_MAX_RESULTS": int(os.getenv("SEARCH_MAX_RESULTS", "5")),
    "SEARCH_TIMEOUT": int(os.getenv("SEARCH_TIMEOUT", "20")),
}


def get(key, default=None):
    return CONFIG.get(key, default)
