import pygame
from dataclasses import dataclass, field
from typing import Tuple, Optional


@dataclass
class Pedido:
    id: str
    priority: int
    payout: float
    weight: float
    deadline: int
    release_time: int
    pickup: Tuple[int, int]
    dropoff: Tuple[int, int]
    status: str = "pendiente"
    holder: Optional[str] = None
    sprite_pickup: str = "assets/package.png"
    sprite_dropoff: str = "assets/destination_marker.png"
    imagen: Optional[pygame.Surface] = field(default=None)

    # Métodos auxiliares
    def es_prioritario(self) -> bool:
        return self.priority > 0

    def tiempo_restante(self, tiempo_actual: int) -> int:
        return max(0, self.deadline - tiempo_actual)

    def cargar_sprite(self, size: Tuple[int, int]):
        if self.status == "pendiente":
            ruta = self.sprite_pickup
        elif self.status == "en curso":
            ruta = self.sprite_dropoff
        else:
            self.imagen = None
            return

        self.imagen = pygame.image.load(ruta).convert_alpha()
        self.imagen = pygame.transform.scale(self.imagen, size)

    def __getstate__(self):
        """Prepara el estado para ser guardado (excluye la superficie de Pygame)."""
        state = self.__dict__.copy()
        # Eliminamos el atributo 'imagen' que no se puede guardar
        if 'imagen' in state:
            del state['imagen']
        return state

    def __setstate__(self, state):
        """Restaura el estado después de cargar."""
        self.__dict__.update(state)
        # La imagen se deja como None. Se cargará dinámicamente
        # la próxima vez que se llame a `dibujar()` en JuegoView.
        self.imagen = None