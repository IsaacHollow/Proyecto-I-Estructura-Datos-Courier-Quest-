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
dificultad_cpu_actual = "facil"  # Valor por defecto


def reproducir_musica(ruta):
    if pygame.mixer.music.get_busy():
        pygame.mixer.music.stop()
    pygame.mixer.music.load(ruta)
    pygame.mixer.music.play(-1)


def irAJuego(parametro=None, **kwargs):
    global current_view

    if parametro == "jugar_ia":
        mapa = load_city_map(MAP_URL)
        pedidos = load_pedidos(PEDIDOS_URL, mapa.start_time) if mapa.start_time else []
        dificultad = kwargs.get("dificultad", "facil")
        current_view = JuegoView(screen, onJugar=irAJuego, city_map=mapa, pedidos_disponibles=pedidos,
                                 dificultad_cpu=dificultad)
        reproducir_musica("assets/music/game_theme.mp3")
        return

    if parametro == "cargar_juego":
        estado = kwargs.get("estado_cargado")
        dificultad = kwargs.get("dificultad", "facil")
        current_view = JuegoView(screen, onJugar=irAJuego, estado_cargado=estado, dificultad_cpu=dificultad)
        reproducir_musica("assets/music/game_theme.mp3")
        return

    if parametro == "creditos":
        current_view = PantallaCreditos(screen, WIDTH, HEIGHT, onVolver=volverAlMenu)
    elif parametro == "reglas":
        current_view = PantallaReglas(screen, WIDTH, HEIGHT, onVolver=volverAlMenu)

    elif parametro == "victoria":
        puntaje = kwargs.get("puntaje", 0)
        current_view = PantallaVictoria(
            screen,
            puntaje=puntaje,
            onJugar=irAJugarModo,
            onVolver=volverAlMenu
        )

    elif parametro == "derrota":
        puntaje = kwargs.get("puntaje", 0)
        current_view = PantallaDerrota(
            screen,
            puntaje=puntaje,
            onJugar=irAJugarModo,
            onVolver=volverAlMenu
        )


def irAJugarModo():
    reproducir_musica("assets/music/Elegir_Juego2.mp3")
    global current_view

    def jugar_con_ia(dificultad):
        global dificultad_cpu_actual
        dificultad_cpu_actual = dificultad
        irAJuego("jugar_ia", dificultad=dificultad)

    current_view = PantallaModoJuego(
        screen,
        WIDTH,
        HEIGHT,
        onJugarIA=jugar_con_ia,
        onVolver=volverAlMenu
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
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE and isinstance(current_view, JuegoView):
                paused = not paused
                reproducir_musica("assets/music/paused.wav" if paused else "assets/music/game_theme.mp3")
            elif event.key == pygame.K_p:
                volverAlMenu()
                paused = False

        # El nombre estandarizado es `manejar_evento`
        if current_view and hasattr(current_view, "manejar_evento"):
            current_view.manejar_evento(event)
        elif current_view and hasattr(current_view, "manejarEvento"):
            current_view.manejarEvento(event)

    if paused:
        screen.fill((0, 0, 0))

        pause_text = font.render("JUEGO PAUSADO - Presione ESC para continuar", True, WHITE)
        salir_text = font.render("Presione P para salir al menú", True, WHITE)

        screen.blit(pause_text, pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 20)))
        screen.blit(salir_text, salir_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20)))

        pygame.display.flip()
        continue

    if current_view:
        if hasattr(current_view, "actualizar"): current_view.actualizar(dt)
        if hasattr(current_view, "dibujar"): current_view.dibujar()

    pygame.display.flip()

pygame.quit()