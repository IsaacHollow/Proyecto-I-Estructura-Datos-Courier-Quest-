import pygame, sys
from random import randint


class Camera():
    def __init__(self, pantalla, map_width_px, map_height_px):
        self.pantalla = pantalla
        self.zoom = 1.0
        self.offset_x = 0
        self.offset_y = 0
        self.map_width_px = map_width_px
        self.map_height_px = map_height_px

    def center_on(self, target_rect):
        # Centra la cámara sobre el rectángulo del objetivo (el repartidor)
        pantalla_w, pantalla_h = self.pantalla.get_size()
        self.offset_x = target_rect.centerx - pantalla_w // 2
        self.offset_y = target_rect.centery - pantalla_h // 2
        # Opcional: Limitar para que no se salga del mapa
        self.offset_x = max(0, min(self.offset_x, self.map_width_px - pantalla_w))
        self.offset_y = max(0, min(self.offset_y, self.map_height_px - pantalla_h))

    def apply(self, pos):
        # Aplica el offset y zoom a una posición (x, y) en píxeles
        x, y = pos
        return int((x - self.offset_x) * self.zoom), int((y - self.offset_y) * self.zoom)