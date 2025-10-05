import pygame
import pygame.freetype
from src.repartidor import *
from api_client import load_city_map
from Views.pantalla_creditos import PantallaCreditos
from Views.pantalla_reglas import PantallaReglas
from Views.pantalla_puntaje import PantallaPuntaje
from src.save_manager import SaveManager

WIDTH_DEF = 800
HEIGHT_DEF = 600
# URL de donde se carga el mapa si se presiona "Jugar"
MAP_URL = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map"


class MenuPrincipal:
    def __init__(self, pantalla, ancho: int = WIDTH_DEF, alto: int = HEIGHT_DEF, onJugar=None):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.onJugar = onJugar  # Callback opcional cuando se presione "Jugar"
        self.save_manager = SaveManager()

        # Colores en formato RGB (rojo, verde, azul)
        self.fondo = (18, 18, 30)        # Fondo oscuro
        self.btnNormal = (60, 120, 170)  # Color normal del boton
        self.btnHover = (90, 150, 200)   # Color cuando el mouse pasa encima
        self.txtColor = (255, 255, 255)  # Texto blanco

        # Inicializamos el sistema de fuentes de Pygame
        pygame.font.init()

        self.tituloFont = pygame.freetype.SysFont(None, 64)

        self.btnFont = pygame.freetype.SysFont(None, 28)


        self.botones = []

        self.configurarBotones()

    def configurarBotones(self):
        cx = self.ancho // 2   # Centro horizontal de la ventana
        btn_w = 160            # Ancho del boton
        btn_h = 48             # Alto del boton
        sep = 22               # Espacio entre botones

        # Textos de los botones
        textos = ["Jugar","Cargar Partida", "Reglas", "Puntajes", "Creditos","Salir",]
        # Funciones que se ejecutan al hacer click
        callbacks = [
            self.jugarClick,
            self.cargarClick,
            self.reglasclick,
            self.puntajeclick,
            self.creditosClick,
            self.salirClick,
        ]


        total_altura = len(textos) * btn_h + (len(textos) - 1) * sep
        start_y = self.alto // 2 - total_altura // 2 + btn_h // 2 + 30

        self.botones = []
        for i, texto in enumerate(textos):
            y = start_y + i * (btn_h + sep)
            r = pygame.Rect(0, 0, btn_w, btn_h)
            r.center = (cx, y)

            deshabilitado = (texto == "Cargar Partida" and not self.save_manager.existe_guardado(1))

            self.botones.append({
                "rect": r,
                "texto": texto,
                "callback": callbacks[i],
                "hover": False, # Si el mouse esta encima o no
                "deshabilitado": deshabilitado
            })

    def manejarEvento(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for b in self.botones:
                if b["rect"].collidepoint(pos) and not b.get("deshabilitado"):
                    b["callback"]()


        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def actualizar(self, *args, **kwargs):
        mpos = pygame.mouse.get_pos()  # Posicion actual del mouse
        for b in self.botones:
            # Cambiamos hover segun si el mouse esta encima del boton
            b["hover"] = b["rect"].collidepoint(mpos)

    def dibujar(self):
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
            #Cambia el color si el boton está deshabilitado
            if b.get("deshabilitado"):
                color = (40, 40, 50)  # Gris oscuro
            else:
                color = self.btnHover if b["hover"] else self.btnNormal

            pygame.draw.rect(self.pantalla, color, b["rect"], border_radius=8)

            # Dibujamos el texto centrado dentro del boton
            color_texto = (100, 100, 100) if b.get("deshabilitado") else self.txtColor
            text_surf, text_rect = self.btnFont.render(b["texto"], color_texto, size=28)
            text_rect.center = b["rect"].center
            self.pantalla.blit(text_surf, text_rect)

    def jugarClick(self):
        pygame.mixer.music.stop()
        mapa = load_city_map(MAP_URL)
        print(f"Mapa cargado: {mapa.city_name} ({mapa.width}x{mapa.height})")
        if callable(self.onJugar):
            self.onJugar(mapa)

    def cargarClick(self):
        estado = self.save_manager.cargar_partida(1)
        if estado and callable(self.onJugar):
            pygame.mixer.music.stop()
            self.onJugar("cargar_juego", estado_cargado=estado)

    def creditosClick(self):
            self.onJugar("creditos")

    def reglasclick(self):
            self.onJugar("reglas")

    def puntajeclick(self):
        self.onJugar("puntajes")

    def salirClick(self):
        pygame.quit()
        exit()
