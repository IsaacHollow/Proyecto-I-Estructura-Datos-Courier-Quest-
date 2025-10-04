import requests
from src.mapa import TileType, Tile, CityMap
from src.clima import Clima
from src.pedidos import Pedido
from datetime import datetime, timezone


# Factor para acelerar la aparición de paquetes.
# Un valor más alto hace que aparezcan más rápido.
# Por ejemplo, 3.0 significa que aparecerán 3 veces más rápido.
FACTOR_ACELERACION_RELEASE = 3.0

def load_city_map(url: str) -> CityMap:
    response = requests.get(url)
    response.raise_for_status()
    raw = response.json()["data"]

    legend = {key: TileType(**value) for key, value in raw["legend"].items()}

    tile_matrix = []
    for y, row in enumerate(raw["tiles"]):
        tile_row = []
        for x, symbol in enumerate(row):
            tile_type = legend.get(symbol, TileType(name="unknown"))
            tile_row.append(Tile(x=x, y=y, type=tile_type))
        tile_matrix.append(tile_row)

    return CityMap(
        city_name=raw["city_name"],
        width=raw["width"],
        height=raw["height"],
        goal=raw["goal"],
        max_time=raw["max_time"],
        tiles=tile_matrix
    )

def load_clima(url: str) -> Clima:
    response = requests.get(url)
    response.raise_for_status()
    raw = response.json()["data"]

    return Clima(
        city=raw["city"],
        condition=raw["initial"]["condition"],
        intensity=raw["initial"]["intensity"],
        conditions=raw["conditions"],
        transition=raw["transition"]
    )


def load_pedidos(url: str) -> list[Pedido]:
    response = requests.get(url)
    response.raise_for_status()
    raw_data = response.json()["data"]

    # 1. Crear objetos Pedido a partir de los datos del API
    #    Aquí se produce el error si deadline es str en el dataclass
    pedidos_iniciales = []
    for item in raw_data:
        # Creamos un diccionario temporal para poder modificarlo
        data = item.copy()
        # Mantenemos el deadline como string por ahora
        pedidos_iniciales.append(Pedido(**data))

    if not pedidos_iniciales:
        return []

    # 2. Normalizar los tiempos
    # Convertimos los deadlines (string) a timestamps para encontrar el punto de inicio
    timestamps = []
    for p in pedidos_iniciales:
        dt_obj = datetime.fromisoformat(p.deadline.replace('Z', '+00:00'))
        timestamps.append(dt_obj.timestamp())

    start_time = min(timestamps)

    # 3. Procesar y finalizar la lista de pedidos
    pedidos_finales = []
    for i, pedido in enumerate(pedidos_iniciales):
        # Ajustes del juego
        pedido.status = "pendiente"
        pedido.pickup = (int(pedido.pickup[0]), int(pedido.pickup[1]))
        pedido.dropoff = (int(pedido.dropoff[0]), int(pedido.dropoff[1]))

        # Convertimos el deadline a segundos relativos al inicio
        deadline_timestamp = timestamps[i]
        pedido.deadline = int(deadline_timestamp - start_time)

        # Aceleramos el tiempo de liberación dividiéndolo por nuestro factor
        pedido.release_time = int(pedido.release_time / FACTOR_ACELERACION_RELEASE)

        pedidos_finales.append(pedido)

    return pedidos_finales