import pickle
from pathlib import Path
from typing import Optional
from src.estado_juego import EstadoJuego


class SaveManager:
    def __init__(self, save_dir="saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

    def guardar_partida(self, estado: EstadoJuego, slot: int):
        """
        Guarda el estado del juego en un archivo binario.
        """
        save_path = self.save_dir / f"slot{slot}.sav"
        try:
            with open(save_path, "wb") as f:
                pickle.dump(estado, f)
            print(f"Partida guardada exitosamente en {save_path}")
            return True
        except Exception as e:
            print(f"Error al guardar la partida: {e}")
            return False

    def cargar_partida(self, slot: int) -> Optional[EstadoJuego]:
        """
        Carga el estado del juego desde un archivo binario.
        """
        save_path = self.save_dir / f"slot{slot}.sav"
        if not save_path.exists():
            print(f"No se encontró ninguna partida guardada en el slot {slot}.")
            return None

        try:
            with open(save_path, "rb") as f:
                estado = pickle.load(f)
            print(f"Partida cargada exitosamente desde {save_path}")
            return estado
        except Exception as e:
            print(f"Error al cargar la partida: {e}")
            return None

    def existe_guardado(self, slot: int) -> bool:
        """Verifica si existe un archivo de guardado para un slot."""
        return (self.save_dir / f"slot{slot}.sav").exists()