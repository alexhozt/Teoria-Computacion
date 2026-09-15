# pytest
"""
Suite de pruebas del analizador lexico.

Cubre (ver seccion 6 del enunciado - "Casos de prueba minimos"):
  - Mas de 20 casos validos, uno por cada categoria lexica del catalogo.
  - Al menos 8 casos invalidos (errores lexicos de distinto tipo).
  - Casos especificos de maxima coincidencia / prioridad entre operadores.
  - Verificacion de que la tabla de lexemas no duplica entradas.

Ejecucion:
    pytest tests/test_lexer.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from src.lexer import Lexer
from src.token_types import TokenType


def tokens_de(fuente: str):
    """Atajo: tokeniza una cadena y devuelve solo la lista de tokens."""
    return Lexer(fuente).tokenizar()


# ----------------------------------------------------------------------
# 1) Casos validos: al menos un caso por cada categoria del catalogo
# ----------------------------------------------------------------------
@pytest.mark.parametrize("fuente, tipo_esperado, lexema_esperado", [
    # Identificadores
    ("padre", TokenType.ATOMO, "padre"),
    ("persona_1", TokenType.ATOMO, "persona_1"),
    ("x1", TokenType.ATOMO, "x1"),
    ("'Juan Perez'", TokenType.ATOMO_COMILLADO, "'Juan Perez'"),
    ("':-'", TokenType.ATOMO_COMILLADO, "':-'"),
    ("X", TokenType.VARIABLE, "X"),
    ("Persona", TokenType.VARIABLE, "Persona"),
    ("_Temporal", TokenType.VARIABLE, "_Temporal"),
    ("_x1", TokenType.VARIABLE, "_x1"),
    ("_", TokenType.VAR_ANONIMA, "_"),
    # Literales
    ("42", TokenType.ENTERO, "42"),
    ("0", TokenType.ENTERO, "0"),
    ("3.14", TokenType.REAL, "3.14"),
    ("0.001", TokenType.REAL, "0.001"),
    ('"hola"', TokenType.CADENA, '"hola"'),
    ('"linea\\nnueva"', TokenType.CADENA, '"linea\\nnueva"'),
    # Operadores de clausula/consulta
    (":-", TokenType.OP_CLAUSULA, ":-"),
    ("?-", TokenType.OP_CLAUSULA, "?-"),
    ("-->", TokenType.OP_CLAUSULA, "-->"),
    # Unificacion y comparacion
    ("=", TokenType.OP_UNIF_COMP, "="),
    ("\\=", TokenType.OP_UNIF_COMP, "\\="),
    ("==", TokenType.OP_UNIF_COMP, "=="),
    ("\\==", TokenType.OP_UNIF_COMP, "\\=="),
    ("=..", TokenType.OP_UNIF_COMP, "=.."),
    ("<", TokenType.OP_UNIF_COMP, "<"),
    ("=<", TokenType.OP_UNIF_COMP, "=<"),
    (">", TokenType.OP_UNIF_COMP, ">"),
    (">=", TokenType.OP_UNIF_COMP, ">="),
    # Aritmeticos
    ("+", TokenType.OP_ARITM, "+"),
    ("*", TokenType.OP_ARITM, "*"),
    ("/", TokenType.OP_ARITM, "/"),
    ("//", TokenType.OP_ARITM, "//"),
    ("**", TokenType.OP_ARITM, "**"),
    # Control
    ("\\+", TokenType.OP_CONTROL, "\\+"),
    ("!", TokenType.OP_CONTROL, "!"),
    (";", TokenType.OP_CONTROL, ";"),
    (",", TokenType.OP_CONTROL, ","),
    # Delimitadores
    ("(", TokenType.DELIM, "("),
    (")", TokenType.DELIM, ")"),
    ("[", TokenType.DELIM, "["),
    ("]", TokenType.DELIM, "]"),
    ("{", TokenType.DELIM, "{"),
    ("}", TokenType.DELIM, "}"),
    ("|", TokenType.DELIM, "|"),
])
def test_categoria_valida(fuente, tipo_esperado, lexema_esperado):
    tokens = tokens_de(fuente)
    assert tokens[0].tipo == tipo_esperado
    assert tokens[0].lexema == lexema_esperado


def test_is_mod_reclasificados_como_operador():
    tokens = tokens_de("X is 5")
    assert tokens[1].tipo == TokenType.OP_ARITM
    assert tokens[1].lexema == "is"
    assert tokens[1].atributo is None  # no debe entrar a la tabla de simbolos


def test_punto_cierra_clausula():
    tokens = tokens_de("hecho.\n")
    # tokens: [ATOMO 'hecho', PUNTO '.', EOF]
    assert tokens[1].tipo == TokenType.PUNTO


def test_comentario_linea_no_se_emite_como_token():
    tokens = tokens_de("% esto es un comentario\npadre")
    tipos = [t.tipo for t in tokens]
    assert TokenType.COMENTARIO_LINEA not in tipos
    assert tokens[0].tipo == TokenType.ATOMO


def test_comentario_bloque_no_se_emite_como_token():
    tokens = tokens_de("/* varias\nlineas */ X")
    assert tokens[0].tipo == TokenType.VARIABLE


# ----------------------------------------------------------------------
# 2) Maxima coincidencia y prioridad entre operadores
# ----------------------------------------------------------------------
@pytest.mark.parametrize("fuente, tipo_esperado, lexema_esperado", [
    ("\\==", TokenType.OP_UNIF_COMP, "\\=="),  # gana sobre '\='
    ("\\=", TokenType.OP_UNIF_COMP, "\\="),
    ("=..", TokenType.OP_UNIF_COMP, "=.."),    # gana sobre '='
    ("==", TokenType.OP_UNIF_COMP, "=="),      # gana sobre '='
    ("-->", TokenType.OP_CLAUSULA, "-->"),     # gana sobre '-' solo
    (":-", TokenType.OP_CLAUSULA, ":-"),
])
def test_maxima_coincidencia(fuente, tipo_esperado, lexema_esperado):
    tokens = tokens_de(fuente)
    assert tokens[0].tipo == tipo_esperado
    assert tokens[0].lexema == lexema_esperado


def test_signo_se_integra_al_numero_tras_operador():
    tokens = tokens_de("X is -5")
    # [VARIABLE X, OP_ARITM is, ENTERO -5, EOF]
    assert tokens[2].tipo == TokenType.ENTERO
    assert tokens[2].lexema == "-5"


def test_signo_no_se_integra_tras_un_operando():
    tokens = tokens_de("3-5")
    # 3 (ENTERO) - (OP_ARITM binario) 5 (ENTERO): NO debe quedar pegado "-5"
    assert [t.tipo for t in tokens[:3]] == [
        TokenType.ENTERO, TokenType.OP_ARITM, TokenType.ENTERO
    ]
    assert tokens[0].lexema == "3"
    assert tokens[2].lexema == "5"


# ----------------------------------------------------------------------
# 3) Casos invalidos: al menos 8 tipos distintos de error lexico
# ----------------------------------------------------------------------
def test_atomo_comillado_sin_cierre():
    lex = Lexer("'Maria")
    lex.tokenizar()
    assert len(lex.errores) == 1
    assert "sin cierre" in lex.errores[0].mensaje


def test_cadena_sin_cierre():
    lex = Lexer('"texto sin cerrar')
    lex.tokenizar()
    assert len(lex.errores) == 1
    assert "cadena" in lex.errores[0].mensaje


def test_comentario_bloque_sin_cierre():
    lex = Lexer("/* sin cerrar")
    lex.tokenizar()
    assert len(lex.errores) == 1
    assert "comentario" in lex.errores[0].mensaje


def test_caracter_no_admitido():
    lex = Lexer("padre(@)")
    lex.tokenizar()
    assert any("no admitido" in e.mensaje for e in lex.errores)


def test_numero_mal_formado_letra_pegada():
    lex = Lexer("3abc")
    lex.tokenizar()
    assert len(lex.errores) == 1
    assert "mal formado" in lex.errores[0].mensaje


def test_numero_mal_formado_doble_punto():
    lex = Lexer("3.4.5")
    lex.tokenizar()
    assert len(lex.errores) == 1
    assert "mal formado" in lex.errores[0].mensaje


def test_punto_no_cierra_clausula():
    lex = Lexer("hecho..")
    lex.tokenizar()
    assert len(lex.errores) >= 1
    assert any("punto" in e.mensaje for e in lex.errores)


def test_escape_no_reconocido_en_cadena():
    lex = Lexer('"a\\qb"')
    lex.tokenizar()
    assert any("escape" in e.mensaje for e in lex.errores)


def test_simbolo_suelto_no_forma_operador():
    lex = Lexer("x : y")
    lex.tokenizar()
    assert any("operador" in e.mensaje for e in lex.errores)


def test_recuperacion_continua_tras_un_error():
    # el analizador NO debe detenerse: despues del error sigue tokenizando
    lex = Lexer("padre(@, ana).")
    tokens = lex.tokenizar()
    lexemas = [t.lexema for t in tokens]
    assert "ana" in lexemas
    assert len(lex.errores) == 1


# ----------------------------------------------------------------------
# 4) Tabla de lexemas
# ----------------------------------------------------------------------
def test_tabla_no_duplica_lexemas_repetidos():
    analizador = Lexer("padre(juan, ana). padre(juan, pedro).")
    analizador.tokenizar()
    lexemas_en_tabla = [lexema for lexema, _ in analizador.tabla]
    assert lexemas_en_tabla.count("juan") == 1


def test_variable_anonima_no_entra_a_la_tabla():
    analizador = Lexer("foo(_, Y)")
    analizador.tokenizar()
    assert "_" not in [lexema for lexema, _ in analizador.tabla]


def test_is_mod_no_entran_a_la_tabla():
    analizador = Lexer("C is A mod B")
    analizador.tokenizar()
    lexemas = [lexema for lexema, _ in analizador.tabla]
    assert "is" not in lexemas
    assert "mod" not in lexemas
