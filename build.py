#!/usr/bin/env python3
"""Compila la consola de un evento en un único HTML autocontenido (dist/<id>.html).

Lee evento.json de la carpeta del evento, une src/consola.html con el CSS, las escenas
y el dibujo de la pantalla del proyector, embebe la configuración y las imágenes y el
video del evento como data URIs, para que el archivo funcione sin internet ni archivos sueltos.

Uso:  python3 build.py                        -> compila eventos/cristo-rey-70
      python3 build.py ruta/a/la/carpeta      -> dist/<id>.html
"""
import base64
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
SRC, DIST = ROOT / 'src', ROOT / 'dist'
POR_DEFECTO = ROOT / 'eventos' / 'cristo-rey-70'

# tipos de fondo (un molde por tipo en src/escenas.html); los de IMAGENES llevan "imagen"
IMAGENES = {'escudo', 'logo', 'bordado'}
TIPOS = IMAGENES | {'aniversario', 'video'}
MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp',
        '.svg': 'image/svg+xml', '.gif': 'image/gif', '.avif': 'image/avif',
        '.mp4': 'video/mp4', '.webm': 'video/webm', '.m4v': 'video/mp4'}
TEXTOS = ('titulo', 'institucion', 'numero', 'unidad', 'anios', 'lema')
# colores que entiende cada parte: los generales y los propios de algunos tipos de fondo
COLORES = {'fondo', 'acento', 'texto'}
COLORES_TIPO = {'escudo': {'fondo_abajo', 'brasas'}, 'logo': {'papel'}, 'bordado': {'hilos'}}
LISTAS = {'papel': 1, 'hilos': 2}  # colores que van en lista, con su cantidad mínima
HEX = re.compile(r'#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})')


class ErrorEvento(Exception):
    pass


def b64(path: pathlib.Path) -> str:
    return base64.b64encode(path.read_bytes()).decode()


def archivo(carpeta: pathlib.Path, nombre, donde: str, clase: str) -> pathlib.Path:
    if not isinstance(nombre, str) or not nombre:
        raise ErrorEvento(f'{donde}: falta el nombre del archivo')
    f = carpeta / nombre
    if not f.is_file():
        raise ErrorEvento(f'{donde}: no encuentro {f.relative_to(ROOT) if f.is_relative_to(ROOT) else f}')
    if not MIME.get(f.suffix.lower(), '').startswith(clase + '/'):
        raise ErrorEvento(f'{donde}: {nombre} no es {"una imagen" if clase == "image" else "un video"} que conozca'
                          f' ({", ".join(sorted(k for k, v in MIME.items() if v.startswith(clase + "/")))})')
    return f


def colores(c, permitidos: set, donde: str) -> None:
    if c is None:
        return
    if not isinstance(c, dict):
        raise ErrorEvento(f'{donde}: "colores" tiene que ser un objeto {{…}}')
    for k, v in c.items():
        if k not in permitidos:
            raise ErrorEvento(f'{donde}: no conozco el color "{k}" (se puede usar: {", ".join(sorted(permitidos))})')
        lista = v if k in LISTAS else [v]
        if k in LISTAS and (not isinstance(v, list) or len(v) < LISTAS[k]):
            raise ErrorEvento(f'{donde}: "{k}" tiene que ser una lista de al menos {LISTAS[k]} colores')
        for x in lista:
            if not isinstance(x, str) or not HEX.fullmatch(x):
                raise ErrorEvento(f'{donde}: el color "{k}" tiene que ser como "#e2b85c", no {json.dumps(x, ensure_ascii=False)}')


