# Consola del acto

Consola para manejar la proyección de un acto escolar con el teclado: una ventana de **consola** en la notebook y una ventana de **pantalla** en el proyector (segundo monitor). Nació para el acto de los 70 años del Instituto Superior Cristo Rey (Apóstoles, Misiones), donde **se usó en vivo el 23/10/2026 y funcionó bien**. El objetivo actual es **volverla genérica** para cualquier institución o evento y publicarla en GitHub.

## Cómo se trabaja

- `python3 build.py` compila todo en `dist/consola-acto.html`: un único archivo autocontenido de unos 6–7 MB que funciona sin internet al abrirlo con doble clic. **Siempre se edita `src/`, nunca `dist/`.**
- `.venv/bin/python tests/smoke.py` hace una prueba de punta a punta con Playwright. Después de cualquier cambio de comportamiento: compilar, correr la prueba y agregar un caso nuevo si hace falta.
  - Playwright está instalado en el entorno virtual `.venv/` (fuera de git). Para crearlo de cero: `python3 -m venv .venv`, `.venv/bin/pip install playwright` y `.venv/bin/python -m playwright install chromium`. También hace falta `ffmpeg`.
  - El Chromium de Playwright **no reproduce H.264**: los videos de prueba son WebM. El MP4 de la historia no se puede probar ahí, pero en Chrome y Brave anda.
- Lo usa el autor en **Manjaro con GNOME**, desde Brave o Chrome, con el proyector en modo "Unir pantallas". El código vive en `~/workspace/consola-acto`; el HTML compilado se copia a la carpeta de cada evento.

## Arquitectura

Un solo HTML con dos modos, según el hash de la URL:

- **Sin hash, modo consola.** Muestra la lista del programa, lo que está "al aire" y lo que sigue, los fondos, la música, el volumen y los atajos de teclado.
- **Con `#pantalla`, modo proyector.** La consola lo abre con `window.open(url + '#pantalla')`. Muestra escenas a pantalla completa que se funden entre sí cambiando la opacidad de capas `.scene`.

Las dos ventanas se comunican con `postMessage`. La consola tiene la referencia `win` y la pantalla usa `window.opener`. Los archivos (`File`) se pasan por `postMessage` y la pantalla crea sus propias `blob:` URLs.

### Mensajes

| Dirección | `type` / `cmd` | Para qué |
|---|---|---|
| consola → pantalla | `files` | Envía los `{id, file}` del programa y de los fondos agregados |
| consola → pantalla | `cmd: cue` | Lanza un contenido `{id, kind, sound, end, loop, fit, label}` |
| consola → pantalla | `cmd: cueUpdate` | Cambia `end`, `sound` o `fit` del contenido que está al aire (se aplica en vivo) |
| consola → pantalla | `cmd: fondos` | Pasa a fondos: `{which, rotar}` (`which` = clave o `null`) |
| consola → pantalla | `cmd: bgList` | Envía la rotación `{rot: [claves], kinds: {id: 'image'|'video'}}` |
| consola → pantalla | `cmd: config` | Ajusta `{fondoSeg, fadeSeg}` |
| consola → pantalla | `cmd: negro / pausa / stopMusic / loopMusic / vol / seek / nudge` | Controles en vivo |
| pantalla → consola | `hola` | La pantalla está lista |
| pantalla → consola | `estado` | Se envía cada 250 ms: modo, escena, tiempos de video y música, `nextIn`, etc. |
| pantalla → consola | `tecla` | Teclas apretadas en la ventana del proyector, que se reenvían a la consola |
| pantalla → consola | `terminado` | Terminó un video con "Al terminar: pasar al siguiente" |

### Escenas de la pantalla

- **Fondos animados** dibujados en `<canvas>` (`src/dibujo.js`): `escudo`, `aniversario`, `logo` y `sokoly`. Su HTML está en `src/escenas.html` y su CSS en `src/pantalla.css`.
- `historia`: video embebido en base64, con rótulos de año.
- `m1` / `m2`: dos ranuras que se alternan para los videos e imágenes del programa (fundido entre una y otra).
- `u1` / `u2`: dos ranuras para los fondos agregados por el usuario.
- `negro`.
- Música: un `<audio>` independiente de la imagen.
- Claves de rotación: los nombres de los fondos animados, o `u:<id>` para los agregados.

### Estado guardado

