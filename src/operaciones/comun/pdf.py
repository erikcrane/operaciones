"""Piezas de PDF que comparten todos los ejercicios.

Cada ejercicio dibuja su ficha en su propio `pdf.py`; aquí solo está lo que
es igual en todas: registrar las fuentes, la página A4, la cabecera (título
y texto de introducción) y el nombre automático de los PDF.
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate

# Carpeta del paquete `operaciones`. Las fuentes .ttf se indican con una
# ruta relativa a ella, por ejemplo "fonts/Fredoka-SemiBold.ttf".
CARPETA_PAQUETE = Path(__file__).resolve().parent.parent

# Márgenes por defecto de la página A4.
MARGEN_LATERAL = 20 * mm
MARGEN_VERTICAL = 18 * mm


def registrar_fuente(fuente):
    """Devuelve el nombre de fuente que entiende reportlab.

    `fuente` puede ser una fuente estándar de PDF ("Helvetica",
    "Times-Roman", "Courier") o la ruta a un .ttf relativa a la carpeta del
    paquete ("fonts/Anton-Regular.ttf"). Las estándar se devuelven tal
    cual. Los .ttf se registran con el nombre del fichero; como la mayoría
    de fuentes decorativas no tienen negrita ni cursiva, se usa el mismo
    fichero para todas (así funciona la etiqueta <b>). Si no se encuentra
    el fichero, el programa termina con un error.
    """
    if not fuente.lower().endswith(".ttf"):
        return fuente

    ruta = CARPETA_PAQUETE / fuente
    if not ruta.exists():
        sys.exit(f"No se encuentra la fuente {ruta}")

    nombre = ruta.stem
    pdfmetrics.registerFont(TTFont(nombre, str(ruta)))
    pdfmetrics.registerFontFamily(
        nombre, normal=nombre, bold=nombre, italic=nombre, boldItalic=nombre
    )
    return nombre


def documento_a4(ruta_pdf, titulo, margen_superior=MARGEN_VERTICAL,
                 margen_inferior=MARGEN_VERTICAL):
    """Devuelve el documento A4 de reportlab en el que se escribe la ficha.

    `titulo` es el título interno del PDF (el que muestra el visor).
    """
    return SimpleDocTemplate(
        str(ruta_pdf),
        pagesize=A4,
        leftMargin=MARGEN_LATERAL,
        rightMargin=MARGEN_LATERAL,
        topMargin=margen_superior,
        bottomMargin=margen_inferior,
        title=titulo,
        author="operaciones",
    )


def parrafos_cabecera(titulo, texto, fuente_titulo, fuente_texto, tamano,
                      separacion_titulo, separacion_texto):
    """Devuelve los párrafos de la cabecera de la ficha.

    El título va centrado y 1,6 veces más grande que `tamano`; el texto de
    introducción, justificado. `separacion_titulo` es el espacio entre el
    título y el texto, y `separacion_texto` el que queda debajo del texto.
    Cualquiera de los dos puede ser "" para que no salga.
    """
    estilo_titulo = ParagraphStyle(
        "titulo",
        fontName=fuente_titulo,
        fontSize=tamano * 1.6,
        leading=tamano * 1.6 * 1.3,
        alignment=TA_CENTER,
        spaceAfter=separacion_titulo,
    )
    estilo_texto = ParagraphStyle(
        "introduccion",
        fontName=fuente_texto,
        fontSize=tamano,
        leading=tamano * 1.4,
        alignment=TA_JUSTIFY,
        spaceAfter=separacion_texto,
    )
    parrafos = []
    if titulo:
        parrafos.append(Paragraph(escape(titulo), estilo_titulo))
    if texto:
        parrafos.append(Paragraph(escape(texto), estilo_texto))
    return parrafos


def nombre_pdf_automatico(prefijo, carpeta=Path(".")):
    """Devuelve la ruta del siguiente PDF numerado dentro de `carpeta`.

    El nombre es <prefijo>_<día-mes>_<hora>_<año>_<número>.pdf, por ejemplo
    divisiones_08-11_14h30_2026_001.pdf. El número sigue al más alto que ya
    haya en la carpeta con ese prefijo y no se reinicia.
    """
    patron = re.compile(rf"^{re.escape(prefijo)}_.*_(\d+)\.pdf$")
    numeros = [
        int(coincidencia.group(1))
        for fichero in carpeta.glob(f"{prefijo}_*.pdf")
        if (coincidencia := patron.match(fichero.name))
    ]
    siguiente = max(numeros, default=0) + 1
    ahora = datetime.now()
    nombre = f"{prefijo}_{ahora:%d-%m}_{ahora:%Hh%M}_{ahora:%Y}_{siguiente:03d}.pdf"
    return carpeta / nombre
