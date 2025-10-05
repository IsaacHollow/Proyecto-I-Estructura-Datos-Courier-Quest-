from dataclasses import dataclass, field
from typing import List, Any
from src.repartidor import Repartidor
from src.weather import Weather
from src.mapa import CityMap
from src.pedidos import Pedido

@dataclass
class EstadoJuego:
    # Datos de la sesión inicial
    city_map: CityMap
    pedidos_iniciales: List[Pedido]

    # Estado dinámico del juego
    tiempo_juego: float
    repartidor: Repartidor
    pedidos_actuales: List[Pedido] # La lista de pedidos con sus estados actualizados
    weather: Weather