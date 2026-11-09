"""Generación «en bruto» de las multiplicaciones y elección de la tabla.

Reglas:
  - Nunca se usan el 0, el 1 ni el 10, ni en las tablas ni en los factores.
  - Las tablas y los factores válidos van del 2 al 9.
  - Sin tablas indicadas se usan todas (2..9).
  - Con tablas indicadas, solo aparecen esas. Las repetidas se ignoran.
  - Al final de la hoja va una tabla de multiplicar de referencia, ya
    resuelta, elegida al azar. No se repite ninguna tabla hasta que han
    salido todas (ver `elegir_tabla`).

Este módulo solo genera los números. Los enunciados y el PDF se generan en
`pdf.py`.
"""

import argparse
import random
from pathlib import Path

from operaciones.comun.rotacion import elegir_sin_repetir

NUM_EJERCICIOS = 10

# Números que pueden aparecer en una multiplicación (se excluyen 0, 1 y 10).
# Se usan tanto para las tablas (el primer número) como para el número por
# el que se multiplica (el segundo). Sin tablas indicadas se usan todas.
NUMEROS_VALIDOS = (2, 3, 4, 5, 6, 7, 8, 9)

# Fichero donde se guardan las tablas de referencia que ya han salido en la
# ronda actual. Se crea en la carpeta desde la que se ejecuta (la misma de
# los PDF; con el servidor, <CARPETA_PDFS>/multiplicaciones). Una tabla no
# se repite hasta que han salido todas las demás.
FICHERO_TABLAS_SALIDAS = Path("tablas_salidas.json")


def tabla_valida(valor):
    """Convierte un argumento de la línea de comandos en una tabla válida.

    Lo usa argparse (`type=`): si el valor no es un número del 2 al 9,
    argparse muestra el error y termina.
    """
    try:
        tabla = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{valor}' no es un número entero válido.")
    if tabla not in NUMEROS_VALIDOS:
        raise argparse.ArgumentTypeError(
            f"la tabla '{tabla}' no está permitida. "
            "Solo se admiten tablas del 2 al 9 (se excluyen 0, 1 y 10)."
        )
    return tabla


def tablas_pedidas(tablas):
    """Quita las tablas repetidas; si no se indica ninguna, devuelve todas."""
    return list(dict.fromkeys(tablas)) or list(NUMEROS_VALIDOS)


def fix_adjacent_dups(items):
    """Evita, cuando puede, que haya elementos iguales consecutivos."""
    for i in range(1, len(items)):
        if items[i] == items[i - 1]:
            for j in range(i + 1, len(items)):
                if items[j] != items[i]:
                    items[i], items[j] = items[j], items[i]
                    break


def generar_lineas(tablas, num_ejercicios):
    """Genera las parejas (tabla, factor) que se convertirán en enunciados."""
    combinaciones = [(tabla, factor) for tabla in tablas for factor in NUMEROS_VALIDOS]
    total = len(combinaciones)

    if total >= num_ejercicios:
        random.shuffle(combinaciones)
        lineas = combinaciones[:num_ejercicios]
    else:
        # Todas las combinaciones tantas veces como quepan enteras, y el
        # resto se completa con combinaciones al azar.
        reps, rem = divmod(num_ejercicios, total)
        pool = combinaciones * reps
        random.shuffle(combinaciones)
        pool.extend(combinaciones[:rem])
        random.shuffle(pool)
        lineas = pool

    fix_adjacent_dups(lineas)

    return lineas


def elegir_tabla():
    """Elige al azar la tabla de referencia de la hoja, sin repetir.

    Devuelve (tabla, salidas): `salidas` es la lista que hay que guardar
    con `guardar_salidas` una vez generado el PDF.
    """
    return elegir_sin_repetir(NUMEROS_VALIDOS, FICHERO_TABLAS_SALIDAS)
