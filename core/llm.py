"""Multi-backend LLM: Claude, GPT-4, Gemini, Colab, or Ollama."""
import json
import urllib.request
import urllib.parse
from config import cfg


def _post(url: str, payload: dict, headers: dict) -> dict:
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def chat(messages: list[dict]) -> str:
    backend = cfg.backend.lower()
    try:
        if backend == "claude":
            return _claude(messages)
        elif backend in ("gpt", "openai", "gpt4"):
            return _gpt(messages)
        elif backend == "gemini":
            return _gemini(messages)
        elif backend == "colab":
            return _colab(messages)
        else:
            return _ollama(messages)
    except Exception as e:
        return f"[{backend} error: {e}]"


# ── Claude (Anthropic) ────────────────────────────────────────────────────────

def _claude(messages: list[dict]) -> str:
    key = cfg.anthropic_api_key
    if not key:
        return "[Claude error: ANTHROPIC_API_KEY not set]"

    system = next((m["content"] for m in messages if m["role"] == "system"), "")
    msgs = [m for m in messages if m["role"] != "system"]

    payload = {
        "model": cfg.claude_model,
        "max_tokens": 4096,
        "messages": msgs,
    }
    if system:
        payload["system"] = system

    result = _post(
        "https://api.anthropic.com/v1/messages",
        payload,
        {
            "x-api-key": key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
    )
    return result["content"][0]["text"]


# ── GPT-4 (OpenAI) ────────────────────────────────────────────────────────────

def _gpt(messages: list[dict]) -> str:
    key = cfg.openai_api_key
    if not key:
        return "[GPT error: OPENAI_API_KEY not set]"

    payload = {
        "model": cfg.gpt_model,
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.3,
    }
    result = _post(
        "https://api.openai.com/v1/chat/completions",
        payload,
        {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    )
    return result["choices"][0]["message"]["content"]


# ── Gemini (Google) ───────────────────────────────────────────────────────────

def _gemini(messages: list[dict]) -> str:
    key = cfg.gemini_api_key
    if not key:
        return "[Gemini error: GEMINI_API_KEY not set]"

    contents = []
    for m in messages:
        if m["role"] == "system":
            contents.append({"role": "user", "parts": [{"text": m["content"]}]})
            contents.append({"role": "model", "parts": [{"text": "Understood."}]})
        elif m["role"] == "assistant":
            contents.append({"role": "model", "parts": [{"text": m["content"]}]})
        else:
            contents.append({"role": "user", "parts": [{"text": m["content"]}]})

    payload = {
        "contents": contents,
        "generationConfig": {"temperature": 0.3, "maxOutputTokens": 4096}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{cfg.gemini_model}:generateContent?key={key}"
    result = _post(url, payload, {"Content-Type": "application/json"})
    return result["candidates"][0]["content"]["parts"][0]["text"]


# ── Colab (ngrok tunnel) ──────────────────────────────────────────────────────

def _colab(messages: list[dict]) -> str:
    if not cfg.colab_url:
        return "[Colab error: COLAB_URL not set]"
    headers = {"Content-Type": "application/json"}
    if cfg.colab_api_key:
        headers["Authorization"] = f"Bearer {cfg.colab_api_key}"
    result = _post(cfg.colab_url.rstrip("/") + "/chat", {"messages": messages}, headers)
    return result.get("response", result.get("content", str(result)))


# ── Ollama (local fallback) ───────────────────────────────────────────────────

def _ollama(messages: list[dict]) -> str:
    payload = {
        "model": cfg.ollama_model,
        "messages": messages,
        "stream": False,
        "options": {"temperature": 0.3, "num_ctx": 4096}
    }
    result = _post(
        f"{cfg.ollama_url}/api/chat",
        payload,
        {"Content-Type": "application/json"}
    )
    return result["message"]["content"]


# ── Utilities ─────────────────────────────────────────────────────────────────

def is_backend_available() -> bool:
    try:
        backend = cfg.backend.lower()
        if backend == "claude":
            return bool(cfg.anthropic_api_key)
        elif backend in ("gpt", "openai", "gpt4"):
            return bool(cfg.openai_api_key)
        elif backend == "gemini":
            return bool(cfg.gemini_api_key)
        elif backend == "colab":
            return bool(cfg.colab_url)
        else:
            urllib.request.urlopen(f"{cfg.ollama_url}/api/tags", timeout=3)
            return True
    except Exception:
        return False


def list_available_backends() -> list[str]:
    available = []
    if cfg.anthropic_api_key:
        available.append(f"claude ({cfg.claude_model})")
    if cfg.openai_api_key:
        available.append(f"gpt ({cfg.gpt_model})")
    if cfg.gemini_api_key:
        available.append(f"gemini ({cfg.gemini_model})")
    if cfg.colab_url:
        available.append("colab")
    available.append(f"ollama ({cfg.ollama_model})")
    return available


def list_ollama_models() -> list[str]:
    try:
        req = urllib.request.Request(f"{cfg.ollama_url}/api/tags")
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read())
        return [m["name"] for m in data.get("models", [])]
    except Exception:
        return []
