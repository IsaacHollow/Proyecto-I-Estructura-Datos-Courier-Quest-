# src/repartidor.py
import pygame
from src.inventario import Inventario

REPARTIDOR_ANCHO = 27
REPARTIDOR_ALTO = 27


class Repartidor:
    def __init__(self, start_tile_x, start_tile_y, tile_size):
        self.tile_x = start_tile_x
        self.tile_y = start_tile_y
        self.tile_size = tile_size

        self.px = float(start_tile_x * tile_size)
        self.py = float(start_tile_y * tile_size)

        self.is_moving = False
        self.target_px = self.px
        self.target_py = self.py

        self.v0_celdas_por_seg = 3.0
        self.move_speed_px_por_seg = 0

        self.direccion = "derecha"
        self.sprites = {}
        self.imagen = None

        # Atributos de animación
        self.anim_timer = 0.0
        self.frame_actual = 0
        self.es_animado = False

        self.inicializar_sprites()

        offset_x = (self.tile_size - REPARTIDOR_ANCHO) // 2
        offset_y = (self.tile_size - REPARTIDOR_ALTO) // 2
        self.rect = pygame.Rect(0, 0, REPARTIDOR_ANCHO, REPARTIDOR_ALTO)
        self.rect.topleft = (self.px + offset_x, self.py + offset_y)

        # Atributos de juego
        self.resistencia = 100.0
        self.reputacion = 70.0
        self.exhausto = False
        self.puntaje = 0
        self.movimiento_iniciado = False
        self.inventario = Inventario(peso_max=7.0)
        self.racha_sin_penalizacion = 0

    def inicializar_sprites(self, ruta_base="assets/bicycle_down.png"):
        self.sprites = {}
        self.es_animado = "player2" in ruta_base

        if not self.es_animado:
            sprites_orig = {
                "arriba": pygame.image.load("assets/bicycle_up.png").convert_alpha(),
                "abajo": pygame.image.load("assets/bicycle_down.png").convert_alpha(),
                "izquierda": pygame.image.load("assets/bicycle_left.png").convert_alpha(),
                "derecha": pygame.image.load("assets/bicycle_right.png").convert_alpha()
            }
            for key, sprite in sprites_orig.items():
                self.sprites[key] = pygame.transform.scale(sprite, (REPARTIDOR_ANCHO, REPARTIDOR_ALTO))
        else:
            sheet = pygame.image.load(ruta_base).convert_alpha()
            frame_w = sheet.get_width() // 4
            frame_h = sheet.get_height() // 4

            direcciones_map = ["abajo", "izquierda", "derecha", "arriba"]
            for i, dir_name in enumerate(direcciones_map):
                self.sprites[dir_name] = []
                for j in range(4):
                    rect = pygame.Rect(j * frame_w, i * frame_h, frame_w, frame_h)
                    frame = sheet.subsurface(rect)

                    frame_escalado = pygame.transform.scale(frame, (REPARTIDOR_ANCHO, REPARTIDOR_ALTO))
                    self.sprites[dir_name].append(frame_escalado)

        self.actualizar_imagen()

    def actualizar_imagen(self):
        frame_set = self.sprites.get(self.direccion)
        if not frame_set: return

        if self.es_animado:
            if self.is_moving:
                self.imagen = frame_set[self.frame_actual]
            else:
                self.imagen = frame_set[0]  # Frame estático si no se mueve
        else:
            self.imagen = frame_set

    def aplicar_reputacion(self, delta):
        self.reputacion = max(0.0, min(100.0, self.reputacion + delta))
        return self.reputacion < 20.0

    def obtener_multiplicador_pago(self):
        return 1.05 if self.reputacion >= 90.0 else 1.0

    # ===== Movimiento =====
    def start_move(self, dx, dy, city_map, colliders, clima):
        if self.is_moving or self.exhausto:
            return

        next_tile_x = self.tile_x + dx
        next_tile_y = self.tile_y + dy

        if not (0 <= next_tile_x < city_map.width and 0 <= next_tile_y < city_map.height):
            return

        next_tile_type = city_map.tiles[next_tile_y][next_tile_x].type
        if next_tile_type.blocked:
            return

        # ===== Fórmula de velocidad con clima =====
        m_resistencia = 0.8 if self.resistencia <= 30 else 1.0
        m_rep = 1.03 if self.reputacion >= 90 else 1.0
        m_peso = max(0.8, 1 - 0.03 * self.inventario.peso_total)
        m_clima = clima.obtener_multiplicador()

        current_tile = city_map.tiles[self.tile_y][self.tile_x]
        surface_weight = current_tile.type.surface_weight or 1.0

        v_celdas_por_seg = self.v0_celdas_por_seg * m_clima * m_peso * m_rep * m_resistencia * surface_weight

        if v_celdas_por_seg <= 0:
            return

        self.move_speed_px_por_seg = v_celdas_por_seg * self.tile_size
        self.target_px = next_tile_x * self.tile_size
        self.target_py = next_tile_y * self.tile_size
        self.is_moving = True
        self.movimiento_iniciado = True

        # Actualizar dirección y la imagen correspondiente
        if dx > 0:
            self.direccion = "derecha"
        elif dx < 0:
            self.direccion = "izquierda"
        elif dy > 0:
            self.direccion = "abajo"
        elif dy < 0:
            self.direccion = "arriba"
        self.actualizar_imagen()

    def update(self, dt, clima, en_parque):
        if self.es_animado and self.is_moving:
            self.anim_timer += dt
            if self.anim_timer > 0.15:
                self.anim_timer = 0
                self.frame_actual = (self.frame_actual + 1) % 4
                self.actualizar_imagen()

        if self.is_moving:
            if self.movimiento_iniciado:
                consumo = 0.5 + (0.2 * (self.inventario.peso_total - 3.0) if self.inventario.peso_total > 3.0 else 0)
                consumo += clima.obtener_extra_resistencia()
                self.resistencia -= consumo
                self.movimiento_iniciado = False

            dx = self.target_px - self.px
            dy = self.target_py - self.py
            distance = (dx ** 2 + dy ** 2) ** 0.5
            move_dist = self.move_speed_px_por_seg * dt

            if distance < move_dist:
                self.px = self.target_px
                self.py = self.target_py
                self.is_moving = False
                self.tile_x = int(self.px // self.tile_size)
                self.tile_y = int(self.py // self.tile_size)
                self.actualizar_imagen()
            else:
                self.px += (dx / distance) * move_dist
                self.py += (dy / distance) * move_dist

            offset_x = (self.tile_size - REPARTIDOR_ANCHO) // 2
            offset_y = (self.tile_size - REPARTIDOR_ALTO) // 2
            self.rect.topleft = (round(self.px) + offset_x, round(self.py) + offset_y)
        else:
            recuperacion = 10.0 if en_parque else 5.0
            self.resistencia += recuperacion * dt

        if self.exhausto and self.resistencia >= 30:
            self.exhausto = False
        elif not self.exhausto and self.resistencia <= 0:
            self.exhausto = True

        self.resistencia = min(100.0, max(0.0, self.resistencia))

    def __getstate__(self):
        state = self.__dict__.copy()
        if 'sprites' in state: del state['sprites']
        if 'imagen' in state: del state['imagen']
        if 'rect' in state: del state['rect']
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        # Determinar qué sprites cargar al recuperar el estado
        ruta = "assets/player2.png" if "ia" in self.__class__.__name__.lower() else "assets.bicycle_down.png"
        self.inicializar_sprites(ruta_base=ruta)