# Consola del acto

Herramienta para proyectar el contenido de un acto escolar desde una notebook con dos pantallas. En la notebook se maneja todo desde la **consola**, con el teclado; en el proyector se ve solo el contenido, con fundidos y fondos animados en los momentos de pausa.

Es un único archivo HTML. No hay que instalar nada y funciona sin internet.

## Qué hace

- **Programa del acto.** Elegís una carpeta con videos, imágenes y música, y queda armado en el orden de los nombres de archivo (`01_…`, `02_…`). **Espacio** lanza el siguiente y las teclas **1–9** lanzan directo ese número.
- **Al aire y siguiente.** La consola muestra qué se está viendo, cuánto le falta al video y qué viene después. Las barras de progreso sirven para moverse dentro del video o la música, y **← →** saltan de a 5 segundos.
- **Al terminar un video** puede volver a los fondos, pasar a negro, pasar al siguiente, repetirse o quedar en la última imagen. Se puede cambiar en vivo.
- **Entera o Llenar pantalla** por cada video o imagen, para proyectores 4:3 o 16:9.
- **Música independiente de la imagen**, con opción de repetir (**R**) y corte con fundido (**S**).
- **Fondos animados en rotación**, con tiempos ajustables. Se pueden sumar imágenes y videos propios como fondos.
- **Negro** con la tecla **N**, **pausa** con **P** y **volumen** con **+ / −**.
- Los ajustes de cada archivo y de los fondos se recuerdan en la computadora.

## Uso

1. En la configuración de pantallas, elegí **Unir** (no "Duplicar").
2. Abrí `consola-acto.html` en Chrome, Brave o Edge.
3. Elegí la carpeta del acto y tocá **Abrir pantalla del proyector**.
4. Pasá esa ventana al proyector (en GNOME: **Super + Shift + →**) y hacé **un clic** en ella. Ese clic activa la pantalla completa y el sonido.

## Desarrollo

```bash
python3 build.py eventos/mi-acto                  # genera dist/<id>.html
.venv/bin/python tests/smoke.py eventos/mi-acto   # compila y prueba de punta a punta (Playwright + ffmpeg)
```

La prueba usa un entorno virtual en `.venv/`. Para crearlo la primera vez:

```bash
python3 -m venv .venv
.venv/bin/pip install playwright
.venv/bin/python -m playwright install chromium
```

También hace falta tener `ffmpeg` instalado.

Cada evento es una carpeta con un `evento.json` (título, institución, años, lema y fondos) y sus imágenes y video. El código está en `src/`. Los detalles de la arquitectura están en `CLAUDE.md`.
