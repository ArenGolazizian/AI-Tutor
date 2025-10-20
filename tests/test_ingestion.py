"""Tests for ingestion pipeline."""
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.chunker import chunk_text, chunk_document
from core.csv_loader import load_csv_metadata, match_metadata_to_documents
from core.pdf_extractor import extract_text_from_pdf
from core.ingestion import IngestionPipeline


def test_chunking():
    """Test text chunking and show sample output."""
    print("\n" + "="*60)
    print("TEST: Text Chunking")
    print("="*60)
    
    text = "Machine learning is artificial intelligence. " * 50
    chunks = chunk_text(text, chunk_size=512)
    
    print(f"\nCreated {len(chunks)} chunks from text")
    print(f"\nSample Chunk (chunk 0):")
    print(f"  - text: '{chunks[0]['text'][:80]}...'")
    print(f"  - chunk_id: {chunks[0]['chunk_id']}")
    print(f"  - token_count: {chunks[0]['token_count']}")
    print(f"  - start_pos: {chunks[0]['start_pos']}")
    print(f"  - end_pos: {chunks[0]['end_pos']}")
    
    assert len(chunks) > 0
    assert all('text' in chunk for chunk in chunks)
    assert all('token_count' in chunk for chunk in chunks)
    print("\nAll assertions passed")


def test_chunk_with_metadata():
    """Test chunking a document with metadata attached."""
    print("\n" + "="*60)
    print("TEST: Chunking with Metadata")
    print("="*60)
    
    doc = {
        'filename': 'test_math.pdf',
        'text': 'Algebra is the study of mathematical symbols. ' * 30,
        'metadata': {
            'subject': 'Mathematics',
            'grade_level': '9',
            'topic': 'Algebra'
        }
    }
    
    chunks = chunk_document(doc, chunk_size=512)
    
    print(f"\nDocument: {doc['filename']}")
    print(f"Created {len(chunks)} chunks")
    print(f"\nSample Chunk with Metadata:")
    print(f"  - filename: {chunks[0]['filename']}")
    print(f"  - text: '{chunks[0]['text'][:60]}...'")
    print(f"  - chunk_id: {chunks[0]['chunk_id']}")
    print(f"  - token_count: {chunks[0]['token_count']}")
    print(f"  - metadata:")
    print(f"      • subject: {chunks[0]['metadata']['subject']}")
    print(f"      • grade_level: {chunks[0]['metadata']['grade_level']}")
    print(f"      • topic: {chunks[0]['metadata']['topic']}")
    
    assert chunks[0]['filename'] == 'test_math.pdf'
    assert chunks[0]['metadata']['subject'] == 'Mathematics'
    print("\nAll assertions passed")


def test_pdf_extraction():
    """Test PDF extraction from demo files."""
    print("\n" + "="*60)
    print("TEST: PDF Text Extraction")
    print("="*60)
    
    demo_path = Path(__file__).parent.parent / "data" / "demo"
    pdf_file = demo_path / "algebra_basics.pdf"
    
    if pdf_file.exists():
        result = extract_text_from_pdf(str(pdf_file))
        
        print(f"\nPDF: {result['filename']}")
        print(f"Pages: {result['num_pages']}")
        print(f"Total characters: {len(result['text'])}")
        print(f"\nText preview:")
        print(f"  {result['text'][:150]}...")
        
        assert result['num_pages'] > 0
        assert len(result['text']) > 0
        print("\nAll assertions passed")
    else:
        print("\nSkipping - demo PDF not found")
        print("  Run: python scripts/generate_demo_data.py")


def test_csv_metadata():
    """Test CSV metadata loading and matching."""
    print("\n" + "="*60)
    print("TEST: CSV Metadata Loading")
    print("="*60)
    
    demo_path = Path(__file__).parent.parent / "data" / "demo"
    csv_file = demo_path / "metadata.csv"
    
    if csv_file.exists():
        metadata = load_csv_metadata(str(csv_file))
        
        print(f"\nLoaded {len(metadata)} metadata entries")
        print(f"\nSample metadata entry:")
        for key, value in metadata[0].items():
            print(f"  - {key}: {value}")
        
        docs = [{'filename': metadata[0]['filename'], 'text': 'Test content'}]
        matched = match_metadata_to_documents(docs, metadata)
        
        print(f"\nMatched metadata to document")
        print(f"  Document: {matched[0]['filename']}")
        print(f"  Subject: {matched[0]['metadata']['subject']}")
        
        assert len(metadata) > 0
        assert matched[0]['metadata']['subject'] is not None
        print("\nAll assertions passed")
    else:
        print("\nSkipping - metadata CSV not found")


def test_full_ingestion_pipeline():
    """Test complete ingestion pipeline with demo data."""
    print("\n" + "="*60)
    print("TEST: Full Ingestion Pipeline")
    print("="*60)
    
    demo_path = Path(__file__).parent.parent / "data" / "demo"
    csv_path = demo_path / "metadata.csv"
    
    if demo_path.exists() and csv_path.exists():
        pipeline = IngestionPipeline(chunk_size=512)
        chunks = pipeline.ingest_documents(
            pdf_dir=str(demo_path),
            csv_path=str(csv_path)
        )
        
        print(f"\nTotal chunks created: {len(chunks)}")
        
        target_doc = "algebra_basics.pdf"
        doc_chunks = [c for c in chunks if c['filename'] == target_doc]
        
        print(f"\n" + "="*60)
        print(f"DETAILED VIEW: All chunks from {target_doc}")
        print("="*60)
        print(f"Total chunks for this document: {len(doc_chunks)}")
        print(f"Subject: {doc_chunks[0]['metadata'].get('subject', 'N/A')}")
        print(f"Grade: {doc_chunks[0]['metadata'].get('grade_level', 'N/A')}")
        print()
        
        for i, chunk in enumerate(doc_chunks):
            print(f"--- Chunk {i} ---")
            print(f"  chunk_id: {chunk['chunk_id']}")
            print(f"  token_count: {chunk['token_count']}")
            print(f"  text_length: {len(chunk['text'])} chars")
            print(f"  text: {chunk['text']}")
            print()
        
        print("\n" + "="*60)
        print("SUMMARY: All documents")
        print("="*60)
        docs_summary = {}
        for chunk in chunks:
            fname = chunk['filename']
            if fname not in docs_summary:
                docs_summary[fname] = {
                    'count': 0,
                    'subject': chunk['metadata'].get('subject', 'N/A'),
                    'grade': chunk['metadata'].get('grade_level', 'N/A')
                }
            docs_summary[fname]['count'] += 1
        
        for fname, info in docs_summary.items():
            print(f"  {fname}")
            print(f"     Subject: {info['subject']}, Grade: {info['grade']}")
            print(f"     Chunks: {info['count']}")
        
        assert len(chunks) > 0
        assert all('metadata' in chunk for chunk in chunks)
        assert chunks[0]['metadata'].get('subject') is not None
        print("\nAll assertions passed")
    else:
        print("\nSkipping - demo data not found")
        print("  Run: python scripts/generate_demo_data.py")


