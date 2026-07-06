import faiss
import numpy as np

index = faiss.read_index("parser/data/vector/openai/faiss_openai.index")
print("Number of vectors in FAISS:", index.ntotal)

emb = np.load("parser/data/vector/openai/embeddings.npy")
print("Number of embeddings:", len(emb), " | Dimension:", emb.shape[1])