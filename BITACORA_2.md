DIFICULTAD DIFICIL:

La dificultad dificil es el algoritmo más avanzado/inteligente de las tres dificultades que implementamos.
Para su creacion e implementacion utilizamos ayuda de IA para crear el archivo pathfinding_A.py

Primero se le pidió información sobre las dos opciones posibles para el algoritmo de esta dificultad (Dijkstra o A*) con el siguiente prompt:

    "Tengo un proyecto sobre un juego de repartidor por una ciudad, el repartidor posee un inventario donde puede observar sus paquetes actuales así como poder seleccionar uno para visualizar su ubicacion de entrega,
    recoger mas paquetes y entregarlos, tiene un movimiento por casillas y el mapa es una matriz grande de casillas con diferentes propiedades.
    El jugador se enfrenta a una IA con 3 niveles de dificultad diferentes quiero hacer la dificultad dificil la cual tiene las siguientes indicaciones:
    
    [Indicaciones para la dificultad dificil dadas en el enunciado del proyecto]
    
    Antes de implementar quiero que me recomiendes que metodo de busqueda de rutas usar entre dijkstra y A* y por qué la opcion elegida sería mejor para mi proyecto."

La IA no solo nos recomendó usar A* para dicha dificultad, si no tambien su heuristica, la Distancia de Manhattan.
A continuacion un resumen de la respuesta:

    "Para tu proyecto, la recomendación clara y directa es usar el *algoritmo A (A-star)**. Es más eficiente y está mejor adaptado para el problema que el CPU necesita resolver."

    "El Algoritmo de Dijkstra:

    ¿Qué hace? El algoritmo de Dijkstra encuentra el camino más corto desde un nodo de inicio hasta todos los demás nodos en un grafo ponderado
    
    -Fortalezas:
        Garantiza encontrar el camino más corto (si los pesos de las aristas no son negativos, lo cual es tu caso).
        Es útil si necesitas saber la distancia desde un punto a múltiples destinos a la vez.

    -Debilidades en tu proyecto:
        Es ineficiente. El CPU casi siempre tiene un único objetivo: "ir al punto de recogida X" o "ir al punto de entrega Y". 
        Dijkstra perderá mucho tiempo y recursos computacionales explorando caminos que se alejan del objetivo..
    
    El Algoritmo A* (A-star)

    ¿Qué hace?:
    A* encuentra el camino más corto desde un nodo de inicio hasta un único nodo de destino.
    ¿Cómo funciona?:
    A* es esencialmente una versión "inteligente" de Dijkstra. Al igual que Dijkstra, calcula el costo real del camino recorrido desde el inicio hasta la casilla actual (esto se llama g(n)).
    
    Pero, además, añade una heurística: una estimación del costo que queda desde la casilla actual hasta el destino (esto se llama h(n)).

    La fórmula es: f(n) = g(n) + h(n)
    g(n) = Costo real desde el inicio hasta la casilla n.
    h(n) = Costo estimado desde la casilla n hasta el destino.

    La Heurística (La Magia de A)**: Para un mapa de cuadrícula como el tuyo, la heurística más común y efectiva es la distancia de Manhattan. Esta simplemente calcula la distancia horizontal y vertical entre dos puntos, ignorando los obstáculos. Es muy rápida de calcular: h(n) = abs(n.x - destino.x) + abs(n.y - destino.y).
    Como nunca sobreestima el costo real (el camino más corto nunca será menor que la distancia en línea recta sin obstáculos), A garantiza encontrar el camino óptimo.

    Fortalezas en tu proyecto:
        Es muy eficiente. Gracias a la heurística, A* prioriza los caminos que parecen dirigirse hacia el destino. No pierde tiempo explorando en direcciones obviamente incorrectas, lo que reduce drásticamente el número de casillas que necesita evaluar.
        Está diseñado para un solo objetivo. El problema del CPU ("ir de A a B") es exactamente el caso de uso para el que se creó A*.


