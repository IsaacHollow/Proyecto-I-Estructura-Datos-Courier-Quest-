import pygame
from dataclasses import dataclass, field
from typing import Tuple, Optional

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
    status: str = "pendiente"     # pendiente, en curso, entregado
    sprite_path: str = "assets/package.png"
    imagen: Optional[pygame.Surface] = field(default=None)

    # Métodos auxiliares
    def es_prioritario(self) -> bool:
        """Retorna True si el pedido tiene prioridad mayor que 0"""
        return self.priority > 0

    def tiempo_restante(self, tiempo_actual: int) -> int:
        """Calcula el tiempo restante hasta el deadline"""
        return max(0, self.deadline - tiempo_actual)
    
    def cargar_sprite(self):
        if self.imagen is None:
            self.imagen = pygame.image.load(self.sprite_path).convert_alpha()
            self.imagen = pygame.transform.scale(self.imagen, (50, 50))  # tamaño tile