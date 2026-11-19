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

## 2. O jogo completo, adaptado para idle (v2)

Todos os sistemas do GDD original estão no protótipo, com os números do GDD:

| Sistema do GDD | Como ficou no idle |
|---|---|
| Grana suja e limpa | Venda dá grana suja (paga sementes e vasos). Lavagem vira grana limpa (equipamentos, imóveis, cidade, Zé). |
| Paranoia 👁️ | Barra grande no topo, com marcas em 60% e 80%. Cai sozinha (−1 a cada 4 s). Em 60% a Estamina custa o dobro; acima de 80% a polícia faz **rondas** a cada 5 min (50% de chance de batida); em 100% é batida na hora. |
| Estamina ⚡ | Gasta na cidade e para mendigar; recupera +1 a cada 20 s, com Café, Energético, Bar e Vó. |
| 18 sementes | Preço, venda, produção, tempo, Botânica e equipamentos exigidos iguais ao GDD. O replantio é automático e paga a semente com grana suja. |
| 6 estágios por planta | Semente na terra → broto → muda → jovem → crescida → adulta, com desenho próprio de cada planta. |
| 18 equipamentos | Preços e bônus do GDD. O 1º nível libera sementes, os seguintes repetem o bônus (custo ×2,4). Alguns têm efeito extra: velocidade, toque, menos Paranoia, proteção contra batida. |
| 13 imóveis | Do Quartinho (2 vasos) ao Bunker Militar (40 vasos). A Estação Espacial saiu: o passo seguinte vai ser mudar de cidade. O visual muda: gambiarra → profissional → high-tech. |
| 5 níveis de venda | Por porcentagem do estoque: Discreto 5%, Normal 15%, Ousado 35%, Agressivo 70% e All-in 100% (maior risco). Cada nível tem Paranoia, chance de flagrante e bônus de preço. Uma venda por vez (espera de 20 s a 3 s). |
| Flagrante | Perde a mercadoria, paga multa de 5–25% da grana suja, −20⚡, +15 Paranoia. |
| Batida | Perde **tudo**: grana suja e limpa, estoque, equipamentos e o esconderijo (volta ao Quartinho). Mantém atributos (Botânica, Lábia, Furtividade, Segurança), Respeito e Lenda, e ganha metade da Lenda da rodada. Câmeras, bunker e Segurança diminuem a chance de a ronda te achar. |
| Lavagem | Laranjas, NFTs, Crypto e Consultoria, com taxa, tempo, Paranoia e Lábia do GDD. Vários processos ao mesmo tempo. |
| Cidade | Café, Energético, Bar, Biblioteca, Academia, Beco, Praça, Spa e Fliperama, com tempo real, uma por vez. |
| Atributos | Botânica, Lábia, Furtividade e Segurança sobem por experiência (colher, vender, arriscar) e com a cidade. Ficam com você ao passar o ponto. |
| Avó, Agiota, Mendigar | Na aba Cidade, para recomeçar depois de uma batida. |
| Respeito e Nível | Sobem colhendo e vendendo; cada nível dá +1% no preço. |
| Lenda (prestígio) | (log10(vendido) − 4)², +10% de preço por ponto. Passar o ponto dá tudo; batida dá metade. |
| Zé | Vende sozinho no Discreto a cada 20 s, inclusive com o app fechado. |
| Offline | Até 8 h: plantas, replantio, Zé, lavagem e Paranoia continuam. |

Não entraram (precisam de servidor): ranking, cartéis, chat, visitas e trocas.

## 3. Economia (testada por simulação)

`node prototype/idle/sim.js` joga com um robô que usa todos os sistemas (vende pelo risco aceito,
lava dinheiro, vai à cidade e compra os equipamentos exigidos):

| Perfil | Resultado |
|---|---|
| Ativo cauteloso (8 h) | chega à semente 18 sem nenhuma batida |
| Ativo arriscado (8 h) | ~33 batidas e ~64 flagrantes; mais Lenda que antes, mas preso sem parar |
| Casual (15 min a cada 4 h, 5 dias) | semente 18 |
| Idle (só joga 2 min, 24 h) | semente 18 em ~19 h |

O que a simulação pegou e foi corrigido nesta versão:
- **Batidas a cada 10 minutos.** Ações que levariam a Paranoia a 100% agora ficam bloqueadas (só a venda é aposta).
- **Botânica sem freio.** Os atributos agora sobem por experiência, com curva mais longa.
- **A Lenda disparava.** Agora cresce de forma logarítmica.
- **A espera entre vendas era longa demais no começo.** Caiu de 30 s para 20 s.

Ainda a ajustar: o jogador que fica ativo por 8 horas seguidas termina o jogo; a Botânica
continua crescendo depois da semente 18 (falta um uso para ela no fim de jogo).

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
