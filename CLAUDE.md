# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Terminal Chat App - A client-server terminal-based chat application in Python with end-to-end encryption, message history, and WebSocket-based real-time communication.

## Technology Stack

- **Backend**: FastAPI + uvicorn (async WebSocket support)
- **Client UI**: Textual (modern terminal UI framework)
- **Database**: SQLite (development) → PostgreSQL (production)
- **Encryption**: Fernet symmetric encryption
- **Protocol**: WebSockets for real-time bidirectional communication

## Project Structure

```
terminal-chat/
├── server/               # FastAPI WebSocket server
│   ├── main.py          # FastAPI app entry point
│   ├── connection_manager.py
│   ├── database.py
│   └── models.py
├── client/              # Terminal UI client
│   ├── main.py         # Client entry point
│   ├── ui.py           # Textual UI components
│   └── connection.py   # WebSocket client
└── shared/             # Shared utilities
    └── crypto.py       # Encryption utilities
```

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate     # On Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the server (from project root)
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000

# Run the client (from project root)
python -m client.main
```

### Database
```bash
# Database migrations (when using Alembic)
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Architecture Notes

### WebSocket Communication Flow
- Clients connect via WebSocket to `/ws/{user_id}`
- ConnectionManager maintains active connections and handles broadcasting
- All messages are encrypted client-side before transmission
- Server stores encrypted message blobs and cannot decrypt them

### Authentication Flow
1. User registers via `POST /api/register` (username + password)
2. User logs in via `POST /api/login` → receives JWT token
3. JWT token is validated on WebSocket connection
4. Token must be included in WebSocket handshake

### Encryption Architecture
- End-to-end encryption using Fernet (symmetric)
- Client-side key generation on first run
- Keys stored locally in `~/.terminal-chat/keys`
- Message flow: `Client A → Encrypt → Server (stores encrypted) → Broadcast → Client B → Decrypt`
- Server cannot read message contents

### Database Schema

**Users Table:**
- id (primary key)
- username (unique)
- password_hash (bcrypt)
- public_key
- created_at

**Messages Table:**
- id (primary key)
- user_id (foreign key to Users)
- content (encrypted blob)
- timestamp
- room_id (for future multi-room support)

## API Endpoints

```
POST /api/register    - Create new user account
POST /api/login       - Authenticate and get JWT token
WS   /ws/{user_id}    - WebSocket connection for real-time chat
GET  /api/history     - Retrieve message history (query param: limit)
```

## Important Implementation Details

### Client Auto-Reconnection
Clients must implement exponential backoff when reconnecting:
- Initial retry: 1 second
- Max retry delay: 60 seconds
- Queue messages while offline, send when reconnected

### Message Persistence
- Server saves all encrypted messages to database on receive
- History endpoint supports pagination (default: 100 messages)
- Client loads recent messages on connection and implements scroll-back loading

### Security Considerations
- All passwords must be hashed with bcrypt before storage
- JWT tokens should have reasonable expiration (e.g., 24 hours)
- Implement rate limiting to prevent spam and DoS attacks
- Input validation on all user-provided data (username, messages)
- Use SSL/TLS (HTTPS/WSS) in production

## Dependencies

Core dependencies (see requirements.txt for complete list):
- fastapi - Web framework
- uvicorn - ASGI server
- websockets - WebSocket support
- textual - Terminal UI framework
- sqlalchemy - Database ORM
- cryptography - Encryption library
- python-jose - JWT token handling
- python-dotenv - Environment variable management

## Testing Strategy

### Manual Testing Checklist
- User registration and login
- Multiple simultaneous clients
- Message encryption/decryption
- Connection loss and auto-reconnection
- Server restart while clients are connected
- Message history retrieval
- Special characters and emoji in messages

### Running Tests
```bash
# When tests are implemented
pytest
pytest -v                    # Verbose output
pytest tests/test_server.py  # Specific test file
```

## Deployment

### Environment Variables
Required environment variables (set in .env):
- `DATABASE_URL` - Database connection string
- `JWT_SECRET_KEY` - Secret key for JWT signing
- `ENCRYPTION_KEY` - Server-side encryption key (if needed)

### Docker Deployment
```bash
# Build and run server container
docker build -t terminal-chat-server .
docker run -p 8000:8000 --env-file .env terminal-chat-server
```

### Cloud Deployment Platforms
Recommended platforms: Railway, Render, or DigitalOcean
- Ensure WebSocket support is enabled
- Upgrade to PostgreSQL for production
- Configure SSL/TLS certificates
- Set environment variables in platform settings
- always update task progress in @IMPLEMENTATION_PLAN.md after a task has been completed