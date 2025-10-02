# src/repartidor.py
import pygame

class Repartidor:
    """
    Repartidor con resistencia y clima:
    - se recupera +5/s estando quieto
    - se recupera +10/s si está en parque
    - consume resistencia al moverse según base + peso + clima
    - si resistencia llega a 0 sigue pudiendo moverse, pero más lento
    """

    def __init__(self, ancho_mapa, alto_mapa):
        self.ancho_mapa = ancho_mapa
        self.alto_mapa = alto_mapa

        self.sprites = {
            "arriba": pygame.image.load("assets/bicycle_up.png").convert_alpha(),
            "abajo": pygame.image.load("assets/bicycle_down.png").convert_alpha(),
            "izquierda": pygame.image.load("assets/bicycle_left.png").convert_alpha(),
            "derecha": pygame.image.load("assets/bicycle_right.png").convert_alpha()
        }
        self.direccion = "derecha"
        self.imagen = self.sprites[self.direccion]
        self.rect = self.imagen.get_rect(center=(ancho_mapa // 2, alto_mapa // 2))

        self.vel_base = 3.0  # celdas/seg
        self.resistencia = 100.0
        self.peso_total = 0.0
        self.reputacion = 70.0

    # multiplicador por peso
    def _mult_peso(self):
        m = 1.0 - 0.03 * self.peso_total
        return max(0.8, m)

    def _mult_reputacion(self):
        return 1.05 if self.reputacion >= 90.0 else 1.0

    def _mult_resistencia(self):
        if self.resistencia > 30.0:
            return 1.0
        if 10.0 < self.resistencia <= 30.0:
            return 0.8
        if self.resistencia <= 0.0:
            return 0.5  # sigue moviéndose, pero más lento
        return 0.8

    def _clima_velocidad(self, clima):
        return clima.obtener_multiplicador() if hasattr(clima, "obtener_multiplicador") else 1.0

    def _clima_consumo_extra(self, clima):
        return clima.obtener_extra_resistencia() if hasattr(clima, "obtener_extra_resistencia") else 0.0

    def actualizar(self, teclas, dt, clima, tam_tile, mult_superficie, en_parque=False):
        """
        - teclas: pygame.key.get_pressed()
        - dt: segundos
        - clima: objeto clima
        - tam_tile: tamaño del tile en px
        - mult_superficie: multiplicador de terreno (ej. 0.95)
        - en_parque: bool -> si True, recuperación mayor
        """

        # velocidad en px/seg con multiplicadores
        vel_px = (self.vel_base * tam_tile *
                  self._mult_peso() *
                  self._mult_reputacion() *
                  self._mult_resistencia() *
                  self._clima_velocidad(clima) *
                  mult_superficie)

        dx = dy = 0.0
        movio = False

        if teclas[pygame.K_LEFT] and self.rect.left > 0:
            dx = -vel_px * dt
            self.direccion = "izquierda"
        if teclas[pygame.K_RIGHT] and self.rect.right < self.ancho_mapa:
            dx = vel_px * dt
            self.direccion = "derecha"
        if teclas[pygame.K_UP] and self.rect.top > 0:
            dy = -vel_px * dt
            self.direccion = "arriba"
        if teclas[pygame.K_DOWN] and self.rect.bottom < self.alto_mapa:
            dy = vel_px * dt
            self.direccion = "abajo"

        # mover
        if dx or dy:
            self.rect.x += int(dx)
            self.rect.y += int(dy)
            movio = True

        # resistencia
        if movio:
            celdas = (abs(dx) + abs(dy)) / float(tam_tile)
            if celdas > 0:
                consumo = 0.5
                if self.peso_total > 3.0:
                    consumo += 0.2 * (self.peso_total - 3.0)
                consumo += self._clima_consumo_extra(clima)
                self.resistencia -= consumo * celdas
        else:
            recuperacion = 10.0 if en_parque else 5.0
            self.resistencia += recuperacion * dt

        # limitar resistencia
        self.resistencia = min(100.0, max(0.0, self.resistencia))

        # actualizar sprite
        self.imagen = self.sprites[self.direccion]
