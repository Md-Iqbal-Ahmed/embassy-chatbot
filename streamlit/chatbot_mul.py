# chatbot_mul.py
import os
import sys
import json
from pathlib import Path
import re 

import faiss
import toml
import numpy as np
import streamlit as st

import openai
import cohere

# --- Project Path Setup (Unchanged) ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Config Loading (Unchanged) ---
CONFIG_PATH = Path(
    r"E:\chatbot\Chatbot_BD_Embassy_Berlin-task-3-search_fiass-streamlit\streamlit\.streamlit\secrets.toml"
)
if not CONFIG_PATH.exists():
    st.error(f"❌ Config file missing at {CONFIG_PATH}")
    st.stop()
try:
    config = toml.load(CONFIG_PATH)
except Exception as e:
    st.error(f"❌ Failed to parse {CONFIG_PATH}: {e}")
    st.stop()
provider_default = config.get("settings", {}).get("provider", "openai").lower()
OPENAI_API_KEY = config.get("openai", {}).get("api_key")
COHERE_API_KEY = config.get("cohere", {}).get("api_key")
if not OPENAI_API_KEY:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not COHERE_API_KEY:
    COHERE_API_KEY = os.getenv("COHERE_API_KEY")
if provider_default == "openai" and not OPENAI_API_KEY:
    st.error("❌ Missing OpenAI API key in secrets.toml or environment.")
    st.stop()
if provider_default == "cohere" and not COHERE_API_KEY:
    st.error("❌ Missing Cohere API key in secrets.toml or environment.")
    st.stop()
openai.api_key = OPENAI_API_KEY
co = cohere.Client(COHERE_API_KEY) if COHERE_API_KEY else None

# --- Imports (Unchanged) ---
from retrieval.src.faiss_index import find_index_and_meta, load_faiss_index, load_meta
from retrieval.src.multilingual_embeddeds import embed_text

st.set_page_config(page_title="Embassy Chatbot", layout="centered", page_icon="🇧🇩")
st.title("🇧🇩 Bangladesh Embassy Berlin Chatbot")
st.markdown("---")


# ▼▼▼ 1. ADD THIS NEW HELPER FUNCTION ▼▼▼
def clean_content(content: str) -> str:
    """
    Attempts to clean the messy, nested JSON/byte-like content
    found in meta.json, as seen in the screenshot.
    """
    if not content or (not content.startswith("b'{") and not content.startswith("b'[") and not content.startswith("{")):
        return content
    
    try:
        # Strip the b'...' wrapper
        cleaned_str = content.strip("b'").strip("'")
        # Fix escaped quotes
        cleaned_str = cleaned_str.replace(r'\"', '"')
        
        inner_data = json.loads(cleaned_str)
        
        if isinstance(inner_data, dict):
            # Extract the *real* content
            real_content = inner_data.get('content', content)
            return real_content
        return content 
    except Exception:
        return content # Fallback
# ▲▲▲ END OF NEW FUNCTION ▲▲▲


# --- ensure_float32_and_2d (Unchanged) ---
def ensure_float32_and_2d(arr):
    arr = np.asarray(arr, dtype=np.float32)
    if arr.ndim == 1:
        arr = arr.reshape(1, -1)
    return arr

# --- search_with_provider_vector (Unchanged) ---
@st.cache_data
def search_with_provider_vector(query: str, provider_name: str, top_k: int = 5):
    base_dir = r"E:\chatbot\Chatbot_BD_Embassy_Berlin-task-3-search_fiass-streamlit\parser\data\vector"
    index_path, meta_path = find_index_and_meta(provider_name, base_dir=base_dir)
    index = load_faiss_index(index_path)
    meta = load_meta(meta_path)
    q_emb = embed_text(query, provider_name)
    q_emb = ensure_float32_and_2d(q_emb)
    D, I = index.search(q_emb, top_k)
    results = []
    for idx, dist in zip(I[0], D[0]):
        if int(idx) < 0 or int(idx) >= len(meta):
            continue
        rec = dict(meta[int(idx)])
        content = rec.get("content") or rec.get("text") or ""
        rec["content"] = content
        rec["score"] = float(dist)
        rec["display"] = rec.get("display", (content[:300] + ("..." if len(content) > 300 else "")))
        rec["id"] = int(rec.get("id", idx))
        results.append(rec)
    return results

# ▼▼▼ 2. UPDATE `keyword_search` TO USE THE CLEANER ▼▼▼
def keyword_search(query: str, meta: list[dict], top_k: int) -> list[dict]:
    results = []
    query_lower = query.lower()
    for idx, doc in enumerate(meta):
        # We clean the content *here*
        raw_content = doc.get("content", "")
        content = clean_content(raw_content).lower() # <-- USE CLEANER
        
        if query_lower in content:
            entry = dict(doc)
            entry['content'] = raw_content # Store the original raw content
            entry["score"] = 1.0
            entry["id"] = int(doc.get("id", idx))
            entry["search_type"] = "keyword"
            results.append(entry)
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

# --- search_with_provider_keyword (Unchanged) ---
@st.cache_data
def search_with_provider_keyword(query: str, provider_name: str, top_k: int = 5):
    base_dir = r"E:\chatbot\Chatbot_BD_Embassy_Berlin-task-3-search_fiass-streamlit\parser\data\vector"
    meta_path = Path(base_dir) / provider_name / "meta.json"
    if not meta_path.exists():
        st.error(f"Meta file not found: {meta_path}")
        return []
    meta = load_meta(meta_path)
    return keyword_search(query, meta, top_k)

