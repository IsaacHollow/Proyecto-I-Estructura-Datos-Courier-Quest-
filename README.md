# Proyecto-I-Estructura-Datos-Courier-Quest-
# Courier Quest — EIF-207 (Ciclo II, 2025)

Deben	 incluir	 un	 archivo	 README.md	 con	 información	 general	 del	 proyecto,	
incluyendo	las	estructuras	de	datos	que	utilizaron	y	para	qué	partes	del	programa.	
Así	como	detalles	de	la	complejidad	algorítmica	


# Equipo:

Isaac Sibaja Cortes
Gabriel Quiros Villalobos
Hernán Sánchez Chaves

___________________________________________________________________________________________________

# Libreria escogida:
Pygame

# Motivo:  
Despues de mirar varias opciones como Arcade o cocos2d, 
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

# Estructuras y rendimiento del juego:

# Clase "Inventario"
Gestiona los pedidos que el repartidor puede cargar y entregar.

**Estructuras** 
  "List[Pedido]": para almacenar pedidos  
  cursor: int` para el pedido actualmente seleccionado  
**Operaciones:**  
  Agregar pedido: O(1)  
  Entregar pedido: O(n)  
  Obtener pedido actual: O(1)  
  Ordenar vistas por prioridad/deadline: O(n²) (`insertion sort`)  
**Impacto:**  
  Operaciones rápidas para inventarios pequeños.  
  Mayor tiempo de corrida al ordenar vistas con listas grandes.  
-----------------------------------------------------------------------------------------------------------
# Clase "Repartidor"
Representa al jugador y su bicicleta, controla movimiento, resistencia y velocidad.

**Estructuras:**  
  Variables escalares (`float`, `int`) para posición, resistencia, reputación  
  `Inventario` para pedidos  
  Rectángulos de Pygame (`pygame.Rect`) para colisiones  
**Operaciones:**  
  Movimiento: O(1) por tick, velocidad calculada con multiplicadores de clima, peso, reputación y terreno  
  Recuperación de resistencia: O(1)  
**Impacto:**  
  Lógica eficiente, sin impacto visible en FPS incluso con varios pedidos  
  Actualización de velocidad y resistencia es constante por frame  
-----------------------------------------------------------------------------------------------------------
# Clase "Pedido"
Define los pedidos a entregar.

**Estructuras:**  
  Dataclass con atributos simples (`int`, `float`, `tuple`)  
  `pygame.Surface` opcional para sprites  
**Operaciones:**  
  Calcular tiempo restante: O(1)  
  Determinar prioridad: O(1)  
**Impacto:**  
  Muy ligera, sin impacto en rendimiento  
-----------------------------------------------------------------------------------------------------------

# Clase "Weather / Clima"
Gestiona condiciones climáticas y multiplicadores de velocidad/resistencia.

**Estructuras:**  
  Diccionarios para probabilidades de transición (`dict[str, dict[str, float]]`)  
  Variables escalares para intensidad y multiplicadores  
**Operaciones:**  
  Actualización por tick: O(1)  
  Cálculo de multiplicador y resistencia extra: O(1)  
**Impacto:**  
  Ligero y eficiente, escala lineal con el tiempo de tick  
-----------------------------------------------------------------------------------------------------------

# Clase "CityMap / Tile"
Representa el mapa y los tipos de terreno.

**Estructuras:**  
  `List[List[Tile]]` para las celdas del mapa  
  `TileType` para propiedades de terreno  
**Operaciones:**  
  Acceso a celdas por índice: O(1)  
  Iteración para render o colisiones: O(n*m) con n=width, m=height  
**Impacto:**  
  Renderizado y colisiones son la operación más costosa, pero manejable en mapas moderados  
-----------------------------------------------------------------------------------------------------------
# Clase "Camera"
Controla el seguimiento del repartidor y el desplazamiento de la vista.
**Estructuras:**  
  Variables escalares para offset y zoom  
**Operaciones:**  
  Centrar sobre objetivo: O(1)  
  Aplicar offset a posición: O(1)  
**Impacto:**  
  Muy eficiente, sin impacto notable en FPS  
-----------------------------------------------------------------------------------------------------------

# Clase "MenuPrincipal"
Muestra los botones del menú y maneja navegación.

**Estructuras:**  
  Lista de diccionarios con rectángulos y callbacks (`List[dict]`)  
**Operaciones:**  
  Hover y click: O(n_botones) por tick  
**Impacto:**  
  Ligero, incluso con 5–10 botones, no afecta rendimiento  
___________________________________________________________________________________________________________


# Fecha de entrega: 28 de septiembre de 2025
# Nueva Fecha de entrega: 5 de octubre de 2025
