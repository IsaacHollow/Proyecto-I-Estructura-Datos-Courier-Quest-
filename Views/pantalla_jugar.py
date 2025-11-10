import pygame
import pygame.freetype


class PantallaModoJuego:
    def __init__(self, pantalla, ancho=800, alto=600, onJugarSolo=None, onJugarIA=None):
        self.pantalla = pantalla
        self.ancho = ancho
        self.alto = alto
        self.onJugarSolo = onJugarSolo
        self.onJugarIA = onJugarIA
        self.mostrar_dificultades = False

        pygame.font.init()
        self.font_titulo = pygame.freetype.SysFont(None, 52)
        self.font_btn = pygame.freetype.SysFont(None, 34)
        self.color_fondo = (0, 0, 0)
        self.color_btn = (0, 160, 0)
        self.color_btn_hover = (0, 200, 0)
        self.color_texto = (255, 255, 255)
        self.color_volver = (200, 40, 40)
        self.color_volver_hover = (230, 60, 60)

        self.botones_principales = self.crear_botones_principales()
        self.botones_dificultad = self.crear_botones_dificultad()

    def crear_botones_principales(self):
        w, h = 260, 60
        y_center = self.alto // 2

        btn_solo = pygame.Rect(0, 0, w, h)
        btn_solo.center = (self.ancho // 2, y_center - 50)

        btn_ia = pygame.Rect(0, 0, w, h)
        btn_ia.center = (self.ancho // 2, y_center + 50)

        return [
            {"rect": btn_solo, "texto": "Jugar Solo", "accion": "solo"},
            {"rect": btn_ia,   "texto": "Jugar vs IA", "accion": "ia"}
        ]

    def crear_botones_dificultad(self):
        w, h = 240, 55
        cx = self.ancho // 2
        start_y = self.alto // 2 - 110
        sep = 75

        btns = []
        dificultades = ["Fácil", "Medio", "Difícil"]
        acciones = ["facil", "medio", "dificil"]

        for i, txt in enumerate(dificultades):
            r = pygame.Rect(0, 0, w, h)
            r.center = (cx, start_y + i * sep)
            btns.append({"rect": r, "texto": txt, "accion": acciones[i]})

        # Botón Volver abajo a la derecha
        volver = pygame.Rect(self.ancho - 150, self.alto - 70, 130, 50)
        btns.append({"rect": volver, "texto": "Volver", "accion": "volver"})

        return btns

    def manejar_evento(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            # Pantalla inicial
            if not self.mostrar_dificultades:
                for b in self.botones_principales:
                    if b["rect"].collidepoint(pos):
                        if b["accion"] == "solo":
                            if callable(self.onJugarSolo):
                                self.onJugarSolo()
                        elif b["accion"] == "ia":
                            self.mostrar_dificultades = True

            else:
                for b in self.botones_dificultad:
                    if b["rect"].collidepoint(pos):
                        if b["accion"] == "volver":
                            self.mostrar_dificultades = False
                        else:
                            # Llamar al juego con la dificultad seleccionada
                            if callable(self.onJugarIA):
                                self.onJugarIA(b["accion"])

    def dibujar(self):
        self.pantalla.fill(self.color_fondo)

        if not self.mostrar_dificultades:
            for b in self.botones_principales:
                self.dibujar_boton(b["rect"], b["texto"])
        else:
            self.font_titulo.render_to(self.pantalla, (self.ancho//2 - 140, 80),
                                       "Selecciona dificultad", self.color_texto)

            for b in self.botones_dificultad:
                if b["accion"] == "volver":
                    self.dibujar_boton(b["rect"], b["texto"], rojo=True)
                else:
                    self.dibujar_boton(b["rect"], b["texto"])

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
