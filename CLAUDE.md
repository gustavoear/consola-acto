# Consola del acto

Consola para manejar la proyección de un acto escolar con el teclado: una ventana de **consola** en la notebook y una ventana de **pantalla** en el proyector (segundo monitor). Nació para el acto de los 70 años del Instituto Superior Cristo Rey (Apóstoles, Misiones), donde **se usó en vivo el 23/10/2026 y funcionó bien**. Ahora es una herramienta **genérica y vacía**: un único `consola-acto.html`, sin fondos ni contenidos incluidos, en el que cada usuario carga los suyos en el momento. Se publica en GitHub con licencia MIT.

## Cómo se trabaja

- `python3 build.py` compila todo en `dist/consola-acto.html`: un único archivo autocontenido (unos 70 KB) que funciona sin internet al abrirlo con doble clic. Une `src/consola.html` con `src/pantalla.css` y pone el texto de `LICENSE` como comentario al principio. **Siempre se edita `src/`, nunca `dist/`.**
- `.venv/bin/python tests/smoke.py` compila y hace una prueba de punta a punta con Playwright. Después de cualquier cambio de comportamiento: compilar, correr la prueba y agregar un caso nuevo si hace falta.
  - Playwright está instalado en el entorno virtual `.venv/` (fuera de git). Para crearlo de cero: `python3 -m venv .venv`, `.venv/bin/pip install playwright` y `.venv/bin/python -m playwright install chromium`. También hace falta `ffmpeg`.
  - El Chromium de Playwright **no reproduce H.264**: los videos de prueba son WebM. Los MP4 no se pueden probar ahí, pero en Chrome y Brave andan.
- Lo usa el autor en **Manjaro con GNOME**, desde Brave o Chrome, con el proyector en modo "Unir pantallas". El código vive en `~/workspace/consola-acto`; el HTML compilado se copia a la carpeta de cada evento.

## Créditos y licencia

- Licencia **MIT**, a nombre de Gustavo Earnshaw (`LICENSE`). Como el HTML compilado se comparte solo, `build.py` copia la licencia completa en un comentario al principio del archivo.
- En la consola, el panel **"Acerca de"** (un `<details>` al final de la columna lateral) muestra el autor, el origen (el acto de los 70 años del Instituto Superior Cristo Rey), que se desarrolló con ayuda de Claude y un resumen de la licencia.
- El link al repositorio sale de la constante `REPO` de `build.py`, que reemplaza el bloque `<!--REPO-->…<!--/REPO-->`. Si se deja vacía, la línea no aparece.
- Se publica en https://github.com/gustavoear/consola-acto. Cada versión es una **Release** con `consola-acto.html` adjunto (`dist/` no va en git): compilar, probar, crear el tag `vX.Y.Z` y `gh release create`.

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

- `m1` / `m2`: dos ranuras que se alternan para los videos e imágenes del programa (fundido entre una y otra).
- `u1` / `u2`: dos ranuras que se alternan para los fondos (imágenes o videos que agrega el usuario).
- `negro`. **Sin fondos cargados, el modo fondos muestra negro** (`curKey = null`). Cuando llega el primer fondo, `setBgList` lo muestra enseguida.
- Música: un `<audio>` independiente de la imagen.
- Claves de rotación: `u:<id>` de cada fondo agregado.

### Estado guardado

**Al volver a abrir la consola está todo como se dejó, sin ningún paso.** Se guarda solo, en cada cambio:

- En `localStorage['consola-acto:programa']`: nombre, sonido, "al terminar", repetición de música y ajuste (`fit`) de cada archivo (por `nombre|tamaño|fecha`), `config` (tiempos de fondos), `bg` (orden y qué fondos rotan), y qué hay cargado: `order` (ids del programa, en orden) y `fondos` (ids de los fondos).
- En IndexedDB (base `consola-acto`, almacén `archivos`): **una copia de cada archivo**, con su firma `nombre|tamaño|fecha` como clave. Si un archivo está en el programa y en los fondos, se guarda una sola vez. `recordar()` copia lo que se agrega, `olvidar()` borra las copias que ya no usa nadie (al quitar, vaciar o reemplazar con "Elegir carpeta"), y `recuperar()` arma el programa y los fondos al iniciar.
- Las copias ocupan en disco lo mismo que los archivos y quedan en ese navegador de esa computadora. Si no hay lugar, se avisa y la consola sigue funcionando; lo que no se pudo copiar simplemente no vuelve.
- Se descartó guardar una configuración en `.json` y volver a elegir la carpeta: eran dos pasos y confundían. El navegador no da rutas de archivos ni puede releerlos solo.

### Orden del programa

**"Elegir carpeta" reemplaza el programa y lo ordena por nombre de archivo** (`localeCompare` numérico: `01_…`, `02_…`). El orden manual con ↑ ↓ se recuerda al volver a abrir la consola (con el programa recuperado), pero **"Elegir carpeta" siempre ordena por nombre**. Antes el orden guardado le ganaba a los nombres al elegir la carpeta: al renombrar archivos, el programa quedaba desordenado (pasó en el ensayo). No volver a ese comportamiento. Cada fila muestra el nombre real del archivo (`.fname`) porque la etiqueta oculta el número.

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
- Se usaron videos MP4 de fondos animados, exportados aparte en 16:9 y 4:3, además de los fondos dibujados en vivo. Por eso la versión genérica no trae fondos propios: cada usuario carga sus imágenes o videos de fondo.
- Encadenar contenidos con "pasar al siguiente" funcionó muy bien para transiciones (foto → video de transición → video), siempre que todos usen el mismo ajuste (Entera/Llenar).
- La música previa y posterior se cargó como archivos del programa; una "lista de música" que reproduzca una carpeta en secuencia sería más cómoda.
- Una nota o guion por contenido ("lanzar cuando dicen…") visible en la consola habría ayudado al operador.

## Historia del proyecto

- La versión del acto tenía fondos animados dibujados en canvas (escudo, aniversario, logo de los 70 años y bordado de Вільні Соколи) y el video de la historia embebido. Después pasó por una etapa con `evento.json` para compilar una consola por evento. **Las dos se descartaron a favor de la consola vacía**, pero siguen en la historia de git: el primer commit es la versión del acto, y el commit `0764473` es la última con `evento.json`.
- Las imágenes y el video de Cristo Rey están en `eventos/cristo-rey-70/`, que está en `.gitignore`: **son de la institución y del grupo de danzas** y no se publican. El `build.py` actual ya no los usa.
