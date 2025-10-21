# Terminal Chat App - Implementation Plan

## Overview
Building a client-server terminal-based chat application in Python with end-to-end encryption, message history, and cloud deployment capabilities.

## Technology Stack
- **Backend**: FastAPI + uvicorn (async WebSocket support)
- **Client UI**: Textual (modern terminal UI framework)
- **Database**: SQLite (development) → PostgreSQL (production)
- **Encryption**: Fernet symmetric encryption
- **Cloud Platform**: Railway, Render, or DigitalOcean
- **Protocol**: WebSockets for real-time bidirectional communication

## Phase 1: Project Foundation (2-3 hours)

### Directory Structure
```
terminal-chat/
├── server/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── connection_manager.py
│   ├── database.py
│   └── models.py
├── client/
│   ├── __init__.py
│   ├── main.py              # Client entry point
│   ├── ui.py                # Textual UI components
│   └── connection.py        # WebSocket client
├── shared/
│   ├── __init__.py
│   └── crypto.py            # Encryption utilities
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

### Core Dependencies
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
websockets==12.0
textual==0.44.1
sqlalchemy==2.0.23
cryptography==41.0.7
python-jose[cryptography]==3.3.0
python-dotenv==1.0.0
asyncio
```

### Tasks
- [x] Create directory structure
- [x] Initialize virtual environment (`python -m venv venv`)
- [x] Create requirements.txt with dependencies
- [x] Initialize git repository
- [x] Create .gitignore (venv/, __pycache__/, .env, *.db)

## Phase 2: Server Core (4-5 hours) ✅ COMPLETED

### WebSocket Server
- [x] Set up FastAPI application with WebSocket endpoint
- [x] Create ConnectionManager class to handle active connections
- [x] Implement connection lifecycle (connect, disconnect, send)
- [x] Add basic message broadcasting to all connected clients
- [x] Implement heartbeat/ping-pong for connection health

### Database Schema
```sql
Users:
  - id (primary key)
  - username (unique)
  - password_hash
  - public_key
  - created_at

Messages:
  - id (primary key)
  - user_id (foreign key)
  - content (encrypted)
  - timestamp
  - room_id (for future multi-room support)
```

### Authentication
- [x] Create user registration endpoint
- [x] Implement login with JWT token generation
- [x] Add token validation middleware
- [x] Password hashing with bcrypt

### API Endpoints
```
POST /api/register
POST /api/login
WS   /ws/{user_id}
GET  /api/history?limit=100
```

## Phase 3: Client Foundation (4-5 hours) ✅ COMPLETED

### Terminal UI Components
- [x] Create login/registration screen
- [x] Build main chat interface layout:
  - Header (app title, online users)
  - Message display area (scrollable)
  - Input field at bottom
  - Status bar
- [x] Implement keyboard navigation
- [x] Add color scheme for better readability

### WebSocket Client
- [x] Create async WebSocket connection handler
- [x] Implement auto-reconnection with exponential backoff
- [x] Handle connection status updates
- [x] Queue messages when offline, send when reconnected

### Message Flow
- [x] Send messages from input to server
- [x] Receive and display messages in real-time
- [x] Show typing indicators (implemented with debouncing)
- [x] Display timestamps in human-readable format

## Phase 4: Message Persistence (2-3 hours) ✅ COMPLETED

### Server-Side Storage
- [x] Save all messages to database on receive
- [x] Create message history API endpoint
- [x] Implement pagination (load 100 messages at a time)
- [ ] Add filtering by date range (optional - skipped)

### Client-Side History
- [x] Load recent messages on connection
- [ ] Implement scroll-back to load older messages (pending)
- [x] Cache loaded messages in memory
- [ ] Show "loading" indicator when fetching history (pending)

## Phase 5: End-to-End Encryption (3-4 hours) ✅ COMPLETED

### Key Management
- [x] Generate client-side encryption keys on first run
- [x] Store keys securely in local config file (~/.terminal-chat/encryption.key)
- [ ] Implement key exchange protocol on connection (optional - skipped, using shared key)
- [ ] Add key rotation mechanism (optional - skipped)

### Encryption Flow
```
Client A -> Encrypt(message, shared_key) -> Server -> Store encrypted ->
-> Broadcast encrypted -> Client B -> Decrypt(message, shared_key)
```

