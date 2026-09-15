# runner sin dependencias
"""
Runner del corpus de prueba que NO depende de pytest (solo libreria
estandar). Sirve para verificar rapidamente, sin instalar nada, que:

  - examples/completo_ok.pl        -> se tokeniza con 0 errores lexicos.
  - examples/completo_errores.pl   -> produce multiples errores lexicos
                                       recuperables (y el analisis NO se
                                       detiene en el primero).

Uso:
    python tests/run_corpus.py
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.lexer import Lexer

MINIMO_ERRORES_ESPERADOS = 5  # el archivo completo_errores.pl trae varios mas


def analizar(ruta: Path) -> Lexer:
    texto = ruta.read_text(encoding="utf-8")
    lex = Lexer(texto)
    lex.tokenizar()
    return lex


def main() -> None:
    ok_path = RAIZ / "examples" / "completo_ok.pl"
    err_path = RAIZ / "examples" / "completo_errores.pl"
    fallas = 0

    print(f"--- {ok_path.name}: se espera 0 errores lexicos ---")
    lex_ok = analizar(ok_path)
    print(f"tokens: {len(lex_ok.tokens)} | errores: {len(lex_ok.errores)} | "
          f"simbolos en tabla: {len(lex_ok.tabla)}")
    if lex_ok.errores:
        fallas += 1
        print("FALLA: se esperaban 0 errores y se encontraron:")
        for e in lex_ok.errores:
            print("  ", e)
    else:
        print("OK")

    print(f"\n--- {err_path.name}: se esperan multiples errores recuperables ---")
    lex_err = analizar(err_path)
    print(f"tokens: {len(lex_err.tokens)} | errores: {len(lex_err.errores)} | "
          f"simbolos en tabla: {len(lex_err.tabla)}")
    if len(lex_err.errores) < MINIMO_ERRORES_ESPERADOS:
        fallas += 1
        print(f"FALLA: se esperaban al menos {MINIMO_ERRORES_ESPERADOS} errores "
              f"y se encontraron {len(lex_err.errores)}")
    else:
        print("OK - errores detectados:")
        for e in lex_err.errores:
            print("  ", e)
    # el archivo tambien debe seguir tokenizando bien DESPUES de los errores
    lexemas = [t.lexema for t in lex_err.tokens]
    if "juan" not in lexemas or "ana" not in lexemas:
        fallas += 1
        print("FALLA: el analizador no se recupero correctamente tras los errores")

    print(f"\n=== RESUMEN: {'TODO OK' if fallas == 0 else str(fallas) + ' verificacion(es) fallida(s)'} ===")
    sys.exit(1 if fallas else 0)


if __name__ == "__main__":
    main()
