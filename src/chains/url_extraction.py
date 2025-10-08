"""URL extraction chain using LangChain"""

import json
import logging
import re
from typing import Any

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import Runnable
from langchain_ollama import ChatOllama

from ..prompts import create_url_extraction_prompt

logger = logging.getLogger(__name__)


class URLExtractionChain:
    """Chain for extracting YouTube URLs from messages"""

    # YouTube URL patterns for fallback
    YOUTUBE_PATTERNS = [
        r"https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+(?:&[\w=&]*)?",
        r"https?://(?:www\.)?youtube\.com/shorts/[\w-]+",
        r"https?://youtu\.be/[\w-]+(?:\?[\w=&]*)?",
    ]

    # Download intent keywords
    DOWNLOAD_KEYWORDS = [
        "다운로드",
        "받아",
        "저장",
        "download",
        "get",
        "save",
        "받아줘",
        "저장해",
        "다운",
    ]

    def __init__(self, llm: ChatOllama):
        """
        Initialize the URL extraction chain
        
        Args:
            llm: ChatOllama LLM instance
        """
        self.llm = llm
        self.chain = self._create_chain()

    def _create_chain(self) -> Runnable:
        """Create the LangChain runnable chain"""
        prompt = create_url_extraction_prompt()
        output_parser = StrOutputParser()
        
        chain = prompt | self.llm | output_parser
        return chain

    def _extract_with_regex(self, text: str) -> tuple[list[str], bool]:
        """
        Fallback: Extract URLs using regex patterns
        
        Args:
            text: Message text
            
        Returns:
            Tuple of (urls list, download intent boolean)
        """
        urls = []
        for pattern in self.YOUTUBE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            urls.extend(matches)

        # Remove duplicates while preserving order
        unique_urls = list(dict.fromkeys(urls))

        # Detect download intent
        download_intent = any(
            keyword in text.lower() for keyword in self.DOWNLOAD_KEYWORDS
        )

        logger.info(
            f"Regex fallback: {len(unique_urls)} URLs, download intent: {download_intent}"
        )
        return unique_urls, download_intent

    def _parse_llm_response(self, response: str) -> tuple[list[str], bool]:
        """
        Parse LLM JSON response
        
        Args:
            response: LLM response string
            
        Returns:
            Tuple of (urls list, download intent boolean)
        """
        try:
            # Try to find JSON in the response
            # Sometimes LLM adds extra text before/after JSON
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response)

            urls = result.get("urls", [])
            intent = result.get("download_intent", False)

            # Validate URLs
            valid_urls = [url for url in urls if self._is_valid_youtube_url(url)]

            logger.info(
                f"LLM extracted {len(valid_urls)} URLs, download intent: {intent}"
            )
            return valid_urls, intent

        except (json.JSONDecodeError, AttributeError) as e:
            logger.warning(f"Failed to parse LLM JSON response: {e}")
            return [], False

    def _is_valid_youtube_url(self, url: str) -> bool:
        """Validate YouTube URL"""
        for pattern in self.YOUTUBE_PATTERNS:
            if re.match(pattern, url, re.IGNORECASE):
                return True
        return False

    def extract(self, message: str, use_llm: bool = True) -> dict[str, Any]:
        """
        Extract YouTube URLs and download intent from message
        
        Args:
            message: The message text to analyze
            use_llm: Whether to use LLM (True) or regex only (False)
            
        Returns:
            Dictionary with 'urls' and 'download_intent'
        """
        if not message or not message.strip():
            return {"urls": [], "download_intent": False}

        if not use_llm:
            urls, intent = self._extract_with_regex(message)
            return {"urls": urls, "download_intent": intent}

        try:
            # Try LLM extraction
            logger.debug(f"Extracting URLs from message: {message[:100]}...")
            response = self.chain.invoke({"message": message})
            
            logger.debug(f"LLM response: {response}")
            
            urls, intent = self._parse_llm_response(response)
            
            # If LLM found nothing but there are URLs in text, use regex fallback
            if not urls:
                logger.info("LLM found no URLs, trying regex fallback")
                urls, intent_regex = self._extract_with_regex(message)
                # Keep LLM's intent decision if it was confident
                if not intent:
                    intent = intent_regex

            return {"urls": urls, "download_intent": intent}

        except Exception as e:
            logger.error(f"LLM extraction failed: {e}, using regex fallback")
            urls, intent = self._extract_with_regex(message)
            return {"urls": urls, "download_intent": intent}


def create_url_extraction_chain(
    model: str = "gemma3:4b",
    host: str = "http://localhost:11434",
    temperature: float = 0.1
) -> URLExtractionChain:
    """
    Factory function to create a URL extraction chain
    
    Args:
        model: Ollama model name
        host: Ollama server URL
        temperature: LLM temperature (lower = more consistent)
        
    Returns:
        URLExtractionChain instance
    """
    llm = ChatOllama(
        model=model,
        base_url=host,
        temperature=temperature,
    )
    
    return URLExtractionChain(llm)

