from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import List, Dict
import json
from datetime import datetime

from jose import jwt, JWTError
from app.config import settings
from app.database import SessionLocal
from app import models

router = APIRouter(tags=["WebSocket"])


# ─── TOKEN CHECK ──────────────────────────────
async def get_ws_user(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        user_id = payload.get("user_id")
        if not user_id:
            return None

    except JWTError:
        return None

    db = SessionLocal()
    try:
        user = db.query(models.User).filter(
            models.User.id == user_id
        ).first()
        return user
    finally:
        db.close()


# ─── CONNECTION MANAGER ───────────────────────
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, room: str):
        await websocket.accept()

        if room not in self.active_connections:
            self.active_connections[room] = []

        self.active_connections[room].append(websocket)

        print(f"Connected: {room} | Count: {len(self.active_connections[room])}")

    def disconnect(self, websocket: WebSocket, room: str):
        if room in self.active_connections:
            self.active_connections[room].remove(websocket)

            if not self.active_connections[room]:
                del self.active_connections[room]

        print(f"Disconnected: {room}")

    async def broadcast(self, message: str, room: str):
        if room in self.active_connections:
            for connection in self.active_connections[room]:
                await connection.send_text(message)

    def get_room_count(self, room: str) -> int:
        return len(self.active_connections.get(room, []))


manager = ConnectionManager()


# ─── SECURE CHAT ENDPOINT ─────────────────────
@router.websocket("/ws/chat/{room}")
async def chat_endpoint(
    websocket: WebSocket,
    room: str,
    token: str = Query(None)
):
    # 🔐 TOKEN VALIDATION (before accept)
    user = await get_ws_user(token)

    if not token or not user:
        await websocket.close(code=1008)
        return

    username = user.username

    # ✅ ACCEPT CONNECTION
    await manager.connect(websocket, room)

    # JOIN MESSAGE
    await manager.broadcast(
        json.dumps({
            "type": "system",
            "message": f"{username} joined",
            "room": room,
            "users_count": manager.get_room_count(room),
            "timestamp": datetime.now().strftime("%H:%M")
        }),
        room
    )

    try:
        while True:
            data = await websocket.receive_text()

            await manager.broadcast(
                json.dumps({
                    "type": "message",
                    "username": username,
                    "message": data,
                    "room": room,
                    "timestamp": datetime.now().strftime("%H:%M")
                }),
                room
            )

    except WebSocketDisconnect:
        manager.disconnect(websocket, room)

        await manager.broadcast(
            json.dumps({
                "type": "system",
                "message": f"{username} left",
                "room": room,
                "users_count": manager.get_room_count(room),
                "timestamp": datetime.now().strftime("%H:%M")
            }),
            room
        )


# ─── ROOMS ───────────────────────────────────
@router.get("/ws/rooms")
def get_active_rooms():
    return {
        "rooms": {
            room: len(connections)
            for room, connections in manager.active_connections.items()
        }
    }