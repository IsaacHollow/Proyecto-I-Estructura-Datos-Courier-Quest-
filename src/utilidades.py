def encontrar_casilla_accesible_adyacente(pos_edificio, city_map):
    """
    Encuentra la casilla de calle más cercana y accesible adyacente a una posición de edificio.
    """
    x, y = pos_edificio

    direcciones = [
        (x, y - 1),
        (x, y + 1),
        (x - 1, y),
        (x + 1, y),
    ]

    for nx, ny in direcciones:
        if not (0 <= nx < city_map.width and 0 <= ny < city_map.height):
            continue
        tile = city_map.tiles[ny][nx]
        if not tile.type.blocked:
            return (nx, ny)

    return None