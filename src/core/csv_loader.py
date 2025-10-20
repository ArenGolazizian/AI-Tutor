"""CSV metadata loading module."""
import csv
from pathlib import Path
from typing import List, Dict


def load_csv_metadata(csv_path: str) -> List[Dict[str, str]]:
    """Load metadata from a CSV file."""
    csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    metadata_list = []
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            metadata_list.append(dict(row))
    
    return metadata_list


def match_metadata_to_documents(
    documents: List[Dict], 
    metadata: List[Dict]
) -> List[Dict]:
    """Match document metadata to extracted PDF documents by filename."""
    metadata_lookup = {item['filename']: item for item in metadata}
    
    for doc in documents:
        filename = doc['filename']
        if filename in metadata_lookup:
            doc['metadata'] = metadata_lookup[filename]
        else:
            doc['metadata'] = {}
    
    return documents
