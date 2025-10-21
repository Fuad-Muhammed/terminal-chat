"""
WebSocket connection manager for handling active connections
"""

from typing import List, Dict
from fastapi import WebSocket


class ConnectionManager:
    """Manages active WebSocket connections"""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_personal_message(self, message: str, user_id: str):
        """Send a message to a specific user"""
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(message)

    async def broadcast(self, message: str, exclude_user: str = None):
        """Broadcast a message to all connected clients"""
        for user_id, connection in self.active_connections.items():
            if exclude_user and user_id == exclude_user:
                continue
            await connection.send_text(message)

    def get_active_users(self) -> List[str]:
        """Get list of currently connected user IDs"""
        return list(self.active_connections.keys())

    def get_active_user_info(self, db_session) -> List[Dict[str, str]]:
        """Get list of currently connected users with their usernames"""
        from .models import User
        user_info = []
        for user_id in self.active_connections.keys():
            user = db_session.query(User).filter(User.id == int(user_id)).first()
            if user:
                user_info.append({
                    "user_id": user_id,
                    "username": user.username
                })
        return user_info
