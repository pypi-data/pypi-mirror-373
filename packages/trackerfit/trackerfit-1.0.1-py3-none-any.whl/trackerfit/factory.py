from trackerfit.utils.ejercicio_enum import EjercicioId
from trackerfit.ejercicios.curl_bicep import CurlBicep
from trackerfit.ejercicios.sentadilla import Sentadilla
from trackerfit.ejercicios.flexion import Flexion
from trackerfit.ejercicios.press_militar import PressMilitar
from trackerfit.ejercicios.extension_cuadricep import ExtensionCuadricep
from trackerfit.ejercicios.crunch_abdominal import CrunchAbdominal
from trackerfit.ejercicios.dip_tricep import DipTricep
from trackerfit.ejercicios.elevacion_lateral import ElevacionLateral


def get_ejercicio(nombre: EjercicioId, lado='derecho'):
    """
    Devuelve una instancia del ejercicio correspondiente al identificador dado.

    Args:
        nombre (EjercicioId): Enum con el nombre del ejercicio.
        lado (str): 'derecho' o 'izquierdo'
    Raises:
        ValueError: Si el nombre no corresponde a ningún ejercicio
    Returns:
        Ejercicio: instancia del ejercicio correspondiente.
    """
    if nombre == EjercicioId.CURL_BICEP:
        return CurlBicep(lado=lado)
    elif nombre == EjercicioId.SENTADILLA:
        return Sentadilla(lado=lado)
    elif nombre == EjercicioId.FLEXION:
        return Flexion(lado=lado)
    elif nombre == EjercicioId.PRESS_MILITAR:
        return PressMilitar(lado=lado)
    elif nombre == EjercicioId.EXTENSION_CUADRICEP:
        return ExtensionCuadricep(lado=lado)
    elif nombre == EjercicioId.CRUNCH_ABDOMINAL:
        return CrunchAbdominal(lado=lado)
    elif nombre == EjercicioId.DIP_TRICEP:
        return DipTricep(lado=lado)
    elif nombre == EjercicioId.ELEVACION_LATERAL:
        return ElevacionLateral(lado=lado)

    raise ValueError(f"Ejercicio desconocido: {nombre}")
