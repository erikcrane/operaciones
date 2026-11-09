# Ayuda del proyecto «operaciones»

Referencia técnica: qué hace cada fichero, cada constante y cada función.
Para saber qué es el proyecto, cómo se instala y cómo se usa, mira el
**[README.md](README.md)**.

Este proyecto une los antiguos proyectos `multiplicaciones` y `divisiones`
en un solo programa con un solo servidor web. Las fichas que genera son
idénticas a las que generaban ellos.

## Cómo encajan los ficheros

Todo el código está en el paquete `src/operaciones/`:

```
cli.py                  main(): un subcomando por ejercicio, más «servidor»
  │
  ├── ejercicios/__init__.py   EJERCICIOS: la lista de ejercicios
  │     ├── multiplicaciones/  __init__.py (ficha de identidad), generar.py,
  │     │                      pdf.py, situaciones.py, emojis/
  │     └── divisiones/        __init__.py (ficha de identidad), generar.py,
  │                            pdf.py, cabeceras.py
  │
  ├── comun/
  │     ├── enviar_email.py    envía el PDF por correo (opción -e)
  │     ├── pdf.py             fuentes, página A4, cabecera, nombre de los PDF
  │     └── rotacion.py        elegir al azar sin repetir (tabla, cabecera...)
  │
  └── servidor.py + index.html página web: un botón por ejercicio, que
                               ejecuta «python -m operaciones <ejercicio> -e»

fonts/                  fuentes compartidas (Anton, Fredoka) y sus licencias
```

La idea general:

- **Nada pregunta «qué botón se ha pulsado»**: no hay ningún
  `if ejercicio == ...`. Cada ejercicio se presenta con la misma «ficha de
  identidad» (su `__init__.py`) y está en la lista `EJERCICIOS`. A partir de
  esa lista se crean los subcomandos, los botones y las direcciones del
  servidor.
- **El correo es uno solo** para todos: recibe el PDF, el asunto y el texto,
  y no sabe de qué ejercicio es (salvo para elegir sus destinatarios en el
  `.env`).
- **El PDF tiene una parte común** (`comun/pdf.py`) y **un dibujo propio por
  ejercicio** (`ejercicios/<ejercicio>/pdf.py`), porque cada ficha tiene una
  maqueta distinta.

---

## `ejercicios/__init__.py`

Contiene `EJERCICIOS`, un diccionario `{clave: módulo del ejercicio}`. El
orden del diccionario es el orden de los botones de la web.

La **clave** es el nombre interno del ejercicio (`"multiplicaciones"`,
`"divisiones"`). Se usa en:
- la línea de comandos (`operaciones <clave>`);
- la dirección del servidor (`/generar/<clave>`);
- el prefijo del nombre de los PDF;
- la subcarpeta de sus PDF en el servidor (`pdfs/<clave>/`);
- en mayúsculas, el prefijo de sus destinatarios en el `.env`
  (`<CLAVE>_DESTINATARIOS`).

Por eso tiene que ir en minúsculas, sin espacios ni tildes.

Lo que tiene que definir el `__init__.py` de cada ejercicio:

| Nombre | Para qué sirve |
|---|---|
| `NOMBRE` | Texto del botón de la página web. |
| `DESCRIPCION` | Descripción del subcomando en la ayuda (`-h`). |
| `NOMBRE_REMITENTE` | Nombre con el que llega el correo («Patitas Felices», «Batalla Fortnite»). La dirección es la común del `.env`. Con `""` se usa el `NOMBRE_REMITENTE` del `.env`. |
| `ASUNTO_EMAIL`, `TEXTO_EMAIL` | Asunto y texto del correo que se envía con `-e`. |
| `anadir_argumentos(parser)` | Añade los argumentos propios del ejercicio. Los comunes (`-o` y `-e`) los añade `cli.py`. Puede no añadir ninguno. |
| `comprobar(args)` | Comprueba los datos antes de generar nada. Si algo está mal, lanza `ValueError` con un mensaje, y la línea de comandos lo muestra como error. |
| `crear_pdf(args, ruta_pdf)` | Genera los números, elige lo que rota, crea el PDF en `ruta_pdf` y, cuando el PDF ya existe, guarda la rotación en la carpeta actual. |

