# embeddings_handler.py
import os
import pickle
import numpy as np
from typing import List
from openai import OpenAI
import cohere


openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
cohere_client = cohere.Client(os.getenv("COHERE_API_KEY"))

def get_embedding_openai(texts: List[str]):
    response = openai_client.embeddings.create(
        input=texts,
        model="text-embedding-3-large"
    )
    return [item.embedding for item in response.data]

def get_embedding_cohere(texts):
    response = cohere_client.embed(
        texts=texts,
        model="embed-multilingual-v3.0",
        input_type="search_document"  
    )
    return response.embeddings

def get_or_create_embeddings(texts: List[str], provider: str, file_path: str):
    if os.path.exists(file_path):
        print(f"🔹 Loading existing embeddings from {file_path}")
        with open(file_path, "rb") as f:
            return pickle.load(f)

    print(f"🔹 Generating new embeddings with {provider}...")
    if provider.lower() == "openai":
        embeddings = get_embedding_openai(texts)
    elif provider.lower() == "cohere":
        embeddings = get_embedding_cohere(texts)
    else:
        raise ValueError("Provider must be 'openai' or 'cohere'.")

    with open(file_path, "wb") as f:
        pickle.dump(embeddings, f)

    print(f"Saved embeddings to {file_path}")
    return embeddings