En `localStorage['acto70:programa']`: nombre, sonido, "al terminar", repetición de música y ajuste (`fit`) de cada archivo (por `nombre|tamaño|fecha`), `config` (tiempos de fondos) y `bg` (orden y qué fondos rotan). Los archivos en sí **no** se guardan: el usuario vuelve a elegir la carpeta en cada sesión.

### Orden del programa

**"Elegir carpeta" reemplaza el programa y lo ordena por nombre de archivo** (`localeCompare` numérico: `01_…`, `02_…`). El orden manual con ↑ ↓ dura solo la sesión. Antes se guardaba el orden en `localStorage` y le ganaba a los nombres: al renombrar archivos el programa quedaba desordenado (pasó en el ensayo). No volver a ese comportamiento. Cada fila muestra el nombre real del archivo (`.fname`) porque la etiqueta oculta el número.

### Opciones por contenido

- Video: **Con / Sin sonido**, **▭ Entera / ⛶ Llenar pantalla** (`object-fit: contain` o `cover`) y **Al terminar**: volver a fondos, negro, pasar al siguiente, **repetir** (`video.loop`) o quedar en la última imagen.
- Imagen: Entera / Llenar pantalla. Queda en pantalla hasta el próximo.
- Música: suena una vez o se repite (**R**). No cambia la pantalla.

## Convenciones

- Interfaz en **español rioplatense con voseo** ("Elegí", "Tocá"). Textos claros, sin tecnicismos: lo opera un docente durante un acto en vivo.
- Todo tiene que funcionar **sin conexión**. El HTML de `dist/` no puede depender de archivos externos, salvo Google Fonts, que tiene respaldo.
- La consola se usa con la sala a oscuras: tema oscuro, el rojo indica "al aire" y el dorado indica "siguiente".
- **Espacio** tiene que lanzar siempre el siguiente. Después de un clic con el mouse se le quita el foco a los botones, y los atajos se ignoran mientras se escribe en un campo.
- Nada se borra sin confirmar: un segundo clic, nunca `confirm()`.

## Lo que se aprendió en el acto

- **El proyector del salón era 4:3.** Los fondos dibujados en canvas se adaptan solos; los videos 16:9 quedaban con bandas. Por eso existe "Llenar pantalla" y por eso cualquier logo o texto incrustado en un video debe quedar dentro de la **zona central 4:3** (el logo del video de la historia se movió ahí). Una mejora natural: detectar la relación de aspecto de la pantalla del proyector y sugerir "Llenar" automáticamente.
- Se usaron videos MP4 de los fondos animados (exportados aparte, en 16:9 y 4:3) además de los fondos en vivo. Exportarlos desde la propia consola (grabando el canvas) sería una función útil.
- Encadenar contenidos con "pasar al siguiente" funcionó muy bien para transiciones (foto → video de transición → video), siempre que todos usen el mismo ajuste (Entera/Llenar).
- La música previa y posterior se cargó como archivos del programa; una "lista de música" que reproduzca una carpeta en secuencia sería más cómoda.
- Una nota o guion por contenido ("lanzar cuando dicen…") visible en la consola habría ayudado al operador.

## Qué está atado al acto de los 70 años (para volverlo genérico)

- **Textos** en `src/escenas.html`: nombre de la institución, "70 años", "1956 · 2026", el lema y los rótulos "Los comienzos" / "Nuestro colegio hoy".
- **Textos** en `src/consola.html`: el título, el encabezado (`c-brand`), el título del proyector, `BUILTIN` (etiquetas de los fondos) y la clave `acto70:programa` de `localStorage`.
- **Tiempos del video de la historia**: `CONFIG.cambio1956` / `cambio2026`.
- **Imágenes y video** en `assets/` (escudo, logo de los 70 años, logo del grupo Вільні Соколи y video de la historia). **Son de la institución y del grupo de danzas:** antes de publicar el repositorio, confirmar si se pueden subir. Si no, dejarlos fuera de git (`.gitignore`) y agregar imágenes de ejemplo.
- **Fondos animados de diseño propio** (`escudo`, `aniversario`, `logo`, `sokoly`): para hacerlos genéricos, conviene que tomen de configuración el logo, los textos y la paleta, y que la lista `BUILTIN` y las escenas se generen a partir de esa configuración.

Una idea posible es un `evento.json` (nombre, subtítulo, años, lema, colores, logos y qué fondos animados se incluyen) que `build.py` lea para reemplazar marcadores. Así se podría compilar una consola distinta por evento sin tocar el código.
