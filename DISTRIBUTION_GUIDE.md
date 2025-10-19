# Terminal Chat Client - Distribution Guide

This guide explains how to distribute the Terminal Chat client to your friends.

## Package Files Created

The build process created two distribution files in the `dist/` directory:

1. **terminal_chat_client-1.0.0-py3-none-any.whl** (15KB) - Recommended for distribution
   - Universal wheel file (works on Windows, Linux, and macOS)
   - Easy to install with a single pip command

2. **terminal_chat_client-1.0.0.tar.gz** (18KB) - Source distribution
   - Contains the full source code
   - Backup option if wheel doesn't work

## Distribution Options

### Option 1: Direct File Sharing (Easiest)

**Best for:** Small group of friends, no need for GitHub

1. **Share the wheel file with your friends:**
   - Send them `dist/terminal_chat_client-1.0.0-py3-none-any.whl` via email, file sharing, or USB

2. **Friends install with one command:**
   ```bash
   pip install terminal_chat_client-1.0.0-py3-none-any.whl
   ```

3. **Friends run the client:**
   ```bash
   terminal-chat
   ```

### Option 2: GitHub Repository (Better for Updates)

**Best for:** Easier updates, version control, larger group

1. **Push your code to GitHub:**
   ```bash
   git add .
   git commit -m "Add client package distribution"
   git push origin main
   ```

2. **Friends install directly from GitHub:**
   ```bash
   pip install git+https://github.com/YOUR_USERNAME/terminal-chat.git
   ```

3. **To update later, friends just run:**
   ```bash
   pip install --upgrade git+https://github.com/YOUR_USERNAME/terminal-chat.git
   ```

### Option 3: Publish to PyPI (Most Professional)

**Best for:** Public distribution, easiest for users

1. **Create a PyPI account:**
   - Go to https://pypi.org and create an account

2. **Install twine:**
   ```bash
   pip install twine
   ```

3. **Upload to PyPI:**
   ```bash
   twine upload dist/*
   ```

4. **Friends install with:**
   ```bash
   pip install terminal-chat-client
   ```

## Complete Installation Instructions for Friends

Here's a simple guide you can copy-paste and send to your friends:

---

### Quick Start Guide for Friends

#### Windows

1. **Install Python** (if not already installed):
   - Download from https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Open Command Prompt** and run:
   ```cmd
   pip install terminal_chat_client-1.0.0-py3-none-any.whl
   ```
   (Make sure the .whl file is in your current directory)

3. **Launch the chat:**
   ```cmd
   terminal-chat
   ```

4. **First time setup:**
   - Choose "Register" to create an account
   - Enter a username and password
   - Start chatting!

#### Linux

1. **Open terminal** and run:
   ```bash
   pip install terminal_chat_client-1.0.0-py3-none-any.whl
   ```

2. **If you get "command not found", install pip first:**
   ```bash
   # Ubuntu/Debian
   sudo apt install python3-pip

   # Fedora
   sudo dnf install python3-pip
   ```

3. **Launch the chat:**
   ```bash
   terminal-chat
   ```

4. **If "terminal-chat" command not found:**
   ```bash
   # Add to your ~/.bashrc or ~/.zshrc
   export PATH="$HOME/.local/bin:$PATH"

   # Then reload your shell
   source ~/.bashrc
   ```

---

## Updating the Package

When you make changes and want to distribute a new version:

1. **Update version number** in `pyproject.toml`:
   ```toml
   version = "1.0.1"  # Increment this
   ```

2. **Rebuild the package:**
   ```bash
   # Clean old builds
   rm -rf dist/ build/ *.egg-info/

   # Build new version
   python -m build
   ```

3. **Redistribute** the new wheel file to your friends, or push to GitHub/PyPI

## Troubleshooting Common Issues

### "pip: command not found"
- **Windows:** Python wasn't added to PATH during installation. Reinstall Python and check "Add to PATH"
- **Linux:** Install pip with your package manager (see Linux instructions above)

### "terminal-chat: command not found" after installation
- The Python scripts directory isn't in PATH
- **Quick fix:** Use `python -m client.main` instead
- **Permanent fix:** Add `~/.local/bin` (Linux/Mac) or Python Scripts folder (Windows) to PATH

### "Cannot connect to server"
- Check if the server URL in the config is correct
- Default is: https://terminal-chat.fuadmuhammed.com
- Users can override with: `terminal-chat --server https://your-server.com`

### Dependencies installation fails
- Make sure Python version is 3.8 or higher: `python --version`
- Try upgrading pip: `pip install --upgrade pip`

## Server Configuration

The client is pre-configured to connect to:
```
https://terminal-chat.fuadmuhammed.com
```

Users can change this by:
1. Editing `~/.terminal-chat/config.json`, or
2. Using environment variable: `export CHAT_SERVER_URL=https://new-server.com`
3. Using command-line flag: `terminal-chat --server https://new-server.com`

## Package Contents

The distributed package includes:
- ✅ Terminal chat client UI
- ✅ WebSocket connection handler
- ✅ End-to-end encryption support
- ✅ Auto-reconnection logic
- ✅ Configuration management
- ❌ Server code (not needed by clients)
- ❌ Development/testing files

## Security Notes for Friends

- All messages are end-to-end encrypted
- Encryption keys are stored locally at `~/.terminal-chat/encryption.key`
- Keep your encryption key safe - if you lose it, you can't decrypt old messages
- The server cannot read your messages
- Always verify you're connecting to the correct server URL

## License

MIT License - Free to use and distribute

## Support

If your friends have issues:
1. Check the README-CLIENT.md file for detailed instructions
2. Verify server is running and accessible
3. Check Python and pip versions
4. Contact you for support!

---

## Quick Distribution Checklist

- [ ] Built the package with `python -m build`
- [ ] Verified dist/terminal_chat_client-1.0.0-py3-none-any.whl exists
- [ ] Tested installation (optional but recommended)
- [ ] Chose distribution method (file sharing/GitHub/PyPI)
- [ ] Sent README-CLIENT.md to friends for installation instructions
- [ ] Verified server is running at https://terminal-chat.fuadmuhammed.com
- [ ] Ready to help friends with any installation issues!
