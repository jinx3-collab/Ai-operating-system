import os
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Config:
    # LLM backend: "ollama" or "colab"
    backend: str = os.getenv("AI_OS_BACKEND", "ollama")

    # Ollama settings
    ollama_url: str = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "phi3:mini")

    # Colab settings (set COLAB_URL to your ngrok/colab tunnel URL)
    colab_url: Optional[str] = os.getenv("COLAB_URL")
    colab_api_key: Optional[str] = os.getenv("COLAB_API_KEY")

    # Web dashboard
    web_host: str = os.getenv("AI_OS_HOST", "0.0.0.0")
    web_port: int = int(os.getenv("AI_OS_PORT", "7860"))

    # Safety: commands that require user confirmation
    dangerous_patterns: list = field(default_factory=lambda: [
        "rm -rf", "mkfs", "dd if=", ":(){ :|:& };:", "shutdown", "reboot",
        "format", "fdisk", "> /dev/"
    ])

    # Max shell command timeout in seconds
    shell_timeout: int = int(os.getenv("SHELL_TIMEOUT", "30"))


cfg = Config()
