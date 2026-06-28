"""GUI automation via xdotool and scrot (Linux/X11 or Wayland via xwayland)."""
import subprocess
import base64
import tempfile
import os


def _run(cmd: list) -> dict:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        return {"output": r.stdout.strip(), "error": r.stderr.strip(), "ok": r.returncode == 0}
    except FileNotFoundError as e:
        return {"error": f"Tool not found: {e}. Install xdotool/scrot.", "ok": False}
    except Exception as e:
        return {"error": str(e), "ok": False}


def type_text(text: str) -> dict:
    """Type text at the current cursor position."""
    return _run(["xdotool", "type", "--clearmodifiers", text])


def key(keys: str) -> dict:
    """Press a key combo e.g. 'ctrl+c', 'super', 'Return'."""
    return _run(["xdotool", "key", keys])


def click(x: int, y: int, button: int = 1) -> dict:
    """Click at screen coordinates."""
    return _run(["xdotool", "mousemove", str(x), str(y), "click", str(button)])


def screenshot() -> dict:
    """Take a screenshot and return base64-encoded PNG."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        tmp = f.name
    try:
        r = subprocess.run(["scrot", tmp], capture_output=True, timeout=10)
        if r.returncode != 0:
            # fallback: import (ImageMagick)
            r = subprocess.run(["import", "-window", "root", tmp], capture_output=True, timeout=10)
        with open(tmp, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        return {"image_base64": b64, "format": "png"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            os.unlink(tmp)
        except Exception:
            pass


def open_app(app: str) -> dict:
    """Launch an application by name."""
    return _run(["xdg-open", app]) if app.startswith("/") or "." in app else _run([app, "&"])


def window_list() -> dict:
    """List open windows."""
    return _run(["xdotool", "search", "--onlyvisible", "--name", ""])
