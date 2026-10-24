  // ===== Lienzos animados =====
  // DIBUJOS[tipo](sec, P) prepara el dibujo de una escena (sec) con su paleta (P) y devuelve
  // { size, draw }: size() se llama al cambiar el tamaño de la ventana y draw(t) en cada cuadro.
  // Los colores salen de la paleta del fondo: las variantes cambian la luminosidad del color base.
  let dpr = 1;
  const rnd = Math.random;
  const lienzo = sec => { const c = sec.querySelector('canvas'); return { c, x: c.getContext('2d'), W: 0, H: 0 }; };
  const ajustar = k => { k.W = k.c.width = innerWidth * dpr; k.H = k.c.height = innerHeight * dpr; };
  const cuantos = div => Math.round(innerWidth * innerHeight / div);
  const dust = (W, H, any) => ({ x: rnd() * W, y: any ? rnd() * H : H + 10, r: (rnd() * 1.8 + .4) * dpr, v: (rnd() * .25 + .08) * dpr, sw: rnd() * 6.28, tw: rnd() * .02 + .005, a: rnd() * .6 + .25 });
  const ember = (W, H, any) => ({ x: rnd() * W, y: any ? rnd() * H : H + 20 * dpr, r: (rnd() * 2.2 + .6) * dpr, v: (rnd() * .5 + .2) * dpr, ph: rnd() * 6.28, f: rnd() * .05 + .02, hot: rnd() });
  // papel picado en los colores cols
  const conf = (W, H, any, cols) => ({ x: rnd() * W, y: any ? rnd() * H : -20 * dpr, w: (rnd() * 8 + 5) * dpr, h: (rnd() * 4 + 3) * dpr,
    v: (rnd() * .6 + .35) * dpr, sw: rnd() * 6.28, sws: rnd() * .02 + .008, rot: rnd() * 6.28, rs: (rnd() - .5) * .06,
    flip: rnd() * 6.28, fs: rnd() * .05 + .02, c: cols[(rnd() * cols.length) | 0], a: rnd() * .35 + .55 });
  // centro y tamaño (en píxeles del lienzo) de la imagen principal de la escena
  const centro = (img, alto = .5) => { const r = img.getBoundingClientRect(); return { cx: (r.left + r.width / 2) * dpr, cy: (r.top + r.height * alto) * dpr, r }; };

  const DIBUJOS = {
    // logo sobre un medallón de luz blanca, con rayos y papel picado
    logo(sec, P) {
      const L = lienzo(sec), img = sec.querySelector('img');
      const C = { centro: escala(P.fondo, 1.45), borde: escala(P.fondo, .46), rayo: rgb(luz(P.fondo, .87, 1)),
        luz: [.98, .93, .89].map(l => rgb(luz(P.fondo, l, 1))) };
      sec.style.setProperty('--sombra', `rgba(${rgb(escala(P.fondo, .8))},.35)`);
      let confL = [];
      return {
        size() { ajustar(L); confL = Array.from({ length: cuantos(16000) }, () => conf(L.W, L.H, true, P.papel)); },
        draw(t) {
          const { x, W, H } = L, { cx, cy, r } = centro(img), cr = Math.max(r.width, r.height) * dpr;
          const g = x.createRadialGradient(cx, cy, 0, cx, cy, Math.max(W, H) * .8);
          g.addColorStop(0, C.centro); g.addColorStop(.4, P.fondo); g.addColorStop(1, C.borde);
          x.fillStyle = g; x.fillRect(0, 0, W, H);
          // rayos claros que giran detrás del medallón
          x.save(); x.translate(cx, cy); x.rotate(t * .0004);
          const rays = 32, R = Math.hypot(W, H);
          for (let i = 0; i < rays; i++) {
            x.rotate(Math.PI * 2 / rays);
            const a = .06 + .03 * Math.sin(t * .01 + i * .9), rg = x.createLinearGradient(0, 0, R, 0);
            rg.addColorStop(.1, `rgba(${C.rayo},${a})`); rg.addColorStop(.8, `rgba(${C.rayo},0)`);
            x.fillStyle = rg; x.beginPath(); x.moveTo(0, 0); x.lineTo(R, -R * .03); x.lineTo(R, R * .03); x.closePath(); x.fill();
          }
          x.restore();
          // medallón de luz blanca para que el logo resalte
          const p = .96 + .04 * Math.sin(t * .012), mr = cr * .9, m = x.createRadialGradient(cx, cy, 0, cx, cy, mr);
          m.addColorStop(0, `rgba(255,255,255,${p})`); m.addColorStop(.6, `rgba(${C.luz[0]},${p * .95})`);
          m.addColorStop(.8, `rgba(${C.luz[1]},${p * .4})`); m.addColorStop(1, `rgba(${C.luz[2]},0)`);
          x.fillStyle = m; x.beginPath(); x.arc(cx, cy, mr, 0, Math.PI * 2); x.fill();
          // papel picado que cae
          for (const q of confL) {
            q.y += q.v; q.sw += q.sws; q.x += Math.sin(q.sw) * .6 * dpr; q.rot += q.rs; q.flip += q.fs;
            if (q.y > H + 20 * dpr) Object.assign(q, conf(W, H, false, P.papel));
            const dx = q.x - cx, dy = q.y - cy, inside = Math.hypot(dx, dy) < cr * .5;
            x.save(); x.translate(q.x, q.y); x.rotate(q.rot); x.scale(1, Math.cos(q.flip));
            x.globalAlpha = q.a * (inside ? .35 : 1); x.fillStyle = q.c; x.fillRect(-q.w / 2, -q.h / 2, q.w, q.h);
            x.restore();
          }
          x.globalAlpha = 1;
        }
      };
    },

    // texto centrado con rayos y polvo dorado
    aniversario(sec, P) {
      const A = lienzo(sec);
      const C = { centro: escala(P.fondo, 1.37), borde: escala(P.fondo, .44), rayo: rgb(P.acento), halo: rgb(luz(P.acento, .83, 1)),
        polvo: rgb(luz(P.acento, .79, 1)), brillo: rgb(luz(P.acento, .735, 1)) };
      let dustA = [];
      return {
        size() { ajustar(A); dustA = Array.from({ length: cuantos(9000) }, () => dust(A.W, A.H, true)); },
        draw(t) {
          const { x, W, H } = A;
          const g = x.createRadialGradient(W/2, H*.48, 0, W/2, H*.48, Math.max(W, H) * .75);
          g.addColorStop(0, C.centro); g.addColorStop(.45, P.fondo); g.addColorStop(1, C.borde);
          x.fillStyle = g; x.fillRect(0, 0, W, H);
          x.save(); x.translate(W/2, H*.48); x.rotate(t * .0006);
          const R = Math.hypot(W, H), rays = 24;
          for (let i = 0; i < rays; i++) {
            x.rotate(Math.PI * 2 / rays);
            const p = .035 + .02 * Math.sin(t * .01 + i), rg = x.createLinearGradient(0, 0, R, 0);
            rg.addColorStop(0, `rgba(${C.rayo},${p})`); rg.addColorStop(1, `rgba(${C.rayo},0)`);
            x.fillStyle = rg; x.beginPath(); x.moveTo(0, 0); x.lineTo(R, -R * .045); x.lineTo(R, R * .045); x.closePath(); x.fill();
          }
          x.restore();
          const h = x.createRadialGradient(W/2, H*.48, 0, W/2, H*.48, Math.min(W, H) * .45);
          h.addColorStop(0, `rgba(${C.halo},${.10 + .03 * Math.sin(t * .015)})`); h.addColorStop(1, `rgba(${C.halo},0)`);
          x.fillStyle = h; x.fillRect(0, 0, W, H);
          for (const p of dustA) {
            p.y -= p.v; p.sw += p.tw; p.x += Math.sin(p.sw) * .25 * dpr;
            if (p.y < -10) Object.assign(p, dust(W, H, false));
            x.beginPath(); x.arc(p.x, p.y, p.r, 0, Math.PI * 2);
            x.fillStyle = `rgba(${C.polvo},${p.a * (.6 + .4 * Math.sin(p.sw * 3))})`;
            x.shadowColor = `rgba(${C.brillo},.9)`; x.shadowBlur = 8 * dpr; x.fill();
          }
          x.shadowBlur = 0;
        }
      };
    },

    // escudo a la izquierda y cifra a la derecha, con rayos, halo y brasas que suben
    escudo(sec, P) {
      const B = lienzo(sec), img = sec.querySelector('img');
      const C = { arriba: escala(P.fondo, .63), rayo: rgb(P.acento), halo: [.92, .81, .75].map(l => rgb(luz(P.acento, l, 1))),
        brasa: [rgb(luz(P.brasas, .68, 1)), rgb(P.brasas), rgb(luz(P.acento, .79, 1))] };
      sec.style.setProperty('--brasas', P.brasas);
      let embB = [];
      return {
        size() { ajustar(B); embB = Array.from({ length: cuantos(14000) }, () => ember(B.W, B.H, true)); },
        draw(t) {
          const { x, W, H } = B, { cx, cy, r } = centro(img), cr = Math.max(r.width, r.height) * dpr;
          const g = x.createLinearGradient(0, 0, 0, H);
          g.addColorStop(0, C.arriba); g.addColorStop(.6, P.fondo); g.addColorStop(1, P.fondo_abajo);
          x.fillStyle = g; x.fillRect(0, 0, W, H);
          x.save(); x.translate(cx, cy); x.rotate(-t * .0005);
          const rays = 48, R = cr * 1.6;
          for (let i = 0; i < rays; i++) {
            x.rotate(Math.PI * 2 / rays);
            const a = .05 + .03 * Math.sin(t * .012 + i * .7), rg = x.createLinearGradient(0, 0, R, 0);
            rg.addColorStop(.15, `rgba(${C.rayo},${a})`); rg.addColorStop(1, `rgba(${C.rayo},0)`);
            x.fillStyle = rg; x.beginPath(); x.moveTo(0, 0); x.lineTo(R, -R * .02); x.lineTo(R, R * .02); x.closePath(); x.fill();
          }
          x.restore();
          const pulse = .5 + .06 * Math.sin(t * .013), h = x.createRadialGradient(cx, cy, 0, cx, cy, cr * .62);
          h.addColorStop(0, `rgba(${C.halo[0]},${pulse})`); h.addColorStop(.55, `rgba(${C.halo[1]},${pulse * .45})`); h.addColorStop(1, `rgba(${C.halo[2]},0)`);
          x.fillStyle = h; x.fillRect(0, 0, W, H);
          x.globalCompositeOperation = 'lighter';
          for (const p of embB) {
            p.y -= p.v; p.ph += p.f; p.x += Math.sin(p.ph) * .4 * dpr;
            if (p.y < -20) Object.assign(p, ember(W, H, false));
            const life = Math.min(1, p.y / H + .15), fl = .55 + .45 * Math.sin(p.ph * 2.3);
            const col = C.brasa[p.hot > .6 ? 0 : p.hot > .25 ? 1 : 2];
            const s = p.r * 4, eg = x.createRadialGradient(p.x, p.y, 0, p.x, p.y, s);
            eg.addColorStop(0, `rgba(${col},${.8 * life * fl})`); eg.addColorStop(1, `rgba(${col},0)`);
            x.fillStyle = eg; x.fillRect(p.x - s, p.y - s, s * 2, s * 2);
          }
          x.globalCompositeOperation = 'source-over';
        }
      };
    },

    // emblema sobre bordado (vyshyvanka) en punto cruz, como el de Вільні Соколи
    bordado(sec, P) {
      const S = lienzo(sec), img = sec.querySelector('img');
      const C = { centro: escala(P.fondo, 1.68), borde: escala(P.fondo, .4), hilo1: rgb(P.hilos[0]),
        brillo: rgb(luz(P.fondo, .62, 1)), franja: `rgba(${rgb(escala(P.fondo, .57))},.55)` };
      sec.style.setProperty('--brillo1', `rgba(${rgb(luz(P.fondo, .58, 1))},.45)`);
      sec.style.setProperty('--brillo2', `rgba(${rgb(P.hilos[0])},.35)`);
      let bandTile, starTile, bandW;
      // m: matriz del motivo; 1 y 2 = colores.hilos (rojo y blanco en Sokoly)
      function stitchTile(m, cell, pad) {
        const n = m.length, c = document.createElement('canvas');
        c.width = c.height = n * cell + pad * 2; const x = c.getContext('2d');
        for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
          if (!m[i][j]) continue;
          const px = pad + j * cell, py = pad + i * cell, s = cell * .82;
          x.fillStyle = P.hilos[m[i][j] - 1];
          // punto cruz: dos diagonales gruesas
          x.save(); x.translate(px + cell / 2, py + cell / 2); x.rotate(Math.PI / 4);
          x.fillRect(-s * .62, -s * .17, s * 1.24, s * .34); x.fillRect(-s * .17, -s * .62, s * .34, s * 1.24);
          x.restore();
        }
        return c;
      }
      function makeTiles() {
        const cell = Math.max(4, Math.round(Math.min(innerWidth, innerHeight) * dpr / 115));
        starTile = stitchTile(motif(15), cell, cell);
        // franja lateral tipo rushnyk: motivos apilados con bordes de punto cruz
        const tile = stitchTile(motif(11), cell, 0), w = tile.width + cell * 6, h = tile.height + cell * 4;
        const b = document.createElement('canvas'); b.width = w; b.height = h; const x = b.getContext('2d');
        x.fillStyle = C.franja; x.fillRect(0, 0, w, h);
        x.drawImage(tile, cell * 3, cell * 2);
        for (let k = 0; k < h; k += cell * 2) {
          x.fillStyle = P.hilos[(k / (cell * 2)) % 2 ? 0 : 1];
          x.fillRect(cell * .6, k + cell * .5, cell, cell); x.fillRect(w - cell * 1.6, k + cell * .5, cell, cell);
        }
        bandTile = b; bandW = w;
      }
      return {
        size() { ajustar(S); makeTiles(); },
        draw(t) {
          const { x, W, H } = S, { cx, cy, r } = centro(img), cr = Math.min(r.width, r.height) * dpr / 2;
          const g = x.createRadialGradient(cx, cy, 0, cx, cy, Math.max(W, H) * .75);
          g.addColorStop(0, C.centro); g.addColorStop(.5, P.fondo); g.addColorStop(1, C.borde);
          x.fillStyle = g; x.fillRect(0, 0, W, H);
          // resplandor (color del primer hilo y del fondo) que late detrás del emblema
          const p = .5 + .5 * Math.sin(t * .02);
          let h = x.createRadialGradient(cx, cy, cr * .7, cx, cy, cr * 1.5);
          h.addColorStop(0, `rgba(${C.hilo1},${.18 + .12 * p})`); h.addColorStop(1, `rgba(${C.hilo1},0)`);
          x.fillStyle = h; x.fillRect(0, 0, W, H);
          h = x.createRadialGradient(cx, cy, cr * .9, cx, cy, cr * 1.9);
          h.addColorStop(0, `rgba(${C.brillo},${.22 + .1 * (1 - p)})`); h.addColorStop(1, `rgba(${C.brillo},0)`);
          x.fillStyle = h; x.fillRect(0, 0, W, H);
          // anillo de estrellas bordadas que gira alrededor del emblema
          const ring = cr * 1.32, n = 12, sz = starTile.width;
          x.save(); x.translate(cx, cy); x.rotate(t * .0012);
          for (let i = 0; i < n; i++) {
            const a = i / n * Math.PI * 2;
            x.save(); x.rotate(a); x.translate(ring, 0); x.rotate(-a - t * .0012);
            x.globalAlpha = .55 + .35 * Math.sin(t * .03 + i * 1.3);
            x.drawImage(starTile, -sz / 2, -sz / 2); x.restore();
          }
          x.restore(); x.globalAlpha = 1;
          // franjas de bordado en los costados, que suben y bajan lentamente
          const bh = bandTile.height, off = (t * .35 * dpr) % bh, m = Math.round(W * .03);
          for (let y = -bh + off; y < H; y += bh) x.drawImage(bandTile, m, y);
          for (let y = -off; y < H; y += bh) x.drawImage(bandTile, W - m - bandW, y);
        }
      };
    }
  };

  // motivo romboidal con estrella de ocho puntas (bordado)
  function motif(n) {
    const c = (n - 1) / 2, m = [];
    for (let i = 0; i < n; i++) { m.push([]); for (let j = 0; j < n; j++) {
      const x = Math.abs(i - c), y = Math.abs(j - c), d = x + y; let v = 0;
      if (d === c) v = 1;
      else if (d === c - 2 && (i + j) % 2 === 0) v = 1;
      else if ((x === y && d <= c - 4 && d >= 2) || ((x === 0 || y === 0) && d <= c - 4)) v = 1;
      else if (d === 1) v = 2;
      m[i].push(v);
    } }
    return m;
  }