Para resumir, el algoritmo A* es mejor para nuestro proyecto dado que el CPU siempre tendrá un objetivo claro (recoger y entregar de un punto A a un punto B).
A* permitirá calcular la ruta mas corta de manera mas rapida y con menos consumo de recursos que Dijsktra, sobre todo al utilizar la distancia de Manhattan como heuristica.

-------------

El codigo para la implementacion del Pathfinding A* fue hecho en gran parte por IA, quien además nos recomendó utilizar la librería "heapq" para usar una cola de prioridad de minimo.

Por lo tanto, pedimos la suficiente explicacion para comprender como funcionaba, no solo con fines educativos, sino también para poder implementarlo de manera correcta con el repartidor_IA que ya teníamos.

A continuacion una explicacion detallada de todo el algoritmo, su funcionamiento y ciclo de ejecucion.


1. El Algoritmo A* (src/pathfinding_A.py)
¿Qué es A*?

A* (A-Star) es un algoritmo de búsqueda de caminos que encuentra la ruta más corta entre dos puntos en un grafo (en este caso, un mapa en cuadrícula).
Lo que hace especial a A* es que es inteligente: no explora todas las direcciones por igual, sino que prioriza las que parecen más prometedoras.

Componentes Clave del Algoritmo:

a. La Heurística
def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

Esta función calcula la distancia Manhattan entre dos puntos. Es una estimación de cuántas casillas faltan para llegar al destino si pudiera mover en línea recta (sin considerar obstáculos).
Por ejemplo:

    Desde (5, 5) hasta (8, 9): |8-5| + |9-5| = 3 + 4 = 7 casillas.

b. Las Dos Puntuaciones

El algoritmo usa dos valores para cada casilla:

    g_score: El costo real desde el inicio hasta esa casilla. Es decir, cuánto te ha costado llegar hasta ahí.
    f_score: La puntuación total estimada: f = g + h, donde h es la heurística (estimación del costo restante).


Ejemplo visual:

Inicio [0,0] → [1,0] → [2,0] → Meta [3,0]

Para [2,0]:
- g_score = 2 (dos pasos desde el inicio)
- h = 1 (estimación: falta 1 casilla)
- f_score = 2 + 1 = 3

c. El Open Set (Cola de Prioridad)
open_set = []
heapq.heappush(open_set, (0, start_pos))

Es una cola de prioridad implementada con un heap. Siempre extrae la casilla con el f_score más bajo (la más prometedora).
Esto es lo que hace a A* tan eficiente: siempre explora primero los caminos que parecen llevar más rápido a la meta.


d. El Bucle Principal

while open_set:
    _, current_pos = heapq.heappop(open_set)
    
    if current_pos == goal_pos:
        # Llegamos, reconstruimos la ruta
        ...
    
    # Explorar vecinos
    for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
        neighbor_pos = (current_pos[0] + dx, current_pos[1] + dy)
        
        # Verificar si es válido
        if not (dentro del mapa) or (bloqueado):
            continue
        
        # Calcular el costo de moverse a ese vecino
        move_cost = peso_de_superficie or 1.0
        tentative_g_score = g_score[current_pos] + move_cost
        
        # Si este camino es mejor que el anterior, actualizarlo
        if tentative_g_score < g_score[neighbor_pos]:
            came_from[neighbor_pos] = current_pos
            g_score[neighbor_pos] = tentative_g_score
            f_score = tentative_g_score + heuristic(neighbor_pos, goal_pos)
            heapq.heappush(open_set, (f_score, neighbor_pos))

Paso a paso:

    Extrae la casilla más prometedora del open_set.
    Si es la meta, termina y reconstruye la ruta.
    Si no, explora sus 4 vecinos (arriba, abajo, izquierda, derecha).
    Para cada vecino válido:
        Calcula el costo de llegar ahí.
        Si es un camino mejor que el anterior, lo guarda en came_from y lo añade al open_set.


e. Reconstrucción de la Ruta

