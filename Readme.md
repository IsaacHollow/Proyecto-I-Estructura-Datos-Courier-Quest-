# Proyecto-I-Estructura-Datos-Courier-Quest-
# Courier Quest — EIF-207 (Ciclo II, 2025)
# Courier Quest II (Apartir de la liena 295)

Deben incluir un archivo README.md con información general del proyecto,	
incluyendo	las	estructuras	de	datos	que	utilizaron	y	para	qué	partes	del	programa.	
Así	como	detalles	de	la	complejidad	algorítmica	


# Equipo:

Isaac Sibaja Cortes
Gabriel Quiros Villalobos
Hernán Sánchez Chaves

___________________________________________________________________________________________________

# Librería escogida:
Pygame

# Motivo:  
Después de mirar varias opciones como Arcade o cocos2d, 
elegimos Pygame porque es facil de usar, hay muchos ejemplos 
y nos deja manejar bien los dibujos, sonidos y la logica del juego.

# Descripcion:
El jugador toma el rol de un repartidor en bicicleta. Cada pedido tiene atributos únicos:

Peso: afecta la velocidad y el consumo de resistencia.  
Deadline: tiempo límite para entregar, afecta la puntuación y reputación.  
Payout: pago por completar el pedido.  
Prioridad: determina la importancia del pedido.  

El juego incluye:  

Sistema de resistencia y agotamiento del repartidor.  
Clima dinámico, que impacta la velocidad y el gasto de energía.  
Inventario limitado con selección y gestión de pedidos.  
Vistas de pedidos por prioridad, deadline o normal.  
Pantallas interactivas: menú principal, reglas, créditos, puntajes, victoria y derrota.  

# Requisitos:
Python 3.10+  
Pygame  
Acceso a internet para cargar mapas y pedidos desde API  

___________________________________________________________________________________________________

# IMPORTANTE:
Al tiempo del juego se le aplicó un factor de aceleracion x3, esto debido a que el tiempo dado por la API es excesivamente alto para la poca cantidad de pedidos que existen.
El tiempo de salida de cada pedido se ajusta al tiempo de partida, 
y esto hace que el jugador tenga que esperar varios minutos sin hacer absolutamente nada hasta que aparezca el proximo pedido a entregar.

Si bien esto hace que no sigamos estrictamente la información dada por la API, aparte de implementar estructuras de datos y analisis de complejidades algoritmicas,
también nos preocupamos porque el resultado final del juego sea de calidad, no solo a nivel de codigo sino también de jugabilidad.

# Estructuras y rendimiento del juego:
---

## Clase "Inventario"
Gestiona los pedidos que el repartidor puede cargar y entregar.

**Estructuras:**  
- `List[Pedido]` para almacenar pedidos  
- `cursor: int` para el pedido actualmente seleccionado  
- `peso_total: float` para llevar el peso acumulado  
**Operaciones:**  
- Agregar pedido: O(1)  
- Entregar pedido: O(n)  
- Obtener pedido actual: O(1)  
- Recorrido con cursor (siguiente/anterior): O(n) sobre la vista actual  
- Ordenar vistas por prioridad/deadline: O(n²) (`insertion sort`)  
**Impacto:**  
Operaciones rápidas para inventarios pequeños.  
Mayor tiempo de corrida al ordenar vistas con listas grandes.  

**Algoritmos utilizados:**
- insertion sort para ordenar pedidos por prioridad o deadline.
- Complejidad: O(n²)
- Eficiente en listas cortas, ineficiente en grandes volúmenes.

---

## Clase "Repartidor"
Representa al jugador y su bicicleta, controla movimiento, resistencia y velocidad.

**Estructuras:**  
- Variables escalares (`float`, `int`) para posición, resistencia, reputación  
- `Inventario` para pedidos  
- Rectángulos de Pygame (`pygame.Rect`) para colisiones  
**Operaciones:**  
- Movimiento: O(1) por tick, velocidad calculada con multiplicadores de clima, peso, reputación y terreno  
- Recuperación de resistencia: O(1)  
**Impacto:**  
Lógica eficiente, sin impacto visible en FPS incluso con varios pedidos  
Actualización de velocidad y resistencia es constante por frame  
**Algoritmos utilizados:**
- Actualización de movimiento y resistencia mediante operaciones aritméticas simples.
- Complejidad: O(1)
- Sin algoritmos de ordenamiento.

