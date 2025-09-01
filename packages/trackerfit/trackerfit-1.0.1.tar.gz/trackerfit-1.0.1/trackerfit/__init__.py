# trackerfit/__init__.py
"""
Utilidades para contar repeticiones de ejercicios a partir de landmarks de MediaPipe
"""
from trackerfit.session.manager import SessionManager
from trackerfit.factory import get_ejercicio
from trackerfit.utils.tipo_entrada_enum import TipoEntrada

__all__ = ["SessionManager", "get_ejercicio", "TipoEntrada"]
