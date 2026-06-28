"""Rolling conversation memory with optional file persistence."""
import json
import os
from pathlib import Path

MEMORY_FILE = Path.home() / ".ai-os-memory.json"
MAX_MESSAGES = 40  # keep last N messages in context


class Memory:
    def __init__(self, persist: bool = True):
        self.persist = persist
        self.messages: list[dict] = []
        self._system = (
            "You are an AI Operating System assistant with full access to the user's computer. "
            "You can run shell commands, manage files, automate the GUI, and write/run code. "
            "Always be safe: confirm before destructive operations. "
            "When you need to execute something, emit a JSON block like:\n"
            '{"action": "shell", "command": "ls -la"}\n'
            "Available actions: shell, file_read, file_write, file_list, gui_type, gui_click, "
            "gui_screenshot, code_run, notify. "
            "Always explain what you are doing and why."
        )
        if persist and MEMORY_FILE.exists():
            self._load()

    def add(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})
        if len(self.messages) > MAX_MESSAGES:
            self.messages = self.messages[-MAX_MESSAGES:]
        if self.persist:
            self._save()

    def get_context(self) -> list[dict]:
        return [{"role": "system", "content": self._system}] + self.messages

    def clear(self):
        self.messages = []
        if self.persist and MEMORY_FILE.exists():
            MEMORY_FILE.unlink()

    def _save(self):
        try:
            MEMORY_FILE.write_text(json.dumps(self.messages, indent=2))
        except Exception:
            pass

    def _load(self):
        try:
            self.messages = json.loads(MEMORY_FILE.read_text())
        except Exception:
            self.messages = []
