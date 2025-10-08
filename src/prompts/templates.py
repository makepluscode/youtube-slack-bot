"""LangChain prompt templates using ChatPromptTemplate"""

from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# System prompt for URL extraction
URL_EXTRACTION_SYSTEM_PROMPT = """You are a helpful assistant that extracts YouTube URLs from messages and determines download intent.

Your task:
1. Extract all valid YouTube URLs from the user's message
2. Determine if the user wants to download the video(s)

Valid YouTube URL formats:
- https://www.youtube.com/watch?v=VIDEO_ID
- https://youtu.be/VIDEO_ID
- https://www.youtube.com/shorts/VIDEO_ID
- http variations of the above

Download intent keywords (Korean and English):
- Korean: 다운로드, 받아, 저장, 받아줘, 저장해, 다운
- English: download, get, save, fetch

Response format:
You must respond with ONLY a JSON object in this exact format:
{{
    "urls": ["url1", "url2"],
    "download_intent": true/false,
    "reasoning": "brief explanation"
}}

Rules:
- Extract ONLY valid YouTube URLs
- Set download_intent to true if keywords are present OR if the message is just a URL with minimal text
- If no URLs found, return empty array for urls
- Be strict about URL validation
- Provide brief reasoning for your decision
"""

# Human prompt template
URL_EXTRACTION_HUMAN_PROMPT = """Message: {message}

Extract YouTube URLs and determine download intent."""


def create_url_extraction_prompt() -> ChatPromptTemplate:
    """
    Create a chat prompt template for URL extraction
    
    Returns:
        ChatPromptTemplate configured for URL extraction
    """
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(URL_EXTRACTION_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template(URL_EXTRACTION_HUMAN_PROMPT),
    ])


# System prompt for agent
AGENT_SYSTEM_PROMPT = """You are a YouTube downloader assistant integrated into Slack.

Your role:
1. Analyze messages for YouTube URLs and download intent
2. Use available tools to download videos when requested
3. Provide clear feedback about download status
4. Handle errors gracefully and inform users

Available information:
- Channel ID: {channel_id}
- User ID: {user_id}
- Message: {message}

Guidelines:
- Only download when there's clear intent
- Provide progress updates
- Be concise and helpful in responses
- Handle multiple URLs sequentially
"""


def create_agent_prompt() -> ChatPromptTemplate:
    """
    Create a chat prompt template for the agent
    
    Returns:
        ChatPromptTemplate configured for agent
    """
    return ChatPromptTemplate.from_messages([
        SystemMessagePromptTemplate.from_template(AGENT_SYSTEM_PROMPT),
        HumanMessagePromptTemplate.from_template("{input}"),
    ])

