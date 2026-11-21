// Simula jogadores para testar o ritmo da economia.
//   node prototype/idle/sim.js
const E = require("./econ.js");

const fmt = (n) => {
  if (Math.abs(n) < 1000) return n.toFixed(0);
  const u = ["K", "M", "B", "T", "Qa", "Qi"];
  let i = -1;
  while (Math.abs(n) >= 1000 && i < u.length - 1) { n /= 1000; i++; }
  return n.toFixed(1) + u[i];
};
const hms = (t) => {
  const d = Math.floor(t / 86400), h = Math.floor((t % 86400) / 3600), m = Math.floor((t % 3600) / 60);
  return d ? `${d}d${String(h).padStart(2, "0")}h` : h ? `${h}h${String(m).padStart(2, "0")}` : `${m}m${String(Math.floor(t % 60)).padStart(2, "0")}s`;
};

function bestSeed(s) {
  for (let i = E.SEEDS.length - 1; i >= 0; i--) if (E.seedOk(s, i)) return i;
  return 0;
}
function nextSeedNeeds(s) {
  const i = bestSeed(s) + 1;
  if (i >= E.SEEDS.length) return [];
  return E.SEEDS[i].req.filter((r) => !E.lvl(s, r));
}

function brain(s, p) {
  // 1) semente: troca para a melhor se der para plantar em todos os vasos
  const b = bestSeed(s);
  if (b !== s.seed && s.dirty >= E.SEEDS[b].price * s.pots.length) E.chooseSeed(s, b);
  // 2) venda: o maior nível que não estoura a Paranoia nem passa do risco aceito
  const needWash = s.dirty > (E.SEEDS[s.seed].price * s.pots.length * 4 + 20) * 3 && s.laundry.length < 3;
  if (s.saleCd <= 0 && E.stockUnits(s) > 0 && !(needWash && s.para > 35)) {
    let pick = -1;
    for (let l = E.SALES.length - 1; l >= 0; l--) {
      if (E.riskOf(s, l) > p.risk) continue;
      if (s.para + E.paraOf(s, l) > p.paraLimit) continue;
      if (s.sta < E.saleSta(s, l) + 5) continue;
      pick = l; break;
    }
    if (pick >= 0) E.sell(s, pick);
  }
  // 3) vasos com grana suja
  while (s.pots.length < E.maxPots(s) && s.dirty > E.potCost(s) * 2 && E.buyPot(s));
  // 4) lavagem: guarda o suficiente para replantar
  const reserve = E.SEEDS[s.seed].price * s.pots.length * 4 + 20;
  if (s.dirty > reserve + 50 && s.laundry.length < 3) {
    const m = s.attrs.lab >= 10 ? "consultoria" : s.attrs.lab >= 5 ? "crypto" : "laranjas";
    const frac = (s.dirty - reserve) / s.dirty;
    if (s.para + 8 < p.paraLimit - 10) E.launder(s, m, frac);
  }
  // 5) compras com grana limpa
  let guard = 0;
  while (guard++ < 20) {
    if (!s.ze && s.clean >= E.R.zeCost && s.time > 120) { E.hireZe(s); continue; }
    const need = nextSeedNeeds(s);
    if (need.length) {
      const e = E.EQUIP.find((x) => x.id === need[0]);
      if (E.buyEquip(s, e.id)) continue;
      if (s.clean < E.equipCost(s, e)) break; // juntando para o equipamento exigido
    }
    if (s.pots.length >= E.maxPots(s) && E.PLACES[s.place + 1] && E.buyPlace(s)) continue;
    // fachadas: compra/sobe a mais barata se custar até 25% da grana limpa
    const fr = E.FRONTS.filter((f) => E.frontLvl(s, f.id) < E.FRONT_MAX).map((f) => [E.frontCost(s, f), f]).sort((x, y) => x[0] - y[0])[0];
    if (fr && fr[0] <= s.clean * 0.25 && E.buyFront(s, fr[1].id)) continue;
    // equipamento mais barato que ainda não estoura o orçamento para o próximo imóvel
    const opts = E.EQUIP.filter((e) => !E.equipBlock(s, e)).map((e) => [E.equipCost(s, e), e]).sort((a, b) => a[0] - b[0]);
    if (!opts.length) break;
    const nextPlace = E.PLACES[s.place + 1];
    const budget = nextPlace ? s.clean - E.placeCost(s) * 0.3 : s.clean;
    if (opts[0][0] <= budget && E.buyEquip(s, opts[0][1].id)) continue;
    break;
  }
  // encomendas: entrega o que der
  for (const o of [...(s.orders || [])]) if (s.stock[o.seed] >= o.n) E.deliver(s, o.id);
  // fim do jogo: muda de cidade
  if (p.towns && E.canMoveTown(s)) E.moveTown(s);
  // Vó: escolhe uma das duas explicações no chute
  if (s.surprise) {   // quem já viu a Vó aprende: acerta 80% das vezes
    const safe = E.SURPRISE[s.surprise.opts[0]].kind === "bust" ? 1 : 0;
    E.surpriseAnswer(s, Math.random() < 0.8 ? safe : 1 - safe);
  }
  // fiscal: suborna se der, senão fecha
  if (s.fiscal) { if (!E.fiscalBribe(s)) E.fiscalClose(s); }
  // maquininha (só quem joga ativo)
  if (p.bills && s.sta > 50) for (let k = 0; k < 3; k++) E.countBills(s, 2);
  // 6) cidade: Spa se a Paranoia apertar; senão treina
  if (!s.city) {
    // com a Paranoia alta, prefere esperar baixar; só vai ao Fliperama (curto, dá pra apressar) se estiver muito alta
    if (s.para > 75 && s.clean > 15 && !p.session) E.startCity(s, "fliperama");
    // treina só de vez em quando (um jogador de verdade não fica o tempo todo fora de casa)
    else if (s.sta > 60 && s.clean > 50 && (s.time % 1800) < 400) E.startCity(s, ["biblioteca", "praca", "biblioteca", s.para < 40 ? "beco" : "biblioteca", "academia"][Math.floor(s.time / 1800) % 5]);
    else if (s.sta < 30 && s.clean > 20) E.startCity(s, "bar");
  }
  // 7) começo: mendiga e visita a Vó
  if (s.dirty < 10) E.beg(s);
  if (s.para < 50) E.visitAvo(s);
}

