"""Elección al azar sin repetir, con lo que ya ha salido guardado en un JSON.

La usan los ejercicios para lo que debe ir rotando de una ficha a otra (la
tabla de referencia de multiplicaciones, la cabecera de divisiones...):

  - Solo se elige entre los candidatos que aún no han salido en la ronda.
  - Cuando ya han salido todos, empieza una ronda nueva, pero sin repetir
    el último que salió (así nunca hay dos fichas seguidas con lo mismo).
  - Lo que ya ha salido se apunta en un fichero JSON, que se guarda solo
    cuando el PDF ya está creado (`guardar_salidas`). Así, si algo falla,
    no se gasta un candidato de la ronda.

Los candidatos son las claves que identifican a cada elemento (números o
textos que se puedan guardar en JSON), y no pueden repetirse.
"""

import json
import random


def leer_salidas(fichero, candidatos):
    """Devuelve la lista de candidatos que ya han salido en la ronda.

    Si el fichero no existe o está estropeado, se empieza una ronda nueva.
    Lo que ya no está entre los candidatos (porque se ha quitado o
    cambiado) se ignora.
    """
    try:
        datos = json.loads(fichero.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(datos, list):
        return []
    return [salido for salido in datos if salido in candidatos]


def guardar_salidas(fichero, salidas):
    """Guarda la lista de lo que ya ha salido en la ronda."""
    fichero.write_text(json.dumps(salidas, ensure_ascii=False, indent=1), encoding="utf-8")


def elegir_sin_repetir(candidatos, fichero):
    """Elige al azar uno de los `candidatos` que aún no haya salido.

    Devuelve (elegido, salidas): `salidas` es la lista que hay que guardar
    con `guardar_salidas` una vez generado el PDF.
    """
    candidatos = list(candidatos)
    salidas = leer_salidas(fichero, candidatos)
    pendientes = [candidato for candidato in candidatos if candidato not in salidas]

    if not pendientes:
        ultimo = salidas[-1]
        pendientes = [candidato for candidato in candidatos if candidato != ultimo]
        salidas = []

    # Si solo hubiera un candidato, no queda otra que repetirlo.
    elegido = random.choice(pendientes or candidatos)
    return elegido, salidas + [elegido]

