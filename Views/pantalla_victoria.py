import pygame

class PantallaVictoria:
    def __init__(self, pantalla, puntaje, onJugar, onVolver=None):
        self.pantalla = pantalla
        self.puntaje = puntaje
        self.onJugar = onJugar
        self.onVolver = onVolver  # Función que vuelve al menú

        self.font = pygame.font.SysFont(None, 56)
        self.btnFont = pygame.font.SysFont(None, 30)
        self.btnColor = (60, 120, 170)
        self.btnHover = (90, 150, 200)
        self.txtColor = (255, 255, 255)

        self.title_font = pygame.font.SysFont(None, 72)
        self.score_font = pygame.font.SysFont(None, 40)

        self.btn_w = 220
        self.btn_h = 52
        self.sep = 18

        # Botones
        self.botones = [
            {"rect": pygame.Rect(0, 0, self.btn_w, self.btn_h),
             "texto": "Jugar de nuevo",
             "accion": self.onJugar,
             "hover": False},
            {"rect": pygame.Rect(0, 0, self.btn_w, self.btn_h),
             "texto": "Salir al menú",
             "accion": self.onVolver,
             "hover": False},
        ]

        pygame.mixer.music.load("assets/music/Victoria.mp3")
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
            elif event.key == pygame.K_ESCAPE and self.onVolver:
                self.onVolver()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for b in self.botones:
                if b["rect"].collidepoint(event.pos):
                    if b["accion"]:
                        b["accion"]()

    def actualizar(self, dt=0):
        self.colocar_botones()
        mpos = pygame.mouse.get_pos()
        for b in self.botones:
            b["hover"] = b["rect"].collidepoint(mpos)

    def dibujar(self):
        self.pantalla.fill((10, 10, 16))
        w, h = self.pantalla.get_size()

        titulo_surf = self.title_font.render("¡Ganaste!", True, (0, 220, 100))
        puntaje_surf = self.score_font.render(f"Puntaje: {self.puntaje}", True, (200, 255, 200))

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
