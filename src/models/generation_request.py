from dataclasses import dataclass
from typing import Optional

@dataclass
class GenerationRequest:
    generation_request_id: str
    user_id: str
    model: str
    style: str
    color: str
    size: str
    prompt: str
    status: str
    image_url: Optional[str]
    cost: int
    created_at: object  # Firestore timestamp
    completed_at: Optional[object] = None
