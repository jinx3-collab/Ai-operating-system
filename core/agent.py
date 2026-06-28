"""Core agent loop: parse LLM output, dispatch tool calls, return results."""
import json
import re
from typing import Callable

from core.llm import chat
from core.memory import Memory
import tools.shell as shell
import tools.files as files
import tools.code_runner as code_runner
import tools.gui as gui


# JSON action block pattern
ACTION_RE = re.compile(r'\{[^{}]*"action"\s*:\s*"[^"]+"[^{}]*\}', re.DOTALL)


def _extract_actions(text: str) -> list[dict]:
    actions = []
    for match in ACTION_RE.finditer(text):
        try:
            actions.append(json.loads(match.group()))
        except json.JSONDecodeError:
            pass
    return actions


def _dispatch(action: dict, confirmed: bool = False) -> str:
    name = action.get("action", "")

    if name == "shell":
        r = shell.run(action.get("command", ""), confirmed=confirmed)
        if r.get("needs_confirm"):
            return f"CONFIRM_NEEDED: {r['error']}"
        out = r["output"] or r["error"]
        return out or f"(exit {r['returncode']})"

    elif name == "file_read":
        r = files.read(action.get("path", ""))
        return r.get("content") or r.get("error", "")

    elif name == "file_write":
        r = files.write(action.get("path", ""), action.get("content", ""), action.get("append", False))
        return str(r)

    elif name == "file_list":
        r = files.list_dir(action.get("path", "."))
        if "error" in r:
            return r["error"]
        lines = [f"{'[DIR]' if i['type']=='dir' else '     '} {i['name']}" for i in r["items"]]
        return "\n".join(lines) or "(empty)"

    elif name == "gui_type":
        r = gui.type_text(action.get("text", ""))
        return "typed" if r["ok"] else r["error"]

    elif name == "gui_click":
        r = gui.click(action.get("x", 0), action.get("y", 0))
        return "clicked" if r["ok"] else r["error"]

    elif name == "gui_screenshot":
        r = gui.screenshot()
        if "error" in r:
            return r["error"]
        return f"[screenshot captured, {len(r['image_base64'])} bytes base64]"

    elif name == "code_run":
        r = code_runner.run_code(
            action.get("code", ""),
            action.get("language", "python")
        )
        out = r.get("stdout") or r.get("error", "")
        err = r.get("stderr", "")
        return (out + ("\n[stderr]: " + err if err else "")).strip()

    elif name == "notify":
        msg = action.get("message", "")
        shell.run(f'notify-send "AI-OS" "{msg}"')
        return f"notified: {msg}"

    else:
        return f"Unknown action: {name}"


class Agent:
    def __init__(self, on_status: Callable[[str], None] = None):
        self.memory = Memory()
        self.on_status = on_status or (lambda s: None)
        self._pending_confirm: dict | None = None

    def send(self, user_input: str, confirmed: bool = False) -> str:
        """Process user input and return assistant response."""
        if self._pending_confirm and confirmed:
            result = _dispatch(self._pending_confirm, confirmed=True)
            self._pending_confirm = None
            resp = f"Executed (confirmed):\n{result}"
            self.memory.add("assistant", resp)
            return resp

        self.memory.add("user", user_input)
        self.on_status("Thinking...")

        context = self.memory.get_context()
        llm_response = chat(context)
        self.on_status("Executing...")

        # Extract and run any action blocks
        actions = _extract_actions(llm_response)
        tool_outputs = []

        for action in actions:
            result = _dispatch(action, confirmed=False)
            if result.startswith("CONFIRM_NEEDED:"):
                self._pending_confirm = action
                llm_response += f"\n\n⚠️  Confirmation required before running: `{action.get('command', action)}`\nType **yes** to confirm or **no** to cancel."
                tool_outputs.append(result)
            else:
                tool_outputs.append(f"[{action['action']}] → {result}")

        if tool_outputs:
            tool_summary = "\n".join(tool_outputs)
            # Feed results back for a follow-up response
            self.memory.add("assistant", llm_response)
            self.memory.add("user", f"[Tool results]\n{tool_summary}")
            self.on_status("Summarizing results...")
            final = chat(self.memory.get_context())
            self.memory.add("assistant", final)
            return final

        self.memory.add("assistant", llm_response)
        return llm_response

    def clear_memory(self):
        self.memory.clear()
        return "Memory cleared."

    def confirm(self) -> str:
        return self.send("yes", confirmed=True)

    def cancel(self) -> str:
        self._pending_confirm = None
        return "Cancelled."
