# Greenhood Idle — repensando o projeto

> Substitui a direção "RPG online estilo The Crims/Habbo" do `GDD.md`.
> A arte (`ARTE.md`, sprites v2) continua valendo.
> Protótipo jogável: `prototype/idle/index.html` · simulação: `node prototype/idle/sim.js`.

## 1. Avaliação sincera

**O RPG online (GDD original) é o projeto errado para uma pessoa só.**
- Precisa de servidor autoritativo, contas, moderação de chat, anti-trapaça e comunidade ativa
  desde o primeiro dia. Jogo social sem gente vazia, e um mundo vazio mata o jogo.
- Jogos de crime em navegador (The Crims, Torn) sobrevivem com comunidades antigas. Começar um do
  zero hoje é muito difícil.

**Idle/clicker é um formato melhor:** dá para fazer sozinho, joga-se offline, as sessões são curtas
no celular e o modelo de receita é conhecido (anúncio recompensado + compras pequenas).

**Mas o tema "maconha idle" é um nicho pequeno e já ocupado.**
- Já existem *Hempire*, *Weed Inc*, *Bud Farm* e cópias. Pelos dados do Sensor Tower, nenhum faz
  números grandes hoje: são poucos milhares de downloads por trimestre nos EUA.
- O Google Play proíbe app que facilite venda de maconha. Jogo que *mostra* drogas não é proibido,
  mas sobe a classificação (16+). Isso reduz o público e os anúncios que pagam bem.

**Recomendação:** manter o humor de "crime das plantas" e **tirar as referências diretas a
drogas**. Plantas absurdas e inofensivas (Alface Mística, Mandrágora, Fruto do Éden), polícia,
calor e batidas continuam. Assim o jogo cabe em 12+, fica diferente dos jogos de maconha e mantém
a graça. Já troquei os nomes: Ayahuasca → Cipó Enrolado, San Pedro → Cacto Cabeludo,
Esporos Especiais → Cogumelo Saltitante, Carolina Reaper → Pimenta do Capeta.

## 2. O que deixa este idle diferente

A maioria dos idles não tem risco: o número só sobe. Aqui o risco é o centro do jogo.

1. **Tocar para crescer.** Cada toque rega todos os vasos. Equipamentos fazem crescer sozinho.
2. **Vender é apostar.** Quatro níveis: Discreto (×1, vende 25%), Normal (×1,5), Ousado (×2,2) e
   All-in (×3,2, vende tudo). Cada venda esquenta o **Calor**, com variação aleatória. O calor
   esfria com o tempo.
3. **Batida = prestígio forçado.** Com calor em 100%, a polícia leva tudo. Esse era o wipe
   punitivo do protótipo web; agora ele vira **Lenda**: você recomeça, mas mais famoso.
4. **Passar o ponto = prestígio por escolha.** Dá a Lenda inteira; a batida dá só metade.
   Arriscar acelera, mas pode custar caro.
5. **Progressão visual** da gambiarra ao high-tech: lata de tinta → vaso de barro → bancada →
   rack hidropônico; garagem → porão → galpão → bunker (ver `ARTE.md`).

## 3. Economia (testada por simulação)

| Item | Regra |
|---|---|
| Sementes (18) | valor ×3 e tempo de crescimento ×2 por nível; liberar custa ×15 |
| Equipamentos (9) | níveis com custo ×1,13 a ×1,27; força do toque, crescimento automático, multiplicadores, esfriar o calor |
| Esconderijos (4) | 3, 6, 12 e 24 vasos |
| Zé | vende sozinho no Discreto a cada 8 s, inclusive com o app fechado |
| Lenda | pontos = raiz cúbica(ganho da rodada / 10 mi); bônus = 1 + 0,3 × Lenda^0,6 |
| Offline | até 8 h de produção automática |

Resultados de `node prototype/idle/sim.js` depois de três rodadas de ajuste:

| Perfil | Resultado |
|---|---|
| Ativo (5 toques/s, sem parar) | 1ª Lenda aos ~10 min; 11 de 18 sementes em 6 h |
| Arriscado (vende Ousado/All-in) | progride mais rápido no começo, mas foi preso 7 vezes em 3 h |
| Casual (10 min a cada 3 h) | 12 de 18 sementes em 2 dias |
| Idle puro (só toca no 1º minuto) | progride sozinho, devagar: 1ª Lenda em ~1 h |

O que a simulação pegou e foi corrigido:
- **A Lenda disparava até o infinito.** O bônus multiplicava crescimento e valor ao mesmo tempo.
  Agora vale só uma vez e tem retorno decrescente.
- **O jogo inteiro acabava em 8 minutos.** As sementes ficaram mais caras (×15 por nível).
- **O jogador idle travava depois do prestígio.** Agora ele recomeça com um regador.

Ainda falta: equilibrar o fim de jogo (sementes 12 a 18) e decidir se arriscar deve compensar
mais. Hoje o jogador cauteloso e o arriscado terminam parecidos.

## 4. Tecnologia: Android nativo, Godot ou web?

| Opção | A favor | Contra |
|---|---|---|
| **Kotlin nativo (Android)** | app leve, melhor integração com o Android | só Android (iOS seria outro projeto), mais código para animação e pixel art, teste mais lento |
| **Godot 4** | ótimo para pixel art, exporta Android, iOS e PC; o Pixelwright exporta direto | APK maior (~30 MB+), plugins de anúncio e compra são da comunidade, interface de loja e listas dá mais trabalho |
| **Web (TypeScript) + Capacitor** | o protótipo já é isso; mesmo código vira Android, iOS e site; testa por link; plugins maduros de AdMob e compras (RevenueCat); dá para publicar em portais web de jogos, onde idle vai bem | performance menor para cenas pesadas (não é o caso de um idle) |

**Recomendação: web + Capacitor.** Um idle é 80% interface (listas, botões, números) e 20%
animação, e a web é a forma mais rápida de fazer isso. Você testa no celular por um link, como
este protótipo, e vira APK no Google Play sem reescrever. "Direto para Android" não exige código
nativo: o Capacitor gera um app Android de verdade.

O projeto Godot (M0) fica como referência. Se no futuro o jogo ganhar uma parte de exploração
(andar pela cidade), dá para voltar a ele.

## 5. Próximos passos sugeridos

1. **Jogar o protótipo** por uns dias e anotar o que é chato ou bom. É a única forma de saber se
   o "loop" prende.
2. Estruturar o projeto web: TypeScript + Vite, salvamento com versão, testes da economia.
3. Conteúdo: plantas compactas nos racks, NPCs (Zé, Vó como tutorial), sons, eventos ("Feira de
   sementes", "Operação policial").
4. Monetização ética: anúncio recompensado opcional (2× produção por 4 h, esfriar o calor na
   hora) e um passe sem anúncios. Nada de pagar para não ser preso.
5. Capacitor → APK de teste interno no Google Play → teste fechado com amigos.
