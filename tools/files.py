"""File management tools."""
import os
import shutil
from pathlib import Path


def read(path: str) -> dict:
    try:
        p = Path(path).expanduser()
        content = p.read_text(errors="replace")
        return {"content": content[:8000], "size": p.stat().st_size, "path": str(p)}
    except Exception as e:
        return {"error": str(e)}


def write(path: str, content: str, append: bool = False) -> dict:
    try:
        p = Path(path).expanduser()
        p.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if append else "w"
        p.write_text(content) if not append else p.open("a").write(content)
        return {"written": str(p), "bytes": len(content)}
    except Exception as e:
        return {"error": str(e)}


def list_dir(path: str = ".", pattern: str = "*") -> dict:
    try:
        p = Path(path).expanduser()
        items = []
        for entry in sorted(p.iterdir()):
            items.append({
                "name": entry.name,
                "type": "dir" if entry.is_dir() else "file",
                "size": entry.stat().st_size if entry.is_file() else None
            })
        return {"path": str(p), "items": items[:200]}
    except Exception as e:
        return {"error": str(e)}


def delete(path: str) -> dict:
    try:
        p = Path(path).expanduser()
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        return {"deleted": str(p)}
    except Exception as e:
        return {"error": str(e)}


def move(src: str, dst: str) -> dict:
    try:
        s, d = Path(src).expanduser(), Path(dst).expanduser()
        shutil.move(str(s), str(d))
        return {"moved": str(s), "to": str(d)}
    except Exception as e:
        return {"error": str(e)}


def search(root: str, query: str) -> dict:
    try:
        results = []
        for dirpath, _, filenames in os.walk(Path(root).expanduser()):
            for fn in filenames:
                if query.lower() in fn.lower():
                    results.append(os.path.join(dirpath, fn))
                if len(results) >= 50:
                    break
        return {"results": results, "count": len(results)}
    except Exception as e:
        return {"error": str(e)}
