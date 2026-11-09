"""Ejercicio «multiplicaciones»: 10 problemas con temática de perros.

Este fichero es la «ficha de identidad» del ejercicio que usan la línea de
comandos y el servidor (ver `operaciones/ejercicios/__init__.py`).
"""

from operaciones.comun.rotacion import guardar_salidas

from .generar import (
    FICHERO_TABLAS_SALIDAS,
    NUM_EJERCICIOS,
    NUMEROS_VALIDOS,
    elegir_tabla,
    generar_lineas,
    tabla_valida,
    tablas_pedidas,
)
from .pdf import mostrar_salida, preparar_emojis, validar_datos

# Texto del botón de la página web.
NOMBRE = "Multiplicaciones"

# Descripción para la ayuda de la línea de comandos.
DESCRIPCION = "Genera multiplicaciones con enunciados de temática perruna."

# Correo que se envía con la opción -e (el PDF va adjunto). NOMBRE_REMITENTE
# es el nombre que ve el destinatario; la dirección es la común del .env.
NOMBRE_REMITENTE = "Patitas Felices"
ASUNTO_EMAIL = "Ficha de multiplicaciones"
TEXTO_EMAIL = (
    "¡Hola!\n\n"
    "Te envío una nueva ficha de multiplicaciones de la tienda Patitas Felices.\n\n"
    "¡Mucho ánimo!"
)


def anadir_argumentos(parser):
    """Argumentos propios: las tablas que salen en los problemas."""
    parser.add_argument(
        "tablas",
        nargs="*",
        type=tabla_valida,
        metavar="tabla",
        help=(
            "tablas del 2 al 9 (si no se indica ninguna, se usan todas). "
            "Si usas -e sin dirección, ponlo después de las tablas"
        ),
    )


def comprobar(args):
    """Comprueba los datos antes de generar nada (ValueError si algo falla)."""
    validar_datos()


def crear_pdf(args, ruta_pdf):
    """Genera los problemas, elige la tabla, crea el PDF y guarda la rotación."""
    preparar_emojis()
    lineas = generar_lineas(tablas_pedidas(args.tablas), NUM_EJERCICIOS)
    tabla, salidas = elegir_tabla()
    mostrar_salida(lineas, tabla, NUMEROS_VALIDOS, ruta_pdf)
    guardar_salidas(FICHERO_TABLAS_SALIDAS, salidas)