---

## `cli.py`

La línea de comandos. Se ejecuta con `uv run operaciones ...` o con
`python -m operaciones ...` (`__main__.py`); el servidor usa esta segunda
forma.

| Función | Qué hace |
|---|---|
| `anadir_argumentos_comunes(parser, clave)` | Añade a un ejercicio las opciones que tienen todos: `-o` (ruta del PDF) y `-e` (enviar por correo; se puede repetir, y sin dirección usa los destinatarios del `.env`). |
| `ejecutar_ejercicio(args)` | Lo que pasa al generar una ficha. Comprueba que las direcciones de `-e` tengan `@` y llama a `comprobar` del ejercicio. Si se usó `-e`, comprueba los datos del correo con `preparar_envio`; si falta algo, termina sin generar nada ni gastar un elemento de la rotación. Después decide el nombre del PDF, llama a `crear_pdf` del ejercicio y, con `-e`, envía el PDF. |
| `crear_parser()` | Crea los subcomandos: uno por cada ejercicio de `EJERCICIOS` (con sus argumentos propios y los comunes) y `servidor`. |
| `main(argv=None)` | Lee los argumentos y ejecuta el subcomando elegido. |

`__init__.py` (del paquete) tiene un `main()` que llama a este. Es el que
ejecuta el comando `operaciones` (ver `[project.scripts]` en
`pyproject.toml`).

---

## `comun/rotacion.py`

Elige al azar sin repetir. Lo usan la tabla de referencia de
multiplicaciones y la cabecera de divisiones:

- Solo se elige entre los candidatos que aún no han salido en la ronda.
- Cuando han salido todos, empieza una ronda nueva, y su primer elegido
  nunca es el último que salió. Así nunca hay dos fichas seguidas con lo
  mismo.
- Lo que ya ha salido se apunta en un fichero JSON en la carpeta desde la
  que se ejecuta, la misma de los PDF.

| Función | Qué hace |
|---|---|
| `leer_salidas(fichero, candidatos)` | Devuelve la lista de lo que ya ha salido en la ronda. Si el fichero no existe o está estropeado, devuelve una lista vacía (ronda nueva). Ignora lo que ya no está entre los candidatos. |
| `guardar_salidas(fichero, salidas)` | Guarda esa lista en el fichero. Los ejercicios la llaman solo cuando el PDF ya está creado. |
| `elegir_sin_repetir(candidatos, fichero)` | Elige al azar entre los que aún no han salido, siguiendo las reglas de arriba. Devuelve `(elegido, salidas)`: el elegido y la lista que hay que guardar. |

---

## `comun/pdf.py`

Las piezas de PDF que son iguales en todas las fichas.

| Nombre | Para qué sirve |
|---|---|
| `CARPETA_PAQUETE` | Carpeta del paquete `operaciones`. Las rutas de las fuentes `.ttf` son relativas a ella (`"fonts/Fredoka-SemiBold.ttf"`). |
| `MARGEN_LATERAL`, `MARGEN_VERTICAL` | Márgenes por defecto de la página: 20 mm a los lados y 18 mm arriba y abajo. |
| `registrar_fuente(fuente)` | Prepara una fuente para reportlab y devuelve su nombre. Las estándar (`"Helvetica"`...) las devuelve tal cual. Los `.ttf` los registra y usa el mismo fichero para la negrita y la cursiva, porque estas fuentes no las tienen; así funciona `<b>`. Si no encuentra el fichero, termina con un error. |
| `documento_a4(ruta_pdf, titulo, margen_superior, margen_inferior)` | Crea el documento A4 en el que se escribe la ficha. `titulo` es el título interno del PDF, el que muestra el visor. |
| `parrafos_cabecera(titulo, texto, fuente_titulo, fuente_texto, tamano, separacion_titulo, separacion_texto)` | Devuelve los párrafos de la cabecera: el título centrado (1,6 veces `tamano`) y el texto de introducción justificado. Cualquiera de los dos puede ser `""` para que no salga. |
| `nombre_pdf_automatico(prefijo, carpeta)` | Nombre del PDF cuando no se usa `-o`: `<prefijo>_<día-mes>_<hora>_<año>_<número>.pdf`. El número es uno más que el más alto que ya haya en la carpeta con ese prefijo, y no se reinicia. |

