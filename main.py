import arcade
from Views.menu_principal import MenuPrincipal



WIDTH = 800
HEIGHT = 600
TITLE = "Courier Quest"

window = arcade.Window(WIDTH, HEIGHT, TITLE)

menu = MenuPrincipal() # Crea una instancia del menu principal
menu.setup() # Configura los botones del menu
window.show_view(menu) # Muestra la vista del menu principal

arcade.run() # Inicia el bucle del juego
