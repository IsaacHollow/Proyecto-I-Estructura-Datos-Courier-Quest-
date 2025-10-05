import pygame
import pygame.freetype
from src.puntajes import ScoreManager 


class PantallaPuntaje:
    def __init__(self, pantalla, ancho, alto, onVolver=None):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.onVolver = onVolver

        pygame.font.init()
        self.tituloFont = pygame.freetype.SysFont(None, 40)
        self.textoFont = pygame.freetype.SysFont(None, 28)

        self.fondo = (18, 18, 30)
        self.btnNormal = (60, 120, 170)
        self.btnHover = (90, 150, 200)
        self.txtColor = (255, 255, 255)
        self.txtSecundario = (180, 180, 180)

        #Cargar puntajes
        self.score_manager = ScoreManager()
        self.actualizar_puntajes()

        # Botón volver
        cx, cy = self.ancho // 2, self.alto - 60
        self.boton_volver = {
            "rect": pygame.Rect(0, 0, 120, 45),
            "texto": "Volver",
            "hover": False
        }
        self.boton_volver["rect"].center = (cx, cy)


    def actualizar_puntajes(self):

        scores = self.score_manager.obtener_top(10)
        if not scores:
            self.lineas = ["Nada... aún"]
        else:
            self.lineas = []
            for i, entry in enumerate(scores, start=1):
                fecha = entry.get("fecha", "??")
                resultado = entry.get("resultado", "—")
                puntaje = entry.get("puntaje", 0)
                linea = f"{i:2d}.  {resultado.upper():<8}  |  Puntaje: {puntaje:4d}  |  {fecha}"
                self.lineas.append(linea)


    def manejarEvento(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if callable(self.onVolver):
                self.onVolver()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.boton_volver["rect"].collidepoint(event.pos):
                if callable(self.onVolver):
                    self.onVolver()


    def actualizar(self, dt=0):
        mpos = pygame.mouse.get_pos()
        self.boton_volver["hover"] = self.boton_volver["rect"].collidepoint(mpos)


    def dibujar(self):
        self.pantalla.fill(self.fondo)

        # Título
        titulo = "Puntajes Más Altos"
        text_rect = self.tituloFont.get_rect(titulo, size=40)
        text_rect.center = (self.ancho // 2, 60)
        self.tituloFont.render_to(self.pantalla, text_rect.topleft, titulo, self.txtColor, size=40)

        # Tabla de puntajes 
        margen_x = self.ancho // 2 - 360
        y = 150
        for linea in self.lineas:
            self.textoFont.render_to(
                self.pantalla,
                (margen_x, y),
                linea,
                self.txtColor
            )
            y += 35

        # Botón volver
        color = self.btnHover if self.boton_volver["hover"] else self.btnNormal
        pygame.draw.rect(self.pantalla, color, self.boton_volver["rect"], border_radius=8)
        text_surf, text_rect = self.textoFont.render(self.boton_volver["texto"], self.txtColor, size=26)
        text_rect.center = self.boton_volver["rect"].center
        self.pantalla.blit(text_surf, text_rect)