from dataclasses import dataclass
from typing import Optional

@dataclass
class TileType:
    name: str
    surface_weight: Optional[float] = None
    blocked: Optional[bool] = False

@dataclass
class Tile:
    x: int
    y: int
    type: TileType

@dataclass
class CityMap:
    city_name: str
    width: int
    height: int
    goal: int
    max_time: int
    tiles: list[list[Tile]]
    start_time: Optional[str] = None