### Implementation
- [x] Use Fernet symmetric encryption (from cryptography library)
- [x] Encrypt messages before sending
- [x] Server stores encrypted blobs (can't read them)
- [x] Clients decrypt received messages
- [x] Add encryption status indicator in UI (🔒 E2EE badge in header)

## Phase 6: Polish & UX (2-3 hours) ✅ COMPLETED

### User Experience
- [x] Display connection status in UI
- [x] Add notification sounds (system bell on new messages)
- [x] Implement /commands (/help, /quit, /clear)
- [ ] Add user presence system (online/offline status) - skipped, active user count is shown
- [x] Show "User is typing..." indicators - implemented with debouncing and auto-timeout
- [x] Display list of online member names in UI

### Error Handling
- [x] Graceful handling of network failures
- [x] User-friendly error messages
- [x] Retry logic for failed operations (auto-reconnect with exponential backoff)
- [x] Validation for usernames and messages

### Configuration
- [x] Create config file for server address/port (~/.terminal-chat/config.json)
- [x] Support environment variables (CHAT_SERVER_URL)
- [x] Add command-line arguments for client (--server, --config, --version)
- [x] Create .env.example template

### UI Polish
- [x] Color-code messages by user (consistent hash-based colors)
- [x] Add timestamps to messages
- [x] Show username with each message
- [x] Implement smooth scrolling (auto-scroll to bottom)
- [x] Add loading states (history loading, connection status)

## Phase 7: Cloud Deployment (2-3 hours) ✅ COMPLETED

### Containerization
- [x] Create Dockerfile for server (with health checks and multi-stage build)
- [x] Create .dockerignore file to optimize build context
- [x] Create docker-compose.yml with SQLite and PostgreSQL configurations
- [x] Test Docker build locally (image builds successfully)

### Deployment Steps
- [x] Create Dockerfile for server
- [x] Set up environment variables (.env.example updated)
- [x] Document cloud platform deployment (Railway/Render/DigitalOcean)
- [x] Configure database support (both SQLite and PostgreSQL)
- [x] Document SSL/TLS configuration with Nginx
- [x] Provide deployment instructions for multiple platforms
- [x] Document client configuration for production servers
- [x] Add health check endpoints (/api/health)

### Documentation
- [x] Write comprehensive README with setup instructions
- [x] Document API endpoints (docs/API.md)
- [x] Create user guide for clients (docs/USER_GUIDE.md)
- [x] Add deployment guide (docs/DEPLOYMENT.md)
- [x] Document encryption implementation (docs/ENCRYPTION.md)

### Created Files
- `Dockerfile` - Production-ready container image
- `.dockerignore` - Build optimization
- `docker-compose.yml` - Local and production configurations
- `docs/API.md` - Complete API documentation
- `docs/DEPLOYMENT.md` - Deployment guide for Railway, Render, DigitalOcean
- `docs/USER_GUIDE.md` - End-user documentation
- `docs/ENCRYPTION.md` - Security and encryption architecture
- Updated `README.md` - Comprehensive project documentation

## Testing Checklist

### Functional Tests
- [ ] User registration and login
- [ ] Send and receive messages
- [ ] Multiple clients simultaneously
- [ ] Message history persistence
- [ ] Encryption/decryption
- [ ] Reconnection after disconnect
- [ ] Graceful server shutdown

### Edge Cases
- [ ] Very long messages
- [ ] Special characters and emoji
- [ ] Rapid message sending
- [ ] Network interruption
- [ ] Server restart while clients connected
- [ ] Duplicate usernames

## Security Considerations

1. **Authentication**: JWT tokens with expiration
2. **Passwords**: Hashed with bcrypt, never stored plain text
3. **Encryption**: End-to-end, server can't read messages
4. **Rate Limiting**: Prevent spam and DoS attacks
5. **Input Validation**: Sanitize all user inputs
6. **HTTPS**: Use SSL/TLS for production deployment

## Future Enhancements (Optional)

- [ ] Multiple chat rooms/channels
- [ ] Private direct messages
- [ ] File sharing
- [ ] Message editing and deletion
- [ ] User profiles and avatars
- [ ] Message search functionality
- [ ] Mobile client (using same server)
- [ ] Voice messages
- [ ] Rich text formatting (markdown)

## Estimated Timeline

| Phase | Duration | Cumulative |
|-------|----------|------------|
| Phase 1: Foundation | 2-3 hours | 2-3 hours |
| Phase 2: Server Core | 4-5 hours | 6-8 hours |
| Phase 3: Client Foundation | 4-5 hours | 10-13 hours |
| Phase 4: Message Persistence | 2-3 hours | 12-16 hours |
| Phase 5: Encryption | 3-4 hours | 15-20 hours |
| Phase 6: Polish & UX | 2-3 hours | 17-23 hours |
| Phase 7: Deployment | 2-3 hours | 19-26 hours |

**Total Estimated Time**: 19-26 hours

## Getting Started

Once you're ready to begin implementation, we'll start with Phase 1 and work through each phase sequentially, testing as we go. Each phase builds on the previous one, ensuring a solid foundation before adding complexity.
