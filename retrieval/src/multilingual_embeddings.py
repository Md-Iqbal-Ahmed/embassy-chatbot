import os
import sys
import json
import numpy as np
import faiss
from pathlib import Path

try:
    import tomllib  
except ModuleNotFoundError:
    import toml as tomllib  

import openai
import cohere

CONFIG_PATH = r"E:\chatbot\Chatbot_BD_Embassy_Berlin-task-3-search_fiass-streamlit\streamlit\.streamlit\secrets.toml"

if not os.path.exists(CONFIG_PATH):
    print("❌ ERROR: secrets.toml file not found at:")
    print(CONFIG_PATH)
    sys.exit(1)

with open(CONFIG_PATH, "rb") as f:
    config = tomllib.load(f)

# Extract values
provider = config.get("settings", {}).get("provider", "openai").lower()
OPENAI_API_KEY = config.get("openai", {}).get("api_key")
COHERE_API_KEY = config.get("cohere", {}).get("api_key")


openai.api_key = OPENAI_API_KEY
co = cohere.Client(COHERE_API_KEY)


def get_openai_embeddings(texts: list[str]) -> np.ndarray:
    print("🚀 Using OpenAI embeddings...")
    embeddings = []
    for i in range(0, len(texts), 100):
        batch = texts[i:i + 100]
        try:
            response = openai.embeddings.create(
                model="text-embedding-3-large",
                input=batch
            )
            batch_vectors = [d.embedding for d in response.data]
            embeddings.extend(batch_vectors)
        except Exception as e:
            print(f"⚠️ OpenAI batch {i}-{i+100} failed: {e}")
    return np.array(embeddings, dtype=np.float32)


def get_cohere_embeddings(texts: list[str]) -> np.ndarray:
    print("🚀 Using Cohere embeddings...")
    try:
        response = co.embed(
    texts=texts,
    model="embed-multilingual-v3.0",
    input_type="search_document"
)

        return np.array(response.embeddings, dtype=np.float32)
    except Exception as e:
        print(f"⚠️ Cohere embedding failed: {e}")
        return np.zeros((len(texts), 1024), dtype=np.float32)  # fallback


def get_provider_function(provider_name: str):
    funcs = {
        "openai": get_openai_embeddings,
        "cohere": get_cohere_embeddings,
    }
    if provider_name not in funcs:
        raise ValueError(f"❌ Unknown provider: {provider_name}")
    return funcs[provider_name]



def save_faiss_index(embeddings: np.ndarray, meta: dict, provider: str):
    folder = Path(f"parser/data/vector/{provider}")
    folder.mkdir(parents=True, exist_ok=True)

    np.save(folder / "embeddings.npy", embeddings)
    with open(folder / "meta.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)
    faiss.write_index(index, str(folder / f"faiss_{provider}.index"))

    print(f"✅ Saved FAISS index and embeddings for {provider} at: {folder}")



def build_embeddings(input_file: str):
    if not os.path.exists(input_file):
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    texts = [item["text"] for item in data]
    print(f"📄 Loaded {len(texts)} texts from {input_file}")

    embedding_func = get_provider_function(provider)
    embeddings = embedding_func(texts)

    meta = {"provider": provider, "num_texts": len(texts)}
    save_faiss_index(embeddings, meta, provider)



if __name__ == "__main__":
    build_embeddings("parser/data/clean/output.cleaned.json")
