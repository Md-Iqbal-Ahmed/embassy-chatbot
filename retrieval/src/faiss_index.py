from pathlib import Path
import json
import faiss


def save_faiss_index(index, path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(p))


def load_faiss_index(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"FAISS index not found: {p}")
    return faiss.read_index(str(p))


def save_meta(meta_rows, path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(meta_rows, ensure_ascii=False, indent=2), encoding="utf-8")


def load_meta(path):
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Meta JSON not found: {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def find_index_and_meta(provider: str, base_dir: str = "parser/data/vector"):
    base = Path(base_dir)
    if not base.exists():
        raise FileNotFoundError(f"Base directory not found: {base_dir}")

    candidates = list(base.rglob(f"*{provider}*.index"))
    if not candidates:
        raise FileNotFoundError(f"No .index file found for provider '{provider}' in {base_dir}")
    index_path = candidates[0]

    meta_path = index_path.parent / "meta.json"
    if not meta_path.exists():
        metas = list(base.rglob("meta.json"))
        if not metas:
            raise FileNotFoundError(f"No meta.json found under {base_dir}")
        meta_path = metas[0]

    return index_path, meta_path
