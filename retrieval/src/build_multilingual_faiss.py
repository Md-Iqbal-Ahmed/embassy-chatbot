import json
import faiss
import numpy as np
from pathlib import Path
from multilingual_embeddings import (
    get_openai_embeddings,
    get_cohere_embeddings,
)
import os
import sys

corpus_path = Path("parser/data/clean/output.cleaned.json")
if not corpus_path.exists():
    raise FileNotFoundError("❌ Missing file: parser/data/clean/output.cleaned.json")

docs = json.loads(corpus_path.read_text(encoding="utf-8"))

# Normalize content field
texts = []
normalized_docs = []
# Use enumerate to get a counter 'i'
for i, d in enumerate(docs):
    text = d.get("content") or d.get("text") or ""
    if not text.strip():
        continue
    texts.append(text)
    
    # Create the new dictionary entry
    meta_entry = {"content": text, **{k: v for k, v in d.items() if k not in ["content", "text"]}}
    
    # Add 'id' field, using 'i' as fallback
    meta_entry["id"] = d.get("id", i) 
    
    normalized_docs.append(meta_entry)

print(f"📄 Loaded {len(texts)} cleaned documents for embedding.")


PROVIDERS = {
    "openai": get_openai_embeddings,
    "cohere": get_cohere_embeddings,
}


def save_embeddings(embeddings, docs, folder):
    import json, numpy as np, faiss, os
    os.makedirs(folder, exist_ok=True)

    np.save(f"{folder}/embeddings.npy", embeddings)

    # Save full docs as metadata (THE CORRECT WAY)
    with open(f"{folder}/meta.json", "w", encoding="utf-8") as f:
        json.dump(docs, f, ensure_ascii=False, indent=2)

    d = embeddings.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embeddings)
    faiss.write_index(index, f"{folder}/faiss_{os.path.basename(folder)}.index")

    print(f"✅ Saved FAISS index to {folder}")



for name, embed_func in PROVIDERS.items():
    print(f"\n🚀 Building FAISS index for {name.upper()} ...")

    embeddings = embed_func(texts)
    embeddings = np.array(embeddings, dtype=np.float32)

    folder = f"parser/data/vector/{name}"
    os.makedirs(folder, exist_ok=True)

    save_embeddings(embeddings, normalized_docs, folder)

    print(f"✅ Finished {name} ({len(texts)} vectors, dim={embeddings.shape[1]})")

print("\n🎉 All FAISS indexes successfully built!")


if __name__ == "__main__":
    if "streamlit" in sys.modules:
        import streamlit as st
        st.success("✅ FAISS index building complete!")