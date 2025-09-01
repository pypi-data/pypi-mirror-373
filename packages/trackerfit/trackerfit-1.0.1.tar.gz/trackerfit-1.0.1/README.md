# 🏋️ trackerfit

**Librería de visión artificial para el seguimiento, análisis y conteo automático de repeticiones en ejercicios físicos** usando [MediaPipe](https://mediapipe.dev/) y [OpenCV](https://opencv.org/).

## ✅ Requisitos

- Python >= 3.10
- pip >= 21.0

## 🚀 Instalación

### Desde PyPI

```bash
pip install trackerfit 
```

### Desde un repositorio local
```bash
git clone https://github.com/4lverto/trackerfit.git
cd trackerfit
pip install -e .
```

### Instalación rápida + Troubleshooting

Si durante la instalación tienes problemas, siguie los siguientes pasos y asegúrate de cumplir con las versiones establecidas en las dependencias.

```bash
python -m pip install --upgrade pip setuptools wheel
pip install --prefer-binary "numpy==1.26.4" "matplotlib>=3.9" "opencv-python>=4.11"
pip install trackerfit==1.0.1
```

## 📦 Características

- Detecta automáticamente poses humanas con MediaPipe
- Calcula ángulos articulares en tiempo real
- Cuenta repeticiones mediante lógica configurable
- Permite entrada por cámara o vídeo
- Visualización dinámica del ángulo y triángulo codificado por color
- Exportación del historial de sesión (ángulo, reps, landmarks, timestamp)
- Arquitectura modular y extensible

## 🧠 Ejercicios soportados

| Ejercicio               | Landmarks utilizados       |
| ----------------------- | -------------------------- |
| Curl de bíceps          | Hombro – Codo – Muñeca     |
| Sentadilla              | Cadera – Rodilla – Tobillo |
| Flexiones               | Hombro – Codo – Muñeca     |
| Press militar           | Cadera – Hombro – Muñeca   |
| Extensión de cuádriceps | Cadera – Rodilla – Tobillo |
| Crunch abdominal        | Cadera – Abdomen – Cabeza  |
| Tríceps dip             | Hombro – Codo – Muñeca     |
| Elevación lateral       | Cadera – Hombro – Muñeca   |

## ⚙️ Uso básico
```python
from trackerfit import SessionManager, TipoEntrada

# Crear y configurar la sesión
manager = SessionManager()
manager.iniciar_sesion(
    tipo=TipoEntrada.CAMARA,
    nombre_ejercicio="curl_bicep"
)

# Esperar a que el usuario finalice
while manager.sesion_activa():
    pass

# Obtener repeticiones y resumen
reps = manager.obtener_repeticiones()
resumen = manager.generar_resumen(reps)
print(resumen)
```

## 🎨 Visualización en tiempo real

La librería muestra en la ventana de OpenCV:

Landmarks del cuerpo detectados

Un triángulo sobre el ángulo evaluado:

🔴 Rojo si no se ha alcanzado el rango válido

✅ Verde si el ángulo es válido para contar una repetición

Valor numérico del ángulo en grados

## 📁 Estructura de la librería
```pgsql
trackerfit/
├── ejercicios/         # Clases para cada tipo de ejercicio
├── session/            # Entrada por vídeo o cámara + gestión de sesiones
├── tracker/            # Wrapper de MediaPipe
├── utils/              # Cálculo de ángulos, enums
├── factory.py          # Devuelve el ejercicio correspondiente
```

## 📂 Ejemplos

Puedes encontrar ejemplos de uso real en la carpeta `/examples`:

- `usar_camera.py`: inicia una sesión desde la cámara.
- `usar_video.py`: procesa un vídeo local de ejercicio.

## 🧪 Tests

Usa `pytest` para validar funcionalidades mínimas:

```bash
pytest
```

## 📜 Licencia

Este proyecto está licenciado bajo la MIT License.

## 👤 Autor

Desarrollado por Alberto Ortega Vílchez
Grado en Ingeniería Informática
Universidad de Granada

## 🌐 Recursos
- [MediaPipe Pose](https://ai.google.dev/edge/mediapipe/solutions/vision/pose_landmarker?hl=es-419)
- [NumPy](https://numpy.org/)
- [OpenCV](https://opencv.org/)