# ejercicios/curl_bicep.py
# -------------------------------
# Requierements
# -------------------------------
from trackerfit.ejercicios.ejercicio import Ejercicio
from trackerfit.utils.tipo_esfuerzo_enum import TipoEsfuerzo

# -------------------------------
# Helpers
# -------------------------------
class CurlBicep(Ejercicio):
    """
    Implementación del ejercicio 'Curl de Bíceps'.
    Calcula el ángulo entre hombro, codo y muñeca para contar repeticiones.
    """
    def __init__(self, lado='derecho'):
        if lado == 'derecho':
            puntos = (12, 14, 16) # Hombro (der) = 12, # Codo (der) = 14, Muñeca (der) = 16
        else:
            puntos = (11, 13, 15) # Hombro (izq) = 11, # Codo (izq) = 13, Muñeca (izq) = 15

        super().__init__(angulo_min=45, angulo_max=160, puntos=puntos, tipo_esfuerzo=TipoEsfuerzo.CONTRACCION)
        self.umbral_validacion = self.angulo_min