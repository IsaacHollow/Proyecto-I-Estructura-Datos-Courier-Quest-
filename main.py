import pygame
import requests
import json
from api_client import load_city_map, load_clima, load_pedidos
from Views.menu_principal import MenuPrincipal
from Views.cityMap import CityMapView

weather = load_clima("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/weather?city=TigerCity&mode=seed")
pedidos = load_pedidos("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/jobs")

#print(f"Mapa cargado: {city_map.city_name} ({city_map.width}x{city_map.height})")
print(weather.city, weather.condition, weather.intensity)
print(f"Se cargaron {len(pedidos)} pedidos")
for p in pedidos:
    print(f"{p.id} -> pickup {p.pickup}, dropoff {p.dropoff}, payout {p.payout}")

WIDTH = 800
HEIGHT = 600
TITLE = "Courier Quest"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Esta variable controlará la vista actual
current_view = None

def irAJuego(mapa):
    global current_view
    current_view = CityMapView(screen,mapa)


menu = MenuPrincipal(screen, onJugar=irAJuego)
current_view = menu  # aquí controlamos qué pantalla se muestra


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        current_view.manejarEvento(event)

    current_view.actualizar()

    current_view.dibujar()
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
