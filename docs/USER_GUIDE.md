# Terminal Chat User Guide

Welcome to Terminal Chat! This guide will help you get started with using the chat application.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Installation](#installation)
3. [First Time Setup](#first-time-setup)
4. [Using the Chat](#using-the-chat)
5. [Slash Commands](#slash-commands)
6. [Keyboard Shortcuts](#keyboard-shortcuts)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)
9. [FAQ](#faq)

---

## Getting Started

Terminal Chat is a modern, secure terminal-based chat application featuring:
- **Real-time messaging** with instant delivery
- **End-to-end encryption** for privacy
- **Beautiful terminal UI** with colors and formatting
- **Message history** to see previous conversations
- **Auto-reconnection** if you lose connection

---

## Installation

### Prerequisites
- Python 3.11 or higher
- Terminal with UTF-8 support
- Internet connection

### Install from Source

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd terminal-chat
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **You're ready!**
   ```bash
   python -m client.main
   ```

---

## First Time Setup

### 1. Launch the Client

```bash
python -m client.main
```

You'll see the Terminal Chat login screen.

### 2. Create an Account

On first launch:

1. Enter a **username** (3-30 characters, letters, numbers, `_`, `-`)
2. Enter a **password** (minimum 6 characters)
3. Click the **"Register"** button or press `Tab` then `Enter`

**Username Requirements:**
- 3-30 characters long
- Only letters, numbers, underscores (_), and hyphens (-)
- Must be unique
- Examples: `john_doe`, `user123`, `chat-master`

**Password Requirements:**
- Minimum 6 characters
- No maximum length
- Case-sensitive

### 3. Encryption Key Generation

On first run, Terminal Chat automatically generates an encryption key:
- Location: `~/.terminal-chat/encryption.key`
- This key encrypts all your messages
- **Keep this file safe!** Without it, you can't decrypt messages
- Never share this file

### 4. Start Chatting!

After registration, you'll enter the chat room automatically.

---

## Using the Chat

### Chat Screen Layout

```
┌─────────────────────────────────────────────────────┐
│ Terminal Chat - john_doe    🔒 E2EE    Online: 3   │  ← Header
├─────────────────────────────────────────────────────┤
│ Connected                                           │  ← Status Bar
├─────────────────────────────────────────────────────┤
│                                                     │
│ 10:30:00 alice: Hello everyone!                    │
│ 10:30:15 bob: Hey Alice, how are you?              │  ← Message Area
│ 10:30:30 john_doe: Hi all!                         │
│                                                     │
├─────────────────────────────────────────────────────┤
│ Type a message and press Enter...                  │  ← Input Field
└─────────────────────────────────────────────────────┘
```

### Sending Messages

1. **Type your message** in the input field at the bottom
2. **Press `Enter`** to send
3. Your message appears immediately in the chat

**Message Limits:**
- Maximum 5,000 characters per message
- No minimum length
- Empty messages are ignored

### Receiving Messages

- Messages from others appear instantly
- Each message shows:
  - **Time** - When the message was sent (HH:MM:SS)
  - **Username** - Who sent it (in color)
  - **Content** - The message text
- New messages trigger a notification sound (bell)
- Messages from you appear in white

### Understanding Message Colors

Each user gets a **unique color** based on their username:
- **Your messages**: White/bold
- **Other users**: Assigned colors (cyan, magenta, yellow, blue, green, etc.)
- **System messages**: Yellow/italic
- **Timestamps**: Dimmed gray

---

## Slash Commands

Commands start with `/` and provide special functions:

### `/help`
Show available commands and keyboard shortcuts.

**Usage:**
```
/help
```

**Example Output:**
```
Available Commands:
  /help       - Show this help message
  /quit       - Exit the application
  /clear      - Clear message history

Keyboard Shortcuts:
  Ctrl+C/Q    - Quit application
```

### `/quit` or `/exit`
Exit the application immediately.

**Usage:**
```
/quit
```
or
```
/exit
```

Both commands do the same thing - cleanly exit Terminal Chat.

### `/clear`
Clear all messages from your screen.

**Usage:**
```
/clear
```

**Notes:**
- Only clears your local display
- Doesn't delete messages from server
- Message history still loads on reconnect
- Useful for privacy or decluttering

---

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Enter` | Send message |
| `Ctrl+C` | Quit application |
| `Ctrl+Q` | Quit application |
| `Tab` | Navigate between buttons (login screen) |
| `↑` / `↓` | Scroll message history |
| `Home` | Jump to top of messages |
| `End` | Jump to bottom of messages |

---

## Configuration

### Configuration File

Terminal Chat stores settings in `~/.terminal-chat/config.json`.

**Default Configuration:**
```json
{
  "server_url": "http://127.0.0.1:8000",
  "auto_reconnect": true,
  "reconnect_delay": 1,
  "max_reconnect_delay": 60,
  "notification_sound": true,
  "message_history_limit": 50
}
```

### Configuration Options

#### `server_url`
- **Type**: String
- **Default**: `http://127.0.0.1:8000`
- **Description**: URL of the chat server
- **Example**: `https://chat.example.com`

#### `auto_reconnect`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Automatically reconnect if connection is lost

#### `reconnect_delay`
- **Type**: Number (seconds)
- **Default**: `1`
- **Description**: Initial delay before reconnecting

#### `max_reconnect_delay`
- **Type**: Number (seconds)
- **Default**: `60`
- **Description**: Maximum delay between reconnection attempts

#### `notification_sound`
- **Type**: Boolean
- **Default**: `true`
- **Description**: Play sound when receiving messages

#### `message_history_limit`
- **Type**: Number
- **Default**: `50`
- **Description**: Number of messages to load on startup

### Command Line Options

#### Connect to Custom Server
```bash
python -m client.main --server https://chat.example.com:8000
```

#### View Current Configuration
```bash
python -m client.main --config
```

**Output:**
```
Current Configuration:
  Config file: /home/user/.terminal-chat/config.json
  Server URL: http://127.0.0.1:8000
  Auto-reconnect: True
  Notification sound: True
  Message history limit: 50
```

#### View Version
```bash
python -m client.main --version
```

### Environment Variables

You can override settings using environment variables:

```bash
# Set server URL
export CHAT_SERVER_URL=https://chat.example.com

# Run client
python -m client.main
```

**Precedence (highest to lowest):**
1. Command-line arguments (`--server`)
2. Environment variables (`CHAT_SERVER_URL`)
3. Configuration file (`config.json`)
4. Default values

---

## Troubleshooting

### Can't Connect to Server

**Problem:**
```
Cannot connect to server at http://127.0.0.1:8000. Is it running?
```

**Solutions:**
1. Verify the server is running
2. Check the server URL in config
3. Check firewall settings
4. Verify network connectivity

**How to check:**
```bash
# Test if server is responding
curl http://127.0.0.1:8000/api/health

# Should return:
# {"status":"healthy","version":"1.0.0"}
```

### Username Already Taken

**Problem:**
```
Error: Username already registered
```

**Solutions:**
1. Choose a different username
2. If you forgot your password, contact server admin
3. Use login instead of register if you have an account

### Connection Keeps Dropping

**Problem:** Chat disconnects frequently

**Solutions:**
1. Check internet connection stability
2. Verify server is stable
3. Check firewall isn't blocking WebSocket connections
4. Try a different network

### Messages Not Appearing

**Problem:** You send messages but don't see them

**Solutions:**
1. Check you're connected (status bar shows "Connected")
2. Verify message length isn't too long (max 5000 chars)
3. Check server logs for errors
4. Try `/clear` and resending

### Decryption Failed

**Problem:**
```
[Decryption failed]
```

**Cause:** Message encrypted with different key

**Solutions:**
1. Ensure all clients use the same encryption key
2. Check `~/.terminal-chat/encryption.key` hasn't been corrupted
3. If key is lost, old messages can't be decrypted

### Terminal Rendering Issues

**Problem:** UI looks broken or has display issues

**Solutions:**
1. Ensure terminal supports UTF-8
2. Resize terminal window
3. Update Textual library: `pip install -U textual`
4. Try a different terminal emulator

**Recommended Terminals:**
- **Linux**: GNOME Terminal, Konsole, Alacritty
- **macOS**: iTerm2, Alacritty
- **Windows**: Windows Terminal, ConEmu

---

## FAQ

### Is Terminal Chat secure?

**Yes!** Terminal Chat uses:
- **End-to-end encryption**: Messages encrypted before leaving your device
- **JWT authentication**: Secure user authentication
- **Bcrypt password hashing**: Passwords never stored in plain text

The server **cannot read** your messages - they're encrypted!

### Can I use Terminal Chat on multiple devices?

**Partially.** You can log in from multiple devices, but:
- Encryption keys are device-specific
- Each device generates its own key
- Messages encrypted on Device A can't be decrypted on Device B (by default)

**Workaround:** Copy `~/.terminal-chat/encryption.key` to all devices.

### How do I change my password?

Currently, password changing is not implemented. Contact your server admin.

### Can I delete messages?

Message deletion is not yet implemented. All messages are permanent.

### How long is message history kept?

Message history is kept indefinitely on the server. You can control how many messages load on startup with `message_history_limit` in config.

### Can I create private messages?

Private messaging is not yet implemented. All messages are in the public room.

### Does Terminal Chat work on Windows?

Yes! Terminal Chat works on:
- **Linux** ✓
- **macOS** ✓
- **Windows** ✓

For best experience on Windows, use **Windows Terminal**.

### Can I run my own server?

**Yes!** Terminal Chat is open source. See the [Deployment Guide](DEPLOYMENT.md) for instructions.

### How do I report bugs?

Report bugs on GitHub Issues or contact the development team.

### Is there a mobile app?

Not yet. Terminal Chat is currently terminal-only.

---

## Tips & Best Practices

### 1. Keep Your Encryption Key Safe
- Backup `~/.terminal-chat/encryption.key`
- Don't share it publicly
- Without it, you can't read encrypted messages

### 2. Use Strong Passwords
- Minimum 12 characters recommended
- Mix letters, numbers, symbols
- Don't reuse passwords from other services

### 3. Monitor Connection Status
- Check status bar regularly
- "Connected" = everything is working
- "Reconnecting..." = temporary network issue
- "Offline" = server unreachable

### 4. Customize Your Experience
- Disable notification sounds if they're annoying
- Adjust `message_history_limit` based on your needs
- Use `/clear` to declutter when needed

### 5. Use Slash Commands
- `/help` - When you forget commands
- `/clear` - Clean slate for new conversation
- `/quit` - Clean exit

---

## Getting Help

### Resources
- **README**: General information
- **API Documentation**: For developers
- **Deployment Guide**: For server admins
- **Encryption Documentation**: Security details

### Support
- GitHub Issues: Report bugs and request features
- Community Chat: Join the Terminal Chat community
- Email: support@example.com

---

## Changelog

### Version 1.0.0 (2025-01-18)
- ✨ Initial release
- 🔒 End-to-end encryption
- 💬 Real-time messaging
- 🎨 Colored terminal UI
- 📝 Message history
- 🔄 Auto-reconnection
- ⌨️ Slash commands
- 🔔 Notification sounds

---

**Happy Chatting!** 🎉

If you have questions or feedback, don't hesitate to reach out.
