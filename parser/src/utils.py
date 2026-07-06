import re
import hashlib
from urllib.parse import urlparse, urljoin, urldefrag

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
    return s.scheme in ("http","https") and c.scheme in ("http","https") and s.netloc == c.netloc

def is_crawlable(url):
    path = urlparse(url).path.lower()
    return not any(path.endswith(ext) for ext in BINARY_EXTENSIONS)

def url_fingerprint(url) -> str:
    p = urlparse(url)
    norm_path = re.sub(r"/+$", "/", p.path.lower())
    norm = p._replace(path=norm_path).geturl()
    return hashlib.sha1(norm.encode("utf-8")).hexdigest()
