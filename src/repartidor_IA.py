import pygame
import random
from src.repartidor import Repartidor
from src.pedidos import Pedido
from typing import List, Optional

from src.pathfinding_A import a_star_pathfinding


class RepartidorIA(Repartidor):
    def __init__(self, start_tile_x, start_tile_y, tile_size, dificultad: str = "facil"):
        super().__init__(start_tile_x, start_tile_y, tile_size)

        self.dificultad = dificultad
        self.movimiento_timer = 0
        self.intervalo_movimiento_simple = 0.5

        self.estado: str = "BUSCANDO_PEDIDO"
        self.objetivo_actual: Optional[Pedido] = None
        self.ruta_actual: List[tuple[int, int]] = []
        self.intervalo_decision = 2.0
        self.decision_timer = self.intervalo_decision

        self.inicializar_sprites(ruta_base="assets/player2.png")

    def actualizar_logica_ia(self, dt: float, city_map, colliders, weather, pedidos_disponibles: List[Pedido],
                             tiempo_juego: float):
        if self.dificultad in ["facil", "medio"]:
            self._ejecutar_logica_simple(dt, city_map, colliders, weather)
        elif self.dificultad == "dificil":
            self._ejecutar_logica_dificil(dt, city_map, weather, pedidos_disponibles, tiempo_juego, colliders)

    def _ejecutar_logica_simple(self, dt, city_map, colliders, weather):
        self.movimiento_timer += dt
        if self.movimiento_timer >= self.intervalo_movimiento_simple and not self.is_moving:
            self.movimiento_timer = 0
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            self.start_move(dx, dy, city_map, colliders, weather)

    def _ejecutar_logica_dificil(self, dt, city_map, weather, pedidos: List[Pedido], tiempo_juego: float, colliders):
        self.decision_timer += dt

        if self.estado == "BUSCANDO_PEDIDO":
            if self.decision_timer >= self.intervalo_decision:
                self.decision_timer = 0
                pedidos_disponibles_ahora = [p for p in pedidos if tiempo_juego >= p.release_time]
                mejor_pedido = self._seleccionar_mejor_pedido(pedidos_disponibles_ahora, city_map, tiempo_juego)

                if mejor_pedido:
                    self.objetivo_actual = mejor_pedido
                    ruta = a_star_pathfinding((self.tile_x, self.tile_y), self.objetivo_actual.pickup, city_map)
                    if ruta:
                        self.ruta_actual = ruta[1:]
                        self.estado = "YENDO_A_RECOGIDA"
                        print(f"IA [DIFÍCIL]: Nuevo objetivo: {self.objetivo_actual.id}. Ruta a recogida calculada.")

        elif self.estado == "YENDO_A_RECOGIDA":
            if not self.objetivo_actual or (
                    self.objetivo_actual.holder is not None and self.objetivo_actual.holder != 'cpu'):
                print(f"IA [DIFÍCIL]: El objetivo fue tomado o ya no es válido. Buscando nuevo pedido.")
                self._reset_estado()
                return
            self._seguir_ruta(city_map, weather, colliders)
            if not self.ruta_actual and not self.is_moving:
                self._intentar_recoger(city_map)

        elif self.estado == "YENDO_A_ENTREGA":
            if not self.objetivo_actual:
                self._reset_estado()
                return
            self._seguir_ruta(city_map, weather, colliders)
            if not self.ruta_actual and not self.is_moving:
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
        self.estado = "BUSCANDO_PEDIDO"
        self.objetivo_actual = None
        self.ruta_actual = []
        self.decision_timer = 0

    def _seleccionar_mejor_pedido(self, pedidos_disponibles: List[Pedido], city_map, tiempo_juego: float) -> Optional[
        Pedido]:
        pedidos_validos = [p for p in pedidos_disponibles if p.status == "pendiente" and p.holder is None]
        print(f"IA [DIAGNÓSTICO]: Encontrados {len(pedidos_validos)} pedidos válidos para evaluar.")
        if not pedidos_validos:
            return None

        mejor_pedido = None
        mejor_puntuacion = -float('inf')

        for pedido in pedidos_validos:
            pos_actual = (self.tile_x, self.tile_y)
            ruta_recogida = a_star_pathfinding(pos_actual, pedido.pickup, city_map)
            if not ruta_recogida:
                continue

            ruta_entrega = a_star_pathfinding(pedido.pickup, pedido.dropoff, city_map)
            if not ruta_entrega:
                continue

            costo_recogida = len(ruta_recogida)
            costo_entrega = len(ruta_entrega)
            costo_total = costo_recogida + costo_entrega


            tiempo_restante = pedido.deadline - (tiempo_juego + costo_total)
            if tiempo_restante < -30:
                continue

            puntuacion = (pedido.payout + pedido.priority * 50) / (costo_total * 1.5 + pedido.weight * 5 + 1)
            print(f"IA [DIAGNÓSTICO]: Pedido {pedido.id}: Puntuación = {puntuacion:.2f} (Costo: {costo_total})")

            if puntuacion > mejor_puntuacion:
                mejor_puntuacion = puntuacion
                mejor_pedido = pedido

        if mejor_pedido:
            print(
                f"IA [DIFÍCIL]: Se ha decidido ir por el pedido {mejor_pedido.id} con una puntuación de {mejor_puntuacion:.2f}.")
        else:
            print("IA [DIFÍCIL]: No se ha seleccionado ningún pedido en este ciclo de decisión.")
        return mejor_pedido

    def _intentar_recoger(self, city_map):
        if not self.objetivo_actual: return
        print(f"IA [DIFÍCIL]: Ha llegado a la ubicación de recogida del pedido {self.objetivo_actual.id}.")
        if abs(self.tile_x - self.objetivo_actual.pickup[0]) + abs(self.tile_y - self.objetivo_actual.pickup[1]) <= 1:
            if self.inventario.agregar_pedido(self.objetivo_actual):
                self.objetivo_actual.status = "en curso"
                self.objetivo_actual.holder = "cpu"
                print(f"IA [DIFÍCIL]: Pedido {self.objetivo_actual.id} recogido. Calculando ruta a entrega.")
                ruta_entrega = a_star_pathfinding((self.tile_x, self.tile_y), self.objetivo_actual.dropoff, city_map)
                if ruta_entrega:
                    self.ruta_actual = ruta_entrega[1:]
                    self.estado = "YENDO_A_ENTREGA"
                else:
                    print(
                        f"IA [ERROR]: No se pudo calcular la ruta de entrega para {self.objetivo_actual.id}. Reiniciando.")
                    self.inventario.entregar_pedido(self.objetivo_actual)
                    self.objetivo_actual.status = "pendiente"
                    self.objetivo_actual.holder = None
                    self._reset_estado()
            else:
                print(
                    f"IA [ADVERTENCIA]: No se pudo recoger {self.objetivo_actual.id} por falta de capacidad. Reiniciando.")
                self._reset_estado()
        else:
            print("IA [ADVERTENCIA]: Llegó a la zona de recogida pero no está adyacente. Recalculando.")
            self._reset_estado()

    def _intentar_entregar(self, tiempo_juego: float):
        if not self.objetivo_actual: return
        print(f"IA [DIFÍCIL]: Ha llegado a la ubicación de entrega del pedido {self.objetivo_actual.id}.")
        if abs(self.tile_x - self.objetivo_actual.dropoff[0]) + abs(self.tile_y - self.objetivo_actual.dropoff[1]) <= 1:
            if self.inventario.entregar_pedido(self.objetivo_actual):
                self.objetivo_actual.status = "entregado"

                pago_base = self.objetivo_actual.payout
                tiempo_restante = self.objetivo_actual.deadline - tiempo_juego
                ventana_tiempo = self.objetivo_actual.deadline - self.objetivo_actual.release_time if self.objetivo_actual.deadline > self.objetivo_actual.release_time else 1
                bonificacion = 0
                if ventana_tiempo > 0 and tiempo_restante > 0:
                    ratio = tiempo_restante / ventana_tiempo
                    if ratio >= 0.5:
                        bonificacion = pago_base * 0.20
                    elif ratio >= 0.2:
                        bonificacion = pago_base * 0.10

                pago_final = (pago_base + bonificacion) * self.obtener_multiplicador_pago()
                self.puntaje += int(pago_final)

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

                print(
                    f"IA [DIFÍCIL]: Pedido {self.objetivo_actual.id} entregado. Puntaje: {self.puntaje}, Rep: {self.reputacion:.1f}")
                self._reset_estado()
            else:
                print(f"IA [ERROR]: Intentó entregar un pedido que no tenía. Reiniciando.")
                self._reset_estado()
        else:
            print("IA [ADVERTENCIA]: Llegó a la zona de entrega pero no está adyacente. Recalculando.")
            self._reset_estado()