---

## Clase "Pedido"
Define los pedidos a entregar.

**Estructuras:**  
- Dataclass con atributos simples (`int`, `float`, `tuple`)  
- `pygame.Surface` opcional para sprites  
**Operaciones:**  
- Calcular tiempo restante: O(1)  
- Determinar prioridad: O(1)  
**Impacto:**  
Muy ligera, sin impacto en rendimiento  

---

## Clase "Weather / Clima"
Gestiona condiciones climáticas y multiplicadores de velocidad/resistencia.

**Estructuras:**  
- Diccionarios para probabilidades de transición (`dict[str, dict[str, float]]`)  
- Variables escalares para intensidad y multiplicadores  
**Operaciones:**  
- Actualización por tick: O(1)  
- Cálculo de multiplicador y resistencia extra: O(1)  
**Impacto:**  
Ligero y eficiente, escala lineal con el tiempo de tick  
**Algoritmos utilizados:**
- Selección aleatoria ponderada según las probabilidades de transición.
- Complejidad: O(k) con k = número de estados posibles
- Ligero impacto, escala lineal con el número de condiciones.
**Algoritmos utilizados:**
- Iteración completa de la matriz para renderizado.
- Complejidad: O(n*m)
- Sin ordenamiento, solo recorrido secuencial.

---

## Clase "CityMap / Tile"
Representa el mapa y los tipos de terreno.

**Estructuras:**  
- `List[List[Tile]]` para las celdas del mapa  
- `TileType` para propiedades de terreno  
**Operaciones:**  
- Acceso a celdas por índice: O(1)  
- Iteración para render o colisiones: O(n*m) con n=width, m=height  
**Impacto:**  
Renderizado y colisiones son la operación más costosa, pero manejable en mapas moderados  

---

## Clase "Camera"
Controla el seguimiento del repartidor y el desplazamiento de la vista.

**Estructuras:**  
- Variables escalares para offset y zoom  
**Operaciones:**  
- Centrar sobre objetivo: O(1)  
- Aplicar offset a posición: O(1)  
**Impacto:**  
Muy eficiente, sin impacto notable en FPS  

---

## Clase "MenuPrincipal"
Muestra los botones del menú y maneja navegación.

**Estructuras:**  
- Lista de diccionarios con rectángulos y callbacks (`List[dict]`)  
**Operaciones:**  
- Hover y click: O(n_botones) por tick  
**Impacto:**  
Ligero, incluso con 5–10 botones, no afecta rendimiento  
**Algoritmos utilizados:**
- Iteración lineal sobre los botones para verificar eventos.
- Complejidad: O(n).
- Sin ordenamiento.

---

## Clase "ScoreManager"
Administra y guarda los puntajes obtenidos tras una partida.

**Estructuras:**
- List[dict] para almacenar los puntajes.
- Archivos .json para almacenamiento persistente.
**Operaciones:**
- Agregar puntaje: O(n log n) (ordenamiento).
- Guardar/leer archivo JSON: O(n).
- Obtener top N: O(k).
**Impacto:**
- Ligero y escalable.
- El ordenamiento mantiene los puntajes siempre actualizados sin degradar el rendimiento.
**Algoritmos utilizados:**
- Timsort para ordenar los puntajes de mayor a menor.
- Complejidad: O(n log n)
- Altamente eficiente en listas cortas o parcialmente ordenadas.

---

## Clase "PantallaPuntaje"
Muestra la tabla de puntajes en pantalla.
**Estructuras:**
- List[str] para las líneas de texto
- Diccionario para el botón “Volver” (dict[str, Any])
**Operaciones:**
- Renderizado de texto: O(n)
- Detección de hover y clic: O(1)
**Impacto:**
- Muy ligera, solo se redibuja cuando se muestra la pantalla.
**Algoritmos utilizados:**
- Ninguno explícito. Iteración secuencial sobre líneas de texto (O(n)).

