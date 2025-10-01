import pygame

from src.camera import Camera
from src.repartidor import Repartidor

TILE_WIDTH = 50
TILE_HEIGHT = 50

class CityMapView:
    def __init__(self, pantalla, city_map):

        self.pantalla = pantalla
        self.city_map = city_map
        self.repartidor = Repartidor(self.city_map.width * TILE_WIDTH, self.city_map.height * TILE_HEIGHT)

        self.sprites = {
            "street": pygame.image.load("assets/street.png").convert_alpha(),
            "park": pygame.image.load("assets/park.png").convert_alpha(),
            "building": pygame.image.load("assets/building.png").convert_alpha(),
        }
        # Instancia la camara
        self.camera = Camera(self.pantalla, city_map.width * TILE_WIDTH, city_map.height * TILE_HEIGHT)

        # Escala los sprites de calle y parque
        self.sprites["street"] = pygame.transform.scale(self.sprites["street"], (TILE_WIDTH, TILE_HEIGHT))
        self.sprites["park"] = pygame.transform.scale(self.sprites["park"], (TILE_WIDTH, TILE_HEIGHT))

        # Calcula los grupos de edificios al inicio
        self.building_groups = self.detect_building_groups()



    def detect_building_groups(self):
        """Detecta los grupos de tiles contiguos tipo 'building' y devuelve una lista de rectángulos"""
        visited = [[False for _ in range(self.city_map.width)] for _ in range(self.city_map.height)]
        groups = []
        tiles = self.city_map.tiles

        for y in range(self.city_map.height):
            for x in range(self.city_map.width):
                if tiles[y][x].type.name == "building" and not visited[y][x]:
                    # Inicia flood fill/BFS
                    queue = [(x, y)]
                    visited[y][x] = True
                    min_x, max_x = x, x
                    min_y, max_y = y, y
                    while queue:
                        cx, cy = queue.pop(0)
                        # Actualiza límites
                        min_x = min(min_x, cx)
                        max_x = max(max_x, cx)
                        min_y = min(min_y, cy)
                        max_y = max(max_y, cy)
                        # Chequea vecinos
                        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                            nx, ny = cx+dx, cy+dy
                            if 0 <= nx < self.city_map.width and 0 <= ny < self.city_map.height:
                                if tiles[ny][nx].type.name == "building" and not visited[ny][nx]:
                                    visited[ny][nx] = True
                                    queue.append((nx, ny))
                    # Guarda el rectángulo del grupo
                    groups.append((min_x, min_y, max_x, max_y))
        return groups

    def dibujar(self, offset_x=100, offset_y=0):
        # Dibuja primero calles y parques
        # Al dibujar un tile se calcula su posicion en pixeles para llamar a camera.apply
        for y, row in enumerate(self.city_map.tiles):
            for x, tile in enumerate(row):
                if tile.type.name != "building":
                    sprite = self.sprites[tile.type.name]
                    px = x * TILE_WIDTH
                    py = y * TILE_HEIGHT
                    screen_x, screen_y = self.camera.apply((px, py))
                    self.pantalla.blit(sprite, (screen_x, screen_y))

        # Dibuja cada grupo de edificio con una sola imagen escalada
        building_sprite = self.sprites["building"]
        for min_x, min_y, max_x, max_y in self.building_groups:
            width = (max_x - min_x + 1) * TILE_WIDTH
            height = (max_y - min_y + 1) * TILE_HEIGHT
            sprite_scaled = pygame.transform.scale(building_sprite, (width, height))
            px = min_x * TILE_WIDTH
            py = min_y * TILE_HEIGHT
            screen_x, screen_y = self.camera.apply((px, py))
            self.pantalla.blit(sprite_scaled, (screen_x, screen_y))


        # Para el repartidor hace lo mismo que con calles y parques:
        screen_x, screen_y = self.camera.apply(self.repartidor.rect.topleft)
        self.pantalla.blit(self.repartidor.imagen, (screen_x, screen_y))

    def manejarEvento(self, event):
        # Aquí puedes manejar eventos del mapa (teclado, mouse, etc)
        pass

    def actualizar(self):
        teclas = pygame.key.get_pressed()
        self.repartidor.mover(teclas)
        self.camera.center_on(self.repartidor.rect)
