import pygame

class PantallaDerrota:
    def __init__(self, pantalla, puntaje, onJugar):
        self.pantalla = pantalla
        self.puntaje = puntaje
        self.onJugar = onJugar

        self.font = pygame.font.SysFont(None, 52)
        self.btnFont = pygame.font.SysFont(None, 30)
        self.btnColor = (200, 60, 60)
        self.btnHover = (230, 90, 90)
        self.txtColor = (255, 255, 255)

        self.title_font = pygame.font.SysFont(None, 72)
        self.score_font = pygame.font.SysFont(None, 40)

        self.btn_w = 220
        self.btn_h = 52
        self.sep = 18
        self.botones = [
            {"rect": pygame.Rect(0, 0, self.btn_w, self.btn_h), "texto": "Volver a jugar", "accion": lambda: self.onJugar("jugar"), "hover": False},
            {"rect": pygame.Rect(0, 0, self.btn_w, self.btn_h), "texto": "Salir al menú", "accion": lambda: self.onJugar("menu"), "hover": False},
        ]

        pygame.mixer.music.load("assets/music/Perder2.wav")
        pygame.mixer.music.play(-1)

        self.colocar_botones()

    def colocar_botones(self):
        w, h = self.pantalla.get_size()
        margin_right = 40
        margin_bottom = 40

        total_h = len(self.botones) * self.btn_h + (len(self.botones) - 1) * self.sep
        start_y = h - margin_bottom - total_h
        x = w - margin_right - self.btn_w

        for i, b in enumerate(self.botones):
            y = start_y + i * (self.btn_h + self.sep)
            b["rect"].topleft = (x, y)

    def manejarEvento(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.onJugar("jugar")
            elif event.key == pygame.K_ESCAPE:
                self.onJugar("menu")

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self.botones:
                if b["rect"].collidepoint(event.pos):
                    b["accion"]()

    def actualizar(self):
        self.colocar_botones()
        mpos = pygame.mouse.get_pos()
        for b in self.botones:
            b["hover"] = b["rect"].collidepoint(mpos)

    def dibujar(self):
        self.pantalla.fill((20, 8, 10))
        w, h = self.pantalla.get_size()

        titulo_surf = self.title_font.render("¡Perdiste!", True, (255, 130, 80))
        puntaje_surf = self.score_font.render(f"Puntaje: {self.puntaje}", True, (255, 200, 160))

        gap = 24
        titulo_rect = titulo_surf.get_rect(center=(w // 2, h // 3))
        puntaje_rect = puntaje_surf.get_rect(midtop=(w // 2, titulo_rect.bottom + gap))

        self.pantalla.blit(titulo_surf, titulo_rect)
        self.pantalla.blit(puntaje_surf, puntaje_rect)

        for b in self.botones:
            color = self.btnHover if b["hover"] else self.btnColor
            pygame.draw.rect(self.pantalla, color, b["rect"], border_radius=8)
            txt_surf = self.btnFont.render(b["texto"], True, self.txtColor)
            txt_rect = txt_surf.get_rect(center=b["rect"].center)
            self.pantalla.blit(txt_surf, txt_rect)
