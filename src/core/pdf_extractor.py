"""PDF text extraction module."""
import pdfplumber
from pathlib import Path
from typing import Dict, List


def extract_text_from_pdf(pdf_path: str) -> Dict[str, any]:
    """Extract text from a PDF file with paragraph breaks."""
    pdf_path = Path(pdf_path)
    
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    pages_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                lines = page_text.split('\n')
                processed_lines = []
                
                for i, line in enumerate(lines):
                    stripped = line.strip()
                    if not stripped:
                        continue
                    
                    processed_lines.append(stripped)
                    
                    if (i < len(lines) - 1 and 
                        stripped and 
                        stripped[-1] in '.!?:' and
                        lines[i + 1].strip() and
                        lines[i + 1].strip()[0].isupper()):
                        processed_lines.append('')
                
                page_text = '\n'.join(processed_lines)
                pages_text.append(page_text)
    
    full_text = "\n\n".join(pages_text)
    
    return {
        "filename": pdf_path.name,
        "num_pages": len(pages_text),
        "text": full_text,
        "pages": pages_text
    }


def extract_from_multiple_pdfs(pdf_paths: List[str]) -> List[Dict[str, any]]:
    """Extract text from multiple PDF files."""
    results = []
    for pdf_path in pdf_paths:
        try:
            result = extract_text_from_pdf(pdf_path)
            results.append(result)
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            
    return results
