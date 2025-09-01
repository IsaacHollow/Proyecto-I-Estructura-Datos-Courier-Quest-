
class Pedido:
    def __init__(self):
        self.id = ""          # ID del pedido
        self.priority = 0     # Prioridad
        self.payout = 0       # Pago
        self.weight = 0       # Peso
        self.deadline = ""    # Fecha límite (string ISO)
        self.release_time = 0 # Tiempo de liberación en segundos
        self.pickup = [0, 0]  # Coordenadas recogida
        self.dropoff = [0, 0] # Coordenadas entrega

