"""
FastAPI application entry point with WebSocket endpoint
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio
from datetime import datetime

from .database import get_db, init_db
from .models import User, Message
from .schemas import UserRegister, UserLogin, Token, MessageResponse
from .auth import hash_password, verify_password, create_access_token, verify_token
from .connection_manager import ConnectionManager

# Initialize FastAPI app
app = FastAPI(title="Terminal Chat Server", version="1.0.0")

# Initialize connection manager
manager = ConnectionManager()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("Database initialized successfully")


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "message": "Terminal Chat Server is running",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health():
    """API health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "version": "1.0.0"
    }


@app.post("/api/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    User registration endpoint

    Creates a new user account with hashed password
    """
    # Validate username
    if len(user_data.username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long"
        )

    if len(user_data.username) > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be less than 30 characters"
        )

    # Check for valid characters (alphanumeric, underscore, hyphen)
    if not user_data.username.replace('_', '').replace('-', '').isalnum():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username can only contain letters, numbers, underscores, and hyphens"
        )

    # Validate password
    if len(user_data.password) < 6:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must be at least 6 characters long"
        )

    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Create new user
    hashed_pw = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        password_hash=hashed_pw
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(new_user.id), "username": new_user.username})

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=new_user.id,
        username=new_user.username
    )


@app.post("/api/login", response_model=Token)
async def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    User login endpoint

    Authenticates user and returns JWT token
    """
    # Find user by username
    user = db.query(User).filter(User.username == user_data.username).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate JWT token
    access_token = create_access_token(data={"sub": str(user.id), "username": user.username})

    return Token(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        username=user.username
    )


async def get_current_user(token: str, db: Session) -> User:
    """
    Dependency to validate JWT token and get current user
    """
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )

    return user


@app.get("/api/history", response_model=List[MessageResponse])
async def get_history(
    limit: int = 100,
    room_id: str = "general",
    db: Session = Depends(get_db)
):
    """
    Get message history

    Retrieves recent messages with pagination support
    """
    messages = db.query(Message).filter(
        Message.room_id == room_id
    ).order_by(
        Message.timestamp.desc()
    ).limit(limit).all()

    # Reverse to get chronological order
    messages.reverse()

    # Format response with username
    response = []
    for msg in messages:
        response.append(MessageResponse(
            id=msg.id,
            user_id=msg.user_id,
            username=msg.user.username,
            content=msg.content,
            timestamp=msg.timestamp,
            room_id=msg.room_id
        ))

    return response


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    user_id: int,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time chat

    Handles connection lifecycle, message broadcasting, and heartbeat
    """
    # Validate user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Accept connection and add to manager
    await manager.connect(str(user_id), websocket)

    # Broadcast user joined message
    join_message = json.dumps({
        "type": "user_joined",
        "username": user.username,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat()
    })
    await manager.broadcast(join_message, exclude_user=str(user_id))

    # Broadcast updated active users count to ALL users
    active_users = manager.get_active_users()
    active_users_message = json.dumps({
        "type": "active_users",
        "users": active_users,
        "count": len(active_users)
    })
    await manager.broadcast(active_users_message)

    try:
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(heartbeat_loop(websocket, user_id))

        # Message receive loop
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)

            # Handle different message types
            if message_data.get("type") == "message":
                # Validate message content
                content = message_data.get("content", "").strip()

                if not content:
                    # Ignore empty messages
                    continue

                if len(content) > 5000:
                    # Message too long, send error to user
                    error_msg = json.dumps({
                        "type": "error",
                        "message": "Message too long (max 5000 characters)"
                    })
                    await manager.send_personal_message(error_msg, str(user_id))
                    continue

                # Save message to database
                new_message = Message(
                    user_id=user_id,
                    content=content,
                    room_id=message_data.get("room_id", "general")
                )
                db.add(new_message)
                db.commit()
                db.refresh(new_message)

                # Broadcast to all connected clients
                broadcast_data = json.dumps({
                    "type": "message",
                    "id": new_message.id,
                    "user_id": user_id,
                    "username": user.username,
                    "content": new_message.content,
                    "timestamp": new_message.timestamp.isoformat(),
                    "room_id": new_message.room_id
                })
                await manager.broadcast(broadcast_data)

            elif message_data.get("type") == "pong":
                # Heartbeat response - connection is alive
                pass

    except WebSocketDisconnect:
        # Remove connection and broadcast user left
        manager.disconnect(str(user_id))
        leave_message = json.dumps({
            "type": "user_left",
            "username": user.username,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        await manager.broadcast(leave_message)

        # Broadcast updated active users count to remaining users
        active_users = manager.get_active_users()
        active_users_message = json.dumps({
            "type": "active_users",
            "users": active_users,
            "count": len(active_users)
        })
        await manager.broadcast(active_users_message)

        # Cancel heartbeat task
        heartbeat_task.cancel()


async def heartbeat_loop(websocket: WebSocket, user_id: int):
    """
    Send periodic heartbeat pings to keep connection alive

    Sends ping every 30 seconds
    """
    try:
        while True:
            await asyncio.sleep(30)
            ping_message = json.dumps({
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat()
            })
            await websocket.send_text(ping_message)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print(f"Heartbeat error for user {user_id}: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
