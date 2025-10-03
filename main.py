import pygame
from Views.pantalla_victoria import PantallaVictoria
from Views.pantalla_derrota import PantallaDerrota
from Views.menu_principal import MenuPrincipal
from Views.juego import JuegoView
from Views.pantalla_creditos import PantallaCreditos
from Views.pantalla_reglas import PantallaReglas
from Views.pantalla_puntaje import PantallaPuntaje
from api_client import load_city_map, load_pedidos

WIDTH = 800
HEIGHT = 600
TITLE = "Courier Quest"
MAP_URL = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/map"
PEDIDOS_URL = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/jobs"

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

WHITE = (255, 255, 255)
font = pygame.font.Font(None, 36)

current_view = None
paused = False

def reproducir_musica(ruta):
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.play(-1)

def irAJuego(parametro, **kwargs):
    global current_view
    pedidos = load_pedidos(PEDIDOS_URL)

    if not isinstance(parametro, str):
        current_view = JuegoView(screen, parametro, pedidos, onJugar=irAJuego)
        reproducir_musica("assets/music/game_theme.mp3")
        return

    if parametro == "creditos":
        current_view = PantallaCreditos(screen, WIDTH, HEIGHT, onVolver=volverAlMenu)
    elif parametro == "reglas":
        current_view = PantallaReglas(screen, WIDTH, HEIGHT, onVolver=volverAlMenu)
    elif parametro == "puntajes":
        current_view = PantallaPuntaje(screen, WIDTH, HEIGHT, onVolver=volverAlMenu)
    elif parametro == "victoria":
        puntaje = kwargs.get("puntaje", 0)
        current_view = PantallaVictoria(screen, puntaje=puntaje, onJugar=irAJuego)
    elif parametro == "derrota":
        puntaje = kwargs.get("puntaje", 0)
        current_view = PantallaDerrota(screen, puntaje=puntaje, onJugar=irAJuego)
    elif parametro == "menu":
        current_view = MenuPrincipal(screen, WIDTH, HEIGHT, onJugar=irAJuego)
        reproducir_musica("assets/music/menu_theme.mp3")
    elif parametro == "jugar":
        mapa = load_city_map(MAP_URL)
        current_view = JuegoView(screen, mapa, pedidos, onJugar=irAJuego)
        reproducir_musica("assets/music/game_theme.mp3")
    else:
        current_view = JuegoView(screen, parametro, pedidos, onJugar=irAJuego)
        reproducir_musica("assets/music/game_theme.mp3")

def volverAlMenu():
    global current_view
    current_view = MenuPrincipal(screen, WIDTH, HEIGHT, onJugar=irAJuego)
    reproducir_musica("assets/music/menu_theme.mp3")

volverAlMenu()

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and isinstance(current_view, JuegoView):
                paused = not paused
                if paused:
                    reproducir_musica("assets/music/paused.wav")
                else:
                    reproducir_musica("assets/music/game_theme.mp3")
            elif event.key == pygame.K_p:
                volverAlMenu()
                paused = False

        if current_view is not None:
            current_view.manejarEvento(event)

    if paused:
        screen.fill((0, 0, 0))
        w, h = screen.get_size()
        pause_text = font.render("JUEGO PAUSADO - Presione ESC para continuar", True, WHITE)
        pause_text2 = font.render("Presione \"P\" para salir al menú", True, WHITE)
        pause_text3 = font.render("Al salir el progreso no se guarda", True, WHITE)

        rect1 = pause_text.get_rect(center=(w//2, h//2 - 30))
        rect2 = pause_text2.get_rect(center=(w//2, h//2 + 10))
        rect3 = pause_text3.get_rect(center=(w//2, h//2 + 50))

        screen.blit(pause_text, rect1)
        screen.blit(pause_text2, rect2)
        screen.blit(pause_text3, rect3)

        pygame.display.flip()
        clock.tick(60)
        continue

    if current_view is not None:
        current_view.actualizar()
        current_view.dibujar()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
