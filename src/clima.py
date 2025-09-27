from dataclasses import dataclass, field
from typing import List

@dataclass
class Clima:
    temperatura: float
    humedad: float
    presion: float
    condition: str = "Clouds"
    intensity: int = 0
    conditions: List[str] = field(default_factory=lambda: [
        "clear", "clouds", "rain_light", "rain",
        "storm", "fog", "wind", "heat", "cold"
    ])
