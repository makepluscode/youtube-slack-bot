"""Main entry point for the Slack YouTube Downloader Bot (LangChain-based)"""

import logging
import signal
import sys
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import get_settings
from .agents import YouTubeAgent
from .slack_handler import SlackHandler

# Global flag for graceful shutdown
running = True


def setup_logging(settings) -> None:
    """Configure logging with both file and console handlers"""
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create formatters
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    console_formatter = logging.Formatter("%(levelname)s - %(message)s")

    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5  # 10 MB
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, settings.log_level.upper()))
    console_handler.setFormatter(console_formatter)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Reduce noise from external libraries
    logging.getLogger("slack_sdk").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)


def signal_handler(signum, frame):
    """Handle shutdown signals gracefully"""
    global running
    logger = logging.getLogger(__name__)
    logger.info(f"Received signal {signum}, shutting down...")
    running = False


class YouTubeBot:
    """Main bot orchestrator using LangChain Agent"""

    def __init__(self):
        """Initialize the bot with all components"""
        self.settings = get_settings()
        self.logger = logging.getLogger(__name__)

        # Initialize Slack handler
        self.slack_handler = SlackHandler(self.settings)

        # Initialize LangChain Agent with feedback callback
        self.agent = YouTubeAgent(
            settings=self.settings,
            feedback_callback=self.slack_handler.send_message
        )

        # Set up message callback
        self.slack_handler.set_message_callback(self.handle_message)

    def handle_message(self, channel_id: str, user_id: str, text: str, ts: str) -> None:
        """
        Handle incoming Slack messages using LangChain Agent

        Args:
            channel_id: The channel where the message was posted
            user_id: The user who posted the message
            text: The message text
            ts: The message timestamp (for threading)
        """
        self.logger.info(f"Processing message from {user_id} in {channel_id}")

        try:
            # Delegate to LangChain Agent
            result = self.agent.process_message(
                channel_id=channel_id,
                user_id=user_id,
                message=text,
                thread_ts=ts
            )
            
            # Log the result
            if result.get("success"):
                action = result.get("action", "none")
                if action == "download":
                    total = result.get("total", 0)
                    successful = result.get("successful", 0)
                    self.logger.info(
                        f"Agent completed: {successful}/{total} downloads successful"
                    )
                else:
                    self.logger.debug(f"Agent action: {action}")
            else:
                self.logger.error(f"Agent failed: {result.get('error')}")

        except Exception as e:
            self.logger.error(f"Error in message handler: {e}", exc_info=True)
            self.slack_handler.send_message(
                channel_id,
                f"❌ An error occurred: {str(e)}",
                thread_ts=ts,
            )

    def run(self) -> None:
        """Start the bot and keep it running"""
        global running

        self.logger.info("=" * 60)
        self.logger.info("🚀 Starting Slack YouTube Downloader Bot (LangChain)")
        self.logger.info("=" * 60)
        self.logger.info(f"🤖 Using LangChain Agent with {self.settings.ollama_model}")

        # Start Slack connection
        try:
            self.slack_handler.start()

            self.logger.info("✨ Bot is now running and listening for messages...")
            self.logger.info(f"📂 Download directory: {self.settings.download_dir}")
            self.logger.info("Press Ctrl+C to stop")

            # Keep the main thread alive
            while running:
                time.sleep(1)

        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt")
        except Exception as e:
            self.logger.error(f"Fatal error: {e}", exc_info=True)
        finally:
            self.shutdown()

    def shutdown(self) -> None:
        """Gracefully shutdown the bot"""
        self.logger.info("Shutting down bot...")
        self.slack_handler.stop()
        self.logger.info("✅ Bot shutdown complete")


def main():
    """Main entry point"""
    # Load settings first to set up logging
    settings = get_settings()
    setup_logging(settings)

    logger = logging.getLogger(__name__)

    try:
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Create and run bot
        bot = YouTubeBot()
        bot.run()

    except Exception as e:
        logger.error(f"Failed to start bot: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

