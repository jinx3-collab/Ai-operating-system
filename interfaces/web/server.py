"""FastAPI web server for AI-OS dashboard."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json
import asyncio
from pathlib import Path

from core.agent import Agent
from core.llm import is_backend_available, list_ollama_models
from config import cfg

app = FastAPI(title="AI Operating System")

STATIC_DIR = Path(__file__).parent / "static"

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# One agent per session (single-user for now)
_agents: dict[str, Agent] = {}


def get_agent(session_id: str = "default") -> Agent:
    if session_id not in _agents:
        _agents[session_id] = Agent()
    return _agents[session_id]


@app.get("/")
async def root():
    index = STATIC_DIR / "index.html"
    if index.exists():
        return FileResponse(str(index))
    return HTMLResponse("<h1>AI-OS</h1><p>Static files not found.</p>")


@app.get("/api/status")
async def status():
    return {
        "backend": cfg.backend,
        "model": cfg.ollama_model,
        "available": is_backend_available(),
        "colab_url": cfg.colab_url,
    }


@app.get("/api/models")
async def models():
    return {"models": list_ollama_models()}


@app.post("/api/chat")
async def chat_endpoint(body: dict):
    session = body.get("session", "default")
    message = body.get("message", "")
    confirmed = body.get("confirmed", False)
    agent = get_agent(session)
    response = agent.send(message, confirmed=confirmed)
    return {"response": response}


@app.post("/api/clear")
async def clear(body: dict = {}):
    session = body.get("session", "default")
    agent = get_agent(session)
    return {"message": agent.clear_memory()}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    status_msgs = []

    def on_status(s):
        status_msgs.append(s)

    agent = Agent(on_status=on_status)
    _agents[session_id] = agent

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            action = msg.get("action", "chat")

            if action == "chat":
                text = msg.get("message", "")
                confirmed = msg.get("confirmed", False)

                await websocket.send_text(json.dumps({"type": "status", "text": "Thinking..."}))

                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(None, lambda: agent.send(text, confirmed))

                await websocket.send_text(json.dumps({"type": "response", "text": response}))

            elif action == "clear":
                await websocket.send_text(json.dumps({"type": "response", "text": agent.clear_memory()}))

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({"type": "error", "text": str(e)}))
        except Exception:
            pass
