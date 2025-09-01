# ejercicios/ejercicio.py
# -------------------------------
# Requierements
# -------------------------------
from __future__ import annotations

from abc import ABC
from collections import deque
from statistics import median
from typing import Optional, Deque, Tuple, Dict

from trackerfit.utils.angulos import calcular_angulo_landmarks
from trackerfit.utils.tipo_esfuerzo_enum import TipoEsfuerzo

# -------------------------------
# Helpers
# -------------------------------

class Ejercicio(ABC):
    """
    Clase base para ejercicios. 
    - Define la lógica general de conteo de repeticiones
    - Cálculo y suavizado del ángulo entre 3 landmarks
    - Detección de transiciones de esfeurzo/relajación para contar repeticiones
    """
    def __init__(self, angulo_min, angulo_max, puntos, tipo_esfuerzo : TipoEsfuerzo = TipoEsfuerzo.CONTRACCION):
        """
        Inicializa un ejercicio con umbrales y puntos clave.

        Args:
            angulo_min (float): Ángulo mínimo esperado (posición contraída).
            angulo_max (float): Ángulo máximo esperado (posición extendida).
            puntos (tuple): IDs de 3 landmarks (id1, id2, id3) en orden.
            tipo_esfuerzo (TipoEsfuerzo) : CONTRACCION o AMPLITUD
        """ 
        self.reps = 0
        self.angulo_min = angulo_min
        self.angulo_max = angulo_max
        
        self.id1, self.id2, self.id3 = puntos

        # Valor usado por las vistas para colorear / validar el ángulo, sobrescrito por cada subclase
        self.umbral_validacion = 90
        self.tipo_esfuerzo = tipo_esfuerzo
        
        # Parámetros de suavizado de ángulo
        self.suavizado = 4
        self.frames_rebotados = 3
        self.ventana_suavizado = 4 
        
        # Parámetros de estado interno
        self._esforzandose : Optional[bool] = None
        self._buffer_angulos : Deque[float] = deque(maxlen=self.ventana_suavizado)
        self._frames_diferentes : int = 0
 
    def actualizar(self, puntos_detectados: Dict[int, Dict[str,float]]) -> tuple[Optional[float], int]:
        """
        Actualiza el estado del ejercicio con los puntos detectados.

        Returns:
            tuple: (ángulo del frame actual, repeticiones acumuladas)
        """
        if not all(k in puntos_detectados for k in [self.id1, self.id2, self.id3]):
            return None, self.reps

        # Cálculo del ángulo frame a frame
        angulo = calcular_angulo_landmarks(puntos_detectados, self.id1, self.id2, self.id3)
        angulo_suavizado = self._suavizar(angulo)
        
        # Si se detectara una transición suavizada, se incrementa una repetición
        self.detectar_transicion(angulo_suavizado) 
        
        return angulo, self.reps

    def detectar_transicion(self, angulo: float | None):
        """
        Detecta si ha habido una transición válida (esfuerzo <-> relajación) para contar una repetición.
        """

        esforzandose = self.esfuerzo_activo(angulo)
        
        if self._esforzandose is None:
            self._esforzandose = esforzandose
            self._frames_diferentes = 0
            return
        
        if esforzandose != self._esforzandose:
            self._frames_diferentes += 1
            if self._frames_diferentes >= self.frames_rebotados:
                # Transición relajación -> esfuerzo ---> Añade repetición
                if self._esforzandose is False and esforzandose is True:
                    self.reps += 1
                
                self._esforzandose = esforzandose
                self._frames_diferentes = 0
        else:
            self._frames_diferentes = 0

    def reset(self):
        """Reinicia el conteo de repeticiones y el estado interno."""
        self.reps = 0
        self._esforzandose = None

    def get_reps(self):
        """Devuelve el número actual de repeticiones."""
        return self.reps

    def esfuerzo_activo(self, angulo: Optional[float]) -> bool:
        """
        Devuelve True si, para el ángulo dado, el estado corresponde al "esfuerzo" del ejercicio
        según su tipo de esfuerzo configurado
        """
        if angulo is None:
            return False
        
        # Primer estado: Fijamos referencia sin suavizado
        if self._esforzandose is None:
            if self.tipo_esfuerzo == TipoEsfuerzo.CONTRACCION:
                return angulo <= self.angulo_min
            else:
                return angulo >= self.angulo_max
        
        # Suavizamos para evitar rebotes.
        if self.tipo_esfuerzo == TipoEsfuerzo.CONTRACCION:
            if self._esforzandose:
                return not (angulo >= (self.angulo_min + self.suavizado))
            else:
                return (angulo <= (self.angulo_min - self.suavizado))
        else:
            if self._esforzandose:
                return not (angulo <= (self.angulo_max - self.suavizado))
            else:
                return (angulo >= (self.angulo_max + self.suavizado))
          
    def estado_angulo(self, angulo: float | None) -> str:
        """
        'esfuerzo' o 'relajación' para colorear en tiempo real.
        """
        return "esfuerzo" if self.esfuerzo_activo(angulo) else "relajacion"

    def _suavizar(self, angulo: Optional[float]) -> Optional[float]:
        if angulo is None:
            return None
        
        self._buffer_angulos.append(float(angulo))
        
        return float(median(self._buffer_angulos))
    