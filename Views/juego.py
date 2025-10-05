import pygame
from datetime import timedelta

from src.camera import Camera
from src.repartidor import Repartidor
from src.weather import Weather
from src.puntajes import ScoreManager

TILE_WIDTH = 35
TILE_HEIGHT = 35
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (100, 100, 255)
YELLOW = (255, 255, 0)
BTN_COLOR = (60, 120, 170)
BTN_HOVER_COLOR = (90, 150, 200)

PEDIDO_SIZE = 20


class JuegoView:
    def __init__(self, pantalla, city_map, pedidos_disponibles, onJugar):
        self.pantalla = pantalla
        self.city_map = city_map
        self.pedidos_disponibles = pedidos_disponibles
        self.onJugar = onJugar

        self.score_manager = ScoreManager()

        # Tiempo de juego en segundos (contador ascendente)
        self.tiempo_juego = 0.0

        # Meta de puntaje y tiempo límite (si city_map proporciona valores)
        self.goal_income = getattr(self.city_map, "goal", 500)
        self.time_limit = getattr(self.city_map, "max_time", 0)
        if not self.time_limit or self.time_limit <= 0:
            self.time_limit = 300.0  # 5 minutos por defecto

        # Flag para evitar múltiples transiciones de pantalla al finalizar
        self._fin_juego_iniciado = False

        # Estados UI / juego
        self.mostrando_inventario = False
        self.vista_inventario = "normal"

        start_tile_x = self.city_map.width // 2
        start_tile_y = self.city_map.height // 2
        self.repartidor = Repartidor(start_tile_x, start_tile_y, TILE_WIDTH)

        self.weather = Weather()

        self.sprites = {
            "calle": pygame.image.load("assets/street.png").convert_alpha(),
            "parque": pygame.image.load("assets/park.png").convert_alpha(),
            "edificio": pygame.image.load("assets/building.png").convert_alpha(),
        }

        self.camera = Camera(self.pantalla,
                             city_map.width * TILE_WIDTH,
                             city_map.height * TILE_HEIGHT)

        for key, sprite in list(self.sprites.items()):
            self.sprites[key] = pygame.transform.scale(sprite, (TILE_WIDTH, TILE_HEIGHT))

        self.building_rects = []
        for y, row in enumerate(self.city_map.tiles):
            for x, tile in enumerate(row):
                if tile.type.name == "edificio":
                    px = x * TILE_WIDTH
                    py = y * TILE_HEIGHT
                    self.building_rects.append(pygame.Rect(px, py, TILE_WIDTH, TILE_HEIGHT))

        self.font = pygame.font.Font(None, 24)
        self.inventory_font = pygame.font.SysFont("monospace", 16)
        self.btn_font = pygame.font.Font(None, 20)

        self.botones_inventario = [
            {"texto": "Normal", "accion": "normal", "rect": pygame.Rect(0, 0, 80, 30), "hover": False},
            {"texto": "Por Prioridad", "accion": "prioridad", "rect": pygame.Rect(0, 0, 120, 30), "hover": False},
            {"texto": "Por Deadline", "accion": "deadline", "rect": pygame.Rect(0, 0, 120, 30), "hover": False},
        ]

        self.city_map.max_time = 105
        self.city_map.meta_puntaje = 1000

    def manejarEvento(self, event):
        if self.mostrando_inventario:
            if event.type == pygame.KEYDOWN:
                lista_ordenada = self.repartidor.inventario.obtener_vista_actual(self.vista_inventario)
                if event.key == pygame.K_w:
                    self.repartidor.inventario.anterior(lista_ordenada)
                elif event.key == pygame.K_s:
                    self.repartidor.inventario.siguiente(lista_ordenada)
                elif event.key in (pygame.K_LCTRL, pygame.K_RCTRL, pygame.K_ESCAPE):
                    self.mostrando_inventario = False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for boton in self.botones_inventario:
                    if boton["rect"].collidepoint(event.pos):
                        self.vista_inventario = boton["accion"]
                        break
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                self.intentar_interaccion()
            elif event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                self.mostrando_inventario = not self.mostrando_inventario
                if self.mostrando_inventario:
                    self.vista_inventario = "normal"

    def dibujar(self, offset_x=10, offset_y=10):
        self.pantalla.fill((0, 0, 0))
        self.camera.center_on(self.repartidor.rect)

        for y, row in enumerate(self.city_map.tiles):
            for x, tile in enumerate(row):
                sprite = self.sprites.get(tile.type.name)
                if sprite:
                    px, py = x * TILE_WIDTH, y * TILE_HEIGHT
                    screen_x, screen_y = self.camera.apply((px, py))
                    self.pantalla.blit(sprite, (screen_x, screen_y))

        for pedido in self.pedidos_disponibles:
            if self.tiempo_juego < pedido.release_time:
                continue

            if not hasattr(pedido, "imagen") or pedido.imagen is None:
                pedido.cargar_sprite((PEDIDO_SIZE, PEDIDO_SIZE))

            offset_paquete = (TILE_WIDTH - PEDIDO_SIZE) // 2
            if pedido.status == "pendiente":
                px = pedido.pickup[0] * TILE_WIDTH + offset_paquete
                py = pedido.pickup[1] * TILE_HEIGHT + offset_paquete
                screen_x, screen_y = self.camera.apply((px, py))
                self.pantalla.blit(pedido.imagen, (screen_x, screen_y))
            elif pedido.status == "en curso" and self.repartidor.inventario.actual() == pedido:
                px = pedido.dropoff[0] * TILE_WIDTH + offset_paquete
                py = pedido.dropoff[1] * TILE_HEIGHT + offset_paquete
                screen_x, screen_y = self.camera.apply((px, py))
                self.pantalla.blit(pedido.imagen, (screen_x, screen_y))

        screen_x, screen_y = self.camera.apply(self.repartidor.rect.topleft)
        self.pantalla.blit(self.repartidor.imagen, (screen_x, screen_y))

        self.dibujar_ui(offset_x, offset_y)

        if self.mostrando_inventario:
            self.dibujar_inventario_overlay()

    def dibujar_ui(self, offset_x, offset_y):
        barra_ancho = 100
        barra_alto = 10
        resistencia_ratio = self.repartidor.resistencia / 100
        pygame.draw.rect(self.pantalla, RED, (offset_x, offset_y, barra_ancho, barra_alto))
        pygame.draw.rect(self.pantalla, GREEN, (offset_x, offset_y, barra_ancho * resistencia_ratio, barra_alto))

        # Clima
        estado_clima, _ = self.weather.obtener_estado_y_intensidad()
        texto_clima = f"Clima: {estado_clima}"
        self.pantalla.blit(self.font.render(texto_clima, True, WHITE), (offset_x, offset_y + 15))

        # Puntaje
        texto_puntaje = f"Ganancia: {self.repartidor.puntaje}"
        self.pantalla.blit(self.font.render(texto_puntaje, True, YELLOW), (offset_x, offset_y + 35))

        # --- Barra de reputación ---
        rep_bar_width = 100
        rep_bar_height = 10
        screen_w, _ = self.pantalla.get_size()
        rep_ratio = self.repartidor.reputacion / 100
        bar_x = screen_w - rep_bar_width - 20
        bar_y = 20

        pygame.draw.rect(self.pantalla, (100, 100, 100), (bar_x, bar_y, rep_bar_width, rep_bar_height))
        pygame.draw.rect(self.pantalla, YELLOW, (bar_x, bar_y, rep_bar_width * rep_ratio, rep_bar_height))

        texto_rep = f"{int(self.repartidor.reputacion)}/100"
        text_surface = self.font.render(texto_rep, True, WHITE)
        text_rect = text_surface.get_rect(center=(bar_x + rep_bar_width // 2, bar_y + rep_bar_height + 12))
        self.pantalla.blit(text_surface, text_rect)

        # --- Cronómetro y meta ---
        tiempo_restante = max(0, self.city_map.max_time - self.tiempo_juego)
        minutos = int(tiempo_restante // 60)
        segundos = int(tiempo_restante % 60)
        texto_tiempo = f"Tiempo: {minutos:02d}:{segundos:02d}"

        meta_puntaje = getattr(self.city_map, "meta_puntaje", 1000)
        texto_meta = f"Meta: {meta_puntaje}"

        # Bajamos el texto para que no choque con reputación
        self.pantalla.blit(self.font.render(texto_tiempo, True, WHITE), (bar_x, bar_y + 35))
        self.pantalla.blit(self.font.render(texto_meta, True, YELLOW), (bar_x, bar_y + 55))

        # --- Texto inventario ---
        screen_w, screen_h = self.pantalla.get_size()
        texto_inv = "Presiona Ctrl para ver el inventario"
        text_surf = self.font.render(texto_inv, True, WHITE)
        text_rect = text_surf.get_rect(center=(screen_w / 2, screen_h - 20))
        self.pantalla.blit(text_surf, text_rect)

        # Ejemplo de overlay para el clima en dibujar()
        color_overlay = None

        if self.weather.estado_actual == "clear":
            color_overlay = (255, 240, 180, int(60 * self.weather.intensidad))

        elif self.weather.estado_actual == "sunny":
            color_overlay = (255, 200, 120, int(70 * self.weather.intensidad))

        elif self.weather.estado_actual == "clouds":
            color_overlay = (220, 220, 220, int(50 * self.weather.intensidad))

        elif self.weather.estado_actual == "rain_light":
            color_overlay = (150, 180, 255, int(50 * self.weather.intensidad))

        elif self.weather.estado_actual == "rain":
            color_overlay = (100, 120, 200, int(70 * self.weather.intensidad))

        elif self.weather.estado_actual == "storm":
            color_overlay = (40, 50, 90, int(100 * self.weather.intensidad))

        elif self.weather.estado_actual == "fog":
            color_overlay = (200, 200, 200, int(60 * self.weather.intensidad))

        if color_overlay:
            overlay = pygame.Surface((self.pantalla.get_width(), self.pantalla.get_height()), pygame.SRCALPHA)
            overlay.fill(color_overlay)
            self.pantalla.blit(overlay, (0, 0))

        if color_overlay:
            overlay = pygame.Surface((self.pantalla.get_width(), self.pantalla.get_height()), pygame.SRCALPHA)
            overlay.fill(color_overlay)
            self.pantalla.blit(overlay, (0, 0))


    def dibujar_inventario_overlay(self):
        overlay_w, overlay_h = 600, 400
        x_overlay = (self.pantalla.get_width() - overlay_w) // 2
        y_overlay = (self.pantalla.get_height() - overlay_h) // 2

        overlay = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
        overlay.fill((10, 20, 40, 210))
        self.pantalla.blit(overlay, (x_overlay, y_overlay))
        padding = 15

        y_offset = y_overlay + padding
        self.pantalla.blit(self.font.render("Inventario", True, WHITE), (x_overlay + padding, y_offset))
        ayuda_texto = "Usa w/s para navegar"
        ayuda_surf = self.font.render(ayuda_texto, True, YELLOW)
        self.pantalla.blit(ayuda_surf, ayuda_surf.get_rect(topright=(x_overlay + overlay_w - padding, y_offset)))
        y_offset += 30

        x_botones = x_overlay + padding
        for boton in self.botones_inventario:
            boton["rect"].topleft = (x_botones, y_offset)
            color = BTN_HOVER_COLOR if boton["hover"] else BTN_COLOR
            pygame.draw.rect(self.pantalla, color, boton["rect"], border_radius=5)
            txt_surf = self.btn_font.render(boton["texto"], True, WHITE)
            self.pantalla.blit(txt_surf, txt_surf.get_rect(center=boton["rect"].center))
            x_botones += boton["rect"].width + 10
        y_offset += 40

        columnas = {"ID": 0, "Prio": 90, "Peso": 150, "Deadline": 220, "Release": 340}
        base_x = x_overlay + padding
        for texto, offset_x in columnas.items():
            self.pantalla.blit(self.inventory_font.render(texto, True, BLUE), (base_x + offset_x, y_offset))

        pygame.draw.line(self.pantalla, WHITE, (base_x, y_offset + 20),
                         (x_overlay + overlay_w - padding, y_offset + 20), 1)
        y_offset += 25

        lista_pedidos = self.repartidor.inventario.obtener_vista_actual(self.vista_inventario)
        if not lista_pedidos:
            self.pantalla.blit(self.font.render("Inventario vacío", True, WHITE), (base_x, y_offset))
        else:
            pedido_activo = self.repartidor.inventario.actual()
            for pedido in lista_pedidos:
                if pedido == pedido_activo:
                    fila_rect = pygame.Rect(x_overlay, y_offset, overlay_w, 20)
                    pygame.draw.rect(self.pantalla, (70, 80, 110, 180), fila_rect)

                tiempo_restante = pedido.deadline - self.tiempo_juego
                color_texto = GREEN if tiempo_restante > 900 else YELLOW if tiempo_restante > 300 else RED

                seconds = int(tiempo_restante)
                sign = "-" if seconds < 0 else ""
                seconds = abs(seconds)
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                deadline_str = f"{sign}{h}:{m:02d}:{s:02d}" if h > 0 else f"{sign}{m:02d}:{s:02d}"

                release_str = str(timedelta(seconds=int(pedido.release_time)))

                datos_fila = {
                    "ID": pedido.id, "Prio": str(pedido.priority), "Peso": f"{pedido.weight:.2f}",
                    "Deadline": deadline_str, "Release": release_str
                }

                for texto_col, offset_x in columnas.items():
                    dato = datos_fila[texto_col]
                    self.pantalla.blit(self.inventory_font.render(dato, True, color_texto),
                                       (base_x + offset_x, y_offset))

                y_offset += 20

    def estan_adyacentes(self, pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    def intentar_interaccion(self):
        if self.repartidor.is_moving: return
        pos_repartidor = (self.repartidor.tile_x, self.repartidor.tile_y)

        for pedido in self.pedidos_disponibles:
            if self.tiempo_juego < pedido.release_time:
                continue

            if pedido.status == "pendiente" and self.estan_adyacentes(pos_repartidor, pedido.pickup):
                if self.repartidor.inventario.agregar_pedido(pedido):
                    pedido.status = "en curso"
                    pedido.cargar_sprite((PEDIDO_SIZE, PEDIDO_SIZE))
                    print(f"Pedido {pedido.id} recogido")
                    return

            elif pedido.status == "en curso" and self.estan_adyacentes(pos_repartidor, pedido.dropoff):
                if self.repartidor.inventario.entregar_pedido(pedido):
                    pedido.status = "entregado"
                    self.repartidor.puntaje += pedido.payout
                    tiempo_restante = pedido.deadline - self.tiempo_juego
                    delta_rep = 0
                    if tiempo_restante >= 0.2 * (pedido.deadline - pedido.release_time):
                        delta_rep = 5
                    elif tiempo_restante >= 0:
                        delta_rep = 3
                    else:
                        atraso = -tiempo_restante
                        if atraso <= 30:
                            delta_rep = -2
                        elif atraso <= 120:
                            delta_rep = -5
                        else:
                            delta_rep = -10
                    baja_critica = self.repartidor.aplicar_reputacion(delta_rep)
                    if delta_rep >= 0:
                        self.repartidor.racha_sin_penalizacion += 1
                        if self.repartidor.racha_sin_penalizacion == 3:
                            self.repartidor.aplicar_reputacion(2)
                            self.repartidor.racha_sin_penalizacion = 0
                    else:
                        self.repartidor.racha_sin_penalizacion = 0
                    if baja_critica:
                        pygame.mixer.music.stop()
                        if not self._fin_juego_iniciado:
                            self._fin_juego_iniciado = True
                            self.onJugar("derrota", puntaje=self.repartidor.puntaje)
                        return
                    # comprobar victoria inmediata al entregar
                    if self.repartidor.puntaje >= self.goal_income:
                        pygame.mixer.music.stop()
                        if not self._fin_juego_iniciado:
                            self._fin_juego_iniciado = True
                            self.onJugar("victoria", puntaje=self.repartidor.puntaje)
                        return
                    print(f"Pedido {pedido.id} entregado")
                    return

    def actualizar(self, dt):
        # Contador de tiempo de juego
        self.tiempo_juego += dt

        # Actualiza botones inventario si está abierto
        if self.mostrando_inventario:
            mpos = pygame.mouse.get_pos()
            for boton in self.botones_inventario:
                boton["hover"] = boton["rect"].collidepoint(mpos)

        # Movimiento del repartidor
        if not self.repartidor.is_moving and not self.mostrando_inventario:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.repartidor.start_move(-1, 0, self.city_map, self.building_rects, self.weather)
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.repartidor.start_move(1, 0, self.city_map, self.building_rects, self.weather)
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                self.repartidor.start_move(0, -1, self.city_map, self.building_rects, self.weather)
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.repartidor.start_move(0, 1, self.city_map, self.building_rects, self.weather)

        # Actualiza clima
        self.weather.actualizar(dt)

        # Determinar si el repartidor está en parque
        tile_actual = self.city_map.tiles[self.repartidor.tile_y][self.repartidor.tile_x]
        en_parque = tile_actual.type.name == "parque"

        # Actualiza el repartidor
        self.repartidor.update(dt, self.weather, en_parque)

        # Verifica si se terminó el juego
        self.comprobar_fin_juego()

    def comprobar_fin_juego(self):
        if self.city_map.max_time > 0 and self.tiempo_juego > self.city_map.max_time:
            puntaje_final = self.calcular_puntaje_final()
            pygame.mixer.music.stop()
            self.score_manager.agregar_puntaje(puntaje_final, "derrota")
            self.onJugar("derrota", puntaje=puntaje_final)
            return

        if self.repartidor.reputacion < 20:
            puntaje_final = self.calcular_puntaje_final()
            pygame.mixer.music.stop()
            self.score_manager.agregar_puntaje(puntaje_final, "derrota")
            self.onJugar("derrota", puntaje=puntaje_final)
            return

        if self.repartidor.puntaje >= getattr(self.city_map, "meta_puntaje", 1000):
            puntaje_final = self.calcular_puntaje_final()
            pygame.mixer.music.stop()
            self.score_manager.agregar_puntaje(puntaje_final, "victoria")
            self.onJugar("victoria", puntaje=puntaje_final)
            return

        if all(p.status == "entregado" for p in self.pedidos_disponibles):
            puntaje_final = self.calcular_puntaje_final()
            pygame.mixer.music.stop()
            self.score_manager.agregar_puntaje(puntaje_final, "victoria")
            self.onJugar("victoria", puntaje=puntaje_final)

    def calcular_puntaje_final(self):
        puntaje = 0
        for pedido in self.pedidos_disponibles:
            base = pedido.payout

            # Penalización por retraso
            tiempo_retraso = self.tiempo_juego - pedido.deadline
            if tiempo_retraso > 0:
                if tiempo_retraso <= 30:
                    penal = 0.05 * base
                elif tiempo_retraso <= 120:
                    penal = 0.10 * base
                else:
                    penal = 0.20 * base
                base -= penal

            # Bonus si se entrega antes del release_time + margen
            tiempo_antes = pedido.deadline - self.tiempo_juego
            if tiempo_antes > 0.2 * (pedido.deadline - pedido.release_time):
                bonus = 0.05 * base
                base += bonus

            puntaje += base

        # Ajustar por reputación (menos de 50 reduce puntaje)
        reputacion_factor = max(0.5, self.repartidor.reputacion / 100)
        puntaje *= reputacion_factor

        return int(puntaje)

    def calcular_puntaje(self):
        return self.repartidor.puntaje
