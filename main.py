import arcade
import requests
import json
from api_client import load_city_map
from Views.menu_principal import MenuPrincipal

city_map = load_city_map("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map")

print(f"Mapa cargado: {city_map.city_name} ({city_map.width}x{city_map.height})")


WIDTH = 800
HEIGHT = 600
TITLE = "Courier Quest"

window = arcade.Window(WIDTH, HEIGHT, TITLE)

menu = MenuPrincipal()
menu.setup()
window.show_view(menu)

arcade.run()