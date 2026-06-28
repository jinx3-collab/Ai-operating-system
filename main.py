#!/usr/bin/env python3
"""AI Operating System — main entry point."""
import sys
import os
import argparse

# Project root on path
sys.path.insert(0, os.path.dirname(__file__))


def run_cli():
    from interfaces.cli import run
    run()


def run_web(host="0.0.0.0", port=7860):
    try:
        import uvicorn
    except ImportError:
        print("uvicorn not installed. Run: pip install uvicorn fastapi")
        sys.exit(1)
    from interfaces.web.server import app
    print(f"\n🤖 AI-OS Web Dashboard → http://localhost:{port}\n")
    uvicorn.run(app, host=host, port=port, log_level="warning")


def run_both(host="0.0.0.0", port=7860):
    """Start web server in background thread, then run CLI."""
    import threading
    t = threading.Thread(target=run_web, args=(host, port), daemon=True)
    t.start()
    import time; time.sleep(1)
    run_cli()


def main():
    parser = argparse.ArgumentParser(
        description="AI Operating System — control your laptop with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py               # CLI mode
  python main.py --web         # Web dashboard only
  python main.py --both        # CLI + web dashboard
  python main.py --backend colab --colab-url https://xxxx.ngrok.io
  python main.py --model llama3.2:1b
        """
    )
    parser.add_argument("--web", action="store_true", help="Start web dashboard")
    parser.add_argument("--both", action="store_true", help="CLI + web dashboard")
    parser.add_argument("--host", default="0.0.0.0", help="Web server host")
    parser.add_argument("--port", type=int, default=7860, help="Web server port")
    parser.add_argument("--backend", choices=["ollama", "colab"], help="LLM backend")
    parser.add_argument("--model", help="Ollama model name (e.g. phi3:mini, llama3.2:1b)")
    parser.add_argument("--colab-url", help="Colab/ngrok tunnel URL")
    args = parser.parse_args()

    # Apply overrides
    from config import cfg
    if args.backend:
        cfg.backend = args.backend
    if args.model:
        cfg.ollama_model = args.model
    if args.colab_url:
        cfg.colab_url = args.colab_url
        cfg.backend = "colab"

    if args.web:
        run_web(args.host, args.port)
    elif args.both:
        run_both(args.host, args.port)
    else:
        run_cli()


if __name__ == "__main__":
    main()
