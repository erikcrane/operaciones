"""Lista de ejercicios disponibles.

La línea de comandos crea un subcomando por cada ejercicio de `EJERCICIOS`,
y la página web, un botón. El orden del diccionario es el de los botones.

Para añadir un ejercicio nuevo:
  1. Crea su carpeta en `ejercicios/` (copia la de divisiones como modelo).
  2. En su `__init__.py` define lo que se describe abajo.
  3. Añádelo a `EJERCICIOS`. La clave es su nombre interno: se usa en la
     línea de comandos (`operaciones <clave>`), en la dirección del
     servidor (`/generar/<clave>`), como prefijo de los PDF, como carpeta
     de sus PDF en el servidor y, en mayúsculas, como prefijo de sus
     destinatarios en el .env (`<CLAVE>_DESTINATARIOS`). Solo letras minúsculas,
     sin espacios ni tildes.
No hace falta tocar nada más (ni el servidor, ni el email, ni la web).

Lo que tiene que definir cada ejercicio:
  NOMBRE                    texto del botón de la web
  DESCRIPCION               ayuda de la línea de comandos
  NOMBRE_REMITENTE          nombre del remitente que ve el destinatario
                            ("" para usar el NOMBRE_REMITENTE del .env)
  ASUNTO_EMAIL, TEXTO_EMAIL correo que se envía con -e
  anadir_argumentos(parser) argumentos propios, además de -o y -e (puede
                            no añadir ninguno)
  comprobar(args)           comprueba los datos antes de generar nada;
                            lanza ValueError con un mensaje si algo falla
  crear_pdf(args, ruta_pdf) genera la ficha en `ruta_pdf` y guarda su
                            rotación (si la tiene) en la carpeta actual
"""

from . import divisiones, multiplicaciones

EJERCICIOS = {
    "multiplicaciones": multiplicaciones,
    "divisiones": divisiones,
}
