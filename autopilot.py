#!/usr/bin/env python3
"""
Autopilot mode — Claude runs autonomously in your shell.
It reads your project, plans what needs to be done, and executes.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.agent import Agent
from core.llm import chat, is_backend_available
from config import cfg

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║            AI-OS AUTOPILOT — Claude in your shell           ║
║  Backend: {backend:<10}  Model: {model:<28}║
║  Type a task, say 'auto' to let AI decide, or 'quit'        ║
╚══════════════════════════════════════════════════════════════╝
""".format(backend=cfg.backend.upper(), model=cfg.claude_model if cfg.backend=="claude" else cfg.gemini_model)

AUTO_PROMPT = """
You are an autonomous AI agent with full shell access to this Linux machine.
Your job is to look at the user's projects and finish them.

Current projects on this machine:
- /home/jinx3/Ai-operating-system (AI OS project - Python)

GitHub repos: jinx3-collab/Ai-operating-system

Your tasks:
1. Scan the codebase and identify what's incomplete or broken
2. Fix issues, add missing features, write tests
3. Run the code to verify it works
4. Commit and push changes to GitHub

Start by scanning the project structure, then take action.
Use shell commands to explore, edit files, run tests.
Be autonomous — don't ask for confirmation on non-destructive operations.
"""


def run():
    print(BANNER)

    if not is_backend_available():
        print(f"⚠️  Backend '{cfg.backend}' not available. Check your API key in .env")
        sys.exit(1)

    print(f"✅ {cfg.backend} connected\n")

    agent = Agent(on_status=lambda s: print(f"  [{s}]", end="\r", flush=True))

    print("Commands: 'auto' = let AI scan & fix projects | 'quit' = exit\n")

    while True:
        try:
            user_input = input("You → ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nStopping autopilot.")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if user_input.lower() == "auto":
            user_input = AUTO_PROMPT

        print()
        response = agent.send(user_input)
        print(f"\nAI → {response}\n")
        print("-" * 60)


if __name__ == "__main__":
    run()
