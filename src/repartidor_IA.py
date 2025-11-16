import pygame
import random
from src.repartidor import Repartidor
from src.pedidos import Pedido
from typing import List, Optional

from src.pathfinding_A import a_star_pathfinding
from src.mapa import CityMap
from src.utilidades import encontrar_casilla_accesible_adyacente


class RepartidorIA(Repartidor):
    def __init__(self, start_tile_x, start_tile_y, tile_size, dificultad: str = "facil"):
        super().__init__(start_tile_x, start_tile_y, tile_size)
        self.dificultad = dificultad
        self.movimiento_timer = 0
        self.intervalo_movimiento_simple = 0.5

        # Estado y objetivo para media/dificil
        self.estado: str = "BUSCANDO_PEDIDO"
        self.objetivo_actual: Optional[Pedido] = None
        self.ruta_actual: List[tuple[int, int]] = []

        # Timers de decisión
        self.intervalo_decision = 1.2  # más responsiva para media
        self.decision_timer = self.intervalo_decision

        # Inicializar sprites animados (si aplica)
        self.inicializar_sprites(ruta_base="assets/player2.png")

    # ================================================================
    #              SISTEMA DE DECISIÓN PRINCIPAL
    # ================================================================
    def actualizar_logica_ia(self, dt: float, city_map: CityMap, colliders, weather,
                             pedidos_disponibles: List[Pedido], tiempo_juego: float):

        # DIFICULTAD DIFÍCIL (ya implementada)
        if self.dificultad == "dificil":
            self._ejecutar_logica_dificil(dt, city_map, weather,
                                          pedidos_disponibles, tiempo_juego, colliders)
            return

        # FÁCIL: random walk
        if self.dificultad == "facil":
            self._ejecutar_logica_simple(dt, city_map, colliders, weather)
            return

        # MEDIO: greedy best-first (elige pedidos y sigue rutas con A*)
        if self.dificultad == "medio":
            self._ejecutar_logica_media(dt, city_map, colliders, weather, pedidos_disponibles, tiempo_juego)
            return

    # ================================================================
    #                    DIFICULTAD FÁCIL
    # ================================================================
    def _ejecutar_logica_simple(self, dt, city_map, colliders, weather):
        self.movimiento_timer += dt
        if self.movimiento_timer >= self.intervalo_movimiento_simple and not self.is_moving:
            self.movimiento_timer = 0
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            self.start_move(dx, dy, city_map, colliders, weather)

    # ================================================================
    #                💠 DIFICULTAD MEDIO: GREEDY BEST-FIRST 💠
    # ================================================================
    def _ejecutar_logica_media(self, dt, city_map, colliders, weather, pedidos: List[Pedido], tiempo_juego: float):
        """
        Flujo:
         - Si ya tiene ruta (yendo a recogida/entrega) la sigue.
         - Si está BUSCANDO_PEDIDO: cada intervalo_decision evalúa pedidos y fija el mejor (greedy).
         - Si no hay pedido válido -> movimiento aleatorio ligero.
        """
        # Si ya está yendo a algo, procesar ruta igual que difícil
        if self.estado in ["YENDO_A_RECOGIDA", "YENDO_A_ENTREGA"]:
            self._procesar_movimiento_con_ruta(city_map, weather, colliders, tiempo_juego)
            return

        # Evitar decidir si está en movimiento
        if self.is_moving:
            return

        # Ciclo de decisión: elegir mejor pedido (greedy) cada intervalo
        self.decision_timer += dt
        if self.decision_timer < self.intervalo_decision:
            # no ha llegado tiempo de decidir; pequeño "idle" o movimiento mínimo
            self.movimiento_timer += dt
            if self.movimiento_timer >= 1.2 and not self.is_moving:
                self.movimiento_timer = 0
                # movimiento suave aleatorio para que no esté estático
                dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                # check básico de límites y edificios
                nx, ny = self.tile_x + dx, self.tile_y + dy
                if 0 <= nx < city_map.width and 0 <= ny < city_map.height and not city_map.tiles[ny][nx].type.blocked:
                    self.start_move(dx, dy, city_map, colliders, weather)
            return

        # Resetear timer y evaluar pedidos
        self.decision_timer = 0

        pedidos_disponibles_ahora = [p for p in pedidos if tiempo_juego >= p.release_time and p.status == "pendiente" and (getattr(p, "holder", None) in (None,))]

        mejor_pedido = self._seleccionar_pedido_greedy(pedidos_disponibles_ahora, city_map, tiempo_juego, weather)

        if mejor_pedido:
            # fijar objetivo y ruta hacia casilla accesible de pickup
            self.objetivo_actual = mejor_pedido
            casilla_recogida = encontrar_casilla_accesible_adyacente(self.objetivo_actual.pickup, city_map)
            if casilla_recogida:
                ruta = a_star_pathfinding((self.tile_x, self.tile_y), casilla_recogida, city_map)
                if ruta:
                    self.ruta_actual = ruta[1:]
                    self.estado = "YENDO_A_RECOGIDA"
                    # marcar temporalmente el pedido como "tenido" provisorio para evitar que otro lo agarre
                    # NOTE: no confirmamos hasta recoger, pero asignamos holder="cpu_pending" para competencia simple
                    try:
                        self.objetivo_actual.holder = "cpu_pending"
                    except Exception:
                        pass
                else:
                    # no ruta a la casilla de recogida: descartar y esperar siguiente ciclo
                    self.objetivo_actual = None
            else:
                # no casilla accesible, descartar
                self.objetivo_actual = None
        else:
            # no hay pedidos buenos -> comportamiento de vagabundeo leve (evita edificios)
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            nx, ny = self.tile_x + dx, self.tile_y + dy
            if 0 <= nx < city_map.width and 0 <= ny < city_map.height and not city_map.tiles[ny][nx].type.blocked:
                self.start_move(dx, dy, city_map, colliders, weather)

    def _seleccionar_pedido_greedy(self, pedidos_validos: List[Pedido], city_map: CityMap, tiempo_juego: float, weather) -> Optional[Pedido]:
        """
        Heurística greedy simple:
        score = alpha * expected_payout - beta * distance_cost - gamma * weather_penalty
        Distance cost = coste ruta (A* steps) desde mi posición a la casilla de pickup + pickup->dropoff
        """
        if not pedidos_validos:
            return None

        alpha = 1.0
        beta = 1.0
        gamma = 0.6

        mejor = None
        mejor_score = -float("inf")
        pos_actual = (self.tile_x, self.tile_y)

        for pedido in pedidos_validos:
            # encontrar casilla accesible pickup/dropoff
            casilla_recogida = encontrar_casilla_accesible_adyacente(pedido.pickup, city_map)
            casilla_entrega = encontrar_casilla_accesible_adyacente(pedido.dropoff, city_map)
            if not casilla_recogida or not casilla_entrega:
                continue

            # ruta desde yo -> recogida
            ruta1 = a_star_pathfinding(pos_actual, casilla_recogida, city_map)
            if not ruta1:
                continue
            # ruta desde recogida -> entrega
            ruta2 = a_star_pathfinding(casilla_recogida, casilla_entrega, city_map)
            if not ruta2:
                continue

            costo = (len(ruta1) - 1) + (len(ruta2) - 1)
            # penalización por clima: usar propiedad weather (asumo tiene estado_actual)
            clima_pen = 0
            estado_clima = getattr(weather, "estado_actual", None)
            if estado_clima in ("rain", "storm"):
                clima_pen = 10
            elif estado_clima == "rain_light":
                clima_pen = 4

            # expected payout: payout más prioridad bonus
            expected_payout = pedido.payout + pedido.priority * 10

            # tiempo disponible
            tiempo_estimado = tiempo_juego + costo
            tiempo_restante = pedido.deadline - tiempo_estimado
            # si está claramente fuera de deadline descartar
            if tiempo_restante < -30:
                continue

            score = alpha * expected_payout - beta * costo - gamma * clima_pen

            # small tie-breakers: prefer menos peso (más fácil) y mayor priority
            score += (pedido.priority * 2) - (pedido.weight * 0.5)

            if score > mejor_score:
                mejor_score = score
                mejor = pedido

        return mejor

    # ================================================================
    # DIFICULTAD DIFÍCIL (conservada, usa _procesar_movimiento_con_ruta)
    # ================================================================
    def _ejecutar_logica_dificil(self, dt, city_map, weather, pedidos: List[Pedido],
                                 tiempo_juego: float, colliders):

        self.decision_timer += dt
        if self.estado == "BUSCANDO_PEDIDO":
            if self.decision_timer >= self.intervalo_decision:
                print("\n--- CICLO DE DECISIÓN IA (DIFICIL) ---")
                self.decision_timer = 0
                pedidos_disponibles_ahora = [p for p in pedidos if tiempo_juego >= p.release_time]
                mejor_pedido = self._seleccionar_mejor_pedido(pedidos_disponibles_ahora, city_map, tiempo_juego)
                if mejor_pedido:
                    self.objetivo_actual = mejor_pedido
                    casilla_recogida = encontrar_casilla_accesible_adyacente(self.objetivo_actual.pickup, city_map)
                    if casilla_recogida:
                        ruta = a_star_pathfinding((self.tile_x, self.tile_y), casilla_recogida, city_map)
                        if ruta:
                            self.ruta_actual = ruta[1:]
                            self.estado = "YENDO_A_RECOGIDA"
                            print(f"IA [DIFÍCIL] objetivo {self.objetivo_actual.id} fijado.")
                        else:
                            print("IA [ERROR]: No se encontró ruta hacia recogida.")
                    else:
                        print("IA [ERROR]: No hay casilla accesible para recogida.")
        elif self.estado in ["YENDO_A_RECOGIDA", "YENDO_A_ENTREGA"]:
            self._procesar_movimiento_con_ruta(city_map, weather, colliders, tiempo_juego)

    # ================================================================
    # Procesamiento de ruta común (usado por medio y dificil)
    # ================================================================
    def _procesar_movimiento_con_ruta(self, city_map, weather, colliders, tiempo_juego):
        # Si objetivo fue tomado por otro, resetear
        if not self.objetivo_actual or (self.estado == "YENDO_A_RECOGIDA" and getattr(self.objetivo_actual, "holder", None) not in (None, "cpu_pending")):
            # liberar si lo teníamos pendiente
            if self.objetivo_actual:
                try:
                    if getattr(self.objetivo_actual, "holder", None) == "cpu_pending":
                        self.objetivo_actual.holder = None
                except Exception:
                    pass
            self._reset_estado()
            return

        # Seguir la ruta
        self._seguir_ruta(city_map, weather, colliders)

        # Si ya llegamos al final de la ruta y no estamos moviendo, intentar acciones
        if not self.ruta_actual and not self.is_moving:
            if self.estado == "YENDO_A_RECOGIDA":
                self._intentar_recoger(city_map)
            elif self.estado == "YENDO_A_ENTREGA":
                self._intentar_entregar(tiempo_juego)

    def _seguir_ruta(self, city_map, weather, colliders):
        if not self.ruta_actual or self.is_moving:
            return
        proximo_paso = self.ruta_actual[0]
        dx = proximo_paso[0] - self.tile_x
        dy = proximo_paso[1] - self.tile_y
        self.start_move(dx, dy, city_map, colliders, weather)
        if self.is_moving:
            self.ruta_actual.pop(0)

    def _reset_estado(self):
        # liberar marca pending si existe
        if self.objetivo_actual and getattr(self.objetivo_actual, "holder", None) == "cpu_pending":
            try:
                self.objetivo_actual.holder = None
            except Exception:
                pass
        self.estado = "BUSCANDO_PEDIDO"
        self.objetivo_actual = None
        self.ruta_actual = []
        self.decision_timer = 0

    # ================================================================
    # Métodos de selección/recogida/entrega (copiados y adaptados)
    # ================================================================
    def _seleccionar_mejor_pedido(self, pedidos_disponibles: List[Pedido], city_map: CityMap, tiempo_juego: float) -> Optional[Pedido]:
        # Esta función corresponde a tu versión "dificil" original (dejada igual)
        pedidos_validos = [p for p in pedidos_disponibles if p.status == "pendiente" and p.holder is None]
        if not pedidos_validos:
            return None

        mejor_pedido = None
        mejor_puntuacion = -float('inf')

        for pedido in pedidos_validos:
            pos_actual = (self.tile_x, self.tile_y)

            casilla_recogida = encontrar_casilla_accesible_adyacente(pedido.pickup, city_map)
            if not casilla_recogida:
                continue

            ruta_recogida = a_star_pathfinding(pos_actual, casilla_recogida, city_map)
            if not ruta_recogida:
                continue

            casilla_entrega = encontrar_casilla_accesible_adyacente(pedido.dropoff, city_map)
            if not casilla_entrega:
                continue

            ruta_entrega = a_star_pathfinding(casilla_recogida, casilla_entrega, city_map)
            if not ruta_entrega:
                continue

            costo_recogida = len(ruta_recogida) - 1
            costo_entrega = len(ruta_entrega) - 1
            costo_total = costo_recogida + costo_entrega

            tiempo_estimado_al_final = tiempo_juego + costo_total
            tiempo_restante = pedido.deadline - tiempo_estimado_al_final

            if tiempo_restante < -30:
                continue

            puntuacion = (pedido.payout + pedido.priority * 50) / (costo_total * 1.5 + pedido.weight * 5 + 1)

            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_pedido = pedido

        return mejor_pedido

    def _intentar_recoger(self, city_map: CityMap):
        if not self.objetivo_actual:
            return

        # Verificar adyacencia real respecto a pickup (nota: usamos pickup original)
        if abs(self.tile_x - self.objetivo_actual.pickup[0]) + abs(self.tile_y - self.objetivo_actual.pickup[1]) <= 1:
            if self.inventario.agregar_pedido(self.objetivo_actual):
                self.objetivo_actual.status = "en curso"
                self.objetivo_actual.holder = "cpu"

                casilla_entrega = encontrar_casilla_accesible_adyacente(self.objetivo_actual.dropoff, city_map)
                if casilla_entrega:
                    ruta_entrega = a_star_pathfinding((self.tile_x, self.tile_y), casilla_entrega, city_map)
                    if ruta_entrega:
                        self.ruta_actual = ruta_entrega[1:]
                        self.estado = "YENDO_A_ENTREGA"
                    else:
                        # no hay ruta a entrega, descartar
                        self._reset_estado()
                else:
                    self._reset_estado()
            else:
                # no pudo agregar al inventario (peso) -> reset
                self._reset_estado()
        else:
            # no está adyacente -> reset (posible que se movió otro)
            self._reset_estado()

    def _intentar_entregar(self, tiempo_juego: float):
        if not self.objetivo_actual:
            return

        if abs(self.tile_x - self.objetivo_actual.dropoff[0]) + abs(self.tile_y - self.objetivo_actual.dropoff[1]) <= 1:
            if self.inventario.entregar_pedido(self.objetivo_actual):
                self.objetivo_actual.status = "entregado"
                self._procesar_pago(tiempo_juego)
                self._reset_estado()
            else:
                self._reset_estado()
        else:
            self._reset_estado()

    def _procesar_pago(self, tiempo_juego):
        pago_base = self.objetivo_actual.payout
        tiempo_restante = self.objetivo_actual.deadline - tiempo_juego
        ventana_tiempo = self.objetivo_actual.deadline - self.objetivo_actual.release_time
        bonificacion = 0
        if ventana_tiempo > 0 and tiempo_restante > 0:
            ratio = tiempo_restante / ventana_tiempo
            if ratio >= 0.5:
                bonificacion = pago_base * 0.20
            elif ratio >= 0.2:
                bonificacion = pago_base * 0.10
        self.puntaje += int((pago_base + bonificacion) * self.obtener_multiplicador_pago())
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
        self.aplicar_reputacion(delta_rep)
