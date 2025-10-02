import pygame

class Repartidor:
    """
    Repartidor con resistencia y clima:
    - Se recupera +5/s estando quieto
    - Se recupera +10/s si está en parque
    - Consume resistencia al moverse según base + peso + clima
    - Si resistencia llega a 0, se mueve muy lento (Exhausto)
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

        self.vel_base = 3.0  # velocidad base en px/frame
        self.resistencia = 100.0
        self.peso_total = 0.0
        self.reputacion = 70.0

    def mover(self, teclas, dt, clima, tam_tile, mult_superficie,colliders, en_parque=False):

        # Calcula multiplicadores
        mult_peso = max(0.8, 1.0 - 0.03 * self.peso_total)
        mult_reputacion = 1.05 if getattr(self, "reputacion", 0) >= 90 else 1.0

        # Determinar velocidad según resistencia
        if self.resistencia > 30:
            vel_mult = 1.0  # Normal
        elif 10 < self.resistencia <= 30:
            vel_mult = 0.8  # Cansado
        elif 0 < self.resistencia <= 10:
            vel_mult = 0.05  # Exhausto casi detenido
        else:
            vel_mult = 0.05  # También cuando resistencia = 0

        mult_clima = clima.obtener_multiplicador() if hasattr(clima, "obtener_multiplicador") else 1.0
        extra_clima = clima.obtener_extra_resistencia() if hasattr(clima, "obtener_extra_resistencia") else 0.0

        # Velocidad final en píxeles
        vel_px = self.vel_base * tam_tile * vel_mult * mult_peso * mult_reputacion * mult_clima * mult_superficie

        dx = dy = 0.0
        movio = False

        # Solo moverse si velocidad > 0
        if vel_px > 0:
            # Solo una dirección a la vez para evitar diagonales
            if teclas[pygame.K_LEFT] and self.rect.left > 0:
                dx = -vel_px * dt
                self.direccion = "izquierda"
            elif teclas[pygame.K_RIGHT] and self.rect.right < self.ancho_mapa:
                dx = vel_px * dt
                self.direccion = "derecha"
            elif teclas[pygame.K_UP] and self.rect.top > 0:
                dy = -vel_px * dt
                self.direccion = "arriba"
            elif teclas[pygame.K_DOWN] and self.rect.bottom < self.alto_mapa:
                dy = vel_px * dt
                self.direccion = "abajo"

        # Aplicar movimiento
        movio = False
        if dx != 0:
            self.rect.x += int(dx)
            # Comprobar colisión en el eje X
            if self.rect.collidelist(colliders) != -1:
                # Si hay colisión, volver a la posición anterior
                self.rect.x -= int(dx)
            else:
                movio = True

        if dy != 0:
            self.rect.y += int(dy)
            # Comprobar colisión en el eje Y
            if self.rect.collidelist(colliders) != -1:
                self.rect.y -= int(dy)
            else:
                movio = True

        # Limitar al mapa
        self.rect.left = max(0, self.rect.left)
        self.rect.right = min(self.ancho_mapa, self.rect.right)
        self.rect.top = max(0, self.rect.top)
        self.rect.bottom = min(self.alto_mapa, self.rect.bottom)

        # Actualizar resistencia
        if movio:
            celdas = (abs(dx) + abs(dy)) / float(tam_tile)
            if celdas > 0:
                consumo = 0.5
                if getattr(self, "peso_total", 0) > 3.0:
                    consumo += 0.2 * (self.peso_total - 3.0)
                consumo += extra_clima
                self.resistencia -= consumo * celdas
        else:
            recuperacion = 10.0 if en_parque else 5.0
            self.resistencia += recuperacion * dt

        # Limitar resistencia entre 0 y 100
        self.resistencia = min(100.0, max(0.0, self.resistencia))

        # Actualizar sprite
        self.imagen = self.sprites[self.direccion]
