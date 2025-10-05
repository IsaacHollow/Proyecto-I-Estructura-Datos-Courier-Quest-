import requests
import random
import json
import os

API_URL = "https://tigerds-api.kindflower-ccaf48b6.eastus.azurecontainerapps.io/city/weather?mode=seed"
LOCAL_FILE = "assets/weather.json"

class Weather:
    def __init__(self):
        data = None
        try:
            resp = requests.get(API_URL, timeout=5)
            if resp.status_code == 200:
                data = resp.json().get("data", None)
        except Exception:
            pass

        if data is None:
            if os.path.exists(LOCAL_FILE):
                with open(LOCAL_FILE, "r", encoding="utf-8") as f:
                    contenido = json.load(f)
                    data = contenido["data"]
            else:
                data = {
                    "conditions": ["clear", "clouds", "rain", "storm", "fog"],
                    "transition": {"clear": {"clear": 1.0}},
                    "initial": {"condition": "clear", "intensity": 0.0},
                }

        self.condiciones_disponibles = data["conditions"]
        self.transiciones = data["transition"]
        initial = data["initial"]

        self.estado_actual = initial["condition"]
        self.intensidad = initial["intensity"]

        self.estado_objetivo = self.estado_actual
        self.intensidad_objetivo = self.intensidad

        self.tiempo_transicion = 0.0
        self.duracion_transicion = 3.0
        self.tiempo_burst = random.uniform(10.0, 20.0)

        self.multiplicadores = {
            "clear": 1.00, "clouds": 0.98, "rain_light": 0.90,
            "rain": 0.85, "storm": 0.75, "fog": 0.88,
            "wind": 0.92, "heat": 0.90, "cold": 0.92
        }

    def actualizar(self, dt):
        self.tiempo_burst -= dt
        if self.tiempo_burst <= 0:
            self.elegir_nuevo_estado()
            self.tiempo_burst = random.uniform(10.0, 20.0)
        if self.tiempo_transicion > 0:
            progreso = min(1.0, dt / self.tiempo_transicion)
            self.intensidad += progreso * (self.intensidad_objetivo - self.intensidad)
            self.tiempo_transicion -= dt
        else:
            self.intensidad = self.intensidad_objetivo
            self.estado_actual = self.estado_objetivo

    def elegir_nuevo_estado(self):
        posibles = self.transiciones.get(self.estado_actual, {"clear": 1.0})
        estados = list(posibles.keys())
        probs = list(posibles.values())
        nuevo_estado = random.choices(estados, weights=probs)[0]
        self.estado_objetivo = nuevo_estado
        self.intensidad_objetivo = random.uniform(0.4, 1.0)
        self.tiempo_transicion = self.duracion_transicion

    def obtener_estado_y_intensidad(self):
        return self.estado_actual, self.intensidad

    def obtener_multiplicador(self):
        m_actual = self.multiplicadores.get(self.estado_actual, 1.0)
        m_objetivo = self.multiplicadores.get(self.estado_objetivo, 1.0)
        if self.tiempo_transicion > 0:
            factor = 1 - (self.tiempo_transicion / self.duracion_transicion)
            return m_actual + factor * (m_objetivo - m_actual)
        return m_actual

    def obtener_extra_resistencia(self):
        clima = self.estado_actual
        if clima == "rain_light":
            return 0.05
        elif clima == "rain":
            return 0.1
        elif clima == "storm":
            return 0.2
        elif clima in ["heat", "cold", "wind", "fog"]:
            return 0.1
        return 0.0
