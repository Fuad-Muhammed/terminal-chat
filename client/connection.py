"""
WebSocket client connection handler
"""

import asyncio
import websockets
from typing import Callable, Optional
import json


class ChatConnection:
    """Manages WebSocket connection to the chat server"""

    def __init__(self, server_url: str, user_id: str):
        self.server_url = server_url
        self.user_id = user_id
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        self.message_callback: Optional[Callable] = None
        self.reconnect_delay = 1  # Initial reconnect delay in seconds
        self.max_reconnect_delay = 60

    async def connect(self):
        """Connect to the WebSocket server"""
        url = f"{self.server_url}/ws/{self.user_id}"
        self.websocket = await websockets.connect(url)
        self.running = True
        self.reconnect_delay = 1  # Reset delay on successful connection

    async def disconnect(self):
        """Disconnect from the server"""
        self.running = False
        if self.websocket:
            await self.websocket.close()

    async def send_message(self, message: str):
        """Send a message to the server"""
        if self.websocket:
            await self.websocket.send(json.dumps({
                "type": "message",
                "content": message,
                "user_id": self.user_id
            }))

    async def receive_messages(self):
        """Receive messages from the server"""
        while self.running:
            try:
                if self.websocket:
                    message = await self.websocket.recv()
                    if self.message_callback:
                        self.message_callback(message)
            except websockets.exceptions.ConnectionClosed:
                await self.handle_reconnect()
            except Exception as e:
                print(f"Error receiving message: {e}")

    async def handle_reconnect(self):
        """Handle reconnection with exponential backoff"""
        if not self.running:
            return

        print(f"Connection lost. Reconnecting in {self.reconnect_delay} seconds...")
        await asyncio.sleep(self.reconnect_delay)

        try:
            await self.connect()
            print("Reconnected successfully!")
        except Exception as e:
            print(f"Reconnection failed: {e}")
            # Exponential backoff
            self.reconnect_delay = min(self.reconnect_delay * 2, self.max_reconnect_delay)
            await self.handle_reconnect()

    def on_message(self, callback: Callable):
        """Register a callback for incoming messages"""
        self.message_callback = callback
