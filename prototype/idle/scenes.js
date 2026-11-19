// Cenários de cada imóvel, desenhados em pixel art no canvas (320x180, chão começa em y=66).
// Cada cenário tem: fundo estático (em cache), animação opcional e iluminação opcional (escuridão
// com focos de luz em faixas, sem degradê suave).
(function (root) {
  "use strict";
  const W = 320, H = 180, F = 66;
  const C = {
    ol: "#1a1420", wh: "#fffbef",
    w0: "#3b1f2b", w1: "#5e2f2e", w2: "#8a4a33", w3: "#b5703f", w4: "#d99a5b", w5: "#f0c487",
    b0: "#401a2c", b1: "#6e2834", b2: "#a3423a", b3: "#cc6748", b4: "#e99568",
    s0: "#272436", s1: "#403d54", s2: "#646379", s3: "#8f90a2", s4: "#bfbfc8", s5: "#ebe9e1",
    d0: "#1b1f45", d1: "#283c74", d2: "#3a5ea3", d3: "#6590cc", d4: "#a6cbeb",
    g0: "#5a2f1f", g1: "#94592a", g2: "#d1952e", g3: "#f0c94f", g4: "#fff0a6",
    c0: "#3d0f2e", c1: "#6e1b3d", c2: "#a62e4a", c3: "#d95463", c4: "#f2918a",
    l0: "#14292b", l1: "#1d4537", l2: "#2c6a40", l3: "#4a8f40", l4: "#7cb342", l5: "#bcd95e",
    o0: "#2b1a24", o1: "#47292b", o2: "#6b4234", o3: "#8f6040",
    p0: "#1f1630", p1: "#352450", p2: "#56397a", p3: "#8160a8",
    t0: "#132b38", t1: "#1b4a55", t2: "#2a7470", t3: "#48a38a", t4: "#8fd4a8",
    e1: "#bba57e", e2: "#dccaa3", e3: "#efe3c8",
  };

  function rng(seed) {
    let x = seed | 0 || 1;
    return () => { x ^= x << 13; x ^= x >>> 17; x ^= x << 5; return ((x >>> 0) % 100000) / 100000; };
  }
  function tools(g) {
    const R = (x, y, w, h, c) => { g.fillStyle = c; g.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); };
    const O = (x, y, w, h, c, o = C.ol) => { R(x, y, w, h, o); R(x + 1, y + 1, w - 2, h - 2, c); };
    const P = (x, y, c) => R(x, y, 1, 1, c);
    const ell = (cx, cy, rx, ry, c) => {
      g.fillStyle = c;
      for (let y = -ry; y <= ry; y++) {
        const w = Math.round(rx * Math.sqrt(Math.max(0, 1 - (y * y) / (ry * ry))));
        g.fillRect(Math.round(cx - w), Math.round(cy + y), 2 * w + 1, 1);
      }
    };
    const bands = (x, y, w, h, cols) => { for (let i = 0; i < h; i++) R(x, y + i, w, 1, cols[Math.min(cols.length - 1, Math.floor((i / h) * cols.length))]); };
    const line = (x0, y0, x1, y1, c) => {
      const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0), 1);
      for (let i = 0; i <= n; i++) P(x0 + ((x1 - x0) * i) / n, y0 + ((y1 - y0) * i) / n, c);
    };
    return { R, O, P, ell, bands, line };
  }
  const T = (g) => tools(g);

  // ------------------------------------------------------------ peças comuns
  function floorPlanks(g, c1, c2, c3, seed = 1) {
    const { R } = T(g); const r = rng(seed);
    R(0, F, W, H - F, c1);
    for (let y = F; y < H; y += 10) {
      R(0, y, W, 1, c3);
      const off = (y / 10) % 2 ? 0 : 24;
      for (let x = off; x < W; x += 48) R(x, y, 1, 10, c3);
      for (let i = 0; i < 6; i++) R(r() * W, y + 3 + r() * 5, 6 + r() * 10, 1, c2);
    }
  }
  function floorConcrete(g, base, dark, light, seed = 2) {
    const { R, P } = T(g); const r = rng(seed);
    R(0, F, W, H - F, base);
    for (let i = 0; i < 260; i++) P(r() * W, F + r() * (H - F), r() < 0.6 ? dark : light);
    for (let y = F + 38; y < H; y += 48) R(0, y, W, 1, dark);
    for (let x = 80; x < W; x += 106) R(x, F + 4, 1, H - F, dark);
  }
  function baseboard(g, c = C.s1, top = C.s2) {
    const { R } = T(g);
    R(0, F - 5, W, 5, c); R(0, F - 5, W, 1, top); R(0, F - 1, W, 1, C.ol);
    for (let y = F; y < F + 4; y++) R(0, y, W, 1, "rgba(26,20,32," + (0.35 - (y - F) * 0.08) + ")");
  }
  function windowFrame(g, x, y, w, h, frame = C.w2, inner = null) {
    const { R, O } = T(g);
    O(x - 2, y - 2, w + 4, h + 4, frame);
    if (inner) inner(x, y, w, h);
    R(x + Math.floor(w / 2), y, 2, h, frame);
    R(x, y + Math.floor(h / 2), w, 2, frame);
    R(x - 4, y + h + 2, w + 8, 3, frame); R(x - 4, y + h + 5, w + 8, 1, C.ol);
  }
  function skyView(g, x, y, w, h) {
    const { R } = T(g);
    R(x, y, w, h, C.d4); R(x, y + Math.floor(h * 0.55), w, Math.ceil(h * 0.45), C.d3);
    for (let i = 0; i < 4; i++) R(x + 3 + i * 3, y + 2 + i * 3, 4, 1, C.wh);
  }

  // ------------------------------------------------------------ 0 Quartinho dos fundos
  function quartinho(g) {
    const { R, O, P, ell } = T(g);
    R(0, 0, W, F, C.e2);
    for (let x = 0; x < W; x += 10) R(x, 0, 4, F, C.e3);
    R(0, 0, W, 2, C.e1);
    // mancha de umidade
    ell(42, 10, 14, 6, "rgba(143,96,64,.25)");
    floorPlanks(g, C.w3, C.w2, C.w1, 7);
    baseboard(g, C.w2, C.w3);
    // janela com cortina
    windowFrame(g, 236, 10, 52, 34, C.w2, (x, y, w, h) => skyView(g, x, y, w, h));
    R(230, 6, 64, 3, C.s2);
    R(230, 8, 10, 44, C.c2); R(232, 8, 2, 44, C.c3); R(284, 8, 10, 44, C.c2); R(290, 8, 2, 44, C.c1);
    // pôster torto
    g.save(); g.translate(150, 28); g.rotate(-0.08);
    O(-14, -18, 28, 36, C.p2); R(-11, -15, 22, 16, C.c3); ell(0, -7, 6, 6, C.g3); R(-10, 6, 20, 2, C.wh); R(-10, 10, 14, 2, C.wh);
    g.restore();
    // cama (cabeceira na parede e colchão no chão)
    O(4, 34, 74, 30, C.w2); R(6, 36, 70, 4, C.w3);
    O(4, 60, 76, 52, C.w1);
    R(6, 62, 72, 46, C.s5);
    R(8, 64, 26, 12, C.wh); R(8, 74, 26, 2, C.s4);           // travesseiro
    R(6, 78, 72, 30, C.d2); R(6, 78, 72, 3, C.d3);            // edredom
    for (let i = 0; i < 5; i++) R(10 + i * 14, 84 + (i % 2) * 6, 8, 2, C.d1); // dobras
    R(50, 74, 28, 10, C.d3); R(52, 76, 24, 2, C.d4);          // edredom chutado
    R(4, 112, 4, 6, C.ol); R(76, 112, 4, 6, C.ol);
    // criado-mudo + abajur + latinhas
    O(84, 52, 20, 22, C.w3); R(86, 60, 16, 1, C.w2); P(93, 66, C.g3);
    R(91, 40, 2, 12, C.s2); O(86, 34, 12, 8, C.g3); R(88, 36, 8, 2, C.g4);
    O(100, 47, 5, 6, C.c3); O(105, 48, 5, 6, C.l4);
    // bagunça no chão
    const clothes = [[96, 132, C.c2], [108, 136, C.l3], [100, 140, C.d2], [116, 130, C.s4], [88, 138, C.g2]];
    for (const [x, y, c] of clothes) { ell(x, y, 8, 4, C.ol); ell(x, y, 7, 3, c); }
    O(262, 150, 30, 16, C.w4); R(264, 152, 26, 3, C.w5); R(270, 158, 14, 3, C.c3); // caixa de pizza
    P(276, 156, C.c3); P(281, 155, C.g3);
    O(250, 130, 8, 4, C.s5); O(236, 166, 9, 4, C.c3);         // meias
    O(296, 120, 14, 8, C.s1); R(298, 122, 3, 3, C.c3); R(305, 122, 3, 3, C.d3); // controle de videogame
    O(16, 150, 22, 6, C.wh); R(18, 152, 18, 2, C.s4);         // papel
  }

  // ------------------------------------------------------------ 1 Armário Grow
  function armario(g) {
    const { R, O, P, line } = T(g); const r = rng(11);
    // papel alumínio amassado
    R(0, 0, W, H, C.s3);
    for (let i = 0; i < 900; i++) { const x = r() * W, y = r() * H; R(x, y, 2 + r() * 4, 1, r() < 0.5 ? C.s4 : C.s2); if (r() < 0.2) P(x, y, C.s5); }
    // paredes laterais em perspectiva
    g.fillStyle = "rgba(26,20,32,.35)";
    g.beginPath(); g.moveTo(0, 0); g.lineTo(46, 12); g.lineTo(46, H); g.lineTo(0, H); g.fill();
    g.beginPath(); g.moveTo(W, 0); g.lineTo(W - 46, 12); g.lineTo(W - 46, H); g.lineTo(W, H); g.fill();
    line(46, 12, 46, H, C.s2); line(W - 46, 12, W - 46, H, C.s2);
    // chão de madeira escura
    R(46, F + 20, W - 92, H - F - 20, C.w1);
    for (let y = F + 26; y < H; y += 8) R(46, y, W - 92, 1, C.w0);
    // varão e roupas penduradas
    R(0, 6, W, 3, C.s2); R(0, 6, W, 1, C.s4);
    const hang = [[6, C.c2], [18, C.d2], [30, C.l2], [280, C.g2], [292, C.c1], [304, C.p2]];
    for (const [x, c] of hang) {
      line(x + 5, 8, x + 5, 12, C.s1); line(x + 1, 13, x + 9, 13, C.s1);
      O(x, 13, 11, 34, c); R(x + 2, 15, 2, 30, "rgba(255,255,255,.15)");
    }
    // sapatos
    O(60, 166, 14, 8, C.ol); O(78, 166, 14, 8, C.c2); O(232, 164, 16, 8, C.d1);
    // cabo e refletor da luz de cultivo
    R(159, 0, 2, 14, C.ol);
    O(124, 14, 72, 8, C.s2); R(128, 20, 64, 3, C.p3);
  }

  // ------------------------------------------------------------ 2 Garagem do Vizinho
  function garagem(g) {
    const { R, O, P, ell } = T(g);
    R(0, 0, W, F, C.s3);
    for (let y = 0; y < F; y += 10) {
      R(0, y + 9, W, 1, C.s2);
      for (let x = (y / 10) % 2 ? 0 : 15; x < W; x += 30) R(x, y, 1, 9, C.s2);
    }
    floorConcrete(g, C.s3, C.s2, C.s4, 21);
    baseboard(g);
    // portão de garagem ondulado
    O(214, 2, 104, F - 2, C.s4);
    for (let y = 4; y < F - 2; y += 4) { R(215, y, 102, 1, C.s2); R(215, y + 1, 102, 1, C.s5); }
    R(260, 50, 12, 3, C.s1);
    // painel de ferramentas
    O(116, 8, 80, 36, C.w4);
    for (let x = 120; x < 194; x += 6) for (let y = 12; y < 42; y += 6) P(x, y, C.w2);
    R(124, 14, 3, 20, C.s2); O(121, 12, 9, 5, C.s2);            // martelo
    R(142, 16, 2, 18, C.s4); ell(143, 15, 3, 3, C.s4);          // chave
    O(156, 14, 10, 18, C.c3); R(158, 26, 6, 6, C.s1);           // furadeira
    R(176, 14, 2, 22, C.g2); R(182, 14, 2, 22, C.s3); R(188, 14, 2, 22, C.w2);
    // mancha de óleo
    ell(150, 160, 30, 8, "rgba(39,36,54,.55)"); ell(150, 160, 18, 5, "rgba(39,36,54,.5)");
    // pneus empilhados
    for (let i = 0; i < 3; i++) { ell(298, 150 - i * 9, 16, 6, C.ol); ell(298, 150 - i * 9, 14, 5, C.s1); ell(298, 150 - i * 9, 6, 2, C.s0); }
    // CARRO (vermelho, de lado, virado para a direita)
    const cx = 2, cy = 70;
    ell(cx + 52, cy + 56, 54, 5, "rgba(26,20,32,.45)");
    O(cx + 22, cy, 56, 22, C.c3);                                // cabine
    R(cx + 26, cy + 4, 22, 14, C.d3); R(cx + 52, cy + 4, 22, 14, C.d3);
    R(cx + 26, cy + 4, 22, 3, C.d4); R(cx + 52, cy + 4, 22, 3, C.d4);
    R(cx + 49, cy + 2, 3, 20, C.c2);
    O(cx, cy + 20, 104, 28, C.c3);                               // carroceria
    R(cx + 2, cy + 22, 100, 4, C.c4); R(cx + 2, cy + 40, 100, 6, C.c2);
    R(cx + 50, cy + 28, 1, 14, C.c1); R(cx + 40, cy + 30, 6, 2, C.s4);
    O(cx + 96, cy + 26, 7, 6, C.g3); O(cx + 1, cy + 26, 5, 6, C.c4);   // farol e lanterna
    R(cx, cy + 42, 104, 3, C.s2);                                // para-choque
    for (const wx of [cx + 22, cx + 80]) { ell(wx, cy + 48, 10, 10, C.ol); ell(wx, cy + 48, 8, 8, C.s1); ell(wx, cy + 48, 4, 4, C.s3); }
  }

  // ------------------------------------------------------------ 3 Porão Abandonado
  function porao(g) {
    const { R, O, P, ell, line } = T(g); const r = rng(31);
    R(0, 0, W, F, C.s1);
    for (let y = 0; y < F; y += 11) for (let x = (y / 11) % 2 ? -8 : 0; x < W; x += 16 + Math.floor(r() * 6)) {
      R(x + 1, y + 1, 14, 9, r() < 0.3 ? C.s2 : C.s1); R(x, y + 10, 16, 1, C.s0); R(x + 15, y, 1, 10, C.s0);
    }
    for (let i = 0; i < 40; i++) P(r() * W, r() * F, C.l1);           // musgo
    floorConcrete(g, C.s1, C.s0, C.s2, 33);
    baseboard(g, C.s0, C.s1);
    // canos no teto
    R(0, 4, W, 6, C.s2); R(0, 4, W, 1, C.s3); R(0, 9, W, 1, C.s0);
    for (let x = 30; x < W; x += 70) O(x, 2, 6, 10, C.g1);
    R(88, 9, 6, 50, C.s2); R(88, 9, 1, 50, C.s3); O(85, 56, 12, 6, C.g1);
    // caldeira enferrujada
    O(262, 14, 50, 62, C.g1); R(264, 16, 8, 58, C.g2); R(300, 16, 10, 58, C.g0);
    ell(287, 40, 10, 10, C.ol); ell(287, 40, 8, 8, C.s1); R(286, 33, 2, 6, C.c3);
    for (let i = 0; i < 6; i++) P(266 + r() * 40, 20 + r() * 50, C.o2);
    // poça
    ell(214, 162, 28, 6, C.d1); ell(214, 162, 22, 4, C.d2); R(200, 160, 8, 1, C.d3);
    ell(96, 150, 12, 3, C.d1);
    // teias
    for (const [x, sx] of [[0, 1], [W - 1, -1]]) { for (let i = 0; i < 16; i++) P(x + sx * i, 12 + i, C.s4); for (let i = 0; i < 12; i++) P(x + sx * i, 22 - i * 0.2, C.s4); }
    // caixas velhas
    O(14, 120, 30, 24, C.w2); R(16, 122, 26, 3, C.w3); line(16, 126, 42, 142, C.w1);
    O(20, 104, 22, 18, C.w3); R(22, 106, 18, 2, C.w4);
    // fio da lâmpada
    R(159, 10, 1, 16, C.ol);
  }

  // ------------------------------------------------------------ 4 Terreno Abandonado
  function terreno(g) {
    const { R, O, P, ell, bands } = T(g); const r = rng(41);
    bands(0, 0, W, 34, [C.d4, C.d4, C.d3]);
    // prédios ao longe
    for (let x = 0; x < W; x += 26 + Math.floor(r() * 12)) {
      const h = 12 + Math.floor(r() * 18); R(x, 34 - h, 22, h + 6, C.s3);
      for (let wy = 36 - h; wy < 36; wy += 5) for (let wx = x + 3; wx < x + 20; wx += 5) if (r() < 0.6) R(wx, wy, 2, 2, C.s4);
    }
    // muro de tábuas com pichação
    R(0, 32, W, F - 32, C.w3);
    for (let x = 0; x < W; x += 12) { R(x, 32, 1, F - 32, C.w1); R(x + 1, 32, 2, F - 32, C.w4); }
    for (let x = 0; x < W; x += 12) { R(x + 3, 30, 6, 3, C.w3); P(x + 5, 29, C.w3); }
    const tag = [[120, 40, C.c3], [128, 44, C.c3], [136, 40, C.d3], [144, 42, C.l4], [152, 46, C.g3]];
    for (const [x, y, c] of tag) { ell(x, y, 6, 5, c); ell(x, y, 3, 2, C.w3); }
    R(118, 52, 40, 2, C.p3);
    // chão de terra e mato
    R(0, F, W, H - F, C.o3);
    for (let i = 0; i < 300; i++) P(r() * W, F + r() * (H - F), r() < 0.5 ? C.o2 : C.w4);
    for (let i = 0; i < 26; i++) {
      const x = r() * W, y = F + 6 + r() * (H - F - 10);
      for (let k = 0; k < 5; k++) R(x + k * 2, y - (k % 2 ? 4 : 2), 1, k % 2 ? 4 : 2, k % 3 ? C.l3 : C.l4);
    }
    // árvore
    R(14, 18, 8, 60, C.w1); R(16, 18, 2, 60, C.w2);
    for (const [x, y, rr] of [[18, 14, 16], [6, 22, 10], [32, 20, 12]]) { ell(x, y, rr + 1, rr, C.ol); ell(x, y, rr, rr - 1, C.l3); ell(x - 3, y - 3, rr - 5, rr - 6, C.l4); }
    // pneu, tijolos e TV quebrada
    ell(286, 150, 14, 6, C.ol); ell(286, 150, 12, 5, C.s1); ell(286, 150, 5, 2, C.o2);
    for (let i = 0; i < 4; i++) O(250 + i * 9, 166 - (i % 2) * 4, 9, 5, C.b2);
    O(52, 140, 26, 20, C.s2); R(55, 143, 20, 13, C.s0); R(58, 146, 6, 1, C.s3);
  }

  // ------------------------------------------------------------ 5 Container Marítimo
  function container(g) {
    const { R, O, P } = T(g);
    R(0, 0, W, F, C.b3);
    for (let x = 0; x < W; x += 8) { R(x, 0, 3, F, C.b2); R(x + 3, 0, 1, F, C.b4); }
    R(0, 0, W, 4, C.b1);
    // letreiro em estêncil
    O(110, 20, 100, 22, C.b3, C.b1);
    const txt = "GRN 0451";
    g.fillStyle = C.s5; g.font = "bold 12px monospace"; g.fillText(txt, 124, 36);
    // barras de travamento da porta (lado direito)
    for (const x of [262, 290]) { R(x, 0, 5, F, C.s2); R(x, 0, 1, F, C.s4); O(x - 3, 30, 11, 8, C.s2); }
    // fita de LED
    R(0, 6, W, 2, C.t4);
    // piso de compensado
    R(0, F, W, H - F, C.w3);
    for (let y = F; y < H; y += 16) R(0, y, W, 1, C.w2);
    for (let x = 0; x < W; x += 64) R(x, F, 1, H - F, C.w2);
    baseboard(g, C.b1, C.b2);
    // paletes e fardos
    O(10, 132, 52, 8, C.w4); R(12, 134, 48, 1, C.w2); O(10, 116, 52, 18, C.s4); R(12, 118, 48, 2, C.s5);
    for (let i = 0; i < 4; i++) P(16 + i * 12, 126, C.s2);
    O(264, 140, 44, 30, C.g2); R(266, 142, 40, 3, C.g3); R(270, 150, 30, 2, C.g1);
  }

  // ------------------------------------------------------------ 6 Sobrado na Favela
  function sobrado(g) {
    const { R, O, P, ell } = T(g); const r = rng(61);
    // tijolo aparente
    R(0, 0, W, F, C.b3);
    for (let y = 0; y < F; y += 6) { R(0, y + 5, W, 1, C.b1); for (let x = (y / 6) % 2 ? 0 : 6; x < W; x += 12) R(x, y, 1, 5, C.b1); }
    for (let i = 0; i < 30; i++) R(r() * W, r() * F, 10, 5, C.b2);
    // janela com a vista do morro
    windowFrame(g, 186, 8, 92, 44, C.s2, (x, y, w, h) => {
      R(x, y, w, h, C.d4);
      R(x, y + 16, w, h - 16, C.l3);
      const cols = [C.c3, C.g3, C.d3, C.l5, C.b4, C.s5, C.c4, C.t3];
      for (let row = 0; row < 4; row++) for (let i = 0; i < 9; i++) {
        const bx = x + i * 10 + (row % 2) * 5, by = y + 14 + row * 8;
        if (bx + 8 > x + w) continue;
        O(bx, by, 9, 8, cols[(i + row * 3) % cols.length]); P(bx + 3, by + 3, C.ol);
      }
      ell(x + w - 12, y + 6, 4, 4, C.g4);
    });
    // ventilador de teto
    R(100, 0, 2, 8, C.s1); O(80, 8, 42, 3, C.w2); ell(101, 9, 4, 3, C.s2);
    floorConcrete(g, C.s4, C.s3, C.s5, 63);
    for (let y = F + 12; y < H; y += 22) for (let x = 0; x < W; x += 22) R(x, y, 22, 1, C.s3);
    baseboard(g, C.b1, C.b2);
    // sofá verde
    O(4, 52, 66, 20, C.l2); R(6, 54, 62, 4, C.l3);
    O(4, 70, 68, 30, C.l3); R(6, 72, 64, 4, C.l4); R(36, 74, 1, 24, C.l1);
    O(0, 64, 8, 36, C.l2); O(66, 64, 8, 36, C.l2);
    O(16, 76, 14, 10, C.c3); // almofada
    // TV no caixote
    O(276, 108, 36, 24, C.w3); R(278, 110, 32, 3, C.w4);
    O(274, 82, 40, 28, C.s1); R(277, 85, 34, 20, C.t1); R(279, 87, 10, 2, C.t3);
  }

  // ------------------------------------------------------------ 7 Galpão Industrial
  function galpao(g) {
    const { R, O, line } = T(g);
    R(0, 0, W, F, C.s2);
    for (let x = 0; x < W; x += 6) { R(x, 0, 2, F, C.s1); R(x + 2, 0, 1, F, C.s3); }
    for (const x of [30, 140, 250]) windowFrame(g, x, 6, 40, 18, C.s1, (a, b, w, h) => skyView(g, a, b, w, h));
    for (const x of [80, 200]) { R(x, 0, 1, 12, C.ol); O(x - 9, 12, 19, 5, C.s1); R(x - 7, 16, 15, 1, C.g4); }
    floorConcrete(g, C.s3, C.s2, C.s4, 71);
    for (let x = 0; x < W; x++) { R(x, F + 6, 1, 2, Math.floor(x / 8) % 2 ? C.g3 : C.ol); }
    baseboard(g);
    // paletes empilhados
    for (let i = 0; i < 4; i++) { O(6, 150 - i * 7, 48, 7, C.w4); R(8, 152 - i * 7, 44, 1, C.w2); }
    // empilhadeira
    O(268, 118, 36, 30, C.g3); R(270, 120, 32, 4, C.g4); O(276, 96, 24, 24, C.s1, C.ol); R(278, 98, 20, 18, C.d4);
    R(260, 90, 3, 60, C.s1); R(250, 142, 18, 3, C.s1);
    for (const x of [276, 300]) { R(x - 6, 146, 13, 12, C.ol); R(x - 4, 148, 9, 8, C.s1); }
  }

  // ------------------------------------------------------------ 8 Sítio na Serra
  function sitio(g) {
    const { R, O, P, ell } = T(g);
    // parede de troncos
    for (let y = 0; y < F; y += 8) { R(0, y, W, 8, C.w3); R(0, y, W, 2, C.w4); R(0, y + 7, W, 1, C.w1); }
    for (let y = 0; y < F; y += 8) for (const x of [0, W - 6]) { ell(x + 3, y + 4, 4, 3, C.w4); ell(x + 3, y + 4, 2, 1, C.w2); }
    // janela com montanhas
    windowFrame(g, 110, 8, 80, 38, C.w1, (x, y, w, h) => {
      R(x, y, w, h, C.d4);
      g.fillStyle = C.s3; g.beginPath(); g.moveTo(x, y + h); g.lineTo(x + 22, y + 8); g.lineTo(x + 40, y + h); g.fill();
      g.fillStyle = C.s2; g.beginPath(); g.moveTo(x + 28, y + h); g.lineTo(x + 56, y + 4); g.lineTo(x + w, y + h); g.fill();
      R(x + 52, y + 4, 8, 3, C.wh);
      R(x, y + h - 10, w, 10, C.l3); R(x, y + h - 10, w, 2, C.l4);
    });
    // lareira de pedra
    O(244, 4, 72, F + 4, C.s3);
    for (let y = 6; y < F + 6; y += 7) for (let x = 246 + ((y / 7) % 2) * 5; x < 314; x += 11) { R(x, y, 10, 6, C.s4); R(x, y + 6, 10, 1, C.s2); }
    O(258, 34, 44, 34, C.s0);
    R(254, 30, 52, 4, C.w2);
    floorPlanks(g, C.w4, C.w3, C.w2, 81);
    baseboard(g, C.w1, C.w2);
    // tapete e lenha
    ell(80, 150, 50, 16, C.c1); ell(80, 150, 46, 14, C.c2); ell(80, 150, 30, 8, C.c3);
    for (let i = 0; i < 4; i++) { O(252 + (i % 2) * 6, 86 - Math.floor(i / 2) * 6 + 0, 30, 6, C.w2); ell(253 + (i % 2) * 6, 89 - Math.floor(i / 2) * 6, 2, 2, C.w4); }
  }

  // ------------------------------------------------------------ 9 Fazenda Paraíso Verde (estufa)
  function fazenda(g) {
    const { R, O, ell } = T(g);
    // vidro da estufa mostrando céu, campo e celeiro
    R(0, 0, W, F, C.d4);
    R(0, 34, W, F - 34, C.l3);
    for (let y = 36; y < F; y += 4) R(0, y, W, 1, C.l4);
    O(220, 18, 40, 22, C.c2); g.fillStyle = C.c1; g.beginPath(); g.moveTo(216, 20); g.lineTo(240, 6); g.lineTo(264, 20); g.fill();
    R(234, 28, 12, 12, C.wh); R(239, 28, 2, 12, C.c2);
    ell(40, 12, 8, 8, C.g4);
    for (let x = 0; x < W; x += 40) R(x, 0, 3, F, C.s5);
    for (let y = 0; y < F; y += 22) R(0, y, W, 2, C.s5);
    R(0, 0, W, F, "rgba(255,255,255,.08)");
    // chão de terra com canteiros
    R(0, F, W, H - F, C.o2);
    for (let y = F + 8; y < H; y += 18) { R(0, y, W, 6, C.o3); R(0, y, W, 1, C.o1); }
    baseboard(g, C.s4, C.s5);
    // mangueira enrolada e regador
    for (let i = 0; i < 3; i++) { ell(296, 154, 14 - i * 3, 6 - i, C.l1); ell(296, 154, 12 - i * 3, 5 - i, C.l3); }
    O(14, 146, 22, 16, C.g2); R(36, 150, 8, 3, C.g2);
  }

  // ------------------------------------------------------------ 10 Ilha Privada
  function ilha(g) {
    const { R, O, ell, bands } = T(g); const r = rng(101);
    bands(0, 0, W, 34, [C.d4, C.d4, C.d3]);
    ell(270, 14, 10, 10, C.g4); ell(270, 14, 8, 8, C.wh);
    R(0, 32, W, 26, C.t2); R(0, 32, W, 2, C.t3);
    // areia
    R(0, 56, W, H - 56, C.w5);
    for (let i = 0; i < 260; i++) R(r() * W, 60 + r() * (H - 60), 1, 1, r() < 0.5 ? C.w4 : C.e3);
    // coqueiros
    for (const [x, flip] of [[18, 1], [302, -1]]) {
      for (let i = 0; i < 60; i++) R(x + flip * Math.round(Math.sin(i / 20) * 6), 120 - i, 6, 2, i % 6 < 3 ? C.w2 : C.w3);
      const tx = x + flip * 6, ty = 60;
      for (const [dx, dy] of [[-22, 8], [22, 8], [-14, -6], [14, -6], [0, -12]]) {
        g.fillStyle = C.l2; g.beginPath(); g.moveTo(tx + 3, ty); g.lineTo(tx + 3 + dx, ty + dy - 3); g.lineTo(tx + 3 + dx, ty + dy + 3); g.fill();
      }
      ell(tx + 3, ty + 4, 3, 3, C.w1); ell(tx + 7, ty + 5, 3, 3, C.w1);
    }
    // rede entre os coqueiros (de longe) e cadeira de praia
    O(260, 140, 30, 6, C.c3); R(262, 146, 2, 10, C.w2); R(286, 146, 2, 10, C.w2);
    O(40, 150, 26, 14, C.d3); R(42, 152, 22, 2, C.wh);
  }

  // ------------------------------------------------------------ 11 Mina de Ouro Desativada
  function mina(g) {
    const { R, O, P, ell } = T(g); const r = rng(111);
    R(0, 0, W, H, C.o1);
    for (let i = 0; i < 120; i++) { const x = r() * W, y = r() * F; ell(x, y, 6 + r() * 12, 3 + r() * 6, r() < 0.5 ? C.o2 : C.o0); }
    for (let i = 0; i < 26; i++) { const x = r() * W, y = 4 + r() * (F - 8); P(x, y, C.g3); P(x + 1, y, C.g2); }
    // escoras de madeira
    for (const x of [40, 270]) { O(x, 0, 10, F + 10, C.w2); R(x + 2, 0, 2, F + 10, C.w3); }
    O(30, 4, 260, 10, C.w2); R(32, 6, 256, 2, C.w3);
    // chão rochoso com trilhos
    R(0, F, W, H - F, C.o2);
    for (let i = 0; i < 200; i++) P(r() * W, F + r() * (H - F), r() < 0.5 ? C.o1 : C.o3);
    for (let x = 0; x < W; x += 10) R(x, 150, 6, 14, C.w1);
    R(0, 152, W, 2, C.s3); R(0, 160, W, 2, C.s3);
    // carrinho de mina
    O(10, 128, 46, 22, C.s2); R(12, 130, 42, 4, C.s3);
    for (let i = 0; i < 6; i++) ell(18 + i * 6, 128, 4, 3, C.g2);
    for (const wx of [20, 46]) { ell(wx, 152, 5, 5, C.ol); ell(wx, 152, 3, 3, C.s2); }
    // lampiões (a chama é animada)
    for (const x of [62, 254]) { R(x, 14, 1, 10, C.ol); O(x - 4, 24, 9, 12, C.s1); }
  }

  // ------------------------------------------------------------ 12 Bunker Militar
  function bunker(g) {
    const { R, O, P, ell } = T(g);
    R(0, 0, W, F, C.s1);
    for (let x = 0; x < W; x += 32) R(x, 0, 1, F, C.s0);
    for (let y = 0; y < F; y += 16) R(0, y, W, 1, C.s0);
    for (let x = 4; x < W; x += 32) for (let y = 4; y < F; y += 16) P(x, y, C.s2);
    // porta blindada redonda
    ell(48, 38, 28, 28, C.ol); ell(48, 38, 26, 26, C.s3); ell(48, 38, 20, 20, C.s2); ell(48, 38, 6, 6, C.g2);
    for (let a = 0; a < 6; a++) { const x = 48 + Math.cos(a) * 14, y = 38 + Math.sin(a) * 14; R(x - 1, y - 1, 3, 3, C.s4); }
    // faixa de perigo
    for (let x = 0; x < W; x++) R(x, F - 8, 1, 4, Math.floor((x + 0) / 6) % 2 ? C.g3 : C.ol);
    // monitores
    for (const [x, y] of [[180, 10], [216, 10], [252, 10]]) { O(x, y, 32, 22, C.s0); R(x + 2, y + 2, 28, 18, C.t1); for (let k = 0; k < 4; k++) R(x + 4, y + 5 + k * 4, 10 + ((x + k * 7) % 14), 1, C.t4); }
    floorConcrete(g, C.s2, C.s1, C.s3, 121);
    baseboard(g, C.s0, C.s1);
    // sacos de areia
    for (let row = 0; row < 3; row++) for (let i = 0; i < 3 - row; i++) { const x = 262 + i * 18 + row * 9, y = 158 - row * 9; ell(x, y, 10, 5, C.ol); ell(x, y, 9, 4, C.w4); R(x - 6, y, 12, 1, C.w3); }
    // sirene
    O(150, 2, 12, 8, C.s2);
  }

  // ------------------------------------------------------------ 13 Estação Espacial
  function estacao(g) {
    const { R, O, P, ell } = T(g); const r = rng(131);
    R(0, 0, W, F, C.s2);
    for (let x = 0; x < W; x += 40) { R(x, 0, 2, F, C.s1); R(x + 2, 0, 1, F, C.s3); }
    // janelão com espaço
    O(70, 4, 180, 52, C.s1);
    R(74, 8, 172, 44, C.p0);
    for (let i = 0; i < 70; i++) P(74 + r() * 172, 8 + r() * 44, r() < 0.7 ? C.s4 : C.wh);
    g.save(); g.beginPath(); g.rect(74, 8, 172, 44); g.clip();
    ell(210, 82, 70, 50, C.d2); ell(200, 76, 60, 40, C.d3);
    for (let i = 0; i < 9; i++) ell(170 + r() * 70, 40 + r() * 20, 8 + r() * 10, 3 + r() * 3, C.l4);
    ell(200, 82, 72, 52, "rgba(166,203,234,.0)");
    g.restore();
    R(158, 4, 4, 52, C.s1);
    // faixas de luz
    R(0, F - 10, W, 2, C.t4); R(0, 2, W, 1, C.t3);
    // piso de metal com grade
    R(0, F, W, H - F, C.s1);
    for (let y = F; y < H; y += 14) R(0, y, W, 1, C.s0);
    for (let x = 0; x < W; x += 14) R(x, F, 1, H - F, C.s0);
    for (let y = F + 7; y < H; y += 14) for (let x = 7; x < W; x += 14) P(x, y, C.s3);
    baseboard(g, C.s0, C.t2);
    // painéis
    O(8, 20, 50, 30, C.s0); for (let k = 0; k < 5; k++) R(12, 24 + k * 5, 8 + (k * 9) % 30, 2, k % 2 ? C.t4 : C.c3);
    O(262, 20, 50, 30, C.s0); for (let k = 0; k < 4; k++) O(266 + k * 11, 26, 8, 8, k % 2 ? C.t3 : C.g3, C.s1);
  }

  const STATIC = [quartinho, armario, garagem, porao, terreno, container, sobrado, galpao, sitio, fazenda, ilha, mina, bunker, estacao];

  // ------------------------------------------------------------ animações (por quadro)
  const ANIM = {
    1: (g, t) => { const { R } = T(g); if (Math.floor(t * 2) % 7 !== 0) R(128, 22, 64, 2, C.p3); },
    3: (g, t) => { // gotas caindo nos dois pingos
      const { R, ell } = T(g);
      for (const [x, y0, y1, ph] of [[212, 10, 158, 0], [94, 62, 148, 0.45]]) {
        const k = (t * 0.55 + ph) % 1;
        if (k < 0.75) R(x, y0 + (y1 - y0) * (k / 0.75), 1, 3, C.d4);
        else { const s = (k - 0.75) / 0.25; ell(x, y1 + 2, Math.round(3 + s * 8), 1, "rgba(166,203,234," + (0.7 - s * 0.7) + ")"); }
      }
    },
    8: (g, t) => { // fogo da lareira
      const { R } = T(g);
      for (let i = 0; i < 7; i++) {
        const h = 6 + ((Math.sin(t * 9 + i * 1.7) + 1) * 5) | 0;
        R(262 + i * 5, 66 - h, 4, h, i % 2 ? "#d1952e" : "#d95463");
        R(263 + i * 5, 66 - h / 2, 2, h / 2, "#fff0a6");
      }
    },
    10: (g, t) => { // ondas
      const { R } = T(g);
      for (let x = 0; x < W; x += 16) { const o = Math.round(Math.sin(t * 2 + x / 30) * 3); R(x + o + 4, 44 + (x % 32 ? 0 : 6), 8, 1, "#8fd4a8"); }
      R(0, 55 + Math.round(Math.sin(t * 1.5) * 1), W, 2, "#ebe9e1");
    },
    11: (g, t) => { const { R } = T(g); for (const x of [62, 254]) { const f = Math.sin(t * 13 + x) > 0; R(x - 2, 26, 5, 8, f ? "#f0c94f" : "#d1952e"); R(x - 1, 28, 3, 4, "#fff0a6"); } },
    12: (g, t) => { const { R } = T(g); if (Math.floor(t * 2) % 2) R(151, 3, 10, 6, "#d95463"); else R(151, 3, 10, 6, "#6e1b3d"); },
    13: (g, t) => { const { P } = T(g); const r = rng(Math.floor(t * 3)); for (let i = 0; i < 10; i++) P(74 + r() * 172, 8 + r() * 44, "#fffbef"); },
  };

  // ------------------------------------------------------------ iluminação
  const LIGHT = {
    1: { a: 0.35, tint: "53,36,80", lights: [[160, 30, 120]] },
    3: { a: 0.6, tint: "26,20,32", lights: [[160, 30, 115]], flicker: true },
    11: { a: 0.5, tint: "26,20,32", lights: [[62, 34, 80], [254, 34, 80]], flicker: true },
  };

  // ------------------------------------------------------------ cômodos vistos de cima (tools/arte/comodos.py)
  // cada cômodo: fundo iluminado, fundo um degrau mais escuro (sombra) e mapa de luz por pixel
  const ROOM = {}; const STEP = new Map();           // cor -> [um degrau abaixo, um acima] na rampa
  const OL = 0x1a1420;
  const mk = (w, h) => { const c = document.createElement("canvas"); c.width = w; c.height = h; return c; };
  function registerRooms(map, shift) {
    for (const k in shift) STEP.set(parseInt(k.slice(1), 16), shift[k].map((h) => parseInt(h.slice(1), 16)));
    for (const id in map) {
      const m = map[id], r = { meta: m.meta, img: new Image(), sh: new Image(), lm: null, lit: new Map(), raw: new Map(), shadow: null, sig: "" };
      r.img.src = m.src; r.sh.src = m.srcS;
      const li = new Image();
      li.onload = () => {
        const c = mk(li.width, li.height), x = c.getContext("2d"); x.drawImage(li, 0, 0);
        const d = x.getImageData(0, 0, li.width, li.height).data;
        r.lm = new Int8Array(li.width * li.height);
        for (let i = 0; i < r.lm.length; i++) r.lm[i] = Math.round(d[i * 4] / 64) - 2;
      };
      li.src = m.srcL;
      ROOM[id] = r;
    }
  }
  function shiftN(rgb, n) {
    while (n !== 0) { const s = STEP.get(rgb); if (!s) break; rgb = n < 0 ? s[0] : s[1]; n += n < 0 ? 1 : -1; }
    return rgb;
  }
  // sprite cru (vaso + planta) desenhado pelo jogo, guardado por chave
  function rawSprite(r, it) {
    let c = r.raw.get(it.key);
    if (!c) {
      c = mk(it.w, it.h); const x = c.getContext("2d"); x.imageSmoothingEnabled = false; it.paint(x);
      c.data = x.getImageData(0, 0, it.w, it.h);
      r.raw.set(it.key, c);
    }
    return c;
  }
  // o sprite aceso pelo mapa de luz do lugar onde está + luz de borda virada para a lâmpada
  function litSprite(r, it) {
    const k = it.key + "@" + it.x + "," + it.y;
    let c = r.lit.get(k);
    if (c) return c;
    const raw = rawSprite(r, it);
    if (!r.lm || !raw.data) return raw;
    const { w, h } = it, src = raw.data.data, W0 = r.meta.w;
    c = mk(w, h); const x = c.getContext("2d"), out = x.createImageData(w, h), o = out.data;
    const [lx] = r.meta.light, cx = it.x + w / 2, dx = lx > cx + 8 ? 1 : lx < cx - 8 ? -1 : 0;
    const op = (sx, sy) => sx >= 0 && sy >= 0 && sx < w && sy < h && src[(sy * w + sx) * 4 + 3] > 0 &&
      ((src[(sy * w + sx) * 4] << 16) | (src[(sy * w + sx) * 4 + 1] << 8) | src[(sy * w + sx) * 4 + 2]) !== OL;
    for (let sy = 0; sy < h; sy++) for (let sx = 0; sx < w; sx++) {
      const i = (sy * w + sx) * 4;
      if (!src[i + 3]) continue;
      let rgb = (src[i] << 16) | (src[i + 1] << 8) | src[i + 2];
      if (rgb !== OL) {
        const px = it.x + sx, py = it.y + sy;
        let n = px >= 0 && py >= 0 && px < W0 && py < r.meta.h ? r.lm[py * W0 + px] : 0;
        if (!op(sx, sy - 1) || (dx && !op(sx + dx, sy))) n += 1;
        rgb = shiftN(rgb, n);
      }
      o[i] = rgb >> 16; o[i + 1] = (rgb >> 8) & 255; o[i + 2] = rgb & 255; o[i + 3] = 255;
    }
    x.putImageData(out, 0, 0);
    if (r.lit.size > 600) r.lit.clear();
    r.lit.set(k, c);
    return c;
  }
  // sombras projetadas pela luz principal (mesma conta do comodos.py) + sombra de contato, recortadas do fundo escuro
  function shadowLayer(r, items) {
    const sig = items.map((it) => it.key + "@" + it.x + "," + it.y).join("|");
    if (r.shadow && r.sig === sig) return r.shadow;
    const { w: W0, h: H0 } = r.meta, [lx] = r.meta.light;
    const c = r.shadow || mk(W0, H0), x = c.getContext("2d");
    x.globalCompositeOperation = "source-over"; x.clearRect(0, 0, W0, H0);
    const m = x.createImageData(W0, H0), d = m.data;
    const mark = (px, py) => { if (px >= 0 && py >= 0 && px < W0 && py < H0) d[(py * W0 + px) * 4 + 3] = 255; };
    for (const it of items) {
      const raw = rawSprite(r, it); if (!raw.data) continue;
      const src = raw.data.data, ground = it.y + it.h - 1 - (it.foot || 0), cxo = it.x + it.w / 2;
      const kx = Math.max(-0.7, Math.min(0.7, (cxo - lx) / 70)), ky = 0.45;
      for (let sy = 0; sy < it.h; sy++) for (let sx = 0; sx < it.w; sx++) {
        if (!src[(sy * it.w + sx) * 4 + 3]) continue;
        const hh = Math.max(0, ground - (it.y + sy));
        const tx = Math.round(it.x + sx + hh * kx), ty = Math.round(ground + hh * ky);
        mark(tx, ty); mark(tx, ty + 1);
      }
      const bw = it.w * 0.42;
      for (let yy = ground - 1; yy <= ground + 2; yy++) for (let xx = Math.floor(cxo - bw); xx <= cxo + bw; xx++)
        if (((xx - cxo) / bw) ** 2 + ((yy - ground - 0.5) / 2.2) ** 2 <= 1) mark(xx, yy);
    }
    x.putImageData(m, 0, 0);
    x.globalCompositeOperation = "source-in";
    if (r.sh.complete) x.drawImage(r.sh, 0, 0);
    x.globalCompositeOperation = "source-over";
    r.shadow = c; r.sig = sig;
    return c;
  }
  // desenha as plantas do cômodo: sombras primeiro, depois cada vaso aceso, de trás para frente
  function plants(g, id, items) {
    const r = ROOM[id];
    if (!r) { for (const it of items) g.drawImage(rawSprite({ raw: PLAIN }, it), it.x, it.y); return; }
    g.drawImage(shadowLayer(r, items), 0, 0);
    for (const it of items) g.drawImage(litSprite(r, it), it.x, it.y);
  }
  const PLAIN = new Map();
  const roomMeta = (id) => ROOM[id] && ROOM[id].meta;
  // cenários desenhados em PNG (tools/arte/cenarios.py): substituem os desenhados em código
  const PNG = {};
  function register(map) {
    for (const id in map) { const img = new Image(); img.src = map[id].src; PNG[id] = { img, meta: map[id].meta }; }
  }
  function size(id) {
    if (ROOM[id]) return { w: ROOM[id].meta.w, h: ROOM[id].meta.h, floor: ROOM[id].meta.floor };
    const p = PNG[id];
    return p ? { w: p.meta.w, h: p.meta.h, floor: p.meta.floor } : { w: W, h: H, floor: F };
  }

  let darkCanvas = null;
  function lighting(g, id, t) {
    if (ROOM[id]) {                                   // a luz já está pintada no cômodo; só a lâmpada pisca
      const gl = ROOM[id].meta.glow;
      if (gl) { const { ell } = T(g); const [x, y, rx, ry, col] = gl; ell(x, y, rx, ry, col); ell(x, y - 2, Math.round(rx * 0.6), Math.round(ry * 0.6), col); }
      const b = ROOM[id].meta.bulb;
      if (b) { const { R } = T(g); const [bx, by] = b; R(bx - 3, by - 2, 7, 6, "#1a1420"); R(bx - 2, by - 1, 5, 4, Math.sin(t * 23) > 0.93 ? "#d1952e" : "#fff0a6"); R(bx - 1, by, 2, 1, "#fffbef"); }
      return;
    }
    const L = (PNG[id] && PNG[id].meta.dark) || (!PNG[id] && LIGHT[id]);
    if (!L) return;
    const { w: RW, h: RH } = size(id);
    if (!darkCanvas || darkCanvas.width !== RW) { darkCanvas = document.createElement("canvas"); darkCanvas.width = RW; darkCanvas.height = RH; }
    const d = darkCanvas.getContext("2d");
    d.globalCompositeOperation = "source-over";
    d.clearRect(0, 0, RW, RH);
    let a = L.a;
    if (L.flicker && Math.sin(t * 23) > 0.93) a += 0.15;
    d.fillStyle = `rgba(${L.tint},${a})`;
    d.fillRect(0, 0, RW, RH);
    d.globalCompositeOperation = "destination-out";
    for (const [x, y, r] of L.lights) {
      for (const [k, al] of [[1, 0.35], [0.72, 0.5], [0.45, 1]]) {
        d.globalAlpha = al;
        const { ell } = T(d);
        ell(x, y + r * 0.35 * k, Math.round(r * k), Math.round(r * 0.75 * k), "#000");
      }
    }
    d.globalAlpha = 1;
    d.globalCompositeOperation = "source-over";
    g.drawImage(darkCanvas, 0, 0);
    if (PNG[id]) {
      if (L.bulb) { const { R } = T(g); const [bx, by] = L.bulb; R(bx - 4, by - 4, 9, 8, "#1a1420"); R(bx - 3, by - 3, 7, 6, Math.sin(t * 23) > 0.93 ? "#d1952e" : "#fff0a6"); R(bx - 1, by - 2, 2, 2, "#fffbef"); }
      return;
    }
    if (id === 3 || id === 1) { // a lâmpada
      const { R } = T(g);
      R(156, 24, 8, 7, "#1a1420"); R(157, 25, 6, 5, id === 3 ? "#fff0a6" : "#8160a8");
    }
  }

  const cache = {};
  function background(g, id) {
    if (ROOM[id]) {
      const r = ROOM[id];
      if (r.img.complete) g.drawImage(r.img, 0, 0);
      anims(g, r.meta, performance.now() / 1000);
      return;
    }
    const png = PNG[id];
    if (png) {
      if (png.img.complete) g.drawImage(png.img, 0, 0);
      const t = performance.now() / 1000, { R, ell } = T(g);
      for (const [i, [x, y0, y1]] of (png.meta.drips || []).entries()) {   // gotas da goteira
        const k = (t * 0.55 + i * 0.45) % 1;
        if (k < 0.75) R(x, y0 + (y1 - y0) * (k / 0.75), 1, 3, "#a6cbeb");
        else { const sp = (k - 0.75) / 0.25; ell(x, y1 + 2, Math.round(2 + sp * 8), 1, "rgba(166,203,234," + (0.7 - sp * 0.7) + ")"); }
      }
      if (id === 1 && Math.floor(t * 2) % 9 !== 0) R(83, 18, 74, 2, "#8160a8");   // luz roxa do armário
      anims(g, png.meta, t);
      return;
    }
    if (!cache[id]) {
      const c = document.createElement("canvas");
      c.width = W; c.height = H;
      const cg = c.getContext("2d");
      cg.imageSmoothingEnabled = false;
      STATIC[id](cg);
      cache[id] = c;
    }
    g.drawImage(cache[id], 0, 0);
    if (ANIM[id]) ANIM[id](g, performance.now() / 1000);
  }

  function anims(g, meta, t) {
    const { R, ell } = T(g);
      for (const an of meta.anims || []) {
        const [kind, ...a] = an;
        if (kind === "fire") {                       // fogo da lareira: [x, base, largura]
          const [x, y, w] = a;
          for (let i = 0; i < w / 4; i++) {
            const h = 6 + Math.round((Math.sin(t * 9 + i * 1.7) + 1) * 5);
            R(x + i * 4, y - h, 3, h, i % 2 ? "#d1952e" : "#d95463");
            R(x + i * 4 + 1, y - Math.round(h / 2), 1, Math.round(h / 2), "#fff0a6");
          }
        } else if (kind === "waves") {              // brilho do mar entre y0 e y1
          const [y0, y1] = a;
          const rw = meta.room || [0, 0, meta.w];
          for (let x = rw[0]; x < rw[0] + rw[2] - 12; x += 18) {
            const o = Math.round(Math.sin(t * 2 + x / 30) * 3);
            R(x + o + 4, y0 + 4 + ((x / 18) % 3) * 7, 7, 1, "#fffbef");
          }
          const rm = meta.room || [0, 0, meta.w];
          R(rm[0], y1 + Math.round(Math.sin(t * 1.5)), rm[2], 1, "#fffbef");
        } else if (kind === "torch" || kind === "lantern") {
          const [x, y] = a, f = Math.sin(t * 13 + x) > 0;
          R(x - 2, y - 2, 5, 6, f ? "#f0c94f" : "#d1952e"); R(x - 1, y, 3, 3, "#fff0a6");
        } else if (kind === "sparkle") {            // ouro brilhando na rocha
          const [x0, y0, x1, y1] = a, rr = rng(Math.floor(t * 2));
          for (let i = 0; i < 6; i++) { const x = x0 + rr() * (x1 - x0), y = y0 + rr() * (y1 - y0); R(x, y, 1, 1, "#fff0a6"); R(x - 1, y, 3, 1, "#f0c94f"); }
        } else if (kind === "siren") {
          const [x, y] = a, on = Math.floor(t * 2) % 2;
          R(x - 1, y, 14, 9, "#1a1420"); R(x, y + 1, 12, 7, on ? "#d95463" : "#6e1b3d");
          if (on) R(x + 3, y + 2, 4, 2, "#f2918a");
        } else if (kind === "drip") {              // goteira: [x, teto, chão]
          const [x, y0, y1] = a, k = (t * 0.55) % 1;
          if (k < 0.75) R(x, y0 + (y1 - y0) * (k / 0.75), 1, 3, "#a6cbeb");
          else { const sp = (k - 0.75) / 0.25; ell(x, y1 + 2, Math.round(2 + sp * 8), 1, "rgba(166,203,234," + (0.7 - sp * 0.7) + ")"); }
        } else if (kind === "purple") {            // lâmpada roxa piscando: [x, y, largura]
          const [x, y, w] = a;
          if (Math.floor(t * 2) % 9 !== 0) R(x, y, w, 1, "#c79ef0");
        } else if (kind === "stars") {
          const [x0, y0, x1, y1] = a, rr = rng(Math.floor(t * 3));
          for (let i = 0; i < 12; i++) R(x0 + rr() * (x1 - x0), y0 + rr() * (y1 - y0), 1, 1, "#fffbef");
        }
      }
  }

  root.SCENES = { register, registerRooms, plants, roomMeta, size, background, lighting: (g, id) => lighting(g, id, performance.now() / 1000), count: STATIC.length };
})(this);
