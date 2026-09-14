#token + error lexico
# Estructuras de datos emitidas por el analizador léxico.
from dataclasses import dataclass, field
from typing import Optional
from .token_types import TokenType

@dataclass
class Token:
    tipo: TokenType
    lexema: str
    linea: int
    columna: int
    atributo: Optional[int] = None

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
    mensaje: str
    linea: int
    columna: int
    fragmento: str
    codigo: str = field(default="LEX")

    def __str__(self) -> str:
        return (f"[{self.codigo}] L{self.linea}:C{self.columna} - "
                f"{self.mensaje} | cerca de: {self.fragmento!r}")