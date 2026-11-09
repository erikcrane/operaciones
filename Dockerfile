FROM python:3.13-slim

# tzdata para que la hora de los nombres de los PDF sea la local (ver TZ en docker-compose.yml).
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata \
    && rm -rf /var/lib/apt/lists/*

# uv, la misma versión que se usa para desarrollar (para instalar
# exactamente las versiones de uv.lock).
COPY --from=ghcr.io/astral-sh/uv:0.13.6 /uv /bin/uv

WORKDIR /app

# Se instala el paquete (no editable) en /app/.venv con las versiones
# exactas de uv.lock. Primero solo las dependencias, para que Docker las
# guarde en caché y no las reinstale cada vez que cambia el código.
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --locked --no-dev --no-install-project
COPY src/ src/
RUN uv sync --locked --no-dev --no-editable

# Carpeta de los PDF y de la rotación de cada ejercicio (una subcarpeta por
# ejercicio). En docker-compose.yml se monta en ella el volumen
# "operaciones_pdfs" para que no se pierdan al recrear el contenedor. Con
# permisos para cualquier usuario, porque el contenedor no corre como root
# (ver "user:" en docker-compose.yml); el volumen copia estos permisos al
# crearse.
RUN mkdir -p /app/pdfs && chmod 777 /app/pdfs

# PYTHONUNBUFFERED para que los mensajes (PDF generado, lo que ha salido en
# la rotación, correo enviado) salgan al momento en el log del contenedor.
ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    CARPETA_PDFS=/app/pdfs

EXPOSE 80
CMD ["operaciones", "servidor"]
