"""Servidor web mínimo para generar las fichas desde el navegador.

Sirve `index.html`, que muestra un botón por cada ejercicio de `EJERCICIOS`.
Al pulsar uno, ejecuta `python -m operaciones <ejercicio> -e` (genera el PDF
y lo envía a los DESTINATARIOS del fichero .env).

Lo que escribe el programa por consola (el PDF generado, lo que ha salido en
la rotación, el resultado del correo o el error) se muestra solo en la
consola del servidor (en Docker, en el log del contenedor), nunca en la
página web.

Uso:
    uv run operaciones servidor            # escucha en el puerto 80 (el de Docker)
    uv run operaciones servidor -p 8000    # fuera de Docker: sin root no se puede usar el 80
"""

import json
import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .ejercicios import EJERCICIOS

PAGINA = Path(__file__).resolve().parent / "index.html"

# Carpeta donde se guardan los PDF generados, con una subcarpeta por
# ejercicio (pdfs/multiplicaciones, pdfs/divisiones...), donde también va su
# fichero de rotación. Por defecto, "pdfs" dentro de la carpeta desde la que
# se arranca el servidor; en Docker se cambia con la variable de entorno
# CARPETA_PDFS (un volumen).
CARPETA_PDFS = Path(os.environ.get("CARPETA_PDFS", "pdfs")).resolve()

# Segundos que hay que esperar, después de generar una ficha, antes de poder
# generar (y enviar por email) otra. Es común a todos los ejercicios. Evita
# mandar muchos emails por error.
ESPERA_SEGUNDOS = 20

# Segundos como máximo que puede tardar en generarse y enviarse una ficha.
LIMITE_SEGUNDOS = 120

# Evita que dos pulsaciones seguidas lancen el programa a la vez.
cerrojo = threading.Lock()

# Momento (reloj monotónico) en que terminó la última generación.
ultima_generacion = None


def segundos_restantes():
    """Segundos que faltan para poder generar otra ficha (0 si ya se puede)."""
    if ultima_generacion is None:
        return 0
    return max(0, ESPERA_SEGUNDOS - (time.monotonic() - ultima_generacion))


class Manejador(BaseHTTPRequestHandler):
    def _responder(self, codigo, tipo, cuerpo):
        self.send_response(codigo)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(cuerpo)))
        self.end_headers()
        self.wfile.write(cuerpo)

    def _responder_json(self, codigo, datos):
        # "espera": segundos que faltan para poder volver a generar; la página
        # lo usa para la cuenta atrás de los botones.
        datos = {**datos, "espera": round(segundos_restantes())}
        cuerpo = json.dumps(datos, ensure_ascii=False).encode()
        self._responder(codigo, "application/json; charset=utf-8", cuerpo)

    def _responder_mensaje(self, codigo, mensaje):
        self._responder_json(codigo, {"mensaje": mensaje})

    def do_GET(self):
        if self.path in ("/", "/index.html"):
            self._responder(200, "text/html; charset=utf-8", PAGINA.read_bytes())
        elif self.path == "/ejercicios":
            # Lista de botones de la página, en el orden de EJERCICIOS.
            lista = [
                {"clave": clave, "nombre": ejercicio.NOMBRE}
                for clave, ejercicio in EJERCICIOS.items()
            ]
            self._responder_json(200, {"ejercicios": lista})
        else:
            self._responder(404, "text/plain; charset=utf-8", b"No encontrado")

    def do_POST(self):
        global ultima_generacion
        prefijo = "/generar/"
        clave = self.path[len(prefijo):] if self.path.startswith(prefijo) else None
        # Solo se ejecutan ejercicios de la lista: nunca lo que llegue en la
        # dirección tal cual.
        if clave not in EJERCICIOS:
            self._responder_mensaje(404, "Ese ejercicio no existe.")
            return
        nombre = EJERCICIOS[clave].NOMBRE.lower()

        if not cerrojo.acquire(blocking=False):
            self._responder_mensaje(409, "Ya se está generando una ficha, espera un momento.")
            return
        if segundos_restantes() > 0:
            cerrojo.release()
            self._responder_mensaje(429, "Espera un poco antes de generar otra ficha.")
            return
        try:
            carpeta = CARPETA_PDFS / clave
            carpeta.mkdir(parents=True, exist_ok=True)
            resultado = subprocess.run(
                [sys.executable, "-m", "operaciones", clave, "-e"],
                cwd=carpeta,
                capture_output=True,
                text=True,
                timeout=LIMITE_SEGUNDOS,
            )
        except subprocess.TimeoutExpired:
            print(f"[{clave}] cancelado: tardó más de {LIMITE_SEGUNDOS} s",
                  file=sys.stderr, flush=True)
            self._responder_mensaje(500, "Ha tardado demasiado y se ha cancelado.")
            return
        finally:
            # La espera cuenta desde que termina, haya ido bien o no.
            ultima_generacion = time.monotonic()
            cerrojo.release()

        # La salida del programa (PDF generado, rotación, correo enviado o
        # error) va solo a la consola del servidor / log de Docker.
        if resultado.returncode == 0:
            print(resultado.stdout, end="", flush=True)
            self._responder_mensaje(200, f"¡Ficha de {nombre} generada y enviada!")
        else:
            print(resultado.stdout, resultado.stderr, sep="", end="",
                  file=sys.stderr, flush=True)
            self._responder_mensaje(
                500, f"Error al generar la ficha de {nombre} (mira el log del servidor)."
            )


def anadir_argumentos(parser):
    parser.add_argument("-p", "--puerto", type=int, default=80,
                        help="puerto en el que escuchar (por defecto 80)")


def arrancar(args):
    """Arranca el servidor para toda la red local. Se para con Ctrl+C."""
    CARPETA_PDFS.mkdir(parents=True, exist_ok=True)

    # 0.0.0.0 para que se pueda abrir desde otros dispositivos de la red (móvil, tablet).
    servidor = ThreadingHTTPServer(("0.0.0.0", args.puerto), Manejador)
    print(f"Servidor en http://localhost:{args.puerto}  (PDF en {CARPETA_PDFS}; Ctrl+C para parar)",
          flush=True)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
