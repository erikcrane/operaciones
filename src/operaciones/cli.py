"""Línea de comandos: un subcomando por ejercicio, más `servidor`.

    operaciones multiplicaciones 3 6 9 -o hoja.pdf
    operaciones divisiones -e
    operaciones servidor -p 8000

Los subcomandos de los ejercicios salen de `EJERCICIOS`
(`ejercicios/__init__.py`), así que un ejercicio nuevo aparece aquí solo.
"""

import argparse

from . import servidor
from .comun.enviar_email import enviar_pdf, preparar_envio
from .comun.pdf import nombre_pdf_automatico
from .ejercicios import EJERCICIOS


def anadir_argumentos_comunes(parser, clave):
    """Añade -o y -e, que tienen todos los ejercicios."""
    parser.add_argument(
        "-o",
        "--salida",
        metavar="PDF",
        help=(
            "ruta del PDF de salida (por defecto: "
            f"{clave}_<día-mes>_<hora>_<año>_<número>.pdf)"
        ),
    )
    parser.add_argument(
        "-e",
        "--email",
        action="append",
        nargs="?",
        const="",
        metavar="DIRECCION",
        help=(
            "envía el PDF por correo a esta dirección (se puede repetir); "
            "sin dirección, a los DESTINATARIOS del fichero .env"
        ),
    )


def ejecutar_ejercicio(args):
    """Genera la ficha del ejercicio elegido y, con -e, la envía por correo."""
    clave, parser = args.ejercicio, args.parser_ejercicio
    ejercicio = EJERCICIOS[clave]

    direcciones = [d for d in args.email or [] if d]
    for direccion in direcciones:
        if "@" not in direccion:
            parser.error(f"'{direccion}' no parece una dirección de correo.")

    try:
        ejercicio.comprobar(args)
    except ValueError as error:
        parser.error(str(error))

    # Con -e, los datos del correo se comprueban antes de generar nada: si
    # falta el .env o algún dato, el programa se corta sin crear el PDF ni
    # gastar un elemento de la rotación.
    envio = None
    if args.email is not None:
        envio = preparar_envio(direcciones, clave, ejercicio.NOMBRE_REMITENTE)

    ruta_pdf = args.salida or nombre_pdf_automatico(clave)
    ejercicio.crear_pdf(args, ruta_pdf)

    if envio is not None:
        enviar_pdf(*envio, ejercicio.ASUNTO_EMAIL, ejercicio.TEXTO_EMAIL, ruta_pdf)


def crear_parser():
    parser = argparse.ArgumentParser(
        prog="operaciones",
        description="Genera fichas PDF de ejercicios de matemáticas para practicar.",
        epilog=(
            "Ejemplos:\n"
            "  operaciones multiplicaciones\n"
            "  operaciones multiplicaciones 3 6 9 -o tablas.pdf\n"
            "  operaciones multiplicaciones 3 6 -e\n"
            "  operaciones divisiones -e alguien@gmail.com\n"
            "  operaciones servidor -p 8000\n\n"
            "Ayuda de cada orden: operaciones <orden> -h"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ordenes = parser.add_subparsers(title="órdenes", metavar="ORDEN", required=True)

    for clave, ejercicio in EJERCICIOS.items():
        sub = ordenes.add_parser(
            clave, help=ejercicio.DESCRIPCION, description=ejercicio.DESCRIPCION
        )
        ejercicio.anadir_argumentos(sub)
        anadir_argumentos_comunes(sub, clave)
        sub.set_defaults(funcion=ejecutar_ejercicio, ejercicio=clave, parser_ejercicio=sub)

    sub = ordenes.add_parser(
        "servidor",
        help="arranca la página web con un botón por ejercicio",
        description=servidor.__doc__.splitlines()[0],
    )
    servidor.anadir_argumentos(sub)
    sub.set_defaults(funcion=servidor.arrancar)

    return parser


def main(argv=None):
    args = crear_parser().parse_args(argv)
    args.funcion(args)
