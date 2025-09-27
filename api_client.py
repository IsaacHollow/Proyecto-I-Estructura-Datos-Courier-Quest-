import requests
from src.mapa import TileType, Tile, CityMap

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
