
# Aca vamos a ir agregando los prompts de IA que vamos a usar
# Recuerden que se penalizara la copia directa sin explicacion del codigo



   # Prompts de IA 


-Para el renderizado del mapa:

	"Quiero renderizar un mapa en pygame basado en casillas, para ello importo un mapa desde un API que tiene forma de matriz, este especifica el tipo de casilla con distintos atributos para luego cargar un sprite diferente segun su tipo, como puedo renderizar un mapa así usando pygame?"

-Para la cámara:

	"Tengo este codigo para una camara que sigue al jugador con zoom tomada de un tutorial de youtube:[código, enlace del video en la bitacora] como puedo adaptar dicho codigo a mi proyecto sobre un repartidor por una ciudad donde el mapa está hecho como una matriz de tiles, en que afecta esto a la implementacion de la camara?"


-Para el movimiento del jugador tuvimos un problema, ya que lo habíamos implementado por pixeles por segundo y no en casillas por segundo:

	"Para mi proyecto sobre un juego de repartidor de paquetes en una ciudad, el movimiento debe de ser por casillas, pero lo implementé por pixeles, como puedo revertir esto y convertir el movimiento a movimiento por casillas, manteniendo la logica del programa y las colisiones con los edificios a como están actualmente"

Para este prompt se utilizo bastante inspiración de los ejemplos dados por la IA, por lo que se le preguntó por explicación mas a fondo, el sistema recomendado fue de movimiento entre casillas, donde el personaje se desplaza de una casilla a otra y en medio de ellas no se pueden realizar acciones.


Se pidió recomendación para mostrar ubicación de entrega:

	"Quiero que al recoger un pedido se muestre la posicion donde se debe de entregar, para ello quiero mostrar una indicacion en la casilla donde se debe entregar cada paquete, que me recomiendas? ya sea un sprite diferente, un simbolo, una señal o algo parecido, que se ajusta mejor a mi proyecto?"

Luego de esto decidimos utilizar el Sprite de pedido pero con un tono rojizo.


Para un reajuste en como se muestra el inventario:

    "Para mi proyecto sobre un juego de repartidor, quiero agregar un inventario que muestre informacion sobre los pedidos, esta es mi clase de inventario actual: [código del inventario hasta ese momento], a la hora de dibujar el inventario, quiero que tenga un formato tipo columna para que el jugador pueda identificar cada parte de la informacion"

También había un problema con como se mostraba el tiempo negativo de los pedidos:

    "Tengo un problema con el inventario, si el deadline es menor a 0 muestra -1 day, quiero que se muestre un contador de segundos negativos para saber que tan atrasado está el jugador, como puedo convertirlo?"

Para el inventario se pidió ayuda para la lógica de recorrer y elegir dentro del inventario:

    "Para el inventario, como puedo hacer que el jugador seleccione pedidos de la lista presionando ciertas teclas, quiero que dentro del inventario se resalte el pedido seleccionado como si fuese un cursor de seleccion"

En este prompt también se tomo bastante de los ejemplos de IA pues habían ciertos problemas a la hora de reajustar el cursor, por lo que se pidió amplia explicación del código, aquí un resumen dado por la IA:

    "La idea central es la siguiente:

    El self.cursor siempre será un índice que apunta a un elemento en la lista original y sin ordenar (self.pedidos).
    Los métodos siguiente y anterior ahora son más inteligentes: calculan el movimiento del cursor basándose en la lista ordenada que el jugador está viendo (vista_actual), pero al final actualizan el self.cursor para que apunte al pedido correcto en la lista original."



Para cargar los pedidos del API se pidió bastante explicación, aquí un resumen de la información tomada de la IA:

"

    Obtención de Datos Crudos:

    La función comienza haciendo una petición HTTP GET a la url que se le pasa como argumento.
    Verifica que la petición fue exitosa (código 200 OK). Si no, lanza un error.
    Extrae los datos de los pedidos del JSON, que se encuentran bajo la clave "data".

    Creación de Objetos Pedido Iniciales:

    Itera sobre cada "pedido" en los datos crudos.
    Crea un objeto Pedido para cada uno. En esta etapa, el deadline sigue siendo una cadena de texto (ej: "2025-09-01T12:10Z"), tal como viene de la API.

    Normalización de Tiempos (La parte clave):

    Encontrar el Punto de Inicio: El código necesita establecer un "tiempo cero" para la partida. Para hacerlo, recorre todos los pedidos y convierte sus deadline (que son strings) en timestamps numéricos (segundos desde 1970).
    Establecer start_time: Una vez tiene todos los timestamps de los deadlines, busca el más bajo (el más temprano en el tiempo). Este valor se convierte en el start_time de la sesión de juego. Este es el punto que causa el problema que notaste: el juego empieza a contar desde el momento en que el primer paquete debe ser entregado.
    Calcular Deadlines Relativos: Vuelve a recorrer los pedidos y, para cada uno, calcula su nuevo deadline como la diferencia en segundos entre su deadline original y el start_time que se acaba de encontrar. El resultado es un número entero que representa cuántos segundos tiene el jugador desde el inicio de la partida para entregar ese pedido."


Para el modo offline del API en caso de fallo se pidió una explicación de las instrucciones y como funcionaba esto adaptado al programa:

    "Para este proyecto sobre un juego de repartidor debo de cargar datos de un API (eso ya está implementado) pero tambien se dan estas instrucciones:
    Ante fallo del API, cargar archivos locales equivalentes:
    /data/ciudad.json,
    /data/pedidos.json,
    /data/weather.json
    Guardar copias cacheadas de respuestas en /api_cache con fecha/hora.Si no hay conexión al
    API server, se utiliza la última versión.
    
    que quiere decir todo esto y como podría implementarlo en mi programa"

