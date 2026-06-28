"""Browser control: open URLs, fetch pages, extract text."""
import subprocess
import urllib.request
import urllib.parse
import html.parser
import re


def open_url(url: str) -> dict:
    """Open a URL in the default browser."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        result = subprocess.run(
            ["xdg-open", url],
            capture_output=True, text=True, timeout=10
        )
        return {"opened": url, "ok": result.returncode == 0}
    except Exception as e:
        return {"error": str(e), "ok": False}


def search(query: str, engine: str = "google") -> dict:
    """Open a web search in the browser."""
    engines = {
        "google": "https://www.google.com/search?q=",
        "duckduckgo": "https://duckduckgo.com/?q=",
        "github": "https://github.com/search?q=",
        "youtube": "https://www.youtube.com/results?search_query=",
        "wikipedia": "https://en.wikipedia.org/wiki/Special:Search?search=",
    }
    base = engines.get(engine.lower(), engines["google"])
    url = base + urllib.parse.quote_plus(query)
    return open_url(url)


class _TextExtractor(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = []
        self._skip = False

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "nav", "footer", "head"):
            self._skip = True

    def handle_endtag(self, tag):
        if tag in ("script", "style", "nav", "footer", "head"):
            self._skip = False

    def handle_data(self, data):
        if not self._skip:
            stripped = data.strip()
            if stripped:
                self.text.append(stripped)


def fetch(url: str, max_chars: int = 4000) -> dict:
    """Fetch a URL and return its text content (no browser needed)."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (compatible; AI-OS/1.0)"}
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            raw = resp.read().decode(errors="replace")

        parser = _TextExtractor()
        parser.feed(raw)
        text = " ".join(parser.text)
        text = re.sub(r"\s{2,}", " ", text).strip()
        return {"url": url, "text": text[:max_chars], "total_chars": len(text)}
    except Exception as e:
        return {"error": str(e), "url": url}
