import heapq


def a_star_pathfinding(start_pos, goal_pos, city_map):
    """
    Encuentra la ruta más corta usando el algoritmo A*.

    Args:
        start_pos (tuple): Coordenadas (x, y) de inicio.
        goal_pos (tuple): Coordenadas (x, y) del destino.
        city_map (CityMap): El objeto del mapa de la ciudad.

    Returns:
        list: Una lista de tuplas (x, y) que representan la ruta, o una lista vacía si no se encuentra.
    """

    # Función heurística (Distancia de Manhattan)
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    # (f_score, g_score, posición, padre)
    # f_score es el costo total estimado, g_score es el costo real desde el inicio.
    heapq.heappush(open_set, (heuristic(start_pos, goal_pos), 0, start_pos))

    came_from = {}
    g_score = {(x, y): float('inf') for y, row in enumerate(city_map.tiles) for x, tile in enumerate(row)}
    g_score[start_pos] = 0

    while open_set:
        # Obtener el nodo con el f_score más bajo
        _, current_g, current_pos = heapq.heappop(open_set)

        if current_pos == goal_pos:
            # Reconstruir la ruta
            path = []
            while current_pos in came_from:
                path.append(current_pos)
                current_pos = came_from[current_pos]
            path.append(start_pos)
            return path[::-1]  # Devolver la ruta en el orden correcto (invertido)

        # Explorar vecinos (arriba, abajo, izquierda, derecha)
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor_pos = (current_pos[0] + dx, current_pos[1] + dy)

            # Comprobar si el vecino está dentro del mapa
            if not (0 <= neighbor_pos[0] < city_map.width and 0 <= neighbor_pos[1] < city_map.height):
                continue

            neighbor_tile = city_map.tiles[neighbor_pos[1]][neighbor_pos[0]]

            # Ignorar si es un obstáculo
            if neighbor_tile.type.blocked:
                continue

            # El costo de moverse a este vecino es el peso de la superficie del tile actual
            # (asumimos que el costo se paga al "entrar" en una casilla).
            move_cost = neighbor_tile.type.surface_weight

            tentative_g_score = current_g + move_cost

            if tentative_g_score < g_score[neighbor_pos]:
                # Se encontró un camino mejor hacia este vecino
                came_from[neighbor_pos] = current_pos
                g_score[neighbor_pos] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor_pos, goal_pos)
                heapq.heappush(open_set, (f_score, tentative_g_score, neighbor_pos))

    return []  # No se encontró ruta