import requests
import json
import os
from src.mapa import TileType, Tile, CityMap
from src.clima import Clima
from src.pedidos import Pedido
from datetime import datetime, timezone
from pathlib import Path

FACTOR_ACELERACION = 3.0
CACHE_DIR = Path("api_cache")
DATA_DIR = Path("data")


def _get_data_with_cache(url: str, name: str):
    CACHE_DIR.mkdir(exist_ok=True)
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        cache_file = CACHE_DIR / f"{name}_{timestamp}.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Datos de '{name}' obtenidos del API y cacheados.")
        return data["data"]
    except (requests.RequestException, json.JSONDecodeError) as e:
        print(f"Fallo al obtener datos de '{name}' desde el API: {e}")
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
        max_time=max_time_acelerado,
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
    if not map_start_time: return []

    start_timestamp = datetime.fromisoformat(map_start_time.replace('Z', '+00:00')).timestamp()

    pedidos_finales = []
    for item in raw:
        if not isinstance(item, dict): continue

        # LÓGICA DE TIEMPO CORREGIDA
        try:
            #Obtener tiempos originales en segundos
            release_time_original = int(item.get("release_time", 0))
            deadline_timestamp = datetime.fromisoformat(item["deadline"].replace('Z', '+00:00')).timestamp()
            deadline_relativo_original = deadline_timestamp - start_timestamp

            #Calcular la ventana de tiempo original
            ventana_tiempo_original = deadline_relativo_original - release_time_original
            if ventana_tiempo_original < 0:
                print(f"ADVERTENCIA: Pedido '{item['id']}' ignorado por tener tiempos inconsistentes.")
                continue

            #Acelerar los componentes del tiempo
            release_time_acelerado = int(release_time_original / FACTOR_ACELERACION)
            ventana_tiempo_acelerada = int(ventana_tiempo_original / FACTOR_ACELERACION)

            #Calcular el nuevo deadline acelerado
            deadline_acelerado = release_time_acelerado + ventana_tiempo_acelerada

            pedido = Pedido(
                id=item["id"],
                priority=item["priority"],
                payout=item["payout"],
                weight=item["weight"],
                pickup=(int(item["pickup"][0]), int(item["pickup"][1])),
                dropoff=(int(item["dropoff"][0]), int(item["dropoff"][1])),
                release_time=release_time_acelerado,
                deadline=deadline_acelerado,
                status="pendiente"
            )
            pedidos_finales.append(pedido)

        except (KeyError, TypeError, ValueError) as e:
            print(f"ADVERTENCIA: No se pudo procesar un pedido, saltando. Error: {e}. Datos del pedido: {item}")
            continue

    return pedidos_finales