import pygame
import random
from src.repartidor import Repartidor


class RepartidorIA(Repartidor):
    def __init__(self, start_tile_x, start_tile_y, tile_size, dificultad: str = "facil"):
        super().__init__(start_tile_x, start_tile_y, tile_size)

        # Atributos específicos de la IA
        self.dificultad = dificultad
        self.movimiento_timer = 0
        self.intervalo_movimiento = 0.5


        self.inicializar_sprites(ruta_base="assets/player2.png")

    def actualizar_logica_ia(self, dt, city_map, colliders, weather):
        self.movimiento_timer += dt
        if self.movimiento_timer >= self.intervalo_movimiento and not self.is_moving:
            self.movimiento_timer = 0

            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            self.start_move(dx, dy, city_map, colliders, weather)
