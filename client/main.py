"""
Terminal Chat Client - Entry point
"""

import asyncio
from .ui import ChatApp


def main():
    """Run the chat application"""
    app = ChatApp()
    app.run()


if __name__ == "__main__":
    main()
