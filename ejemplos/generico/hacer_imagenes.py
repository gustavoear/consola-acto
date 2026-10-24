"""Genera las imágenes SVG del evento de ejemplo (escudo.svg y logo.svg) en esta carpeta.

Uso:  python3 ejemplos/generico/hacer_imagenes.py
"""
import math
import pathlib
out = pathlib.Path(__file__).resolve().parent

# ---------- escudo: sol sobre un libro abierto, en un escudo dorado ----------
rayos = ''.join(
    f'<path d="M0 -44 L7 -78 L0 -86 L-7 -78 Z" transform="rotate({a})"/>' for a in range(0, 360, 30))
escudo = f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="480" viewBox="0 0 400 480">
  <defs>
    <linearGradient id="oro" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fbe3a1"/><stop offset=".5" stop-color="#e8b64c"/><stop offset="1" stop-color="#a8792a"/>
    </linearGradient>
    <linearGradient id="campo" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#2d7262"/><stop offset="1" stop-color="#103630"/>
    </linearGradient>
  </defs>
  <path d="M200 14 L378 64 V226 C378 354 296 426 200 468 C104 426 22 354 22 226 V64 Z" fill="url(#oro)"/>
  <path d="M200 40 L354 84 V228 C354 336 284 400 200 438 C116 400 46 336 46 228 V84 Z" fill="url(#campo)"/>
  <path d="M200 52 L342 92 V228 C342 328 278 388 200 424 C122 388 58 328 58 228 V92 Z" fill="none" stroke="#e8b64c" stroke-opacity=".45" stroke-width="2"/>
  <g transform="translate(200 158)" fill="#f2c25c">{rayos}<circle r="36" fill="url(#oro)"/></g>
  <g transform="translate(200 300)" stroke="#a8792a" stroke-width="3" stroke-linejoin="round">
    <path d="M0 -36 C-30 -54 -72 -54 -106 -40 V44 C-72 30 -30 30 0 48 Z" fill="#f6f1e3"/>
    <path d="M0 -36 C30 -54 72 -54 106 -40 V44 C72 30 30 30 0 48 Z" fill="#fbf8ef"/>
    <g fill="none" stroke="#c9b48a" stroke-width="2.5" stroke-linecap="round">
      <path d="M-18 -20 C-40 -30 -64 -30 -86 -24 M-18 -2 C-40 -12 -64 -12 -86 -6 M-18 16 C-40 6 -64 6 -86 12"/>
      <path d="M18 -20 C40 -30 64 -30 86 -24 M18 -2 C40 -12 64 -12 86 -6 M18 16 C40 6 64 6 86 12"/>
    </g>
  </g>
</svg>
'''

# ---------- logo: "50 años" con laurel, para el fondo con medallón de luz ----------
def rama(lado):
    """Rama de laurel sobre un arco alrededor del centro; lado -1 = izquierda, 1 = derecha.
    Crece desde abajo hacia arriba: un tallo y pares de hojas que apuntan hacia donde crece."""
    cx, cy, R, n = 250, 262, 190, 8
    angs = [100 + i * 13 for i in range(n)] if lado < 0 else [80 - i * 13 for i in range(n)]
    pts = [(cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a))) for a in angs]
    tallo = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
    hojas = []
    for i, (a, (x, y)) in enumerate(zip(angs, pts)):
        base = a + 180 if lado < 0 else a          # la hoja sin girar apunta hacia arriba
        tam = 1 - i * .035                          # más chicas hacia la punta
        for s in (-1, 1):
            hojas.append(f'<ellipse cx="0" cy="{-19 * tam:.1f}" rx="{8 * tam:.1f}" ry="{19 * tam:.1f}" '
                         f'transform="translate({x:.1f} {y:.1f}) rotate({base + s * 40:.1f})"/>')
    x, y = pts[-1]
    hojas.append(f'<ellipse cx="0" cy="-17" rx="7" ry="17" transform="translate({x:.1f} {y:.1f}) rotate({angs[-1] + 180 if lado < 0 else angs[-1]:.1f})"/>')
    return f'<path d="{tallo}" fill="none" stroke="#3d7f55" stroke-width="4" stroke-linecap="round"/>' + ''.join(hojas)
logo = f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500" viewBox="0 0 500 500">
  <defs>
    <linearGradient id="azul" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#3f8fd2"/><stop offset="1" stop-color="#173f73"/>
    </linearGradient>
    <path id="arco" d="M 92 250 A 158 158 0 0 1 408 250"/>
  </defs>
  <g fill="#4f9e6a">{rama(-1)}</g>
  <g fill="#6cbb84">{rama(1)}</g>
  <text font-family="Georgia, 'DejaVu Serif', serif" font-size="30" font-weight="700" letter-spacing="6" fill="#173f73">
    <textPath href="#arco" startOffset="50%" text-anchor="middle">ESCUELA N.º 1</textPath>
  </text>
  <text x="250" y="318" text-anchor="middle" font-family="Georgia, 'DejaVu Serif', serif" font-size="178" font-weight="700" fill="url(#azul)" stroke="#0f2c52" stroke-width="3">50</text>
  <rect x="140" y="336" width="220" height="44" rx="8" fill="#e8b64c"/>
  <text x="250" y="368" text-anchor="middle" font-family="Georgia, 'DejaVu Serif', serif" font-size="28" font-weight="700" letter-spacing="8" fill="#0f2c52">AÑOS</text>
  <text x="250" y="418" text-anchor="middle" font-family="Georgia, 'DejaVu Serif', serif" font-size="22" letter-spacing="3" fill="#173f73">1976 · 2026</text>
</svg>
'''
(out / 'escudo.svg').write_text(escudo, encoding='utf-8')
(out / 'logo.svg').write_text(logo, encoding='utf-8')
