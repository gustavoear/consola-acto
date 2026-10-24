#!/usr/bin/env python3
"""Compila la consola en un único HTML autocontenido (dist/consola-acto.html).

Une src/consola.html con el CSS de la pantalla del proyector y agrega al principio el aviso
de licencia (LICENSE), porque el archivo compilado se copia y se comparte solo.

Uso:  python3 build.py
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC, DIST = ROOT / 'src', ROOT / 'dist'
SALIDA = DIST / 'consola-acto.html'
# dirección del repositorio, para los créditos; mientras esté vacía, el link no aparece
REPO = 'https://github.com/gustavoear/consola-acto'


def main() -> int:
    s = (SRC / 'consola.html').read_text(encoding='utf-8')
    s = s.replace('/*CSS_PANTALLA*/', (SRC / 'pantalla.css').read_text(encoding='utf-8'))

    # línea del repositorio en "Acerca de": se completa o se quita entera
    i, j = s.find('<!--REPO-->'), s.find('<!--/REPO-->')
    if i < 0 or j < 0:
        print('No encontré la línea del repositorio en los créditos', file=sys.stderr)
        return 1
    s = s[:i] + (s[i + len('<!--REPO-->'):j].replace('__REPO__', REPO) if REPO else '') + s[j + len('<!--/REPO-->'):]

    # el <body> se abre después de los estilos para que el HTML sea válido al abrirlo desde el disco
    a = '</style>\n\n<template id="tplPantalla">'
    if a not in s:
        print('No encontré el inicio de la plantilla de la pantalla', file=sys.stderr)
        return 1
    s = s.replace(a, '</style>\n</head>\n<body>\n<template id="tplPantalla">', 1)
    licencia = (ROOT / 'LICENSE').read_text(encoding='utf-8').strip()
    head = ('<!doctype html>\n<html lang="es">\n<!--\n  Consola del acto' + (f' · {REPO}' if REPO else '') + '\n\n'
            + '\n'.join('  ' + l if l else '' for l in licencia.splitlines()) + '\n-->\n'
            '<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1">\n')

    DIST.mkdir(exist_ok=True)
    SALIDA.write_text(head + s + '\n</body>\n</html>\n', encoding='utf-8')
    print(f'Listo: {SALIDA.relative_to(ROOT)} ({SALIDA.stat().st_size / 1e3:.0f} KB)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
