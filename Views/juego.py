import pygame
from datetime import timedelta

from src.camera import Camera
from src.repartidor import Repartidor
from src.weather import Weather
from src.puntajes import ScoreManager
from src.estado_juego import EstadoJuego
from src.save_manager import SaveManager

from src.repartidor_IA import RepartidorIA

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
    def __init__(self, pantalla, onJugar, city_map=None, pedidos_disponibles=None, estado_cargado=None,
                 dificultad_cpu: str = "facil"):
        self.pantalla = pantalla
        self.pedidos_disponibles = pedidos_disponibles
        self.onJugar = onJugar
        self.save_manager = SaveManager()
        self.dificultad_cpu = dificultad_cpu

        if estado_cargado:
            # --- Cargar desde un estado ---
            self.city_map = estado_cargado.city_map
            self.pedidos_disponibles = estado_cargado.pedidos_actuales
            self.tiempo_juego = estado_cargado.tiempo_juego
            self.repartidor = estado_cargado.repartidor
            self.weather = estado_cargado.weather
            start_tile_x_cpu = self.city_map.width // 2 + 1
            start_tile_y_cpu = self.city_map.height // 2
            self.repartidor_ia = RepartidorIA(start_tile_x_cpu, start_tile_y_cpu, TILE_WIDTH, self.dificultad_cpu)
            self._pedidos_iniciales_sesion = estado_cargado.pedidos_iniciales
        else:
            # --- Iniciar una nueva partida ---
            if city_map is None or pedidos_disponibles is None:
                raise ValueError("Se requiere 'city_map' y 'pedidos_disponibles' para una nueva partida.")

            self.city_map = city_map
            self.pedidos_disponibles = pedidos_disponibles
            self._pedidos_iniciales_sesion = list(pedidos_disponibles)
            self.tiempo_juego = 0.0

            # Jugador Humano
            start_tile_x = self.city_map.width // 2
            start_tile_y = self.city_map.height // 2
            self.repartidor = Repartidor(start_tile_x, start_tile_y, TILE_WIDTH)

            # Jugador IA
            start_tile_x_cpu = self.city_map.width // 2 + 1
            start_tile_y_cpu = self.city_map.height // 2
            self.repartidor_ia = RepartidorIA(start_tile_x_cpu, start_tile_y_cpu, TILE_WIDTH, self.dificultad_cpu)

            self.weather = Weather()

        self.score_manager = ScoreManager()
        self.goal_income = getattr(self.city_map, "goal")
        self.time_limit = getattr(self.city_map, "max_time")
        self._fin_juego_iniciado = False

        self.mostrando_inventario = False
        self.vista_inventario = "normal"

        self.sprites = {
            "calle": pygame.image.load("assets/street.png").convert_alpha(),
            "parque": pygame.image.load("assets/park.png").convert_alpha(),
            "edificio": pygame.image.load("assets/building.png").convert_alpha(),
        }

        self.camera = Camera(self.pantalla,
                             self.city_map.width * TILE_WIDTH,
                             self.city_map.height * TILE_HEIGHT)

        for key, sprite in list(self.sprites.items()):
            self.sprites[key] = pygame.transform.scale(sprite, (TILE_WIDTH, TILE_HEIGHT))

        self.building_rects = []
        for y, row in enumerate(self.city_map.tiles):
            for x, tile in enumerate(row):
                if tile.type.blocked:
                    self.building_rects.append(pygame.Rect(x * TILE_WIDTH, y * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT))

        self.font = pygame.font.Font(None, 24)
        self.inventory_font = pygame.font.SysFont("monospace", 16)
        self.btn_font = pygame.font.Font(None, 20)

        self.botones_inventario = [
            {"texto": "Normal", "accion": "normal", "rect": pygame.Rect(0, 0, 80, 30), "hover": False},
            {"texto": "Por Prioridad", "accion": "prioridad", "rect": pygame.Rect(0, 0, 120, 30), "hover": False},
            {"texto": "Por Deadline", "accion": "deadline", "rect": pygame.Rect(0, 0, 120, 30), "hover": False},
        ]

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
            if event.key == pygame.K_F5:
                self.guardar_estado_actual(1)
                print("¡Partida guardada!")
            if event.key == pygame.K_z:
                self.intentar_interaccion()
            elif event.key in (pygame.K_LCTRL, pygame.K_RCTRL):
                self.mostrando_inventario = not self.mostrando_inventario
                if self.mostrando_inventario:
                    self.vista_inventario = "normal"

    def dibujar(self):
        self.pantalla.fill((0, 0, 0))
        self.camera.center_on(self.repartidor.rect)

        # Dibujar mapa
        for y, row in enumerate(self.city_map.tiles):
            for x, tile in enumerate(row):
                sprite = self.sprites.get(tile.type.name)
                if sprite:
                    px, py = x * TILE_WIDTH, y * TILE_HEIGHT
                    screen_x, screen_y = self.camera.apply((px, py))
                    self.pantalla.blit(sprite, (screen_x, screen_y))

        # Dibujar pedidos
        for pedido in self.pedidos_disponibles:
            if self.tiempo_juego < pedido.release_time:
                continue
            if not hasattr(pedido, "imagen") or pedido.imagen is None:
                pedido.cargar_sprite((PEDIDO_SIZE, PEDIDO_SIZE))

            offset_paquete = (TILE_WIDTH - PEDIDO_SIZE) // 2
            holder = getattr(pedido, 'holder', None)

            if pedido.status == "pendiente" and holder is None:
                px = pedido.pickup[0] * TILE_WIDTH + offset_paquete
                py = pedido.pickup[1] * TILE_HEIGHT + offset_paquete
                sx, sy = self.camera.apply((px, py))
                self.pantalla.blit(pedido.imagen, (sx, sy))
            elif pedido.status == "en curso":
                if holder == 'human' and self.repartidor.inventario.actual() == pedido:
                    px = pedido.dropoff[0] * TILE_WIDTH + offset_paquete
                    py = pedido.dropoff[1] * TILE_HEIGHT + offset_paquete
                    sx, sy = self.camera.apply((px, py))
                    self.pantalla.blit(pedido.imagen, (sx, sy))

        # Dibujar repartidores
        for repartidor_obj in [self.repartidor, self.repartidor_ia]:
            if repartidor_obj.imagen:
                sx, sy = self.camera.apply(repartidor_obj.rect.topleft)
                self.pantalla.blit(repartidor_obj.imagen, (sx, sy))

        self.dibujar_ui()

        if self.mostrando_inventario:
            self.dibujar_inventario_overlay()

    def dibujar_ui(self):
        offset_x = 10
        offset_y = 10
        screen_w, _ = self.pantalla.get_size()

        # --- UI Jugador Humano ---
        barra_ancho, barra_alto = 100, 10
        res_ratio_h = self.repartidor.resistencia / 100
        pygame.draw.rect(self.pantalla, RED, (offset_x, offset_y, barra_ancho, barra_alto))
        pygame.draw.rect(self.pantalla, GREEN, (offset_x, offset_y, barra_ancho * res_ratio_h, barra_alto))
        self.pantalla.blit(self.font.render(f"Jugador", True, WHITE), (offset_x, offset_y + 15))

        rep_ratio_h = self.repartidor.reputacion / 100
        bar_x_h = screen_w - barra_ancho - 20
        pygame.draw.rect(self.pantalla, (80, 80, 80), (bar_x_h, offset_y, barra_ancho, barra_alto))
        pygame.draw.rect(self.pantalla, YELLOW, (bar_x_h, offset_y, barra_ancho * rep_ratio_h, barra_alto))
        self.pantalla.blit(self.font.render(f"Rep: {int(self.repartidor.reputacion)}", True, WHITE),
                           (bar_x_h, offset_y + 15))

        # --- UI Jugador CPU ---
        y_cpu = offset_y + 50
        res_ratio_c = self.repartidor_ia.resistencia / 100
        pygame.draw.rect(self.pantalla, RED, (offset_x, y_cpu, barra_ancho, barra_alto))
        pygame.draw.rect(self.pantalla, BLUE, (offset_x, y_cpu, barra_ancho * res_ratio_c, barra_alto))
        self.pantalla.blit(self.font.render(f"CPU ({self.dificultad_cpu})", True, WHITE), (offset_x, y_cpu + 15))

        rep_ratio_c = self.repartidor_ia.reputacion / 100
        bar_x_c = screen_w - barra_ancho - 20
        pygame.draw.rect(self.pantalla, (80, 80, 80), (bar_x_c, y_cpu, barra_ancho, barra_alto))
        pygame.draw.rect(self.pantalla, (120, 180, 255), (bar_x_c, y_cpu, barra_ancho * rep_ratio_c, barra_alto))
        self.pantalla.blit(self.font.render(f"Rep: {int(self.repartidor_ia.reputacion)}", True, WHITE),
                           (bar_x_c, y_cpu + 15))

        # Puntajes
        self.pantalla.blit(self.font.render(f"Ganancia J: {self.repartidor.puntaje}", True, YELLOW),
                           (offset_x, offset_y + 95))
        self.pantalla.blit(self.font.render(f"Ganancia C: {self.repartidor_ia.puntaje}", True, (150, 200, 255)),
                           (offset_x, offset_y + 120))

        # Info General
        tiempo_restante = max(0, self.time_limit - self.tiempo_juego)
        minutos, segundos = divmod(int(tiempo_restante), 60)
        self.pantalla.blit(self.font.render(f"Tiempo: {minutos:02d}:{segundos:02d}", True, WHITE),
                           (screen_w / 2 - 70, 10))
        self.pantalla.blit(self.font.render(f"Meta: {self.goal_income}", True, YELLOW), (screen_w / 2 - 70, 35))

        estado_clima, _ = self.weather.obtener_estado_y_intensidad()
        self.pantalla.blit(self.font.render(f"Clima: {estado_clima}", True, WHITE), (screen_w / 2 - 70, 60))

        # Indicaciones
        self.pantalla.blit(self.font.render("Ctrl: Inventario | Z: Interactuar | F5: Guardar", True, WHITE),
                           (10, self.pantalla.get_height() - 30))

        self.dibujar_overlay_clima()

    def dibujar_overlay_clima(self):
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
            overlay = pygame.Surface(self.pantalla.get_size(), pygame.SRCALPHA)
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
        ayuda_surf = self.font.render("Usa w/s para navegar", True, YELLOW)
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
                color_texto = GREEN if tiempo_restante > 60 else YELLOW if tiempo_restante > 30 else RED
                seconds = int(tiempo_restante)
                sign = "-" if seconds < 0 else ""
                seconds = abs(seconds)
                m, s = divmod(seconds, 60)
                h, m = divmod(m, 60)
                deadline_str = f"{sign}{h}:{m:02d}:{s:02d}" if h > 0 else f"{sign}{m:02d}:{s:02d}"
                release_str = str(timedelta(seconds=int(pedido.release_time)))
                datos_fila = {"ID": pedido.id, "Prio": str(pedido.priority), "Peso": f"{pedido.weight:.2f}",
                              "Deadline": deadline_str, "Release": release_str}
                for texto_col, offset_x in columnas.items():
                    self.pantalla.blit(self.inventory_font.render(datos_fila[texto_col], True, color_texto),
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

            holder = getattr(pedido, 'holder', None)

            # Recoger pedido
            if pedido.status == "pendiente" and holder is None and self.estan_adyacentes(pos_repartidor, pedido.pickup):
                if self.repartidor.inventario.agregar_pedido(pedido):
                    pedido.status = "en curso"
                    pedido.holder = "human"
                    pedido.cargar_sprite((PEDIDO_SIZE, PEDIDO_SIZE))
                    print(f"Pedido {pedido.id} recogido por el jugador")
                    return
            # Entregar pedido
            elif pedido.status == "en curso" and holder == "human" and self.estan_adyacentes(pos_repartidor,
                                                                                             pedido.dropoff):
                if self.repartidor.inventario.entregar_pedido(pedido):
                    pedido.status = "entregado"
                    self.procesar_pago_y_reputacion(self.repartidor, pedido)
                    print(f"Pedido {pedido.id} entregado por el jugador")
                    return

    def procesar_pago_y_reputacion(self, repartidor_obj, pedido):
        pago_base = pedido.payout
        tiempo_restante = pedido.deadline - self.tiempo_juego
        ventana_tiempo = pedido.deadline - pedido.release_time

        bonificacion = 0
        if ventana_tiempo > 0 and tiempo_restante > 0:
            ratio = tiempo_restante / ventana_tiempo
            if ratio >= 0.5:
                bonificacion = pago_base * 0.20
            elif ratio >= 0.2:
                bonificacion = pago_base * 0.10

        pago_final = (pago_base + bonificacion) * repartidor_obj.obtener_multiplicador_pago()
        repartidor_obj.puntaje += int(pago_final)

        delta_rep = 0
        if ventana_tiempo > 0 and tiempo_restante >= 0.2 * ventana_tiempo:
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

        baja_critica = repartidor_obj.aplicar_reputacion(delta_rep)

        if repartidor_obj is self.repartidor:
            if baja_critica and not self._fin_juego_iniciado:
                self._fin_juego_iniciado = True
                self.onJugar("derrota", puntaje=self.repartidor.puntaje)
            elif self.repartidor.puntaje >= self.goal_income and not self._fin_juego_iniciado:
                self._fin_juego_iniciado = True
                self.onJugar("victoria", puntaje=self.repartidor.puntaje)

    def actualizar(self, dt):
        self.tiempo_juego += dt
        self.weather.actualizar(dt)

        if self.mostrando_inventario:
            mpos = pygame.mouse.get_pos()
            for boton in self.botones_inventario:
                boton["hover"] = boton["rect"].collidepoint(mpos)
        else:
            keys = pygame.key.get_pressed()
            if not self.repartidor.is_moving:
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.repartidor.start_move(-1, 0, self.city_map, self.building_rects, self.weather)
                elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.repartidor.start_move(1, 0, self.city_map, self.building_rects, self.weather)
                elif keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.repartidor.start_move(0, -1, self.city_map, self.building_rects, self.weather)
                elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.repartidor.start_move(0, 1, self.city_map, self.building_rects, self.weather)

        # Lógica y actualización del repartidor IA
        self.repartidor_ia.actualizar_logica_ia(
            dt,
            self.city_map,
            self.building_rects,
            self.weather,
            self.pedidos_disponibles,
            self.tiempo_juego
        )
        tile_ia = self.city_map.tiles[self.repartidor_ia.tile_y][self.repartidor_ia.tile_x]
        en_parque_ia = tile_ia.type.name == "parque"
        self.repartidor_ia.update(dt, self.weather, en_parque_ia)

        # Actualización del repartidor humano
        tile_humano = self.city_map.tiles[self.repartidor.tile_y][self.repartidor.tile_x]
        en_parque_humano = tile_humano.type.name == "parque"
        self.repartidor.update(dt, self.weather, en_parque_humano)

        self.comprobar_fin_juego()

    def comprobar_fin_juego(self):
        if self._fin_juego_iniciado: return

        partida_terminada = False
        if self.time_limit > 0 and self.tiempo_juego > self.time_limit:
            partida_terminada = True
        elif self.repartidor.reputacion < 20:
            partida_terminada = True
        elif all(p.status == "entregado" for p in self.pedidos_disponibles):
            partida_terminada = True

        if partida_terminada:
            self._fin_juego_iniciado = True
            pygame.mixer.music.stop()
            puntaje_final = self.calcular_puntaje_final()

            if puntaje_final >= self.goal_income:
                self.score_manager.agregar_puntaje(puntaje_final, "victoria")
                self.onJugar("victoria", puntaje=puntaje_final)
            else:
                self.score_manager.agregar_puntaje(puntaje_final, "derrota")
                self.onJugar("derrota", puntaje=puntaje_final)

    def calcular_puntaje_final(self):
        score_base = self.repartidor.puntaje
        pay_mult = self.repartidor.obtener_multiplicador_pago()
        score_con_bonus_rep = score_base * pay_mult
        score_final = score_con_bonus_rep
        if self.time_limit > 0 and self.tiempo_juego < (self.time_limit * 0.8):
            score_final += score_con_bonus_rep * 0.10
        if self.repartidor.reputacion < 50:
            reputacion_factor = max(0.5, self.repartidor.reputacion / 100)
            score_final *= reputacion_factor
        return int(score_final)

    def guardar_estado_actual(self, slot: int):
        estado = EstadoJuego(
            city_map=self.city_map,
            pedidos_iniciales=self._pedidos_iniciales_sesion,
            tiempo_juego=self.tiempo_juego,
            repartidor=self.repartidor,
            pedidos_actuales=self.pedidos_disponibles,
            weather=self.weather
        )
        self.save_manager.guardar_partida(estado, slot)