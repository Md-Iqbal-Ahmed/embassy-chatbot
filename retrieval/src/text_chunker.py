# retrieval/src/text_chunker.py
import re
from typing import List

class SimpleTextChunker:
    """
    A simple text chunker that splits by paragraphs and then
    by a fixed size with overlap.
    """
    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

    def chunk(self, text: str) -> List[str]:
        """
        Splits a long text into smaller, overlapping chunks.
        """
        if not text:
            return []
        
        # 1. Split by double newlines (paragraphs)
        paragraphs = re.split(r'\n\n+', text)
        all_chunks = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # 2. If paragraph is small enough, keep it
            if len(para) <= self.chunk_size:
                all_chunks.append(para)
            else:
                # 3. If paragraph is too long, split it by character
                start = 0
                while start < len(para):
                    end = start + self.chunk_size
                    chunk = para[start:end]
                    all_chunks.append(chunk)
                    # Move the start pointer
                    start += (self.chunk_size - self.chunk_overlap)
                    
        return [chunk for chunk in all_chunks if chunk] # Return non-empty chunks