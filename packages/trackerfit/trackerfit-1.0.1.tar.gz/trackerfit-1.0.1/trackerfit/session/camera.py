# session/camera.py
# -------------------------------
# Requierements
# -------------------------------
import threading
from typing import Literal, Optional
import cv2
import time

from trackerfit.tracker.pose_tracker import PoseTracker
from trackerfit.factory import get_ejercicio
from trackerfit.session.session import Session

from trackerfit.utils.rotacion import (
    GradosRotacion, Normalizar,
    calcular_altura_pantalla, rotar_frame,
    rotacion_necesaria, redimensionar
)

from trackerfit.utils.lado_enum import Lado

# -------------------------------
# Helpers
# -------------------------------

class CameraSession(Session):
    def __init__(self):
        self.pose_tracker = PoseTracker()
        self.contador = None
        self.repeticiones = 0
        self.running = False
        self.thread = None
        self.cap = None
        self.historial_frames = []
        
        self.normalizar_a: Normalizar = "auto"
        self.grados_rotacion: GradosRotacion = 0
        self.rotacion_sesion: GradosRotacion = 0

    def iniciar(
            self,
            nombre_ejercicio: str,
            fuente: Optional[str] = None,
            lado: Lado = Lado.derecho,
            normalizar: Normalizar = "horizontal",
            forzar_grados_rotacion: GradosRotacion = 0,
            indice_camara: int = 0        
    ):
        if self.running:
            return
        
        self.cap = cv2.VideoCapture(indice_camara)
        
        if not self.cap.isOpened():
            raise RuntimeError(f"No se pudo abrir la cámara con índice {indice_camara}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        ok, frame0 = self.cap.read()
        if not ok:
            raise RuntimeError("No se pudo capturar el primer frame de la cámara")
        
        self.normalizar_a = normalizar
        self.grados_rotacion = forzar_grados_rotacion
        
        if self.grados_rotacion != 0:
            self.rotacion_sesion = self.grados_rotacion
        else:
            self.rotacion_sesion = rotacion_necesaria(frame0,self.normalizar_a)
        
        self.contador = get_ejercicio(nombre_ejercicio,lado)
        self.pose_tracker.set_ejercicio(self.contador) # CAMBIO

        self.repeticiones = 0
        self.running = True
        self.thread = threading.Thread(target=self.loop, daemon=True)
        self.thread.start()

    def loop(self):
        """
        Bucle principal que procesa el vídeo y actualiza el estado del ejercicio Frame a Frame
        """
        pantalla_alto = calcular_altura_pantalla()
        nuevo_alto = max(200, pantalla_alto - 120)

        nombre_ventana = "Ejercicio en directo - Seguimiento"
        cv2.namedWindow(nombre_ventana, cv2.WINDOW_NORMAL)
        cv2.moveWindow(nombre_ventana, 100, 100)

        while self.running and self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                self.running = False
                break
            
            if self.rotacion_sesion:
                frame = rotar_frame(frame, self.rotacion_sesion)
            
            results = self.pose_tracker.procesar(frame)
            puntos = self.pose_tracker.extraer_landmarks(results, frame.shape)

            if puntos and self.contador:
                angulo, reps = self.contador.actualizar(puntos)
                self.repeticiones = reps # CAMBIO
                
                #Dibujo del triángulo representativo del ángulo
                estado = self.pose_tracker.dibujar_triangulo_con_angulo(
                    frame, puntos,
                    self.contador.id1,
                    self.contador.id2,
                    self.contador.id3,
                    angulo, getattr(self.contador,"umbral_validacion", None)
                )
                
                # Guardar detalles del frame actual para el resumen final
                # Incluye timestamp, valor del ángulo, estado del movimiento, repeticiones y coordenadas de landmarks
                self.historial_frames.append({
                    "timestamp": time.time(),
                    "angulo": angulo if angulo is not None else None,
                    "repeticiones": self.repeticiones,
                    "estado": estado,
                    "landmarks": puntos
                })

            if results:
                frame = self.pose_tracker.dibuja_landmarks(frame, results)
            
            frame = redimensionar(frame, nuevo_alto)
            cv2.imshow(nombre_ventana, frame)
            
            if cv2.getWindowProperty(nombre_ventana, cv2.WND_PROP_VISIBLE) < 1:
                self.running = False
                break

            if cv2.waitKey(1) & 0xFF == 27:
                self.running = False

        self._cleanup()

    def finalizar(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self._cleanup()

    def _cleanup(self):
        if self.cap:
            self.cap.release()
        cv2.destroyAllWindows()  # Cierra la ventana al finalizar

    def get_repeticiones(self) -> int:
        return self.repeticiones
