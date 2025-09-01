# tracker/pose_tracker.py
# -------------------------------
# Requierements
# -------------------------------

import mediapipe as mp
import cv2
from typing import Optional

from trackerfit.ejercicios.ejercicio import Ejercicio
from trackerfit.utils.estado_ejercicio_enum import TipoEstadoEjercicio


# -------------------------------
# Helpers
# -------------------------------

class PoseTracker:

    def __init__(self, ejercicio: Optional[Ejercicio]=None):
        """
        Configuración inicial: Inicializo el modelo de pose de Mediapipe con mis parámetros
        """
        self.pose = mp.solutions.pose.Pose()
        
        self.drawing_utils = mp.solutions.drawing_utils # Para dibujar puntos y líneas
        self.drawing_styles = mp.solutions.drawing_styles # Para obtener los colores y estilos por defecto
        self.pose_connections = mp.solutions.pose.POSE_CONNECTIONS # Cómo se conectan los puntos del cuerpo

        self.ejercicio = ejercicio

    def procesar(self, frame):
        """
        Detección de landmarks
        Convierte el frame de BGR (formato de OpenCV) a RGB (formato de MediaPipe) y luego
        lo pasa por el modelo para obtener los landmarks (puntos del cuerpo)
        """
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(frame_rgb)
        return results # Results contiene toda la información de la pose

    def set_ejercicio(self, ejercicio: Ejercicio) -> None:
        self.ejercicio = ejercicio
    
    def dibuja_landmarks(self, frame, results):
        """
        Dibuja la pose (Esqueleto)
        Es decir, dibujo los landmarks y las conexiones entre ellos para mostrar
        visualmente la pose en pantalla
        """
        if(results.pose_landmarks):
            self.drawing_utils.draw_landmarks(
                frame,
                results.pose_landmarks,
                self.pose_connections,
                self.drawing_styles.get_default_pose_landmarks_style()
            )
        return frame

    def dibujar_triangulo_con_angulo(self,frame, puntos, id1, id2, id3, angulo, umbral_validacion=None):
        """
        Dibuja un triángulo entre tres landmarks y muestra el ángulo.
        Cambia de color (rojo/verde) según si supera (o reduce) el umbral de validación,
        en función del tipo de ejercicio que se esté realizando.
        """
        p1 = puntos[id1]["x"], puntos[id1]["y"]
        p2 = puntos[id2]["x"], puntos[id2]["y"]
        p3 = puntos[id3]["x"], puntos[id3]["y"]

        # Color según validación del ángulo
        estado,color = self._obtener_color(angulo if angulo is not None else 0.0,umbral_validacion)

        # Dibujar líneas del triángulo
        cv2.line(frame, p1, p2, color, 2)
        cv2.line(frame, p2, p3, color, 2)
        cv2.line(frame, p3, p1, color, 2)

        # Mostrar valor del ángulo
        cv2.putText(frame, f"{int(angulo)} {estado}" if angulo is not None else f"-- {estado}", p2, cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

        return estado
    
    def extraer_landmarks(self, results, frame_shape):
        """
        Extraemos las coordenadas de los landmarks
        Convierto los landmarks a coordenadas reales en píxeles según el tamaño del frame (alto,ancho),
        ya que los landmarks están en coordenadas normalizadas (0,1)
        """
        height, width, _ = frame_shape
        puntos = {}
        
        if(results.pose_landmarks):
            for idx, landmark in enumerate(results.pose_landmarks.landmark):
                puntos[idx] = {
                    'x': int(landmark.x * width),
                    'y': int(landmark.y * height),
                    'z': landmark.z,
                    #'visibilidad': landmark.visibility
                }
        return puntos
    
    def _obtener_color(self, angulo: float, umbral_validacion: Optional[float]):
        if self.ejercicio is not None and hasattr(self.ejercicio, "esfuerzo_activo"):
            esforzandose = self.ejercicio.esfuerzo_activo(angulo)
            return (f"{TipoEstadoEjercicio.ESFUERZO.value}" if esforzandose else f"{TipoEstadoEjercicio.RELAJACION.value}", (0,255,0) if esforzandose else (0,0,255))
        else:
            if umbral_validacion is None:
                umbral_validacion = 90
            
        hay_esfuerzo = angulo < umbral_validacion
        return (f"{TipoEstadoEjercicio.ESFUERZO.value}" if hay_esfuerzo else f"{TipoEstadoEjercicio.RELAJACION.value}" , (0, 255, 0) if hay_esfuerzo else (0, 0, 255))
            
        