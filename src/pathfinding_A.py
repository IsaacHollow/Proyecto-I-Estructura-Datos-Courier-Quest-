import heapq


def a_star_pathfinding(start_pos, goal_pos, city_map):
    """
    Encuentra la ruta más corta usando el algoritmo A*.
    """
    if not (0 <= start_pos[0] < city_map.width and 0 <= start_pos[1] < city_map.height):
        return []
    if not (0 <= goal_pos[0] < city_map.width and 0 <= goal_pos[1] < city_map.height):
        return []
    if city_map.tiles[start_pos[1]][start_pos[0]].type.blocked:
        return []
    if city_map.tiles[goal_pos[1]][goal_pos[0]].type.blocked:
        return []

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_set = []
    heapq.heappush(open_set, (0, start_pos))  # Guardamos (f_score, pos)

    came_from = {}
    g_score = {(x, y): float('inf') for y in range(city_map.height) for x in range(city_map.width)}
    g_score[start_pos] = 0

    f_score_map = {(x, y): float('inf') for y in range(city_map.height) for x in range(city_map.width)}
    f_score_map[start_pos] = heuristic(start_pos, goal_pos)

    while open_set:
        _, current_pos = heapq.heappop(open_set)

        if current_pos == goal_pos:
            # Reconstrucción de ruta
            path = [current_pos]
            while current_pos in came_from:
                current_pos = came_from[current_pos]
                path.append(current_pos)
            return path[::-1]

        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            neighbor_pos = (current_pos[0] + dx, current_pos[1] + dy)

            if not (0 <= neighbor_pos[0] < city_map.width and 0 <= neighbor_pos[1] < city_map.height):
                continue

            if city_map.tiles[neighbor_pos[1]][neighbor_pos[0]].type.blocked:
                continue

            move_cost = city_map.tiles[neighbor_pos[1]][neighbor_pos[0]].type.surface_weight or 1.0
            tentative_g_score = g_score[current_pos] + move_cost

            if tentative_g_score < g_score[neighbor_pos]:
                came_from[neighbor_pos] = current_pos
                g_score[neighbor_pos] = tentative_g_score
                f_score = tentative_g_score + heuristic(neighbor_pos, goal_pos)
                f_score_map[neighbor_pos] = f_score

                # Evitar duplicados en open_set
                in_open_set = False
                for _, pos_in_set in open_set:
                    if pos_in_set == neighbor_pos:
                        in_open_set = True
                        break
                if not in_open_set:
                    heapq.heappush(open_set, (f_score, neighbor_pos))

    return []  # No se encontró ruta