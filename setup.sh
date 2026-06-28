#!/bin/bash
set -e

echo "=== AI Operating System Setup ==="

# Python venv
python3 -m venv .venv
source .venv/bin/activate

# Install Python deps
pip install --upgrade pip -q
pip install -r requirements.txt -q

echo ""
echo "=== Installing Ollama (local LLM) ==="
if ! command -v ollama &>/dev/null; then
  curl -fsSL https://ollama.com/install.sh | sh
else
  echo "Ollama already installed."
fi

echo ""
echo "=== Pulling default model: phi3:mini ==="
echo "(This is a ~2GB download — smallest capable model)"
ollama pull phi3:mini || echo "Skipped — pull manually: ollama pull phi3:mini"

echo ""
echo "=== Optional GUI tools ==="
echo "For screenshot/GUI automation, install:"
echo "  sudo apt-get install -y xdotool scrot"
echo ""
echo "=== Done! ==="
echo ""
echo "To run AI-OS:"
echo "  source .venv/bin/activate"
echo "  python main.py           # CLI"
echo "  python main.py --web     # Web dashboard (http://localhost:7860)"
echo "  python main.py --both    # Both"
echo ""
echo "To use Colab instead of Ollama:"
echo "  export COLAB_URL=https://your-ngrok-url.ngrok.io"
echo "  python main.py --backend colab"