function run(name, p) {
  const s = E.newState(p.seed || 7);
  if (p.easy) s.easy = true;
  const ms = [];
  let lastSeed = bestSeed(s), lastPlace = 0, lastFlag = 0, lastTown = 0;
  const end = p.hours * 3600;
  let t = 0;
  while (t < end) {
    const playing = p.session ? (t % p.session.every) < p.session.len : true;
    if (!playing) {
      const skip = p.session.every - (t % p.session.every);
      const r = E.offline(s, skip);
      if (r.busted) ms.push([t, "PRESO com o app fechado"]);
      t += skip;
      continue;
    }
    for (let k = 0; k < p.taps && t < (p.tapFor ?? Infinity); k++) (s.city ? E.cityTap(s) : E.tap(s));
    E.tick(s, 1);
    brain(s, p);
    const gain = E.legendFor(s.runEarned);
    if (gain >= Math.max(1, s.legend * p.retireAt)) { E.retire(s); ms.push([t, `-- passou o ponto: Lenda ${s.legend}`]); lastSeed = 0; lastPlace = 0; }
    const bs = bestSeed(s);
    if (bs > lastSeed) { ms.push([t, `semente ${bs + 1}: ${E.SEEDS[bs].name} (Bot ${s.attrs.bot})`]); lastSeed = bs; }
    if ((s.town || 0) > (lastTown || 0)) { ms.push([t, `== CIDADE NOVA: ${E.townName(s.town)} (Lenda ${s.legend})`]); lastTown = s.town; lastSeed = 0; lastPlace = 0; }
    if (s.place > lastPlace) { ms.push([t, `imóvel: ${E.PLACES[s.place].name} (${E.PLACES[s.place].pots} vasos)`]); lastPlace = s.place; }
    if (s.timesArrested > lastFlag) { lastFlag = s.timesArrested; }
    if (s.lastBust) { ms.push([t, `BATIDA: ${s.lastBust.why} +${s.lastBust.gain} Lenda`]); s.lastBust = null; lastSeed = 0; lastPlace = 0; }
    t += 1;
  }
  console.log(`\n=== ${name} (${p.hours}h) ===`);
  const show = !p.all && ms.length > 60 ? ms.slice(0, 40).concat([[0, "..."]], ms.slice(-15)) : ms;
  for (const [tt, m] of show) console.log(`  ${hms(tt).padStart(7)}  ${m}`);
  console.log(`  fim: Lenda ${s.legend} · suja ${fmt(s.dirty)} · limpa ${fmt(s.clean)} · semente ${bestSeed(s) + 1}/18 · ${E.PLACES[s.place].name} · ` +
    `Bot ${s.attrs.bot} Láb ${s.attrs.lab} Fur ${s.attrs.fur} Seg ${s.attrs.seg} · nível ${E.level(s)} · flagrantes ${s.timesArrested} · batidas ${s.busts}`);
}

const base = { taps: 5, risk: 0.05, paraLimit: 70, retireAt: 1, bills: true };
if (process.env.PACE) {
  // ritmo da progressão: sem passar o ponto, mostra quando cada semente e cada imóvel chegam
  run("RITMO normal (sem passar o ponto)", { ...base, retireAt: Infinity, hours: 24 * 7, all: true });
  run("RITMO fácil (sem passar o ponto)", { ...base, retireAt: Infinity, hours: 48, easy: true, all: true });
  run("RITMO casual: 15 min a cada 4h (sem passar o ponto)", { ...base, taps: 3, session: { every: 4 * 3600, len: 900 }, retireAt: Infinity, hours: 24 * 14, all: true });
  process.exit(0);
}
run("Ativo cauteloso", { ...base, hours: 8 });
run("Ativo arriscado", { ...base, risk: 0.3, paraLimit: 95, hours: 8 });
run("Casual: 15 min a cada 4h", { ...base, taps: 3, session: { every: 4 * 3600, len: 900 }, hours: 24 * 10 });
run("Idle: toca só nos 2 primeiros min", { ...base, tapFor: 120, hours: 24 });
run("MODO FÁCIL · ativo cauteloso (2h)", { ...base, easy: true, hours: 2 });
