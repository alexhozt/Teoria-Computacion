# Teoría de la Computación — Analizador léxico de Prolog

Analizador léxico para un subconjunto acotado del lenguaje Prolog, desarrollado
para la tarea "Análisis léxico" del curso Teoría de la Computación
(INFO1148, 2do semestre 2026).

El analizador recorre un archivo fuente `.pl` carácter a carácter y produce:

- La secuencia de tokens `<TIPO, 'lexema', línea, columna>`.
- La lista de errores léxicos detectados (con recuperación: el análisis
  nunca se detiene ante un error).
- La tabla de lexemas (símbolos) sin duplicados.
- El registro de comentarios de línea y de bloque encontrados.

La especificación completa de tokens, expresiones regulares y decisiones de
diseño está en [`docs/tabla_tokens.md`](docs/tabla_tokens.md) y en el informe
técnico (PDF, entregado por separado / carpeta `docs/`).

## Requisitos

- Python 3.10 o superior (se usa sintaxis de tipos como `list[Token]` y
  `int | None`).
- Sin dependencias externas para ejecutar el analizador (solo librería
  estándar).
- Para correr la suite de pruebas: [`pytest`](https://pypi.org/project/pytest/).

Instalar pytest (opcional, solo para pruebas):

```bash
pip install pytest
```

## Estructura del repositorio

```
src/
  lexer.py         -> núcleo del analizador léxico (el "AFD integrado")
  token_types.py   -> enum TokenType y categorías con atributo
  lex_token.py     -> dataclasses Token y ErrorLexico
  symbol_table.py  -> tabla de lexemas / símbolos
  main.py          -> CLI para analizar un archivo .pl
tests/
  test_lexer.py    -> suite de pytest (casos válidos, inválidos, prioridad)
  run_corpus.py     -> runner sin dependencias sobre examples/*.pl
examples/
  completo_ok.pl       -> archivo de prueba sin errores léxicos
  completo_errores.pl  -> archivo de prueba con múltiples errores recuperables
docs/
  tabla_tokens.md  -> especificación formal de cada categoría léxica
```

## Cómo ejecutar el analizador

Sobre cualquier archivo fuente de Prolog (`.pl`):

```bash
python -m src.main examples/completo_ok.pl
```

o, equivalentemente:

```bash
python src/main.py examples/completo_ok.pl
```

Esto imprime, en orden: la lista de tokens, los errores léxicos encontrados
(si los hay, con línea/columna/fragmento), la tabla de lexemas y los
comentarios registrados.

## Cómo correr las pruebas

Suite completa con pytest (casos válidos por categoría, prioridad/máxima
coincidencia, errores léxicos y tabla de símbolos):

```bash
pytest tests/test_lexer.py -v
```

Runner rápido sin dependencias, que valida los dos archivos de ejemplo
completos (`examples/completo_ok.pl` debe dar 0 errores;
`examples/completo_errores.pl` debe dar varios errores recuperables sin
detener el análisis):

```bash
python tests/run_corpus.py
```

## Estado actual

- 69 pruebas automatizadas, todas en verde (`pytest tests/test_lexer.py`).
- Corpus de ejemplo validado con `tests/run_corpus.py`.
- Resultados completos de ejecución documentados en el informe técnico
  (sección "Implementación y resultados").
