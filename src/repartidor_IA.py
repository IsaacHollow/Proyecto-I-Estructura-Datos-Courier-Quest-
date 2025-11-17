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
        self.estado: str = "BUSCANDO_PEDIDO"
        self.objetivo_actual: Optional[Pedido] = None
        self.ruta_actual: List[tuple[int, int]] = []
        self.intervalo_decision = 2.5
        self.decision_timer = self.intervalo_decision
        self.inicializar_sprites(ruta_base="assets/player2.png")

    def actualizar_logica_ia(self, dt: float, city_map: CityMap, colliders, weather,
                             pedidos_disponibles: List[Pedido], tiempo_juego: float):

        if self.dificultad == "dificil":
            self._ejecutar_logica_dificil(dt, city_map, weather,
                                          pedidos_disponibles, tiempo_juego, colliders)
            return

        if self.dificultad == "facil":
            self._ejecutar_logica_simple(dt, city_map, colliders, weather, pedidos_disponibles, tiempo_juego)
            return

        if self.dificultad == "medio":
            self._ejecutar_logica_media(dt, city_map, colliders, weather, pedidos_disponibles, tiempo_juego)
            return

    def _ejecutar_logica_simple(self, dt, city_map, colliders, weather, pedidos: List[Pedido], tiempo_juego: float):
        self.decision_timer += dt
        self.movimiento_timer += dt

        # Intenta interactuar si está cerca
        if not self.is_moving and self.objetivo_actual:
            if self.estado == "YENDO_A_RECOGIDA":
                if abs(self.tile_x - self.objetivo_actual.pickup[0]) + abs(
                        self.tile_y - self.objetivo_actual.pickup[1]) <= 1:
                    self._intentar_recoger(city_map)
            elif self.estado == "YENDO_A_ENTREGA":
                if abs(self.tile_x - self.objetivo_actual.dropoff[0]) + abs(
                        self.tile_y - self.objetivo_actual.dropoff[1]) <= 1:
                    self._intentar_entregar(tiempo_juego)

        if self.movimiento_timer >= self.intervalo_movimiento_simple and not self.is_moving:
            self.movimiento_timer = 0

            # Si no tiene un objetivo, o si se ha "aburrido" de perseguirlo, busca uno nuevo.
            if self.estado == "BUSCANDO_PEDIDO" or (
                    self.objetivo_actual and self.decision_timer > 20):  # Re-evalúa cada 20 segundos
                self.decision_timer = 0
                # Busca un pedido al azar solo si no está ya en camino a entregar algo
                if self.estado != "YENDO_A_ENTREGA":
                    pedidos_disponibles_ahora = [p for p in pedidos if
                                                 p.status == "pendiente" and p.holder is None and tiempo_juego >= p.release_time]
                    if pedidos_disponibles_ahora:
                        self.objetivo_actual = random.choice(pedidos_disponibles_ahora)
                        self.estado = "YENDO_A_RECOGIDA"
                    else:  # Si no hay pedidos, resetea
                        self._reset_estado()

            # Moverse hacia el objetivo o de forma aleatoria
            if self.objetivo_actual:
                target_pos = self.objetivo_actual.pickup if self.estado == "YENDO_A_RECOGIDA" else self.objetivo_actual.dropoff

                dx = target_pos[0] - self.tile_x
                dy = target_pos[1] - self.tile_y

                # Movimiento errático: prioriza la dirección correcta pero puede desviarse
                possible_moves = []
                if dx > 0: possible_moves.extend([(1, 0)] * 8)
                if dx < 0: possible_moves.extend([(-1, 0)] * 8)
                if dy > 0: possible_moves.extend([(0, 1)] * 8)
                if dy < 0: possible_moves.extend([(0, -1)] * 8)

                # Añadir movimientos laterales para simular error o aleatoriedad
                if dx != 0:
                    possible_moves.extend([(0, 1), (0, -1)])
                if dy != 0:
                    possible_moves.extend([(1, 0), (-1, 0)])

                if not possible_moves:
                    possible_moves = [(0, 1), (0, -1), (1, 0), (-1, 0)]

                move = random.choice(possible_moves)
                self.start_move(move[0], move[1], city_map, colliders, weather)

            else:  # Si no hay objetivo, movimiento 100% aleatorio
                dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                self.start_move(dx, dy, city_map, colliders, weather)

    # DIFICULTAD MEDIA
    def _ejecutar_logica_media(self, dt, city_map, colliders, weather, pedidos: List[Pedido], tiempo_juego: float):

        if self.estado in ["YENDO_A_RECOGIDA", "YENDO_A_ENTREGA"]:
            self._procesar_movimiento_con_ruta(city_map, weather, colliders, tiempo_juego)
            return
        if self.is_moving:
            return

        self.decision_timer += dt
        if self.decision_timer < self.intervalo_decision:
            self.movimiento_timer += dt
            if self.movimiento_timer >= 1.2 and not self.is_moving:
                self.movimiento_timer = 0
                dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                nx, ny = self.tile_x + dx, self.tile_y + dy
                if 0 <= nx < city_map.width and 0 <= ny < city_map.height and not city_map.tiles[ny][nx].type.blocked:
                    self.start_move(dx, dy, city_map, colliders, weather)
            return

        self.decision_timer = 0
        pedidos_disponibles_ahora = [p for p in pedidos if
                                     tiempo_juego >= p.release_time and p.status == "pendiente" and (
                                                 getattr(p, "holder", None) in (None,))]
        mejor_pedido = self._seleccionar_pedido_greedy(pedidos_disponibles_ahora, city_map, tiempo_juego, weather)
        if mejor_pedido:
            self.objetivo_actual = mejor_pedido
            casilla_recogida = encontrar_casilla_accesible_adyacente(self.objetivo_actual.pickup, city_map)
            if casilla_recogida:
                ruta = a_star_pathfinding((self.tile_x, self.tile_y), casilla_recogida, city_map)
                if ruta:
                    self.ruta_actual = ruta[1:]
                    self.estado = "YENDO_A_RECOGIDA"
                else:
                    self.objetivo_actual = None
            else:
                self.objetivo_actual = None
        else:
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            nx, ny = self.tile_x + dx, self.tile_y + dy
            if 0 <= nx < city_map.width and 0 <= ny < city_map.height and not city_map.tiles[ny][nx].type.blocked:
                self.start_move(dx, dy, city_map, colliders, weather)

    def _seleccionar_pedido_greedy(self, pedidos_validos: List[Pedido], city_map: CityMap, tiempo_juego: float,
                                   weather) -> Optional[Pedido]:

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

            ruta1 = a_star_pathfinding(pos_actual, casilla_recogida, city_map)
            if not ruta1:
                continue
            ruta2 = a_star_pathfinding(casilla_recogida, casilla_entrega, city_map)
            if not ruta2:
                continue

            costo = (len(ruta1) - 1) + (len(ruta2) - 1)
            clima_pen = 0
            estado_clima = getattr(weather, "estado_actual", None)
            if estado_clima in ("rain", "storm"):
                clima_pen = 10
            elif estado_clima == "rain_light":
                clima_pen = 4

            expected_payout = pedido.payout + pedido.priority * 10

            tiempo_estimado = tiempo_juego + costo
            tiempo_restante = pedido.deadline - tiempo_estimado
            if tiempo_restante < -30:
                continue

            score = alpha * expected_payout - beta * costo - gamma * clima_pen
            score += (pedido.priority * 2) - (pedido.weight * 0.5)

            if score > mejor_score:
                mejor_score = score
                mejor = pedido

        return mejor

    # DIFICULTAD DIFICIL

    def _ejecutar_logica_dificil(self, dt, city_map, weather, pedidos: List[Pedido],
                                 tiempo_juego: float, colliders):
        self.decision_timer += dt

        if self.estado == "BUSCANDO_PEDIDO":
            # Si no está en movimiento, puede tomar una decisión
            if not self.is_moving:
                # Cada cierto tiempo, intenta buscar un nuevo pedido
                if self.decision_timer >= self.intervalo_decision:
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
                                # Inicia el movimiento inmediatamente si encuentra ruta
                                self._seguir_ruta(city_map, weather, colliders)
                        return  # Termina el ciclo de decisión

                # Si no encontró pedido o no es tiempo de decidir, se mueve aleatoriamente
                dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                self.start_move(dx, dy, city_map, colliders, weather)

        elif self.estado in ["YENDO_A_RECOGIDA", "YENDO_A_ENTREGA"]:
            self._procesar_movimiento_con_ruta(city_map, weather, colliders, tiempo_juego)

    # Procesamiento de ruta comun

    def _procesar_movimiento_con_ruta(self, city_map, weather, colliders, tiempo_juego):
        # Si objetivo fue tomado por otro, resetear
        if not self.objetivo_actual or (
                self.estado == "YENDO_A_RECOGIDA" and getattr(self.objetivo_actual, "holder", None) not in (None,
                                                                                                            "cpu_pending")):
            # liberar si lo teníamos pendiente
            if self.objetivo_actual:
                try:
                    if getattr(self.objetivo_actual, "holder", None) == "cpu_pending":
                        self.objetivo_actual.holder = None
                except Exception:
                    pass
            self._reset_estado()
            return

        self._seguir_ruta(city_map, weather, colliders)
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
        if self.objetivo_actual and getattr(self.objetivo_actual, "holder", None) == "cpu_pending":
            try:
                self.objetivo_actual.holder = None
            except Exception:
                pass
        self.estado = "BUSCANDO_PEDIDO"
        self.objetivo_actual = None
        self.ruta_actual = []
        self.decision_timer = 0

    def _seleccionar_mejor_pedido(self, pedidos_disponibles: List[Pedido], city_map: CityMap, tiempo_juego: float) -> \
    Optional[Pedido]:
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
            self._reset_estado()
            return

        if abs(self.tile_x - self.objetivo_actual.pickup[0]) + abs(self.tile_y - self.objetivo_actual.pickup[1]) <= 1:
            if self.inventario.agregar_pedido(self.objetivo_actual):
                self.objetivo_actual.status = "en curso"
                self.objetivo_actual.holder = "cpu"

                self.estado = "YENDO_A_ENTREGA"
                self.decision_timer = 0

                if self.dificultad in ["medio", "dificil"]:
                    casilla_entrega = encontrar_casilla_accesible_adyacente(self.objetivo_actual.dropoff, city_map)
                    if casilla_entrega:
                        ruta_entrega = a_star_pathfinding((self.tile_x, self.tile_y), casilla_entrega, city_map)
                        if ruta_entrega:
                            self.ruta_actual = ruta_entrega[1:]
                        else:
                            self._reset_estado()
                    else:
                        self._reset_estado()
            else:  # No pudo agregarlo al inventario (ej. por peso)
                self._reset_estado()
        else:
            self._reset_estado()

    def _intentar_entregar(self, tiempo_juego: float):
        if not self.objetivo_actual:
            self._reset_estado()
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