def leer_evento(carpeta: pathlib.Path) -> dict:
    j = carpeta / 'evento.json'
    if not j.is_file():
        raise ErrorEvento(f'No encuentro {j}')
    try:
        ev = json.loads(j.read_text(encoding='utf-8'))
    except json.JSONDecodeError as e:
        raise ErrorEvento(f'{j.name} tiene un error en la línea {e.lineno}: {e.msg}')
    if not isinstance(ev, dict):
        raise ErrorEvento(f'{j.name} tiene que ser un objeto {{…}}')
    for k in ('id', 'titulo', 'institucion'):
        if not isinstance(ev.get(k), str) or not ev[k].strip():
            raise ErrorEvento(f'Falta el campo "{k}" en {j.name}')
    if not re.fullmatch(r'[a-z0-9]+(-[a-z0-9]+)*', ev['id']):
        raise ErrorEvento(f'"id" solo puede tener minúsculas, números y guiones (por ejemplo "escuela-50"), no "{ev["id"]}"')
    for k in TEXTOS:
        if not isinstance(ev.get(k, ''), str):
            raise ErrorEvento(f'El campo "{k}" tiene que ser un texto')
    colores(ev.get('colores'), COLORES, j.name)
    fondos = ev.get('fondos')
    if not isinstance(fondos, list) or not fondos:
        raise ErrorEvento(f'Falta la lista "fondos" en {j.name}')
    cuenta = {}
    for i, f in enumerate(fondos, 1):
        donde = f'fondos[{i}]'
        if not isinstance(f, dict) or f.get('tipo') not in TIPOS:
            raise ErrorEvento(f'{donde}: "tipo" tiene que ser uno de {", ".join(sorted(TIPOS))}')
        # clave del fondo: su tipo, o tipo-2, tipo-3… si se repite
        cuenta[f['tipo']] = cuenta.get(f['tipo'], 0) + 1
        f['clave'] = f['tipo'] if cuenta[f['tipo']] == 1 else f'{f["tipo"]}-{cuenta[f["tipo"]]}'
        if not isinstance(f.get('nombre'), str) or not f['nombre'].strip():
            raise ErrorEvento(f'{donde}: falta "nombre"')
        if not isinstance(f.get('rota', True), bool):
            raise ErrorEvento(f'{donde}: "rota" tiene que ser true o false')
        colores(f.get('colores'), COLORES | COLORES_TIPO.get(f['tipo'], set()), donde)
        if f['tipo'] in IMAGENES:
            archivo(carpeta, f.get('imagen'), donde, 'image')
        if f['tipo'] == 'video':
            archivo(carpeta, f.get('archivo'), donde, 'video')
            for r in f.setdefault('rotulos', []):
                if not isinstance(r, dict) or not isinstance(r.get('desde'), (int, float)) or not isinstance(r.get('texto'), str):
                    raise ErrorEvento(f'{donde}: cada rótulo necesita "desde" (segundos) y "texto"')
    return ev


def main() -> int:
    carpeta = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else POR_DEFECTO
    try:
        ev = leer_evento(carpeta)
    except ErrorEvento as e:
        print(f'Error: {e}', file=sys.stderr)
        return 1

    s = (SRC / 'consola.html').read_text(encoding='utf-8')
    s = s.replace('/*CSS_PANTALLA*/', (SRC / 'pantalla.css').read_text(encoding='utf-8'))
    s = s.replace('<!--ESCENAS-->', (SRC / 'escenas.html').read_text(encoding='utf-8'))
    s = s.replace('/*DIBUJO*/', (SRC / 'dibujo.js').read_text(encoding='utf-8'))
    s = s.replace('__TITULO__', html.escape('Consola · ' + ev['titulo']))

    # las imágenes viajan dentro de la configuración; los videos, aparte, en un <script> cada uno
    videos = []
    for f in ev['fondos']:
        if f['tipo'] in IMAGENES:
            img = carpeta / f['imagen']
            f['src'] = f'data:{MIME[img.suffix.lower()]};base64,{b64(img)}'
        if f['tipo'] == 'video':
            v = carpeta / f['archivo']
            videos.append(f'<script type="text/plain" class="vid64" data-clave="{f["clave"]}" '
                          f'data-mime="{MIME[v.suffix.lower()]}">{b64(v)}</script>')
    s = s.replace('__VIDEO_DATA__', '\n'.join(videos))
    # "</" escapado para que un texto del evento no pueda cerrar el <script>
    s = s.replace('__EVENTO__', json.dumps(ev, ensure_ascii=False).replace('</', '<\\/'))

    # el <body> se abre después de los estilos para que el HTML sea válido al abrirlo desde el disco
    a = '</style>\n\n<template id="tplPantalla">'
    if a not in s:
        print('No encontré el inicio de la plantilla de la pantalla', file=sys.stderr)
        return 1
    s = s.replace(a, '</style>\n</head>\n<body>\n<template id="tplPantalla">', 1)
    head = ('<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\n')

    DIST.mkdir(exist_ok=True)
    out = DIST / f'{ev["id"]}.html'
    out.write_text(head + s + '\n</body>\n</html>\n', encoding='utf-8')
    print(f'Listo: {out.relative_to(ROOT)} ({out.stat().st_size / 1e6:.1f} MB)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
