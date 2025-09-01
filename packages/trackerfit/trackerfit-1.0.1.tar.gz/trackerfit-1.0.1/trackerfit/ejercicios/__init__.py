# ejercicios/__init__.py
# -------------------------------
# Requierements
# -------------------------------
from .curl_bicep import CurlBicep
from .sentadilla import Sentadilla
from .flexion import Flexion
from .extension_cuadricep import ExtensionCuadricep
from .press_militar import PressMilitar
from .crunch_abdominal import CrunchAbdominal
from .dip_tricep import DipTricep
from .elevacion_lateral import ElevacionLateral
from .ejercicio import Ejercicio
# -------------------------------
# Helpers
# -------------------------------
__all__ = [
    "CurlBicep", "Sentadilla", "Flexion", "ExtensionCuadricep", "PressMilitar",
    "CrunchAbdominal", "DipTricep", "ElevacionLateral", "Ejercicio"
]
