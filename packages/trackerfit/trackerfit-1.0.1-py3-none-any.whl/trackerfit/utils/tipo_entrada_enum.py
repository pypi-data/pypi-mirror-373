# utils/tipo_entrada_enum.py
# -------------------------------
# Requierements
# -------------------------------
from enum import Enum

# -------------------------------
# Helpers
# -------------------------------

class TipoEntrada(str, Enum):
    CAMARA = "camera"
    VIDEO = "video"
