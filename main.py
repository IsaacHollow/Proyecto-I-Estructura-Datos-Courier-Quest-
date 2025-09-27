import arcade
import requests
import json
from Views.menu_principal import MenuPrincipal

def jprint(obj):
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

response = requests.get("https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map")
print(response.status_code)

jprint(response.json())


WIDTH = 800
HEIGHT = 600
TITLE = "Courier Quest"

window = arcade.Window(WIDTH, HEIGHT, TITLE)

menu = MenuPrincipal()
menu.setup()
window.show_view(menu)

arcade.run()