if current_pos == goal_pos:
    path = [current_pos]
    while current_pos in came_from:
        current_pos = came_from[current_pos]
        path.append(current_pos)
    return path[::-1]  # Invertir para tener inicio→fin


Una vez que llegamos a la meta, usamos el diccionario came_from para "retroceder" desde la meta hasta el inicio, reconstruyendo el camino paso a paso.


2. La Función Auxiliar (src/utilidades.py)

encontrar_casilla_accesible_adyacente:

def encontrar_casilla_accesible_adyacente(pos_edificio, city_map):
    x, y = pos_edificio
    direcciones = [(x, y - 1), (x, y + 1), (x - 1, y), (x + 1, y)]
    
    for nx, ny in direcciones:
        if (dentro del mapa) and (no bloqueada):
            return (nx, ny)
    
    return None


¿Por qué es necesaria?

Los paquetes están dentro de edificios (casillas bloqueadas tipo "B"), pero los repartidores solo pueden moverse por calles. Esta función encuentra la casilla de calle adyacente al edificio, que es desde donde el repartidor puede "recoger" o "entregar" el paquete.

Cabe destacar que el archivo utilidades.py se planeó como un conjunto de funciones que nos ayudarían en diferentes partes del codigo, pero al final solo declaramos e implementamos una funcion en el.
Decidimos dejarlo solo para aislar la funcion para casillas accesibles adyecentes.


4. Flujo Detallado de la IA Difícil
Máquina de Estados

La IA opera con 3 estados:

    BUSCANDO_PEDIDO: No tiene objetivo, está evaluando qué pedido tomar.
    YENDO_A_RECOGIDA: Ya eligió un pedido y está en camino a recogerlo.
    YENDO_A_ENTREGA: Recogió el pedido y lo está llevando al destino.

Paso 1: Evaluar y Seleccionar el Mejor Pedido

def _seleccionar_mejor_pedido(self, pedidos_disponibles, city_map, tiempo_juego):
    mejor_pedido = None
    mejor_puntuacion = -float('inf')
    
    for pedido in pedidos_validos:
        # 1. Encontrar casilla accesible para recogida
        casilla_recogida = encontrar_casilla_accesible_adyacente(pedido.pickup, city_map)
        if not casilla_recogida:
            continue  # No se puede acceder, descartar
        
        # 2. Calcular ruta de recogida con A*
        ruta_recogida = a_star_pathfinding((self.tile_x, self.tile_y), casilla_recogida, city_map)
        if not ruta_recogida:
            continue  # No hay camino, descartar
        
        # 3. Encontrar casilla accesible para entrega
        casilla_entrega = encontrar_casilla_accesible_adyacente(pedido.dropoff, city_map)
        if not casilla_entrega:
            continue
        
        # 4. Calcular ruta de entrega con A*
        ruta_entrega = a_star_pathfinding(casilla_recogida, casilla_entrega, city_map)
        if not ruta_entrega:
            continue
        
        # 5. Calcular el costo total
        costo_total = (len(ruta_recogida) - 1) + (len(ruta_entrega) - 1)
        
        # 6. Verificar si llegará a tiempo
        tiempo_estimado = tiempo_juego + costo_total
        tiempo_restante = pedido.deadline - tiempo_estimado
        if tiempo_restante < -30:  # Si llega más de 30s tarde, descartar
            continue
        
        # 7. Calcular puntuación
        puntuacion = (pedido.payout + pedido.priority * 50) / (costo_total * 1.5 + pedido.weight * 5 + 1)
        
        if puntuacion > mejor_puntuacion:
            mejor_puntuacion = puntuacion
            mejor_pedido = pedido
    
    return mejor_pedido


Fórmula de Puntuación Explicada:

puntuacion = (ganancia + prioridad_bonus) / (costo_penalizado + peso_penalizado + 1)

