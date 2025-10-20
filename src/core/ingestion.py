"""Main ingestion pipeline for PDF extraction, metadata loading, and chunking."""
from pathlib import Path
from typing import List, Dict
from .pdf_extractor import extract_from_multiple_pdfs
from .csv_loader import load_csv_metadata, match_metadata_to_documents
from .chunker import chunk_document


class IngestionPipeline:
    """Handles the complete document ingestion workflow."""
    
    def __init__(self, chunk_size: int = 512):
        """Initialize the ingestion pipeline."""
        self.chunk_size = chunk_size
    
    def ingest_documents(
        self,
        pdf_dir: str,
        csv_path: str = None
    ) -> List[Dict[str, any]]:
        """Ingest all PDFs from a directory and optionally load metadata."""
        pdf_dir = Path(pdf_dir)
        
        pdf_files = list(pdf_dir.glob("*.pdf"))
        if not pdf_files:
            raise ValueError(f"No PDF files found in {pdf_dir}")
        
        print(f"Found {len(pdf_files)} PDF files")
        
        pdf_paths = [str(p) for p in pdf_files]
        documents = extract_from_multiple_pdfs(pdf_paths)
        print(f"Extracted text from {len(documents)} documents")
        
        if csv_path:
            metadata = load_csv_metadata(csv_path)
            documents = match_metadata_to_documents(documents, metadata)
            print(f"Matched metadata from {csv_path}")
        
        all_chunks = []
        for doc in documents:
            chunks = chunk_document(doc, self.chunk_size)
            all_chunks.extend(chunks)
        
        print(f"Created {len(all_chunks)} total chunks")
        
        return all_chunks
    
    def ingest_single_pdf(
        self,
        pdf_path: str,
        metadata: Dict = None
    ) -> List[Dict[str, any]]:
        """Ingest a single PDF file."""
        from .pdf_extractor import extract_text_from_pdf
        
        document = extract_text_from_pdf(pdf_path)
        
        if metadata:
            document['metadata'] = metadata
        else:
            document['metadata'] = {}
        
        chunks = chunk_document(document, self.chunk_size)
        
        return chunks
