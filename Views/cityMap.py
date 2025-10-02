import pygame
from src.camera import Camera
from src.repartidor import Repartidor
from src.weather import Clima

TILE_WIDTH = 50
TILE_HEIGHT = 50
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

class CityMapView:
    def __init__(self, pantalla, city_map, onJugar):
        self.pantalla = pantalla
        self.city_map = city_map
        self.onJugar = onJugar
        self.repartidor = Repartidor(self.city_map.width * TILE_WIDTH,
                                     self.city_map.height * TILE_HEIGHT)

        self.weather = Clima()  # usamos Clima

        # Diccionario de sprites con nombres en español
        self.sprites = {
            "calle": pygame.image.load("assets/street.png").convert_alpha(),
            "parque": pygame.image.load("assets/park.png").convert_alpha(),
            "edificio": pygame.image.load("assets/building.png").convert_alpha(),
        }

        # Instancia la cámara
        self.camera = Camera(self.pantalla,
                             city_map.width * TILE_WIDTH,
                             city_map.height * TILE_HEIGHT)

        # Escala sprites de calles y parques
        self.sprites["calle"] = pygame.transform.scale(self.sprites["calle"], (TILE_WIDTH, TILE_HEIGHT))
        self.sprites["parque"] = pygame.transform.scale(self.sprites["parque"], (TILE_WIDTH, TILE_HEIGHT))
        # edificio se escala al dibujar grupos

        # Calcula grupos de edificios
        self.building_groups = self.detect_building_groups()

        # Fuente para mostrar clima
        self.font = pygame.font.Font(None, 24)

    def manejarEvento(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:  # Simular victoria
                pygame.mixer.music.stop()
                self.onJugar("victoria", puntaje=0)
            elif event.key == pygame.K_s:  # Simular derrota
                pygame.mixer.music.stop()
                self.onJugar("derrota", puntaje=0)

    def detect_building_groups(self):
        """Detecta grupos de tiles contiguos tipo 'edificio'"""
        visited = [[False for _ in range(self.city_map.width)] for _ in range(self.city_map.height)]
        groups = []
        tiles = self.city_map.tiles

        for y in range(self.city_map.height):
            for x in range(self.city_map.width):
                if tiles[y][x].type.name == "edificio" and not visited[y][x]:
                    queue = [(x, y)]
                    visited[y][x] = True
                    min_x, max_x = x, x
                    min_y, max_y = y, y
                    while queue:
                        cx, cy = queue.pop(0)
                        min_x = min(min_x, cx)
                        max_x = max(max_x, cx)
                        min_y = min(min_y, cy)
                        max_y = max(max_y, cy)
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            nx, ny = cx+dx, cy+dy
                            if 0 <= nx < self.city_map.width and 0 <= ny < self.city_map.height:
                                if tiles[ny][nx].type.name == "edificio" and not visited[ny][nx]:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))
                    groups.append((min_x, min_y, max_x, max_y))
        return groups

    def dibujar(self, offset_x=10, offset_y=10):
        # Dibuja calles y parques
        for y, row in enumerate(self.city_map.tiles):
            for x, tile in enumerate(row):
                if tile.type.name != "edificio":
                    sprite = self.sprites[tile.type.name]
                    px = x * TILE_WIDTH
                    py = y * TILE_HEIGHT
                    screen_x, screen_y = self.camera.apply((px, py))
                    self.pantalla.blit(sprite, (screen_x, screen_y))

        # Dibuja grupos de edificios
        building_sprite = self.sprites["edificio"]
        for min_x, min_y, max_x, max_y in self.building_groups:
            width = (max_x - min_x + 1) * TILE_WIDTH
            height = (max_y - min_y + 1) * TILE_HEIGHT
            sprite_scaled = pygame.transform.scale(building_sprite, (width, height))
            px = min_x * TILE_WIDTH
            py = min_y * TILE_HEIGHT
            screen_x, screen_y = self.camera.apply((px, py))
            self.pantalla.blit(sprite_scaled, (screen_x, screen_y))

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
        texto_clima = f"Clima: {estado_clima} ({int(intensidad*100)}%)"
        text_surface = self.font.render(texto_clima, True, WHITE)
        self.pantalla.blit(text_surface, (offset_x, offset_y + 15))

    def actualizar(self):
        teclas = pygame.key.get_pressed()
        dt = 1 / 60  # asumiendo 60 FPS

        # Actualizar clima
        self.weather.actualizar(dt)

        # Revisar si el repartidor está en parque
        en_parque = False
        tile_x = self.repartidor.rect.centerx // TILE_WIDTH
        tile_y = self.repartidor.rect.centery // TILE_HEIGHT
        if 0 <= tile_x < self.city_map.width and 0 <= tile_y < self.city_map.height:
            tile = self.city_map.tiles[tile_y][tile_x]
            if tile.type.name == "parque":
                en_parque = True

        # Actualizar repartidor
        self.repartidor.actualizar(teclas, dt, self.weather, TILE_WIDTH, 1.0, en_parque)

        # Centrar cámara
        self.camera.center_on(self.repartidor.rect)
