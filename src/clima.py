
class Clima:
    def __init__(self, temperatura, humedad, presion):
        self.condition = "Clouds"
        self.intensity = 0
        self.conditions = [ "clear", "clouds",
                            "rain_light", "rain",
                            "storm", "fog", "wind",
                            "heat", "cold" ]
        
