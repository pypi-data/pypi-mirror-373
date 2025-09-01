from enum import Enum

class TipoEsfuerzo(str,Enum):
    CONTRACCION = "contraccion"
    AMPLITUD = "amplitud"