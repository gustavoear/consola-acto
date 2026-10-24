# Consola del acto

Herramienta para proyectar el contenido de un acto escolar, o de cualquier evento, desde una notebook con dos pantallas. En la notebook se maneja todo desde la **consola**, con el teclado; en el proyector se ve solo el contenido, con fundidos entre uno y otro y fondos en los momentos de pausa.

Es un único archivo, `consola-acto.html`. No hay que instalar nada y funciona sin internet. Viene vacío: en cada evento cargás tus videos, imágenes, música y fondos.

## Qué hace

- **Programa del acto.** Elegís una carpeta con videos, imágenes y música, y queda armado en el orden de los nombres de archivo (`01_…`, `02_…`). **Espacio** lanza el siguiente y las teclas **1–9** lanzan directo ese número.
- **Al aire y siguiente.** La consola muestra qué se está viendo, cuánto le falta al video y qué viene después. Las barras de progreso sirven para moverse dentro del video o la música, y **← →** saltan de a 5 segundos.
- **Al terminar un video** puede volver a los fondos, pasar a negro, pasar al siguiente, repetirse o quedar en la última imagen. Se puede cambiar en vivo.
- **Entera o Llenar pantalla** por cada video o imagen, para proyectores 4:3 o 16:9.
- **Música independiente de la imagen**, con opción de repetir (**R**) y corte con fundido (**S**).
- **Fondos en rotación.** Cargás imágenes o videos (el escudo, el logo, una animación) que se muestran entre contenido y contenido, con tiempos ajustables. Podés dejar uno fijo o sacarlo de la rotación. Mientras no cargues ninguno, la pantalla queda en negro.
- **Negro** con la tecla **N**, **pausa** con **P** y **volumen** con **+ / −**.
- Los ajustes de cada archivo y de los fondos se recuerdan en la computadora.

## Uso

1. Conseguí `consola-acto.html` (o generalo con `python3 build.py`, ver [Desarrollo](#desarrollo)) y guardalo junto a la carpeta del acto.
2. En la configuración de pantallas, elegí **Unir** (no "Duplicar").
3. Abrí `consola-acto.html` en Chrome, Brave o Edge.
4. Elegí la carpeta del acto y, si querés, cargá los fondos en el panel **Fondos**.
5. Tocá **Abrir pantalla del proyector** y pasá esa ventana al proyector (en GNOME: **Super + Shift + →**). Hacé **un clic** en ella: ese clic activa la pantalla completa y el sonido.

Consejo: nombrá los archivos con un número adelante (`01 Bienvenida.mp4`, `02 Himno.mp3`, `03 Danza.mp4`…) para que el programa quede en orden.

## Desarrollo

```bash
python3 build.py                   # genera dist/consola-acto.html
.venv/bin/python tests/smoke.py    # compila y prueba de punta a punta
```

El código está en `src/`. La prueba usa un entorno virtual en `.venv/`; para crearlo la primera vez:

```bash
python3 -m venv .venv
.venv/bin/pip install playwright
.venv/bin/python -m playwright install chromium
```

También hace falta tener `ffmpeg` instalado. Los detalles de la arquitectura están en `CLAUDE.md`.

## Créditos

Creada por **Gustavo Earnshaw**. Nació para el acto de los 70 años del Instituto Superior Cristo Rey (Apóstoles, Misiones), en 2026, y después se convirtió en una herramienta para cualquier institución o evento. Se desarrolló con ayuda de Claude, de Anthropic.

## Licencia

[MIT](LICENSE): podés usarla, copiarla, modificarla y compartirla, siempre que mantengas el aviso de autoría y de licencia. Se ofrece tal cual, sin garantías.
