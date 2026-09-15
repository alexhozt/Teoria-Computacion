# nucleo del analizador
"""
Analizador léxico del subconjunto de Prolog definido en docs/tabla_tokens.md.

Enfoque: en vez de usar el módulo `re` para todo, se implementa un scanner
manual que recorre la fuente carácter a carácter. Esto es intencional: cada
método `_xxx()` de esta clase corresponde, conceptualmente, al recorrido de
un AFD específico (ver docs/automatas.md), y el `if/elif` de tokenizar()
actúa como el "AFD integrado" que decide, según el primer carácter leído
(el lookahead), a qué sub-autómata saltar. Esa es la "estrategia equivalente"
al AFD integrado que permite el enunciado de la tarea (punto 4.3).

El analizador NUNCA se detiene ante un error: lo registra en self.errores
y sigue avanzando (recuperación de errores), tal como pide el punto 4.7
del enunciado.
"""

from .lex_token import Token, ErrorLexico
from .token_types import TokenType, TOKENS_CON_ATRIBUTO
from .symbol_table import TablaSimbolos


# Palabras reservadas: se leen primero como ATOMO (mismo patron [a-z][a-z0-9_]*)
# y luego se reclasifican aqui, tal como indica docs/tabla_tokens.md seccion 5.3.
# Al reclasificarse NO entran a la tabla de simbolos (son operadores, no datos).
RESERVADAS = {
    "is": TokenType.OP_ARITM,
    "mod": TokenType.OP_ARITM,
}

# Tabla de operadores agrupada por longitud (3, 2, 1 caracteres).
# tokenizar() intenta primero el candidato mas largo posible en la posicion
# actual: asi se implementa la regla de "maxima coincidencia" (maximal munch)
# documentada en docs/tabla_tokens.md seccion 2.
OPERADORES = {
    3: {
        "-->": TokenType.OP_CLAUSULA,
        "\\==": TokenType.OP_UNIF_COMP,
        "=..": TokenType.OP_UNIF_COMP,
    },
    2: {
        ":-": TokenType.OP_CLAUSULA,
        "?-": TokenType.OP_CLAUSULA,
        "\\=": TokenType.OP_UNIF_COMP,
        "==": TokenType.OP_UNIF_COMP,
        "=<": TokenType.OP_UNIF_COMP,
        ">=": TokenType.OP_UNIF_COMP,
        "//": TokenType.OP_ARITM,
        "**": TokenType.OP_ARITM,
        "\\+": TokenType.OP_CONTROL,
    },
    1: {
        "=": TokenType.OP_UNIF_COMP,
        "<": TokenType.OP_UNIF_COMP,
        ">": TokenType.OP_UNIF_COMP,
        "+": TokenType.OP_ARITM,
        "-": TokenType.OP_ARITM,
        "*": TokenType.OP_ARITM,
        "/": TokenType.OP_ARITM,
        "!": TokenType.OP_CONTROL,
        ";": TokenType.OP_CONTROL,
        ",": TokenType.OP_CONTROL,
    },
}

# ( ) [ ] { } | -> delimitadores de un solo caracter, sin logica adicional
DELIMITADORES = set("()[]{}|")

# Escapes reconocidos dentro de una CADENA "..." (doc seccion 4.3)
ESCAPES_CADENA_VALIDOS = {"t", "n", "\\", '"'}

# Tipos de token que cuentan como "operando" para la regla del signo +/-
# (doc seccion 2: "el signo se integra al numero solo si el token previo
# NO es operando"). Un ')' ']' '}' tambien cuenta como operando: cierra una
# expresion que ya produjo un valor.
OPERANDO_PREVIO = {
    TokenType.ATOMO,
    TokenType.ATOMO_COMILLADO,
    TokenType.VARIABLE,
    TokenType.VAR_ANONIMA,
    TokenType.ENTERO,
    TokenType.REAL,
    TokenType.CADENA,
}
DELIMS_CIERRE = set(")]}")


