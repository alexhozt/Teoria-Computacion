# tabla de lexemas
"""
Tabla de símbolos / tabla de lexemas.

Registra los lexemas de las categorías que la tarea exige:
  - ATOMO
  - ATOMO_COMILLADO
  - VARIABLE
  - ENTERO
  - REAL
  - CADENA

NO registra VAR_ANONIMA (cada _ es independiente).
NO registra operadores, delimitadores ni comentarios.
"""

from typing import Iterator

# Mapea lexema -> índice entero único (1-indexado).
# El primer lexema insertado recibe índice 1, el segundo 2, etc.
# Si un lexema se repite, se devuelve el mismo índice.
class TablaSimbolos:
    def __init__(self) -> None:
        self._tabla: dict[str, int] = {}
        self._siguiente: int = 1

    # Inserta el lexema si no existe y devuelve su índice.
    # Si ya existe, devuelve el índice previo sin duplicar.
    def insertar(self, lexema: str) -> int:
        if lexema not in self._tabla:
            self._tabla[lexema] = self._siguiente
            self._siguiente += 1
        return self._tabla[lexema]

    #Devuelve el índice del lexema, o None si no está registrado
    def buscar(self, lexema: str) -> int | None:
        return self._tabla.get(lexema)

    def contiene(self, lexema: str) -> bool:
        return lexema in self._tabla

    #utilidades 
    def __len__(self) -> int:
        return len(self._tabla)

    def __iter__(self) -> Iterator[tuple[str, int]]:
        """Itera en orden de índice (útil para imprimir la tabla)."""
        return iter(sorted(self._tabla.items(), key=lambda kv: kv[1]))

    def __repr__(self) -> str:
        entradas = ", ".join(f"{i}:{lex}" for lex, i in self)
        return f"TablaSimbolos({{{entradas}}})"