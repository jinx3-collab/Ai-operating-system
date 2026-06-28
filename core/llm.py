"""LLM backend: Ollama (local) or Colab (remote via ngrok)."""
import json
import urllib.request
import urllib.parse
from typing import Generator
from config import cfg


def _post(url: str, payload: dict, headers: dict = None) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers or {"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def chat(messages: list[dict], stream: bool = False) -> str:
    """Send messages to the configured LLM backend and return response text."""
    if cfg.backend == "colab":
        return _colab_chat(messages)
    return _ollama_chat(messages)


def _ollama_chat(messages: list[dict]) -> str:
    url = f"{cfg.ollama_url}/api/chat"
    payload = {
        "model": cfg.ollama_model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.3, "num_ctx": 4096}
    }
    try:
        result = _post(url, payload)
        return result["message"]["content"]
    except Exception as e:
        return f"[Ollama error: {e}]"


def _colab_chat(messages: list[dict]) -> str:
    if not cfg.colab_url:
        return "[Colab error: COLAB_URL not set. Export your ngrok tunnel URL.]"
    url = cfg.colab_url.rstrip("/") + "/chat"
    headers = {"Content-Type": "application/json"}
    if cfg.colab_api_key:
        headers["Authorization"] = f"Bearer {cfg.colab_api_key}"
    try:
        result = _post(url, {"messages": messages}, headers=headers)
        return result.get("response", result.get("content", str(result)))
    except Exception as e:
        return f"[Colab error: {e}]"


def list_ollama_models() -> list[str]:
    try:
        url = f"{cfg.ollama_url}/api/tags"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []


def is_backend_available() -> bool:
    try:
        if cfg.backend == "ollama":
            urllib.request.urlopen(f"{cfg.ollama_url}/api/tags", timeout=3)
        else:
            if not cfg.colab_url:
                return False
            urllib.request.urlopen(cfg.colab_url.rstrip("/") + "/health", timeout=5)
        return True
    except Exception:
        return False
