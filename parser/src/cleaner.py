from bs4 import BeautifulSoup
import re

DROP_TAGS = {"script","style","noscript","iframe","svg"}
MENU_HINT = re.compile(r"(menu|nav|breadcrumb|sidebar|footer|header|cookie|consent|social|share)", re.I)

def _link_density(tag):
    links = tag.find_all("a")
    if not links:
        return 0.0
    link_text = " ".join(a.get_text(" ", strip=True) for a in links)
    total = len(tag.get_text(" ", strip=True)) or 1
    return min(len(link_text) / total, 1.0)

def _is_noise_container(tag):
    if tag is None or not hasattr(tag, "get"):
        return False
    tag_id = tag.get("id") or ""
    tag_cls = " ".join(tag.get("class") or [])
    attrs = f"{tag_id} {tag_cls}"
    return bool(MENU_HINT.search(attrs))

def _get_main(soup: BeautifulSoup):
    m = soup.select_one("main") or soup.select_one("[role=main]") or soup.select_one("article")
    return m or (soup.body or soup)

def clean_html(html: str):
    soup = BeautifulSoup(html, "html.parser")

    # drop obvious noise
    for t in DROP_TAGS:
        for n in soup.find_all(t):
            n.decompose()

    # drop containers that look like menus/headers/footers (if small)
    for n in list(soup.find_all(True)):
        try:
            if _is_noise_container(n):
                txt = n.get_text(strip=True) if hasattr(n, "get_text") else ""
                if len(txt) < 2000:
                    n.decompose()
        except Exception:
            continue

    title = soup.title.get_text(strip=True) if soup.title else None
    md = soup.find("meta", attrs={"name":"description"}) or soup.find("meta", attrs={"property":"og:description"})
    meta_description = (md.get("content") or "").strip() if md else None

    main = _get_main(soup)

    sections = []
    current = {"heading": None, "level": 0, "content": []}

    def flush():
        if current["heading"] or current["content"]:
            blocks, seen = [], set()
            for x in current["content"]:
                x = re.sub(r"\s+", " ", x).strip()
                if x and x not in seen and len(x) >= 30:
                    seen.add(x)
                    blocks.append(x)
            if blocks:
                sections.append({
                    "heading": current["heading"],
                    "level": current["level"],
                    "text": "\n\n".join(blocks),
                    "blocks": blocks
                })

    for el in main.descendants:
        if not getattr(el, "name", None):
            continue
        if el.name in {"h1","h2","h3","h4","h5","h6"}:
            flush()
            current = {
                "heading": el.get_text(" ", strip=True),
                "level": int(el.name[1]),
                "content": []
            }
            continue
        if el.name in {"p","li","figcaption"}:
            txt = el.get_text(" ", strip=True)
            if not txt:
                continue
            if _link_density(el) > 0.6:
                continue
            if len(txt) < 20:
                continue
            current["content"].append(txt)

    flush()

    if not sections:
        all_ps = []
        for p in main.find_all(["p","li","figcaption"]):
            t = p.get_text(" ", strip=True)
            if t and len(t) >= 30 and _link_density(p) <= 0.6:
                all_ps.append(t)
        text = "\n\n".join(all_ps)
    else:
        text = "\n\n\n".join(s["text"] for s in sections)

    return {
        "title": title,
        "meta_description": meta_description,
        "text": text,
        "sections": sections
    }
