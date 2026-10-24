#!/usr/bin/env python3
"""Compila la consola en un único HTML autocontenido (dist/consola-acto.html).

Une src/consola.html con el CSS, las escenas y el dibujo de la pantalla del proyector,
y embebe las imágenes y el video de assets/ como data URIs, para que el archivo
funcione sin internet ni archivos sueltos.

Uso:  python3 build.py            -> dist/consola-acto.html
"""
import base64
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC, ASSETS, DIST = ROOT / 'src', ROOT / 'assets', ROOT / 'dist'

# marcador en el código  ->  (archivo en assets/, tipo MIME)
IMAGENES = {
    '__ESCUDO__': ('escudo.png', 'image/png'),
    '__LOGO70__': ('logo70.png', 'image/png'),
    '__SOKOLY__': ('sokoly.webp', 'image/webp'),
}
VIDEO = 'historia.mp4'


def b64(path: pathlib.Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def main() -> int:
    s = (SRC / 'consola.html').read_text(encoding='utf-8')
    s = s.replace('/*CSS_PANTALLA*/', (SRC / 'pantalla.css').read_text(encoding='utf-8'))
    s = s.replace('<!--ESCENAS-->', (SRC / 'escenas.html').read_text(encoding='utf-8'))
    s = s.replace('/*DIBUJO*/', (SRC / 'dibujo.js').read_text(encoding='utf-8'))

    for marca, (nombre, mime) in IMAGENES.items():
        f = ASSETS / nombre
        if not f.exists():
            print(f'Falta {f}', file=sys.stderr)
            return 1
        s = s.replace(marca, f'data:{mime};base64,{b64(f)}')

    video = ASSETS / VIDEO
    datos = f'<script type="text/plain" id="vid64">{b64(video)}</script>' if video.exists() else ''
    s = s.replace('__VIDEO_DATA__', datos)

    # el <body> se abre después de los estilos para que el HTML sea válido al abrirlo desde el disco
    a = '</style>\n\n<template id="tplPantalla">'
    if a not in s:
        print('No encontré el inicio de la plantilla de la pantalla', file=sys.stderr)
        return 1
    s = s.replace(a, '</style>\n</head>\n<body>\n<template id="tplPantalla">', 1)
    head = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n')

    DIST.mkdir(exist_ok=True)
    out = DIST / 'consola-acto.html'
    out.write_text(head + s + '\n</body>\n</html>\n', encoding='utf-8')
    print(f'Listo: {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.1f} MB)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
