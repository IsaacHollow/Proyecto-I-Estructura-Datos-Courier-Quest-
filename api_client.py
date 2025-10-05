import requests
from src.mapa import TileType, Tile, CityMap
from src.clima import Clima
from src.pedidos import Pedido
from datetime import datetime, timezone


# Factor para acelerar la aparición de paquetes.
# Un valor más alto hace que aparezcan más rápido.
# Por ejemplo, 3.0 significa que aparecerán 3 veces más rápido.
FACTOR_ACELERACION = 3.0

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

    max_time_acelerado = int(raw.get("max_time", 0) / FACTOR_ACELERACION)

    return CityMap(
        city_name=raw["city_name"],
        width=raw["width"],
        height=raw["height"],
        goal=raw["goal"],
        #max_time=raw["max_time"],
        max_time=max_time_acelerado,
        tiles=tile_matrix,
        start_time=raw.get("start_time")
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


def load_pedidos(url: str, map_start_time: str) -> list[Pedido]:
    response = requests.get(url)
    response.raise_for_status()
    raw_data = response.json()["data"]

    pedidos_iniciales = [Pedido(**item) for item in raw_data]

    if not pedidos_iniciales or not map_start_time:
        return []

    # Convertimos el start_time del mapa (string) a un timestamp de referencia.
    start_timestamp = datetime.fromisoformat(map_start_time.replace('Z', '+00:00')).timestamp()

    # Procesar y finalizar la lista de pedidos
    pedidos_finales = []
    for pedido in pedidos_iniciales:
        # Ajustes del juego
        pedido.status = "pendiente"
        pedido.pickup = (int(pedido.pickup[0]), int(pedido.pickup[1]))
        pedido.dropoff = (int(pedido.dropoff[0]), int(pedido.dropoff[1]))

        # Convertimos el deadline del pedido (string ISO) a segundos relativos al start_time del mapa.
        deadline_timestamp = datetime.fromisoformat(pedido.deadline.replace('Z', '+00:00')).timestamp()
        #pedido.deadline = int(deadline_timestamp - start_timestamp)

        pedido.deadline = int((deadline_timestamp - start_timestamp) / FACTOR_ACELERACION)
        pedido.release_time = int(pedido.release_time / FACTOR_ACELERACION)

        pedidos_finales.append(pedido)

    return pedidos_finales