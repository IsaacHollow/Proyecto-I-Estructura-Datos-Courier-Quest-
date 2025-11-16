import heapq


def a_star_pathfinding(start_pos, goal_pos, city_map):
    """
    Encuentra la ruta más corta usando el algoritmo A*.
    """

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    initial_f_score = heuristic(start_pos, goal_pos)
    heapq.heappush(open_set, (initial_f_score, 0, start_pos))

    came_from = {}
    g_score = {(x, y): float('inf') for y in range(city_map.height) for x in range(city_map.width)}
    g_score[start_pos] = 0

    while open_set:
        _, current_g, current_pos = heapq.heappop(open_set)

        if current_pos == goal_pos:
            # Reconstruir la ruta correctamente
            path = []
            temp_pos = current_pos
            while temp_pos in came_from:
                path.append(temp_pos)
                temp_pos = came_from[temp_pos]
            path.append(start_pos)  # Añadir el nodo inicial
            return path[::-1]  # Devolver en el orden correcto (inicio -> fin)

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor_pos = (current_pos[0] + dx, current_pos[1] + dy)

            if not (0 <= neighbor_pos[0] < city_map.width and 0 <= neighbor_pos[1] < city_map.height):
                continue

            neighbor_tile = city_map.tiles[neighbor_pos[1]][neighbor_pos[0]]

            if neighbor_tile.type.blocked:
                continue

            move_cost = neighbor_tile.type.surface_weight or 1.0
            tentative_g_score = current_g + move_cost

            if tentative_g_score < g_score[neighbor_pos]:
                came_from[neighbor_pos] = current_pos
                g_score[neighbor_pos] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor_pos, goal_pos)
                heapq.heappush(open_set, (f_score, tentative_g_score, neighbor_pos))

    return []  # No se encontró ruta