"""
Terminal Chat Client - Entry point
"""

import asyncio
import aiohttp
import os
from typing import Dict, Any
from .ui import ChatApp, ChatScreen
from .connection import ChatConnection
from shared.crypto import get_or_create_encryption


class ChatClient:
    """Main chat client controller integrated with Textual"""

    def __init__(self):
        self.server_url = os.getenv("CHAT_SERVER_URL", "http://127.0.0.1:8000").rstrip('/')
        self.ws_url = self.server_url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.app = ChatApp()
        self.connection: ChatConnection = None
        self.user_id: int = None
        self.username: str = None
        self.token: str = None

        # Initialize encryption
        self.encryption = get_or_create_encryption()

        # Set up callbacks
        self.app.set_login_callback(self.handle_login_sync)
        self.app.set_send_message_callback(self.handle_send_message_sync)

    def handle_login_sync(self, username: str, password: str, action: str):
        """Synchronous wrapper for login callback"""
        self.app.run_worker(self.handle_login(username, password, action), exclusive=True)

    def handle_send_message_sync(self, message: str):
        """Synchronous wrapper for send message callback"""
        self.app.run_worker(self.send_message(message))

    async def handle_login(self, username: str, password: str, action: str):
        """Handle login or registration"""
        try:
            async with aiohttp.ClientSession() as session:
                endpoint = f"{self.server_url}/api/{action}"
                data = {"username": username, "password": password}

                async with session.post(endpoint, json=data) as response:
                    if response.status in [200, 201]:
                        result = await response.json()
                        self.token = result.get("access_token")
                        self.user_id = result.get("user_id")
                        self.username = result.get("username")

                        # Switch to chat screen
                        self.app.show_chat(self.username, self.user_id, self.token)

                        # Connect to WebSocket
                        await self.connect_websocket()

                        # Load message history
                        await self.load_history()

                    else:
                        error_data = await response.json()
                        error_msg = error_data.get("detail", "Unknown error")
                        self.app.show_login_error(error_msg)

        except aiohttp.ClientError as e:
            self.app.show_login_error(f"Connection error: {str(e)}")
        except Exception as e:
            self.app.show_login_error(f"Error: {str(e)}")

    async def connect_websocket(self):
        """Connect to WebSocket server"""
        try:
            self.connection = ChatConnection(self.ws_url, self.user_id, self.token)

            # Set up message and status callbacks
            self.connection.on_message(self.handle_incoming_message)
            self.connection.on_status_change(self.handle_status_change)

            # Connect
            await self.connection.connect()

            # Show encryption info
            chat_screen = self.app.get_chat_screen()
            if chat_screen:
                from pathlib import Path
                key_path = Path.home() / ".terminal-chat" / "encryption.key"
                chat_screen.add_system_message(f"🔒 End-to-end encryption enabled")
                chat_screen.add_system_message(f"Key: {key_path}")

        except Exception as e:
            chat_screen = self.app.get_chat_screen()
            if chat_screen:
                chat_screen.update_status(f"Connection error: {str(e)}")

    async def load_history(self):
        """Load message history from server"""
        try:
            async with aiohttp.ClientSession() as session:
                endpoint = f"{self.server_url}/api/history?limit=50"

                async with session.get(endpoint) as response:
                    if response.status == 200:
                        messages = await response.json()

                        chat_screen = self.app.get_chat_screen()
                        if chat_screen:
                            for msg in messages:
                                # Decrypt message content
                                encrypted_content = msg.get("content")
                                try:
                                    content = self.encryption.decrypt(encrypted_content)
                                except Exception as e:
                                    content = f"[Decryption failed]"

                                chat_screen.add_message(
                                    msg.get("username"),
                                    content,
                                    msg.get("timestamp")
                                )

        except Exception as e:
            chat_screen = self.app.get_chat_screen()
            if chat_screen:
                chat_screen.add_system_message(f"Failed to load history: {str(e)}")

    def handle_incoming_message(self, message_data: Dict[str, Any]):
        """Handle incoming WebSocket messages"""
        message_type = message_data.get("type")
        chat_screen = self.app.get_chat_screen()

        if not chat_screen:
            return

        if message_type == "message":
            # Regular chat message - decrypt content
            username = message_data.get("username", "Unknown")
            encrypted_content = message_data.get("content", "")
            timestamp = message_data.get("timestamp")

            # Decrypt the message
            try:
                content = self.encryption.decrypt(encrypted_content)
            except Exception as e:
                content = f"[Decryption failed: {str(e)}]"

            chat_screen.add_message(username, content, timestamp)

        elif message_type == "user_joined":
            # User joined notification
            username = message_data.get("username", "Someone")
            chat_screen.add_system_message(f"{username} joined the chat")

        elif message_type == "user_left":
            # User left notification
            username = message_data.get("username", "Someone")
            chat_screen.add_system_message(f"{username} left the chat")

        elif message_type == "active_users":
            # Active users count update
            count = message_data.get("count", 0)
            chat_screen.update_online_users(count)

    def handle_status_change(self, status: str):
        """Handle connection status changes"""
        chat_screen = self.app.get_chat_screen()
        if not chat_screen:
            return

        status_message = status
        if status == "connected":
            status_message = "Connected"
        elif status == "disconnected":
            status_message = "Disconnected"
        elif status == "connection_lost":
            status_message = "Connection lost..."
        elif status.startswith("reconnecting"):
            status_message = "Reconnecting..."
        elif status == "reconnected":
            status_message = "Reconnected!"
        elif status == "offline_queued":
            status_message = "Offline - message queued"

        chat_screen.update_status(status_message)

    async def send_message(self, message: str):
        """Handle sending a message"""
        if self.connection and self.connection.connected:
            try:
                # Encrypt message before sending
                encrypted_message = self.encryption.encrypt(message)
                await self.connection.send_message(encrypted_message)
            except Exception as e:
                chat_screen = self.app.get_chat_screen()
                if chat_screen:
                    chat_screen.add_system_message(f"Failed to send: {str(e)}")
        else:
            chat_screen = self.app.get_chat_screen()
            if chat_screen:
                chat_screen.add_system_message("Not connected - message queued")
                # Still try to queue the message (encrypt it first)
                if self.connection:
                    encrypted_message = self.encryption.encrypt(message)
                    await self.connection.send_message(encrypted_message)

    async def shutdown(self):
        """Clean shutdown"""
        if self.connection:
            await self.connection.disconnect()

    def run(self):
        """Run the chat client"""
        try:
            self.app.run()
        finally:
            # Cleanup
            if self.connection:
                asyncio.run(self.shutdown())


def main():
    """Entry point"""
    client = ChatClient()
    client.run()


if __name__ == "__main__":
    main()
