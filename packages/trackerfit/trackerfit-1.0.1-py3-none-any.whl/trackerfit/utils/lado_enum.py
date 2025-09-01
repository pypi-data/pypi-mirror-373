# utils/lado_enum.py
# -------------------------------
# Requierements
# -------------------------------
from enum import Enum

# -------------------------------
# Helpers
# -------------------------------

class Lado(str, Enum):
    derecho = "derecho"
    izquierdo = "izquierdo"
