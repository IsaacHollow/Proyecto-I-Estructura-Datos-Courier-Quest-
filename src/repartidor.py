
import pygame

ANCHO, ALTO = 800, 600


class Repartidor:
    def __init__(self):
        self.sprites = {
            "arriba": pygame.image.load("assets/bicycle_up.png").convert_alpha(),
            "abajo": pygame.image.load("assets/bicycle_down.png").convert_alpha(),
            "izquierda": pygame.image.load("assets/bicycle_left.png").convert_alpha(),
            "derecha": pygame.image.load("assets/bicycle_right.png").convert_alpha()
        }
        self.direccion = "derecha"  # Dirección inicial
        self.imagen = self.sprites[self.direccion]
        self.rect = self.imagen.get_rect(center=(ANCHO // 2, ALTO // 2))
        self.velocidad: float = 3

    def mover(self, teclas):
        if teclas[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.velocidad
            self.direccion = "izquierda"
        elif teclas[pygame.K_RIGHT] and self.rect.right < ANCHO:
            self.rect.x += self.velocidad
            self.direccion = "derecha"
        elif teclas[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.velocidad
            self.direccion = "arriba"
        elif teclas[pygame.K_DOWN] and self.rect.bottom < ALTO:
            self.rect.y += self.velocidad
            self.direccion = "abajo"

        self.imagen = self.sprites[self.direccion]
