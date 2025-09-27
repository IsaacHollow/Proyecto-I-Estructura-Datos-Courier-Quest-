import arcade
import requests
import json
from api_client import load_city_map, load_clima, load_pedidos
from Views.menu_principal import MenuPrincipal


#AQUI SE CARGAN DATOS DEL API USANDO LOS METODOS DE  api_client.py
city_map = load_city_map("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map")
weather = load_clima("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/weather?city=TigerCity&mode=seed")
pedidos = load_pedidos("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/jobs")


#AQUI SE HACEN COMPROBACIONES PARA LOS DATOS CARGADOS (IGNORAR)
print(f"Mapa cargado: {city_map.city_name} ({city_map.width}x{city_map.height})")

print(weather.city)
print(weather.condition)
print(weather.intensity)
print(weather.conditions)
print(weather.transition["clear"])

print(f"Se cargaron {len(pedidos)} pedidos")
for p in pedidos:
    print(f"{p.id} -> pickup {p.pickup}, dropoff {p.dropoff}, payout {p.payout}")


WIDTH = 800
HEIGHT = 600
TITLE = "Courier Quest"

window = arcade.Window(WIDTH, HEIGHT, TITLE)

menu = MenuPrincipal()
menu.setup()
window.show_view(menu)

arcade.run()