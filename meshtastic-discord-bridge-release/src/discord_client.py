"""Discord bot client for sending messages to Discord channels."""

import logging
import asyncio
from datetime import datetime
from typing import Optional, Callable

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)


class DiscordClient:
    """Discord bot client for sending Meshtastic messages to Discord."""

    def __init__(self, bot_token: str, channel_id: int):
        """Initialize the Discord client.
        
        Args:
            bot_token: Discord bot token
            channel_id: Discord channel ID to send messages to
        """
        self.bot_token = bot_token
        self.channel_id = channel_id
        self.ready = False
        
        # Callbacks for Meshtastic operations
        self.get_node_info_callback: Optional[Callable] = None
        self.send_mesh_message_callback: Optional[Callable] = None
        self.list_nodes_callback: Optional[Callable] = None
        
        # Set up intents
        intents = discord.Intents.default()
        intents.message_content = True
        
        # Create bot instance
        self.bot = commands.Bot(command_prefix='!', intents=intents)
        
        # Set up event handlers
        self.bot.event(self.on_ready)
        self.bot.event(self.on_error)
        
        # Register commands
        self._register_commands()
        
        self.target_channel: Optional[discord.TextChannel] = None
    
    def set_meshtastic_callbacks(self,
                                  get_node_info: Callable,
                                  send_message: Callable,
                                  list_nodes: Callable):
        """Set callback functions for Meshtastic operations.
        
        Args:
            get_node_info: Function to get connected node information
            send_message: Function to send message to mesh
            list_nodes: Function to list all nodes on mesh
        """
        self.get_node_info_callback = get_node_info
        self.send_mesh_message_callback = send_message
        self.list_nodes_callback = list_nodes
        logger.info("Meshtastic callbacks registered")
    
    def _register_commands(self):
        """Register Discord bot commands."""
        
        @self.bot.group(name='mesh', help='Meshtastic mesh network commands', invoke_without_command=True)
        async def mesh(ctx):
            """Mesh command group."""
            if ctx.channel.id != self.channel_id:
                return
            
            # If called without subcommand, show help
            await ctx.send_help(ctx.command)
        
        @mesh.command(name='info', help='Get information about the connected Meshtastic node')
        async def info(ctx):
            """Get node info command."""
            if ctx.channel.id != self.channel_id:
                return
            
            if not self.get_node_info_callback:
                await ctx.send("❌ Meshtastic connection not available")
                return
            
            try:
                node_info = self.get_node_info_callback()
                
                if node_info:
                    embed = discord.Embed(
                        title="📡 Connected Node Information",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )
                    
                    user = node_info.get('user', {})
                    position = node_info.get('position', {})
                    metrics = node_info.get('deviceMetrics', {})
                    
                    # Basic info
                    embed.add_field(name="Node ID", value=f"`{user.get('id', 'Unknown')}`", inline=True)
                    embed.add_field(name="Long Name", value=user.get('longName', 'Unknown'), inline=True)
                    embed.add_field(name="Short Name", value=user.get('shortName', 'Unknown'), inline=True)
                    embed.add_field(name="Hardware", value=user.get('hwModel', 'Unknown'), inline=True)
                    
                    # Metrics if available
                    if metrics:
                        battery = metrics.get('batteryLevel')
                        voltage = metrics.get('voltage')
                        if battery is not None:
                            embed.add_field(name="Battery", value=f"{battery}%", inline=True)
                        if voltage is not None:
                            embed.add_field(name="Voltage", value=f"{voltage:.2f}V", inline=True)
                    
                    # Position if available
                    if position:
                        lat = position.get('latitude')
                        lon = position.get('longitude')
                        alt = position.get('altitude')
                        if lat and lon:
                            embed.add_field(name="📍 Location", value=f"[{lat:.6f}, {lon:.6f}](https://www.google.com/maps?q={lat},{lon})", inline=False)
                        if alt is not None:
                            embed.add_field(name="Altitude", value=f"{alt}m", inline=True)
                    
                    embed.set_footer(text="Meshtastic Network")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Could not retrieve node information")
                    
            except Exception as e:
                logger.error(f"Error in info command: {e}", exc_info=True)
                await ctx.send("❌ Error retrieving node information")
        
        @mesh.command(name='send', help='Send a message to the mesh network (max 240 chars)')
        async def send(ctx, *, message: str):
            """Send message to mesh command."""
            if ctx.channel.id != self.channel_id:
                return
            
            if not self.send_mesh_message_callback:
                await ctx.send("❌ Meshtastic connection not available")
                return
            
            # Check message length
            if len(message) > 240:
                await ctx.send(f"❌ Message too long! **{len(message)}/240** characters\nPlease shorten your message.")
                return
            
            try:
                # Send message to mesh
                success = self.send_mesh_message_callback(message)
                
                if success:
                    embed = discord.Embed(
                        title="📡 Message Sent to Mesh",
                        description=f"```{message}```",
                        color=discord.Color.green(),
                        timestamp=datetime.utcnow()
                    )
                    embed.add_field(name="Sent by", value=ctx.author.mention, inline=True)
                    embed.add_field(name="Length", value=f"{len(message)}/240", inline=True)
                    embed.set_footer(text="Meshtastic Network")
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ Failed to send message to mesh network")
                    
            except Exception as e:
                logger.error(f"Error in send command: {e}", exc_info=True)
                await ctx.send("❌ Error sending message to mesh network")
        
        @mesh.command(name='nodes', help='List all nodes visible on the mesh network')
        async def nodes(ctx):
            """List nodes command."""
            if ctx.channel.id != self.channel_id:
                return
            
            if not self.list_nodes_callback:
                await ctx.send("❌ Meshtastic connection not available")
                return
            
            try:
                nodes_list = self.list_nodes_callback()
                
                if nodes_list:
                    embed = discord.Embed(
                        title="📡 Mesh Network Nodes",
                        description=f"Found **{len(nodes_list)}** nodes on the network",
                        color=discord.Color.blue(),
                        timestamp=datetime.utcnow()
                    )
                    
                    # Sort by SNR (signal strength)
                    sorted_nodes = sorted(
                        nodes_list,
                        key=lambda x: x.get('snr', -999),
                        reverse=True
                    )
                    
                    # Add up to 25 nodes (Discord limit)
                    for i, node in enumerate(sorted_nodes[:25]):
                        user = node.get('user', {})
                        node_id = user.get('id', 'Unknown')
                        long_name = user.get('longName', 'Unknown')
                        short_name = user.get('shortName', '???')
                        hw_model = user.get('hwModel', 'Unknown')
                        snr = node.get('snr')
                        hops = node.get('hopsAway', '?')
                        
                        node_info = f"**{long_name}** `({short_name})`\n"
                        node_info += f"ID: `{node_id}`\n"
                        node_info += f"HW: {hw_model}\n"
                        if snr is not None:
                            node_info += f"SNR: {snr:.1f} dB | "
                        node_info += f"Hops: {hops}"
                        
                        embed.add_field(
                            name=f"#{i+1}",
                            value=node_info,
                            inline=True
                        )
                    
                    if len(nodes_list) > 25:
                        embed.set_footer(text=f"Showing 25 of {len(nodes_list)} nodes • Meshtastic Network")
                    else:
                        embed.set_footer(text="Meshtastic Network")
                    
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("❌ No nodes found on the network")
                    
            except Exception as e:
                logger.error(f"Error in nodes command: {e}", exc_info=True)
                await ctx.send("❌ Error retrieving node list")
        
        @mesh.command(name='help', help='Show mesh network commands')
        async def help_command(ctx):
            """Help command."""
            if ctx.channel.id != self.channel_id:
                return
            
            embed = discord.Embed(
                title="🤖 Meshtastic Bridge Commands",
                description="Control the mesh network from Discord",
                color=discord.Color.gold(),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="!mesh info",
                value="Get information about the connected node",
                inline=False
            )
            embed.add_field(
                name="!mesh send <message>",
                value="Send a message to the mesh (max 240 chars)\nExample: `!mesh send Hello from Discord!`",
                inline=False
            )
            embed.add_field(
                name="!mesh nodes",
                value="List all visible nodes on the network",
                inline=False
            )
            embed.add_field(
                name="!mesh help",
                value="Show this help message",
                inline=False
            )
            
            embed.set_footer(text="Meshtastic Discord Bridge")
            await ctx.send(embed=embed)
        
    async def on_ready(self):
        """Handle bot ready event."""
        logger.info(f"Discord bot logged in as {self.bot.user}")
        
        # Get the target channel
        self.target_channel = self.bot.get_channel(self.channel_id)
        
        if self.target_channel:
            logger.info(f"Target channel found: #{self.target_channel.name}")
            self.ready = True
            
            # Send a startup message
            try:
                await self.target_channel.send(
                    "🟢 **Meshtastic Bridge Online**\n"
                    f"Connected and monitoring mesh network.\n"
                    f"Type `!mesh help` for available commands.\n"
                    f"Started at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                )
            except Exception as e:
                logger.error(f"Error sending startup message: {e}")
        else:
            logger.error(f"Could not find channel with ID {self.channel_id}")
            self.ready = False
    
    async def on_error(self, event: str, *args, **kwargs):
        """Handle bot errors.
        
        Args:
            event: Event name where error occurred
        """
        logger.error(f"Discord bot error in {event}", exc_info=True)
    
    async def start(self):
        """Start the Discord bot."""
        try:
            logger.info("Starting Discord bot...")
            await self.bot.start(self.bot_token)
        except Exception as e:
            logger.error(f"Failed to start Discord bot: {e}")
            raise
    
    async def stop(self):
        """Stop the Discord bot."""
        try:
            logger.info("Stopping Discord bot...")
            
            if self.ready and self.target_channel:
                try:
                    await self.target_channel.send(
                        "🔴 **Meshtastic Bridge Offline**\n"
                        f"Stopped at: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC"
                    )
                except Exception as e:
                    logger.error(f"Error sending shutdown message: {e}")
            
            await self.bot.close()
            logger.info("Discord bot stopped")
        except Exception as e:
            logger.error(f"Error stopping Discord bot: {e}")
    
    def is_ready(self) -> bool:
        """Check if bot is ready to send messages.
        
        Returns:
            True if ready, False otherwise
        """
        return self.ready and self.target_channel is not None
    
    async def send_message(self, content: str, embed: Optional[discord.Embed] = None):
        """Send a message to the Discord channel.
        
        Args:
            content: Message content
            embed: Optional embed to send with the message
        """
        if not self.is_ready():
            logger.warning("Discord bot not ready, cannot send message")
            return
        
        try:
            if embed:
                await self.target_channel.send(content=content, embed=embed)
            else:
                await self.target_channel.send(content=content)
            logger.debug(f"Sent message to Discord: {content[:50]}...")
        except Exception as e:
            logger.error(f"Error sending message to Discord: {e}")
    
    async def send_direct_message(self, message_data: dict):
        """Send a direct message from Meshtastic to Discord.
        
        Args:
            message_data: Dictionary containing message information
        """
        try:
            from_id = message_data.get('from_id', 'Unknown')
            text = message_data.get('text', '')
            timestamp = message_data.get('timestamp', int(datetime.utcnow().timestamp()))
            
            # Convert timestamp to datetime
            dt = datetime.fromtimestamp(timestamp)
            
            # Create embed for better formatting
            embed = discord.Embed(
                title="💬 Mesh Message",
                description=text,
                color=discord.Color.blue(),
                timestamp=dt
            )
            embed.add_field(name="From", value=from_id, inline=True)
            embed.set_footer(text="Meshtastic Network")
            
            await self.send_message(content="", embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending direct message to Discord: {e}")
    

    async def send_telemetry(self, message_data: dict):
        """Send device telemetry to Discord.
        
        Args:
            message_data: Dictionary containing telemetry information
        """
        try:
            from_id = message_data.get('from_id', 'Unknown')
            timestamp = message_data.get('timestamp', int(datetime.utcnow().timestamp()))
            
            # Convert timestamp to datetime
            dt = datetime.fromtimestamp(timestamp)
            
            # Extract telemetry values
            battery = message_data.get('battery_level')
            voltage = message_data.get('voltage')
            channel_util = message_data.get('channel_utilization')
            air_util = message_data.get('air_util_tx')
            uptime = message_data.get('uptime_seconds')
            
            # Build description
            desc_parts = []
            
            if battery is not None and voltage is not None:
                desc_parts.append(f"🔋 **Battery:** {battery}% ({voltage:.2f}V)")
            elif battery is not None:
                desc_parts.append(f"🔋 **Battery:** {battery}%")
            elif voltage is not None:
                desc_parts.append(f"⚡ **Voltage:** {voltage:.2f}V")
            
            if channel_util is not None:
                desc_parts.append(f"📡 **Channel Usage:** {channel_util:.1f}%")
            
            if air_util is not None:
                desc_parts.append(f"📶 **Air Utilization:** {air_util*100:.2f}%")
            
            if uptime is not None:
                # Format uptime nicely
                hours = uptime // 3600
                minutes = (uptime % 3600) // 60
                if hours > 0:
                    uptime_str = f"{hours}h {minutes}m"
                else:
                    uptime_str = f"{minutes}m"
                desc_parts.append(f"⏱️ **Uptime:** {uptime_str}")
            
            description = "\n".join(desc_parts) if desc_parts else "No metrics available"
            
            # Create embed
            embed = discord.Embed(
                title="📊 Device Telemetry",
                description=description,
                color=discord.Color.purple(),
                timestamp=dt
            )
            embed.add_field(name="Device", value=from_id, inline=True)
            embed.set_footer(text="Meshtastic Telemetry")
            
            await self.send_message(content="", embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending telemetry to Discord: {e}")
    
    async def send_error_notification(self, error_message: str):
        """Send an error notification to Discord.
        
        Args:
            error_message: Error message to send
        """
        try:
            embed = discord.Embed(
                title="⚠️ Bridge Error",
                description=error_message,
                color=discord.Color.red(),
                timestamp=datetime.utcnow()
            )
            
            await self.send_message(content="", embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending error notification to Discord: {e}")
