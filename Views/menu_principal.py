import arcade
from arcade.gui import UIManager, UIFlatButton # Importa UIManager y UIFlatButton que son necesarios para los botones
from .juego import Juego  


WIDTH = 800 # Ancho 
HEIGHT = 600  # Alto

class MenuPrincipal(arcade.View):
    def __init__(self):
        super().__init__()
        self.ui_manager = UIManager # Inicializa el UIManager
        self.ui_manager.enable() # Habilita el UIManager

    def setup(self):
        # Boton Jugar
        boton_jugar = UIFlatButton(text="Jugar", width=200, height=60)
        boton_jugar.center_x = WIDTH // 2
        boton_jugar.center_y = HEIGHT // 2 + 100
        boton_jugar.on_click = self.juego

        # Boton Salir
        boton_salir = UIFlatButton(text="Salir", width=200, height=60)
        boton_salir.center_x = WIDTH // 2 - 150
        boton_salir.center_y = HEIGHT // 2 - 100
        boton_salir.on_click = self.salir_juego

        # Boton Reglas 
        boton_reglas = UIFlatButton(text="Reglas", width=200, height=60)
        boton_reglas.center_x = WIDTH // 2 - 150
        boton_reglas.center_y = HEIGHT // 2

        # Boton Creditos 
        boton_creditos = UIFlatButton(text="Creditos", width=200, height=60)
        boton_creditos.center_x = WIDTH // 2 + 150
        boton_creditos.center_y = HEIGHT // 2 - 100

        # Boton Puntajes 
        boton_puntaje = UIFlatButton(text="Puntajes", width=200, height=60)
        boton_puntaje.center_x = WIDTH // 2 + 150
        boton_puntaje.center_y = HEIGHT // 2

        # Agregar al UIManager
        self.ui_manager.add(boton_jugar)
        self.ui_manager.add(boton_salir)
        self.ui_manager.add(boton_reglas)
        self.ui_manager.add(boton_creditos)
        self.ui_manager.add(boton_puntaje)

   
    # Metodos de los botones
    def juego(self, event):
        self.window.show_view(Juego())

    def salir_juego(self, event):
        arcade.close_window()


    # Dibuja la vista
    def on_draw(self):
        self.clear()
        arcade.draw_text("Courier Quest", WIDTH // 2, HEIGHT - 100,
                         arcade.color.WHITE, 40, anchor_x="center")
        self.ui_manager.draw()
