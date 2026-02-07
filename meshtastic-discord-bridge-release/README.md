# Meshtastic Discord Bridge

A Python-based bridge that connects your Meshtastic mesh network to Discord, allowing real-time message forwarding and network monitoring.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)

## Features

- 📡 **Bidirectional Messaging**: Send and receive messages between Discord and Meshtastic
- 📊 **Device Telemetry**: Monitor battery levels, signal strength, and network health
- 🔍 **Network Visibility**: View all nodes on your mesh network
- 🤖 **Discord Commands**: Control your mesh network directly from Discord
- 🔄 **Auto-Reconnect**: Automatic recovery from connection failures
- 🐳 **Docker Support**: Easy deployment with Docker Compose

## Screenshots

### Message Forwarding
Messages from the mesh network appear in Discord with sender information and timestamps.

### Telemetry Monitoring
Real-time device metrics including battery, voltage, channel usage, and uptime.

### Discord Commands
Control your mesh network with simple commands:
- `!mesh info` - Get connected node information
- `!mesh send <message>` - Send messages to the mesh
- `!mesh nodes` - List all visible nodes

## Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (recommended)
- A Meshtastic device connected via USB
- Discord bot token and channel ID

## Quick Start with Docker

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/meshtastic-discord-bridge.git
cd meshtastic-discord-bridge
```

### 2. Create Discord Bot

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section
4. Click "Reset Token" and copy your bot token
5. Enable "Message Content Intent" under Privileged Gateway Intents
6. Go to OAuth2 → URL Generator
7. Select scopes: `bot`
8. Select permissions: `Send Messages`, `Embed Links`, `Read Message History`
9. Copy the generated URL and invite the bot to your server

### 3. Get Discord Channel ID

1. Enable Developer Mode in Discord (User Settings → Advanced → Developer Mode)
2. Right-click on your target channel
3. Click "Copy Channel ID"

### 4. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit with your credentials
nano .env
```

Add your Discord credentials:

```env
DISCORD_BOT_TOKEN=your_bot_token_here
DISCORD_CHANNEL_ID=your_channel_id_here
MESHTASTIC_DEVICE=/dev/ttyACM0
LOG_LEVEL=INFO
RECONNECT_DELAY=5
```

### 5. Set Up USB Permissions

Create a udev rule for automatic USB permissions:

```bash
sudo nano /etc/udev/rules.d/99-meshtastic.rules
```

Add these lines:

```
# Meshtastic USB devices
SUBSYSTEM=="tty", ATTRS{idVendor}=="10c4", ATTRS{idProduct}=="ea60", MODE="0666"
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="55d4", MODE="0666"
# Heltec and ESP32 devices
SUBSYSTEM=="tty", ATTRS{idVendor}=="303a", MODE="0666"
```

Reload udev rules:

```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### 6. Start the Bridge

```bash
docker-compose up -d
```

### 7. Check Logs

```bash
docker-compose logs -f
```

You should see:
- Discord bot connecting
- Meshtastic device connecting
- "🟢 Meshtastic Bridge Online" message in Discord

## Manual Installation (Without Docker)

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

### 2. Configure Environment

```bash
cp .env.example .env
nano .env
```

### 3. Run the Application

```bash
python src/main.py
```

## Discord Commands

| Command | Description | Example |
|---------|-------------|---------|
| `!mesh help` | Show all available commands | `!mesh help` |
| `!mesh info` | Get connected node information | `!mesh info` |
| `!mesh send <message>` | Send message to mesh (max 240 chars) | `!mesh send Hello mesh!` |
| `!mesh nodes` | List all visible nodes on network | `!mesh nodes` |

## Configuration Options

| Variable | Description | Default |
|----------|-------------|---------|
| `DISCORD_BOT_TOKEN` | Your Discord bot token | Required |
| `DISCORD_CHANNEL_ID` | Discord channel ID for messages | Required |
| `MESHTASTIC_DEVICE` | Serial device path | `/dev/ttyACM0` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |
| `RECONNECT_DELAY` | Seconds to wait before reconnecting | `5` |

## Troubleshooting

### Permission Denied Error

If you see `Permission denied: '/dev/ttyACM0'`:

```bash
# Quick fix (temporary)
sudo chmod 666 /dev/ttyACM0
docker-compose restart

# Permanent fix
# Follow the udev rule setup in step 5 above
```

### Discord Bot Not Connecting

1. Verify bot token is correct in `.env`
2. Ensure "Message Content Intent" is enabled
3. Check bot has permissions in the Discord channel
4. Review logs: `docker-compose logs -f`

### Meshtastic Device Not Found

```bash
# List available USB devices
ls -la /dev/tty*

# Check which device is your Meshtastic
dmesg | grep tty

# Update MESHTASTIC_DEVICE in .env if needed
```

### Node Names Not Showing

Wait a few minutes for the node database to populate. The bridge needs to receive node info packets from the mesh network.

## Architecture

```
┌─────────────────┐
│   Discord Bot   │
│   (async I/O)   │
└────────┬────────┘
         │
         ├─ Commands (!mesh)
         ├─ Message Display
         └─ Telemetry Display
              │
              ▼
    ┌─────────────────┐
    │ Message Handler │
    │  (Thread-safe)  │
    └────────┬────────┘
             │
             ▼
   ┌───────────────────┐
   │ Meshtastic Client │
   │  (Serial Thread)  │
   └─────────┬─────────┘
             │
             ▼
      /dev/ttyACM0
     (Meshtastic Device)
```

## Development

### Project Structure

```
meshtastic-discord-bridge/
├── src/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration management
│   ├── discord_client.py    # Discord bot & commands
│   ├── meshtastic_client.py # Meshtastic serial interface
│   └── message_handler.py   # Message routing logic
├── docker-compose.yml       # Docker orchestration
├── Dockerfile              # Container definition
├── requirements.txt        # Python dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Supported Message Types

- ✅ Direct Messages (TEXT_MESSAGE_APP)
- ✅ Device Telemetry (TELEMETRY_APP)
- ✅ Node Information (NODEINFO_APP) - logged only
- ✅ Position Updates (POSITION_APP) - logged only

## Supported Meshtastic Devices

All ESP32-based Meshtastic devices are supported:
- Heltec V3, Wireless Tracker, Wireless Stick Lite
- LILYGO T-Beam, T-Echo
- RAK WisBlock Meshtastic
- And more...

## Security Notes

- **Never commit `.env` file** - It contains sensitive credentials
- Bot token grants full access to your Discord bot
- Consider running in a restricted Docker environment
- Review bot permissions regularly

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **Built in collaboration with Claude AI (Sonnet 4.5)** - This project was developed through an interactive collaboration between human expertise and AI assistance
- [Meshtastic Project](https://meshtastic.org/) - The awesome mesh networking platform
- [Discord.py](https://github.com/Rapptz/discord.py) - Discord API wrapper
- Community contributors

## Support

- 🐛 [Report Issues](https://github.com/yourusername/meshtastic-discord-bridge/issues)
- 💬 [Discussions](https://github.com/yourusername/meshtastic-discord-bridge/discussions)
- 📧 Email: your.email@example.com


