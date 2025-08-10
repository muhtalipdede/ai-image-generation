from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Report:
    generated_at: object  # Firestore timestamp
    stats: Dict[str, Any]
    credit_summary: Dict[str, int]
