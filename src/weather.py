# src/weather.py
import random

class Clima:
    """
    Clase para controlar el clima:
    - Cambia cada 45-60 s según una matriz de probabilidad.
    - Cada clima tiene una intensidad 0..1.
    - Hay transiciones suaves de 3..5 s.
    """

    ESTADOS = [
        "despejado", "nublado", "llovizna", "lluvia",
        "tormenta", "niebla", "viento", "calor", "frio"
    ]

    MATRIZ = {
        "despejado": {"despejado": 0.6, "nublado": 0.25, "viento": 0.1, "llovizna": 0.05},
        "nublado":   {"nublado": 0.6, "despejado": 0.25, "llovizna": 0.1, "niebla": 0.05},
        "llovizna":  {"llovizna": 0.6, "lluvia": 0.3, "nublado": 0.1},
        "lluvia":    {"lluvia": 0.6, "llovizna": 0.25, "tormenta": 0.1, "nublado": 0.05},
        "tormenta":  {"tormenta": 0.7, "lluvia": 0.2, "viento": 0.1},
        "niebla":    {"niebla": 0.7, "nublado": 0.3},
        "viento":    {"viento": 0.7, "despejado": 0.2, "tormenta": 0.1},
        "calor":     {"calor": 0.7, "despejado": 0.3},
        "frio":      {"frio": 0.7, "despejado": 0.3},
    }

    MULT_VELOCIDAD = {
        "despejado": 1.00, "nublado": 0.98, "llovizna": 0.90,
        "lluvia": 0.85, "tormenta": 0.75, "niebla": 0.88,
        "viento": 0.92, "calor": 0.90, "frio": 0.92
    }

    EXTRA_RES = {
        "despejado": 0.0, "nublado": 0.0, "llovizna": 0.1,
        "lluvia": 0.1, "tormenta": 0.3, "niebla": 0.0,
        "viento": 0.1, "calor": 0.2, "frio": 0.0
    }

    def __init__(self):
        self.estado_actual = "despejado"
        self.intensidad = 0.0  # 0..1
        self.tiempo_rafaga = random.uniform(45.0, 60.0)

        # transición
        self.transicion = False
        self.estado_viejo = self.estado_actual
        self.estado_nuevo = None
        self.t_trans = 0.0
        self.duracion_trans = 0.0
        self.intensidad_vieja = self.intensidad

        # multiplicador inicial
        self.mult_actual = self.MULT_VELOCIDAD[self.estado_actual]

    def _elegir_siguiente(self):
        probs = self.MATRIZ.get(self.estado_actual, {self.estado_actual: 1.0})
        estados = list(probs.keys())
        pesos = list(probs.values())
        return random.choices(estados, weights=pesos, k=1)[0]

    def _multiplicador_estado(self, estado, intensidad):
        base = self.MULT_VELOCIDAD.get(estado, 1.0)
        return base - (1.0 - base) * intensidad

    def actualizar(self, dt):
        """Actualiza el clima en función del tiempo (segundos)."""
        if self.transicion:
            self.t_trans += dt
            t = min(self.t_trans / self.duracion_trans, 1.0)
            prev_mult = self._multiplicador_estado(self.estado_viejo, self.intensidad_vieja)
            target_mult = self._multiplicador_estado(self.estado_nuevo, self.intensidad)
            self.mult_actual = prev_mult + (target_mult - prev_mult) * t
            if t >= 1.0:
                self.transicion = False
                self.estado_actual = self.estado_nuevo
                self.estado_viejo = self.estado_actual
                self.tiempo_rafaga = random.uniform(45.0, 60.0)
                self.mult_actual = self._multiplicador_estado(self.estado_actual, self.intensidad)
        else:
            self.tiempo_rafaga -= dt
            if self.tiempo_rafaga <= 0.0:
                siguiente = self._elegir_siguiente()
                self.estado_nuevo = siguiente
                self.intensidad_vieja = self.intensidad
                self.intensidad = random.uniform(0.0, 1.0)
                self.transicion = True
                self.t_trans = 0.0
                self.duracion_trans = random.uniform(3.0, 5.0)
                self.estado_viejo = self.estado_actual

    def obtener_multiplicador(self):
        """Devuelve el multiplicador actual de velocidad."""
        return self.mult_actual

    def obtener_extra_resistencia(self):
        """Extra de consumo de resistencia por celda."""
        estado = self.estado_nuevo if (self.transicion and self.t_trans > 0) else self.estado_actual
        base = self.EXTRA_RES.get(estado, 0.0)
        return base * (1.0 + self.intensidad)

    def estado_y_intensidad(self):
        """Devuelve el estado en español y su intensidad (0..1)."""
        if self.transicion and self.estado_nuevo:
            return f"{self.estado_viejo} → {self.estado_nuevo}", self.intensidad
        return self.estado_actual, self.intensidad
