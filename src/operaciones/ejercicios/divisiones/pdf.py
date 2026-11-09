"""PDF de la ficha de divisiones.

Recibe las parejas (dividendo, divisor), en centésimas, ya generadas en
`generar.py` y las escribe en un PDF.

La hoja empieza con una cabecera (título y texto de introducción) con
temática de Fortnite (elegida en `generar.py`), seguida de una cuadrícula de
2 columnas x 3 filas con una división en cada celda, dibujada con su caja y
con sitio debajo para resolverla a mano (con el lápiz de una tablet).
"""

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Flowable, Table, TableStyle

from operaciones.comun.pdf import documento_a4, parrafos_cabecera, registrar_fuente

# Fuentes de la hoja. Cada una puede ser:
#   - una fuente estándar de PDF: "Helvetica", "Times-Roman" o "Courier";
#   - la ruta a un fichero .ttf, relativa a la carpeta del paquete.
# Fuentes incluidas (las dos con licencia libre SIL OFL, ver fonts/OFL-*.txt):
#   - "fonts/Fredoka-SemiBold.ttf": redondeada, muy legible.
#   - "fonts/Anton-Regular.ttf": gruesa y estrecha, la alternativa libre más
#     parecida a la de Fortnite (Burbank Big Condensed, que es de pago).
FUENTE_TITULO = "fonts/Anton-Regular.ttf"
FUENTE_TEXTO = "fonts/Anton-Regular.ttf"  # texto de la cabecera
FUENTE_DIVISIONES = "fonts/Fredoka-SemiBold.ttf"

# Tamaño de la letra, en puntos.
TAMANO_TEXTO = 13.5

# Márgenes de la página, en puntos. El de arriba está una línea de texto
# (TAMANO_TEXTO * 1.4) por encima de los 18 mm del resto, para que la
# cabecera suba y deje más aire sobre las divisiones.
MARGEN_SUPERIOR = 18 * mm - TAMANO_TEXTO * 1.4
MARGEN_INFERIOR = 18 * mm

# Espacio entre el título y el texto de la cabecera, y entre la cabecera y
# la cuadrícula de divisiones, en puntos.
SEPARACION_TITULO = TAMANO_TEXTO * 1.2
SEPARACION_CABECERA = TAMANO_TEXTO * 4

# --- Maqueta de las divisiones ----------------------------------------------
# Las 6 divisiones van en una cuadrícula de COLUMNAS x FILAS que ocupa todo
# el espacio de la página que queda debajo de la cabecera. Cada división va
# en la parte de arriba de su celda; el resto de la celda queda libre para
# hacer la cuenta con el lápiz de la tablet.
COLUMNAS = 2
FILAS = 3

# Tamaño de "toda" la división: es el tamaño de la letra de los números, y
# el grosor y largo de las líneas de la caja se ajustan solos a él.
TAMANO_DIVISION = TAMANO_TEXTO * 1.8

# Dónde está la línea vertical de la caja, en proporción al ancho de la
# celda: a la izquierda queda el dividendo (y el sitio para ir restando) y a
# la derecha el divisor (y debajo, el cociente).
POSICION_CAJA = 0.55

# Margen interior de cada celda, en puntos.
MARGEN_CELDA = 8

# Color de las líneas que separan las celdas (None para no dibujarlas) y de
# las líneas de la caja de la división.
COLOR_CUADRICULA = colors.HexColor("#BBBBBB")
COLOR_CAJA = colors.black


def formatear_numero(centesimas):
    """Convierte 34567 en "345,67" (coma decimal, como en el cole)."""
    enteros, decimales = divmod(centesimas, 100)
    return f"{enteros},{decimales:02d}"


def mostrar_salida(divisiones, cabecera, ruta_pdf):
    """Convierte cada pareja (dividendo, divisor) en texto y genera el PDF.

    `cabecera` es la pareja (título, texto) elegida en `generar.py`.

    Es el único punto de salida del ejercicio: si se cambia el destino (otro
    formato, otra maqueta...), solo hay que tocar este módulo.
    """
    ejercicios = [
        (formatear_numero(dividendo), formatear_numero(divisor))
        for dividendo, divisor in divisiones
    ]
    titulo, texto = cabecera
    generar_pdf(titulo, texto, ejercicios, ruta_pdf)
    print(f"PDF generado: {ruta_pdf} (cabecera: {titulo or texto[:40]})")


