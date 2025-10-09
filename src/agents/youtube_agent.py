"""YouTube Download Agent for orchestrating the download workflow"""

import logging
from typing import Any, Callable, Optional

from langchain.agents import AgentExecutor, create_react_agent
from langchain_ollama import ChatOllama
from langchain_core.prompts import PromptTemplate

from ..chains import URLExtractionChain
from ..tools import get_youtube_tools
from ..config import Settings

logger = logging.getLogger(__name__)


class YouTubeDownloadAgent:
    """
    Agent that orchestrates YouTube video downloading workflow
    
    This agent:
    1. Extracts YouTube URLs from messages
    2. Determines download intent
    3. Uses tools to download videos
    4. Provides feedback
    """

    def __init__(
        self,
        settings: Settings,
        feedback_callback: Optional[Callable] = None
    ):
        """
        Initialize the YouTube agent
        
        Args:
            settings: Application settings
            feedback_callback: Optional callback for sending feedback (channel_id, message, thread_ts)
        """
        self.settings = settings
        self.feedback_callback = feedback_callback
        
        # Initialize LLM
        self.llm = ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_host,
            temperature=0.1,
        )
        
        # Initialize URL extraction chain
        self.url_chain = URLExtractionChain(self.llm)
        
        # Initialize tools
        self.tools = get_youtube_tools(settings.download_dir)
        
        # For future: This will enable Agent with tools
        # Currently we use a simpler workflow
        # self.agent_executor = self._create_agent()
        
        logger.info("YouTubeDownloadAgent initialized")

    def _create_agent(self) -> AgentExecutor:
        """
        Create LangChain ReAct agent (for future use)
        
        Returns:
            AgentExecutor instance
        """
        # Define agent prompt
        template = """You are a YouTube downloader assistant.

You have access to the following tools:
{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought: {agent_scratchpad}
"""
        
        prompt = PromptTemplate.from_template(template)
        
        agent = create_react_agent(self.llm, self.tools, prompt)
        
        agent_executor = AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5,
        )
        
        return agent_executor

    def _send_feedback(self, channel_id: str, message: str, thread_ts: str) -> None:
        """Send feedback via callback if available"""
        if self.feedback_callback:
            try:
                self.feedback_callback(channel_id, message, thread_ts)
            except Exception as e:
                logger.error(f"Failed to send feedback: {e}")

    def process_message(
        self,
        channel_id: str,
        user_id: str,
        message: str,
        thread_ts: str
    ) -> dict[str, Any]:
        """
        Process a Slack message and handle YouTube downloads
        
        Args:
            channel_id: Slack channel ID
            user_id: User who sent the message
            message: Message text
            thread_ts: Thread timestamp for responses
            
        Returns:
            Dictionary with processing results
        """
        logger.info(f"Processing message from {user_id} in {channel_id}")
        
        try:
            # Step 1: Extract URLs and check intent
            extraction_result = self.url_chain.extract(message)
            urls = extraction_result["urls"]
            download_intent = extraction_result["download_intent"]
            
            if not urls:
                logger.debug("No YouTube URLs found")
                return {
                    "success": True,
                    "action": "none",
                    "message": "No YouTube URLs found"
                }
            
            logger.info(
                f"Found {len(urls)} URL(s), download intent: {download_intent}"
            )
            
            # If no explicit download intent, check if it's just a URL
            if not download_intent and len(message.split()) <= 3:
                download_intent = True
                logger.info("Assuming download intent from standalone URL")
            
            if not download_intent:
                logger.info("No download intent detected")
                return {
                    "success": True,
                    "action": "none",
                    "message": "URLs found but no download intent"
                }
            
            # Step 2: Download each URL
            results = []
            for url in urls:
                result = self._download_video(channel_id, url, thread_ts)
                results.append(result)
            
            success_count = sum(1 for r in results if r.get("success"))
            
            return {
                "success": True,
                "action": "download",
                "total": len(urls),
                "successful": success_count,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            self._send_feedback(
                channel_id,
                f"❌ An error occurred: {str(e)}",
                thread_ts
            )
            return {
                "success": False,
                "error": str(e)
            }

    def _download_video(
        self,
        channel_id: str,
        url: str,
        thread_ts: str
    ) -> dict[str, Any]:
        """
        Download a single video using the tool
        
        Args:
            channel_id: Slack channel for feedback
            url: YouTube URL
            thread_ts: Thread timestamp
            
        Returns:
            Download result dictionary
        """
        logger.info(f"Downloading: {url}")
        
        # Send starting feedback
        self._send_feedback(
            channel_id,
            f"⏳ Downloading video...\n{url}",
            thread_ts
        )
        
        # Use the YouTube download tool
        download_tool = self.tools[0]  # YouTubeDownloadTool
        
        try:
            import json
            result_json = download_tool.run(url)
            result = json.loads(result_json)
            
            if result.get("success"):
                # Send success feedback
                title = result.get("title", "Unknown")
                file_path = result.get("file_path", "")
                file_name = file_path.split("/")[-1] if file_path else "Unknown"
                
                self._send_feedback(
                    channel_id,
                    f"✅ Download complete!\n*{title}*\n📁 `{file_name}`",
                    thread_ts
                )
                
                return {
                    "success": True,
                    "url": url,
                    "title": title,
                    "file_path": file_path
                }
            else:
                # Send failure feedback
                error_msg = result.get("message", "Unknown error")
                self._send_feedback(
                    channel_id,
                    f"❌ Download failed: {error_msg}\n{url}",
                    thread_ts
                )
                
                return {
                    "success": False,
                    "url": url,
                    "error": error_msg
                }
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Download failed: {error_msg}", exc_info=True)
            
            self._send_feedback(
                channel_id,
                f"❌ Download failed: {error_msg}\n{url}",
                thread_ts
            )
            
            return {
                "success": False,
                "url": url,
                "error": error_msg
            }

