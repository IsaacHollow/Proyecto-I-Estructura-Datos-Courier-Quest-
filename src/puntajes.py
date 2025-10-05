import json
from datetime import datetime
from pathlib import Path

class ScoreManager:
    def __init__(self, file_path="puntajes.json"):
        self.file_path = Path(file_path)
        self.scores = self._load_scores()

    def _load_scores(self):
        if not self.file_path.exists():
            return []
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("scores", [])
        except json.JSONDecodeError:
            return []

    def _save_scores(self):
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump({"scores": self.scores}, f, indent=4, ensure_ascii=False)

    def agregar_puntaje(self, puntaje: int, resultado: str):
        """Guarda un nuevo puntaje con fecha y resultado (victoria/derrota)."""
        nuevo = {
            "puntaje": puntaje,
            "resultado": resultado,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.scores.append(nuevo)
        self.scores.sort(key=lambda x: x["puntaje"], reverse=True)
        self.scores = self.scores[:20]
        self._save_scores()

    def obtener_top(self, n=10):
        return self.scores[:n]