Todo el sistema de cache fue implementado en base a las explicaciones dadas por este prompt.

Para la persistencia de datos se pidió una recomendación para guardar el estado actual del juego:

    "En mi proyecto sobre un juego de repartidor debe existir una opción para guardar el juego con el estado actual en cualquier
    momento, así como una opción para cargar una partida guardada. 
    puedes darme una idea de como guardar el estado actual del juego? esto incluye posicion actual del jugador, su inventario, los pedidos entregados y los que aun están por salir, la puntuacion conseguida hasta ese momento y el tiempo transcurrido"

Para el guardado no hubo mayor problema, excepto por un problema de la librería Pickle que desconocíamos, no podía guardar objetos de pygame tipo Surface, por lo que le pedimos ayuda a IA para solucionarlo:

    "al guardar recibo este error:
    Error al guardar la partida: cannot pickle 'pygame.surface.Surface' object"

Nos recomendó eliminar ese objeto del diccionario donde guardábamos los datos actuales, sobrescribiendo los métodos __setstate__ y __getstate__ de los pedidos y el repartidor, estos métodos fueron copiados directamente de los ejemplos dados por IA

Para la logica de la reputacion:

    "Necesito implementar un sistema de reputacion en mi juego de un repartidor, 
    donde la reputacion empieza en 70 y cambia con base en el rendimiento y las entregas a tiempo,
    tardias y canceladas. Si baja de 20 el jugador pierde, y si es excelente (≥90) obtiene 5% extra de pago.
    Como puedo implementarlo? sin darme codigo, solo explicacion."

Para la logica del clima:

    "Quiero implementar un sistema de clima dinamico en mi juego hecho con pygame,
    que cambie automaticamente entre diferentes estados como sol, lluvia, nubes, tormenta, etc.
    La idea es que el cambio sea suave y tenga diferentes niveles de intensidad.
    Como puedo hacer para que el clima cambie cada cierto tiempo sin afectar el rendimiento
    ni que se vea brusco? no quiero codigo, solo que me lo expliques bien."

Problemas en la logica del clima:

A veces el clima no cambiaba aunque pasara el tiempo que yo queria, 
entonces pregunte que podia estar pasando o si habia que reiniciar algun contador o variable despues del cambio.

Tambien me paso que cuando cambiaba el clima se notaba un salto muy brusco, como si no hiciera la transicion,
asi que pedi que me explicaran como suavizar ese cambio sin tener que rehacer todo el sistema.

Para los efectos visuales del clima:

    "Ya tengo el sistema de clima pero queria que se viera mas bonito,
    por ejemplo que cuando este despejado se vea un tono amarillo o anaranjado,
    cuando llueva se vea algo azul, o cuando haya tormenta se vea mas oscuro. 
    Entonces pregunte cuales son los codigos de colores que se pueden usar en pygame para eso,
    y como se pueden poner como una capa encima sin tapar todo el mapa."

Tambien pregunte como hacer que esos efectos se vean mas suaves, por ejemplo que el color no tape de golpe
sino que se mezcle un poco con la pantalla para que parezca mas realista, sin que se trabe el juego.

Para la musica de todas las ventanas:

     "Queria poner una musica diferente en cada pantalla, por ejemplo una en el menu principal, 
     otra cuando el jugador gana o pierde y otra en el mapa, pero se me quedaban sonando dos al 
     mismo tiempo o no se pausaban bien.
     Pregunte como puedo manejar eso para que cada cancion se detenga justo al cambiar de pantalla,
     pero sin que me den codigo, solo explicacion."

Problemas a la hora de pausar la musica:

A veces cuando pausaba el juego y luego lo reanudaba la musica seguia 
desde otro punto o se escuchaba doble, entonces pedi que me explicaran como puedo pausar y reanudar 
la musica sin que se buguee ni empiece de nuevo.

Para la creacion de las ventanas de creditos, victoria, derrota, etc:

Pregunte como podia hacer las ventanas de creditos, victoria, derrota y puntaje sin repetir tanto codigo, porque todas se parecian mucho y tenian los mismos botones."

Tambien pedi que me explicaran como puedo hacer para que esas pantallas se carguen mas rapido 
y no tenga que reiniciar todo el juego cada vez que paso de una a otra."

Otra pregunta que hice fue como podia agregar animaciones o efectos sencillos 
(por ejemplo que el texto aparezca de a poco o se mueva) pero sin que el rendimiento del juego baje mucho,
solo con la logica.



# Youtube
https://youtu.be/31TNvxUkFAc?si=Xv6GAMpllfB1ig53

https://www.youtube.com/watch?v=OvbOKNGZvoc

https://www.youtube.com/watch?v=J3gZDqkk72Q


# Camaras en pygame:
https://www.youtube.com/watch?v=u7LPRqrzry8

# Colisiones en pygame:
https://www.youtube.com/watch?v=BHr9jxKithk


# Sitios Web
https://www.pygame.org/docs/tut/newbieguide.html

https://www.geeksforgeeks.org/python/pygame-tutorial/

https://www.w3schools.com/python/python_dsa_insertionsort.asp

Para el metodo _get_data_with_cache() de apy_client.py utilizamos sorted() según recomendaciones de IA:

https://www.w3schools.com/python/ref_func_sorted.asp
https://docs.python.org/3/library/functions.html#sorted

