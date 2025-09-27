from dataclasses import dataclass

@dataclass
class Repartidor:
    nombre: str
    resistencia: int = 100
    velocidad: int = 3
    reputacion: int = 70
