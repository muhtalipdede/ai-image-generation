from dataclasses import dataclass
from typing import Optional

@dataclass
class Transaction:
    transaction_id: str
    user_id: str
    type: str  # 'deduction' or 'refund'
    credits: int
    generation_request_id: str
    timestamp: object  # Firestore timestamp
