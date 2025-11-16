import pygame
import random
from src.repartidor import Repartidor
from src.pedidos import Pedido
from typing import List, Optional

from src.pathfinding_A import a_star_pathfinding


class RepartidorIA(Repartidor):
    def __init__(self, start_tile_x, start_tile_y, tile_size, dificultad: str = "facil"):
        super().__init__(start_tile_x, start_tile_y, tile_size)

        # --- Atributos para todas las dificultades ---
        self.dificultad = dificultad
        self.movimiento_timer = 0
        self.intervalo_movimiento_simple = 0.5  # Para dificultad fácil/media

        # --- Atributos específicos para la IA Difícil ---
        self.estado: str = "BUSCANDO_PEDIDO"  # El estado actual de la IA
        self.objetivo_actual: Optional[Pedido] = None  # El pedido que está persiguiendo
        self.ruta_actual: List[tuple[int, int]] = []  # La lista de pasos a seguir
        self.intervalo_decision = 2.0  # Tiempo en segundos para reevaluar qué pedido tomar
        self.decision_timer = self.intervalo_decision

        self.inicializar_sprites(ruta_base="assets/player2.png")

    def actualizar_logica_ia(self, dt: float, city_map, colliders, weather, pedidos_disponibles: List[Pedido],
                             tiempo_juego: float):
        """
        El "cerebro" principal de la IA. Decide qué lógica ejecutar según la dificultad.
        """
        if self.dificultad in ["facil", "medio"]:
            self._ejecutar_logica_simple(dt, city_map, colliders, weather)
        elif self.dificultad == "dificil":
            self._ejecutar_logica_dificil(dt, city_map, weather, pedidos_disponibles, tiempo_juego)

    def _ejecutar_logica_simple(self, dt, city_map, colliders, weather):
        """Lógica de movimiento aleatorio para dificultades fácil y media."""
        self.movimiento_timer += dt
        if self.movimiento_timer >= self.intervalo_movimiento_simple and not self.is_moving:
            self.movimiento_timer = 0
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            self.start_move(dx, dy, city_map, colliders, weather)

    def _ejecutar_logica_dificil(self, dt, city_map, weather, pedidos: List[Pedido], tiempo_juego: float):
        """Lógica avanzada basada en A* y estados para la dificultad difícil."""

        self.decision_timer += dt

        # --- Máquina de Estados ---

        # 1. ESTADO: BUSCANDO_PEDIDO
        if self.estado == "BUSCANDO_PEDIDO":
            if self.decision_timer >= self.intervalo_decision:
                self.decision_timer = 0
                mejor_pedido = self._seleccionar_mejor_pedido(pedidos, city_map)

                if mejor_pedido:
                    self.objetivo_actual = mejor_pedido
                    # Calcular la ruta hacia el punto de recogida
                    ruta = a_star_pathfinding((self.tile_x, self.tile_y), self.objetivo_actual.pickup, city_map)
                    if ruta:
                        self.ruta_actual = ruta[1:]  # Excluimos el primer paso (posición actual)
                        self.estado = "YENDO_A_RECOGIDA"
                        print(f"IA [DIFÍCIL]: Nuevo objetivo: {self.objetivo_actual.id}. Ruta a recogida calculada.")

        # 2. ESTADO: YENDO_A_RECOGIDA
        elif self.estado == "YENDO_A_RECOGIDA":
            if self.objetivo_actual.holder is not None and self.objetivo_actual.holder != 'cpu':
                print(
                    f"IA [DIFÍCIL]: El objetivo {self.objetivo_actual.id} fue tomado por otro. Buscando nuevo pedido.")
                self._reset_estado()
                return

            self._seguir_ruta(city_map, weather, colliders=[])

            if not self.ruta_actual and not self.is_moving:
                self._intentar_recoger(city_map)

        # 3. ESTADO: YENDO_A_ENTREGA
        elif self.estado == "YENDO_A_ENTREGA":
            self._seguir_ruta(city_map, weather, colliders=[])

            if not self.ruta_actual and not self.is_moving:
                self._intentar_entregar()

    def _seguir_ruta(self, city_map, weather, colliders):
        """Mueve a la IA un paso a lo largo de la ruta actual."""
        if not self.ruta_actual or self.is_moving:
            return

        proximo_paso = self.ruta_actual[0]
        dx = proximo_paso[0] - self.tile_x
        dy = proximo_paso[1] - self.tile_y

        # Moverse al siguiente paso
        self.start_move(dx, dy, city_map, colliders, weather)
        self.ruta_actual.pop(0)

    def _reset_estado(self):
        """Resetea el estado de la IA para que vuelva a buscar un pedido."""
        self.estado = "BUSCANDO_PEDIDO"
        self.objetivo_actual = None
        self.ruta_actual = []
        self.decision_timer = 0  # Forzar una nueva decisión inmediatamente

    ### Lógica de decisión (Paso 3) - Aún por implementar ###

    def _seleccionar_mejor_pedido(self, pedidos_disponibles: List[Pedido], city_map) -> Optional[Pedido]:
        """
        Evalúa los pedidos y elige el mejor según una puntuación.
        POR AHORA, solo busca el más cercano.
        """
        pedidos_validos = [p for p in pedidos_disponibles if p.status == "pendiente" and p.holder is None]
        if not pedidos_validos:
            return None

        mejor_pedido = None
        mejor_costo = float('inf')

        for pedido in pedidos_validos:
            # Calcular el costo de la ruta para recoger el pedido
            ruta = a_star_pathfinding((self.tile_x, self.tile_y), pedido.pickup, city_map)
            if ruta:
                costo_ruta = len(ruta)
                if costo_ruta < mejor_costo:
                    mejor_costo = costo_ruta
                    mejor_pedido = pedido

        return mejor_pedido

    ### Lógica de interacción (recoger/entregar) - Aún por implementar ###

    def _intentar_recoger(self, city_map):
        """Lógica para cuando la IA llega al punto de recogida."""
        # Esta es una versión simplificada. La lógica completa vendrá después.
        print(f"IA [DIFÍCIL]: Llegó a la ubicación de recogida de {self.objetivo_actual.id}.")
        # (Aquí irá la lógica para añadir al inventario, cambiar estado del pedido, etc.)
        self._reset_estado()  # De momento, solo volvemos a buscar

    def _intentar_entregar(self):
        """Lógica para cuando la IA llega al punto de entrega."""
        # Esta es una versión simplificada.
        print(f"IA [DIFÍCIL]: Llegó a la ubicación de entrega de {self.objetivo_actual.id}.")
        # (Aquí irá la lógica para obtener puntos, actualizar reputación, etc.)
        self._reset_estado()  # De momento, solo volvemos a buscar