---

## `comun/enviar_email.py`

Envía el PDF por correo (SMTP de Brevo). Los datos privados (servidor,
puerto, tipo de seguridad, usuario, contraseña, remitente y destinatarios)
**no están en el código**: se leen de un fichero con el formato de
`.env.ejemplo`, que no se sube a git. Se usa uno solo, el primero que
exista:

1. `/run/secrets/operaciones_env`: en Docker, el secreto `operaciones_env`
   (ver `docker-compose.yml`).
2. El `.env` de la raíz del proyecto, junto a `pyproject.toml`: al
   ejecutarlo fuera de Docker. En un ordenador nuevo hay que copiar el
   `.env` de otro ordenador, o copiar `.env.ejemplo` como `.env` y
   rellenarlo.

Los datos se leen **solo de ese fichero**: las variables de entorno no se
usan ni se modifican, así que una variable que ya existiera en la terminal
(de otro proyecto o de una prueba antigua) no puede cambiar a quién o desde
dónde se envía el correo. Si no existe ninguno de los dos ficheros, o no se
puede leer, el programa avisa y termina.

**Destinatarios de cada ejercicio**: la cuenta SMTP y el remitente son
comunes a todos los ejercicios. Solo los destinatarios pueden cambiar: con
el nombre del ejercicio delante, en mayúsculas, `DIVISIONES_DESTINATARIOS`
se usa al enviar fichas de divisiones, y `DESTINATARIOS` en los ejercicios
que no tienen los suyos.

El fichero solo se lee cuando se usa `-e`, y se hace al principio, antes de
generar nada: si falta algo, no se crea el PDF ni se gasta un elemento de la
rotación. Sin `-e` no hace falta tener `.env`.

| Función | Qué hace |
|---|---|
| `RUTA_SECRETO`, `RUTA_ENV_PROYECTO` | Las dos rutas donde se buscan los datos privados. |
| `SERVIDOR_POR_DEFECTO`, `PUERTO_POR_DEFECTO`, `SEGURIDAD_POR_DEFECTO` | Valores que se usan si el fichero no indica `SERVIDOR_SMTP`, `PUERTO_SMTP` o `SEGURIDAD`. |
| `fichero_env()` | Devuelve la ruta que se usa: el secreto de Docker si existe y, si no, el `.env` del proyecto. |
| `cargar_env(ruta)` | Lee las líneas `CLAVE=valor` del fichero y las devuelve en un diccionario, sin tocar las variables de entorno. Ignora las líneas vacías y los comentarios, y quita las comillas del valor. Si el fichero no existe o no se puede leer, termina con un mensaje claro. |
| `leer_configuracion(ejercicio)` | Carga el fichero y devuelve la configuración del correo para ese ejercicio. Todo es común salvo los destinatarios: usa los del ejercicio (`DIVISIONES_DESTINATARIOS`) o, si no tiene, los generales (`DESTINATARIOS`). Lo que falte toma el valor por defecto. Termina con un mensaje claro si el puerto no es un número. |
| `comprobar_configuracion(configuracion, ruta)` | Comprueba que estén rellenos el usuario, la contraseña y el remitente, y que `SEGURIDAD` sea `"tls"` o `"ssl"`. Si falta algo, termina con un mensaje claro. |
| `preparar_envio(direcciones, ejercicio, nombre_remitente)` | Se llama antes de generar el PDF. Lee la configuración y decide los destinatarios: las direcciones de `-e` o, si no hay, los del fichero para ese ejercicio. Si tampoco hay, termina. `nombre_remitente` es el `NOMBRE_REMITENTE` del ejercicio y sustituye al del fichero (si está vacío, se usa el del fichero). Devuelve `(configuracion, destinatarios)`. |
| `crear_mensaje(configuracion, destinatarios, asunto, texto, ruta_pdf)` | Construye el correo con remitente, destinatarios, asunto y texto, y el PDF adjunto. |
| `enviar_pdf(configuracion, destinatarios, asunto, texto, ruta_pdf)` | Envía el correo con lo que devolvió `preparar_envio`. Se conecta con SSL o STARTTLS según `SEGURIDAD`, y avisa si falla la contraseña o la conexión. |

