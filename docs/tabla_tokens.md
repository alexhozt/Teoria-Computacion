# Tabla de tokens — Subconjunto de Prolog

---

## 1. Alfabeto de entrada (Σ)

Σ = { a–z, A–Z, 0–9, `_`, espacio, tabulador, salto de línea } ∪ símbolos

Símbolos admitidos:
```
: - ? = \ < > + * / ! ; , ( ) [ ] { } | . % " '
```

Cualquier carácter fuera de Σ produce un **error léxico** de tipo
"carácter no admitido".

---

## 2. Convenciones

- **Máxima coincidencia (maximal munch):** se consume siempre el lexema
  reconocible más largo. Resuelve `=..` vs `=`, `\==` vs `\=`, `-->` vs `-`.
- **Prioridad:** cuando dos patrones empatan en longitud, gana el que
  aparece primero en la tabla de operadores (ordenados por longitud
  descendente).
- **Palabras reservadas:** `is` y `mod` se reconocen primero como
  `ATOMO` y luego se reclasifican como `OP_ARITM` mediante tabla.
- **Signo `+`/`-`:** se integra al número solo si el token previo **no**
  es operando (átomo, variable, número, cadena, `)`, `]`, `}`).
- **Punto final:** `.` cierra cláusula solo si le sigue espacio, salto de
  línea, `%` o fin de archivo.
- **Variable anónima:** cada `_` produce un token `VAR_ANONIMA`
  independiente y **no** se inserta en la tabla de símbolos.
- **Escapes en cadenas:** se reconocen `\t`, `\n`, `\\`, `\"`. Un escape
  no reconocido produce error léxico.

---

## 3. Identificadores

### 3.1. `ATOMO` — Átomo no entrecomillado

| Campo | Valor |
|---|---|
| **Nombre** | `ATOMO` |
| **Patrón** | `[a-z][a-z0-9_]*` |
| **Ejemplos válidos** | `padre`, `persona_1`, `x1`, `nodo_raiz` |
| **Ejemplos inválidos** | `Padre` (es variable), `_x` (es variable), `1abc` (empieza con dígito) |
| **Atributo** | Índice en tabla de símbolos |
| **Notas** | `is` y `mod` se reconocen aquí y luego se reclasifican a `OP_ARITM`. |

### 3.2. `ATOMO_COMILLADO` — Átomo entre comillas simples

| Campo | Valor |
|---|---|
| **Nombre** | `ATOMO_COMILLADO` |
| **Patrón** | `'([^'\n] \| \\')*'` |
| **Ejemplos válidos** | `'Juan Pérez'`, `':-'`, `'con espacio y ñ'`, `'==>'` |
| **Ejemplos inválidos** | `'María` (sin cierre), `'a\nb'` (salto literal no permitido) |
| **Atributo** | Índice en tabla de símbolos |
| **Notas** | Acepta cualquier carácter salvo comilla simple sin escapar y salto de línea. |

### 3.3. `VARIABLE` — Variable nombrada

| Campo | Valor |
|---|---|
| **Nombre** | `VARIABLE` |
| **Patrón** | `([A-Z] \| _[a-zA-Z0-9_]+)[a-zA-Z0-9_]*` |
| **Ejemplos válidos** | `X`, `Persona`, `_Temporal`, `_x1` |
| **Ejemplos inválidos** | `_` (es `VAR_ANONIMA`), `x` (es `ATOMO`), `1X` |
| **Atributo** | Índice en tabla de símbolos |
| **Notas** | Un `_` seguido de letra/dígito/`_` es variable nombrada. |

### 3.4. `VAR_ANONIMA` — Variable anónima

| Campo | Valor |
|---|---|
| **Nombre** | `VAR_ANONIMA` |
| **Patrón** | `_` (exactamente un guion bajo, sin más caracteres) |
| **Ejemplos válidos** | `_` en `foo(_, Y)` |
| **Ejemplos inválidos** | `_X` (es `VARIABLE`), `__` (es `VARIABLE`) |
| **Atributo** | **Ninguno** (no entra a tabla de símbolos) |
| **Notas** | Cada aparición es independiente; no se vinculan entre sí. |

---

## 4. Literales

### 4.1. `ENTERO`

| Campo | Valor |
|---|---|
| **Nombre** | `ENTERO` |
| **Patrón** | `[+-]?[0-9]+` |
| **Ejemplos válidos** | `0`, `42`, `-7`, `+3` |
| **Ejemplos inválidos** | `3.14` (es `REAL`), `--5`, `3abc` |
| **Atributo** | Índice en tabla de símbolos |
| **Notas** | El signo solo se integra si el token previo **no** es operando. |

### 4.2. `REAL`

| Campo | Valor |
|---|---|
| **Nombre** | `REAL` |
| **Patrón** | `[+-]?[0-9]+\.[0-9]+` |
| **Ejemplos válidos** | `0.001`, `-3.5`, `3.14` |
| **Ejemplos inválidos** | `3.` (punto sin decimales), `.5` (sin parte entera) |
| **Atributo** | Índice en tabla de símbolos |
| **Notas** | El punto es decimal solo si le sigue al menos un dígito. |

### 4.3. `CADENA` — Cadena entre comillas dobles

| Campo | Valor |
|---|---|
| **Nombre** | `CADENA` |
| **Patrón** | `"([^"\\\n] \| \\[tn\\"])*"` |
| **Ejemplos válidos** | `"hola"`, `"línea\nnueva"`, `"dijo \"hola\""` |
| **Ejemplos inválidos** | `"texto` (sin cierre), `"a\qb"` (escape no reconocido) |
| **Atributo** | Índice en tabla de símbolos |
| **Notas** | Escapes válidos: `\t`, `\n`, `\\`, `\"`. |

---

## 5. Operadores

