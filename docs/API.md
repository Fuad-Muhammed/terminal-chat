# Terminal Chat API Documentation

This document provides comprehensive documentation for the Terminal Chat REST API and WebSocket protocol.

## Base URL

- **Development**: `http://localhost:8000`
- **Production**: `https://your-domain.com`

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in WebSocket connections.

### Token Format
```
Bearer <token>
```

### Token Expiration
- Default: 24 hours
- Configurable via `JWT_EXPIRATION_HOURS` environment variable

---

## REST API Endpoints

### Health Check

#### `GET /`

Basic health check endpoint.

**Response:**
```json
{
  "status": "ok",
  "message": "Terminal Chat Server is running",
  "version": "1.0.0"
}
```

#### `GET /api/health`

API health check endpoint for monitoring and load balancers.

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

---

### User Registration

#### `POST /api/register`

Create a new user account.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Validation Rules:**
- Username:
  - Minimum length: 3 characters
  - Maximum length: 30 characters
  - Allowed characters: letters, numbers, underscore (_), hyphen (-)
  - Must be unique
- Password:
  - Minimum length: 6 characters

**Success Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "john_doe"
}
```

**Error Responses:**

**400 Bad Request** - Validation error:
```json
{
  "detail": "Username must be at least 3 characters long"
}
```

```json
{
  "detail": "Username already registered"
}
```

---

### User Login

#### `POST /api/login`

Authenticate a user and receive a JWT token.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Success Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "username": "john_doe"
}
```

**Error Response (401 Unauthorized):**
```json
{
  "detail": "Incorrect username or password"
}
```

---

### Message History

#### `GET /api/history`

Retrieve message history with pagination.

**Query Parameters:**
- `limit` (optional): Number of messages to retrieve (default: 100, max: 500)
- `room_id` (optional): Room identifier (default: "general")

**Example:**
```
GET /api/history?limit=50&room_id=general
```

**Success Response (200 OK):**
```json
[
  {
    "id": 1,
    "user_id": 1,
    "username": "john_doe",
    "content": "gAAAAABh...",
    "timestamp": "2025-01-15T10:30:00.000000",
    "room_id": "general"
  },
  {
    "id": 2,
    "user_id": 2,
    "username": "jane_smith",
    "content": "gAAAAABi...",
    "timestamp": "2025-01-15T10:31:00.000000",
    "room_id": "general"
  }
]
```

**Notes:**
- Messages are returned in chronological order (oldest first)
- Content is encrypted (see Encryption section)
- Requires no authentication (public history)

---

## WebSocket Protocol

### Connection

#### `WS /ws/{user_id}`

Establish a WebSocket connection for real-time chat.

**Parameters:**
- `user_id` (path): The user's ID obtained from login/register

**Query Parameters:**
- `token` (optional): JWT token for authentication

**Connection Example:**
```javascript
ws://localhost:8000/ws/1?token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Connection Lifecycle:**

1. **Connect**: Client opens WebSocket connection
2. **Authentication**: Server validates user_id and token
3. **Welcome**: Server sends user_joined broadcast to others
4. **Active**: Bidirectional message exchange
5. **Heartbeat**: Server sends periodic ping messages (every 30s)
6. **Disconnect**: Connection closed, user_left broadcast sent

---

### Message Types

All WebSocket messages are JSON objects with a `type` field.

#### Client → Server Messages

##### Chat Message
```json
{
  "type": "message",
  "content": "gAAAAABh... (encrypted)",
  "room_id": "general"
}
```

**Validation:**
- `content` must not be empty
- `content` maximum length: 5000 characters (encrypted)
- `room_id` defaults to "general"

##### Heartbeat Response
```json
{
  "type": "pong",
  "timestamp": "2025-01-15T10:30:00.000000"
}
```

---

#### Server → Client Messages

##### Chat Message
```json
{
  "type": "message",
  "id": 123,
  "user_id": 1,
  "username": "john_doe",
  "content": "gAAAAABh... (encrypted)",
  "timestamp": "2025-01-15T10:30:00.000000",
  "room_id": "general"
}
```

##### User Joined
```json
{
  "type": "user_joined",
  "username": "jane_smith",
  "user_id": 2,
  "timestamp": "2025-01-15T10:30:00.000000"
}
```

##### User Left
```json
{
  "type": "user_left",
  "username": "jane_smith",
  "user_id": 2,
  "timestamp": "2025-01-15T10:35:00.000000"
}
```

##### Active Users Update
```json
{
  "type": "active_users",
  "users": ["1", "2", "3"],
  "count": 3
}
```

##### Heartbeat Ping
```json
{
  "type": "ping",
  "timestamp": "2025-01-15T10:30:00.000000"
}
```

##### Error Message
```json
{
  "type": "error",
  "message": "Message too long (max 5000 characters)"
}
```

---

## Encryption

### Algorithm
- **Method**: Fernet (symmetric encryption)
- **Library**: `cryptography` Python package
- **Key Storage**: Client-side at `~/.terminal-chat/encryption.key`

### Message Flow

1. **Sending**:
   ```
   Client → Encrypt(message, key) → Server → Store encrypted → Broadcast encrypted
   ```

2. **Receiving**:
   ```
   Server → Broadcast encrypted → Client → Decrypt(message, key) → Display
   ```

3. **Server Role**:
   - Server CANNOT decrypt messages
   - Server only stores and relays encrypted blobs
   - True end-to-end encryption

### Example

**Original Message:**
```
Hello, world!
```

**Encrypted (Fernet):**
```
gAAAAABh3xK7Z9QXvK_xN0yG8KqLqM9xN2PvZGH8W3mL1kJ...
```

---

## Error Handling

### HTTP Status Codes

- **200 OK**: Request successful
- **201 Created**: Resource created successfully
- **400 Bad Request**: Validation error or malformed request
- **401 Unauthorized**: Authentication failed
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

### WebSocket Close Codes

- **1000**: Normal closure
- **1008**: Policy violation (e.g., invalid user_id)
- **1011**: Internal server error

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Rate Limiting

**Status**: Not yet implemented

**Planned Limits**:
- Registration: 5 requests per IP per hour
- Login: 10 requests per IP per 5 minutes
- Messages: 60 messages per user per minute

---

## Examples

### Complete Authentication Flow

```python
import requests
import json

# 1. Register new user
response = requests.post(
    "http://localhost:8000/api/register",
    json={"username": "john_doe", "password": "secret123"}
)
data = response.json()
token = data["access_token"]
user_id = data["user_id"]

# 2. Connect to WebSocket
import websockets
import asyncio

async def chat():
    uri = f"ws://localhost:8000/ws/{user_id}?token={token}"
    async with websockets.connect(uri) as websocket:
        # Send a message
        await websocket.send(json.dumps({
            "type": "message",
            "content": "encrypted_content_here",
            "room_id": "general"
        }))

        # Receive messages
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")

asyncio.run(chat())
```

### Fetch Message History

```python
import requests

response = requests.get(
    "http://localhost:8000/api/history",
    params={"limit": 50, "room_id": "general"}
)

messages = response.json()
for msg in messages:
    print(f"{msg['username']}: {msg['content']}")
```

---

## Interactive Documentation

Visit the auto-generated interactive API documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

These interfaces allow you to:
- View all endpoints
- Test API calls directly in the browser
- View request/response schemas
- Download OpenAPI specification

---

## Versioning

**Current Version**: 1.0.0

API versioning is not yet implemented. Breaking changes will be announced in release notes.

---

## Support

For issues or questions:
- GitHub Issues: [Repository Issues](https://github.com/yourusername/terminal-chat/issues)
- Documentation: See README.md and other docs
