# utils/ejercicio_enum.py
# -------------------------------
# Requierements
# -------------------------------
from enum import Enum

# -------------------------------
# Helpers
# -------------------------------

class EjercicioId(str, Enum):
    CURL_BICEP = "curl_bicep"
    SENTADILLA = "sentadilla"
    FLEXION = "flexion"
    PRESS_MILITAR = "press_militar"
    EXTENSION_CUADRICEP = "extension_cuadricep"
    CRUNCH_ABDOMINAL = "crunch_abdominal"
    DIP_TRICEP = "dip_tricep"
    ELEVACION_LATERAL = "elevacion_lateral"