### 5.1. `OP_CLAUSULA`

| Campo | Valor |
|---|---|
| **Nombre** | `OP_CLAUSULA` |
| **Patrón** | `:- \| ?- \| -->` |
| **Ejemplos válidos** | `a :- b.`, `?- consulta.`, `frase --> sujeto.` |
| **Ejemplos inválidos** | `:`, `?`, `->` (operadores incompletos) |
| **Atributo** | Ninguno |
| **Notas** | `-->` es extensión opcional incluida por decisión del grupo. |

### 5.2. `OP_UNIF_COMP` — Unificación y comparación

| Campo | Valor |
|---|---|
| **Nombre** | `OP_UNIF_COMP` |
| **Patrón** | `= \| \= \| == \| \== \| =.. \| < \| =< \| > \| >=` |
| **Ejemplos válidos** | `X = Y`, `A \= B`, `X == Y`, `F =.. [f,a]`, `3 =< 4` |
| **Ejemplos inválidos** | `===`, `=...` (más largos que cualquier operador válido) |
| **Atributo** | Ninguno |
| **Notas** | Máxima coincidencia: `=..` gana sobre `=`, `\==` sobre `\=`. |

### 5.3. `OP_ARITM` — Operadores aritméticos

| Campo | Valor |
|---|---|
| **Nombre** | `OP_ARITM` |
| **Patrón** | `+ \| - \| * \| / \| // \| ** \| is \| mod` |
| **Ejemplos válidos** | `A + 1`, `A // B`, `2 ** 8`, `A is B`, `10 mod 3` |
| **Ejemplos inválidos** | `is` como parte de `isla` (es `ATOMO`) |
| **Atributo** | Ninguno |
| **Notas** | `is` y `mod` se reclasifican desde `ATOMO` por tabla de reservadas. |

### 5.4. `OP_CONTROL` — Operadores de control

| Campo | Valor |
|---|---|
| **Nombre** | `OP_CONTROL` |
| **Patrón** | `\+ \| ! \| ; \| ,` |
| **Ejemplos válidos** | `\+ hermano(X,X)`, `!`, `a ; b`, `a, b` |
| **Ejemplos inválidos** | `;` aislado al inicio (válido léxicamente, error sintáctico posterior) |
| **Atributo** | Ninguno |
| **Notas** | La coma se incluye aquí por decisión del grupo (no hay `COMA` separada). |

---

## 6. Delimitadores y punto

### 6.1. `DELIM`

| Campo | Valor |
|---|---|
| **Nombre** | `DELIM` |
| **Patrón** | `( \| ) \| [ \| ] \| { \| } \| \|` |
| **Ejemplos válidos** | `(a)`, `[1,2,3]`, `{a,b}`, `[H\|T]` |
| **Ejemplos inválidos** | — (todos los delimitadores son válidos individualmente) |
| **Atributo** | Ninguno |
| **Notas** | La barra vertical `\|` se trata como delimitador simple, sin lógica especial de listas. |

### 6.2. `PUNTO`

| Campo | Valor |
|---|---|
| **Nombre** | `PUNTO` |
| **Patrón** | `\.` seguido de `_` (espacio) \| `\n` \| `%` \| EOF |
| **Ejemplos válidos** | `hecho.` al final de línea, `hecho. % comentario` |
| **Ejemplos inválidos** | `hecho..` (punto seguido de punto), `hecho.x` |
| **Atributo** | Ninguno |
| **Notas** | Si no se cumple la condición de cierre, se reporta error léxico. |

---

## 7. Comentarios (se ignoran pero se registran)

### 7.1. `COMENTARIO_LINEA`

| Campo | Valor |
|---|---|
| **Nombre** | `COMENTARIO_LINEA` |
| **Patrón** | `%[^\n]*` |
| **Ejemplos válidos** | `% esto es un comentario` |
| **Atributo** | Ninguno |
| **Notas** | No se emite al parser; solo se registra para conservar posición. |

### 7.2. `COMENTARIO_BLOQUE`

| Campo | Valor |
|---|---|
| **Nombre** | `COMENTARIO_BLOQUE` |
| **Patrón** | `/\*.*?\*/` (con flag DOTALL) |
| **Ejemplos válidos** | `/* varias\nlíneas */` |
| **Ejemplos inválidos** | `/* sin cerrar` (error léxico) |
| **Atributo** | Ninguno |
| **Notas** | No anidan. |

---

## 8. Tokens de control

### 8.1. `EOF`

| Campo | Valor |
|---|---|
| **Nombre** | `EOF` |
| **Patrón** | Fin de archivo |
| **Atributo** | Ninguno |
| **Notas** | Siempre se emite al final de la tokenización. |

### 8.2. `ERROR`

| Campo | Valor |
|---|---|
| **Nombre** | `ERROR` |
| **Patrón** | Cualquier lexema que no encaje en otra categoría |
| **Atributo** | Ninguno |
| **Notas** | Acompañado de un `ErrorLexico` con línea, columna y fragmento. |

---

## 9. Resumen de atributos

| Token | ¿Entra a tabla de símbolos? |
|---|---|
| `ATOMO` | Sí |
| `ATOMO_COMILLADO` | Sí |
| `VARIABLE` | Sí |
| `VAR_ANONIMA` | **No** |
| `ENTERO` | Sí |
| `REAL` | Sí |
| `CADENA` | Sí |
| `OP_*` | No |
| `DELIM` | No |
| `PUNTO` | No |
| `COMENTARIO_*` | No |
| `EOF` | No |
| `ERROR` | No |

---

## 10. Referencias

- Expresiones regulares completas: informe, sección 3.
- Autómatas: informe, sección 4 
- Implementación: `src/lexer.py`.
- Decisiones de diseño: informe, sección 2.2.