---

## Ejercicio `multiplicaciones`

Regla en todo el ejercicio: el 0, el 1 y el 10 nunca aparecen, ni como
tabla ni como factor.

Las tablas que se pasan como argumento solo deciden qué multiplicaciones
salen en los problemas. La tabla de referencia del final no se puede
elegir: sale al azar (ver `elegir_tabla`).

### `multiplicaciones/__init__.py`

La ficha de identidad (ver `ejercicios/__init__.py`).
- `anadir_argumentos` añade `tablas`: cero o más números del 2 al 9,
  comprobados por `tabla_valida`.
- `comprobar` llama a `validar_datos`.
- `crear_pdf` descarga los emojis que falten (`preparar_emojis`), genera
  las parejas, elige la tabla, crea el PDF y guarda la rotación.

### `multiplicaciones/generar.py`

Genera las multiplicaciones «en bruto», es decir, los números y no el texto.

| Nombre | Para qué sirve |
|---|---|
| `NUM_EJERCICIOS` | Número de problemas de la hoja (10). |
| `NUMEROS_VALIDOS` | Números permitidos como tabla y como factor: del 2 al 9. |
| `FICHERO_TABLAS_SALIDAS` | `tablas_salidas.json`, donde se apuntan las tablas de referencia que ya han salido. Se crea en la carpeta desde la que se ejecuta, la misma de los PDF. |
| `tabla_valida(valor)` | La usa argparse para cada tabla escrita en la línea de comandos. Da error si no es un número entero o no está entre el 2 y el 9. |
| `tablas_pedidas(tablas)` | Quita las tablas repetidas y, si no se indica ninguna, devuelve todas. |
| `fix_adjacent_dups(items)` | Reordena la lista para que no haya dos elementos iguales seguidos, siempre que se pueda. Cambia la lista directamente y no devuelve nada. |
| `generar_lineas(tablas, num_ejercicios)` | Crea las parejas `(tabla, factor)` de los problemas, por ejemplo `(7, 4)`. Combina las tablas pedidas con los factores del 2 al 9 y elige al azar sin repetir. Solo repite cuando no hay bastantes combinaciones distintas. Al final llama a `fix_adjacent_dups`. |
| `elegir_tabla()` | Elige la tabla de referencia del final de la hoja con `elegir_sin_repetir` (ver `comun/rotacion.py`). Devuelve `(tabla, salidas)`. |

### `multiplicaciones/pdf.py`

Convierte las parejas de números en problemas con texto y escribe el PDF.

**Constantes (ajustes del aspecto)**

| Nombre | Para qué sirve |
|---|---|
| `FUENTE_TEXTO` | Fuente del texto. Puede ser una fuente estándar de PDF (`"Helvetica"`...) o un `.ttf` de `fonts/`. |
| `TAMANO_TEXTO` | Tamaño de la letra. El interlineado, los emojis y la línea de respuesta se ajustan solos a este tamaño. |
| `SEPARACION_EJERCICIOS` | Espacio en blanco entre un problema y el siguiente. |
| `TITULO_CABECERA`, `TEXTO_CABECERA` | Título e introducción del principio de la hoja. Si se dejan en `""`, no aparecen. |
| `TITULO_TABLA` | Título de la tabla de referencia (`"Tabla del {tabla}"`). |
| `TAMANO_TABLA`, `COLOR_FONDO_TABLA`, `COLOR_BORDE_TABLA` | Tamaño de la letra y colores de la tabla de referencia. |
| `ALTURA_CIFRAS` | Alto de las cifras en proporción a la letra (0,70 en Fredoka). Sirve para centrar los números en vertical en cada fila de la tabla. Si cambias de fuente y los números quedan altos o bajos, ajústalo: un valor más alto los baja y uno más bajo los sube. |
| `CARPETA_EMOJIS`, `URL_TWEMOJI`, `TAMANO_EMOJI` | Dónde están las imágenes de los emojis (la carpeta `emojis/` junto a este fichero), de dónde se descargan y a qué tamaño se dibujan. |
| `RELACIONES_POR_CONTEXTO`, `PLANTILLAS_POR_CONTEXTO`, `CONTEXTOS` | Agrupan por contexto las relaciones y plantillas de `situaciones.py`. Así cada problema combina una relación y una frase que encajan. |

