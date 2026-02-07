# Contributing to Meshtastic Discord Bridge

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on what is best for the community
- Show empathy towards other community members

## How to Contribute

### Reporting Bugs

Before creating bug reports, please check existing issues to avoid duplicates. When creating a bug report, include:

- Clear and descriptive title
- Exact steps to reproduce the problem
- Expected behavior vs actual behavior
- Screenshots if applicable
- Environment details (OS, Python version, Docker version)
- Relevant logs

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- Clear and descriptive title
- Detailed description of the proposed feature
- Explain why this enhancement would be useful
- Possible implementation approach

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test your changes thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

#### Pull Request Guidelines

- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Keep PRs focused on a single feature/fix
- Write clear commit messages
- Ensure all tests pass

## Development Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- A Meshtastic device
- Discord bot for testing

### Setting Up Development Environment

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/meshtastic-discord-bridge.git
cd meshtastic-discord-bridge

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env
# Edit .env with your test credentials

# Run the application
python src/main.py
```

### Code Style

- Follow PEP 8 style guide
- Use type hints where applicable
- Add docstrings to all functions and classes
- Keep functions focused and small
- Use meaningful variable names

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## Project Structure

```
src/
├── main.py              # Application entry point
├── config.py            # Configuration management
├── discord_client.py    # Discord bot implementation
├── meshtastic_client.py # Meshtastic interface
└── message_handler.py   # Message routing logic
```

## Adding New Features

### Adding a New Message Type

1. Update `meshtastic_client.py` to handle the new port num
2. Add processing logic in `_process_packet()`
3. Create a display method in `discord_client.py`
4. Route the message in `message_handler.py`
5. Add tests
6. Update documentation

### Adding a New Discord Command

1. Add command in `discord_client.py` `_register_commands()`
2. Add callback method in `meshtastic_client.py` if needed
3. Wire callback in `main.py` `_setup_callbacks()`
4. Update README with new command
5. Add tests

## Questions?

Feel free to open an issue for questions or join the discussion board.

Thank you for contributing! 🎉
