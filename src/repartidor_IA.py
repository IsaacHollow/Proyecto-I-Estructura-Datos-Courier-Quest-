import pygame
import random

REPARTIDOR_ANCHO = 35
REPARTIDOR_ALTO = 35
class RepartidorIA:

    def __init__(self, start_tile_x, start_tile_y, tile_size):
        self.tile_x = start_tile_x
        self.tile_y = start_tile_y
        self.tile_size = tile_size

        self.px = start_tile_x * tile_size
        self.py = start_tile_y * tile_size

        self.direccion = "abajo"
        self.frame_actual = 0
        self.anim_timer = 0

        self.direccion_timer = 0
        self.direccion_cooldown = 1.0

        self.sprite_sheet = pygame.image.load("assets/player2.png").convert_alpha()
        self.sprites = self.cargar_sprites(self.sprite_sheet)

        self.imagen = self.sprites[self.direccion][self.frame_actual]
        self.rect = self.imagen.get_rect(topleft=(self.px, self.py))


    def cargar_sprites(self, sheet):
        sprite_dict = {"arriba": [], "abajo": [], "izquierda": [], "derecha": []}
        frame_w = sheet.get_width() // 4
        frame_h = sheet.get_height() // 4
        direcciones = ["abajo", "izquierda", "derecha", "arriba"]

        for i, dir_name in enumerate(direcciones):
            for j in range(4):
                rect = pygame.Rect(j * frame_w, i * frame_h, frame_w, frame_h)
                frame = sheet.subsurface(rect)
                frame = pygame.transform.scale(frame, (REPARTIDOR_ANCHO, REPARTIDOR_ALTO))
                sprite_dict[dir_name].append(frame)

        return sprite_dict

    def decidir_movimiento(self, pedidos, city_map, weather):
        self.direccion_timer += 1/60  # ejemplo usando dt fijo si no pasas dt
        if self.direccion_timer > self.direccion_cooldown:
            self.direccion = random.choice(["arriba", "abajo", "izquierda", "derecha"])
            self.direccion_timer = 0

    def mover(self, edificios, ancho_mapa, alto_mapa):
        velocidad = 2
        dx, dy = 0, 0

        if self.direccion == "arriba":
            dy = -velocidad
        elif self.direccion == "abajo":
            dy = velocidad
        elif self.direccion == "izquierda":
            dx = -velocidad
        elif self.direccion == "derecha":
            dx = velocidad

        nuevo_rect = self.rect.move(dx, dy)

        # Limites del mapa
        if nuevo_rect.left < 0 or nuevo_rect.right > ancho_mapa or \
           nuevo_rect.top < 0 or nuevo_rect.bottom > alto_mapa:
            return

        for edificio in edificios:
            if nuevo_rect.colliderect(edificio):
                return

        self.px += dx
        self.py += dy
        self.rect.topleft = (self.px, self.py)

    def actualizar_animacion(self, dt):
        self.anim_timer += dt
        if self.anim_timer > 0.2:
            self.frame_actual = (self.frame_actual + 1) % 4
            self.imagen = self.sprites[self.direccion][self.frame_actual]
            self.anim_timer = 0

    def dibujar(self, pantalla, camera):
        screen_x, screen_y = camera.apply((self.px, self.py))
        pantalla.blit(self.imagen, (screen_x, screen_y))
