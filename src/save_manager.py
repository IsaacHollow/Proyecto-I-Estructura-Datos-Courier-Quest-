import pickle
from pathlib import Path
from typing import Optional
from src.estado_juego import EstadoJuego


class SaveManager:
    def __init__(self, save_dir="saves"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)

    def guardar_partida(self, estado: EstadoJuego, slot: int):
        save_path = self.save_dir / f"slot{slot}.sav"
        try:
            with open(save_path, "wb") as f:
                pickle.dump(estado, f)
            return True
        except Exception as e:
            print(f"Error al guardar la partida en '{save_path}': {e}")
            return False

    def cargar_partida(self, slot: int) -> Optional[EstadoJuego]:
        save_path = self.save_dir / f"slot{slot}.sav"
        if not save_path.exists():
            return None

        try:
            with open(save_path, "rb") as f:
                estado = pickle.load(f)
            return estado
        except (pickle.UnpicklingError, AttributeError, EOFError, ImportError, IndexError) as e:
            print(f"Error al cargar la partida desde '{save_path}': {e}. El archivo puede ser de una versión anterior o estar corrupto.")
            return None
        except Exception as e:
            print(f"Error inesperado al cargar la partida: {e}")
            return None

    def existe_guardado(self, slot: int) -> bool:
        return (self.save_dir / f"slot{slot}.sav").exists()