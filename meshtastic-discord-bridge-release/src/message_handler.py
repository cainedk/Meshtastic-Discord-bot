"""Message handler for routing messages between Meshtastic and Discord."""

import logging
import asyncio
from typing import Optional

from discord_client import DiscordClient

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handler for processing and routing Meshtastic messages to Discord."""

    def __init__(self, discord_client: DiscordClient):
        """Initialize the message handler.
        
        Args:
            discord_client: Discord client instance
        """
        self.discord_client = discord_client
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        
    def set_event_loop(self, loop: asyncio.AbstractEventLoop):
        """Set the asyncio event loop for scheduling Discord tasks.
        
        Args:
            loop: Event loop to use for async operations
        """
        self.loop = loop
    
    def handle_message(self, message_data: dict):
        """Handle a message received from Meshtastic.
        
        This is called from the Meshtastic thread, so we need to schedule
        the Discord message sending in the asyncio event loop.
        
        Args:
            message_data: Dictionary containing message information
        """
        try:
            message_type = message_data.get('type')
            
            if not message_type:
                logger.warning("Received message with no type, skipping")
                return
            
            logger.info(f"Handling {message_type} message: {message_data}")
            
            # Schedule the appropriate Discord message based on type
            if message_type == 'direct_message':
                self._schedule_discord_task(
                    self.discord_client.send_direct_message(message_data)
                )
            
            elif message_type == 'telemetry':
                self._schedule_discord_task(
                    self.discord_client.send_telemetry(message_data)
                )
            
            else:
                logger.warning(f"Unknown message type: {message_type}")
                
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
    
    def _schedule_discord_task(self, coro):
        """Schedule a coroutine to run in the asyncio event loop.
        
        Args:
            coro: Coroutine to schedule
        """
        if not self.loop:
            logger.error("Event loop not set, cannot schedule Discord task")
            return
        
        try:
            # Schedule the coroutine in the event loop
            asyncio.run_coroutine_threadsafe(coro, self.loop)
        except Exception as e:
            logger.error(f"Error scheduling Discord task: {e}")
    
    def send_error_to_discord(self, error_message: str):
        """Send an error notification to Discord.
        
        Args:
            error_message: Error message to send
        """
        try:
            self._schedule_discord_task(
                self.discord_client.send_error_notification(error_message)
            )
        except Exception as e:
            logger.error(f"Error sending error notification: {e}")
