% ============================================
% Archivo de ejemplo CON multiples errores lexicos
% recuperables. Cada error debe reportarse con linea,
% columna y fragmento, y el analisis debe CONTINUAR
% despues de cada uno (no debe detenerse).
% ============================================

% 1) Atomo entrecomillado sin cierre
nombre('Maria Jose).

% 2) Cadena sin cierre
mensaje("hola sin comillas final).

% 3) Caracteres no admitidos en el alfabeto de Prolog
correo(usuario@dominio).
etiqueta(#tag).

% 4) Numero mal formado: letra pegada al numero
edad(30anios).

% 5) Numero mal formado: doble punto decimal
altura(1.70.5).

% 6) Punto que no cierra correctamente la clausula
hecho..

% 7) Secuencia de escape no reconocida dentro de una cadena
%    (el token SI se recupera y se emite como CADENA, pero
%    igual queda registrado el error de la secuencia invalida)
ruta("carpeta\qarchivo").

% 8) Simbolo suelto que no alcanza a formar un operador valido
raro(x : y).

% El analisis debe seguir funcionando con normalidad despues
% de todos los errores anteriores:
padre(juan, ana).

% 9) Comentario de bloque sin cierre: se deja al FINAL del
%    archivo a proposito, porque su recuperacion consume todo
%    lo que resta del archivo al no encontrar el cierre '*/'.
/* este comentario nunca se cierra
   y se extiende hasta el final del archivo
