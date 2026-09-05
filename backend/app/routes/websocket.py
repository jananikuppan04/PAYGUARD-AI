import asyncio
import json
import random
from datetime import datetime
from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter(tags=["WebSocket"])

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

@router.websocket("/ws/payments")
async def websocket_payments(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and send periodic simulated background events
            await asyncio.sleep(8)
            now_str = datetime.now().strftime("%H:%M:%S")
            mock_event = {
                "type": "PAYMENT_EVENT",
                "timestamp": now_str,
                "data": {
                    "event_id": f"EVT-{random.randint(100, 999)}",
                    "status": random.choice(["RECOVERED", "RECOVERABLE", "FAILED"]),
                    "amount": round(random.choice([499, 999, 1499, 2999, 4999]), 2),
                    "message": "Live Payment Event Broadcasted"
                }
            }
            await websocket.send_json(mock_event)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception:
        manager.disconnect(websocket)
