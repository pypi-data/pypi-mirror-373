# trackerfit/utils/rotacion.py
from typing import Literal, Optional
import cv2

try:
    import ctypes
except Exception:
    ctypes = None

GradosRotacion = Literal[0,90,180,270]
Normalizar = Optional[Literal["horizontal", "vertical", "auto"]]

def calcular_altura_pantalla() -> int:
    """
    Devuelve una altura de pantalla razonable para multiplataforma.
    Si nos encontramos en Windows se usa WinAPI.
    Si estamos en otro entorno, usamos 900px por defecto.
    """
    if ctypes is not None:
        try:
            return int(ctypes.windll.user32.GetSystemMetrics(1))
        except Exception:
            pass
    
    return 900

def rotar_frame(frame, grados: GradosRotacion):
    grados =  grados % 360
    if grados == 90:
        return cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    if grados == 180:
        return cv2.rotate(frame, cv2.ROTATE_180)
    if grados == 270:
        return cv2.rotate(frame, cv2.ROTATE_90_COUNTERCLOCKWISE)
    
    return frame

def orientacion_de_frame(frame) -> Literal["horizontal","vertical"]:
    h,w = frame.shape[:2]
    return "horizontal" if w >= h else "vertical"

def rotacion_necesaria(frame, normalizar_a: Normalizar) -> GradosRotacion:
    """
    Calculamos cuántos grados hay que rotar 'this' frame para que coincida
    con la orientación objetivo. Si 'normalizar_a' == 'auto', no gira.
    """
    if normalizar_a == "auto":
        return 0
    
    actual = orientacion_de_frame(frame)
    
    if actual == normalizar_a:
        return 0
    
    # Heurística: Siempre rotamos 90º para cambiar la relación ancho/alto
    return 90

def redimensionar(frame, alto_objetivo: int):
    alto, ancho =  frame.shape[:2]
    
    if alto <= 0:
        return frame
 
    ratio = alto_objetivo / float(alto)
    nuevo_ancho = max(1, int(ancho * ratio))
    
    return cv2.resize(frame, (nuevo_ancho, alto_objetivo), interpolation=cv2.INTER_AREA)