"""
Run this in Google Colab to serve an LLM that AI-OS can connect to.

In Colab, paste this into a cell and run:

  !pip install flask pyngrok transformers accelerate bitsandbytes

Then set your ngrok token and run the cell. Copy the public URL into AI-OS:
  export COLAB_URL=https://xxxx.ngrok.io
  python main.py --backend colab
"""

# ── Colab cell ────────────────────────────────────────────────────────────────
COLAB_CODE = '''
import os
from flask import Flask, request, jsonify
from threading import Thread

# ---- Choose your model ----
MODEL_ID = "microsoft/phi-2"          # ~1.5GB — fast, smart
# MODEL_ID = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"   # ultra-small
# MODEL_ID = "google/gemma-2b-it"    # 2B, needs HF token

app = Flask(__name__)

print("Loading model...")
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
import torch

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_ID,
    torch_dtype=torch.float16,
    device_map="auto"
)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer,
                max_new_tokens=512, temperature=0.3, do_sample=True)
print("Model ready!")


@app.get("/health")
def health():
    return {"status": "ok", "model": MODEL_ID}


@app.post("/chat")
def chat():
    data = request.json
    messages = data.get("messages", [])
    # Format as prompt
    prompt = ""
    for m in messages:
        role = m["role"]
        content = m["content"]
        if role == "system":
            prompt += f"System: {content}\\n"
        elif role == "user":
            prompt += f"User: {content}\\n"
        elif role == "assistant":
            prompt += f"Assistant: {content}\\n"
    prompt += "Assistant:"

    result = pipe(prompt)[0]["generated_text"]
    # Extract only the new part
    response = result[len(prompt):].strip()
    return {"response": response}


def run_server():
    app.run(port=5000, use_reloader=False)

thread = Thread(target=run_server, daemon=True)
thread.start()

# Start ngrok tunnel
from pyngrok import ngrok
NGROK_TOKEN = ""  # <-- paste your free ngrok token from ngrok.com/signup
if NGROK_TOKEN:
    ngrok.set_auth_token(NGROK_TOKEN)
public_url = ngrok.connect(5000).public_url
print(f"\\n=== AI-OS Colab Server Running ===")
print(f"Public URL: {public_url}")
print(f"\\nIn your terminal, run:")
print(f"  export COLAB_URL={public_url}")
print(f"  python main.py --backend colab")
'''

if __name__ == "__main__":
    print("This file contains the Colab server code.")
    print("Copy the code in COLAB_CODE into a Google Colab cell.")
    print()
    print(COLAB_CODE)
