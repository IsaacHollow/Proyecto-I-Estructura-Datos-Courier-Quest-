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
MAP_URL = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map"


class MenuPrincipal:
    def __init__(self, pantalla, ancho=WIDTH_DEF, alto=HEIGHT_DEF, onJugarModo=None, onAccion=None):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.onJugarModo = onJugarModo
        self.onAccion = onAccion

        self.save_manager = SaveManager()

        self.fondo = (18, 18, 30)
        self.btnNormal = (60, 120, 170)
        self.btnHover = (90, 150, 200)
        self.txtColor = (255, 255, 255)

        pygame.font.init()
        self.tituloFont = pygame.freetype.SysFont(None, 64)
        self.btnFont = pygame.freetype.SysFont(None, 28)

        self.botones = []
        self.configurarBotones()

    def configurarBotones(self):
        cx = self.ancho // 2
        btn_w = 160
        btn_h = 48
        sep = 22

        textos = ["Jugar", "Cargar Partida", "Reglas", "Puntajes", "Creditos", "Salir"]
        callbacks = [
            self.jugarClick,
            self.cargarClick,
            self.reglasClick,
            self.puntajeclick,
            self.creditosClick,
            self.salirClick
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
                "hover": False,
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
        mpos = pygame.mouse.get_pos()
        for b in self.botones:
            b["hover"] = b["rect"].collidepoint(mpos)

    def dibujar(self):
        self.pantalla.fill(self.fondo)
        self.tituloFont.render_to(self.pantalla, (self.ancho // 2 - 220, 60), "Courier Quest", self.txtColor, size=64)

        for b in self.botones:
            color = (40, 40, 50) if b.get("deshabilitado") else (self.btnHover if b["hover"] else self.btnNormal)
            pygame.draw.rect(self.pantalla, color, b["rect"], border_radius=8)
            tx_color = (100, 100, 100) if b.get("deshabilitado") else self.txtColor
            surf, rect = self.btnFont.render(b["texto"], tx_color, size=28)
            rect.center = b["rect"].center
            self.pantalla.blit(surf, rect)


    def jugarClick(self):
        pygame.mixer.music.stop()
        if callable(self.onJugarModo):

            self.onJugarModo()

    def cargarClick(self):
        estado = self.save_manager.cargar_partida(1)
        if estado and callable(self.onAccion):
            pygame.mixer.music.stop()
            self.onAccion("cargar_juego", estado_cargado=estado)

    def creditosClick(self):
        if callable(self.onAccion):
            self.onAccion("creditos")

    def reglasClick(self):
        if callable(self.onAccion):
            self.onAccion("reglas")

    def puntajeclick(self):
        if callable(self.onAccion):
            self.onAccion("puntajes")

    def salirClick(self):
        pygame.quit()
        exit()
