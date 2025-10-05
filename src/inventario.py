from typing import List, Optional
from src.pedidos import Pedido


class Inventario:
    def __init__(self, peso_max: float):
        self.pedidos: List[Pedido] = []
        self.peso_max: float = peso_max
        self.peso_total: float = 0.0
        self.cursor: int = 0  # para recorrer la lista de pedidos

    # Gestión de pedidos
    def agregar_pedido(self, pedido: Pedido) -> bool:
        """Intenta agregar un pedido al inventario. Devuelve True si se pudo."""
        if self.peso_total + pedido.weight <= self.peso_max:
            self.pedidos.append(pedido)
            self.peso_total += pedido.weight
            return True
        return False

    def entregar_pedido(self, pedido: Pedido) -> bool:
        """Elimina un pedido del inventario y descuenta el peso."""
        if pedido in self.pedidos:
            try:
                idx_a_eliminar = self.pedidos.index(pedido)
            except ValueError:
                return False

            self.pedidos.remove(pedido)
            self.peso_total -= pedido.weight

            # Ajustar el cursor de forma segura
            if self.cursor > idx_a_eliminar:
                self.cursor -= 1
            if self.cursor >= len(self.pedidos) and len(self.pedidos) > 0:
                self.cursor = len(self.pedidos) - 1

            return True
        return False

    # Recorrido con cursor
    def actual(self) -> Optional[Pedido]:
        """Devuelve el pedido actualmente seleccionado por el cursor."""
        if not self.pedidos:
            return None
        if self.cursor < 0 or self.cursor >= len(self.pedidos):
            self.cursor = 0
            if not self.pedidos: return None
        return self.pedidos[self.cursor]

    def siguiente(self, vista_actual: List[Pedido]):
        """Mueve el cursor al siguiente pedido en la vista actual."""
        if not vista_actual:
            return

        pedido_actual = self.actual()
        try:
            idx_en_vista = vista_actual.index(pedido_actual)
            nuevo_idx_en_vista = (idx_en_vista + 1) % len(vista_actual)
            nuevo_pedido = vista_actual[nuevo_idx_en_vista]
            self.cursor = self.pedidos.index(nuevo_pedido)
        except (ValueError, IndexError):
            if self.pedidos:
                self.cursor = self.pedidos.index(vista_actual[0])

    def anterior(self, vista_actual: List[Pedido]):
        """Mueve el cursor al pedido anterior en la vista actual."""
        if not vista_actual:
            return

        pedido_actual = self.actual()
        try:
            idx_en_vista = vista_actual.index(pedido_actual)
            nuevo_idx_en_vista = (idx_en_vista - 1) % len(vista_actual)
            nuevo_pedido = vista_actual[nuevo_idx_en_vista]
            self.cursor = self.pedidos.index(nuevo_pedido)
        except (ValueError, IndexError):
            if self.pedidos:
                self.cursor = self.pedidos.index(vista_actual[0])

    def _insertion_sort(self, lista: List[Pedido], key, reverse=False) -> List[Pedido]:
        """
                Ordena una copia de la lista usando el algoritmo Insertion Sort.
                - key: una función que extrae la clave de comparación de un elemento.
                - reverse: si es True, ordena de mayor a menor.
                """
        arr = list(lista)  # Hacemos una copia para no modificar la lista original
        for i in range(1, len(arr)):
            elemento_actual = arr[i]
            # Usamos la función key para obtener el valor a comparar
            valor_actual = key(elemento_actual)

            j = i - 1

            # Comparación para orden ascendente (reverse=False)
            if not reverse:
                while j >= 0 and key(arr[j]) > valor_actual:
                    arr[j + 1] = arr[j]  # Desplazar elemento a la derecha
                    j -= 1
            # Comparación para orden descendente (reverse=True)
            else:
                while j >= 0 and key(arr[j]) < valor_actual:
                    arr[j + 1] = arr[j]  # Desplazar elemento a la derecha
                    j -= 1

            # Insertar el elemento actual en su posición correcta
            arr[j + 1] = elemento_actual
        return arr

    # Vistas de pedidos
    def ver_por_prioridad(self) -> List[Pedido]:
        """Devuelve los pedidos ordenados de mayor a menor prioridad."""
        return self._insertion_sort(self.pedidos, key=lambda p: p.priority, reverse=True)

    def ver_por_deadline(self) -> List[Pedido]:
        """Devuelve los pedidos ordenados por deadline (más temprano primero)."""
        # Como 'deadline' ahora es un entero (segundos), el sort es directo.
        return self._insertion_sort(self.pedidos, key=lambda p: p.deadline, reverse=False)

    def obtener_vista_actual(self, vista: str) -> List[Pedido]:
        """Devuelve la lista de pedidos según la vista seleccionada."""
        if vista == "prioridad":
            return self.ver_por_prioridad()
        elif vista == "deadline":
            return self.ver_por_deadline()
        else:  # "normal" o cualquier otro caso
            return list(self.pedidos)

    # Utilidades
    def esta_lleno(self) -> bool:
        return self.peso_total >= self.peso_max

    def buscar_por_id(self, pedido_id: str) -> Optional[Pedido]:
        for p in self.pedidos:
            if p.id == pedido_id:
                return p
        return None