class DivisionCaja(Flowable):
    """Una división dibujada con su caja, a todo el ancho de la celda.

        345,67      │ 12,34
                    └────────────
                       (cociente)

    El dividendo va a la izquierda; la caja es una "L": la línea vertical,
    en POSICION_CAJA del ancho, baja por la izquierda del divisor solo hasta
    la línea horizontal, que va bajo el divisor hasta el borde derecho.
    """

    def __init__(self, dividendo, divisor, fuente):
        super().__init__()
        self.dividendo = dividendo
        self.divisor = divisor
        self.fuente = fuente
        self.tamano = TAMANO_DIVISION

    def wrap(self, ancho_disponible, alto_disponible):
        self.width = ancho_disponible
        self.height = self.tamano * 1.15
        return self.width, self.height

    def draw(self):
        lienzo = self.canv
        tamano = self.tamano
        hueco = tamano * 0.4

        # Línea base del texto: la parte de arriba de las cifras queda
        # justo en el borde superior de la división.
        base = self.height - tamano * 0.75
        x_caja = self.width * POSICION_CAJA

        lienzo.setFillColor(colors.black)
        lienzo.setFont(self.fuente, tamano)
        lienzo.drawString(0, base, self.dividendo)
        lienzo.drawString(x_caja + hueco, base, self.divisor)

        # La caja en "L": vertical a la izquierda del divisor, que termina
        # en la horizontal de debajo del divisor.
        lienzo.setStrokeColor(COLOR_CAJA)
        lienzo.setLineWidth(max(1, tamano * 0.07))
        lienzo.setLineCap(1)  # extremos redondeados
        y_horizontal = base - tamano * 0.35
        lienzo.line(x_caja, self.height, x_caja, y_horizontal)
        lienzo.line(x_caja, y_horizontal, self.width, y_horizontal)


def cuadricula_divisiones(ejercicios, fuente, ancho, alto):
    """Devuelve la tabla de COLUMNAS x FILAS con una división en cada celda."""
    celdas = [
        DivisionCaja(dividendo, divisor, fuente)
        for dividendo, divisor in ejercicios
    ]
    celdas += [""] * (COLUMNAS * FILAS - len(celdas))
    filas = [celdas[i : i + COLUMNAS] for i in range(0, len(celdas), COLUMNAS)]

    estilo = [
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), MARGEN_CELDA),
        ("RIGHTPADDING", (0, 0), (-1, -1), MARGEN_CELDA),
        ("TOPPADDING", (0, 0), (-1, -1), MARGEN_CELDA),
        ("BOTTOMPADDING", (0, 0), (-1, -1), MARGEN_CELDA),
    ]
    if COLOR_CUADRICULA is not None:
        estilo.append(("INNERGRID", (0, 0), (-1, -1), 0.75, COLOR_CUADRICULA))
        estilo.append(("BOX", (0, 0), (-1, -1), 0.75, COLOR_CUADRICULA))

    tabla = Table(
        filas,
        colWidths=[ancho / COLUMNAS] * COLUMNAS,
        rowHeights=[alto / len(filas)] * len(filas),
    )
    tabla.setStyle(TableStyle(estilo))
    return tabla


def generar_pdf(titulo, texto, ejercicios, ruta_pdf):
    """Escribe la cabecera (título y texto) y las divisiones en un PDF.

    El título se escribe siempre en mayúsculas, al estilo Fortnite. El
    título o el texto pueden ser "" para que esa parte no salga.
    """
    fuente_divisiones = registrar_fuente(FUENTE_DIVISIONES)
    documento = documento_a4(
        ruta_pdf,
        "Ficha de divisiones",
        margen_superior=MARGEN_SUPERIOR,
        margen_inferior=MARGEN_INFERIOR,
    )
    historia = parrafos_cabecera(
        titulo.upper(),
        texto,
        registrar_fuente(FUENTE_TITULO),
        registrar_fuente(FUENTE_TEXTO),
        TAMANO_TEXTO,
        SEPARACION_TITULO,
        SEPARACION_CABECERA,
    )

    # La cuadrícula ocupa todo lo que queda de página debajo de la cabecera.
    # El marco de la página tiene 6 puntos de margen interior por cada lado.
    ancho = documento.width - 12
    alto = documento.height - 12
    for parrafo in historia:
        alto -= parrafo.wrap(ancho, alto)[1] + parrafo.getSpaceAfter()
    historia.append(cuadricula_divisiones(ejercicios, fuente_divisiones, ancho, alto - 1))

    documento.build(historia)
