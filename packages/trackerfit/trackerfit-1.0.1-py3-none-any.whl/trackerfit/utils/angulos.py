# utils/angulos.py
# -------------------------------
# Requierements
# -------------------------------

from math import acos, degrees
import numpy as np

# -------------------------------
# Helpers
# -------------------------------

def calcular_angulo(p1, p2, p3) -> float:
    """
    Calcula el ángulo (en grados) entre tres puntos en 2D.

    El ángulo se calcula en el vértice p2 formado por los segmentos p1-p2 y p3-p2.

    Args:
        p1 (tuple): Coordenadas (x, y) del primer punto.
        p2 (tuple): Coordenadas (x, y) del punto central.
        p3 (tuple): Coordenadas (x, y) del tercer punto.

    Returns:
        float: Ángulo en grados.
    """
    a = np.array(p1, dtype=float)
    b = np.array(p2, dtype=float)
    c = np.array(p3, dtype=float)

    ba = a - b
    bc = c - b
    
    nba = _normalizar(ba)
    nbc = _normalizar(bc)
    
    if nba == 0.0 or nbc == 0.0:
        return None
    
    coseno = np.dot(ba, bc) / (nba * nbc)
    coseno = np.clip(coseno, -1.0, 1.0)
    angulo = degrees(acos(coseno))
    return angulo

def calcular_angulo_landmarks(puntos: dict, id1: int, id2: int, id3: int) -> float:
    """
    Calcula el ángulo (en grados) entre tres landmarks dados por sus IDs.

    Extrae los puntos del diccionario de landmarks detectados por MediaPipe.

    Args:
        puntos (dict): Diccionario con coordenadas de los landmarks.
        id1, id2, id3 (int): IDs de los puntos a usar.

    Returns:
        float: Ángulo en grados.
    """
    p1 = (puntos[id1]['x'], puntos[id1]['y'])
    p2 = (puntos[id2]['x'], puntos[id2]['y'])
    p3 = (puntos[id3]['x'], puntos[id3]['y'])
    return calcular_angulo(p1, p2, p3)

def _normalizar(v: np.ndarray) -> float:
    return float(np.linalg.norm(v))