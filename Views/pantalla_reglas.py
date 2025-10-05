import pygame
import pygame.freetype

class PantallaReglas:
    def __init__(self, pantalla, ancho, alto, onVolver=None):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.onVolver = onVolver

        pygame.font.init()
        self.tituloFont = pygame.freetype.SysFont(None, 25)
        self.textoFont = pygame.freetype.SysFont(None, 18)

        self.fondo = (18, 18, 30)
        self.btnNormal = (60, 120, 170)
        self.btnHover = (90, 150, 200)
        self.txtColor = (255, 255, 255)

        # Líneas de texto
        self.lineas = [
            "Objetivo:",
            "  - Entregar todos los paquetes a tiempo y ganar puntos.",
            "Cómo jugar:",
            "  - Usa Flechas o WASD para mover al repartidor.",
            "  - Recoge paquetes que aparecen en el mapa.",
            "  - Presiona Ctrl para ver tu inventario y seleccionar pedidos.",
            "  - Llega al destino marcado para entregar el paquete.",
            "Puntaje:",
            "  - Cada entrega exitosa otorga puntos.",
            "  - Entregar rápido otorga bonus de tiempo.",
            "  - Demorarse reduce puntos.",
        ]

        cx, cy = self.ancho // 2 + 300, self.alto - 50
        self.boton_volver = {
            "rect": pygame.Rect(0, 0, 100, 50),
            "texto": "Volver",
            "hover": False
        }
        self.boton_volver["rect"].center = (cx, cy)

    def manejarEvento(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if callable(self.onVolver):
                self.onVolver()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            if self.boton_volver["rect"].collidepoint(pos):
                if callable(self.onVolver):
                    self.onVolver()

    def actualizar(self, dt=0):
        mpos = pygame.mouse.get_pos()
        self.boton_volver["hover"] = self.boton_volver["rect"].collidepoint(mpos)

    def dibujar(self):
        self.pantalla.fill(self.fondo)
        # Título
        self.tituloFont.render_to(
            self.pantalla,
            (self.ancho // 2 - 80, 50),
            "Reglas",
            self.txtColor
        )
        # Texto
        y = 150
        for linea in self.lineas:
            self.textoFont.render_to(
                self.pantalla,
                (self.ancho // 2 - 150, y),
                linea,
                self.txtColor
            )
            y += 32

        # Dibujar botón Volver
        color = self.btnHover if self.boton_volver["hover"] else self.btnNormal
        pygame.draw.rect(self.pantalla, color, self.boton_volver["rect"], border_radius=8)
        text_surf, text_rect = self.textoFont.render(self.boton_volver["texto"], self.txtColor, size=28)
        text_rect.center = self.boton_volver["rect"].center
        self.pantalla.blit(text_surf, text_rect)
