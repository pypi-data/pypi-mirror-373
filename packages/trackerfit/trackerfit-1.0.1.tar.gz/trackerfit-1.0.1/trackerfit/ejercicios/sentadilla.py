# ejercicios/sentadilla.py
# -------------------------------
# Requierements
# -------------------------------
from trackerfit.ejercicios.ejercicio import Ejercicio
from trackerfit.utils.tipo_esfuerzo_enum import TipoEsfuerzo
from trackerfit.utils.lado_enum import Lado
# -------------------------------
# Helpers
# -------------------------------

class Sentadilla(Ejercicio):
    """
    Implementación del ejercicio 'Sentadilla'.
    Calcula el ángulo entre cadera, rodilla y tobillo para contar repeticiones al descender completamente.
    """
    def __init__(self,lado: Lado = Lado.derecho):
        if(lado==Lado.derecho):
                puntos = (24,26,28) # Cadera (der) = 24 , Rodilla (der) = 26 y Tobillo(der) = 28
        else:
            puntos = (23,25,27) # Cadera (der) = 23 , Rodilla (der) = 25 y Tobillo(der) = 27

        super().__init__(angulo_min=80,angulo_max=150,puntos=puntos, tipo_esfuerzo=TipoEsfuerzo.CONTRACCION)
        self.umbral_validacion = self.angulo_min