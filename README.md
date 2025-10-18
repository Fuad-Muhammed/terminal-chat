# Terminal Chat

A modern terminal-based chat application built with Python, featuring real-time messaging, end-to-end encryption, and a beautiful terminal UI.

## Features

- **Real-time Messaging**: WebSocket-based communication for instant message delivery
- **End-to-End Encryption**: Messages are encrypted using Fernet symmetric encryption
- **Terminal UI**: Beautiful, responsive interface built with Textual
- **Message History**: Persistent storage of encrypted messages with SQLite/PostgreSQL
- **User Authentication**: Secure JWT-based authentication
- **Auto-Reconnection**: Smart reconnection with exponential backoff
- **Cross-Platform**: Works on Linux, macOS, and Windows

## Technology Stack

- **Backend**: FastAPI + uvicorn (async WebSocket support)
- **Client UI**: Textual (modern terminal UI framework)
- **Database**: SQLite (development) → PostgreSQL (production)
- **Encryption**: Fernet symmetric encryption
- **Authentication**: JWT tokens with bcrypt password hashing
- **Protocol**: WebSockets for real-time bidirectional communication

## Project Structure

```
terminal-chat/
├── server/                 # FastAPI WebSocket server
│   ├── __init__.py
│   ├── main.py            # Server entry point
│   ├── connection_manager.py
│   ├── database.py
│   └── models.py
├── client/                # Terminal UI client
│   ├── __init__.py
│   ├── main.py           # Client entry point
│   ├── ui.py             # Textual UI components
│   └── connection.py     # WebSocket client
├── shared/               # Shared utilities
│   ├── __init__.py
│   └── crypto.py         # Encryption utilities
├── requirements.txt
├── .env.example
└── README.md
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd terminal-chat
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv

   # On Linux/macOS
   source venv/bin/activate

   # On Windows
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and update configuration as needed
   ```

## Usage

### Running the Server

```bash
# From project root
uvicorn server.main:app --reload --host 0.0.0.0 --port 8000
```

The server will start on `http://localhost:8000`. You can access the API documentation at `http://localhost:8000/docs`.

### Running the Client

```bash
# From project root
python -m client.main
```

## API Endpoints

- `GET /` - Health check
- `POST /api/register` - Create a new user account
- `POST /api/login` - Authenticate and receive JWT token
- `WS /ws/{user_id}` - WebSocket connection for real-time chat
- `GET /api/history?limit=100` - Retrieve message history

## Development

### Database Initialization

The database will be automatically initialized on first run. To manually initialize:

```python
from server.database import init_db
init_db()
```

### Running Tests

```bash
pytest
pytest -v  # Verbose output
```

## Security Features

1. **Authentication**: JWT tokens with configurable expiration
2. **Password Security**: Bcrypt hashing for all passwords
3. **End-to-End Encryption**: Messages encrypted before transmission
4. **Input Validation**: All user inputs are validated and sanitized
5. **Rate Limiting**: Protection against spam and DoS attacks (to be implemented)

## Deployment

### Docker Deployment

```dockerfile
# Build the Docker image
docker build -t terminal-chat-server .

# Run the container
docker run -p 8000:8000 --env-file .env terminal-chat-server
```

### Cloud Platforms

Recommended platforms for deployment:
- Railway
- Render
- DigitalOcean

Ensure WebSocket support is enabled and upgrade to PostgreSQL for production.

## Roadmap

- [x] Phase 1: Project foundation and structure
- [ ] Phase 2: Server core implementation
- [ ] Phase 3: Client foundation
- [ ] Phase 4: Message persistence
- [ ] Phase 5: End-to-end encryption
- [ ] Phase 6: Polish & UX improvements
- [ ] Phase 7: Cloud deployment

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details
