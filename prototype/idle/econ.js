// Economia do Greenhood Idle — o GDD inteiro adaptado para jogo idle.
// Funções puras sobre um objeto de estado: roda igual no navegador e no Node (simulação).
(function (root) {
  "use strict";

  // ---------------------------------------------------------------- catálogos
  // Sementes (números do GDD): preço (grana suja, pago a cada plantio), venda por unidade,
  // unidades por colheita, Botânica mínima, equipamentos exigidos e tempo de crescimento (s).
  const SEEDS = [
    ["Alface Mística", 5, 8, 3, 0, [], 30],
    ["Hortelã Selvagem", 10, 15, 3, 0, [], 35],
    ["Manjericão do Olimpo", 20, 30, 4, 1, [], 45],
    ["Tomate Atômico", 50, 80, 4, 2, ["regador"], 55],
    ["Pimenta do Capeta", 120, 200, 3, 3, ["regador", "termometro"], 60],
    ["Cogumelo Saltitante", 300, 500, 5, 4, ["termometro", "ventilador"], 75],
    ["Lavanda Hipnótica", 800, 1200, 4, 5, ["fertilizante", "ventilador"], 90],
    ["Cacto Cabeludo", 2000, 3500, 2, 6, ["ph", "termometro"], 100],
    ["Lótus Azul", 5000, 8000, 3, 7, ["lampada", "ph", "fertilizante"], 120],
    ["Cipó Enrolado", 12000, 25000, 2, 8, ["estufa", "ph", "fertilizante"], 150],
    ["Orquídea Fantasma", 30000, 60000, 2, 10, ["lampada", "estufa", "filtro"], 180],
    ["Trufa Negra", 80000, 150000, 2, 12, ["led", "filtro", "ph"], 210],
    ["Mandrágora", 200000, 450000, 1, 14, ["led", "hidro", "filtro"], 240],
    ["Bonsai Milenar", 500000, 1.2e6, 1, 16, ["hidro", "co2", "led"], 300],
    ["Rafflesia Gigante", 1.5e6, 4e6, 1, 18, ["co2", "osmose", "led", "filtro"], 360],
    ["Aurora Boreal", 5e6, 1.5e7, 1, 20, ["ia", "co2", "osmose", "led"], 420],
    ["Fruto do Éden", 2e7, 6.5e7, 1, 25, ["ia", "bunker", "lab"], 600],
    ["Broto de Yggdrasil", 1e8, 3.5e8, 1, 30, ["lab", "bunker", "ia", "osmose"], 900],
  ].map(([name, price, sell, prod, bot, req, time], id) => ({ id, name, price, sell, prod, bot, req, time, frame: id }));

  // Equipamentos (GDD): preço em grana limpa e bônus de produção. Cada um tem níveis
  // (o 1º libera sementes; os seguintes repetem o bônus) e um efeito extra.
  const EQUIP = [
    ["regador", "Regador de garrafa PET", 100, 0.02, { speed: 0.05 }, "Cresce 5% mais rápido"],
    ["tesoura", "Tesoura enferrujada", 150, 0.02, { tap: 0.5 }, "Toque 50% mais forte"],
    ["ventilador", "Ventilador torto", 300, 0.03, {}, ""],
    ["termometro", "Termômetro na tábua", 500, 0.03, {}, ""],
    ["fertilizante", "Adubo \"El Secreto\"", 1000, 0.04, {}, ""],
    ["lampada", "Lâmpada com alumínio", 2500, 0.05, { speed: 0.1 }, "Cresce 10% mais rápido"],
    ["ph", "Medidor de pH", 5000, 0.04, {}, ""],
    ["estufa", "Mini estufa", 12000, 0.05, { speed: 0.1 }, "Cresce 10% mais rápido"],
    ["drone", "Drone de vigilância", 25000, 0.02, { calm: 0.1 }, "Vendas geram 10% menos Paranoia"],
    ["filtro", "Filtro de carbono", 50000, 0.06, { calm: 0.1 }, "Vendas geram 10% menos Paranoia"],
    ["led", "Painel LED", 120000, 0.08, { speed: 0.15 }, "Cresce 15% mais rápido"],
    ["hidro", "Sistema hidropônico", 300000, 0.1, { speed: 0.15 }, "Cresce 15% mais rápido"],
    ["co2", "Gerador de CO2", 800000, 0.09, { speed: 0.15 }, "Cresce 15% mais rápido"],
    ["cameras", "Câmeras 4K", 1.5e6, 0.03, { guard: 0.1 }, "Batidas levam 10% menos"],
    ["osmose", "Osmose reversa", 4e6, 0.08, {}, ""],
    ["ia", "Controlador IA", 1e7, 0.15, { tap: 1 }, "Toque 100% mais forte"],
    ["bunker", "Kit bunker", 3.5e7, 0.12, { guard: 0.25 }, "Batidas levam 25% menos"],
    ["lab", "Lab. de genética", 1.5e8, 0.2, { speed: 0.25 }, "Cresce 25% mais rápido"],
  ].map(([id, name, price, prod, fx, fxText], i) => ({ id, name, price, prod, fx, fxText, frame: i }));
  const EQUIP_LEVEL_MULT = 2.4; // cada nível extra custa 2,4x o anterior

  // Imóveis (GDD), em grana limpa. tier = visual (0 gambiarra, 1 profissional, 2 high-tech).
  const PLACES = [
    ["Quartinho dos fundos", 0, 2, 0],
    ["Armário Grow", 500, 3, 0],
    ["Garagem do Vizinho", 1500, 4, 0],
    ["Porão Abandonado", 4000, 5, 0],
    ["Terreno Abandonado", 10000, 6, 0],
    ["Container Marítimo", 25000, 8, 1],
    ["Sobrado na Favela", 75000, 10, 1],
    ["Galpão Industrial", 200000, 12, 1],
    ["Sítio na Serra", 500000, 14, 1],
    ["Fazenda Paraíso Verde", 1.5e6, 18, 1],
    ["Ilha Privada", 5e6, 24, 2],
    ["Mina de Ouro Desativada", 2e7, 30, 2],
    ["Bunker Militar", 8e7, 40, 2],
    ["Estação Espacial", 5e8, 60, 2],
  ].map(([name, cost, pots, tier], id) => ({ id, name, cost, pots, tier }));

  // Venda (GDD): quantidade máxima, Paranoia, chance de flagrante e bônus de preço.
  const SALES = [
    { name: "Discreto", max: 5, para: 5, risk: 0, bonus: 0 },
    { name: "Normal", max: 20, para: 15, risk: 0.03, bonus: 0.1 },
    { name: "Ousado", max: 50, para: 25, risk: 0.08, bonus: 0.25 },
    { name: "Agressivo", max: 100, para: 40, risk: 0.15, bonus: 0.5 },
    { name: "All-in", max: Infinity, para: 60, risk: 0.3, bonus: 1 },
  ];

  // Lavagem (GDD): taxa, tempo (s), Paranoia e Lábia mínima.
  const LAUNDRY = [
    { id: "laranjas", name: "Laranjas", fee: 0.2, time: 600, para: 2, lab: 0 },
    { id: "nft", name: "NFTs falsos", fee: 0.35, time: 0, para: 15, lab: 0 },
    { id: "crypto", name: "Mixer de crypto", fee: 0.25, time: 180, para: 8, lab: 5 },
    { id: "consultoria", name: "Consultoria fantasma", fee: 0.15, time: 300, para: 5, lab: 10 },
  ];

  // Cidade (GDD): custo em grana limpa, Estamina gasta, duração (s) e efeitos.
  const CITY = [
    { id: "cafe", name: "Café", cost: 5, sta: 0, time: 60, fx: { sta: 30, para: 15 } },
    { id: "energetico", name: "Energético", cost: 15, sta: 0, time: 120, fx: { sta: 50, para: 30 } },
    { id: "bar", name: "Bar do Zé", cost: 8, sta: 0, time: 180, fx: { sta: 20, para: 5, lab: 1 } },
    { id: "biblioteca", name: "Biblioteca", cost: 3, sta: 10, time: 300, fx: { bot: 1 } },
    { id: "academia", name: "Academia", cost: 12, sta: 20, time: 600, fx: { seg: 1, resp: 1 } },
    { id: "beco", name: "Beco Escuro", cost: 20, sta: 15, time: 600, fx: { fur: 2, para: 20 } },
    { id: "praca", name: "Praça do Papo", cost: 6, sta: 10, time: 300, fx: { lab: 2, resp: 1 } },
    { id: "spa", name: "Spa", cost: 100, sta: 0, time: 900, fx: { para: -50 } },
    { id: "fliperama", name: "Fliperama", cost: 10, sta: 0, time: 300, fx: { para: -20, sta: 5 } },
  ];

  const ATTRS = { bot: "Botânica", lab: "Lábia", fur: "Furtividade", seg: "Segurança" };

  // ---------------------------------------------------------------- regras
  const R = {
    tapSeconds: 0.35, // cada toque adianta 0,35 s de crescimento em todos os vasos
    paraDecay: 1 / 4, // Paranoia cai 1 a cada 4 s
    loanPara: 3 / 60, // dívida com o agiota: +3 por minuto
    staRegen: 1 / 20, // Estamina: +1 a cada 20 s
    raidEvery: 300, raidAt: 80, raidChance: 0.5,
    zeCost: 300, zeEvery: 20,
    avoEvery: 180,
    loan: 500, loanBack: 750,
    offlineCap: 8 * 3600,
    legendBonus: 0.1,
  };

  // ---------------------------------------------------------------- estado
  function newState(seed = 12345) {
    return {
      v: 2,
      dirty: 20, clean: 0, para: 0, sta: 100, resp: 0,
      attrs: { bot: 1, lab: 1, fur: 1, seg: 1 },
      xp: { bot: 0, lab: 0, fur: 0, seg: 0 },
      place: 0,
      pots: [{ g: 0, s: 0, on: true }, { g: 0, s: 0, on: true }],
      seed: 0, // semente escolhida para replantar
      stock: Array(SEEDS.length).fill(0),
      equip: {},
      laundry: [], // { amount, done(t), fee }
      city: null, // { id, end }
      ze: false, zeT: 0,
      avoT: 0, debt: 0,
      saleCd: 0,
      raidT: 0,
      legend: 0, runEarned: 0, timesArrested: 0, busts: 0,
      time: 0, rng: seed,
      log: [],
    };
  }

  function rand(s) {
    let x = s.rng | 0;
    x ^= x << 13; x ^= x >>> 17; x ^= x << 5;
    s.rng = x;
    return ((x >>> 0) % 1000000) / 1000000;
  }
  function note(s, kind, text) {
    s.log.push({ t: s.time, kind, text });
    if (s.log.length > 50) s.log.shift();
  }

  // ---------------------------------------------------------------- derivados
  const lvl = (s, id) => s.equip[id] || 0;
  const fxSum = (s, key) => EQUIP.reduce((a, e) => a + (e.fx[key] || 0) * lvl(s, e.id), 0);
  const level = (s) => Math.max(1, Math.floor(Math.sqrt(s.resp / 5)));
  const legendMult = (s) => 1 + R.legendBonus * s.legend;
  // produção: soma dos bônus dos equipamentos + Botânica × 2% (GDD)
  const prodMult = (s) => 1 + EQUIP.reduce((a, e) => a + e.prod * lvl(s, e.id), 0) + s.attrs.bot * 0.02;
  // crescimento: tempo = base / (1 + Botânica × 5%) (GDD), mais equipamentos de velocidade
  const speed = (s) => (1 + s.attrs.bot * 0.05) * (1 + fxSum(s, "speed"));
  const tapPower = (s) => R.tapSeconds * speed(s) * (1 + fxSum(s, "tap"));
  const priceMult = (s, lvlIdx) => (1 + s.attrs.lab * 0.02) * (1 + SALES[lvlIdx].bonus) * legendMult(s) * (1 + (level(s) - 1) * 0.01);
  const riskOf = (s, lvlIdx) => Math.max(0, SALES[lvlIdx].risk - s.attrs.fur * 0.004);
  const paraOf = (s, lvlIdx) => SALES[lvlIdx].para * Math.max(0.2, 1 - fxSum(s, "calm") - s.attrs.fur * 0.01);
  const staCost = (s, base) => (s.para >= 60 ? base * 2 : base);
  const maxPots = (s) => PLACES[s.place].pots;
  const potCost = (s) => Math.round(20 * Math.pow(2.6, s.pots.length - 2)); // grana suja
  const equipCost = (s, e) => Math.round(e.price * Math.pow(EQUIP_LEVEL_MULT, lvl(s, e.id)));
  const saleCooldown = (s) => Math.max(3, 20 - 17 * (topStockSeed(s) / (SEEDS.length - 1))) * Math.max(0.4, 1 - s.attrs.lab * 0.01);
  const stockUnits = (s) => s.stock.reduce((a, b) => a + b, 0);
  const stockValue = (s) => s.stock.reduce((a, n, i) => a + n * SEEDS[i].sell, 0);
  function topStockSeed(s) {
    for (let i = SEEDS.length - 1; i >= 0; i--) if (s.stock[i] > 0) return i;
    return 0;
  }

  function seedLocked(s, seed) {
    const why = [];
    if (s.attrs.bot < seed.bot) why.push(`Botânica ${seed.bot}`);
    for (const r of seed.req) if (!lvl(s, r)) why.push(EQUIP.find((e) => e.id === r).name);
    return why;
  }
  const seedOk = (s, i) => seedLocked(s, SEEDS[i]).length === 0;

  // Renda estimada (grana suja/s) se tudo for vendido no Discreto.
  function incomePerSec(s) {
    let total = 0;
    for (const p of s.pots) {
      const seed = SEEDS[p.s];
      const per = (seed.prod * prodMult(s) * seed.sell * priceMult(s, 0) - seed.price) / (seed.time / speed(s));
      total += Math.max(0, per);
    }
    return total;
  }

  // ---------------------------------------------------------------- plantio
  function plant(s, pot) {
    const seed = SEEDS[pot.s];
    if (s.dirty < seed.price || !seedOk(s, pot.s)) { pot.on = false; return false; }
    s.dirty -= seed.price;
    pot.on = true;
    pot.g = 0;
    return true;
  }

  function harvest(s, pot) {
    const seed = SEEDS[pot.s];
    const units = Math.max(1, Math.floor(seed.prod * prodMult(s)));
    s.stock[pot.s] += units;
    s.resp += 1;
    gainXp(s, "bot", 1);
    pot.s = s.seed; // replanta com a semente escolhida
    return units;
  }

  function growAll(s, seconds) {
    let n = 0;
    for (const p of s.pots) {
      if (!p.on && !plant(s, p)) continue;
      p.g += seconds;
      const t = SEEDS[p.s].time;
      while (p.g >= t) {
        const carry = p.g - t;
        n += harvest(s, p) ? 1 : 0;
        if (!plant(s, p)) { p.g = 0; break; }
        p.g = Math.min(carry, SEEDS[p.s].time * 0.99);
      }
    }
    return n;
  }

  // ---------------------------------------------------------------- atributos
  const XP_NEED = {
    bot: (l) => 20 * Math.pow(l, 1.8),
    lab: (l) => 40 * Math.pow(l, 1.8),
    fur: (l) => 6 * Math.pow(l, 1.8),
    seg: (l) => 10 * Math.pow(l, 1.8),
  };
  function gainXp(s, k, amt) {
    s.xp[k] += amt;
    while (s.xp[k] >= XP_NEED[k](s.attrs[k])) {
      s.xp[k] -= XP_NEED[k](s.attrs[k]);
      s.attrs[k]++;
      note(s, "attr", `+1 ${ATTRS[k]} (agora ${s.attrs[k]})`);
    }
  }

  // ---------------------------------------------------------------- ações
  function tap(s) {
    return growAll(s, tapPower(s));
  }

  // Ações (fora a venda) que levariam a Paranoia a 100% são bloqueadas: só a venda é aposta.
  const safe = (s, add) => s.para + add < 100;

  function sell(s, lvlIdx, auto = false) {
    if (s.saleCd > 0 || stockUnits(s) <= 0) return null;
    const L = SALES[lvlIdx];
    let left = L.max, units = 0, value = 0;
    for (let i = SEEDS.length - 1; i >= 0 && left > 0; i--) {
      const q = Math.min(left, s.stock[i]);
      if (q <= 0) continue;
      s.stock[i] -= q; left -= q; units += q; value += q * SEEDS[i].sell;
    }
    s.saleCd = saleCooldown(s);
    if (!(s.cheat && s.cheat.noPolice) && rand(s) < riskOf(s, lvlIdx)) {
      // flagrante: perde a mercadoria, multa na grana suja, +Paranoia
      const fine = s.dirty * Math.max(0.05, 0.25 - s.attrs.seg * 0.01);
      s.dirty -= fine;
      s.sta = Math.max(0, s.sta - 20);
      s.resp = Math.max(0, s.resp - 5);
      s.para += 15;
      s.timesArrested++;
      note(s, "flagrante", `Flagrante! Perdeu ${units} unidades e $${Math.round(fine)} de multa.`);
      checkBust(s);
      return { units, money: 0, caught: true };
    }
    const money = Math.floor(value * priceMult(s, lvlIdx));
    s.dirty += money;
    s.runEarned += money;
    s.para += paraOf(s, lvlIdx);
    s.resp += Math.ceil(units / 3);
    gainXp(s, "lab", units * (lvlIdx + 1) / 2);
    if (lvlIdx >= 1) gainXp(s, "fur", lvlIdx);
    checkBust(s);
    return { units, money, caught: false };
  }

  function launder(s, methodId, fraction) {
    const m = LAUNDRY.find((x) => x.id === methodId);
    if (s.attrs.lab < m.lab) return false;
    const amount = Math.floor(s.dirty * fraction);
    if (amount < 1) return false;
    s.dirty -= amount;
    if (!safe(s, m.para)) return false;
    const net = Math.floor(amount * (1 - m.fee));
    s.para += m.para;
    if (m.time === 0) s.clean += net;
    else s.laundry.push({ id: m.id, net, done: s.time + m.time });
    checkBust(s);
    return true;
  }

  function buyEquip(s, id) {
    const e = EQUIP.find((x) => x.id === id);
    const c = equipCost(s, e);
    if (s.clean < c) return false;
    s.clean -= c;
    s.equip[id] = lvl(s, id) + 1;
    return true;
  }
  function buyPlace(s) {
    const next = PLACES[s.place + 1];
    if (!next || s.clean < next.cost) return false;
    s.clean -= next.cost;
    s.place++;
    return true;
  }
  function buyPot(s) {
    if (s.pots.length >= maxPots(s)) return false;
    const c = potCost(s);
    if (s.dirty < c) return false;
    s.dirty -= c;
    s.pots.push({ g: 0, s: s.seed, on: false });
    return true;
  }
  function chooseSeed(s, i) {
    if (!seedOk(s, i)) return false;
    s.seed = i;
    // vasos vazios ou parados trocam já; os que estão crescendo trocam na próxima colheita
    for (const p of s.pots) if (!p.on || p.g === 0) { p.s = i; p.on = false; }
    return true;
  }
  function hireZe(s) {
    if (s.ze || s.clean < R.zeCost) return false;
    s.clean -= R.zeCost;
    s.ze = true;
    return true;
  }
  function startCity(s, id) {
    const a = CITY.find((x) => x.id === id);
    if (s.city) return false;
    const cost = staCost(s, a.sta);
    if (s.clean < a.cost || s.sta < cost) return false;
    if (a.fx.para > 0 && !safe(s, a.fx.para)) return false;
    s.clean -= a.cost;
    s.sta -= cost;
    s.city = { id, end: s.time + a.time };
    return true;
  }
  function finishCity(s) {
    const a = CITY.find((x) => x.id === s.city.id);
    const fx = a.fx;
    if (fx.sta) s.sta = Math.min(100, s.sta + fx.sta);
    if (fx.para) s.para = Math.max(0, s.para + fx.para);
    if (fx.resp) s.resp += fx.resp;
    for (const k of ["bot", "lab", "fur", "seg"]) if (fx[k]) gainXp(s, k, XP_NEED[k](s.attrs[k]) * 0.25 * fx[k]);
    note(s, "city", `${a.name}: pronto!`);
    s.city = null;
    checkBust(s);
  }
  function beg(s) {
    const cost = staCost(s, 3 + Math.floor(rand(s) * 6));
    if (s.sta < cost) return 0;
    s.sta -= cost;
    const got = 1 + Math.floor(rand(s) * 3);
    s.dirty += got;
    return got;
  }
  function visitAvo(s) {
    if (s.time < s.avoT || !safe(s, 10)) return false;
    s.avoT = s.time + R.avoEvery;
    s.sta = Math.min(100, s.sta + 15);
    s.dirty += 5;
    s.para += 10;
    if (rand(s) < 0.3) { s.dirty += SEEDS[s.seed].price * 2; note(s, "avo", "A Vó deu um pacotinho de sementes!"); }
    checkBust(s);
    return true;
  }
  function borrow(s) {
    if (s.debt > 0 || !safe(s, 30)) return false;
    s.dirty += R.loan;
    s.debt = R.loanBack;
    s.para += 30;
    checkBust(s);
    return true;
  }
  function repay(s) {
    if (s.debt <= 0 || s.dirty < s.debt) return false;
    s.dirty -= s.debt;
    s.debt = 0;
    return true;
  }

  // ---------------------------------------------------------------- batida e Lenda
  // Lenda = (log10(ganho) − 4)²: $100 mil = 1, $10 mi = 9, $10 bi = 36, $10 tri = 81
  const legendFor = (earned) => (earned < 1e5 ? 0 : Math.floor(Math.pow(Math.log10(earned) - 4, 2)));

  function checkBust(s) {
    if (s.cheat && s.cheat.noPolice) { s.para = Math.min(s.para, 99); return; }
    if (s.para >= 100) bust(s, "A Paranoia chegou a 100%.");
  }
  function bust(s, why) {
    const gain = Math.floor(legendFor(s.runEarned) / 2);
    const keepClean = Math.min(0.4, fxSum(s, "guard") + s.attrs.seg * 0.01) * s.clean;
    note(s, "batida", `${why} Batida policial! +${gain} Lenda.`);
    const keep = { legend: s.legend + gain, attrs: { ...s.attrs, seg: 1, fur: 1 }, timesArrested: s.timesArrested + 1 };
    reset(s, keep);
    s.dirty = 15 * s.legend; // sai da delegacia só com a roupa do corpo (a Lenda ajuda um pouco)
    s.clean = Math.floor(keepClean);
    s.busts++;
    s.lastBust = { why, gain, kept: Math.floor(keepClean) };
  }
  function retire(s) {
    const gain = legendFor(s.runEarned);
    if (gain < 1) return 0;
    note(s, "lenda", `Passou o ponto: +${gain} Lenda.`);
    reset(s, { legend: s.legend + gain, attrs: { ...s.attrs } });
    return gain;
  }
  function reset(s, keep) {
    const persist = { time: s.time, rng: s.rng, log: s.log, busts: s.busts, timesArrested: s.timesArrested, resp: s.resp, xp: s.xp, cheat: s.cheat };
    Object.assign(s, newState(), persist, keep);
    s.attrs.bot = Math.max(s.attrs.bot, 1);
    // Lenda dá um empurrão inicial: começa com mais grana suja
    s.dirty = 20 + 25 * s.legend;
  }

  // ---------------------------------------------------------------- tempo
  function tick(s, dt) {
    s.time += dt;
    s.saleCd = Math.max(0, s.saleCd - dt);
    s.sta = Math.min(100, s.sta + R.staRegen * dt);
    s.para = Math.max(0, s.para - R.paraDecay * dt + (s.debt > 0 ? R.loanPara * dt : 0));
    growAll(s, dt * speed(s));
    for (let i = s.laundry.length - 1; i >= 0; i--) {
      if (s.time >= s.laundry[i].done) { s.clean += s.laundry[i].net; s.laundry.splice(i, 1); }
    }
    if (s.city && s.time >= s.city.end) finishCity(s);
    if (s.ze) {
      s.zeT += dt;
      if (s.zeT >= R.zeEvery) {
        s.zeT = 0;
        const cd = s.saleCd; s.saleCd = 0;
        sell(s, 0, true);
        s.saleCd = Math.max(cd, 0);
      }
    }
    // batida periódica: a cada 5 min, com Paranoia acima de 80, 50% de chance
    s.raidT += dt;
    if (s.raidT >= R.raidEvery) {
      s.raidT = 0;
      if (!(s.cheat && s.cheat.noPolice) && s.para > R.raidAt && rand(s) < R.raidChance) bust(s, "A polícia fez uma ronda e achou o esconderijo.");
    }
    checkBust(s);
  }

  // Com o app fechado: avança em passos de 5 s (até 8 h).
  function offline(s, seconds) {
    const t = Math.min(seconds, R.offlineCap);
    const before = { dirty: s.dirty, clean: s.clean, units: stockUnits(s), resp: s.resp };
    const busts = s.busts;
    let left = t;
    while (left > 0) { const d = Math.min(5, left); tick(s, d); left -= d; }
    return {
      seconds: t,
      dirty: s.dirty - before.dirty, clean: s.clean - before.clean,
      units: stockUnits(s) - before.units, resp: s.resp - before.resp,
      busted: s.busts > busts,
    };
  }

  const api = {
    SEEDS, EQUIP, PLACES, SALES, LAUNDRY, CITY, ATTRS, R,
    safe, newState, tick, tap, sell, launder, buyEquip, buyPlace, buyPot, chooseSeed, hireZe,
    startCity, beg, visitAvo, borrow, repay, retire, offline,
    level, legendMult, prodMult, speed, tapPower, priceMult, riskOf, paraOf, staCost, maxPots, potCost,
    equipCost, saleCooldown, stockUnits, stockValue, seedLocked, seedOk, incomePerSec, legendFor, lvl,
    xpNeed: (k, l) => XP_NEED[k](l),
  };
  if (typeof module !== "undefined") module.exports = api;
  else root.ECON = api;
})(this);