# --- generate_answer_with_openai (Unchanged) ---
def generate_answer_with_openai(query: str, context: str):
    system_prompt = (
        "You are a helpful assistant for the Bangladesh Embassy in Berlin. "
        "Use only the provided context to answer the user accurately. "
        "If the answer isn't in the context, say you are not sure. "
        "Add short references if possible."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Question: {query}\n\nContext:\n{context}"},
    ]
    try:
        if hasattr(openai, "ChatCompletion"):
            resp = openai.ChatCompletion.create(model="gpt-4o-mini", messages=messages, temperature=0.3, max_tokens=600)
            text = resp.choices[0].message.get("content") if resp.choices and getattr(resp.choices[0], "message", None) else resp.choices[0].text
            return text.strip() if text else "⚠️ No text returned from OpenAI."
        else:
            resp = openai.chat.completions.create(model="gpt-4o-mini", messages=messages, temperature=0.3, max_tokens=600)
            return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Error generating answer: {e}"

# --- Streamlit UI Sidebar (Unchanged) ---
with st.sidebar:
    st.header("⚙️ Settings")
    search_mode = st.radio(
        "Search Mode:",
        ("Vector (Semantic)", "Keyword (Exact Match)"),
        help="**Vector:** Finds results by *meaning*.\n**Keyword:** Finds results by *exact word*."
    )
    provider = st.selectbox(
        "Choose Embedding Provider:",
        options=["openai", "cohere"],
        index=["openai", "cohere"].index(provider_default) if provider_default in ["openai", "cohere"] else 0,
        help="Select which embedding model to use (Vector search only).",
        disabled=(search_mode == "Keyword (Exact Match)")
    )

query = st.text_input("💬 Ask your question:")

# --- Main Search Logic (Unchanged) ---
if st.button("🔍 Search and Answer", use_container_width=True):
    if not query or not query.strip():
        st.warning("Please enter a question first.")
        st.stop()
    results = []
    if search_mode == "Vector (Semantic)":
        with st.spinner(f"Searching using {provider.upper()} vector embeddings..."):
            try:
                results = search_with_provider_vector(query, provider)
            except Exception as e:
                st.error(f"❌ Error during Vector search: {e}")
                st.stop()
    else: # Keyword Search
        with st.spinner(f"Searching for keywords..."):
            try:
                results_openai = search_with_provider_keyword(query, "openai")
                results_cohere = search_with_provider_keyword(query, "cohere")
                all_results = {}
                for r in results_openai + results_cohere:
                    all_results[r['id']] = r
                results = list(all_results.values())
            except Exception as e:
                st.error(f"❌ Error during Keyword search: {e}")
                st.stop()
    if not results:
        st.warning("No relevant results found.")
        st.stop()

    # ▼▼▼ 3. UPDATE `generate_answer` TO USE CLEAN CONTEXT ▼▼▼
    if search_mode == "Vector (Semantic)":
        # We clean the context *before* sending it to the LLM
        cleaned_contexts = [clean_content(r.get("content", "")) for r in results[:6]]
        context_text = "\n\n---\n\n".join(cleaned_contexts)
        
        with st.spinner("Generating final answer with GPT..."):
            final_answer = generate_answer_with_openai(query, context_text)
        st.markdown("## 🧠 Answer")
        st.write(final_answer)
        st.markdown("---")
        st.markdown("### 📚 Retrieved Chunks (Vector)")
    else:
        st.markdown("## 📚 Keyword Search Results")
        st.markdown("---")
    # ▲▲▲ END OF CHANGE ▲▲▲


    # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
    # --- 4. THIS IS THE FINAL MODIFIED DISPLAY LOOP ---
    # (This fixes the problem for BOTH search modes)
    # ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼
    
    query_lower = query.lower()
    
    for i, r in enumerate(results, 1):
        score_label = "distance" if search_mode == "Vector (Semantic)" else "match_score"
        doc_id = r.get('id', 'N/A')
        
        # --- 1. CLEAN THE CONTENT FIRST ---
        raw_content = r.get('content', '')
        content = clean_content(raw_content) # <-- USE OUR NEW FUNCTION
        
        # --- 2. Smart Snippet Logic (Now on clean text) ---
        content_lower = content.lower()
        find_index = content_lower.find(query_lower)
        context_window = 80
        
        if find_index != -1:
            # Found the query (like "High Commission..."), create snippet
            start_index = max(0, find_index - context_window)
            end_index = min(len(content), find_index + len(query) + context_window)
            snippet = content[start_index:end_index]
            if start_index > 0:
                snippet = "..." + snippet
            if end_index < len(content):
                snippet = snippet + "..."
        else:
            # Fallback (for semantic queries where words don't match)
            # This now shows the CLEAN beginning, not the messy data
            snippet = (content[:150] + "...") if len(content) > 150 else content
        # --- End Snippet Logic ---

        st.markdown(f"**Doc {i} | ID: {doc_id}** — *({score_label}={r.get('score', 0):.4f})*")
        st.markdown(f"> {snippet}")
        st.markdown("---")
    # ▲▲▲ END OF FINAL LOOP ▲▲▲