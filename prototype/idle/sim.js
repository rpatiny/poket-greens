// Simula jogadores para testar o ritmo da economia.
//   node prototype/idle/sim.js
const E = require("./econ.js");

const fmt = (n) => {
  if (n < 1000) return n.toFixed(0);
  const u = ["K", "M", "B", "T", "Qa", "Qi"];
  let i = -1;
  while (n >= 1000 && i < u.length - 1) { n /= 1000; i++; }
  return n.toFixed(1) + u[i];
};
const hms = (t) => {
  const h = Math.floor(t / 3600), m = Math.floor((t % 3600) / 60), s = Math.floor(t % 60);
  return h ? `${h}h${String(m).padStart(2, "0")}` : `${m}m${String(s).padStart(2, "0")}s`;
};

// Compra o item mais barato disponível (com prioridade para semente nova e Zé)
function shop(s) {
  let bought = true, n = 0;
  while (bought && n++ < 50) {
    bought = false;
    if (E.buySeed(s)) { bought = true; continue; }
    if (E.hireZe(s)) { bought = true; continue; }
    const opts = [];
    if (s.place + 1 < E.PLACES.length) opts.push([E.PLACES[s.place + 1].cost, () => E.buyPlace(s)]);
    if (s.pots.length < E.maxPots(s)) opts.push([E.potCost(s), () => E.buyPot(s)]);
    for (const u of E.UPGRADES) opts.push([E.upgradeCost(s, u), () => E.buyUpgrade(s, u.id)]);
    opts.sort((a, b) => a[0] - b[0]);
    // guarda para a próxima semente se ela estiver perto
    const next = E.SEEDS[s.unlocked];
    if (next && s.cash > next.unlock * 0.5 && opts[0][0] > next.unlock * 0.1) continue;
    if (opts.length && s.cash >= opts[0][0]) { opts[0][1](); bought = true; }
  }
}

function run(name, { taps, activeFor = Infinity, session = null, hours = 6, greed = 1, retireAt = 1.0 }) {
  const s = E.newState();
  const ms = [];
  let lastSeed = 1, lastPlace = 0;
  const end = hours * 3600;
  let t = 0;
  while (t < end) {
    const playing = session ? (t % session.every) < session.len : true;
    if (!playing) {
      // pula até a próxima sessão (app fechado)
      const skip = session.every - (t % session.every);
      E.offline(s, skip);
      s.time += skip; t += skip;
      shop(s);
      continue;
    }
    const tapping = t < activeFor;
    for (let k = 0; k < (tapping ? taps : 0); k++) E.tap(s);
    E.tick(s, 1);
    // venda: o jogador ativo arrisca até um limite de calor
    if (tapping || !s.ze) {
      const lvl = s.heat < 30 * greed ? 2 : s.heat < 55 * greed ? 1 : 0;
      if (s.heat < 75) E.sell(s, lvl);
    }
    shop(s);
    // aposenta quando dobraria a Lenda (ou na primeira vez que der 3+ pontos)
    const gain = E.legendFor(s.runEarned);
    if (gain >= Math.max(1, s.legend * retireAt)) { E.retire(s); ms.push([t, `-- aposentou: Lenda agora ${s.legend}`]); lastSeed = 1; lastPlace = 0; }
    if (s.unlocked > lastSeed) { ms.push([t, `semente ${s.unlocked}: ${E.SEEDS[s.unlocked - 1].name}`]); lastSeed = s.unlocked; }
    if (s.place > lastPlace) { ms.push([t, `mudou para ${E.PLACES[s.place].name}`]); lastPlace = s.place; }
    t += 1;
  }
  console.log(`\n=== ${name} (${hours}h) ===`);
  for (const [tt, m] of ms.slice(0, 45)) console.log(`  ${hms(tt).padStart(7)}  ${m}`);
  const busts = s.log.filter((l) => l.ev === "batida");
  for (const l of busts.slice(0, 5)) console.log(`  ${hms(l.t).padStart(7)}  PRESO (batida) +${l.gain} Lenda`);
  console.log(`  fim: Lenda ${s.legend}, dinheiro ${fmt(s.cash)}, semente ${s.unlocked}/18, vasos ${s.pots.length}, renda auto ${fmt(E.incomePerSec(s))}/s, batidas ${s.busts}`);
}

run("Ativo: 5 toques/s, joga sem parar", { taps: 5, hours: 6 });
run("Ativo arriscado: vende Ousado/All-in", { taps: 5, hours: 3, greed: 2.2 });
run("Casual: 10 min a cada 3h, toca nos 10 min", { taps: 4, session: { every: 3 * 3600, len: 600 }, hours: 48 });
run("Idle puro: toca só no 1º minuto", { taps: 5, activeFor: 60, hours: 12 });
