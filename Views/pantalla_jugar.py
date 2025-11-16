import pygame
import pygame.freetype


class PantallaModoJuego:
    def __init__(self, pantalla, ancho=800, alto=600, onJugarIA=None, onVolver=None):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.onJugarIA = onJugarIA
        self.onVolver = onVolver

        pygame.font.init()
        self.font_titulo = pygame.freetype.SysFont(None, 52)
        self.font_btn = pygame.freetype.SysFont(None, 34)
        self.color_fondo = (0, 0, 0)
        self.color_btn = (0, 160, 0)
        self.color_btn_hover = (0, 200, 0)
        self.color_texto = (255, 255, 255)
        self.color_volver = (200, 40, 40)
        self.color_volver_hover = (230, 60, 60)

        self.botones_dificultad = self.crear_botones_dificultad()

    def crear_botones_dificultad(self):
        w, h = 240, 55
        cx = self.ancho // 2
        start_y = self.alto // 2 - 110
        sep = 75

        btns = []
        dificultades = [("Fácil", "facil"), ("Medio", "medio"), ("Difícil", "dificil")]

        for i, (texto, accion) in enumerate(dificultades):
            r = pygame.Rect(0, 0, w, h)
            r.center = (cx, start_y + i * sep)
            btns.append({"rect": r, "texto": texto, "accion": accion})

        volver = pygame.Rect(self.ancho - 150, self.alto - 70, 130, 50)
        btns.append({"rect": volver, "texto": "Volver", "accion": "volver"})

        return btns

    def manejar_evento(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for b in self.botones_dificultad:
                if b["rect"].collidepoint(pos):
                    if b["accion"] == "volver":
                        if callable(self.onVolver):
                            self.onVolver()
                    else:
                        if callable(self.onJugarIA):
                            self.onJugarIA(b["accion"])

    def dibujar(self):
        self.pantalla.fill(self.color_fondo)
        self.font_titulo.render_to(self.pantalla, (self.ancho//2 - 250, 80),
                                   "Selecciona Dificultad", self.color_texto)

        for b in self.botones_dificultad:
            self.dibujar_boton(b["rect"], b["texto"], rojo=(b["accion"] == "volver"))

    def dibujar_boton(self, rect, texto, rojo=False):
        mouse = pygame.mouse.get_pos()
        hover = rect.collidepoint(mouse)

        if rojo:
            color = self.color_volver_hover if hover else self.color_volver
        else:
            color = self.color_btn_hover if hover else self.color_btn

        pygame.draw.rect(self.pantalla, color, rect, border_radius=8)
        surf, r = self.font_btn.render(texto, self.color_texto)
        r.center = rect.center
        self.pantalla.blit(surf, r)