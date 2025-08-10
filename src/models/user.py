from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    user_id: str
    display_name: str
    credits: int
