"""
FastAPI application entry point with WebSocket endpoint
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Terminal Chat Server")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "Terminal Chat Server is running"}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """WebSocket endpoint for real-time chat"""
    # TODO: Implement WebSocket connection handling
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass


@app.post("/api/register")
async def register():
    """User registration endpoint"""
    # TODO: Implement user registration
    pass


@app.post("/api/login")
async def login():
    """User login endpoint"""
    # TODO: Implement user login
    pass


@app.get("/api/history")
async def get_history(limit: int = 100):
    """Get message history"""
    # TODO: Implement message history retrieval
    pass
