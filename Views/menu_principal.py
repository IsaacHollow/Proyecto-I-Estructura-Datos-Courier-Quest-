import pygame
import pygame.freetype
from src.repartidor import *
from api_client import load_city_map

# Dimensiones por defecto de la ventana
WIDTH_DEF = 800
HEIGHT_DEF = 600
# URL de donde se carga el mapa si se presiona "Jugar"
MAP_URL = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map"


class MenuPrincipal:
    def __init__(self, pantalla, ancho: int = WIDTH_DEF, alto: int = HEIGHT_DEF, onJugar=None):
        # Guardamos referencia a la pantalla de Pygame (el "canvas" donde se dibuja)
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.onJugar = onJugar  # Callback opcional cuando se presione "Jugar"

        # Colores en formato RGB (rojo, verde, azul)
        self.fondo = (18, 18, 30)        # Fondo oscuro
        self.btnNormal = (60, 120, 170)  # Color normal del boton
        self.btnHover = (90, 150, 200)   # Color cuando el mouse pasa encima
        self.txtColor = (255, 255, 255)  # Texto blanco

        # Inicializamos el sistema de fuentes de Pygame
        pygame.font.init()
        # Fuente para el titulo (grande)
        self.tituloFont = pygame.freetype.SysFont(None, 64)
        # Fuente para los botones (mas pequena)
        self.btnFont = pygame.freetype.SysFont(None, 28)

        # Aqui se guardaran los botones como una lista de diccionarios
        self.botones = []
        # Llamamos a la funcion que configura los botones
        self.configurarBotones()

    def configurarBotones(self):
        """Crea y posiciona los botones en pantalla"""
        cx = self.ancho // 2   # Centro horizontal de la ventana
        btn_w = 160            # Ancho del boton
        btn_h = 48             # Alto del boton
        sep = 22               # Espacio entre botones

        # Textos de los botones
        textos = ["Jugar", "Reglas", "Puntajes", "Salir"]
        # Funciones que se ejecutan al hacer click
        callbacks = [
            self.jugarClick,
            lambda: print("Reglas: pendiente"),
            lambda: print("Puntajes: pendiente"),
            self.salirClick
        ]

        # Calculamos la posicion vertical inicial para centrar el menu
        total_altura = len(textos) * btn_h + (len(textos) - 1) * sep
        start_y = self.alto // 2 - total_altura // 2 + btn_h // 2

        # Creamos cada boton con su rectangulo y datos
        self.botones = []
        for i, texto in enumerate(textos):
            y = start_y + i * (btn_h + sep)
            r = pygame.Rect(0, 0, btn_w, btn_h)
            r.center = (cx, y)  # Centramos el boton en (cx, y)
            self.botones.append({
                "rect": r,
                "texto": texto,
                "callback": callbacks[i],
                "hover": False  # Si el mouse esta encima o no
            })

    def manejarEvento(self, event):
        """Recibe los eventos de Pygame (teclado, mouse)"""
        # Si se hace click izquierdo con el mouse
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos  # Posicion del click
            for b in self.botones:
                if b["rect"].collidepoint(pos):  # Si el click esta dentro del boton
                    b["callback"]()  # Ejecutar la funcion asignada

        # Si se presiona la tecla ESC, cerramos la ventana
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def actualizar(self):
        """Actualiza el estado del menu (por ejemplo hover del mouse)"""
        mpos = pygame.mouse.get_pos()  # Posicion actual del mouse
        for b in self.botones:
            # Cambiamos hover segun si el mouse esta encima del boton
            b["hover"] = b["rect"].collidepoint(mpos)

    def dibujar(self):
        """Dibuja en pantalla el fondo, titulo y botones"""
        # Pintamos el fondo de la ventana
        self.pantalla.fill(self.fondo)
        # Dibujamos el titulo del juego
        self.tituloFont.render_to(
            self.pantalla,
            (self.ancho // 2 - 220, 60),
            "Courier Quest",
            self.txtColor,
            size=64
        )

        # Dibujamos los botones
        for b in self.botones:
            # Escogemos color segun hover
            color = self.btnHover if b["hover"] else self.btnNormal
            pygame.draw.rect(self.pantalla, color, b["rect"], border_radius=8)

            # Dibujamos el texto centrado dentro del boton
            text_surf, text_rect = self.btnFont.render(b["texto"], self.txtColor, size=28)
            text_rect.center = b["rect"].center
            self.pantalla.blit(text_surf, text_rect)

    def jugarClick(self):
        """Accion al presionar Jugar"""
        mapa = load_city_map(MAP_URL)
        print(f"Mapa cargado: {mapa.city_name} ({mapa.width}x{mapa.height})")
        if callable(self.onJugar):
            self.onJugar(mapa)

    def salirClick(self):
        """Accion al presionar Salir"""
        pygame.quit()
        exit()
