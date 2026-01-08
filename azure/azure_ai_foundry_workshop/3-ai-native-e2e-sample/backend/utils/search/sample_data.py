from datetime import datetime, timezone
from typing import List, Dict, Any

def get_sample_literature() -> List[Dict[str, Any]]:
    """Generate sample literature documents for testing."""
    return [
        {
            "id": "1",
            "title": "Advances in Drug Discovery Using AI",
            "abstract": "This paper explores recent advances in using artificial intelligence for drug discovery and development.",
            "content": "Detailed discussion of AI applications in pharmaceutical research...",
            "authors": ["John Smith", "Jane Doe"],
            "publicationDate": datetime.now(timezone.utc).isoformat()
        },
        {
            "id": "2",
            "title": "Machine Learning in Clinical Trials",
            "abstract": "An overview of machine learning applications in clinical trial design and analysis.",
            "content": "Comprehensive analysis of ML impact on clinical research...",
            "authors": ["Alice Johnson", "Bob Wilson"],
            "publicationDate": datetime.now(timezone.utc).isoformat()
        }
    ]
