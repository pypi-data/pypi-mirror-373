"""Sync router for WebSocket real-time synchronization."""

import json
import uuid
from typing import Dict, Set

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..models.thought import Thought

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections for real-time sync."""
    
    def __init__(self):
        # Store active connections by team_id
        self.team_connections: Dict[str, Set[WebSocket]] = {}
        # Store connection metadata
        self.connection_info: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, team_id: str, user_id: str = None):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        # Add to team connections
        if team_id not in self.team_connections:
            self.team_connections[team_id] = set()
        self.team_connections[team_id].add(websocket)
        
        # Store connection metadata
        self.connection_info[websocket] = {
            "team_id": team_id,
            "user_id": user_id,
        }
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.connection_info:
            team_id = self.connection_info[websocket]["team_id"]
            
            # Remove from team connections
            if team_id in self.team_connections:
                self.team_connections[team_id].discard(websocket)
                if not self.team_connections[team_id]:
                    del self.team_connections[team_id]
            
            # Remove connection info
            del self.connection_info[websocket]
    
    async def broadcast_to_team(self, team_id: str, message: dict, exclude_websocket: WebSocket = None):
        """Broadcast a message to all connections in a team."""
        if team_id not in self.team_connections:
            return
        
        message_text = json.dumps(message)
        
        # Send to all team connections except the excluded one
        connections_to_remove = []
        for websocket in self.team_connections[team_id]:
            if websocket == exclude_websocket:
                continue
            
            try:
                await websocket.send_text(message_text)
            except Exception:
                # Connection is dead, mark for removal
                connections_to_remove.append(websocket)
        
        # Clean up dead connections
        for websocket in connections_to_remove:
            self.disconnect(websocket)
    
    async def send_to_websocket(self, websocket: WebSocket, message: dict):
        """Send a message to a specific WebSocket."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception:
            self.disconnect(websocket)


# Global connection manager
connection_manager = ConnectionManager()


@router.websocket("/sync/{team_id}")
async def websocket_sync(
    websocket: WebSocket,
    team_id: str,
    user_id: str = None,
):
    """WebSocket endpoint for real-time synchronization."""
    
    await connection_manager.connect(websocket, team_id, user_id)
    
    try:
        # Send initial connection confirmation
        await connection_manager.send_to_websocket(websocket, {
            "type": "connection_established",
            "team_id": team_id,
            "timestamp": "2025-01-01T00:00:00Z"  # TODO: Use proper timestamp
        })
        
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_sync_message(websocket, team_id, message)
            except json.JSONDecodeError:
                await connection_manager.send_to_websocket(websocket, {
                    "type": "error",
                    "error": "Invalid JSON format"
                })
            except Exception as e:
                await connection_manager.send_to_websocket(websocket, {
                    "type": "error",
                    "error": str(e)
                })
    
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)


async def handle_sync_message(websocket: WebSocket, team_id: str, message: dict):
    """Handle incoming sync messages."""
    
    message_type = message.get("type")
    
    if message_type == "thought_created":
        await broadcast_thought_change(team_id, "thought_created", message.get("thought"), websocket)
    
    elif message_type == "thought_updated":
        await broadcast_thought_change(team_id, "thought_updated", message.get("thought"), websocket)
    
    elif message_type == "thought_deleted":
        await broadcast_thought_change(team_id, "thought_deleted", {"id": message.get("thought_id")}, websocket)
    
    elif message_type == "ping":
        await connection_manager.send_to_websocket(websocket, {
            "type": "pong",
            "timestamp": message.get("timestamp")
        })
    
    elif message_type == "subscribe_to_path":
        # TODO: Implement path-based subscriptions
        await connection_manager.send_to_websocket(websocket, {
            "type": "subscribed",
            "path": message.get("path")
        })
    
    else:
        await connection_manager.send_to_websocket(websocket, {
            "type": "error",
            "error": f"Unknown message type: {message_type}"
        })


async def broadcast_thought_change(
    team_id: str,
    change_type: str,
    thought_data: dict,
    exclude_websocket: WebSocket = None
):
    """Broadcast thought changes to team members."""
    
    message = {
        "type": change_type,
        "thought": thought_data,
        "timestamp": "2025-01-01T00:00:00Z"  # TODO: Use proper timestamp
    }
    
    await connection_manager.broadcast_to_team(team_id, message, exclude_websocket)


# Utility functions for triggering sync events from other parts of the app

async def notify_thought_created(team_id: str, thought_data: dict):
    """Notify team members about a new thought."""
    await connection_manager.broadcast_to_team(
        str(team_id),
        {
            "type": "thought_created",
            "thought": thought_data,
            "timestamp": "2025-01-01T00:00:00Z"
        }
    )


async def notify_thought_updated(team_id: str, thought_data: dict):
    """Notify team members about an updated thought."""
    await connection_manager.broadcast_to_team(
        str(team_id),
        {
            "type": "thought_updated",
            "thought": thought_data,
            "timestamp": "2025-01-01T00:00:00Z"
        }
    )


async def notify_thought_deleted(team_id: str, thought_id: str):
    """Notify team members about a deleted thought."""
    await connection_manager.broadcast_to_team(
        str(team_id),
        {
            "type": "thought_deleted",
            "thought": {"id": thought_id},
            "timestamp": "2025-01-01T00:00:00Z"
        }
    )