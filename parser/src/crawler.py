import json
import time
import re
import hashlib
from collections import deque
from urllib.parse import urlparse, urljoin, urldefrag

import requests
from bs4 import BeautifulSoup

from .cleaner import clean_html

HEADERS = {"User-Agent": "WebContentParser/0.1 (+respectful crawler)"}

BINARY_EXTENSIONS = {
    ".jpg",".jpeg",".png",".gif",".svg",".webp",".pdf",".doc",".docx",".xls",".xlsx",
    ".ppt",".pptx",".zip",".rar",".7z",".mp3",".mp4",".avi",".mov",".woff",".woff2",
    ".ttf",".eot",".ico"
}

def normalize_url(base, href):
    if not href:
        return None
    href = href.strip()
    if href.startswith(("mailto:", "tel:", "javascript:")):
        return None
    abs_url = urljoin(base, href)
    abs_url, _ = urldefrag(abs_url)
    return abs_url

def same_domain(seed, candidate):
    s, c = urlparse(seed), urlparse(candidate)
    return (
        s.scheme in ("http","https") and c.scheme in ("http","https")
        and s.netloc == c.netloc
    )

def is_crawlable(url):
    path = urlparse(url).path.lower()
    return not any(path.endswith(ext) for ext in BINARY_EXTENSIONS)

def url_fingerprint(url) -> str:
    p = urlparse(url)
    norm_path = re.sub(r"/+$", "/", p.path.lower())
    norm = p._replace(path=norm_path).geturl()
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()

def crawl(start_url: str, max_pages: int = 0, rate: float = 1.0):
    """Breadth-first crawl within same domain. Returns list of cleaned page dicts."""
    seen = set()
    q = deque([start_url])
    results = []
    delay = 1.0 / max(rate, 0.1)

    while q and (max_pages == 0 or len(results) < max_pages):
        url = q.popleft()
        fp = url_fingerprint(url)
        if fp in seen or not is_crawlable(url):
            continue
        seen.add(fp)

        time.sleep(delay)
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
        except Exception:
            continue
        if r.status_code != 200 or "text/html" not in r.headers.get("Content-Type",""):
            continue

        html = r.text
        cleaned = clean_html(html)
        results.append({
            "url": url,
            "status": r.status_code,
            "retrieved_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            **cleaned
        })

        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            nxt = normalize_url(url, a["href"])
            if nxt and same_domain(start_url, nxt) and is_crawlable(nxt):
                fp2 = url_fingerprint(nxt)
                if fp2 not in seen and all(fp2 != url_fingerprint(u) for u in q):
                    q.append(nxt)

    return results

def save_json(items, out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