class Lexer:
    """Analizador léxico. Uso básico:

        lex = Lexer(codigo_fuente)
        tokens = lex.tokenizar()
        # lex.errores      -> lista de ErrorLexico encontrados
        # lex.tabla        -> TablaSimbolos con atomos/variables/literales
        # lex.comentarios  -> lista de (texto, linea, columna) de comentarios
    """

    def __init__(self, fuente: str) -> None:
        self.fuente = fuente
        self.n = len(fuente)
        self.pos = 0            # indice del caracter actual dentro de self.fuente
        self.linea = 1          # linea 1-indexada del caracter actual
        self.columna = 1        # columna 1-indexada del caracter actual

        self.tokens: list[Token] = []
        self.errores: list[ErrorLexico] = []
        self.comentarios: list[tuple[str, int, int]] = []
        self.tabla = TablaSimbolos()

    # ------------------------------------------------------------------
    # utilidades de bajo nivel sobre el cursor (todas las demas funciones
    # se apoyan en estas tres para no perder nunca la cuenta de linea/columna)
    # ------------------------------------------------------------------
    def _actual(self) -> str:
        """Caracter en la posicion actual, o '' si ya llegamos al final."""
        return self.fuente[self.pos] if self.pos < self.n else ""

    def _ver(self, offset: int = 1) -> str:
        """Caracter `offset` posiciones adelante, sin consumirlo (lookahead)."""
        idx = self.pos + offset
        return self.fuente[idx] if idx < self.n else ""

    def _avanzar(self, k: int = 1) -> None:
        """Consume `k` caracteres, actualizando linea/columna correctamente
        cuando se cruza un salto de linea."""
        for _ in range(k):
            if self.pos >= self.n:
                return
            if self.fuente[self.pos] == "\n":
                self.linea += 1
                self.columna = 1
            else:
                self.columna += 1
            self.pos += 1

    # ------------------------------------------------------------------
    # registro de tokens y errores
    # ------------------------------------------------------------------
    def _emitir(self, tipo: TokenType, lexema: str, linea: int, columna: int,
                con_atributo: bool = False) -> Token:
        atributo = self.tabla.insertar(lexema) if con_atributo else None
        tok = Token(tipo=tipo, lexema=lexema, linea=linea, columna=columna,
                    atributo=atributo)
        self.tokens.append(tok)
        return tok

    def _error(self, mensaje: str, linea: int, columna: int, fragmento: str) -> None:
        """Registra un ErrorLexico Y además deja un token ERROR en el flujo,
        para que quede visible dónde ocurrió el problema. El análisis
        continúa normalmente después de llamar a este método (no se lanza
        ninguna excepción): esa es la "recuperación de errores" pedida."""
        self.errores.append(
            ErrorLexico(mensaje=mensaje, linea=linea, columna=columna, fragmento=fragmento)
        )
        self.tokens.append(Token(tipo=TokenType.ERROR, lexema=fragmento, linea=linea, columna=columna))

    def _permite_signo(self) -> bool:
        """True si un '+'/'-' en la posición actual debe pegarse al número
        que sigue (porque el token anterior NO es un operando)."""
        if not self.tokens:
            return True  # nada antes: el signo es parte del primer numero
        anterior = self.tokens[-1]
        if anterior.tipo in OPERANDO_PREVIO:
            return False
        if anterior.tipo is TokenType.DELIM and anterior.lexema in DELIMS_CIERRE:
            return False
        return True

    # ------------------------------------------------------------------
    # bucle principal: aqui vive el "AFD integrado" (decide, segun el
    # primer caracter, a que sub-autómata saltar)
    # ------------------------------------------------------------------
    def tokenizar(self) -> list[Token]:
        while self.pos < self.n:
            c = self._actual()

            if c in " \t\r\n":
                # espacios/tabs/saltos de linea: se ignoran pero SI avanzan
                # la posicion (conservando linea/columna para el resto)
                self._avanzar()
                continue

            if c == "%":
                self._comentario_linea()
                continue

            if c == "/" and self._ver() == "*":
                self._comentario_bloque()
                continue

            if c == "'":
                self._atomo_comillado()
                continue

            if c == '"':
                self._cadena()
                continue

            if c.islower():
                self._atomo()
                continue

            if c.isupper() or c == "_":
                self._variable()
                continue

            if c.isdigit():
                self._numero()
                continue

            if c in "+-" and self._ver().isdigit() and self._permite_signo():
                self._numero()
                continue

            if c == ".":
                self._punto()
                continue

            if c in DELIMITADORES:
                self._delimitador()
                continue

            if c in ":?=\\<>*/!;,+-":
                self._operador()
                continue

            # cualquier otro caracter no pertenece al alfabeto Sigma admitido
            self._caracter_no_admitido()

        # EOF siempre se emite al final, incluso si la fuente esta vacia
        self.tokens.append(Token(tipo=TokenType.EOF, lexema="", linea=self.linea, columna=self.columna))
        return self.tokens

    # ------------------------------------------------------------------
    # comentarios (se registran en self.comentarios; NO se emiten como
    # token al flujo que recibiria un analizador sintactico posterior)
    # ------------------------------------------------------------------
    def _comentario_linea(self) -> None:
        linea, col = self.linea, self.columna
        inicio = self.pos
        while self.pos < self.n and self._actual() != "\n":
            self._avanzar()
        self.comentarios.append((self.fuente[inicio:self.pos], linea, col))

    def _comentario_bloque(self) -> None:
        linea, col = self.linea, self.columna
        inicio = self.pos
        self._avanzar(2)  # consume '/*'
        cerrado = False
        while self.pos < self.n:
            if self._actual() == "*" and self._ver() == "/":
                self._avanzar(2)
                cerrado = True
                break
            self._avanzar()
        texto = self.fuente[inicio:self.pos]
        if cerrado:
            self.comentarios.append((texto, linea, col))
        else:
            fragmento = texto if len(texto) <= 20 else texto[:20] + "..."
            self._error("comentario de bloque sin cierre", linea, col, fragmento)

    # ------------------------------------------------------------------
    # atomo entrecomillado 'xxx' y cadena "xxx"
    # ------------------------------------------------------------------
    def _atomo_comillado(self) -> None:
        linea, col = self.linea, self.columna
        inicio = self.pos
        self._avanzar()  # consume la comilla simple de apertura
        cerrado = False
        while self.pos < self.n:
            c = self._actual()
            if c == "\n":
                break  # no se permite salto de linea literal dentro
            if c == "\\" and self._ver() == "'":
                self._avanzar(2)  # escape \' -> comilla literal dentro del atomo
                continue
            if c == "'":
                self._avanzar()
                cerrado = True
                break
            self._avanzar()
        lexema = self.fuente[inicio:self.pos]
        if cerrado:
            self._emitir(TokenType.ATOMO_COMILLADO, lexema, linea, col, con_atributo=True)
        else:
            self._error("atomo entrecomillado sin cierre", linea, col, lexema)

    def _cadena(self) -> None:
        linea, col = self.linea, self.columna
        inicio = self.pos
        self._avanzar()  # consume la comilla doble de apertura
        cerrado = False
        while self.pos < self.n:
            c = self._actual()
            if c == "\n":
                break  # salto de linea sin cerrar -> cadena invalida
            if c == "\\":
                sig = self._ver()
                if sig in ESCAPES_CADENA_VALIDOS:
                    self._avanzar(2)
                else:
                    # escape no reconocido: se reporta pero NO se aborta la
                    # cadena; se sigue buscando el cierre (recuperacion)
                    self._error("secuencia de escape no reconocida", self.linea, self.columna,
                                "\\" + sig)
                    self._avanzar(2 if sig else 1)
                continue
            if c == '"':
                self._avanzar()
                cerrado = True
                break
            self._avanzar()
        lexema = self.fuente[inicio:self.pos]
        if cerrado:
            self._emitir(TokenType.CADENA, lexema, linea, col, con_atributo=True)
        else:
            self._error("cadena sin cierre", linea, col, lexema)

    # ------------------------------------------------------------------
    # identificadores: atomo, variable, variable anonima
    # ------------------------------------------------------------------
    def _atomo(self) -> None:
        """[a-z][a-z0-9_]*  (doc seccion 3.1)"""
        linea, col = self.linea, self.columna
        inicio = self.pos
        self._avanzar()  # el primer caracter ya se valido como [a-z]
        while self.pos < self.n:
            c = self._actual()
            if c.islower() or c.isdigit() or c == "_":
                self._avanzar()
            else:
                break
        lexema = self.fuente[inicio:self.pos]
        tipo = RESERVADAS.get(lexema, TokenType.ATOMO)
        # is/mod reclasificados son operadores: no van a la tabla de simbolos
        con_atributo = tipo is TokenType.ATOMO
        self._emitir(tipo, lexema, linea, col, con_atributo=con_atributo)

    def _variable(self) -> None:
        """([A-Z] | _[a-zA-Z0-9_]+)[a-zA-Z0-9_]*  ó  '_' sola (VAR_ANONIMA)."""
        linea, col = self.linea, self.columna
        inicio = self.pos
        primero = self._actual()
        self._avanzar()

        if primero == "_":
            sigue_identificador = self.pos < self.n and (
                self._actual().isalnum() or self._actual() == "_"
            )
            if not sigue_identificador:
                # un '_' solo, sin nada pegado detras -> variable anonima
                self._emitir(TokenType.VAR_ANONIMA, "_", linea, col, con_atributo=False)
                return
            # si tiene algo pegado, es una variable nombrada normal (_Temporal, _x1)

        while self.pos < self.n and (self._actual().isalnum() or self._actual() == "_"):
            self._avanzar()
        lexema = self.fuente[inicio:self.pos]
        self._emitir(TokenType.VARIABLE, lexema, linea, col, con_atributo=True)

    # ------------------------------------------------------------------
    # numeros: ENTERO y REAL, con deteccion de numeros mal formados
    # ------------------------------------------------------------------
    def _numero(self) -> None:
        linea, col = self.linea, self.columna
        inicio = self.pos

        if self._actual() in "+-":
            self._avanzar()  # signo opcional; ya se valido con _permite_signo()

        while self.pos < self.n and self._actual().isdigit():
            self._avanzar()

        es_real = False
        if self._actual() == "." and self._ver().isdigit():
            es_real = True
            self._avanzar()  # punto decimal
            while self.pos < self.n and self._actual().isdigit():
                self._avanzar()

        # --- deteccion de numero mal formado (doc seccion 4.1/4.2) ---
        malformado = False
        if self.pos < self.n and (self._actual().isalpha() or self._actual() == "_"):
            # letra u guion bajo pegado directo al numero: p.ej. "30anios"
            malformado = True
        elif es_real and self._actual() == "." and self._ver().isdigit():
            # segundo punto decimal pegado: p.ej. "1.70.5"
            malformado = True

        if malformado:
            while self.pos < self.n and (self._actual().isalnum() or self._actual() in "_."):
                self._avanzar()
            lexema = self.fuente[inicio:self.pos]
            self._error("numero mal formado", linea, col, lexema)
            return

        lexema = self.fuente[inicio:self.pos]
        tipo = TokenType.REAL if es_real else TokenType.ENTERO
        self._emitir(tipo, lexema, linea, col, con_atributo=True)

    # ------------------------------------------------------------------
    # punto final de clausula
    # ------------------------------------------------------------------
    def _punto(self) -> None:
        """Un '.' solo cierra clausula si le sigue espacio/salto de linea/
        '%'/EOF (doc seccion 6.2). En cualquier otro caso es un error
        lexico recuperable (se consume solo el '.' y se sigue leyendo)."""
        linea, col = self.linea, self.columna
        siguiente = self._ver()
        self._avanzar()
        if siguiente in (" ", "\t", "\r", "\n", "%", ""):
            self._emitir(TokenType.PUNTO, ".", linea, col, con_atributo=False)
        else:
            self._error("punto no cierra correctamente una clausula", linea, col, ".")

    # ------------------------------------------------------------------
    # delimitadores y operadores
    # ------------------------------------------------------------------
    def _delimitador(self) -> None:
        linea, col = self.linea, self.columna
        c = self._actual()
        self._avanzar()
        self._emitir(TokenType.DELIM, c, linea, col, con_atributo=False)

    def _operador(self) -> None:
        """Maxima coincidencia: se prueba primero el candidato de 3
        caracteres, luego 2, luego 1, tomando el mas largo que exista en
        la tabla OPERADORES (ver AFD del punto 4.4/4.5 del informe)."""
        linea, col = self.linea, self.columna
        for longitud in (3, 2, 1):
            candidato = self.fuente[self.pos:self.pos + longitud]
            tipo = OPERADORES.get(longitud, {}).get(candidato)
            if tipo is not None:
                self._avanzar(longitud)
                self._emitir(tipo, candidato, linea, col, con_atributo=False)
                return
        # el caracter esta en Sigma pero no arma ningun operador valido
        # (p.ej. ':' suelto, sin el '-' que forma ':-')
        c = self._actual()
        self._avanzar()
        self._error("simbolo no reconocido como operador", linea, col, c)

    # ------------------------------------------------------------------
    # caracteres fuera del alfabeto Sigma
    # ------------------------------------------------------------------
    def _caracter_no_admitido(self) -> None:
        linea, col = self.linea, self.columna
        c = self._actual()
        self._avanzar()
        self._error("caracter no admitido en el alfabeto de Prolog", linea, col, c)
