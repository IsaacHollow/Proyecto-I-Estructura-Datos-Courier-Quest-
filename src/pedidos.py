from dataclasses import dataclass
from typing import Tuple

@dataclass
class Pedido:
    id: str
    priority: int
    payout: float
    weight: float
    deadline: str
    release_time: int
    pickup: Tuple[int, int]
    dropoff: Tuple[int, int]
