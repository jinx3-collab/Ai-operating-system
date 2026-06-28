"""Write and execute code in multiple languages."""
import subprocess
import tempfile
import os
from pathlib import Path

RUNNERS = {
    "python": ("python3", ".py"),
    "python3": ("python3", ".py"),
    "bash": ("bash", ".sh"),
    "sh": ("bash", ".sh"),
    "javascript": ("node", ".js"),
    "js": ("node", ".js"),
    "ruby": ("ruby", ".rb"),
}


def run_code(code: str, language: str = "python", timeout: int = 30) -> dict:
    lang = language.lower().strip()
    runner, ext = RUNNERS.get(lang, ("python3", ".py"))

    with tempfile.NamedTemporaryFile(suffix=ext, mode="w", delete=False) as f:
        f.write(code)
        tmp_path = f.name

    try:
        result = subprocess.run(
            [runner, tmp_path],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return {
            "stdout": result.stdout[:4000],
            "stderr": result.stderr[:2000],
            "returncode": result.returncode,
            "language": lang
        }
    except subprocess.TimeoutExpired:
        return {"error": f"Timed out after {timeout}s", "returncode": -1}
    except FileNotFoundError:
        return {"error": f"Runtime '{runner}' not found. Install it first.", "returncode": -1}
    except Exception as e:
        return {"error": str(e), "returncode": -1}
    finally:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
