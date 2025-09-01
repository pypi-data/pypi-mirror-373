# session/session.py
# -------------------------------
# Requierements
# -------------------------------

from abc import ABC, abstractmethod
from typing import Optional

# -------------------------------
# Helpers
# -------------------------------

class Session(ABC):
    @abstractmethod
    def iniciar(self, nombre_ejercicio: str, fuente: Optional[str] = None):
        """
        Inicia la sesión (cámara o vídeo).

        Args:
            nombre_ejercicio (str): Nombre del ejercicio a contar.
            fuente (Optional[str]): Fuente de entrada. Puede ser None para cámara (por defecto) o path para vídeo.
        """
        pass

    @abstractmethod
    def finalizar(self):
        """
        Detiene la sesión y libera recursos.
        """
        pass

    @abstractmethod
    def get_repeticiones(self) -> int:
        """
        Devuelve el número actual de repeticiones contadas.
        """
        pass