"""Generación «en bruto» de las divisiones y elección de la cabecera.

Reglas:
  - Cada ficha tiene siempre NUM_EJERCICIOS (6) divisiones.
  - El dividendo tiene siempre tres cifras enteras y dos decimales
    (de 100,01 a 999,99).
  - El divisor tiene siempre dos cifras enteras y dos decimales
    (de 10,01 a 99,99).
  - "Dos decimales" de verdad: la cifra de las centésimas nunca es 0
    (345,60 no vale, porque en realidad es 345,6).
  - No se repite ninguna división dentro de la misma ficha.
  - La cabecera (título y texto) se elige al azar entre las de
    `cabeceras.py`, sin repetir ninguna hasta que han salido todas (ver
    `elegir_cabecera`).

Los números se guardan como enteros en centésimas (34567 = 345,67) para no
arrastrar errores de redondeo de los float. El PDF se dibuja en `pdf.py`.
"""

import random
from pathlib import Path

from operaciones.comun.rotacion import elegir_sin_repetir

from .cabeceras import CABECERAS

NUM_EJERCICIOS = 6

# Límites de cada número, en centésimas (ambos incluidos).
DIVIDENDO_MIN, DIVIDENDO_MAX = 100_00, 999_99  # 3 cifras enteras, 2 decimales
DIVISOR_MIN, DIVISOR_MAX = 10_00, 99_99  # 2 cifras enteras, 2 decimales

# Fichero donde se guardan los títulos de las cabeceras que ya han salido en
# la ronda actual. Se crea en la carpeta desde la que se ejecuta (la misma de
# los PDF; con el servidor, <CARPETA_PDFS>/divisiones). Una cabecera no se
# repite hasta que han salido todas las demás.
FICHERO_CABECERAS_SALIDAS = Path("cabeceras_salidas.json")


def numero_con_dos_decimales(minimo, maximo):
    """Número al azar en centésimas cuya cifra de las centésimas no es 0."""
    while True:
        numero = random.randint(minimo, maximo)
        if numero % 10 != 0:
            return numero


def generar_divisiones(num_ejercicios):
    """Genera las parejas (dividendo, divisor), en centésimas, sin repetir."""
    divisiones = []
    while len(divisiones) < num_ejercicios:
        pareja = (
            numero_con_dos_decimales(DIVIDENDO_MIN, DIVIDENDO_MAX),
            numero_con_dos_decimales(DIVISOR_MIN, DIVISOR_MAX),
        )
        if pareja not in divisiones:
            divisiones.append(pareja)
    return divisiones


def validar_cabeceras():
    """Comprueba que no haya dos cabeceras con el mismo título.

    El título es lo que identifica a cada cabecera en el fichero de las que
    ya han salido, así que no puede repetirse (tampoco puede haber dos con
    el título vacío).
    """
    vistos = set()
    for titulo, _texto in CABECERAS:
        if titulo in vistos:
            raise ValueError(
                f"Hay dos cabeceras con el título {titulo!r} en cabeceras.py: "
                "cada cabecera debe tener un título distinto."
            )
        vistos.add(titulo)


def elegir_cabecera():
    """Elige al azar la cabecera (título, texto) de la ficha, sin repetir.

    Devuelve (cabecera, salidas): `salidas` es la lista de títulos que hay
    que guardar con `guardar_salidas` una vez generado el PDF.
    """
    textos = dict(CABECERAS)
    titulo, salidas = elegir_sin_repetir(textos, FICHERO_CABECERAS_SALIDAS)
    return (titulo, textos[titulo]), salidas
