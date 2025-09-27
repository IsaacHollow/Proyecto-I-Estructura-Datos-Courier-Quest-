from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class Clima:
    city: str
    condition: str
    intensity: int
    conditions: List[str] = field(default_factory=list)
    transition: Dict[str, Dict[str, float]] = field(default_factory=dict)