**Funciones: enunciados**

| Función | Qué hace |
|---|---|
| `datos_objeto(id_objeto)` | Devuelve `(singular, plural, género, emoji)` de un objeto de `OBJETOS`. Si el objeto no tiene emoji, el emoji es `""`. Da error si el objeto no tiene 3 o 4 datos. |
| `validar_datos()` | Comprueba que todos los objetos están bien escritos, que las relaciones usan objetos que existen y que cada contexto tiene al menos una plantilla. |
| `mostrar_salida(lineas, tabla, factores, ruta_pdf)` | Convierte cada pareja en un problema: elige al azar contexto, relación y plantilla, y rellena los números, los nombres en singular y plural y «Cuántos/Cuántas». Los emojis solo se ponen antes del `¿`, para que la pregunta se lea limpia. Después llama a `generar_pdf`. Es el único punto de salida del ejercicio. |

**Funciones: emojis**

reportlab no sabe dibujar emojis a color, así que cada emoji se sustituye
por una imagen PNG de Twemoji.

| Función | Qué hace |
|---|---|
| `nombre_twemoji(emoji)` | Calcula el nombre del PNG de Twemoji: los códigos del emoji en hexadecimal, unidos por `-`. |
| `emojis_usados()` | Devuelve todos los emojis que aparecen en `OBJETOS`. |
| `ruta_emoji(emoji)` | Devuelve la ruta del PNG de un emoji dentro de `emojis/`. |
| `preparar_emojis()` | Descarga de internet los PNG que falten en `emojis/`. Solo usa la red la primera vez que se añade un emoji nuevo. En Docker no se puede descargar nada, porque la carpeta del paquete no tiene permiso de escritura. Por eso, al añadir un emoji, hay que generar una ficha en local antes de construir la imagen, y subir el PNG a git. |
| `marcar_emojis(texto)` | Cambia cada emoji del texto por una etiqueta `<img>` con su PNG, del tamaño adecuado y alineada con la letra. |

**Funciones: PDF**

| Función | Qué hace |
|---|---|
| `tabla_multiplicar_pdf(tabla, factores, fuente)` | Crea el bloque de la tabla de referencia: el título y un cuadro con las filas `tabla x factor = resultado`, en columnas alineadas. El bloque nunca se parte entre dos páginas. |
| `generar_pdf(ejercicios, tabla, factores, ruta_pdf)` | Monta el PDF en A4: la cabecera, cada problema con su línea `____ x ____ = ____` y la tabla de referencia al final. |

### `multiplicaciones/situaciones.py`

Solo contiene datos, sin funciones. Para dar más variedad a los problemas,
basta con añadir entradas aquí.

| Estructura | Contenido |
|---|---|
| `OBJETOS` | `id: (singular, plural, género "m"/"f"[, emoji])`. El emoji es opcional. |
| `RELACIONES` | `(contexto, id_a, id_b)`: A es el número de grupos y B la cantidad que hay en cada grupo. La respuesta siempre es A × B, en la unidad de B. |
| `PLANTILLAS` | `(contexto, frase)`: una frase solo se usa con relaciones de su mismo contexto. Huecos disponibles: `{a} {b} {a_singular} {a_plural} {b_singular} {b_plural} {a_cuantos} {b_cuantos}`. No se pueden escribir llaves `{}` sueltas en una frase. |

### `multiplicaciones/emojis/`

Imágenes PNG de Twemoji (licencia CC-BY 4.0), con el nombre según la regla
de Twemoji (ver `nombre_twemoji`).

---

## Ejercicio `divisiones`

Reglas de las divisiones:

- Cada ficha tiene siempre 6 divisiones, sin repetir ninguna.
- El dividendo tiene tres cifras enteras y dos decimales (de 100,01 a
  999,99) y el divisor, dos cifras enteras y dos decimales (de 10,01 a
  99,99).