Donde:
- ganancia = payout del pedido
- prioridad_bonus = priority * 50 (pedidos prioritarios valen mucho más)
- costo_penalizado = costo_total * 1.5 (penaliza rutas largas)
- peso_penalizado = weight * 5 (penaliza paquetes pesados)
- +1 al final evita división por cero


Ejemplo de Evaluación:

Pedido A:
- payout: 200
- priority: 1
- costo_total: 20
- weight: 2
→ puntuacion = (200 + 50) / (20*1.5 + 2*5 + 1) = 250 / 41 = 6.09

Pedido B:
- payout: 150
- priority: 0
- costo_total: 8
- weight: 1
→ puntuacion = (150 + 0) / (8*1.5 + 1*5 + 1) = 150 / 18 = 8.33

→ La IA elige el Pedido B (mayor puntuación)


Paso 2: Seguir la Ruta Calculada

def _seguir_ruta(self, city_map, weather, colliders):
    if not self.ruta_actual or self.is_moving:
        return  # Esperar a terminar el movimiento actual
    
    # Tomar el siguiente paso de la ruta
    proximo_paso = self.ruta_actual[0]
    
    # Calcular la dirección
    dx = proximo_paso[0] - self.tile_x
    dy = proximo_paso[1] - self.tile_y
    
    # Moverse
    self.start_move(dx, dy, city_map, colliders, weather)
    
    # Si el movimiento fue exitoso, eliminar ese paso de la ruta
    if self.is_moving:
        self.ruta_actual.pop(0)


Posición actual: [5, 5]
Ruta calculada: [[6,5], [7,5], [7,6], [7,7]]

Iteración 1:
- proximo_paso = [6,5]
- dx = 6-5 = 1, dy = 5-5 = 0
- start_move(1, 0, ...) → mueve a la derecha
- ruta_actual = [[7,5], [7,6], [7,7]]

Iteración 2 (después de terminar el movimiento):
- proximo_paso = [7,5]
- dx = 7-6 = 1, dy = 5-5 = 0
- start_move(1, 0, ...) → mueve a la derecha otra vez
- ruta_actual = [[7,6], [7,7]]

... y así sucesivamente hasta vaciar la ruta

Paso 3: Interacción con Pedidos
-Verificar si estamos adyacentes al edificio donde está el paquete
-Agregar al inventario
-Calcular nueva ruta hacia la entrega


5. Integración con el Juego

En Views/juego.py, el bucle principal actualiza la IA:

def actualizar(self, dt):
    self.repartidor_ia.actualizar_logica_ia(
        dt,
        self.city_map,
        self.building_rects,
        self.weather,
        self.pedidos_disponibles,
        self.tiempo_juego
    )
    
Cada frame (60 veces por segundo), la IA:

    1.Verifica su estado actual.
    2.Si está buscando, evalúa pedidos cada 2.5 segundos.
    3.Si está en ruta, da un paso si no está en movimiento.
    4.Si llegó a un destino, intenta recoger/entregar.

**********************************************************************************************************

DIFICULTAD MEDIA

PROMPTS

    "Quiero hacer la dificultad media del repartidor, se necesita utilizar, el comportamiento ocupa un horizonte de anticipación pequeño (2-3 acciones por delante), Evalúa movimientos potenciales con una función de puntuación simple, por ejemplo: score = α*(expected payout) – β*(distance cost) – γ*(weather penalty) Selecciona el movimiento con la puntuación máxima. Me puedes ayudar a decidir para este proyecto si utilizar “Greedy best-first”, Minimax o expectimax funciona. Me puedes explicar y mostrar los codigos y cual seria mejor utilizar"

Para un balance en la dificultad:

    “Estoy intentando que la IA media no actúe igual que la dificultad difícil, porque siento que se está comportando casi igual y no puede usar A*.
    La idea es que la difícil sí use pathfinding y análisis completo, pero la media solo use evaluación local tipo greedy.
    ¿Que puedo cambiar o qué tengo que mover para "disminuir" un poco la dificultad y que no se mezclen ambas dificultades?”

