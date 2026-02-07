"""Meshtastic device client for reading messages from the mesh network."""

import logging
import time
from typing import Callable, Optional, Any
from threading import Event

import meshtastic
import meshtastic.serial_interface

logger = logging.getLogger(__name__)


class MeshtasticClient:
    """Client for connecting to and reading from a Meshtastic device."""

    def __init__(self, device_path: str, message_callback: Callable[[dict], None]):
        """Initialize the Meshtastic client.
        
        Args:
            device_path: Path to the serial device (e.g., /dev/ttyACM0)
            message_callback: Callback function to handle received messages
        """
        self.device_path = device_path
        self.message_callback = message_callback
        self.interface: Optional[meshtastic.serial_interface.SerialInterface] = None
        self.connected = False
        self.stop_event = Event()
        
    def connect(self) -> bool:
        """Connect to the Meshtastic device.
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            logger.info(f"Connecting to Meshtastic device at {self.device_path}...")
            
            # Import pub for subscriptions
            from pubsub import pub
            
            # Subscribe to message events BEFORE creating interface
            pub.subscribe(self._on_receive, "meshtastic.receive")
            
            # Create serial interface
            self.interface = meshtastic.serial_interface.SerialInterface(
                devPath=self.device_path,
                noProto=False
            )
            
            self.connected = True
            logger.info("Successfully connected to Meshtastic device")
            
            # Get node info
            node_info = self.interface.getMyNodeInfo()
            if node_info:
                logger.info(f"Connected to node: {node_info}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Meshtastic device: {e}")
            self.connected = False
            return False
    
    def _on_receive(self, packet: dict, interface=None) -> None:
        """Handle received packets from Meshtastic device.
        
        Args:
            packet: Received packet data
            interface: Meshtastic interface instance (optional)
        """
        try:
            logger.debug(f"Received packet: {packet}")
            
            # Process the packet and extract relevant information
            processed_message = self._process_packet(packet)
            
            if processed_message:
                # Call the callback with the processed message
                self.message_callback(processed_message)
                
        except Exception as e:
            logger.error(f"Error processing received packet: {e}", exc_info=True)
    
    def _process_packet(self, packet: dict) -> Optional[dict]:
        """Process a received packet and extract message information.
        
        Args:
            packet: Raw packet from Meshtastic
            
        Returns:
            Processed message dict or None if not a message we care about
        """
        try:
            # Check if packet has decoded data
            if 'decoded' not in packet:
                logger.debug("Packet has no decoded data, skipping")
                return None
            
            decoded = packet['decoded']
            portnum = decoded.get('portnum')
            
            # Get sender information
            from_id = packet.get('fromId', 'Unknown')
            from_num = packet.get('from', 0)
            to_id = packet.get('toId', 'Unknown')
            
            # Try to get the friendly node name
            from_name = from_id
            if self.interface and from_num:
                try:
                    logger.debug(f"Looking up node {from_num} (ID: {from_id})")
                    
                    # Try lookup by string ID first, then by number
                    node = self.interface.nodes.get(from_id) or self.interface.nodes.get(from_num)
                    if node:
                        if 'user' in node:
                            longName = node['user'].get('longName')
                            shortName = node['user'].get('shortName')
                            # Prefer longName, fallback to shortName, then ID
                            from_name = longName or shortName or from_id
                            logger.info(f"Resolved node name: {from_id} -> {from_name}")
                except Exception as e:
                    logger.debug(f"Error getting node name: {e}")
            
            # Get timestamp
            rx_time = packet.get('rxTime', int(time.time()))
            
            # Handle TEXT_MESSAGE_APP (direct messages)
            if portnum == 'TEXT_MESSAGE_APP':
                text = decoded.get('text', '')
                
                return {
                    'type': 'direct_message',
                    'from_id': from_name,
                    'from_num': from_num,
                    'to_id': to_id,
                    'text': text,
                    'timestamp': rx_time,
                    'raw_packet': packet
                }
            
            # Handle TELEMETRY_APP (device telemetry)
            elif portnum == 'TELEMETRY_APP':
                telemetry_data = decoded.get('telemetry', {})
                device_metrics = telemetry_data.get('deviceMetrics')
                
                if device_metrics:
                    return {
                        'type': 'telemetry',
                        'from_id': from_name,
                        'from_num': from_num,
                        'battery_level': device_metrics.get('batteryLevel'),
                        'voltage': device_metrics.get('voltage'),
                        'channel_utilization': device_metrics.get('channelUtilization'),
                        'air_util_tx': device_metrics.get('airUtilTx'),
                        'uptime_seconds': device_metrics.get('uptimeSeconds'),
                        'timestamp': rx_time,
                        'raw_packet': packet
                    }
                else:
                    logger.debug(f"Telemetry packet from {from_id} has no device metrics")
                    return None
            
            # Handle NODEINFO_APP (node information updates)
            elif portnum == 'NODEINFO_APP':
                logger.debug(f"Received node info update from {from_id}")
                return None
            
            # Handle POSITION_APP (GPS position updates)
            elif portnum == 'POSITION_APP':
                logger.debug(f"Received position update from {from_id}")
                return None
            
            # Other message types we don't handle yet
            else:
                logger.debug(f"Unhandled portnum: {portnum}")
                return None
                
        except Exception as e:
            logger.error(f"Error processing packet: {e}", exc_info=True)
            return None
    
    def disconnect(self) -> None:
        """Disconnect from the Meshtastic device."""
        try:
            if self.interface:
                logger.info("Disconnecting from Meshtastic device...")
                self.interface.close()
                self.interface = None
            self.connected = False
            logger.info("Disconnected from Meshtastic device")
        except Exception as e:
            logger.error(f"Error disconnecting from Meshtastic device: {e}")
    
    def is_connected(self) -> bool:
        """Check if connected to the device.
        
        Returns:
            True if connected, False otherwise
        """
        return self.connected and self.interface is not None
    
    def send_text(self, text: str, destination: Optional[str] = None) -> bool:
        """Send a text message to the mesh network.
        
        Args:
            text: Message text to send
            destination: Destination node ID (None for broadcast)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            if not self.is_connected():
                logger.error("Cannot send message: not connected to device")
                return False
            
            logger.info(f"Sending message to mesh: {text[:50]}...")
            
            if destination:
                self.interface.sendText(text, destinationId=destination)
            else:
                self.interface.sendText(text)
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending text message: {e}")
            return False
    
    def get_node_info(self) -> Optional[dict]:
        """Get information about the connected node.
        
        Returns:
            Dictionary containing node information or None
        """
        try:
            if not self.is_connected():
                logger.error("Cannot get node info: not connected to device")
                return None
            
            node_info = self.interface.getMyNodeInfo()
            return node_info
            
        except Exception as e:
            logger.error(f"Error getting node info: {e}")
            return None
    
    def list_nodes(self) -> list:
        """Get list of all nodes visible on the mesh.
        
        Returns:
            List of node dictionaries
        """
        try:
            if not self.is_connected():
                logger.error("Cannot list nodes: not connected to device")
                return []
            
            nodes = []
            for node_id, node_data in self.interface.nodes.items():
                nodes.append(node_data)
            
            return nodes
            
        except Exception as e:
            logger.error(f"Error listing nodes: {e}")
            return []
