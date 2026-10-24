#!/usr/bin/env python3
"""Prueba de humo de punta a punta con Playwright (Chromium).

Abre la consola, carga contenidos de ejemplo, abre la pantalla del proyector y recorre
lanzar video / imagen / música, negro, fondos, fondos agregados y opciones "Al terminar".

Requisitos: python3 -m pip install playwright && python3 -m playwright install chromium
            ffmpeg (para generar los archivos de ejemplo)
Uso:        python3 build.py && python3 tests/smoke.py

Nota: el Chromium de Playwright no trae H.264, por eso los videos de ejemplo son WebM.
El video de la historia (MP4) no se reproduce en la prueba, pero sí en Chrome/Brave.
"""
import pathlib
import subprocess
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist' / 'consola-acto.html'
MEDIA = ROOT / 'tests' / 'media'


def ejemplos():
    MEDIA.mkdir(exist_ok=True)
    ff = ['ffmpeg', '-v', 'error', '-y']
    cmds = {
        '01 Danza.webm': ff + ['-f', 'lavfi', '-i', 'testsrc2=size=1280x720:rate=24:duration=6', '-f', 'lavfi', '-i',
                               'sine=frequency=440:duration=6', '-c:v', 'libvpx-vp9', '-b:v', '1M', '-deadline', 'realtime',
                               '-cpu-used', '8', '-c:a', 'libopus'],
        '02 Foto.jpg': ff + ['-f', 'lavfi', '-i', 'color=c=0x2a6f3a:size=1200x1600', '-frames:v', '1'],
        '03 Musica.ogg': ff + ['-f', 'lavfi', '-i', 'sine=frequency=330:duration=20', '-c:a', 'libvorbis'],
    }
    for nombre, cmd in cmds.items():
        if not (MEDIA / nombre).exists():
            subprocess.run(cmd + [str(MEDIA / nombre)], check=True)
    return sorted(str(p) for p in MEDIA.iterdir())


def main() -> int:
    if not DIST.exists():
        print('Primero corré: python3 build.py', file=sys.stderr)
        return 1
    archivos, fallas, errores = ejemplos(), [], []

    def check(nombre, valor, esperado):
        ok = esperado in valor
        print(('OK   ' if ok else 'FALLA'), nombre, '→', valor)
        if not ok:
            fallas.append(nombre)

    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={'width': 1366, 'height': 900})
        c = ctx.new_page()
        c.on('pageerror', lambda e: errores.append('consola: ' + str(e)))
        c.goto(DIST.as_uri()); c.wait_for_timeout(500)
        c.evaluate('localStorage.clear()'); c.reload(); c.wait_for_timeout(800)
        c.set_input_files('#inFiles', archivos); c.wait_for_timeout(1200)
        with ctx.expect_page() as pi:
            c.click('#abrir')
        p = pi.value
        p.on('pageerror', lambda e: errores.append('pantalla: ' + str(e)))
        p.wait_for_timeout(2000); p.click('#arranque'); c.wait_for_timeout(800)

        check('conexión', c.inner_text('#conn'), 'Proyector conectado')
        c.keyboard.press('Space'); p.wait_for_timeout(1500)
        check('lanzar video', c.inner_text('#airName'), 'Danza')
        c.keyboard.press('Space'); p.wait_for_timeout(1500)
        check('lanzar imagen', c.inner_text('#airName'), 'Foto')
        c.keyboard.press('Space'); p.wait_for_timeout(1200)
        check('lanzar música', c.inner_text('#musName'), 'Musica')
        c.keyboard.press('n'); p.wait_for_timeout(1200)
        check('negro', c.inner_text('#airName'), 'Negro')
        c.keyboard.press('s'); p.wait_for_timeout(2000)
        check('cortar música', c.inner_text('#musName'), 'Sin música')
        c.keyboard.press('f'); p.wait_for_timeout(1500)
        check('fondos', c.inner_text('#airName'), 'Fondos animados')

        # "Al terminar: pasar al siguiente" cambiado en vivo
        c.keyboard.press('1'); p.wait_for_timeout(800)
        c.select_option('select[data-act="end"]', 'siguiente'); p.wait_for_timeout(6500)
        check('al terminar → siguiente', c.inner_text('#airName'), 'Foto')

        # "Llenar pantalla": el video ocupa toda la pantalla aunque el formato no coincida
        c.keyboard.press('f'); p.wait_for_timeout(500)
        c.locator('.c-row').first.locator('[data-act="fit"]').click(); c.wait_for_timeout(200)
        c.keyboard.press('1'); p.wait_for_timeout(1200)
        check('llenar pantalla', str(p.evaluate("[...document.querySelectorAll('section.media.on')].map(e => e.classList.contains('cover'))")), 'True')

        # "Al terminar: repetir": el video vuelve a empezar solo
        c.keyboard.press('1'); p.wait_for_timeout(600)
        c.locator('.c-row').first.locator('select[data-act="end"]').select_option('repetir'); p.wait_for_timeout(6500)
        check('repetir', c.inner_text('#airName'), 'Danza')
        check('repetir (sigue reproduciendo)', str(p.evaluate("[...document.querySelectorAll('section.media.on video')].some(v => v.loop && !v.paused)")), 'True')

        # fondos agregados y rotación
        c.keyboard.press('f'); p.wait_for_timeout(500)
        c.set_input_files('#bgFiles', [a for a in archivos if a.endswith('.jpg')]); c.wait_for_timeout(800)
        c.locator('.bgrow', has_text='Foto').locator('.bgname').click(); p.wait_for_timeout(1500)
        check('fondo agregado fijo', c.inner_text('#airSub'), 'Foto · fijo')

        b.close()

    for e in errores:
        print('ERROR JS', e)
    print('\n' + ('Todo bien.' if not fallas and not errores else f'{len(fallas)} fallas, {len(errores)} errores JS.'))
    return 1 if fallas or errores else 0


if __name__ == '__main__':
    sys.exit(main())
