import os, toml
import numpy as np
from typing import List, Union
from pathlib import Path
import openai
import cohere  

CONFIG_PATH = Path(
    r"E:\chatbot\Chatbot_BD_Embassy_Berlin-task-3-search_fiass-streamlit\streamlit\.streamlit\secrets.toml"
)

config = toml.load(CONFIG_PATH)


provider_default = config.get("settings", {}).get("provider", "openai").lower()
OPENAI_API_KEY = config.get("openai", {}).get("api_key")
COHERE_API_KEY = config.get("cohere", {}).get("api_key")

if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not COHERE_API_KEY:
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")

openai.api_key = OPENAI_API_KEY
co = cohere.Client(COHERE_API_KEY) if COHERE_API_KEY else None


def _ensure_float32(arr: Union[np.ndarray, list]) -> np.ndarray:
    arr = np.array(arr, dtype=np.float32)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    return arr


def embed_openai(texts: List[str], model: str = "text-embedding-3-large") -> np.ndarray:
    if not openai or not OPENAI_API_KEY:
        raise RuntimeError("OpenAI API not configured")
    resp = openai.embeddings.create(model=model, input=texts)
    vectors = [r.embedding for r in resp.data]
    return _ensure_float32(vectors)


def embed_cohere(texts: List[str], model: str = "embed-multilingual-v3.0") -> np.ndarray:
    if not co: # Check for the client, not the key
        raise RuntimeError("Cohere client not configured")
    
    resp = co.embed(texts=texts, model=model, input_type="search_query")
    return _ensure_float32(resp.embeddings)


def embed_texts(texts: List[str], provider: str = "openai") -> np.ndarray:
    provider = provider.lower()
    if provider == "openai":
        return embed_openai(texts)
    elif provider == "cohere":
        return embed_cohere(texts)
    else:
        raise ValueError(f"Unsupported provider '{provider}'")


def embed_text(text: str, provider: str = "openai") -> np.ndarray:
    return embed_texts([text], provider=provider)