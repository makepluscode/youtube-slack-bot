"""Prompt templates for LangChain"""

from .templates import (
    URL_EXTRACTION_SYSTEM_PROMPT,
    URL_EXTRACTION_HUMAN_PROMPT,
    create_url_extraction_prompt,
)

__all__ = [
    "URL_EXTRACTION_SYSTEM_PROMPT",
    "URL_EXTRACTION_HUMAN_PROMPT",
    "create_url_extraction_prompt",
]