- La cifra de las centésimas nunca es 0: 345,60 no vale, porque en realidad
  es 345,6.
- Los números se guardan como enteros en centésimas (34567 = 345,67) para
  evitar los errores de redondeo de los números decimales del ordenador.
  Solo se pasan a texto con coma al escribir el PDF.

### `divisiones/__init__.py`

La ficha de identidad (ver `ejercicios/__init__.py`).
- `anadir_argumentos` no añade nada.
- `comprobar` llama a `validar_cabeceras`.
- `crear_pdf` genera las divisiones, elige la cabecera, crea el PDF y
  guarda la rotación.

### `divisiones/generar.py`

| Nombre | Para qué sirve |
|---|---|
| `NUM_EJERCICIOS` | Número de divisiones de la ficha (6). |
| `DIVIDENDO_MIN`, `DIVIDENDO_MAX` | Límites del dividendo, en centésimas: de `100_00` a `999_99`. |
| `DIVISOR_MIN`, `DIVISOR_MAX` | Límites del divisor, en centésimas: de `10_00` a `99_99`. |
| `FICHERO_CABECERAS_SALIDAS` | `cabeceras_salidas.json`, donde se apuntan los títulos de las cabeceras que ya han salido. Se crea en la carpeta desde la que se ejecuta, la misma de los PDF. |
| `numero_con_dos_decimales(minimo, maximo)` | Devuelve un número al azar entre los dos límites, en centésimas, cuya última cifra no sea 0. |
| `generar_divisiones(num_ejercicios)` | Crea las parejas `(dividendo, divisor)` de la ficha, en centésimas, por ejemplo `(34567, 1234)` para 345,67 : 12,34. No repite ninguna pareja. |
| `validar_cabeceras()` | Comprueba que no haya dos cabeceras con el mismo título, porque el título es lo que identifica a cada una en `cabeceras_salidas.json`. |
| `elegir_cabecera()` | Elige la cabecera `(título, texto)` con `elegir_sin_repetir` (ver `comun/rotacion.py`), usando los títulos como candidatos. Devuelve `(cabecera, salidas)`. |

### `divisiones/pdf.py`

Dibuja la ficha: la cabecera que le pasa `generar.py` y la cuadrícula de
divisiones. Todo lo que tiene que ver con el aspecto se cambia con las
constantes del principio del fichero.

| Nombre | Para qué sirve |
|---|---|
| `FUENTE_TITULO`, `FUENTE_TEXTO`, `FUENTE_DIVISIONES` | Fuente del título, del texto de la cabecera y de los números de las divisiones. Ahora: Anton para el título y el texto, y Fredoka para las divisiones. |
| `TAMANO_TEXTO` | Tamaño de la letra del texto de la cabecera, en puntos (13,5). El título, los márgenes, las separaciones y las divisiones se calculan a partir de él. |
| `MARGEN_SUPERIOR`, `MARGEN_INFERIOR` | Márgenes de arriba y de abajo de la página. El de arriba es una línea de texto más pequeño que el de abajo (18 mm), para que la cabecera quede más arriba. |
| `SEPARACION_TITULO` | Espacio entre el título y el texto de la cabecera. |
| `SEPARACION_CABECERA` | Espacio entre el texto de la cabecera y la cuadrícula de divisiones. |
| `COLUMNAS`, `FILAS` | Forma de la cuadrícula: 2 columnas por 3 filas. |
| `TAMANO_DIVISION` | Tamaño de «toda» la división: es el tamaño de los números, y el grosor de las líneas de la caja se ajusta solo a él. |
| `POSICION_CAJA` | Dónde va la línea vertical de la caja, en proporción al ancho de la celda (0,55). |
| `MARGEN_CELDA` | Margen interior de cada celda de la cuadrícula, en puntos. |
| `COLOR_CUADRICULA` | Color de las líneas que separan las celdas. Con `None` no se dibujan. |
| `COLOR_CAJA` | Color de las líneas de la caja de la división. |
| `formatear_numero(centesimas)` | Pasa un número en centésimas a texto con coma decimal: `34567` → `"345,67"`. |
| `mostrar_salida(divisiones, cabecera, ruta_pdf)` | Es el único punto de salida del ejercicio. Pasa los números a texto, llama a `generar_pdf` y escribe por consola el PDF generado y la cabecera que ha salido (en Docker, en el log del contenedor). |
| `DivisionCaja` | Dibuja una división con su caja en forma de «L», ocupando todo el ancho de la celda: el dividendo a la izquierda, una línea vertical en `POSICION_CAJA` a la izquierda del divisor, y una horizontal debajo del divisor hasta el borde derecho. `wrap` le dice al PDF cuánto ocupa (todo el ancho y 1,15 veces `TAMANO_DIVISION` de alto) y `draw` la dibuja. |
| `cuadricula_divisiones(ejercicios, fuente, ancho, alto)` | Crea la tabla de `COLUMNAS` x `FILAS` con una división en la parte de arriba de cada celda. Todas las celdas miden lo mismo y entre todas ocupan el ancho y el alto indicados. |
| `generar_pdf(titulo, texto, ejercicios, ruta_pdf)` | Escribe el PDF: el título (siempre en mayúsculas, al estilo Fortnite), el texto de la cabecera y la cuadrícula. Mide lo que ocupa la cabecera y le da a la cuadrícula todo el alto que queda en la página. |

