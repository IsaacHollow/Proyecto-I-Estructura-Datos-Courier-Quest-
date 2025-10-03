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
            self.pedidos.remove(pedido)
            self.peso_total -= pedido.weight
            pedido.status = "entregado"  # opcional
            return True
        return False

    # Recorrido con cursor
    def actual(self) -> Optional[Pedido]:
        if not self.pedidos:
            return None
        return self.pedidos[self.cursor]

    def siguiente(self) -> Optional[Pedido]:
        if not self.pedidos:
            return None
        self.cursor = (self.cursor + 1) % len(self.pedidos)
        return self.actual()

    def anterior(self) -> Optional[Pedido]:
        if not self.pedidos:
            return None
        self.cursor = (self.cursor - 1) % len(self.pedidos)
        return self.actual()


    # Vistas de pedidos
    def ver_por_prioridad(self) -> List[Pedido]:
        """Devuelve los pedidos ordenados de mayor a menor prioridad."""
        return sorted(self.pedidos, key=lambda p: p.priority, reverse=True)

    def ver_por_deadline(self) -> List[Pedido]:
        """Devuelve los pedidos ordenados por deadline (más temprano primero)."""
        return sorted(self.pedidos, key=lambda p: p.deadline)

    # Utilidades
    def esta_lleno(self) -> bool:
        return self.peso_total >= self.peso_max

    def buscar_por_id(self, pedido_id: str) -> Optional[Pedido]:
        for p in self.pedidos:
            if p.id == pedido_id:
                return p
        return None