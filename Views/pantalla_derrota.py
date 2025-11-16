import pygame
from main import volverAlMenu


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
            {"rect": pygame.Rect(0, 0, self.btn_w, self.btn_h),
             "texto": "Jugar de nuevo",
             "accion": self.onJugar,
             "hover": False},
            {"rect": pygame.Rect(0, 0, self.btn_w, self.btn_h),
             "texto": "Salir al menú",
             "accion": volverAlMenu,
             "hover": False}
        ]

        pygame.mixer.music.load("assets/music/Perder2.wav")
        pygame.mixer.music.play(-1)

        self.colocar_botones()
