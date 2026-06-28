import os
from dataclasses import dataclass, field
from typing import Optional
from pathlib import Path

# Load .env if present
_env = Path(__file__).parent / ".env"
if _env.exists():
    for line in _env.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())


@dataclass
class Config:
    # Active backend: claude | gpt | gemini | colab | ollama
    backend: str = os.getenv("AI_OS_BACKEND", "claude")

    # ── Claude (Anthropic) ────────────────────────────────
    anthropic_api_key: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
    claude_model: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

    # ── GPT (OpenAI) ──────────────────────────────────────
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    gpt_model: str = os.getenv("GPT_MODEL", "gpt-4o")

    # ── Gemini (Google) ───────────────────────────────────
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-flash-latest")

    # ── Colab (ngrok tunnel) ──────────────────────────────
    colab_url: Optional[str] = os.getenv("COLAB_URL")
    colab_api_key: Optional[str] = os.getenv("COLAB_API_KEY")

    # ── Ollama (local fallback) ───────────────────────────
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "phi3:mini")

    # ── Web dashboard ─────────────────────────────────────
    web_host: str = os.getenv("AI_OS_HOST", "0.0.0.0")
    web_port: int = int(os.getenv("AI_OS_PORT", "7860"))

    # ── Safety ────────────────────────────────────────────
    dangerous_patterns: list = field(default_factory=lambda: [
        "rm -rf /", "mkfs", "dd if=", ":(){ :|:& };:", "shutdown", "reboot",
        "format c:", "fdisk", "> /dev/sd"
    ])
    shell_timeout: int = int(os.getenv("SHELL_TIMEOUT", "30"))


cfg = Config()