---

## Clase "SaveManager"
Permite guardar y cargar el estado completo del juego en archivos binarios.
**Estructuras:**
- Path para manejo de directorios.
- Archivos .sav serializados con pickle.
**Operaciones:**
- Guardar partida: O(n) (serialización completa).
- Cargar partida: O(n) (deserialización).
- Verificar guardado existente: O(1).
**Impacto:**
- Asegura persistencia sin afectar la jugabilidad.
- El costo depende del tamaño del estado, pero se ejecuta fuera del bucle principal, evitando caídas de   rendimiento.
**Algoritmos utilizados:**
Serialización:
- Implementación interna de pickle → recorrido profundo y lineal de los atributos del objeto.
- Complejidad: O(n)
Ordenamiento híbrido (implícito):
- Si se mantienen varios guardados:
    -Inserción ordenada → O(n) (insertion sort parcial)
    -Fusión de conjuntos → O(n log n) (merge sort)
- Python implementa esto con Timsort, que combina ambos mecanismos según el patrón de los datos.

---

## Clase "Juego"
Controla la lógica principal del juego, incluyendo interacción del jugador, renderizado de la ciudad, actualización del estado del juego y gestión del inventario.
**Estructuras:**
- Repartidor y su Inventario
- List[Pedido] para los pedidos disponibles
- Camera para manejar el desplazamiento de la vista
- Sprites en diccionario (dict[str, pygame.Surface]) para renderizado de tiles
- Botones de UI (List[dict]) para inventario y menús 
**Operaciones:**
- Renderizado de mapa y tiles: O(n*m), con n = ancho del mapa en tiles, m = alto del mapa
- Renderizado de pedidos: O(p), con p = número de pedidos disponibles y liberados por tiempo
- Actualización del repartidor y movimiento: O(1) por tick
- Detección de colisiones con edificios: O(b), con b = número de edificios en el mapa
- Interacción con pedidos (recoger/entregar): O(p) para recorrer los pedidos adyacentes
Inventario:
    - Acceso al pedido actual: O(1)
    - Navegación (siguiente/anterior): O(n) sobre la vista actual
    - Ordenamiento por prioridad o deadline: O(n²) (insertion sort)
    - Clima y HUD (barra de resistencia, reputación, cronómetro, meta): O(1)
**Impacto:**
- Las operaciones de renderizado son las más costosas, especialmente en mapas grandes, pero permanecen manejables para mapas moderados.
- La lógica de interacción y movimiento es eficiente y constante por frame, sin impacto visible en FPS.
- El inventario mantiene eficiencia para pocas decenas de pedidos; ordenar listas grandes puede generar retrasos, pero rara vez crítico-
- La clase centraliza toda la actualización del juego, por lo que su estructura modular permite mantener FPS estables y facilita la extensión (clima, HUD, inventario, interacción).
**Algoritmos en utilizados**
**Recorrido de tiles para renderizado (dibujar)**
- Tipo: Iteración doble sobre lista 2D (for y in rows; for x in row)
- Complejidad: O(n*m), donde n = ancho del mapa, m = alto del mapa
- Impacto: Es la operación más costosa por frame, especialmente en mapas grandes, pero es lineal en el número de tiles y se puede optimizar con culling de cámara si fuese necesario.
**Renderizado de pedidos**
- Tipo: Iteración sobre lista de pedidos filtrando por release_time
- Complejidad: O(p), con p = número de pedidos activos
- Impacto: Ligero si la cantidad de pedidos es moderada; se ignoran pedidos no liberados, reduciendo la carga.
**Navegación y selección de inventario**
- Tipo: Listas lineales para vistas de inventario (normal, prioridad, deadline)
- Complejidad: Acceso al pedido actual: O(1)
Siguiente/anterior: O(n_vista), n_vista = número de pedidos en la vista actual
Ordenamiento (insertion sort): O(n_vista²)
- Impacto: Operaciones rápidas para inventarios pequeños; ordenar vistas grandes puede ser costoso pero es poco frecuente.
**Interacción con pedidos (recoger/entregar)**
- Tipo: Iteración lineal sobre lista de pedidos y comparación de posiciones adyacentes
- Complejidad: O(p) por intento de interacción
- Impacto: Ligero para un número moderado de pedidos; la lógica se detiene al encontrar el primer pedido válido.
**Cálculo de puntaje y bonificaciones**
- Tipo: Secuencia de multiplicaciones y condiciones para tiempo, reputación y bonificaciones
- Complejidad: O(1)
- Impacto: Muy eficiente, no afecta rendimiento por frame.
**Actualización del clima y multiplicadores**
- Tipo: Acceso a variables y cálculos lineales
- Complejidad: O(1)
- Impacto: Muy eficiente, escala constante por frame.
**Comprobación de fin de juego**
- Tipo: Condicionales y all() sobre pedidos
- Complejidad: O(p) para verificar si todos los pedidos fueron entregados
- Impacto: Ligero; la función se ejecuta una vez por tick y termina rápido.


