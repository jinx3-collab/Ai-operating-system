"""Safe shell command execution."""
import subprocess
import shlex
from config import cfg


def run(command: str, confirmed: bool = False) -> dict:
    """Run a shell command. Returns {output, error, returncode}."""
    # Safety check for dangerous patterns
    for pattern in cfg.dangerous_patterns:
        if pattern in command:
            if not confirmed:
                return {
                    "output": "",
                    "error": f"BLOCKED: '{pattern}' detected. Run with confirmed=True to proceed.",
                    "returncode": -1,
                    "needs_confirm": True,
                    "command": command
                }
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=cfg.shell_timeout,
            cwd=getattr(cfg, "cwd", None)
        )
        return {
            "output": result.stdout[:4000],
            "error": result.stderr[:2000],
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"output": "", "error": f"Command timed out after {cfg.shell_timeout}s", "returncode": -1}
    except Exception as e:
        return {"output": "", "error": str(e), "returncode": -1}
