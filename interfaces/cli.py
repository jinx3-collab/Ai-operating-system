"""Rich terminal UI for AI-OS."""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

try:
    from rich.console import Console
    from rich.markdown import Markdown
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.live import Live
    from rich.spinner import Spinner
    from rich.table import Table
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from core.agent import Agent
from core.llm import is_backend_available, list_ollama_models
from config import cfg


console = Console() if HAS_RICH else None


def print_msg(text: str, style: str = ""):
    if HAS_RICH:
        console.print(Markdown(text))
    else:
        print(text)


def print_banner():
    banner = """
╔═══════════════════════════════════════════╗
║          AI OPERATING SYSTEM v1.0         ║
║  Backend: {backend:<10}  Model: {model:<14}║
╚═══════════════════════════════════════════╝
Commands: /clear  /models  /backend  /help  /quit
""".format(backend=cfg.backend.upper(), model=cfg.ollama_model[:14])
    if HAS_RICH:
        console.print(Panel(banner.strip(), style="bold cyan"))
    else:
        print(banner)


def check_backend():
    if not is_backend_available():
        msg = (
            f"\n⚠️  Backend '{cfg.backend}' is not reachable.\n"
        )
        if cfg.backend == "ollama":
            msg += (
                "  To start Ollama locally:\n"
                "    curl -fsSL https://ollama.com/install.sh | sh\n"
                "    ollama pull phi3:mini\n"
                "    ollama serve\n"
            )
        else:
            msg += (
                "  Set COLAB_URL to your Colab ngrok tunnel URL:\n"
                "    export COLAB_URL=https://xxxx.ngrok.io\n"
            )
        if HAS_RICH:
            console.print(msg, style="yellow")
        else:
            print(msg)
        return False
    return True


def handle_command(cmd: str, agent: Agent) -> bool:
    """Handle slash commands. Returns True to continue, False to quit."""
    cmd = cmd.strip().lower()
    if cmd in ("/quit", "/exit", "/q"):
        print_msg("Goodbye!")
        return False
    elif cmd == "/clear":
        print_msg(agent.clear_memory())
    elif cmd == "/models":
        models = list_ollama_models()
        if models:
            print_msg("Available Ollama models:\n" + "\n".join(f"  - {m}" for m in models))
        else:
            print_msg("No Ollama models found (or Ollama not running).")
    elif cmd.startswith("/backend"):
        parts = cmd.split()
        if len(parts) > 1:
            cfg.backend = parts[1]
            print_msg(f"Backend switched to: **{cfg.backend}**")
        else:
            print_msg(f"Current backend: **{cfg.backend}**. Use `/backend ollama` or `/backend colab`")
    elif cmd == "/help":
        print_msg(
            "**AI-OS Commands**\n"
            "- `/clear` — wipe conversation memory\n"
            "- `/models` — list available Ollama models\n"
            "- `/backend ollama|colab` — switch LLM backend\n"
            "- `/help` — show this help\n"
            "- `/quit` — exit\n\n"
            "**Examples**\n"
            "- `list files in my home directory`\n"
            "- `write a python script that monitors CPU usage`\n"
            "- `open the terminal`\n"
            "- `take a screenshot`\n"
        )
    else:
        print_msg(f"Unknown command: {cmd}. Try /help")
    return True


def run():
    print_banner()
    check_backend()

    status_holder = {"s": ""}

    def on_status(s):
        status_holder["s"] = s

    agent = Agent(on_status=on_status)

    print_msg("Ask me anything or give me a task. Type **/help** for commands.\n")

    while True:
        try:
            if HAS_RICH:
                user_input = Prompt.ask("[bold green]You[/bold green]").strip()
            else:
                user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print_msg("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.startswith("/"):
            if not handle_command(user_input, agent):
                break
            continue

        # Send to agent
        if HAS_RICH:
            with console.status("[cyan]Thinking...[/cyan]"):
                response = agent.send(user_input)
        else:
            print("Thinking...")
            response = agent.send(user_input)

        if HAS_RICH:
            console.print(Panel(Markdown(response), title="AI-OS", border_style="cyan"))
        else:
            print(f"\nAI-OS: {response}\n")


if __name__ == "__main__":
    run()