# Fecha de entrega: 28 de septiembre de 2025
# Nueva Fecha de entrega: 5 de octubre de 2025
___________________________________________________________________________________________________________

# Proyecto II

## Clase "pahtfinding_A"
Implementa el algoritmo de búsqueda A* para encontrar la ruta más corta entre dos posiciones del mapa.

**Estructuras:**
- Heapq como min-heap para la lista de nodos abiertos
- dict para g_score, f_score_map y came_from
- Tuplas (x, y) como claves hashables
- Lista resultante para reconstrucción del camino

**Algoritmos:**
- A* con heurística Manhattan
- Uso de priority queue para seleccionar el nodo más prometedor
- Reconstrucción de ruta mediante backtracking

**Complejidad:**
- Tiempo: O(V log V) donde V = ancho × alto del mapa
- Memoria: O(V)
- Reconstrucción del camino: O(L) donde L es la longitud final de la ruta

**Impacto:**
- Muy eficiente para mapas medianos.
- Escala bien gracias al heap; solo se vuelve costoso en mapas extremadamente grandes o si se ejecuta cada frame.

## Clase "repartidor_IA"
La clase RepartidorIA implementa 3 niveles de dificultad que combinan pathfinding, heurísticas y movimiento probabilístico.

**Estructuras:**
- Listas para rutas, posibles movimientos, pedidos válidos
- Tuplas usadas para posiciones (x, y)
- Diccionarios map score de A*
- Strings para los estados internos de la IA

**Algoritmos:**
- A* para calcular rutas óptimas (recogida y entrega)
- Algoritmo Greedy para seleccionar pedidos en dificultad media
- Algoritmo heurístico de optimización en dificultad difícil
- Movimiento aleatorio ponderado para IA fácil
- Reconstrucción de ruta mediante lista FIFO

**Complejidad:**
- Fácil: O(1) por tick
- Media: O(P × V log V)
- Difícil: O(P × V log V) (con mayor carga)
- Seguimiento de ruta: O(L)

**Impacto en el juego:**
- La IA fácil casi no consume recursos; la IA media y difícil realizan múltiples ejecuciones del algoritmo A*, por lo que el costo crece con el tamaño del mapa y el número de pedidos activos.

## Clase "pantalla_jugar:"
**Estructuras de datos:**
- Listas de botones
- Diccionarios para atributos
- Rectángulos de pygame

**Algoritmos:**
- Recorrido lineal de botones
- Detección de colisión punto-rectángulo
- Renderizado iterativo

**Complejidad:**
- Por evento: O(n)
- Por frame: O(n)
(Excelente para una UI pequeña-mediana)

**Impacto:**
- Muy eficiente y fácil de mantener
- Se adapta bien a pantallas de menú típicas


# Fecha de entrega proyecto #2:  17 de noviembre 2025