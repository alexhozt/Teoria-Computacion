# enum de categorias lexicas

from enum import Enum, auto


class TokenType(Enum):
    #Identificadores 
    ATOMO            = auto()   # [a-z][a-z0-9_]*
    ATOMO_COMILLADO  = auto()   # '...'
    VARIABLE         = auto()   # [A-Z_][a-zA-Z0-9_]*
    VAR_ANONIMA      = auto()   # _ (exactamente)

    #Literales -
    ENTERO           = auto()   # [+-]?[0-9]+
    REAL             = auto()   # [+-]?[0-9]+\.[0-9]+
    CADENA           = auto()   # "..."

    #Operadores 
    OP_CLAUSULA      = auto()   # :-  ?-  -->
    OP_UNIF_COMP     = auto()   # =  \=  ==  \==  =..  <  =<  >  >=
    OP_ARITM         = auto()   # + - * / // ** is mod
    OP_CONTROL       = auto()   # \+  !  ;  ,

    #Delimitadores y punto 
    DELIM            = auto()   # ( ) [ ] { } |
    PUNTO            = auto()   # . que cierra cláusula

    #Comentarios (se registran, no se emiten al parser)
    COMENTARIO_LINEA  = auto()  # % ...
    COMENTARIO_BLOQUE = auto()  # /* ... */

    #Control 
    EOF              = auto()  
    ERROR            = auto()   


# Conjunto de tokens que SÍ entran a la tabla de símbolos.
# Se usa en lexer.py para decidir si se inserta el lexema.
TOKENS_CON_ATRIBUTO = frozenset({
    TokenType.ATOMO,
    TokenType.ATOMO_COMILLADO,
    TokenType.VARIABLE,
    TokenType.ENTERO,
    TokenType.REAL,
    TokenType.CADENA,
})