### `divisiones/cabeceras.py`

Solo contiene datos. `CABECERAS` es la lista de las 100 cabeceras posibles.
Cada una es una pareja `(título, texto)` con una historia de Fortnite: hay
que ayudar a ganar el Battle Royale calculando los materiales de las
construcciones.

Las que ya han salido se apuntan por su título en `cabeceras_salidas.json`,
así que **cada cabecera tiene que tener un título distinto** (se comprueba
al arrancar). Si se cambia el título de una cabecera, cuenta como una
nueva. Para tener más variedad, basta con añadir parejas a la lista: las
nuevas entran en la ronda actual. Ningún texto pasa ahora de 7 líneas en el
PDF; cuanto más largo es el texto, menos sitio queda para las divisiones.

---

## `servidor.py`

Servidor web sencillo, sin dependencias externas. Muestra `index.html`, con
un botón por ejercicio. Al pulsar uno, se crea la ficha de ese ejercicio y
se envía por correo.

Lo que escribe el programa por consola (el PDF generado, lo que ha salido
en la rotación, el resultado del correo o el error) solo se muestra en la
consola del servidor, que en Docker es el log del contenedor. La página web
solo dice si ha ido bien o mal.

| Nombre | Qué hace |
|---|---|
| `PAGINA` | Ruta de `index.html`, dentro del paquete. |
| `CARPETA_PDFS` | Carpeta donde se guardan los PDF, con una subcarpeta por ejercicio en la que también va su fichero de rotación. Se puede cambiar con la variable de entorno `CARPETA_PDFS`. Por defecto es `pdfs/` dentro de la carpeta desde la que se arranca el servidor. En Docker es `/app/pdfs`. |
| `ESPERA_SEGUNDOS` | Segundos que hay que esperar entre una ficha y la siguiente (20), para no mandar muchos correos por error. La espera es **común**: después de una ficha de cualquier ejercicio, todos los botones esperan. |
| `LIMITE_SEGUNDOS` | Tiempo máximo para generar y enviar una ficha (120 s). Si se pasa, se cancela. |
| `segundos_restantes()` | Devuelve los segundos que faltan para poder generar otra ficha (0 si ya se puede). |
| `Manejador` | Clase que atiende las peticiones de la web. |
| `Manejador._responder(codigo, tipo, cuerpo)` | Envía una respuesta HTTP con su código, su tipo de contenido y su cuerpo. |
| `Manejador._responder_json(codigo, datos)` | Responde con un JSON con los datos más `espera`, los segundos que faltan. La página usa `espera` para la cuenta atrás de los botones. |
| `Manejador._responder_mensaje(codigo, mensaje)` | Atajo para responder un JSON con un mensaje. |
| `Manejador.do_GET()` | `/` devuelve la página. `/ejercicios` devuelve la lista de ejercicios (clave y nombre, en el orden de `EJERCICIOS`) para crear los botones. Cualquier otra dirección, un 404. |
| `Manejador.do_POST()` | Atiende `/generar/<ejercicio>`. Si el ejercicio no está en `EJERCICIOS`, responde 404; así nunca se ejecuta lo que llegue en la dirección tal cual. Si ya se está generando una ficha, responde 409, y si aún no ha pasado la espera, 429. Si no, ejecuta `python -m operaciones <ejercicio> -e` en `CARPETA_PDFS/<ejercicio>`, con un límite de `LIMITE_SEGUNDOS`. Pasa la salida a la consola del servidor e informa a la página de si ha ido bien. La espera empieza a contar al terminar, haya ido bien o mal. |
| `anadir_argumentos(parser)` | Añade `-p` (puerto) al subcomando `servidor`. |
| `arrancar(args)` | Arranca el servidor para toda la red local, en el puerto `-p` (por defecto 80, el que se usa en Docker). Fuera de Docker un usuario normal no puede usar el 80, así que hay que indicar otro, por ejemplo `-p 8000`. Se para con Ctrl+C. |

