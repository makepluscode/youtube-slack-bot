"""Slack Socket Mode handler for receiving messages"""

import logging
from typing import Callable, Optional

from slack_sdk import WebClient
from slack_sdk.socket_mode import SocketModeClient
from slack_sdk.socket_mode.request import SocketModeRequest
from slack_sdk.socket_mode.response import SocketModeResponse

from .config import Settings

logger = logging.getLogger(__name__)


class SlackHandler:
    """Handles Slack Socket Mode connections and message events"""

    def __init__(self, settings: Settings):
        """
        Initialize the Slack handler

        Args:
            settings: Application settings containing Slack tokens
        """
        self.settings = settings
        self.web_client = WebClient(token=settings.slack_bot_token)
        self.socket_client: Optional[SocketModeClient] = None
        self.message_callback: Optional[Callable] = None
        self.bot_user_id: Optional[str] = None
        self._get_bot_user_id()

    def _get_bot_user_id(self) -> None:
        """Get the bot's user ID to filter out its own messages"""
        try:
            response = self.web_client.auth_test()
            self.bot_user_id = response["user_id"]
            logger.info(f"Bot User ID: {self.bot_user_id}")
        except Exception as e:
            logger.error(f"Failed to get bot user ID: {e}")
            raise

    def set_message_callback(self, callback: Callable) -> None:
        """
        Set the callback function for processing messages

        Args:
            callback: Function that takes (channel_id, user_id, text, ts) as parameters
        """
        self.message_callback = callback

    def _handle_message_event(self, client: SocketModeClient, req: SocketModeRequest) -> None:
        """
        Handle incoming message events from Slack

        Args:
            client: Socket mode client
            req: Socket mode request containing the event
        """
        # Acknowledge the request immediately
        response = SocketModeResponse(envelope_id=req.envelope_id)
        client.send_socket_mode_response(response)

        # Process the event
        if req.type == "events_api":
            event = req.payload.get("event", {})
            event_type = event.get("type")

            if event_type == "message":
                # Filter out bot messages and message changes
                if event.get("subtype") in ["bot_message", "message_changed"]:
                    return

                # Filter out messages from the bot itself (unless it's a test message)
                user_id = event.get("user")
                text = event.get("text", "")

                # Allow test messages from bot (with [TEST] marker)
                is_test_message = "[TEST]" in text

                if user_id == self.bot_user_id and not is_test_message:
                    logger.debug("Ignoring message from bot itself")
                    return

                channel_id = event.get("channel")
                ts = event.get("ts")

                # Check if we should monitor this channel
                monitored_channels = self.settings.monitored_channels
                if monitored_channels and channel_id not in monitored_channels:
                    logger.debug(f"Ignoring message from non-monitored channel: {channel_id}")
                    return

                logger.info(f"Received message in channel {channel_id} from user {user_id}")

                # Call the message callback if set
                if self.message_callback:
                    try:
                        self.message_callback(channel_id, user_id, text, ts)
                    except Exception as e:
                        logger.error(f"Error in message callback: {e}", exc_info=True)

    def send_message(
        self, channel_id: str, text: str, thread_ts: Optional[str] = None
    ) -> dict:
        """
        Send a message to a Slack channel

        Args:
            channel_id: The channel ID to send the message to
            text: The message text
            thread_ts: Optional thread timestamp to reply in a thread

        Returns:
            The response from Slack API
        """
        try:
            response = self.web_client.chat_postMessage(
                channel=channel_id, text=text, thread_ts=thread_ts
            )
            logger.debug(f"Message sent to {channel_id}: {text[:50]}...")
            return response
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            raise

    def start(self) -> None:
        """Start the Socket Mode connection"""
        try:
            self.socket_client = SocketModeClient(
                app_token=self.settings.slack_app_token, web_client=self.web_client
            )

            # Register event handlers
            self.socket_client.socket_mode_request_listeners.append(self._handle_message_event)

            logger.info("Starting Slack Socket Mode connection...")
            self.socket_client.connect()

            logger.info("✅ Successfully connected to Slack!")

        except Exception as e:
            logger.error(f"Failed to start Slack connection: {e}")
            raise

    def stop(self) -> None:
        """Stop the Socket Mode connection"""
        if self.socket_client:
            logger.info("Disconnecting from Slack...")
            self.socket_client.close()
            logger.info("Disconnected from Slack")

    def is_connected(self) -> bool:
        """Check if the Socket Mode client is connected"""
        return self.socket_client is not None and self.socket_client.is_connected()

