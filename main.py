import pygame

from Views.pantalla_derrota import PantallaDerrota
from Views.menu_principal import MenuPrincipal
from Views.juego import JuegoView
from Views.pantalla_creditos import PantallaCreditos
from Views.pantalla_reglas import PantallaReglas
from Views.pantalla_puntaje import PantallaPuntaje
from Views.pantalla_victoria import PantallaVictoria
from Views.pantalla_jugar import PantallaModoJuego

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


def irAJuego(parametro=None, **kwargs):
    global current_view

    if parametro is not None and not isinstance(parametro, str):
        mapa = parametro
        pedidos = load_pedidos(PEDIDOS_URL, mapa.start_time) if mapa.start_time else []
        current_view = JuegoView(screen, onJugar=irAJuego, city_map=mapa, pedidos_disponibles=pedidos)
        reproducir_musica("assets/music/game_theme.mp3")
        return

    if parametro == "cargar_juego":
        estado = kwargs.get("estado_cargado")
        current_view = JuegoView(screen, onJugar=irAJuego, estado_cargado=estado)
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

    elif parametro == "jugar":
        mapa = load_city_map(MAP_URL)
        pedidos = load_pedidos(PEDIDOS_URL, mapa.start_time) if mapa.start_time else []
        current_view = JuegoView(screen, onJugar=irAJuego, city_map=mapa, pedidos_disponibles=pedidos)
        reproducir_musica("assets/music/game_theme.mp3")


def irAJugarModo():
    reproducir_musica("assets/music/Elegir_Juego2.mp3")
    global current_view

    def jugar_solo():
        irAJuego("jugar")

    def jugar_con_ia(dificultad):
        irAJuego("jugar")

    current_view = PantallaModoJuego(
        screen,
        WIDTH,
        HEIGHT,
        onJugarSolo=jugar_solo,
        onJugarIA=jugar_con_ia
    )


def volverAlMenu():
    global current_view
    current_view = MenuPrincipal(screen, WIDTH, HEIGHT, onJugarModo=irAJugarModo, onAccion=irAJuego)
    reproducir_musica("assets/music/menu_theme.mp3")


volverAlMenu()

running = True

while running:
    dt = clock.tick(60) / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and isinstance(current_view, JuegoView):
                paused = not paused
                reproducir_musica("assets/music/paused.wav" if paused else "assets/music/game_theme.mp3")
            elif event.key == pygame.K_p:
                volverAlMenu()
                paused = False

        if current_view is not None:
            if hasattr(current_view, "manejar_evento"):
                current_view.manejar_evento(event)
            elif hasattr(current_view, "manejarEvento"):
                current_view.manejarEvento(event)

    if paused:
        screen.fill((0, 0, 0))
        pause_text = font.render("JUEGO PAUSADO - Presione ESC para continuar", True, WHITE)
        screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2)))
        pygame.display.flip()
        continue

    if current_view is not None:
        if hasattr(current_view, "actualizar"):
            current_view.actualizar(dt)
        if hasattr(current_view, "dibujar"):
            current_view.dibujar()

    pygame.display.flip()

pygame.quit()
