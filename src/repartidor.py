import pygame


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

        # v0 (velocidad base) en celdas por segundo
        self.v0_celdas_por_seg = 3.0
        # Velocidad de animación actual en píxeles por segundo. Se calculará dinámicamente.
        self.move_speed_px_por_seg = 0

        self.sprites = {
            "arriba": pygame.image.load("assets/bicycle_up.png").convert_alpha(),
            "abajo": pygame.image.load("assets/bicycle_down.png").convert_alpha(),
            "izquierda": pygame.image.load("assets/bicycle_left.png").convert_alpha(),
            "derecha": pygame.image.load("assets/bicycle_right.png").convert_alpha()
        }
        self.direccion = "derecha"
        self.imagen = self.sprites[self.direccion]

        self.rect = self.imagen.get_rect(topleft=(self.px, self.py))

        # Atributos para la fórmula
        self.resistencia = 100.0
        self.peso_total = 0.0  # Como indicaste, se ignora por ahora (valor 0)
        self.reputacion = 70.0
        self.exhausto = False

        self.movimiento_iniciado = False

    def start_move(self, dx, dy, city_map, colliders, clima):
        """Inicia el movimiento y calcula la velocidad según la fórmula."""
        if self.is_moving or self.exhausto:
            return

        next_tile_x = self.tile_x + dx
        next_tile_y = self.tile_y + dy

        if not (0 <= next_tile_x < city_map.width and 0 <= next_tile_y < city_map.height):
            return

        next_rect_check = pygame.Rect(
            next_tile_x * self.tile_size,
            next_tile_y * self.tile_size,
            self.tile_size,
            self.tile_size
        )
        if next_rect_check.collidelist(colliders) != -1:
            return

        # --- Implementación de la Fórmula de Velocidad ---

        if self.resistencia > 30:
            m_resistencia = 1.0  # Normal
        else:
            m_resistencia = 0.8  # Cansado

        # M_rep
        m_rep = 1.03 if self.reputacion >= 90 else 1.0

        # M_peso
        m_peso = max(0.8, 1 - 0.03 * self.peso_total)

        # M_clima
        m_clima = clima.obtener_multiplicador() if hasattr(clima, "obtener_multiplicador") else 1.0

        # surface_weight (del tile actual, ya que es donde se inicia el esfuerzo)
        current_tile = city_map.tiles[self.tile_y][self.tile_x]
        surface_weight = current_tile.type.surface_weight or 1.0

        # Fórmula final (v en celdas/seg)
        v_celdas_por_seg = self.v0_celdas_por_seg * m_clima * m_peso * m_rep * m_resistencia * surface_weight

        # Si la velocidad es 0, no nos movemos
        if v_celdas_por_seg <= 0:
            return

        # Convertir a píxeles por segundo para la animación
        self.move_speed_px_por_seg = v_celdas_por_seg * self.tile_size

        # --- Fin de la Fórmula ---

        self.target_px = next_tile_x * self.tile_size
        self.target_py = next_tile_y * self.tile_size
        self.is_moving = True
        self.movimiento_iniciado = True

        if dx > 0:
            self.direccion = "derecha"
        elif dx < 0:
            self.direccion = "izquierda"
        elif dy > 0:
            self.direccion = "abajo"
        elif dy < 0:
            self.direccion = "arriba"
        self.imagen = self.sprites[self.direccion]

    def update(self, dt, clima, en_parque):
        """Actualiza la posición (animación) y la resistencia."""
        if self.is_moving:
            if self.movimiento_iniciado:
                consumo = 0.5
                if self.peso_total > 3.0:
                    consumo += 0.2 * (self.peso_total - 3.0)
                extra_clima = clima.obtener_extra_resistencia() if hasattr(clima, "obtener_extra_resistencia") else 0.0
                consumo += extra_clima
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
            else:
                self.px += (dx / distance) * move_dist
                self.py += (dy / distance) * move_dist

            self.rect.topleft = (round(self.px), round(self.py))

        else:
            recuperacion = 10.0 if en_parque else 5.0
            self.resistencia += recuperacion * dt

        if self.exhausto:
            # Si está exhausto, comprobar si ya se recuperó al 30%
            if self.resistencia >= 30:
                self.exhausto = False
        else:
            # Si no está exhausto, comprobar si se acaba de agotar
            if self.resistencia <= 0:
                self.exhausto = True

        self.resistencia = min(100.0, max(0.0, self.resistencia))