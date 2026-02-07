# Installation Guide

This guide will walk you through setting up the Meshtastic Discord Bridge from scratch.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Discord Bot Setup](#discord-bot-setup)
3. [Installation Methods](#installation-methods)
   - [Docker (Recommended)](#docker-installation-recommended)
   - [Manual Installation](#manual-installation)
4. [USB Permissions](#usb-permissions)
5. [Configuration](#configuration)
6. [Verification](#verification)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Hardware

- Computer running Linux, macOS, or Windows
- Meshtastic device with USB connection
- USB cable

### Software

**For Docker Installation:**
- Docker (version 20.10+)
- Docker Compose (version 2.0+)

**For Manual Installation:**
- Python 3.11 or higher
- pip (Python package manager)
- git

### Discord

- Discord account
- Server with admin permissions (to add bot)

## Discord Bot Setup

### Step 1: Create Discord Application

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application"
3. Enter a name (e.g., "Meshtastic Bridge")
4. Click "Create"

### Step 2: Configure Bot

1. Navigate to the "Bot" section in the left sidebar
2. Click "Reset Token" and copy the token (save it securely!)
3. **Important:** Enable "Message Content Intent" under Privileged Gateway Intents
4. Save changes

### Step 3: Invite Bot to Server

1. Go to OAuth2 → URL Generator
2. Select scopes:
   - ✅ `bot`
3. Select bot permissions:
   - ✅ Send Messages
   - ✅ Embed Links
   - ✅ Read Message History
   - ✅ View Channels
4. Copy the generated URL
5. Open URL in browser and invite bot to your server

### Step 4: Get Channel ID

1. Enable Developer Mode in Discord:
   - User Settings → Advanced → Developer Mode (toggle ON)
2. Right-click on your target channel
3. Click "Copy Channel ID"
4. Save this ID

## Installation Methods

### Docker Installation (Recommended)

#### 1. Install Docker

**Ubuntu/Debian:**
```bash
# Update package index
sudo apt-get update

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add your user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt-get install docker-compose-plugin

# Log out and back in for group changes to take effect
```

**macOS:**
```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
```

**Windows:**
```bash
# Install Docker Desktop from https://www.docker.com/products/docker-desktop
# Ensure WSL2 is installed
```

#### 2. Clone Repository

```bash
git clone https://github.com/yourusername/meshtastic-discord-bridge.git
cd meshtastic-discord-bridge
```

#### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Add your Discord credentials:
```env
DISCORD_BOT_TOKEN=YOUR_BOT_TOKEN_HERE
DISCORD_CHANNEL_ID=YOUR_CHANNEL_ID_HERE
MESHTASTIC_DEVICE=/dev/ttyACM0
LOG_LEVEL=INFO
RECONNECT_DELAY=5
```

#### 4. Set Up USB Permissions (Linux)

```bash
# Create udev rule
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

Reload rules:
```bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

#### 5. Start the Bridge

```bash
docker-compose up -d
```

#### 6. Check Logs

```bash
docker-compose logs -f
```

You should see:
```
Discord bot logged in as YourBotName
Successfully connected to Meshtastic device
Meshtastic Discord Bridge is running
```

### Manual Installation

#### 1. Install Python

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install python3.11 python3-pip git
```

**macOS:**
```bash
brew install python@3.11
```

**Windows:**
Download and install Python 3.11+ from [python.org](https://www.python.org/downloads/)

#### 2. Clone Repository

```bash
git clone https://github.com/yourusername/meshtastic-discord-bridge.git
cd meshtastic-discord-bridge
```

#### 3. Create Virtual Environment (Optional but Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 4. Install Dependencies

```bash
pip install -r requirements.txt --break-system-packages
```

#### 5. Configure Environment

```bash
cp .env.example .env
nano .env
```

Edit with your credentials (same as Docker method above)

#### 6. Set Up USB Permissions (Linux)

Same as Docker installation Step 4

#### 7. Run the Application

```bash
python src/main.py
```

## USB Permissions

### Finding Your Device

```bash
# List USB devices
ls -la /dev/tty*

# Check system messages
dmesg | grep tty

# Common device names:
# - /dev/ttyACM0 (most Meshtastic devices)
# - /dev/ttyUSB0 (some devices)
# - COM3 (Windows)
```

### Temporary Permission Fix (Linux)

If you get permission errors:
```bash
sudo chmod 666 /dev/ttyACM0
```

**Note:** This is temporary and will reset on reboot. Use udev rules for permanent fix.

### macOS Permissions

macOS usually doesn't require special permissions for USB serial devices.

### Windows Permissions

Windows requires CP210x or CH340 USB drivers:
1. Download drivers from manufacturer website
2. Install and restart computer
3. Check Device Manager to verify device is recognized

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| DISCORD_BOT_TOKEN | Your Discord bot token | - | Yes |
| DISCORD_CHANNEL_ID | Discord channel ID | - | Yes |
| MESHTASTIC_DEVICE | Serial device path | /dev/ttyACM0 | No |
| LOG_LEVEL | Logging verbosity | INFO | No |
| RECONNECT_DELAY | Reconnection delay (seconds) | 5 | No |

### Logging Levels

- `DEBUG` - Detailed information for debugging
- `INFO` - General informational messages (recommended)
- `WARNING` - Warning messages only
- `ERROR` - Error messages only

## Verification

### Check Discord

You should see this message in your Discord channel:
```
🟢 Meshtastic Bridge Online
Connected and monitoring mesh network.
Type !mesh help for available commands.
Started at: YYYY-MM-DD HH:MM:SS UTC
```

### Test Commands

Try these commands in Discord:
```
!mesh help      # Show available commands
!mesh info      # Get node information
!mesh nodes     # List visible nodes
```

### Test Messaging

Send a message from another Meshtastic device. It should appear in Discord within seconds.

## Troubleshooting

### Bot Not Connecting to Discord

**Symptoms:** No startup message in Discord

**Solutions:**
1. Verify bot token is correct in `.env`
2. Check "Message Content Intent" is enabled
3. Verify bot has permissions in the channel
4. Check logs: `docker-compose logs` or `python src/main.py`

### Permission Denied on USB Device

**Symptoms:** Error: `Permission denied: '/dev/ttyACM0'`

**Solutions:**
1. Apply udev rules (see USB Permissions section)
2. Add user to dialout group: `sudo usermod -aG dialout $USER`
3. Log out and log back in
4. Temporary fix: `sudo chmod 666 /dev/ttyACM0`

### Device Not Found

**Symptoms:** `Could not open port /dev/ttyACM0`

**Solutions:**
1. Check device is connected: `ls -la /dev/tty*`
2. Try different device name (/dev/ttyUSB0, etc.)
3. Check `dmesg | grep tty` for device info
4. Update `MESHTASTIC_DEVICE` in `.env`

### Messages Not Appearing in Discord

**Symptoms:** Meshtastic messages don't show up

**Solutions:**
1. Check logs for errors
2. Verify bot has "Send Messages" permission
3. Check channel ID is correct
4. Ensure bot is in the correct server
5. Wait a few minutes for node database to populate

### Docker Container Keeps Restarting

**Symptoms:** Container restarts repeatedly

**Solutions:**
1. Check logs: `docker-compose logs -f`
2. Verify `.env` file exists and is configured
3. Check USB device permissions
4. Ensure device path is correct in `.env`

### Commands Not Working

**Symptoms:** `!mesh` commands don't respond

**Solutions:**
1. Ensure "Message Content Intent" is enabled
2. Check bot has "Read Message History" permission
3. Verify you're using commands in the correct channel
4. Check bot is online in Discord

## Updating

### Docker Installation

```bash
cd meshtastic-discord-bridge
git pull
docker-compose down
docker-compose build
docker-compose up -d
```

### Manual Installation

```bash
cd meshtastic-discord-bridge
git pull
pip install -r requirements.txt --upgrade
# Restart the application
```

## Uninstalling

### Docker Installation

```bash
cd meshtastic-discord-bridge
docker-compose down
cd ..
rm -rf meshtastic-discord-bridge
```

### Manual Installation

```bash
# Deactivate virtual environment if active
deactivate

# Remove directory
cd ..
rm -rf meshtastic-discord-bridge
```

## Getting Help

- 📖 [README](README.md) - General information
- 🐛 [Issues](https://github.com/yourusername/meshtastic-discord-bridge/issues) - Report bugs
- 💬 [Discussions](https://github.com/yourusername/meshtastic-discord-bridge/discussions) - Ask questions

---

