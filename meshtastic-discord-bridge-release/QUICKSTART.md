# Quick Start Guide

Get up and running with Meshtastic Discord Bridge in 5 minutes!

## Prerequisites Checklist

- [ ] Meshtastic device connected via USB
- [ ] Discord bot created and invited to server
- [ ] Docker installed (or Python 3.11+)
- [ ] Bot token and channel ID ready

## 60-Second Setup (Docker)

```bash
# 1. Clone repository
git clone https://github.com/yourusername/meshtastic-discord-bridge.git
cd meshtastic-discord-bridge

# 2. Configure
cp .env.example .env
nano .env
# Add: DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID

# 3. Set USB permissions (Linux only)
sudo chmod 666 /dev/ttyACM0

# 4. Start!
docker-compose up -d

# 5. Check status
docker-compose logs -f
```

## Discord Bot Setup (5 steps)

1. Go to [discord.com/developers/applications](https://discord.com/developers/applications)
2. Create "New Application" → Name it → Create
3. Bot section → Reset Token → **Copy token** → Enable "Message Content Intent"
4. OAuth2 → URL Generator → Select `bot` → Permissions: Send Messages, Embed Links → Copy URL → Invite to server
5. Right-click channel → Copy Channel ID

## Commands

| Command | What it does |
|---------|--------------|
| `!mesh help` | Show all commands |
| `!mesh info` | Node details |
| `!mesh send Hi!` | Send to mesh |
| `!mesh nodes` | List all nodes |

## Verify It's Working

✅ See "🟢 Meshtastic Bridge Online" in Discord  
✅ Run `!mesh info` - see your node info  
✅ Send message from another Meshtastic device - see it in Discord

## Troubleshooting

**Permission denied?**
```bash
sudo chmod 666 /dev/ttyACM0
docker-compose restart
```

**Bot not responding?**
- Check "Message Content Intent" is enabled in Discord Developer Portal

**Device not found?**
```bash
ls -la /dev/tty*  # Find your device
# Update MESHTASTIC_DEVICE in .env
```

## Full Documentation

- 📖 [README.md](README.md) - Complete guide
- 🔧 [INSTALL.md](INSTALL.md) - Detailed installation
- 🤝 [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute

---

**Need help?** Open an [issue](https://github.com/yourusername/meshtastic-discord-bridge/issues)
