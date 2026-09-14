#token + error lexico
# este archivo lo que hace es definir las estructuras de datos que se van a usar para representar los tokens y los errores léxicos que se encuentran durante el análisis léxico.
# Estructuras de datos emitidas por el analizador léxico.
from dataclasses import dataclass, field
from typing import Optional
from .token_types import TokenType

@dataclass 
class Token:
    tipo: TokenType # la categoría léxica del token
    lexema: str # el texto exacto leido de la fuente
    linea: int # linea donde inicia el token
    columna: int # columna donde inicia el token
    atributo: Optional[int] = None # indice en la tabla de símbolos, si corresponde. None si no corresponde.

    def __repr__(self) -> str:
        base = f"<{self.tipo.name}, {self.lexema!r}, {self.linea}, {self.columna}"
        if self.atributo is not None:
            base += f", attr={self.atributo}"
        return base + ">"

    def __str__(self) -> str:
        return self.__repr__()


# Error detectado durante la tokenización.
# El analizador NO se detiene al encontrarlo; lo registra y continúa.
@dataclass
class ErrorLexico:
    mensaje: str # descripción del error
    linea: int # linea donde se detectó el error
    columna: int # columna donde se detectó el error
    fragmento: str # texto de la fuente que causó el error
    codigo: str = field(default="LEX") # codigo de error, por defecto "LEX" para errores léxicos

    def __str__(self) -> str:
        return (f"[{self.codigo}] L{self.linea}:C{self.columna} - "
                f"{self.mensaje} | cerca de: {self.fragmento!r}")