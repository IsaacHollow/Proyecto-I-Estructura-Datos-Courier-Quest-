from dataclasses import dataclass

@dataclass
class Repartidor:
    name: str
    resistance: int = 100
    speed: float = 3
    reputation: int = 70
