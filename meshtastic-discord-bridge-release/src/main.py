"""Main application entry point for Meshtastic Discord Bridge."""

import asyncio
import logging
import signal
import sys
import time
from threading import Thread

from config import get_config
from meshtastic_client import MeshtasticClient
from discord_client import DiscordClient
from message_handler import MessageHandler


# Set up logging
def setup_logging(log_level: str):
    """Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


logger = logging.getLogger(__name__)


class MeshtasticDiscordBridge:
    """Main application class for the Meshtastic Discord Bridge."""

    def __init__(self):
        """Initialize the bridge application."""
        self.config = get_config()
        self.running = True
        self.discord_client: DiscordClient = None
        self.meshtastic_client: MeshtasticClient = None
        self.message_handler: MessageHandler = None
        self.event_loop: asyncio.AbstractEventLoop = None
        
    async def start(self):
        """Start the bridge application."""
        logger.info("Starting Meshtastic Discord Bridge...")
        logger.info(f"Configuration: {self.config}")
        
        try:
            # Create Discord client
            self.discord_client = DiscordClient(
                bot_token=self.config.discord_bot_token,
                channel_id=self.config.discord_channel_id
            )
            
            # Create message handler
            self.message_handler = MessageHandler(self.discord_client)
            
            # Get the current event loop
            self.event_loop = asyncio.get_running_loop()
            self.message_handler.set_event_loop(self.event_loop)
            
            # Start Discord bot in the background
            discord_task = asyncio.create_task(self.discord_client.start())
            
            # Wait for Discord bot to be ready
            logger.info("Waiting for Discord bot to be ready...")
            max_wait = 30
            waited = 0
            while not self.discord_client.is_ready() and waited < max_wait:
                await asyncio.sleep(1)
                waited += 1
            
            if not self.discord_client.is_ready():
                raise RuntimeError("Discord bot failed to start within 30 seconds")
            
            logger.info("Discord bot is ready")
            
            # Start Meshtastic client in a separate thread
            self.start_meshtastic_client()
            
            # Give Meshtastic a moment to connect
            await asyncio.sleep(2)
            
            # Set up command callbacks for Discord
            self._setup_callbacks()
            
            self.running = True
            logger.info("Meshtastic Discord Bridge is running")
            
            # Keep the application running
            await self.run_forever()
            
        except Exception as e:
            logger.error(f"Error starting bridge: {e}", exc_info=True)
            await self.shutdown()
            raise
    
    def _setup_callbacks(self):
        """Set up callback functions for Discord commands."""
        logger.info("Setting up Discord command callbacks...")
        self.discord_client.set_meshtastic_callbacks(
            get_node_info=self._get_node_info,
            send_message=self._send_mesh_message,
            list_nodes=self._list_nodes
        )
        logger.info("Discord commands ready!")
    
    def _get_node_info(self):
        """Get node info callback."""
        if self.meshtastic_client and self.meshtastic_client.is_connected():
            return self.meshtastic_client.get_node_info()
        return None
    
    def _send_mesh_message(self, message: str) -> bool:
        """Send message to mesh callback."""
        if self.meshtastic_client and self.meshtastic_client.is_connected():
            return self.meshtastic_client.send_text(message)
        return False
    
    def _list_nodes(self):
        """List nodes callback."""
        if self.meshtastic_client and self.meshtastic_client.is_connected():
            return self.meshtastic_client.list_nodes()
        return []
    
    def start_meshtastic_client(self):
        """Start the Meshtastic client in a separate thread."""
        def run_meshtastic():
            """Run Meshtastic client with auto-reconnect."""
            while self.running:
                try:
                    # Create Meshtastic client with message callback
                    self.meshtastic_client = MeshtasticClient(
                        device_path=self.config.meshtastic_device,
                        message_callback=self.message_handler.handle_message
                    )
                    
                    # Try to connect
                    if self.meshtastic_client.connect():
                        logger.info("Meshtastic client connected successfully")
                        
                        # Update Discord callbacks now that we're connected
                        if self.discord_client and self.discord_client.is_ready():
                            self._setup_callbacks()
                        
                        # Keep the connection alive
                        while self.running and self.meshtastic_client.is_connected():
                            time.sleep(1)
                        
                        if not self.running:
                            break
                    
                    # Connection lost or failed
                    logger.warning(
                        f"Meshtastic connection lost. "
                        f"Retrying in {self.config.reconnect_delay} seconds..."
                    )
                    
                    # Send error notification to Discord
                    if self.message_handler:
                        self.message_handler.send_error_to_discord(
                            "Meshtastic device connection lost. Attempting to reconnect..."
                        )
                    
                except Exception as e:
                    logger.error(f"Error in Meshtastic client: {e}", exc_info=True)
                
                finally:
                    if self.meshtastic_client:
                        self.meshtastic_client.disconnect()
                
                # Wait before reconnecting
                if self.running:
                    time.sleep(self.config.reconnect_delay)
        
        # Start Meshtastic client thread
        meshtastic_thread = Thread(target=run_meshtastic, daemon=True)
        meshtastic_thread.start()
        logger.info("Meshtastic client thread started")
    
    async def run_forever(self):
        """Keep the application running."""
        try:
            while self.running:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Application loop cancelled")
    
    async def shutdown(self):
        """Shut down the bridge application."""
        logger.info("Shutting down Meshtastic Discord Bridge...")
        
        self.running = False
        
        # Stop Meshtastic client
        if self.meshtastic_client:
            self.meshtastic_client.disconnect()
        
        # Stop Discord client
        if self.discord_client:
            await self.discord_client.stop()
        
        logger.info("Shutdown complete")


async def main():
    """Main entry point."""
    # Load configuration
    config = get_config()
    
    # Set up logging
    setup_logging(config.log_level)
    
    logger.info("=" * 60)
    logger.info("Meshtastic Discord Bridge")
    logger.info("=" * 60)
    
    # Create and start the bridge
    bridge = MeshtasticDiscordBridge()
    
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        asyncio.create_task(bridge.shutdown())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await bridge.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
        await bridge.shutdown()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        await bridge.shutdown()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
