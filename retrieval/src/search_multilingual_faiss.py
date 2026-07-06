import json
import re
from typing import Dict, List
from pathlib import Path
from faiss_index import load_meta  


def keyword_search(query: str, meta: List[Dict], top_k: int) -> List[Dict]:
   
    results = []
    query_lower = query.lower()

    for idx, doc in enumerate(meta):
        content = doc.get("content", "").lower()
        
        if query_lower in content:
            score = 1.0  
            
            entry = dict(doc)
            entry["score"] = score
            entry["id"] = int(doc.get("id", idx)) #
            entry["search_type"] = "keyword"
            results.append(entry)

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]


def search_provider(provider: str, query: str, top_k: int = 5, base_dir: str = "parser/data/vector") -> Dict: #
    """
    Performs a KEYWORD-ONLY search by loading the specified provider's meta.json.
    """
    
    meta_path = Path(base_dir) / provider / "meta.json"
    
    if not meta_path.exists():
        raise FileNotFoundError(f"Meta file not found at: {meta_path}")

    print(f"Loading metadata from: {meta_path}")
    meta = load_meta(meta_path) #

    keyword_results = keyword_search(query, meta, top_k)

    return {
        "provider": provider,
        "meta_path": str(meta_path),
        "results": keyword_results
    }


def print_neat_results(response_dict: Dict, query: str):
    """
    Prints the search results in a clean, ID-focused format.
    Creates a "keyword-in-context" snippet.
    """
    results = response_dict.get("results", [])
    
    if not results:
        print("  No matches found.")
        return
    
    query_lower = query.lower()
    
    for res in results:
        doc_id = res.get('id')
        content = res.get('content', '')
        
        # --- New Smart Snippet Logic ---
        content_lower = content.lower()
        find_index = content_lower.find(query_lower)
        
        context_window = 80  # Characters before and after the keyword
        
        if find_index != -1:
            # Found the query, create snippet around it
            start_index = max(0, find_index - context_window)
            end_index = min(len(content), find_index + len(query) + context_window)
            
            snippet = content[start_index:end_index]
            
            # Add ... to show context
            if start_index > 0:
                snippet = "..." + snippet
            if end_index < len(content):
                snippet = snippet + "..."
        else:
            # Fallback (in case of a bug)
            snippet = (content[:150] + "...") if len(content) > 150 else content
        # --- End New Smart Snippet Logic ---

        print(f"  > ID: {doc_id}")
        # Changed "Content" to "Snippet" for clarity
        print(f"    Snippet: \"{snippet}\"\n") 


if __name__ == "__main__":
    import json

    print("Starting Interactive Keyword Search Engine.")
    print("Searches both 'openai' and 'cohere' metadata.")
    print("(Type 'exit' or 'quit' to stop)\n")

    while True:
        query = input("Enter your search query: ") # query is stored here

        if query.lower() in ["exit", "quit"]:
            print("Exiting search engine. Goodbye!")
            break
        
        if not query.strip():
            print("Please enter a query.")
            continue

        print(f"\n--- Searching for: '{query}' ---")

        try:
            print("--- 1. Results from 'openai' metadata ---")
            results_openai = search_provider("openai", query, top_k=3)
            # We now pass the 'query' to our new function
            print_neat_results(results_openai, query) #
        except Exception as e:
            print(f"❌ OpenAI search failed: {e}")

        print("\n" + "="*30 + "\n")

        try:
            print("--- 2. Results from 'cohere' metadata ---")
            results_cohere = search_provider("cohere", query, top_k=3)
            # We also pass the 'query' here
            print_neat_results(results_cohere, query) #
        except Exception as e:
            print(f"❌ Cohere search failed: {e}")
        
        print("\n" + "="*50 + "\n") # Fixed the typo from your file