Para la dificultad media en la toma de decisiones de la IA utilizamos Greedy Best-First. Decidimos no utilizar minimax ni expectimax porque Minimax requiere modelar al jugador humano como oponente y un árbol de juego grande, lo cual no aplica aquí.
Expectimax es más costoso y se usa cuando hay incertidumbre probabilística.
Greedy Best-First es suficiente, más simple, rápido y cumple exactamente lo que pide el enunciado del proyecto, la anticipación corta, evaluación y selección del mejor movimiento.

*****************************************************************************

DIFICULTAD FACIL

Función y Comportamiento (¿Qué hace?)

El objetivo de la IA en dificultad Fácil es simular a un repartidor novato y distraído. No es un competidor muy eficiente, pero participa activamente en el juego, recogiendo y entregando paquetes de una manera poco óptima y algo errática. Su comportamiento se puede resumir en los siguientes puntos:

    Selección de Objetivos al Azar: No analiza cuál es el "mejor" pedido. Simplemente elige uno al azar de la lista de paquetes disponibles.
    Movimiento Errático: En lugar de seguir una ruta óptima (como lo hacen las dificultades Media y Difícil con el algoritmo A*), se mueve paso a paso. En cada casilla, decide su siguiente movimiento con una fuerte tendencia a ir en la dirección correcta, pero con una probabilidad notable de desviarse hacia los lados.
    Lógica de Paquetes Simple:
        Una vez que elige un paquete, se enfoca en ir al punto de recogida.
        Después de recogerlo, su único objetivo es ir al punto de entrega. No se distrae con otros pedidos disponibles.
    Poca "Memoria" y Distracción: Si pasa demasiado tiempo (unos 20 segundos) intentando llegar a un paquete sin éxito, "se aburre" y elige un nuevo objetivo al azar, simulando distracción o falta de constancia.

En resumen, es un oponente que está en el juego y compite por los mismos recursos, pero sus errores y su falta de estrategia lo convierten en un primer desafío ideal sin ser demasiado abrumador.

Implementación (Cómo lo hace)

La lógica se encuentra principalmente en la función _ejecutar_logica_simple dentro del archivo repartidor_IA.py. 
A continuación se desglosa su funcionamiento interno:

    1.Ciclo de Decisión: La IA toma decisiones de movimiento a intervalos regulares, definidos por self.intervalo_movimiento_simple (0.5 segundos).

    2.Búsqueda de Objetivo:
        La IA solo busca un nuevo pedido si se encuentra en estado BUSCANDO_PEDIDO (no tiene un objetivo) o si han pasado más de 20 segundos persiguiendo el mismo objetivo (el decision_timer).
        Crucialmente, no buscará un nuevo paquete si ya está en estado YENDO_A_ENTREGA.
        Para elegir, obtiene una lista de todos los pedidos disponibles y usa random.choice() para seleccionar uno.

    3.Lógica de Movimiento Probabilístico:
        Una vez que tiene un objetivo (sea de recogida o entrega), calcula la dirección general (ej. "a la derecha y hacia abajo").
        Crea una lista de posibles movimientos. A la dirección correcta se le da un peso mayor (se añade 8 veces a la lista), mientras que a las direcciones laterales se les da un peso menor (se añaden 1 o 2 veces).
        Finalmente, usa random.choice() sobre esta lista ponderada para decidir su siguiente paso. Esto provoca que la mayor parte del tiempo se mueva correctamente, pero ocasionalmente "se equivoque" y se desvíe.

    4.Interacción (Recoger y Entregar):
        En cada ciclo, antes de moverse, comprueba si está adyacente al punto de recogida o entrega de su objetivo actual.
        Si lo está, intenta realizar la acción correspondiente (_intentar_recoger o _intentar_entregar).
        Al recoger un paquete, su estado cambia a YENDO_A_ENTREGA.
        Al entregarlo, se procesa su pago y su estado vuelve a BUSCANDO_PEDIDO.
