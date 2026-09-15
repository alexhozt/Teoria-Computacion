# CLI
"""
Interfaz de linea de comandos del analizador lexico.

Uso:
    python src/main.py archivo.pl

Muestra, en este orden:
  1) la lista de tokens en el formato <TIPO, 'lexema', linea, columna>
     (el mismo formato que usa el enunciado de la tarea, seccion 5)
  2) los errores lexicos detectados (si los hay), con linea/columna/fragmento
  3) la tabla de lexemas (simbolos) resultante, sin duplicados
"""

import sys
from pathlib import Path

# Permite ejecutar este archivo tanto como modulo (python -m src.main)
# como script suelto (python src/main.py), que es la forma mas comun
# en que alguien lo probaria por primera vez.
try:
    from .lexer import Lexer
    from .token_types import TokenType
except ImportError:
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from src.lexer import Lexer
    from src.token_types import TokenType


def analizar_archivo(ruta: str) -> None:
    texto = Path(ruta).read_text(encoding="utf-8")
    lexer = Lexer(texto)
    tokens = lexer.tokenizar()

    print(f"=== TOKENS ({ruta}) ===")
    for tok in tokens:
        print(tok)  # Token.__repr__ ya imprime <TIPO, 'lexema', linea, columna>

    print(f"\n=== ERRORES LEXICOS ({len(lexer.errores)}) ===")
    if not lexer.errores:
        print("Sin errores.")
    else:
        for err in lexer.errores:
            print(err)

    print(f"\n=== TABLA DE LEXEMAS ({len(lexer.tabla)}) ===")
    if len(lexer.tabla) == 0:
        print("(vacia)")
    else:
        for lexema, indice in lexer.tabla:
            print(f"{indice}: {lexema!r}")

    print(f"\n=== COMENTARIOS REGISTRADOS ({len(lexer.comentarios)}) ===")
    for texto, linea, col in lexer.comentarios:
        resumen = texto if len(texto) <= 40 else texto[:40] + "..."
        print(f"L{linea}:C{col} -> {resumen!r}")


def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python src/main.py <archivo.pl>")
        sys.exit(1)
    analizar_archivo(sys.argv[1])


if __name__ == "__main__":
    main()
