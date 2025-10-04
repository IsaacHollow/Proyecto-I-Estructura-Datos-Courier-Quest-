import pygame
from datetime import datetime, timedelta
from src.camera import Camera
from src.repartidor import Repartidor
from src.weather import weather

TILE_WIDTH = 50
TILE_HEIGHT = 50
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Nuevo tamaño para los paquetes
PEDIDO_SIZE = 25


class JuegoView:
    def __init__(self, pantalla, city_map, pedidos_disponibles, onJugar):
        self.pantalla = pantalla
        self.city_map = city_map
        self.pedidos_disponibles = pedidos_disponibles
        self.onJugar = onJugar
        self.tiempo_juego = datetime.utcnow().timestamp()

        start_tile_x = self.city_map.width // 2
        start_tile_y = self.city_map.height // 2
        self.repartidor = Repartidor(start_tile_x, start_tile_y, TILE_WIDTH)

        self.weather = weather()

        self.sprites = {
            "calle": pygame.image.load("assets/street.png").convert_alpha(),
            "parque": pygame.image.load("assets/park.png").convert_alpha(),
            "edificio": pygame.image.load("assets/building.png").convert_alpha(),
        }

        # Instancia la cámara
        self.camera = Camera(self.pantalla,
                             city_map.width * TILE_WIDTH,
                             city_map.height * TILE_HEIGHT)

        # Escala todos los sprites al tamaño del tile
        for key, sprite in self.sprites.items():
            self.sprites[key] = pygame.transform.scale(sprite, (TILE_WIDTH, TILE_HEIGHT))

        # Crear una lista de Rects para las colisiones con cada edificio
        self.building_rects = []
        for y, row in enumerate(self.city_map.tiles):
            for x, tile in enumerate(row):
                if tile.type.name == "edificio":
                    px = x * TILE_WIDTH
                    py = y * TILE_HEIGHT
                    self.building_rects.append(pygame.Rect(px, py, TILE_WIDTH, TILE_HEIGHT))

        # Fuente para mostrar clima
        self.font = pygame.font.Font(None, 24)

    def manejarEvento(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                self.intentar_interaccion()
            elif event.key == pygame.K_a:  # Simular victoria
                pygame.mixer.music.stop()
                self.onJugar("victoria", puntaje=0)
            elif event.key == pygame.K_s:  # Simular derrota
                pygame.mixer.music.stop()
                self.onJugar("derrota", puntaje=0)

    def dibujar(self, offset_x=10, offset_y=10):
        # Dibuja todos los tiles del mapa
        for y, row in enumerate(self.city_map.tiles):
            for x, tile in enumerate(row):
                sprite_name = tile.type.name
                if sprite_name in self.sprites:
                    sprite = self.sprites[sprite_name]
                    px = x * TILE_WIDTH
                    py = y * TILE_HEIGHT
                    screen_x, screen_y = self.camera.apply((px, py))
                    self.pantalla.blit(sprite, (screen_x, screen_y))

        # Dibuja pedidos en el mapa
        for pedido in self.pedidos_disponibles:
            # Solo mostrar si el release_time ha pasado
            if self.tiempo_juego < pedido.release_time:
                continue

            if not hasattr(pedido, "imagen") or pedido.imagen is None:
                pedido.cargar_sprite()

            offset_paquete = (TILE_WIDTH - PEDIDO_SIZE) // 2

            if pedido.status == "pendiente":
                px = pedido.pickup[0] * TILE_WIDTH + offset_paquete
                py = pedido.pickup[1] * TILE_HEIGHT + offset_paquete
                screen_x, screen_y = self.camera.apply((px, py))
                self.pantalla.blit(pedido.imagen, (screen_x, screen_y))
            elif pedido.status == "en curso":
                px = pedido.dropoff[0] * TILE_WIDTH + offset_paquete
                py = pedido.dropoff[1] * TILE_HEIGHT + offset_paquete
                screen_x, screen_y = self.camera.apply((px, py))
                self.pantalla.blit(pedido.imagen, (screen_x, screen_y))

        # Dibuja al repartidor
        screen_x, screen_y = self.camera.apply(self.repartidor.rect.topleft)
        self.pantalla.blit(self.repartidor.imagen, (screen_x, screen_y))

        # Dibuja barra de resistencia
        barra_ancho = 100
        barra_alto = 10
        resistencia_ratio = self.repartidor.resistencia / 100
        pygame.draw.rect(self.pantalla, RED, (offset_x, offset_y, barra_ancho, barra_alto))
        pygame.draw.rect(self.pantalla, GREEN, (offset_x, offset_y, barra_ancho * resistencia_ratio, barra_alto))

        # Dibuja texto de clima
        estado_clima, intensidad = self.weather.estado_y_intensidad()
        texto_clima = f"Clima: {estado_clima} ({int(intensidad * 100)}%)"
        text_surface = self.font.render(texto_clima, True, WHITE)
        self.pantalla.blit(text_surface, (offset_x, offset_y + 15))

        # Pantalla de pedidos si presiona CTRL
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_LCTRL] or teclas[pygame.K_RCTRL]:
            pedidos_inventario = self.repartidor.inventario.pedidos

            # Overlay fijo
            ancho_overlay = 500
            alto_overlay = 300
            x_overlay = 150
            y_overlay = 50
            padding = 10

            overlay = pygame.Surface((ancho_overlay, alto_overlay), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.pantalla.blit(overlay, (x_overlay, y_overlay))

            # Título
            y_offset = y_overlay + 10
            self.pantalla.blit(self.font.render("Pedidos en curso", True, WHITE), (x_overlay + padding, y_offset))
            pygame.draw.line(
                self.pantalla,
                WHITE,
                (x_overlay + padding, y_offset + 20),
                (x_overlay + ancho_overlay - padding, y_offset + 20),
                2
            )
            y_offset += 30

            if not pedidos_inventario:
                self.pantalla.blit(self.font.render("Inventario vacío", True, WHITE), (x_overlay + padding, y_offset))
            else:
                for pedido in pedidos_inventario:
                    # Mostrar solo pedidos que ya se liberaron
                    if self.tiempo_juego < pedido.release_time:
                        continue

                    # Convertir release_time a hora:minutos
                    release_dt = datetime.utcfromtimestamp(pedido.release_time)
                    release_str = release_dt.strftime("%H:%M")

                    # Formatear deadline solo hora:minutos
                    deadline_iso = pedido.deadline.rstrip("Z")
                    deadline_dt = datetime.strptime(deadline_iso, "%Y-%m-%dT%H:%M")
                    deadline_str = deadline_dt.strftime("%H:%M")

                    # Color según urgencia (tiempo restante hasta deadline)
                    tiempo_restante_min = (deadline_dt - datetime.utcfromtimestamp(self.tiempo_juego)).total_seconds() / 60
                    if tiempo_restante_min <= 5:
                        color = (255, 0, 0)
                    elif tiempo_restante_min <= 15:
                        color = (255, 255, 0)
                    else:
                        color = (0, 255, 0)

                    # Mostrar como columnas
                    texto = (
                        f"{pedido.id:<3} | P:{pedido.priority:<2} | W:{pedido.weight:<4} "
                        f"| {pedido.pickup}->{pedido.dropoff} | D:{deadline_str} | R:{release_str}"
                    )
                    self.pantalla.blit(self.font.render(texto, True, color), (x_overlay + padding, y_offset))
                    y_offset += 20

    def estan_adyacentes(self, pos1, pos2):
        """Comprueba si dos posiciones de tile (x, y) son adyacentes (no en diagonal)."""
        x1, y1 = pos1
        x2, y2 = pos2
        # Distancia de Manhattan
        return abs(x1 - x2) + abs(y1 - y2) == 1

    def intentar_interaccion(self):
        """Intenta recoger o entregar un pedido si el repartidor está adyacente."""
        if self.repartidor.is_moving:
            return

        pos_repartidor = (self.repartidor.tile_x, self.repartidor.tile_y)

        for pedido in self.pedidos_disponibles:
            # Intentar recoger
            if pedido.status == "pendiente" and self.estan_adyacentes(pos_repartidor, pedido.pickup):
                if self.repartidor.inventario.agregar_pedido(pedido):
                    pedido.status = "en curso"
                    pedido.cargar_sprite()
                    print(f"Pedido {pedido.id} recogido ")
                    return  # Salimos para interactuar con un solo pedido a la vez

            # Intentar entregar
            elif pedido.status == "en curso" and self.estan_adyacentes(pos_repartidor, pedido.dropoff):
                if self.repartidor.inventario.entregar_pedido(pedido):
                    pedido.status = "entregado"
                    pedido.imagen = None
                    print(f"Pedido {pedido.id} entregado ")
                    return  # Salimos para interactuar con un solo pedido a la vez

    def actualizar(self):
        dt = 1 / 60  # asumiendo 60 FPS
        self.tiempo_juego += dt

        if not self.repartidor.is_moving:
            teclas = pygame.key.get_pressed()
            # Pasamos self.weather a start_move
            if teclas[pygame.K_LEFT]:
                self.repartidor.start_move(-1, 0, self.city_map, self.building_rects, self.weather)
            elif teclas[pygame.K_RIGHT]:
                self.repartidor.start_move(1, 0, self.city_map, self.building_rects, self.weather)
            elif teclas[pygame.K_UP]:
                self.repartidor.start_move(0, -1, self.city_map, self.building_rects, self.weather)
            elif teclas[pygame.K_DOWN]:
                self.repartidor.start_move(0, 1, self.city_map, self.building_rects, self.weather)

        # Actualizar clima
        self.weather.actualizar(dt)

        # Revisar si el repartidor está en parque
        en_parque = False

        # Usamos las coordenadas de tile del repartidor
        tile_x = self.repartidor.tile_x
        tile_y = self.repartidor.tile_y
        if 0 <= tile_x < self.city_map.width and 0 <= tile_y < self.city_map.height:
            tile = self.city_map.tiles[tile_y][tile_x]
            if tile.type.name == "parque":
                en_parque = True

        # Actualizar repartidor
        self.repartidor.update(dt, self.weather, en_parque)

        # Centrar cámara
        self.camera.center_on(self.repartidor.rect)