"""Ejercicio «divisiones»: 6 divisiones con decimales, con temática de Fortnite.

Este fichero es la «ficha de identidad» del ejercicio que usan la línea de
comandos y el servidor (ver `operaciones/ejercicios/__init__.py`).
"""

from operaciones.comun.rotacion import guardar_salidas

from .generar import (
    FICHERO_CABECERAS_SALIDAS,
    NUM_EJERCICIOS,
    elegir_cabecera,
    generar_divisiones,
    validar_cabeceras,
)
from .pdf import mostrar_salida

# Texto del botón de la página web.
NOMBRE = "Divisiones"

# Descripción para la ayuda de la línea de comandos.
DESCRIPCION = f"Genera una ficha PDF con {NUM_EJERCICIOS} divisiones con decimales."

# Correo que se envía con la opción -e (el PDF va adjunto). NOMBRE_REMITENTE
# es el nombre que ve el destinatario; la dirección es la común del .env.
NOMBRE_REMITENTE = "Batalla Fortnite"
ASUNTO_EMAIL = "¡Nueva misión: ficha de divisiones!"
TEXTO_EMAIL = (
    "¡Hola, jugador!\n\n"
    "El autobús de batalla está a punto de despegar y tu equipo te "
    "necesita. Te envío una nueva ficha con 6 divisiones: resuélvelas para "
    "calcular los materiales de tus construcciones y protegerte de los "
    "enemigos.\n\n"
    "Recuerda: si el divisor tiene decimales, primero corre la coma para "
    "que desaparezca, y corre la del dividendo el mismo número de lugares.\n\n"
    "¡Mucha suerte y a por la victoria magistral!"
)


def anadir_argumentos(parser):
    """Divisiones no tiene argumentos propios (solo los comunes -o y -e)."""


def comprobar(args):
    """Comprueba los datos antes de generar nada (ValueError si algo falla)."""
    validar_cabeceras()


def crear_pdf(args, ruta_pdf):
    """Genera las divisiones, elige la cabecera, crea el PDF y guarda la rotación."""
    divisiones = generar_divisiones(NUM_EJERCICIOS)
    cabecera, salidas = elegir_cabecera()
    mostrar_salida(divisiones, cabecera, ruta_pdf)
    guardar_salidas(FICHERO_CABECERAS_SALIDAS, salidas)
