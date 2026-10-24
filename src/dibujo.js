  // ===== Lienzos animados =====
  let dpr = 1;
  const mkCanvas = id => { const c = $(id); return { c, x: c.getContext('2d'), W: 0, H: 0 }; };
  const A = mkCanvas('cA'), B = mkCanvas('cB'), L = mkCanvas('cL'), S = mkCanvas('cS');
  let dustA = [], embB = [], confL = [];
  const rnd = Math.random;
  // colores de cada fondo (evento.json): las variantes salen de cambiar la luminosidad del color base
  const PA = paleta('aniversario'), PB = paleta('escudo'), PL = paleta('logo'), PS = paleta('bordado');
  const A_COL = { centro: escala(PA.fondo, 1.37), borde: escala(PA.fondo, .44), rayo: rgb(PA.acento), halo: rgb(luz(PA.acento, .83, 1)),
    polvo: rgb(luz(PA.acento, .79, 1)), brillo: rgb(luz(PA.acento, .735, 1)) };
  const B_COL = { arriba: escala(PB.fondo, .63), rayo: rgb(PB.acento), halo: [.92, .81, .75].map(l => rgb(luz(PB.acento, l, 1))),
    brasa: [rgb(luz(PB.brasas, .68, 1)), rgb(PB.brasas), rgb(luz(PB.acento, .79, 1))] };
  const L_COL = { centro: escala(PL.fondo, 1.45), borde: escala(PL.fondo, .46), rayo: rgb(luz(PL.fondo, .87, 1)),
    luz: [.98, .93, .89].map(l => rgb(luz(PL.fondo, l, 1))) };
  const S_COL = { centro: escala(PS.fondo, 1.68), borde: escala(PS.fondo, .4), hilo1: rgb(PS.hilos[0]),
    brillo: rgb(luz(PS.fondo, .62, 1)), franja: `rgba(${rgb(escala(PS.fondo, .57))},.55)` };
  const dust = (W, H, any) => ({ x: rnd() * W, y: any ? rnd() * H : H + 10, r: (rnd() * 1.8 + .4) * dpr, v: (rnd() * .25 + .08) * dpr, sw: rnd() * 6.28, tw: rnd() * .02 + .005, a: rnd() * .6 + .25 });
  const ember = (W, H, any) => ({ x: rnd() * W, y: any ? rnd() * H : H + 20 * dpr, r: (rnd() * 2.2 + .6) * dpr, v: (rnd() * .5 + .2) * dpr, ph: rnd() * 6.28, f: rnd() * .05 + .02, hot: rnd() });
  function size() {
    dpr = Math.min(devicePixelRatio || 1, 2);
    for (const k of [A, B, L, S]) { k.W = k.c.width = innerWidth * dpr; k.H = k.c.height = innerHeight * dpr; }
    dustA = Array.from({ length: Math.round(innerWidth * innerHeight / 9000) }, () => dust(A.W, A.H, true));
    embB = Array.from({ length: Math.round(innerWidth * innerHeight / 14000) }, () => ember(B.W, B.H, true));
    makeTiles();
    confL = Array.from({ length: Math.round(innerWidth * innerHeight / 16000) }, () => conf(L.W, L.H, true));
  }
  // papel picado en los colores del logo (colores.papel)
  const CONF_COL = PL.papel;
  function conf(W, H, any) {
    return { x: rnd() * W, y: any ? rnd() * H : -20 * dpr, w: (rnd() * 8 + 5) * dpr, h: (rnd() * 4 + 3) * dpr,
      v: (rnd() * .6 + .35) * dpr, sw: rnd() * 6.28, sws: rnd() * .02 + .008, rot: rnd() * 6.28, rs: (rnd() - .5) * .06,
      flip: rnd() * 6.28, fs: rnd() * .05 + .02, c: CONF_COL[(rnd() * CONF_COL.length) | 0], a: rnd() * .35 + .55 };
  }
  const logoImg = $('logo70');
  function drawL(t) {
    const { x, W, H } = L;
    const r = logoImg.getBoundingClientRect();
    const cx = (r.left + r.width / 2) * dpr, cy = (r.top + r.height / 2) * dpr, cr = Math.max(r.width, r.height) * dpr;
    const g = x.createRadialGradient(cx, cy, 0, cx, cy, Math.max(W, H) * .8);
    g.addColorStop(0, L_COL.centro); g.addColorStop(.4, PL.fondo); g.addColorStop(1, L_COL.borde);
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    // rayos claros que giran detrás del medallón
    x.save(); x.translate(cx, cy); x.rotate(t * .0004);
    const rays = 32, R = Math.hypot(W, H);
    for (let i = 0; i < rays; i++) {
      x.rotate(Math.PI * 2 / rays);
      const a = .06 + .03 * Math.sin(t * .01 + i * .9), rg = x.createLinearGradient(0, 0, R, 0);
      rg.addColorStop(.1, `rgba(${L_COL.rayo},${a})`); rg.addColorStop(.8, `rgba(${L_COL.rayo},0)`);
      x.fillStyle = rg; x.beginPath(); x.moveTo(0, 0); x.lineTo(R, -R * .03); x.lineTo(R, R * .03); x.closePath(); x.fill();
    }
    x.restore();
    // medallón de luz blanca para que el logo resalte
    const p = .96 + .04 * Math.sin(t * .012), mr = cr * .9, m = x.createRadialGradient(cx, cy, 0, cx, cy, mr);
    m.addColorStop(0, `rgba(255,255,255,${p})`); m.addColorStop(.6, `rgba(${L_COL.luz[0]},${p * .95})`);
    m.addColorStop(.8, `rgba(${L_COL.luz[1]},${p * .4})`); m.addColorStop(1, `rgba(${L_COL.luz[2]},0)`);
    x.fillStyle = m; x.beginPath(); x.arc(cx, cy, mr, 0, Math.PI * 2); x.fill();
    // papel picado que cae
    for (const q of confL) {
      q.y += q.v; q.sw += q.sws; q.x += Math.sin(q.sw) * .6 * dpr; q.rot += q.rs; q.flip += q.fs;
      if (q.y > H + 20 * dpr) Object.assign(q, conf(W, H, false));
      const dx = q.x - cx, dy = q.y - cy, inside = Math.hypot(dx, dy) < cr * .5;
      x.save(); x.translate(q.x, q.y); x.rotate(q.rot); x.scale(1, Math.cos(q.flip));
      x.globalAlpha = q.a * (inside ? .35 : 1); x.fillStyle = q.c; x.fillRect(-q.w / 2, -q.h / 2, q.w, q.h);
      x.restore();
    }
    x.globalAlpha = 1;
  }
  addEventListener('resize', size); size();

  function drawA(t) {
    const { x, W, H } = A;
    const g = x.createRadialGradient(W/2, H*.48, 0, W/2, H*.48, Math.max(W, H) * .75);
    g.addColorStop(0, A_COL.centro); g.addColorStop(.45, PA.fondo); g.addColorStop(1, A_COL.borde);
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    x.save(); x.translate(W/2, H*.48); x.rotate(t * .0006);
    const R = Math.hypot(W, H), rays = 24;
    for (let i = 0; i < rays; i++) {
      x.rotate(Math.PI * 2 / rays);
      const p = .035 + .02 * Math.sin(t * .01 + i), rg = x.createLinearGradient(0, 0, R, 0);
      rg.addColorStop(0, `rgba(${A_COL.rayo},${p})`); rg.addColorStop(1, `rgba(${A_COL.rayo},0)`);
      x.fillStyle = rg; x.beginPath(); x.moveTo(0, 0); x.lineTo(R, -R * .045); x.lineTo(R, R * .045); x.closePath(); x.fill();
    }
    x.restore();
    const h = x.createRadialGradient(W/2, H*.48, 0, W/2, H*.48, Math.min(W, H) * .45);
    h.addColorStop(0, `rgba(${A_COL.halo},${.10 + .03 * Math.sin(t * .015)})`); h.addColorStop(1, `rgba(${A_COL.halo},0)`);
    x.fillStyle = h; x.fillRect(0, 0, W, H);
    for (const p of dustA) {
      p.y -= p.v; p.sw += p.tw; p.x += Math.sin(p.sw) * .25 * dpr;
      if (p.y < -10) Object.assign(p, dust(W, H, false));
      x.beginPath(); x.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      x.fillStyle = `rgba(${A_COL.polvo},${p.a * (.6 + .4 * Math.sin(p.sw * 3))})`;
      x.shadowColor = `rgba(${A_COL.brillo},.9)`; x.shadowBlur = 8 * dpr; x.fill();
    }
    x.shadowBlur = 0;
  }

  const crest = $('crest');
  function drawB(t) {
    const { x, W, H } = B;
    const r = crest.getBoundingClientRect();
    const cx = (r.left + r.width / 2) * dpr, cy = (r.top + r.height * .5) * dpr, cr = Math.max(r.width, r.height) * dpr;
    const g = x.createLinearGradient(0, 0, 0, H);
    g.addColorStop(0, B_COL.arriba); g.addColorStop(.6, PB.fondo); g.addColorStop(1, PB.fondo_abajo);
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    x.save(); x.translate(cx, cy); x.rotate(-t * .0005);
    const rays = 48, R = cr * 1.6;
    for (let i = 0; i < rays; i++) {
      x.rotate(Math.PI * 2 / rays);
      const a = .05 + .03 * Math.sin(t * .012 + i * .7), rg = x.createLinearGradient(0, 0, R, 0);
      rg.addColorStop(.15, `rgba(${B_COL.rayo},${a})`); rg.addColorStop(1, `rgba(${B_COL.rayo},0)`);
      x.fillStyle = rg; x.beginPath(); x.moveTo(0, 0); x.lineTo(R, -R * .02); x.lineTo(R, R * .02); x.closePath(); x.fill();
    }
    x.restore();
    const pulse = .5 + .06 * Math.sin(t * .013), h = x.createRadialGradient(cx, cy, 0, cx, cy, cr * .62);
    h.addColorStop(0, `rgba(${B_COL.halo[0]},${pulse})`); h.addColorStop(.55, `rgba(${B_COL.halo[1]},${pulse * .45})`); h.addColorStop(1, `rgba(${B_COL.halo[2]},0)`);
    x.fillStyle = h; x.fillRect(0, 0, W, H);
    x.globalCompositeOperation = 'lighter';
    for (const p of embB) {
      p.y -= p.v; p.ph += p.f; p.x += Math.sin(p.ph) * .4 * dpr;
      if (p.y < -20) Object.assign(p, ember(W, H, false));
      const life = Math.min(1, p.y / H + .15), fl = .55 + .45 * Math.sin(p.ph * 2.3);
      const col = B_COL.brasa[p.hot > .6 ? 0 : p.hot > .25 ? 1 : 2];
      const s = p.r * 4, eg = x.createRadialGradient(p.x, p.y, 0, p.x, p.y, s);
      eg.addColorStop(0, `rgba(${col},${.8 * life * fl})`); eg.addColorStop(1, `rgba(${col},0)`);
      x.fillStyle = eg; x.fillRect(p.x - s, p.y - s, s * 2, s * 2);
    }
    x.globalCompositeOperation = 'source-over';
  }

  // ===== Вільні Соколи: bordado (vyshyvanka) en punto cruz =====
  // motivo romboidal con estrella de ocho puntas, como el del logo; 1 y 2 = colores.hilos (rojo y blanco en Sokoly)
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
  var bandTile, starTile, bandW;
  function stitchTile(m, cell, pad) {
    const n = m.length, c = document.createElement('canvas');
    c.width = c.height = n * cell + pad * 2; const x = c.getContext('2d');
    for (let i = 0; i < n; i++) for (let j = 0; j < n; j++) {
      if (!m[i][j]) continue;
      const px = pad + j * cell, py = pad + i * cell, s = cell * .82, o = (cell - s) / 2;
      x.fillStyle = PS.hilos[m[i][j] - 1];
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
    x.fillStyle = S_COL.franja; x.fillRect(0, 0, w, h);
    x.drawImage(tile, cell * 3, cell * 2);
    for (let k = 0; k < h; k += cell * 2) {
      x.fillStyle = PS.hilos[(k / (cell * 2)) % 2 ? 0 : 1];
      x.fillRect(cell * .6, k + cell * .5, cell, cell); x.fillRect(w - cell * 1.6, k + cell * .5, cell, cell);
    }
    bandTile = b; bandW = w;
  }
  const sokImg = $('sokoly');
  function drawS(t) {
    const { x, W, H } = S;
    const r = sokImg.getBoundingClientRect();
    const cx = (r.left + r.width / 2) * dpr, cy = (r.top + r.height / 2) * dpr, cr = Math.min(r.width, r.height) * dpr / 2;
    const g = x.createRadialGradient(cx, cy, 0, cx, cy, Math.max(W, H) * .75);
    g.addColorStop(0, S_COL.centro); g.addColorStop(.5, PS.fondo); g.addColorStop(1, S_COL.borde);
    x.fillStyle = g; x.fillRect(0, 0, W, H);
    // resplandor (color del primer hilo y del fondo) que late detrás del emblema
    const p = .5 + .5 * Math.sin(t * .02);
    let h = x.createRadialGradient(cx, cy, cr * .7, cx, cy, cr * 1.5);
    h.addColorStop(0, `rgba(${S_COL.hilo1},${.18 + .12 * p})`); h.addColorStop(1, `rgba(${S_COL.hilo1},0)`);
    x.fillStyle = h; x.fillRect(0, 0, W, H);
    h = x.createRadialGradient(cx, cy, cr * .9, cx, cy, cr * 1.9);
    h.addColorStop(0, `rgba(${S_COL.brillo},${.22 + .1 * (1 - p)})`); h.addColorStop(1, `rgba(${S_COL.brillo},0)`);
    x.fillStyle = h; x.fillRect(0, 0, W, H);
    // anillo de estrellas bordadas que gira alrededor del emblema
    if (starTile) {
      const ring = cr * 1.32, n = 12, sz = starTile.width;
      x.save(); x.translate(cx, cy); x.rotate(t * .0012);
      for (let i = 0; i < n; i++) {
        const a = i / n * Math.PI * 2;
        x.save(); x.rotate(a); x.translate(ring, 0); x.rotate(-a - t * .0012);
        x.globalAlpha = .55 + .35 * Math.sin(t * .03 + i * 1.3);
        x.drawImage(starTile, -sz / 2, -sz / 2); x.restore();
      }
      x.restore(); x.globalAlpha = 1;
    }
    // franjas de bordado en los costados, que suben y bajan lentamente
    if (bandTile) {
      const bh = bandTile.height, off = (t * .35 * dpr) % bh, m = Math.round(W * .03);
      for (let y = -bh + off; y < H; y += bh) x.drawImage(bandTile, m, y);
      for (let y = -off; y < H; y += bh) x.drawImage(bandTile, W - m - bandW, y);
    }
  }
