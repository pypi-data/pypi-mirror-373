# ejercicios/press_militar.py
# -------------------------------
# Requierements
# -------------------------------
from trackerfit.ejercicios.ejercicio import Ejercicio
from trackerfit.utils.tipo_esfuerzo_enum import TipoEsfuerzo
from trackerfit.utils.lado_enum import Lado
# -------------------------------
# Helpers
# -------------------------------

class PressMilitar(Ejercicio):
    """
    Implementación del ejercicio 'Press Militar'.
    Calcula el ángulo entre codo, hombro y cadera para validar el levantamiento por encima de la cabeza.
    """
    def __init__(self,lado: Lado = Lado.derecho):
        if(lado==Lado.derecho):
            puntos=(14,12,24) # Codo (der) = 14, # Hombro (der) = 12, Cadera (der) = 24
        else:
            puntos=(13,11,23) # Codo (izq) = 13, # Hombro (izq) = 11, Cadera (izq) = 23

        super().__init__(angulo_min=80 ,angulo_max=140,puntos=puntos, tipo_esfuerzo=TipoEsfuerzo.AMPLITUD)
        self.umbral_validacion = self.angulo_max