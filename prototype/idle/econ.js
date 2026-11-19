// Economia do protótipo idle do Greenhood.
// Funções puras sobre um objeto de estado: roda igual no navegador e no Node (simulação).
(function (root) {
  "use strict";

  // Plantas: crescimento necessário (pontos de crescimento) e valor de venda.
  // Cada nível vale 3x e demora 2x (rende 1,5x mais por crescimento), mas custa 15x para liberar.
  const SEED_NAMES = [
    "Alface Mística", "Hortelã Selvagem", "Manjericão do Olimpo", "Tomate Atômico", "Pimenta do Capeta",
    "Cogumelo Saltitante", "Lavanda Hipnótica", "Cacto Cabeludo", "Lótus Azul", "Cipó Enrolado",
    "Orquídea Fantasma", "Trufa Negra", "Mandrágora", "Bonsai Milenar", "Rafflesia Gigante",
    "Aurora Boreal", "Fruto do Éden", "Broto de Yggdrasil",
  ];
  const SEEDS = SEED_NAMES.map((name, i) => ({
    id: i,
    name,
    frame: i + 2, // quadro em plantas.png (0 = broto, 1 = muda)
    grow: Math.round(10 * Math.pow(2, i)),
    value: Math.round(4 * Math.pow(3, i)),
    unlock: i === 0 ? 0 : Math.round(150 * Math.pow(15, i)),
  }));

  // Melhorias com níveis (custo cresce a cada compra). frame = quadro em equipamentos.png
  const UPGRADES = [
    { id: "tesoura", name: "Tesoura enferrujada", frame: 1, base: 15, mult: 1.2, kind: "tap", amt: 1, desc: "+1 de força por toque" },
    { id: "regador", name: "Regador de garrafa PET", frame: 0, base: 30, mult: 1.18, kind: "auto", amt: 0.5, desc: "+0,5 de crescimento/s em cada vaso" },
    { id: "ventilador", name: "Ventilador torto", frame: 2, base: 250, mult: 1.25, kind: "grow", amt: 0.12, desc: "+12% de crescimento" },
    { id: "adubo", name: "Adubo El Secreto", frame: 4, base: 500, mult: 1.27, kind: "value", amt: 0.15, desc: "+15% no valor das plantas" },
    { id: "lampada", name: "Lâmpada de alumínio", frame: 5, base: 3000, mult: 1.2, kind: "auto", amt: 4, desc: "+4 de crescimento/s em cada vaso" },
    { id: "termometro", name: "Termômetro na tábua", frame: 3, base: 4000, mult: 1.25, kind: "cool", amt: 0.15, desc: "A polícia esquece 15% mais rápido" },
    { id: "led", name: "Painel LED", frame: 10, base: 2e5, mult: 1.2, kind: "auto", amt: 40, desc: "+40 de crescimento/s em cada vaso" },
    { id: "hidro", name: "Sistema hidropônico", frame: 11, base: 5e6, mult: 1.25, kind: "grow", amt: 0.5, desc: "+50% de crescimento" },
    { id: "ia", name: "Controlador IA", frame: 15, base: 5e8, mult: 1.22, kind: "auto", amt: 900, desc: "+900 de crescimento/s em cada vaso" },
  ];

  // Esconderijos: limite de vasos. Mudam o cenário (gambiarra -> profissional -> high-tech).
  const PLACES = [
    { name: "Garagem do Vizinho", pots: 3, cost: 0, tier: 0 },
    { name: "Porão Abandonado", pots: 6, cost: 2e5, tier: 0 },
    { name: "Galpão Industrial", pots: 12, cost: 5e8, tier: 1 },
    { name: "Bunker Militar", pots: 24, cost: 5e12, tier: 2 },
  ];

  // Venda: quanto do estoque sai, multiplicador de preço e calor gerado (média).
  const SALES = [
    { name: "Discreto", pct: 0.25, price: 1.0, heat: 4 },
    { name: "Normal", pct: 0.5, price: 1.5, heat: 11 },
    { name: "Ousado", pct: 0.8, price: 2.2, heat: 24 },
    { name: "All-in", pct: 1.0, price: 3.2, heat: 46 },
  ];

  const ZE_COST = 2000; // contratar o Zé: vende sozinho no modo Discreto
  const ZE_INTERVAL = 8; // segundos
  const SALE_COOLDOWN = 1.5;
  const HEAT_DECAY = 1.6; // por segundo
  const LEGEND_BONUS = 0.3; // bônus = 30% × Lenda^0,6 (retorno decrescente)
  const OFFLINE_CAP = 8 * 3600;

  function newState(legend = 0, seed = 12345) {
    return {
      v: 1,
      cash: 0,
      stock: 0, // valor em produto ainda não vendido
      runEarned: 0, // dinheiro ganho nesta rodada (para a Lenda)
      heat: 0,
      seed: 0, // semente ativa (índice)
      unlocked: 1,
      pots: [0], // crescimento acumulado de cada vaso
      place: 0,
      levels: Object.fromEntries(UPGRADES.map((u) => [u.id, 0])),
      ze: false,
      zeTimer: 0,
      saleCd: 0,
      legend,
      legendSpent: 0,
      busts: 0,
      time: 0,
      rng: seed,
      log: [],
    };
  }

  function rand(s) {
    // xorshift determinístico, para a simulação ser reproduzível
    let x = s.rng | 0;
    x ^= x << 13; x ^= x >>> 17; x ^= x << 5;
    s.rng = x;
    return ((x >>> 0) % 100000) / 100000;
  }

  const lvl = (s, id) => s.levels[id] || 0;
  function sumKind(s, kind) {
    return UPGRADES.filter((u) => u.kind === kind).reduce((a, u) => a + u.amt * lvl(s, u.id), 0);
  }
  const legendMult = (s) => 1 + LEGEND_BONUS * Math.pow(s.legend, 0.6);
  const tapPower = (s) => (1 + sumKind(s, "tap")) * growMult(s);
  const growMult = (s) => 1 + sumKind(s, "grow");
  const autoRate = (s) => sumKind(s, "auto") * growMult(s); // por vaso, por segundo
  const valueMult = (s) => (1 + sumKind(s, "value")) * legendMult(s);
  const coolRate = (s) => HEAT_DECAY * (1 + sumKind(s, "cool"));

  const upgradeCost = (s, u) => Math.round(u.base * Math.pow(u.mult, lvl(s, u.id)));
  const potCost = (s) => Math.round(30 * Math.pow(3.1, s.pots.length - 1));
  const maxPots = (s) => PLACES[s.place].pots;

  // Produção estimada por segundo (só o automático), em dinheiro, no modo Discreto.
  function incomePerSec(s) {
    const seed = SEEDS[s.seed];
    return (autoRate(s) * s.pots.length / seed.grow) * seed.value * valueMult(s);
  }

  function grow(s, amount) {
    const seed = SEEDS[s.seed];
    let harvested = 0;
    for (let i = 0; i < s.pots.length; i++) {
      s.pots[i] += amount;
      if (s.pots[i] >= seed.grow) {
        const n = Math.floor(s.pots[i] / seed.grow);
        s.pots[i] -= n * seed.grow;
        harvested += n;
      }
    }
    if (harvested) s.stock += harvested * seed.value * valueMult(s);
    return harvested;
  }

  function tap(s) {
    return grow(s, tapPower(s));
  }

  function sell(s, level) {
    if (s.saleCd > 0 || s.stock <= 0) return 0;
    const L = SALES[level];
    const goods = s.stock * L.pct;
    const money = goods * L.price;
    s.stock -= goods;
    s.cash += money;
    s.runEarned += money;
    // calor com variação de 50% a 150%: é aqui que mora o risco
    s.heat += L.heat * (0.5 + rand(s));
    s.saleCd = SALE_COOLDOWN;
    if (s.heat >= 100) bust(s);
    return money;
  }

  // Lenda: pontos pela raiz cúbica do que foi ganho na rodada (10M = 1 ponto, 80M = 2, 10B = 10).
  // Ser pego dá só metade. A raiz cúbica impede que a Lenda dispare sem limite.
  const legendFor = (earned) => Math.floor(Math.cbrt(earned / 1e7));

  function bust(s) {
    const gain = Math.floor(legendFor(s.runEarned) / 2);
    s.log.push({ t: s.time, ev: "batida", gain });
    reset(s, s.legend + gain);
    s.busts++;
  }

  function retire(s) {
    const gain = legendFor(s.runEarned);
    if (gain < 1) return 0;
    s.log.push({ t: s.time, ev: "aposentou", gain });
    reset(s, s.legend + gain);
    return gain;
  }

  function reset(s, legend) {
    const keep = { time: s.time, busts: s.busts, log: s.log, rng: s.rng };
    Object.assign(s, newState(legend), keep);
    if (legend > 0) s.levels.regador = 1; // quem já tem Lenda recomeça com um regador
  }

  function buyUpgrade(s, id) {
    const u = UPGRADES.find((x) => x.id === id);
    const c = upgradeCost(s, u);
    if (s.cash < c) return false;
    s.cash -= c;
    s.levels[id]++;
    return true;
  }
  function buyPot(s) {
    if (s.pots.length >= maxPots(s)) return false;
    const c = potCost(s);
    if (s.cash < c) return false;
    s.cash -= c;
    s.pots.push(0);
    return true;
  }
  function buySeed(s) {
    if (s.unlocked >= SEEDS.length) return false;
    const c = SEEDS[s.unlocked].unlock;
    if (s.cash < c) return false;
    s.cash -= c;
    s.unlocked++;
    s.seed = s.unlocked - 1;
    s.pots = s.pots.map(() => 0);
    return true;
  }
  function buyPlace(s) {
    const next = PLACES[s.place + 1];
    if (!next || s.cash < next.cost) return false;
    s.cash -= next.cost;
    s.place++;
    return true;
  }
  function hireZe(s) {
    if (s.ze || s.cash < ZE_COST) return false;
    s.cash -= ZE_COST;
    s.ze = true;
    return true;
  }

  function tick(s, dt) {
    s.time += dt;
    s.saleCd = Math.max(0, s.saleCd - dt);
    s.heat = Math.max(0, s.heat - coolRate(s) * dt);
    const a = autoRate(s);
    if (a > 0) grow(s, a * dt);
    if (s.ze) {
      s.zeTimer += dt;
      while (s.zeTimer >= ZE_INTERVAL) {
        s.zeTimer -= ZE_INTERVAL;
        const cd = s.saleCd;
        s.saleCd = 0;
        sell(s, 0);
        s.saleCd = cd;
      }
    }
  }

  // Ganhos com o app fechado: só o automático, e só vende se o Zé estiver contratado.
  function offline(s, seconds) {
    const t = Math.min(seconds, OFFLINE_CAP);
    const before = s.cash + s.stock;
    const seed = SEEDS[s.seed];
    const harvests = (autoRate(s) * t / seed.grow) * s.pots.length;
    const goods = harvests * seed.value * valueMult(s);
    if (s.ze) {
      s.cash += goods;
      s.runEarned += goods;
    } else {
      s.stock += goods;
    }
    s.heat = Math.max(0, s.heat - coolRate(s) * t);
    return s.cash + s.stock - before;
  }

  const api = {
    SEEDS, UPGRADES, PLACES, SALES, ZE_COST, LEGEND_BONUS,
    newState, tick, tap, sell, retire, buyUpgrade, buyPot, buySeed, buyPlace, hireZe, offline,
    tapPower, autoRate, growMult, valueMult, coolRate, upgradeCost, potCost, maxPots, incomePerSec, legendFor,
  };
  if (typeof module !== "undefined") module.exports = api;
  else root.ECON = api;
})(this);
