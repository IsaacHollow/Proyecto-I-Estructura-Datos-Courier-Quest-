from dataclasses import dataclass
from typing import List

@dataclass
class Pedido:
    id: str = ""
    priority: int = 0
    payout: float = 0.0
    weight: float = 0.0
    deadline: str = ""
    release_time: int = 0
    pickup: List[int] = None
    dropoff: List[int] = None
