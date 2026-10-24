# Consola del acto

Consola para manejar la proyección de un acto escolar con el teclado: una ventana de **consola** en la notebook y una ventana de **pantalla** en el proyector (segundo monitor). Nació para el acto de los 70 años del Instituto Superior Cristo Rey (Apóstoles, Misiones), donde **se usó en vivo el 23/10/2026 y funcionó bien**. El objetivo actual es **volverla genérica** para cualquier institución o evento y publicarla en GitHub.

## Cómo se trabaja

- `python3 build.py [carpeta del evento]` compila todo en `dist/<id>.html`: un único archivo autocontenido (unos 6–7 MB con el video de Cristo Rey) que funciona sin internet al abrirlo con doble clic. Sin argumento compila `eventos/cristo-rey-70`. **Siempre se edita `src/`, nunca `dist/`.**
- `.venv/bin/python tests/smoke.py [carpeta del evento]` compila el evento y hace una prueba de punta a punta con Playwright, que también compara los textos y fondos con su `evento.json`. Después de cualquier cambio de comportamiento: compilar, correr la prueba y agregar un caso nuevo si hace falta.
  - Playwright está instalado en el entorno virtual `.venv/` (fuera de git). Para crearlo de cero: `python3 -m venv .venv`, `.venv/bin/pip install playwright` y `.venv/bin/python -m playwright install chromium`. También hace falta `ffmpeg`.
  - El Chromium de Playwright **no reproduce H.264**: los videos de prueba son WebM. El MP4 de la historia no se puede probar ahí, pero en Chrome y Brave anda.
- Lo usa el autor en **Manjaro con GNOME**, desde Brave o Chrome, con el proyector en modo "Unir pantallas". El código vive en `~/workspace/consola-acto`; el HTML compilado se copia a la carpeta de cada evento.

## Configuración del evento

Cada evento es una carpeta con un `evento.json` y sus imágenes y video. `eventos/` está en `.gitignore`: los archivos son de cada institución. `build.py` valida el JSON (con errores en español), embebe las imágenes y el video, y mete el JSON en `<script type="application/json" id="evento">`. Las imágenes viajan dentro del JSON (`fondos[].src`, data URI); cada video va en su propio `<script class="vid64" data-clave>`. En el navegador queda en `EV`, y `FONDO[clave]` da cada fondo.

- Campos: `id` (minúsculas y guiones; se usa en el nombre del archivo, la clave de `localStorage` y el nombre de la ventana), `titulo`, `institucion` (obligatorios), y `numero`, `unidad`, `anios`, `lema` (opcionales: si faltan, se ocultan).
- `fondos`: lista ordenada de `{tipo, nombre, imagen | archivo, alt?, rota?, colores?}`. El orden es el de la lista y la rotación. `rota: false` lo deja fuera de la rotación automática (se puede poner fijo igual). Los tipos se pueden repetir y ninguno es obligatorio. `build.py` le pone a cada uno su `clave`: el tipo, o `tipo-2`, `tipo-3`… si se repite. Tipos: `escudo`, `aniversario`, `logo`, `bordado` y `video` (con `rotulos: [{desde, hasta?, texto, sub?}]`, en segundos; sin `hasta`, el rótulo queda hasta el final).
- `colores` (opcional, general y también por fondo): `fondo`, `acento`, `texto` en hex. Además, `escudo` acepta `fondo_abajo` y `brasas`, `logo` acepta `papel` (lista para el papel picado) y `bordado` acepta `hilos` (dos colores). `paleta(fondo)` mezcla los del fondo con los generales y pone valores por defecto. Las variantes (centro y borde de los degradés, halos, rayos) salen de `luz()` y `escala()`, que cambian la luminosidad en HSL sin cambiar el tono. Los colores de Cristo Rey están puestos tal cual en su `evento.json`, así que se ve igual que en el acto.
- Los colores de la **consola** no cambian por evento: el rojo ("al aire") y el dorado ("siguiente") son parte de la interfaz.
- En las escenas, los textos llevan `data-ev="campo"` y los completa `fillEv()`. `data-ev-si` oculta un bloque si el campo está vacío.

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

- **Fondos del evento**: una escena por cada elemento de `fondos`, clonada del molde de su tipo (`<template id="tplFondos">`, que sale de `src/escenas.html`) e insertada antes de las ranuras de contenidos. Su CSS está en `src/pantalla.css`.
  - Los animados se dibujan en `<canvas>` con `DIBUJOS[tipo](sección, paleta)` (`src/dibujo.js`), que devuelve `{size, draw}`. Cada escena tiene su propio lienzo y sus partículas.
  - Los de tipo `video` se pasan una vez con sus rótulos y después vuelven al fondo anterior. En el código, `esVideo(clave)` reemplaza a la antigua clave fija `historia`.
- `m1` / `m2`: dos ranuras que se alternan para los videos e imágenes del programa (fundido entre una y otra).
- `u1` / `u2`: dos ranuras para los fondos agregados por el usuario.
- `negro`.
- Música: un `<audio>` independiente de la imagen.
- Claves de rotación: las `clave` de los fondos del evento, o `u:<id>` para los agregados. Si una clave no sirve, se usa `PRIMERO` (el primer fondo que no es video).

### Estado guardado

En `localStorage['consola-acto:<id>']`: nombre, sonido, "al terminar", repetición de música y ajuste (`fit`) de cada archivo (por `nombre|tamaño|fecha`), `config` (tiempos de fondos) y `bg` (orden y qué fondos rotan). Los archivos en sí **no** se guardan: el usuario vuelve a elegir la carpeta en cada sesión.

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

- ~~Textos, títulos, etiquetas de los fondos, clave de `localStorage` y tiempos de los rótulos~~: ya salen de `evento.json` (paso 1).
- ~~Colores fijos en `src/pantalla.css` y `src/dibujo.js`~~: salen de `colores` (paso 2).
- **Imágenes y video** en `eventos/cristo-rey-70/` (escudo, logo de los 70 años, logo del grupo Вільні Соколи y video de la historia). **Son de la institución y del grupo de danzas:** antes de publicar el repositorio, confirmar si se pueden subir. Mientras tanto quedan fuera de git; falta agregar un evento de ejemplo en `ejemplos/generico/` (paso 4).
- ~~Escenas, `BUILTIN` y rotación fijas~~: se generan desde `fondos` (paso 3). El tipo `bordado` (punto cruz ucraniano) sigue siendo un diseño pensado para Sokoly, aunque sus colores son configurables.

Plan en curso: 1) `evento.json` + textos (hecho), 2) colores (hecho), 3) escenas y `BUILTIN` generadas desde `fondos` (hecho), 4) `ejemplos/generico/` como evento por defecto.
