// Economia do Greenhood Idle — o GDD inteiro adaptado para jogo idle.
// Funções puras sobre um objeto de estado: roda igual no navegador e no Node (simulação).
(function (root) {
  "use strict";

  // ---------------------------------------------------------------- catálogos
  // Sementes (números do GDD): preço (grana suja, pago a cada plantio), venda por unidade,
  // unidades por colheita, Botânica mínima, equipamentos exigidos e tempo de crescimento (s).
  // venda e semente pela metade da tabela do GDD: o lucro de cada colheita cai pela metade
  // (o jogo estava fácil demais), e cada semente continua melhor que a anterior
  const SELL_MULT = 0.5;
  const SEEDS = [
    ["Alface Mística", 5, 8, 3, 1, [], 30],
    ["Hortelã Selvagem", 10, 15, 3, 2, [], 35],
    ["Manjericão do Olimpo", 20, 30, 4, 3, [], 45],
    ["Tomate Atômico", 50, 80, 4, 4, ["regador"], 55],
    ["Pimenta do Capeta", 120, 200, 3, 5, ["regador", "termometro"], 60],
    ["Cogumelo Saltitante", 300, 500, 5, 6, ["termometro", "ventilador"], 75],
    ["Lavanda Hipnótica", 800, 1200, 4, 7, ["fertilizante", "ventilador"], 90],
    ["Cacto Cabeludo", 2000, 3500, 2, 8, ["ph", "termometro"], 100],
    ["Lótus Azul", 5000, 8000, 3, 9, ["ventilador", "ph", "fertilizante"], 120],
    ["Cipó Enrolado", 12000, 25000, 2, 10, ["filtro", "ph"], 150],
    ["Orquídea Fantasma", 30000, 60000, 2, 12, ["filtro", "led"], 180],
    ["Trufa Negra", 80000, 150000, 2, 14, ["led", "filtro", "ph"], 210],
    ["Mandrágora", 200000, 450000, 1, 16, ["led", "hidro", "filtro"], 240],
    ["Bonsai Milenar", 500000, 1.2e6, 1, 18, ["hidro", "co2", "led"], 300],
    ["Rafflesia Gigante", 1.5e6, 4e6, 1, 20, ["co2", "led", "filtro"], 360],
    ["Aurora Boreal", 5e6, 1.5e7, 1, 23, ["ia", "co2", "led"], 420],
    ["Fruto do Éden", 2e7, 6.5e7, 1, 26, ["ia", "lab"], 600],
    ["Broto de Yggdrasil", 1e8, 3.5e8, 1, 30, ["lab", "ia", "cameras", "drone"], 900],
  ].map(([name, price, sell, prod, bot, req, time], id) => ({ id, name, price: Math.ceil(price * SELL_MULT), sell: Math.round(sell * SELL_MULT), prod, bot, req, time, frame: id }));

  // Equipamentos (GDD): preço em grana limpa e bônus de produção. Cada um tem níveis
  // (o 1º libera sementes; os seguintes repetem o bônus) e um efeito extra.
  // Regras de instalação. max: níveis (5, ou 1 = compra única). keep: vai com você ao se mudar
  // (os outros ficam para trás e são comprados de novo no lugar novo). place: lugar mínimo onde cabe.
  const EQUIP_RULES = {
    regador: { max: 5, place: 0 }, tesoura: { max: 5, place: 0 }, ventilador: { max: 5, place: 1 },
    termometro: { max: 5, place: 0 }, fertilizante: { max: 5, place: 2 }, lampada: { max: 5, place: 1 },
    ph: { max: 5, place: 2 }, estufa: { max: 5, place: 2 }, drone: { max: 1, keep: true, place: 3 },
    filtro: { max: 5, place: 3 }, led: { max: 5, place: 3 }, hidro: { max: 1, keep: true, place: 6 },
    co2: { max: 5, place: 6 }, cameras: { max: 5, place: 4 }, osmose: { max: 5, place: 7 },
    ia: { max: 1, keep: true, place: 7 }, bunker: { max: 1, keep: true, place: 12, only: true },
    lab: { max: 1, keep: true, place: 12, only: true },
  };
  // saíram do jogo: lâmpada com alumínio, mini estufa, osmose reversa e kit bunker
  const REMOVED_EQUIP = ["lampada", "estufa", "osmose", "bunker"];
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
    ["cameras", "Câmeras 4K", 1.5e6, 0.03, { guard: 0.1 }, "Rondas têm 10% menos chance de te achar"],
    ["osmose", "Osmose reversa", 4e6, 0.08, {}, ""],
    ["ia", "Controlador IA", 1e7, 0.15, { tap: 1 }, "Toque 100% mais forte"],
    ["bunker", "Kit bunker", 3.5e7, 0.12, { guard: 0.25 }, "Rondas têm 25% menos chance de te achar"],
    ["lab", "Lab. de genética", 1.5e8, 0.2, { speed: 0.25 }, "Cresce 25% mais rápido"],
  ].map(([id, name, price, prod, fx, fxText], i) => ({ id, name, price, prod, fx, fxText, frame: i, ...EQUIP_RULES[id] }))
    .filter((e) => !REMOVED_EQUIP.includes(e.id));
  const EQUIP_LEVEL_MULT = 3; // cada nível extra custa 3x o anterior (nível 5 = 81x o preço inicial)

  // Imóveis (GDD), em grana limpa. tier = visual (0 gambiarra, 1 profissional, 2 high-tech).
  const PLACE_MULT = 3; // imóveis mais caros (o jogo estava rápido demais)
  const PLACES = [
    ["Armário Grow", 0, 2, 0],
    ["Quartinho dos fundos", 150, 3, 0],
    ["Garagem do Vizinho", 900, 4, 0],
    ["Porão Abandonado", 5000, 5, 0],
    ["Sobrado na Favela", 25000, 6, 0],
    ["Terreno Abandonado", 120000, 8, 1],
    ["Container Marítimo", 600000, 10, 1],
    ["Galpão Industrial", 3000000, 12, 1],
    ["Sítio na Serra", 15000000, 14, 1],
    ["Fazenda Paraíso Verde", 70000000, 18, 1],
    ["Mina de Ouro Desativada", 350000000, 24, 2],
    ["Praia Particular", 1500000000, 30, 2],
    ["Bunker Desativado", 7000000000, 40, 2],
  ].map(([name, cost, pots, tier], id) => ({ id, name, cost: Math.round(cost * (id > 1 ? PLACE_MULT : id === 1 ? 3 : 1)), pots, tier }));

  // Venda (GDD): quantidade máxima, Paranoia, chance de flagrante e bônus de preço.
  // Venda: fatia do estoque que sai (pct), Paranoia, chance de flagrante e bônus de preço.
  // Quanto maior a fatia, maior o risco; o All-in vende tudo com o maior risco.
  const SALES = [
    // sta: Estamina gasta pela venda (proporcional ao tamanho; o Zé não gasta a sua)
    { name: "Discreto", pct: 0.05, para: 5, risk: 0, bonus: 0, sta: 1 },
    { name: "Normal", pct: 0.15, para: 15, risk: 0.03, bonus: 0.1, sta: 3 },
    { name: "Ousado", pct: 0.35, para: 25, risk: 0.08, bonus: 0.25, sta: 6 },
    { name: "Agressivo", pct: 0.7, para: 40, risk: 0.15, bonus: 0.5, sta: 10 },
    { name: "All-in", pct: 1, para: 60, risk: 0.3, bonus: 1, sta: 16 },
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

  // Fachadas: negócios que lavam sozinhos (até com o app fechado). cap = $/min no nível 1.
  // Cada nível: custa 2,5x e lava 1,7x mais. Nunca mexem na reserva para replantar.
  const FRONTS = [
    { id: "lavajato", name: "Lava-jato do Primo", emoji: "🚗", cost: 300, cap: 30, fee: 0.15 },
    { id: "pastel", name: "Pastelaria da Esquina", emoji: "🥟", cost: 3000, cap: 250, fee: 0.14 },
    { id: "barbearia", name: "Barbearia Navalha", emoji: "💈", cost: 25000, cap: 2000, fee: 0.13 },
    { id: "igreja", name: "Igreja da Prosperidade", emoji: "⛪", cost: 200000, cap: 16000, fee: 0.12 },
    { id: "cambio", name: "Casa de Câmbio", emoji: "💱", cost: 2e6, cap: 150000, fee: 0.12 },
    { id: "galeria", name: "Galeria de Arte", emoji: "🖼️", cost: 2e7, cap: 1.4e6, fee: 0.11 },
    { id: "futebol", name: "Time de Futebol", emoji: "⚽", cost: 3e8, cap: 2e7, fee: 0.1 },
  ];
  const FRONT_MAX = 10;

  // Visita surpresa da Vó: pequena chance para todo mundo. Ela descobre tudo e você escolhe uma
  // de duas explicações (sorteadas destas 10): 5 levam à cadeia, 4 passam, 1 deixa a Paranoia lá em cima.
  const SURPRISE = [
    { say: "É tempero pra sua sopa, vó!", res: "Ela prova uma folha, passa mal e chama a ambulância. A polícia veio junto.", kind: "bust" },
    { say: "É um trabalho da escola sobre fotossíntese.", res: "Ela liga na escola para elogiar você. A diretora chama a polícia.", kind: "bust" },
    { say: "São plantas de um amigo, tô só cuidando.", res: "\"Então liga pra ele agora.\" Você liga pro Zé, que atende: \"E aí, chefe, chegou a carga?\"", kind: "bust" },
    { say: "Tô empreendendo, vó! É um negócio.", res: "Ela fica orgulhosa e conta para a vizinha, que é casada com o delegado.", kind: "bust" },
    { say: "Isso? Nunca vi na vida.", res: "Ela não acredita e chama seu tio, que é policial.", kind: "bust" },
    { say: "É chá pra sua artrite, vó.", res: "Ela se emociona, leva um pouquinho e jura segredo.", kind: "safe" },
    { say: "São mudas pra horta da igreja.", res: "Ela te dá a bênção e um pedaço de bolo. +30⚡", kind: "safe", sta: 30 },
    { say: "Tô estudando pra ser botânico.", res: "Ela te dá um livro velho de plantas. Você aprende umas coisas.", kind: "safe", bot: true },
    { say: "É surpresa pro seu aniversário!", res: "Ela chora, te abraça e promete não contar pra ninguém.", kind: "safe" },
    { say: "Senta aí, vó, vou te contar a verdade...", res: "Ela desmaia, acorda e passa a semana te ligando de hora em hora. A Paranoia foi lá em cima.", kind: "para" },
  ];

  // Cidades: depois do Bunker, com as 18 sementes, você se muda e recomeça numa cidade nova.
  // Cada cidade: produção ×1,5 para sempre (você já sabe o que faz), polícia +10% mais esperta. Não tem fim.
  const TOWNS = ["Vila Esperança", "Baixada Verde", "Serra Alta", "Porto das Águas", "Capital", "Litoral Sul", "Metrópole"];
  const townName = (i) => (i < TOWNS.length ? TOWNS[i] : `Metrópole ${i - TOWNS.length + 2}`);

  // Encomendas: clientes pedem N unidades de uma planta, com prazo, e pagam 2-3x o preço normal.
  const ORDERS_FROM = 4; // as encomendas só começam no Sobrado na Favela (lá tem freguesia)
  const CLIENTS = [
    ["🍺", "Seu Jorge do bar"], ["🎂", "Tia do bolo"], ["🎓", "Playboy da faculdade"], ["🎧", "DJ da festa"],
    ["🙏", "Irmã Lurdes"], ["🏋️", "Personal da academia"], ["🎨", "Artista da praça"], ["🛵", "Motoboy do bairro"],
  ];

  const ATTRS = { bot: "Botânica", lab: "Lábia", fur: "Furtividade", seg: "Segurança" };

  // ---------------------------------------------------------------- regras
  const R = {
    tapSeconds: 0.35, // cada toque adianta 0,35 s de crescimento em todos os vasos
    paraDecay: 1 / 8, // Paranoia cai 1 a cada 8 s
    paraDecayLow: 1 / 3, paraCalm: 40, // abaixo de 40%: cai 1 a cada 3 s (vender no Discreto não acumula)
    fichaStep: 10, fichaMax: 50, // cada batida sobe a ficha na polícia (piso da Paranoia)
    fichaLenda: 5, // a cada 5 de Lenda ganhos depois da batida, a ficha baixa 5
    loanPara: 3 / 60, // dívida com o agiota: +3 por minuto
    staRegen: 1 / 20, // Estamina: +1 a cada 20 s
    raidEvery: 300, raidAt: 80, raidChance: 0.5,
    zeCost: 300, zeEvery: 20, zeMaxPara: 60,
    frontPara: 0.4 / 60, // cada fachada lavando: +0,4 de Paranoia por minuto
    orderEvery: 180, orderTime: 600, orderMax: 3, // encomendas: uma nova a cada 3 min (até 3), prazo de 10 min
    surpriseEvery: 900, surpriseChance: 0.06, // a cada 15 min, 6% de chance (com o jogo aberto)
    fiscalEvery: 420, fiscalChance: 0.35, fiscalClose: 900, // fiscal da Receita: a cada 7 min, 35%; fechar = 15 min
    billSta: 1, billPara: 0.15, // maquininha: por toque
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
      ficha: 0, fichaLenda: 0, // ficha na polícia: piso da Paranoia
      pots: [{ g: 0, s: 0, on: true }],
      seed: 0, // semente escolhida para replantar
      stock: Array(SEEDS.length).fill(0),
      equip: {},
      laundry: [], // { amount, done(t), fee }
      fronts: {}, // id -> nível
      closed: {}, // id -> até quando a fachada fica fechada
      fiscal: null, fiscalT: 0, // fiscal da Receita esperando resposta
      orders: [], orderT: 150, orderN: 0, // encomendas abertas
      town: 0, // cidade (0 = a primeira)
      surprise: null, surpT: 0, // visita surpresa da Vó esperando sua explicação
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
  // cidade nova: tudo vale e custa 10x mais (números maiores, mesmo ritmo), produção ×1,25 e Botânica +6 nas sementes
  const townScale = (s) => Math.pow(10, s.town || 0);
  const townProd = (s) => Math.pow(1.25, s.town || 0);
  const seedPrice = (s, i) => SEEDS[i].price * townScale(s);
  const prodMult = (s) => (1 + EQUIP.reduce((a, e) => a + e.prod * lvl(s, e.id), 0) + s.attrs.bot * 0.02) * townProd(s);
  // crescimento: tempo = base / (1 + Botânica × 5%) (GDD), mais equipamentos de velocidade
  // Modo fácil (para testar com amigos): cresce 3x mais rápido, vende 2x mais caro, tudo custa 30%,
  // atributos sobem 3x mais rápido, Paranoia cai 2x mais rápido e a espera entre vendas cai pela metade.
  const EASY = { speed: 3, price: 2, cost: 0.15, xp: 4, decay: 2, cd: 0.5 };
  const ez = (s, k) => (s.easy ? EASY[k] : 1);
  const speed = (s) => (1 + s.attrs.bot * 0.05) * (1 + fxSum(s, "speed")) * ez(s, "speed");
  const tapPower = (s) => R.tapSeconds * speed(s) * (1 + fxSum(s, "tap"));
  const priceMult = (s, lvlIdx) => (1 + s.attrs.lab * 0.02) * (1 + SALES[lvlIdx].bonus) * legendMult(s) * (1 + (level(s) - 1) * 0.01) * ez(s, "price") * townScale(s);
  const riskOf = (s, lvlIdx) => Math.max(0, SALES[lvlIdx].risk - s.attrs.fur * 0.004) * (1 + 0.1 * (s.town || 0));
  const paraOf = (s, lvlIdx) => SALES[lvlIdx].para * Math.max(0.2, 1 - fxSum(s, "calm") - s.attrs.fur * 0.01);
  const saleSta = (s, lvlIdx) => staCost(s, SALES[lvlIdx].sta);
  const staCost = (s, base) => (s.para >= 60 ? base * 2 : base);
  const maxPots = (s) => PLACES[s.place].pots;
  // vaso novo: segue o preço do lugar onde você está, subindo a cada vaso comprado ali.
  // Assim encher o cômodo custa parecido em todo lugar, em vez de explodir no fim do jogo.
  const POT_MIN = 100, POT_SHARE = 0.13, POT_GROW = 1.3; // vaso: 13% do lugar (mín. $100), +30% a cada vaso ali
  const potCost = (s) => {
    const prev = s.place > 0 ? PLACES[s.place - 1].pots : 0;
    const base = Math.max(POT_MIN, PLACES[s.place].cost * POT_SHARE) * townScale(s);
    return Math.round(base * Math.pow(POT_GROW, Math.max(0, s.pots.length - Math.max(1, prev))) * ez(s, "cost"));
  };
  const equipCost = (s, e) => Math.round(e.price * Math.pow(EQUIP_LEVEL_MULT, lvl(s, e.id)) * ez(s, "cost") * townScale(s));
  const placeCost = (s, i = s.place + 1) => (PLACES[i] ? Math.round(PLACES[i].cost * ez(s, "cost") * townScale(s)) : Infinity);
  const saleCooldown = (s) => Math.max(3, 20 - 17 * (topStockSeed(s) / (SEEDS.length - 1))) * Math.max(0.4, 1 - s.attrs.lab * 0.01) * ez(s, "cd");
  const stockUnits = (s) => s.stock.reduce((a, b) => a + b, 0);
  const stockValue = (s) => s.stock.reduce((a, n, i) => a + n * SEEDS[i].sell, 0);
  function topStockSeed(s) {
    for (let i = SEEDS.length - 1; i >= 0; i--) if (s.stock[i] > 0) return i;
    return 0;
  }

  function seedLocked(s, seed) {
    const why = [];
    const bot = seed.bot + 6 * (s.town || 0);
    if (s.attrs.bot < bot) why.push(`Botânica ${bot}`);
    for (const r of seed.req) if (!lvl(s, r)) why.push(EQUIP.find((e) => e.id === r).name);
    return why;
  }
  const seedOk = (s, i) => seedLocked(s, SEEDS[i]).length === 0;

  // Renda estimada (grana suja/s) se tudo for vendido no Discreto.
  function incomePerSec(s) {
    let total = 0;
    for (const p of s.pots) {
      const seed = SEEDS[p.s];
      const per = (seed.prod * prodMult(s) * seed.sell * priceMult(s, 0) - seedPrice(s, p.s)) / (seed.time / speed(s));
      total += Math.max(0, per);
    }
    return total;
  }

  // ---------------------------------------------------------------- plantio
  // sementes e vasos: paga com grana suja; se faltar, completa com a limpa (limpa compra tudo)
  const canPay = (s, c) => s.dirty + s.clean >= c;
  function pay(s, c) { const d = Math.min(s.dirty, c); s.dirty -= d; s.clean -= c - d; }
  function plant(s, pot) {
    const seed = SEEDS[pot.s];
    if (!canPay(s, seedPrice(s, pot.s)) || !seedOk(s, pot.s)) { pot.on = false; return false; }
    pay(s, seedPrice(s, pot.s));
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
    bot: (l) => 32 * Math.pow(l, 1.9),
    lab: (l) => 40 * Math.pow(l, 1.8),
    fur: (l) => 6 * Math.pow(l, 1.8),
    seg: (l) => 10 * Math.pow(l, 1.8),
  };
  function gainXp(s, k, amt) {
    s.xp[k] += amt * ez(s, "xp");
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
    if (!auto) {
      const sc = staCost(s, L.sta);
      if (s.sta < sc) return null;
      s.sta -= sc;
    }
    // vende a fatia do estoque (no mínimo 1 unidade), começando pelas plantas mais valiosas
    let left = Math.max(1, Math.ceil(stockUnits(s) * L.pct)), units = 0, value = 0;
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
    gainXp(s, "lab", Math.sqrt(units) * (lvlIdx + 1));   // raiz: vender muito não dispara a Lábia
    if (lvlIdx >= 1) gainXp(s, "fur", lvlIdx);
    checkBust(s);
    return { units, money, caught: false };
  }

  // Mercado: a taxa do crypto e dos NFTs sobe e desce (ciclos de ~10 min e ~3 min).
  function marketMult(id, t) {
    const ph = id === "nft" ? 2.1 : 0;
    const m = 1 + 0.55 * Math.sin((2 * Math.PI * t) / 600 + ph) + 0.2 * Math.sin((2 * Math.PI * t) / 170 + ph * 1.7);
    return Math.max(0.3, Math.min(1.8, m));
  }
  const marketFee = (s, id, t = s.time) => {
    const m = LAUNDRY.find((x) => x.id === id);
    return id === "crypto" || id === "nft" ? Math.min(0.9, m.fee * marketMult(id, t)) : m.fee;
  };
  // reserva para replantar: fachadas e maquininha não encostam nela
  const reserve = (s) => Math.max(30, seedPrice(s, s.seed) * s.pots.length * 3);
  const frontLvl = (s, id) => (s.fronts && s.fronts[id]) || 0;
  const frontCost = (s, f) => Math.round(f.cost * Math.pow(2.5, frontLvl(s, f.id)) * ez(s, "cost") * townScale(s));
  const frontCap = (f, l, s) => (l ? f.cap * Math.pow(1.7, l - 1) * (s ? townScale(s) : 1) : 0); // $/min
  function buyFront(s, id) {
    const f = FRONTS.find((x) => x.id === id);
    if (frontLvl(s, id) >= FRONT_MAX) return false;
    const c = frontCost(s, f);
    if (s.clean < c) return false;
    s.clean -= c;
    s.fronts[id] = frontLvl(s, id) + 1;
    return true;
  }
  const frontOpen = (s, id) => !(s.closed && s.closed[id] > s.time) && !(s.fiscal && s.fiscal.id === id);
  function runFronts(s, dt) {
    let avail = Math.max(0, s.dirty - reserve(s)), active = 0;
    for (const f of FRONTS) {
      const l = frontLvl(s, f.id);
      if (!l || !frontOpen(s, f.id) || avail <= 0) continue;
      const amt = Math.min(avail, (frontCap(f, l, s) / 60) * dt);
      avail -= amt; s.dirty -= amt;
      s.clean += amt * (1 - f.fee);
      active++;
    }
    if (active) s.para += active * R.frontPara * dt;
    return active;
  }
  // Fiscal da Receita: aparece numa fachada que está lavando
  function fiscalCheck(s, dt) {
    if (s.fiscal) {
      if (s.time - s.fiscal.at > 120) fiscalClose(s, true); // ninguém respondeu: fecha sozinha
      return;
    }
    s.fiscalT += dt;
    if (s.fiscalT < R.fiscalEvery) return;
    s.fiscalT = 0;
    const open = FRONTS.filter((f) => frontLvl(s, f.id) && frontOpen(s, f.id));
    if (!open.length || s.dirty <= reserve(s) || rand(s) > R.fiscalChance) return;
    const f = open[open.length - 1]; // a maior chama mais atenção
    const bribe = Math.round(frontCap(f, frontLvl(s, f.id), s) * 8 * Math.max(0.5, 1 - s.attrs.lab * 0.01));
    s.fiscal = { id: f.id, at: s.time, bribe };
    note(s, "fiscal", `Fiscal da Receita na ${f.name}!`);
  }
  function fiscalBribe(s) {
    if (!s.fiscal || s.clean < s.fiscal.bribe) return false;
    s.clean -= s.fiscal.bribe;
    note(s, "city", "O fiscal pegou o envelope e foi embora.");
    s.fiscal = null;
    return true;
  }
  function fiscalClose(s, auto) {
    if (!s.fiscal) return false;
    s.closed[s.fiscal.id] = s.time + R.fiscalClose;
    note(s, "city", auto ? "Ninguém atendeu o fiscal: a fachada ficou fechada por 15 min." : "Você fechou a fachada por 15 min até a poeira baixar.");
    s.fiscal = null;
    return true;
  }
  function fiscalRisk(s) {
    if (!s.fiscal) return null;
    s.fiscal = null;
    if (rand(s) < 0.5 + s.attrs.lab * 0.005) { note(s, "city", "Você enrolou o fiscal. Passou!"); return true; }
    const fine = Math.round(s.clean * 0.3);
    s.clean -= fine;
    s.para += 20;
    note(s, "flagrante", `O fiscal não engoliu: multa de $${fine} e +20 Paranoia.`);
    checkBust(s);
    return false;
  }
  // Maquininha de contar notas: lava sem taxa, mas cansa. Combo de 1 a 3 (cada toque rápido soma +0,25).
  const BILL_MAX = 3;
  const billValue = (s) => Math.max(10, incomePerSec(s) * 1.5);
  function countBills(s, combo) {
    const cost = staCost(s, R.billSta);
    if (s.sta < cost) return 0;
    const amt = Math.min(Math.max(0, s.dirty - reserve(s)), billValue(s) * Math.max(1, Math.min(BILL_MAX, combo)));
    if (amt < 1) return 0;
    if (!safe(s, R.billPara)) return 0;
    s.sta -= cost;
    s.dirty -= amt; s.clean += amt;
    s.para += R.billPara;
    return amt;
  }

  function launder(s, methodId, fraction) {
    const m = LAUNDRY.find((x) => x.id === methodId);
    if (s.attrs.lab < m.lab) return false;
    const amount = Math.floor(s.dirty * fraction);
    if (amount < 1) return false;
    s.dirty -= amount;
    if (!safe(s, m.para)) return false;
    const net = Math.floor(amount * (1 - marketFee(s, methodId)));
    s.para += m.para;
    if (m.time === 0) s.clean += net;
    else s.laundry.push({ id: m.id, net, done: s.time + m.time });
    checkBust(s);
    return true;
  }

  // por que não dá para comprar agora ("" = pode)
  function equipBlock(s, e) {
    if (lvl(s, e.id) >= e.max) return e.max === 1 ? "Já instalado" : "Nível máximo";
    if (s.place < e.place) return e.only ? `Só no ${PLACES[e.place].name}` : `Não cabe no ${PLACES[s.place].name} · precisa de ${PLACES[e.place].name}`;
    return "";
  }
  function bestSeed(s) { for (let i = SEEDS.length - 1; i >= 0; i--) if (seedOk(s, i)) return i; return 0; }
  function buyEquip(s, id) {
    const e = EQUIP.find((x) => x.id === id);
    if (equipBlock(s, e)) return false;
    const c = equipCost(s, e);
    if (s.clean < c) return false;
    s.clean -= c;
    s.equip[id] = lvl(s, id) + 1;
    return true;
  }
  const HOME_PLACE = 1; // o Quartinho é da sua casa: aceita grana suja
  const placeNeedsClean = (s, i = s.place + 1) => i !== HOME_PLACE;
  function buyPlace(s) {
    const next = PLACES[s.place + 1];
    const pc = placeCost(s);
    if (!next) return false;
    if (s.place + 1 === HOME_PLACE) { if (!canPay(s, pc)) return false; pay(s, pc); }
    else { if (s.clean < pc) return false; s.clean -= pc; }
    s.place++;
    // os equipamentos do lugar antigo ficam para trás; só os de compra única vêm junto
    for (const e of EQUIP) if (!e.keep) delete s.equip[e.id];
    if (!seedOk(s, s.seed)) s.seed = bestSeed(s);
    return true;
  }
  function buyPot(s) {
    if (s.pots.length >= maxPots(s)) return false;
    const c = potCost(s);
    if (!canPay(s, c)) return false;
    pay(s, c);
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
    if (fx.para) s.para = Math.max(s.ficha || 0, s.para + fx.para);
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
    s.clean += got; // esmola é dinheiro limpo
    return got;
  }
  function visitAvo(s) {
    if (s.time < s.avoT || !safe(s, 10)) return false;
    s.avoT = s.time + R.avoEvery;
    s.sta = Math.min(100, s.sta + 15);
    s.clean += 5; // o dinheiro da Vó é limpinho
    s.para += 10;
    if (rand(s) < 0.3) { s.clean += seedPrice(s, s.seed) * 2; note(s, "avo", "A Vó deu um dinheirinho pras sementes!"); }
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
  // Batida: perde TUDO (grana suja e limpa, estoque, equipamentos, imóveis) e volta ao Armário.
  // Fica só o que é do personagem: atributos, Respeito e Lenda (+ metade da Lenda da rodada).
  function bust(s, why, force = false) {
    if (!s.warned && !force) {                                     // a primeira vez é só um susto
      s.warned = true;
      s.para = 50;
      s.raidT = 0;
      s.lastWarn = { why, at: s.time };
      note(s, "aviso", "A Dona Cleide te pegou no flagra. Da próxima vez ela conta tudo pra Vó.");
      return;
    }
    const gain = Math.floor(legendFor(s.runEarned / townScale(s)) / 2);
    note(s, "batida", `${why} Batida policial! +${gain} Lenda.`);
    const ficha = Math.min(R.fichaMax, (s.ficha || 0) + R.fichaStep);
    const keep = { legend: s.legend + gain, attrs: { ...s.attrs }, timesArrested: s.timesArrested + 1, ficha, fichaLenda: s.legend + gain };
    reset(s, keep);
    s.para = ficha; // sai da delegacia fichado
    s.dirty = 15 * s.legend; // sai da delegacia só com a roupa do corpo (a Lenda ajuda um pouco)
    s.clean = 0;
    s.busts++;
    s.lastBust = { why, gain, kept: 0 };
  }
  // Advogado: baixa a ficha em 10 na hora. Fica 10x mais caro a cada 10% de ficha.
  const lawyerCost = (s) => Math.round(1000 * Math.pow(10, (s.ficha || 0) / 10) * ez(s, "cost") * townScale(s));
  function lawyer(s) {
    if (!s.ficha) return false;
    const c = lawyerCost(s);
    if (s.clean < c) return false;
    s.clean -= c;
    s.ficha = Math.max(0, s.ficha - 10);
    note(s, "city", `O advogado limpou parte da sua ficha: agora ${s.ficha}%.`);
    return true;
  }
  // responde a Vó com a explicação k (0 ou 1); devolve o que aconteceu
  function surpriseAnswer(s, k) {
    if (!s.surprise) return null;
    const o = SURPRISE[s.surprise.opts[k]];
    s.surprise = null;
    if (o.kind === "bust") {
      if (s.cheat && s.cheat.noPolice) return { ...o, kind: "safe", res: o.res + " (Imune à polícia: escapou.)" };
      bust(s, "A Vó fez uma visita surpresa e descobriu tudo.", true);
    } else if (o.kind === "para") s.para = Math.max(s.para, 90);
    else {
      if (o.sta) s.sta = Math.min(100, s.sta + o.sta);
      if (o.bot) gainXp(s, "bot", XP_NEED.bot(s.attrs.bot) * 0.5);
    }
    return o;
  }
  // ---- encomendas
  function newOrder(s) {
    const best = bestSeed(s);
    const seed = Math.max(0, best - Math.floor(rand(s) * 3));
    const per = Math.max(1, Math.floor(SEEDS[seed].prod * prodMult(s)));
    const n = Math.max(3, Math.round(per * s.pots.length * (0.8 + rand(s) * 1.4)));
    const pay = Math.round(n * SEEDS[seed].sell * priceMult(s, 0) * (2 + rand(s)));
    const c = CLIENTS[Math.floor(rand(s) * CLIENTS.length)];
    s.orders.push({ id: ++s.orderN, emoji: c[0], who: c[1], seed, n, pay, until: s.time + R.orderTime });
    note(s, "order", `${c[1]} quer ${n} un de ${SEEDS[seed].name}.`);
  }
  function ordersTick(s, dt) {
    if (!s.orders) s.orders = [];
    for (let i = s.orders.length - 1; i >= 0; i--) {
      if (s.time > s.orders[i].until) { const o = s.orders.splice(i, 1)[0]; s.resp = Math.max(0, s.resp - 1); note(s, "order", `${o.who} cansou de esperar. −1 Respeito.`); }
    }
    if (s.away || (s.tut != null && s.tut < 99) || s.place < ORDERS_FROM) return;
    s.orderT = (s.orderT || 0) + dt;
    if (s.orderT >= R.orderEvery && s.orders.length < R.orderMax) { s.orderT = 0; newOrder(s); }
  }
  function deliver(s, id) {
    const i = s.orders.findIndex((o) => o.id === id);
    if (i < 0) return false;
    const o = s.orders[i];
    if (s.stock[o.seed] < o.n) return false;
    s.stock[o.seed] -= o.n;
    s.dirty += o.pay; s.runEarned += o.pay;
    s.resp += 2; s.para += 3;
    gainXp(s, "lab", Math.sqrt(o.n));
    s.orders.splice(i, 1);
    note(s, "order", `Entregou para ${o.who}: +$${Math.round(o.pay)}.`);
    checkBust(s);
    return true;
  }
  // ---- mudar de cidade (o jogo sem fim)
  const TOWNS_ON = false; // mudar de cidade: desligado até esta versão ficar redonda
  const canMoveTown = (s) => TOWNS_ON && s.place === PLACES.length - 1 && seedOk(s, SEEDS.length - 1);
  function moveTown(s) {
    if (!canMoveTown(s)) return 0;
    const gain = Math.max(1, legendFor(s.runEarned / townScale(s)));
    const town = (s.town || 0) + 1;
    note(s, "lenda", `Mudou para ${townName(town)}: produção ×${Math.pow(1.25, town).toFixed(2).replace(".", ",")} e +${gain} Lenda.`);
    reset(s, { legend: s.legend + gain, attrs: { ...s.attrs }, town });
    return gain;
  }

  function retire(s) {
    const gain = legendFor(s.runEarned / townScale(s));
    if (gain < 1) return 0;
    note(s, "lenda", `Passou o ponto: +${gain} Lenda.`);
    reset(s, { legend: s.legend + gain, attrs: { ...s.attrs } });
    return gain;
  }
  function reset(s, keep) {
    const persist = { time: s.time, rng: s.rng, log: s.log, busts: s.busts, timesArrested: s.timesArrested, resp: s.resp, xp: s.xp, cheat: s.cheat, easy: s.easy, warned: s.warned, town: s.town || 0, ficha: s.ficha || 0, fichaLenda: s.fichaLenda || 0 };
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
    const decay = s.para < R.paraCalm ? R.paraDecayLow : R.paraDecay;   // até 40% a cabeça esfria rápido
    s.para = Math.max(s.ficha || 0, s.para - decay * ez(s, "decay") * dt + (s.debt > 0 ? R.loanPara * dt : 0));
    // ficha limpa aos poucos: a cada 5 de Lenda ganhos depois da última batida
    while (s.ficha > 0 && s.legend >= s.fichaLenda + R.fichaLenda) {
      s.ficha = Math.max(0, s.ficha - 5); s.fichaLenda += R.fichaLenda;
      note(s, "lenda", `Sua fama limpou a ficha: a Paranoia agora pode cair até ${s.ficha}%.`);
    }
    growAll(s, dt * speed(s));
    for (let i = s.laundry.length - 1; i >= 0; i--) {
      if (s.time >= s.laundry[i].done) { s.clean += s.laundry[i].net; s.laundry.splice(i, 1); }
    }
    if (s.city && s.time >= s.city.end) finishCity(s);
    runFronts(s, dt);
    fiscalCheck(s, dt);
    ordersTick(s, dt);
    if (!s.away && !s.surprise && s.time > 600 && !(s.tut < 99)) {
      s.surpT += dt;
      if (s.surpT >= R.surpriseEvery) {
        s.surpT = 0;
        if (rand(s) < R.surpriseChance) {
          const a = Math.floor(rand(s) * SURPRISE.length);
          let b = Math.floor(rand(s) * (SURPRISE.length - 1)); if (b >= a) b++;
          s.surprise = { opts: [a, b], at: s.time };
        }
      }
    }
    if (s.ze) {
      s.zeT += dt;
      if (s.zeT >= R.zeEvery) {
        s.zeT = 0;
        const cd = s.saleCd; s.saleCd = 0;
        if (s.para + paraOf(s, 0) <= R.zeMaxPara) sell(s, 0, true);   // o Zé é cuidadoso: com a Paranoia alta, ele espera
        s.saleCd = Math.max(cd, 0);
      }
    }
    // batida periódica: a cada 5 min, com Paranoia acima de 80, 50% de chance
    s.raidT += dt;
    if (s.raidT >= R.raidEvery) {
      s.raidT = 0;
      const raid = R.raidChance * (1 - Math.min(0.6, fxSum(s, "guard") + s.attrs.seg * 0.005));
      if (!(s.cheat && s.cheat.noPolice) && s.para > R.raidAt && rand(s) < raid) bust(s, "A polícia fez uma ronda e achou o esconderijo.");
    }
    checkBust(s);
  }

  // Com o app fechado: avança em passos de 5 s (até 8 h).
  function offline(s, seconds) {
    const t = Math.min(seconds, R.offlineCap);
    s.away = true; // a Vó não aparece com o jogo fechado
    const before = { dirty: s.dirty, clean: s.clean, units: stockUnits(s), resp: s.resp };
    const busts = s.busts;
    let left = t;
    while (left > 0) { const d = Math.min(5, left); tick(s, d); left -= d; }
    s.away = false;
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
    BILL_MAX, TOWNS_ON, ORDERS_FROM, placeNeedsClean, HOME_PLACE, canPay, townScale, seedPrice, TOWNS, townName, townProd, canMoveTown, moveTown, deliver, newOrder, saleSta, placeCost, EASY, SURPRISE, surpriseAnswer, equipBlock, bestSeed, lawyer, lawyerCost, FRONTS, FRONT_MAX, frontLvl, frontCost, frontCap, frontOpen, buyFront,
    fiscalBribe, fiscalClose, fiscalRisk, countBills, billValue, marketFee, marketMult, reserve, level, legendMult, prodMult, speed, tapPower, priceMult, riskOf, paraOf, staCost, maxPots, potCost,
    equipCost, saleCooldown, stockUnits, stockValue, seedLocked, seedOk, incomePerSec, legendFor, lvl,
    xpNeed: (k, l) => XP_NEED[k](l),
  };
  if (typeof module !== "undefined") module.exports = api;
  else root.ECON = api;
})(this);
