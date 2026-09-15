% ============================================
% Archivo de ejemplo SIN errores lexicos.
% Cubre todas las categorias del subconjunto de Prolog
% definido en docs/tabla_tokens.md.
% ============================================

/* Hechos base:
   relaciones familiares simples */
padre(juan, ana).
padre(juan, pedro).
'madre de ana'(maria, ana).

% Regla con variables y operador de clausula
abuelo(X, Z) :-
    padre(X, Y),
    padre(Y, Z).

% Uso de la variable anonima
tiene_hijo(P) :- padre(P, _).

% Comparaciones y unificacion
mismo(X, X).
distinto(X, Y) :- X \= Y.
igual_estructura(A, B) :- A == B.
diferente_estructura(A, B) :- A \== B.
descompone(F, L) :- F =.. L.

% Operadores relacionales de orden
mayor_de_edad(Edad) :- Edad >= 18.
menor_que(A, B) :- A < B.
menor_o_igual(A, B) :- A =< B.
mayor_que(A, B) :- A > B.

% Operadores aritmeticos
suma(A, B, C) :- C is A + B.
resta(A, B, C) :- C is A - B.
producto(A, B, C) :- C is A * B.
division_entera(A, B, C) :- C is A // B.
potencia(A, B, C) :- C is A ** B.
resto(A, B, C) :- C is A mod B.

% Numeros enteros y reales, con y sin signo
temperatura(-3).
temperatura(21).
precio(19.99).
promedio(-0.5).

% Cadenas con secuencias de escape validas
saludo("hola").
mensaje("linea1\nlinea2").
ruta("C:\\datos").
cita("dijo \"hola\"").

% Operadores de control
sin_hermanos(X) :- \+ hermano(X, X).
corte(X) :- X > 0, !.
opcion(a) ; opcion(b).

% Regla usando flecha de gramatica (extension opcional del grupo)
frase --> sujeto, predicado.
sujeto --> [el, gato].
predicado --> [duerme].

% Listas y delimitadores
lista_vacia([]).
cabeza_cola([H|T], H, T).
conjunto({a, b, c}).

% Consulta final
?- abuelo(juan, Quien).
