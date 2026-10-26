#!/usr/bin/env python3
"""Prueba de humo de punta a punta con Playwright (Chromium).

Abre la consola, carga contenidos de ejemplo, abre la pantalla del proyector y recorre
lanzar video / imagen / música, negro, fondos agregados, créditos y opciones "Al terminar".

Requisitos: Playwright en .venv/ (ver CLAUDE.md) y ffmpeg (para generar los archivos de ejemplo)
Uso:        .venv/bin/python tests/smoke.py   (compila con build.py y prueba dist/consola-acto.html)

Nota: el Chromium de Playwright no trae H.264, por eso los videos de ejemplo son WebM.
Los MP4 no se reproducen en la prueba, pero sí en Chrome/Brave.
"""
import pathlib
import subprocess
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import build  # noqa: E402

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
    if subprocess.run([sys.executable, str(ROOT / 'build.py')]).returncode:
        return 1
    dist = build.SALIDA
    archivos, fallas, errores = ejemplos(), [], []

    def check(nombre, valor, esperado):
        ok = esperado in valor
        corto = next((l.strip() for l in valor.splitlines() if l.strip()), '')
        print(('OK   ' if ok else 'FALLA'), nombre, '→', corto[:70] + ('…' if len(corto) > 70 else ''))
        if not ok:
            fallas.append(nombre)

    check('licencia dentro del HTML', dist.read_text(encoding='utf-8')[:1500], 'Copyright (c) 2026 Gustavo Earnshaw')
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        ctx = b.new_context(viewport={'width': 1366, 'height': 900})
        c = ctx.new_page()
        c.on('pageerror', lambda e: errores.append('consola: ' + str(e)))
        c.goto(dist.as_uri()); c.wait_for_timeout(500)
        c.evaluate('localStorage.clear()'); c.reload(); c.wait_for_timeout(800)
        c.set_input_files('#inFiles', archivos); c.wait_for_timeout(1200)
        with ctx.expect_page() as pi:
            c.click('#abrir')
        p = pi.value
        p.on('pageerror', lambda e: errores.append('pantalla: ' + str(e)))
        p.wait_for_timeout(2000); p.click('#arranque'); c.wait_for_timeout(800)

        check('conexión', c.inner_text('#conn'), 'Proyector conectado')
        check('título de la consola', c.title(), 'Consola del acto')
        check('título del proyector', p.title(), 'Consola del acto')
        check('clave guardada', str(c.evaluate('Object.keys(localStorage)')), 'consola-acto:programa')

        # arranca vacía: sin fondos, la pantalla queda en negro
        check('sin fondos: aviso en la consola', c.inner_text('#bgList'), 'Todavía no hay fondos')
        check('sin fondos: al aire', c.inner_text('#airSub'), 'Sin fondos cargados')
        check('sin fondos: pantalla en negro', p.eval_on_selector('section.scene.on', 'e => e.id'), 'sN')

        # créditos; después de tocarlos, Espacio sigue lanzando el siguiente (se prueba abajo)
        c.click('.creditos summary'); c.wait_for_timeout(200)
        creditos = c.inner_text('.creditos')
        for texto in ('Gustavo Earnshaw', 'Instituto Superior Cristo Rey', 'Claude', 'licencia MIT'):
            check('créditos: ' + texto, creditos, texto)

        c.keyboard.press('Space'); p.wait_for_timeout(1500)
        check('lanzar video', c.inner_text('#airName'), 'Danza')
        c.keyboard.press('Space'); p.wait_for_timeout(1500)
        check('lanzar imagen', c.inner_text('#airName'), 'Foto')
        check('miniatura al aire', c.eval_on_selector('#airThumb', 'e => e.style.backgroundImage'), 'blob:')
        check('miniatura siguiente (música)', c.inner_text('#nextThumb'), '♪')
        c.keyboard.press('Space'); p.wait_for_timeout(1200)
        check('lanzar música', c.inner_text('#musName'), 'Musica')
        c.keyboard.press('n'); p.wait_for_timeout(1200)
        check('negro', c.inner_text('#airName'), 'Negro')
        # "Cortar música" tiene que andar aunque la ventana del proyector no se vea: ahí el navegador
        # no ejecuta requestAnimationFrame (se simula anulándolo)
        p.evaluate('window.requestAnimationFrame = () => 0')
        c.keyboard.press('s'); p.wait_for_timeout(2000)
        check('cortar música', c.inner_text('#musName'), 'Sin música')
        check('cortar música (se detiene)', str(p.evaluate("document.getElementById('mus').paused")), 'True')
        c.keyboard.press('f'); p.wait_for_timeout(1500)
        check('fondos', c.inner_text('#airName'), 'Fondos')

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

        # fondos agregados: el primero aparece enseguida, en rotación
        c.keyboard.press('f'); p.wait_for_timeout(500)
        c.set_input_files('#bgFiles', [a for a in archivos if a.endswith(('.jpg', '.webm'))]); p.wait_for_timeout(1500)
        check('fondos agregados: rotación', c.inner_text('#airSub'), 'Danza · rotación automática')
        check('fondos agregados: en pantalla', p.eval_on_selector('section.scene.on', 'e => e.id'), 'sU')
        c.locator('.bgrow', has_text='Foto').locator('.bgname').click(); p.wait_for_timeout(1500)
        check('fondo agregado fijo', c.inner_text('#airSub'), 'Foto · fijo')

        # memoria: al volver a abrir la consola está todo como se dejó (orden manual, ajustes y fondos)
        c.locator('.c-row').nth(2).locator('[data-act="up"]').click(); c.wait_for_timeout(500)
        c2 = ctx.new_page(); c2.on('pageerror', lambda e: errores.append('consola reabierta: ' + str(e)))
        c2.goto(dist.as_uri()); c2.wait_for_timeout(1500)
        check('reabrir: programa en el mismo orden', str(c2.eval_on_selector_all('.c-row .fname', 'els => els.map(e => e.textContent)')),
              "['01 Danza.webm', '03 Musica.ogg', '02 Foto.jpg']")
        check('reabrir: ajustes', c2.locator('.c-row').first.locator('select[data-act="end"]').input_value(), 'repetir')
        check('reabrir: fondos', str(c2.eval_on_selector_all('#bgList .bgname b', 'els => els.map(e => e.textContent)')), "['Danza', 'Foto']")
        check('reabrir: aviso', c2.inner_text('#toast'), 'Se recuperó lo que habías cargado')
        c2.close()

        # al quitarlos (con confirmación), vuelve a negro
        c.click('#bgVaciar'); c.click('#bgVaciar'); p.wait_for_timeout(1500)
        check('quitar fondos: al aire', c.inner_text('#airSub'), 'Sin fondos cargados')
        check('quitar fondos: pantalla en negro', p.eval_on_selector('section.scene.on', 'e => e.id'), 'sN')

        # al vaciar todo se borran las copias guardadas, y al reabrir la consola está vacía
        copias = "new Promise(ok => { const r = indexedDB.open('consola-acto'); r.onsuccess = () => { const q = r.result.transaction('archivos').objectStore('archivos').count(); q.onsuccess = () => ok(q.result); }; })"
        check('copias guardadas: solo las del programa', str(c.evaluate(copias)), '3')
        c.click('#vaciar'); c.click('#vaciar'); c.wait_for_timeout(800)
        check('vaciar: se borran las copias', str(c.evaluate(copias)), '0')
        c2 = ctx.new_page(); c2.goto(dist.as_uri()); c2.wait_for_timeout(1200)
        check('reabrir vacía', c2.inner_text('#list'), 'Todavía no hay contenidos')
        c2.close()

        b.close()

    for e in errores:
        print('ERROR JS', e)
    print('\n' + ('Todo bien.' if not fallas and not errores else f'{len(fallas)} fallas, {len(errores)} errores JS.'))
    return 1 if fallas or errores else 0


if __name__ == '__main__':
    sys.exit(main())
