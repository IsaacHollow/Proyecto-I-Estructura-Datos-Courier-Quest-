import pygame
import requests
import json
from api_client import load_city_map, load_clima, load_pedidos
from Views.menu_principal import MenuPrincipal
from Views.cityMap import CityMapView

# Cargar datos desde la API
weather = load_clima("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/weather?city=TigerCity&mode=seed")
pedidos = load_pedidos("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/jobs")

print(weather.city, weather.condition, weather.intensity)
print(f"Se cargaron {len(pedidos)} pedidos")
for p in pedidos:
    print(f"{p.id} -> pickup {p.pickup}, dropoff {p.dropoff}, payout {p.payout}")

# Configuración de ventana
WIDTH = 800
HEIGHT = 600
TITLE = "Courier Quest"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Colores y fuentes
WHITE = (255, 255, 255)
font = pygame.font.Font(None, 36)

# Vista actual
current_view = None

def irAJuego(mapa):
    global current_view
    current_view = CityMapView(screen, mapa)

# Crear menú principal
menu = MenuPrincipal(screen, onJugar=irAJuego)
current_view = menu

# Bucle principal
running = True
paused = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # alterna pausa
                paused = not paused
        current_view.manejarEvento(event)

    if paused:
        screen.fill((0, 0, 0))  # fondo negro al pausar
        pause_text = font.render("JUEGO PAUSADO - Presione ESC para continuar", True, WHITE)
        text_rect = pause_text.get_rect(center=(WIDTH/2, HEIGHT/2))
        screen.blit(pause_text, text_rect)
        pygame.display.flip()
        clock.tick(60)
        continue  # no actualizar ni dibujar vista

    current_view.actualizar()
    current_view.dibujar()
    pygame.display.flip()
    clock.tick(60)

pygame.quit()




