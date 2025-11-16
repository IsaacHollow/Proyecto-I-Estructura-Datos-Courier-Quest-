import heapq


def a_star_pathfinding(start_pos, goal_pos, city_map):
    """
    Encuentra la ruta más corta usando el algoritmo A*.
    """

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    # Usamos la heurística inicial para el primer f_score
    initial_f_score = heuristic(start_pos, goal_pos)
    heapq.heappush(open_set, (initial_f_score, 0, start_pos))

    came_from = {}
    # Inicializamos g_score para todas las casillas con infinito
    g_score = {(x, y): float('inf') for y in range(city_map.height) for x in range(city_map.width)}
    g_score[start_pos] = 0

    while open_set:
        current_f, current_g, current_pos = heapq.heappop(open_set)

        if current_pos == goal_pos:
            path = []
            while current_pos in came_from:
                path.append(current_pos)
                current_pos = came_from[current_pos]
            return path[::-1]  # Devolver la ruta en el orden correcto

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor_pos = (current_pos[0] + dx, current_pos[1] + dy)

            if not (0 <= neighbor_pos[0] < city_map.width and 0 <= neighbor_pos[1] < city_map.height):
                continue

            neighbor_tile = city_map.tiles[neighbor_pos[1]][neighbor_pos[0]]

            if neighbor_tile.type.blocked:
                continue

            # El costo se basa en el peso de la superficie de la casilla a la que nos movemos
            move_cost = neighbor_tile.type.surface_weight or 1.0

            tentative_g_score = current_g + move_cost

            if tentative_g_score < g_score[neighbor_pos]:
                came_from[neighbor_pos] = current_pos
                g_score[neighbor_pos] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor_pos, goal_pos)
                heapq.heappush(open_set, (f_score, tentative_g_score, neighbor_pos))

    return []  # No se encontró ruta