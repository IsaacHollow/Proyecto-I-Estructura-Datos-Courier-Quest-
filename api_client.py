import requests
import json
import os
from src.mapa import TileType, Tile, CityMap
from src.clima import Clima
from src.pedidos import Pedido
from datetime import datetime
from pathlib import Path



# Factor para acelerar la aparición de paquetes.
# Un valor más alto hace que aparezcan más rápido.
# Por ejemplo, 3.0 significa que aparecerán 3 veces más rápido.
FACTOR_ACELERACION = 3.0
CACHE_DIR = Path("api_cache")
DATA_DIR = Path("data")


def _get_data_with_cache(url: str, name: str):

    CACHE_DIR.mkdir(exist_ok=True)

    # Intentar obtener datos del API
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        # Guardar en cache si la respuesta es exitosa
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        cache_file = CACHE_DIR / f"{name}_{timestamp}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

        print(f"Datos de '{name}' obtenidos del API y cacheados.")
        return data["data"]

    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Fallo al obtener datos de '{name}' desde el API: {e}")

        # Intentar usar el último archivo de cache
        try:
            cache_files = sorted(CACHE_DIR.glob(f"{name}_*.json"), reverse=True)
            if cache_files:
                latest_cache = cache_files[0]
                with open(latest_cache, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                print(f"Usando datos cacheados para '{name}' de {latest_cache.name}.")
                return data["data"]
        except Exception as cache_error:
            print(f"Fallo al leer cache para '{name}': {cache_error}")

        # Usar archivo local de /data como último recurso
        try:
            local_file = DATA_DIR / f"{name}.json"
            with open(local_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Usando archivo local de respaldo para '{name}'.")
            return data["data"]
        except Exception as local_error:
            print(f"Fallo al leer archivo local para '{name}': {local_error}")
            raise ConnectionError(f"No se pudieron cargar los datos para '{name}' desde ninguna fuente.")


def load_city_map(url: str) -> CityMap:
    raw = _get_data_with_cache(url, "ciudad")

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
        max_time=max_time_acelerado, # Tiempo maximo acelerado
        tiles=tile_matrix,
        start_time=raw.get("start_time")
    )

def load_clima(url: str) -> Clima:
    raw = _get_data_with_cache(url, "weather")

    return Clima(
        city=raw["city"],
        condition=raw["initial"]["condition"],
        intensity=raw["initial"]["intensity"],
        conditions=raw["conditions"],
        transition=raw["transition"]
    )


def load_pedidos(url: str, map_start_time: str) -> list[Pedido]:
    raw = _get_data_with_cache(url, "pedidos")

    pedidos_iniciales = [Pedido(**item) for item in raw]

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
        pedido.release_time = int(pedido.release_time / FACTOR_ACELERACION) #Aqui se utiliza el factor de tiempo para acelerar el juego

        pedidos_finales.append(pedido)

    return pedidos_finales