## `index.html`

La página web. Al cargarse pide `/ejercicios` y crea un botón por
ejercicio, así que un ejercicio nuevo no obliga a tocarla. Durante la
espera, todos los botones se desactivan y muestran la cuenta atrás; si se
recarga la página, la cuenta atrás sigue. Las medidas de los botones se
cambian en el bloque marcado del CSS (`.ejercicio`).

---

## Otros ficheros

| Fichero | Qué es |
|---|---|
| `pyproject.toml`, `uv.lock` | Definición del paquete y versiones exactas de las dependencias (reportlab). `uv sync` las instala en `.venv/`. `[project.scripts]` crea el comando `operaciones`. |
| `.python-version` | Versión de Python que usa uv (3.13). |
| `src/operaciones/fonts/` | Fuentes `Anton-Regular.ttf` y `Fredoka-SemiBold.ttf`, con sus licencias `OFL-Anton.txt` y `OFL-Fredoka.txt`. Las dos son libres (SIL Open Font License), así que se pueden subir a git y redistribuir siempre que vayan acompañadas de su licencia. Fredoka SemiBold es una versión estática (peso 600) creada a partir de la fuente variable de Google Fonts. Anton es la alternativa libre más parecida a la letra de Fortnite. |
| `Dockerfile`, `docker-compose.yml` | Sirven para ejecutar el servidor en Docker (`docker compose up -d --build`). La imagen instala el paquete con las versiones de `uv.lock`. El servidor escucha en el puerto 80 del contenedor, pero no se publica ningún puerto en el host: Nginx Proxy Manager está en la misma red de Docker y apunta a `operaciones`, puerto 80. Para unir el contenedor a la red de NPM, hay un bloque `networks` comentado en `docker-compose.yml`. Los PDF y la rotación se guardan en `/app/pdfs/<ejercicio>`, en el volumen `operaciones_pdfs`: se conservan al recrear el contenedor y solo se borran con `docker compose down -v` o desde Portainer. La contraseña no va en la imagen: se monta el `.env` como secreto de Docker (`operaciones_env`). |
| `.env` | Datos privados del correo, incluida la contraseña. **No se sube a git**: hay que copiarlo a mano a cada ordenador. |
| `.env.ejemplo` | Plantilla del `.env`, sin datos reales. Sí se sube a git. |
| `tablas_salidas.json`, `cabeceras_salidas.json` | Se crean solos junto a los PDF. Guardan lo que ya ha salido en la ronda actual. Si los borras, empieza una ronda nueva. No se suben a git: son estado de la ejecución. |
| `.gitignore` | Lo que git no sincroniza: `.env`, `.venv/`, `__pycache__/`, los PDF, `pdfs/` y los ficheros `*_salidas.json`. |
| `.dockerignore` | Lo que no se envía a Docker al construir la imagen. |
| `README.md` | Portada del repositorio: qué es, instalación, uso y licencias. |
| `docs/multiplicaciones.png`, `docs/divisiones.png` | Capturas de fichas de ejemplo que aparecen en el README. Hay que regenerarlas a mano si cambia mucho el aspecto de las fichas. |
| `CLAUDE.md` | Notas técnicas del proyecto para Claude Code. |
