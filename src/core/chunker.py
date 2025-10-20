"""Text chunking module with recursive splitting strategy."""
import tiktoken
from typing import List, Dict


def chunk_text(
    text: str,
    chunk_size: int = 512,
    separators: List[str] = None
) -> List[Dict[str, any]]:
    """Recursively chunk text using hierarchical separators (paragraph -> sentence -> word -> char)."""
    if separators is None:
        separators = ["\n\n", "\n", ". ", " ", ""]
    
    encoding = tiktoken.get_encoding("cl100k_base")
    
    def _split_recursive(text: str, seps: List[str]) -> List[str]:
        """Recursively split text trying each separator."""
        if not seps or not text.strip():
            return [text] if text.strip() else []
        
        separator = seps[0]
        remaining_seps = seps[1:]
        
        if separator:
            splits = text.split(separator)
        else:
            return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
        
        final_chunks = []
        for split in splits:
            if not split.strip():
                continue
                
            tokens = len(encoding.encode(split))
            
            if tokens <= chunk_size:
                final_chunks.append(split)
            else:
                sub_chunks = _split_recursive(split, remaining_seps)
                final_chunks.extend(sub_chunks)
        
        return final_chunks
    
    raw_chunks = _split_recursive(text, separators)
    
    chunks = []
    position = 0
    for i, chunk_text in enumerate(raw_chunks):
        chunk_text = chunk_text.strip()
        if chunk_text:
            tokens = encoding.encode(chunk_text)
            chunks.append({
                "chunk_id": i,
                "text": chunk_text,
                "token_count": len(tokens),
                "start_pos": position,
                "end_pos": position + len(chunk_text)
            })
            position += len(chunk_text)
    
    return chunks


def chunk_document(
    document: Dict[str, any],
    chunk_size: int = 512
) -> List[Dict[str, any]]:
    """Chunk a document and preserve its metadata."""
    chunks = chunk_text(document['text'], chunk_size)
    
    for chunk in chunks:
        chunk['filename'] = document.get('filename', 'unknown')
        chunk['metadata'] = document.get('metadata', {})
    
    return chunks
