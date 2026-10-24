# Consola del acto

Herramienta para proyectar el contenido de un acto escolar desde una notebook con dos pantallas. En la notebook se maneja todo desde la **consola**, con el teclado; en el proyector se ve solo el contenido, con fundidos y fondos animados en los momentos de pausa.

Es un único archivo HTML. No hay que instalar nada y funciona sin internet. Cada institución o evento tiene su propia consola, con su nombre, sus colores y sus logos.

## Qué hace

- **Programa del acto.** Elegís una carpeta con videos, imágenes y música, y queda armado en el orden de los nombres de archivo (`01_…`, `02_…`). **Espacio** lanza el siguiente y las teclas **1–9** lanzan directo ese número.
- **Al aire y siguiente.** La consola muestra qué se está viendo, cuánto le falta al video y qué viene después. Las barras de progreso sirven para moverse dentro del video o la música, y **← →** saltan de a 5 segundos.
- **Al terminar un video** puede volver a los fondos, pasar a negro, pasar al siguiente, repetirse o quedar en la última imagen. Se puede cambiar en vivo.
- **Entera o Llenar pantalla** por cada video o imagen, para proyectores 4:3 o 16:9.
- **Música independiente de la imagen**, con opción de repetir (**R**) y corte con fundido (**S**).
- **Fondos animados en rotación**, con el escudo, el logo, los años y el lema de la institución, y tiempos ajustables. Se pueden sumar imágenes y videos propios como fondos.
- **Negro** con la tecla **N**, **pausa** con **P** y **volumen** con **+ / −**.
- Los ajustes de cada archivo y de los fondos se recuerdan en la computadora.

## Uso

1. En la configuración de pantallas, elegí **Unir** (no "Duplicar").
2. Abrí el HTML de tu evento (por ejemplo `escuela-ejemplo.html`) en Chrome, Brave o Edge.
3. Elegí la carpeta del acto y tocá **Abrir pantalla del proyector**.
4. Pasá esa ventana al proyector (en GNOME: **Super + Shift + →**) y hacé **un clic** en ella. Ese clic activa la pantalla completa y el sonido.

## Armar la consola de tu evento

Hace falta Python 3.

1. Copiá la carpeta `ejemplos/generico` a `eventos/mi-acto` (o el nombre que quieras). `eventos/` no se sube a git: las imágenes son de cada institución.
2. Reemplazá `escudo.svg` y `logo.svg` por los de tu institución (PNG, JPG, WebP o SVG; mejor con fondo transparente).
3. Editá `evento.json` con los datos del evento.
4. Compilá: `python3 build.py eventos/mi-acto`. Queda en `dist/<id>.html`; ese archivo es el que copiás a la computadora del acto.

Si algo está mal escrito en `evento.json`, `build.py` avisa qué y dónde.

### `evento.json`

```json
{
  "id": "escuela-ejemplo",
  "titulo": "Acto 50 años",
  "institucion": "Escuela N.º 1",
  "numero": "50",
  "unidad": "años",
  "anios": "1976 · 2026",
  "lema": "Aprender juntos, crecer juntos",
  "colores": { "fondo": "#14352e", "acento": "#e8b64c", "texto": "#f3efe4" },
  "fondos": [
    { "tipo": "escudo", "nombre": "Escudo", "imagen": "escudo.svg" },
    { "tipo": "aniversario", "nombre": "Aniversario" },
    { "tipo": "logo", "nombre": "Logo 50 años", "imagen": "logo.svg",
      "colores": { "fondo": "#1d4e89", "papel": ["#1d4e89", "#3f8fd2", "#e8b64c", "#ffffff"] } },
    { "tipo": "video", "nombre": "Nuestra historia", "archivo": "historia.mp4",
      "rotulos": [ { "desde": 0.5, "hasta": 4, "texto": "1976", "sub": "Los comienzos" },
                   { "desde": 8, "texto": "2026", "sub": "Hoy" } ] }
  ]
}
```

| Campo | Para qué |
|---|---|
| `id` | Nombre corto, en minúsculas y con guiones. Se usa para el nombre del archivo compilado y para guardar los ajustes. **Obligatorio.** |
| `titulo`, `institucion` | Se ven en la consola y en los fondos. **Obligatorios.** |
| `numero`, `unidad`, `anios`, `lema` | La cifra grande ("50 años"), el período y el lema de los fondos. Si no van, se ocultan. |
| `colores` | `fondo` (oscuro), `acento` (el de los números y los brillos) y `texto`, en formato `#rrggbb`. Los tonos más claros y más oscuros se calculan solos. |
| `fondos` | Los fondos animados, en el orden de la rotación. Cada uno lleva `tipo` y `nombre` (el que se ve en la consola). Se puede repetir un tipo. |

Tipos de fondo:

| `tipo` | Qué muestra | Lleva |
|---|---|---|
| `escudo` | El escudo a la izquierda y la cifra, los años y el lema a la derecha, con rayos y brasas | `imagen`. Colores extra: `fondo_abajo`, `brasas` |
| `aniversario` | Solo texto: institución, cifra, años y lema, con rayos y polvo dorado | — |
| `logo` | El logo sobre un medallón de luz, con papel picado | `imagen`. Color extra: `papel` (lista) |
| `bordado` | Un emblema sobre bordado ucraniano en punto cruz | `imagen`. Color extra: `hilos` (dos colores) |
| `video` | Un video que se pasa una vez, con rótulos opcionales; después vuelve al fondo anterior | `archivo` (MP4 o WebM) y `rotulos`: `desde` y `hasta` en segundos (sin `hasta`, queda hasta el final), `texto` y `sub` |

Cualquier fondo acepta además `alt` (descripción de la imagen), `"rota": false` (no entra en la rotación automática, pero se puede poner a mano) y sus propios `colores`.

Los videos quedan dentro del HTML: un video de 4 MB suma unos 5,3 MB al archivo.

## Desarrollo

```bash
python3 build.py [carpeta del evento]                 # genera dist/<id>.html (sin argumento: el ejemplo)
.venv/bin/python tests/smoke.py [carpeta del evento]  # compila y prueba de punta a punta
```

Sin argumento, la prueba recorre el ejemplo y cada evento de `eventos/`. Usa un entorno virtual en `.venv/`; para crearlo la primera vez:

```bash
python3 -m venv .venv
.venv/bin/pip install playwright
.venv/bin/python -m playwright install chromium
```

También hace falta tener `ffmpeg` instalado.

El código está en `src/`. Las imágenes del ejemplo se generan con `ejemplos/generico/hacer_imagenes.py`. Los detalles de la arquitectura están en `CLAUDE.md`.
