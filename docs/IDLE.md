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
| Paranoia 👁️ | Barra grande no topo, com marcas em 60% e 80%. Cai sozinha, devagar (−1 a cada 8 s). Em 60% a Estamina custa o dobro; acima de 80% a polícia faz **rondas** a cada 5 min (50% de chance de batida); em 100% é batida na hora. |
| Estamina ⚡ | Gasta na cidade e para mendigar; recupera +1 a cada 20 s, com Café, Energético, Bar e Vó. |
| 18 sementes | Preço, venda, produção, tempo, Botânica e equipamentos exigidos iguais ao GDD. O replantio é automático e paga a semente com grana suja. |
| 6 estágios por planta | Semente na terra → broto → muda → jovem → crescida → adulta, com desenho próprio de cada planta. |
| 18 equipamentos | Preços e bônus do GDD. O 1º nível libera sementes, os seguintes repetem o bônus (custo ×2,4). Alguns têm efeito extra: velocidade, toque, menos Paranoia, proteção contra batida. |
| 13 imóveis | Do Armário Grow (1 vaso numa cadeira, dentro do guarda-roupa) ao Bunker Desativado (40 plantas). Ordem: Armário, Quartinho, Garagem, Porão, Sobrado na Favela, Terreno, Container, Galpão, Sítio, Fazenda, Mina, Praia Particular e Bunker. O Quartinho é o 2º ($100, 3 vasos). Do Terreno em diante as plantas vão para calhas de hidroponia, que cabem mais plantas no mesmo espaço. A Estação Espacial saiu: o passo seguinte vai ser mudar de cidade. O visual muda: gambiarra → profissional → high-tech. |
| 5 níveis de venda | Por porcentagem do estoque: Discreto 5%, Normal 15%, Ousado 35%, Agressivo 70% e All-in 100% (maior risco). Cada nível tem Paranoia, chance de flagrante e bônus de preço. Uma venda por vez (espera de 20 s a 3 s). Cada venda gasta Estamina proporcional ao tamanho: 1, 3, 6, 10 e 16⚡ (o dobro com Paranoia alta). As vendas do Zé não gastam a sua. |
| Ficha na polícia | Cada batida sobe a ficha em 10% (até 50%): a Paranoia nunca cai abaixo dela, então quem já foi preso joga com menos folga. A ficha baixa 5% a cada 5 de Lenda ganhos depois da batida, ou 10% na hora com o advogado (Cidade, grana limpa, 10× mais caro a cada 10% de ficha). Aparece como uma faixa listrada no começo da barra de Paranoia. |
| Equipamentos por lugar | 14 equipamentos (a lâmpada com alumínio, a mini estufa, a osmose reversa e o kit bunker saíram do jogo). Até o nível 5, cada nível custa 3× o anterior. Cada um tem um lugar mínimo: Armário só a garrafa PET; Quartinho até o termômetro (tesoura, ventilador, termômetro); Garagem até o pH (adubo, pH); Porão: drone, filtro e LED; Sobrado: câmeras; Container: hidroponia e CO2; Galpão: IA; Bunker: laboratório. Ao se mudar, os equipamentos ficam para trás e são comprados de novo; drone, hidroponia e IA são compra única e vão com você. |
| Zé cuidadoso | O Zé só vende se a Paranoia ficar até 60%. |
| Visita surpresa da Vó | Com o jogo aberto, a cada 15 min há 6% de chance de a Vó aparecer e descobrir tudo (em média uma vez a cada ~4 h jogando). Você escolhe uma de duas explicações, sorteadas de 10: 5 levam à cadeia (batida), 4 passam (algumas dão energia ou Botânica) e 1 deixa a Paranoia em 90%. Vale para todo mundo, até para quem joga com cuidado. |
| Modo fácil | Escolhido ao começar (ou no Perfil, recomeçando). Cresce 3× mais rápido, vende 2× mais caro, tudo custa 30%, atributos sobem 3× mais rápido, a Paranoia cai 2× mais rápido e a espera entre vendas cai pela metade. Na simulação, um jogador ativo zera em ~1h35. Aparece a etiqueta MODO FÁCIL na cena. |
| Ritmo da progressão | Cada semente pede 1 ponto a mais de Botânica (Alface 1, Hortelã 2, Manjericão 3… até 12, 14, 16, 18, 20, 23, 26 e 30). Os imóveis custam ~5× o anterior ($150, $900, $5 mil, $25 mil, $120 mil, $600 mil, $3 mi, $15 mi, $70 mi, $350 mi, $1,5 bi e $7 bi). O vaso novo custa 6% do lugar onde você está e sobe 25% a cada vaso comprado ali, então encher o cômodo custa parecido em todo lugar. Na simulação sem passar o ponto, um jogador ativo ganha uma semente nova a cada 10–40 min e chega à semente 18 em ~6 h (no modo fácil, em ~1 h). |
| História de abertura | Em estilo RPG de bolso (caixa de diálogo com retrato, texto letra por letra, ▼ para continuar). No seu quarto, a Vó Dita traz uma sementinha que pegou no quintal da Dona Cleide, a vizinha fofoqueira, e pede mudinhas. No armário vazio, a primeira ação é procurar um vaso (acha uma lata de tinta vazia) e plantar a sementinha; aí você rega tocando na planta. Ele pensa que o filho da Dona Cleide já foi preso, agradece a Vó e promete uma mudinha. Na primeira colheita a planta multiplica, a Vó liga cobrando as mudinhas e o jogo de verdade começa ($20 e tudo liberado). Dá para pular a história. |
| Encomendas | Começam no Sobrado na Favela (antes não tem freguesia). A cada 3 min chega um pedido (até 3 abertos): um cliente da vizinhança (Seu Jorge do bar, Tia do bolo, DJ da festa, Irmã Lurdes...) quer N unidades de uma planta, com prazo de 10 min, e paga 2–3× a venda comum, mais +2 Respeito e um pouco de Lábia. Entregar dá só +3 Paranoia. Se o prazo vence, −1 Respeito. Ficam no topo da aba Estufa. Em metade das entregas o neto comenta na caixa de diálogo (uma fala do cliente, como "A Tia do bolo me deu uma fatia de brinde. De que será que é esse bolo...?", ou uma fala geral); some sozinha em 6 s. |
| Mudar de cidade (sem fim) | **Desligado por enquanto** (`TOWNS_ON = false` em econ.js), até esta versão ficar redonda. Quando ligado: no Bunker, com a última semente liberada, você se muda para outra cidade (Vila Esperança → Baixada Verde → Serra Alta → Porto das Águas → Capital → Litoral Sul → Metrópole → Metrópole 2, 3...). Recomeça do Armário com atributos, Lenda e a cidade nova: lá tudo vale e custa 10× mais, as sementes pedem +6 de Botânica, a polícia é 10% mais esperta por cidade e a produção ganha ×1,25 para sempre. A Lenda é calculada sobre o que você ganhou em relação ao tamanho da cidade. Na simulação, a 1ª mudança vem com ~7 h de jogo ativo e cada cidade seguinte leva de 3 a 9 h, sem disparar. Os números passam de "dec" para aa, ab, ac... |
| Dinheiro da Vó e esmola | São grana limpa. Semente e vaso aceitam grana limpa quando a suja não dá, então ninguém fica preso depois de uma batida. |
| Experiência do começo (v3) | Armário com 2 vasos; tesoura e termômetro já cabem nele; o Quartinho (sua casa) aceita grana suja, só sair de casa pede grana limpa. Abaixo de 40% a Paranoia cai 1 a cada 3 s (o Discreto não acumula). A primeira batida é só um aviso: a Dona Cleide ameaça contar tudo pra Vó, nada se perde (a visita surpresa da Vó continua sendo batida de verdade). O neto ganha nome no começo e pensa alto os próximos objetivos e dicas (cada um uma vez, com botão "Ver"), inclusive a dica de 1 min parado. Clientes aparecem na caixa de diálogo quando chega encomenda. |
| Celular (v3) | Câmera com zoom no cômodo (🔍 alterna com a maquete inteira), cena até 55% da altura da tela, barra do topo compacta, botões de venda com o essencial, planta pula ao regar e ao mudar de estágio (com gotinhas e brilho), vibração (liga/desliga no Perfil), loja e sementes enxutas (o resto em "Ver todos"), lavagem numa barra só. Modo master escondido: 7 toques no "Nível" ou #master. |
| Sons (v3) | Efeitos 8-bit gerados na hora pelo navegador (Web Audio), sem nenhum arquivo: regar (gotinha), colher (arpejo), planta mudando de estágio (plim), vender (ka-ching), comprar (sininho), maquininha (notas que sobem com o combo), atributo subindo (vinheta), cliente chegando e visita da Vó (campainha), fiscal, flagrante, aviso da Dona Cleide (alarme), batida (sirene) e os bipinhos das falas (mais agudo para a Vó). Liga/desliga no Perfil. Amostra: `docs/sons-amostra.wav`. |
| Lucro das plantas (v3) | Venda e preço da semente pela metade da tabela do GDD (arredondados): o lucro de cada colheita caiu pela metade e cada semente continua rendendo mais que a anterior. (Cortar só a venda deixava a Mandrágora pior que a Trufa e o começo 5x mais lento.) |
| Ritmo mais lento (v3) | Botânica sobe mais devagar (XP por nível 32 × nível^1,9, antes 20 × nível^1,8). Imóveis 2,5× mais caros da Garagem em diante ($2.250, $12,5 mil, $62,5 mil, $300 mil, $1,5 mi, $7,5 mi, $37,5 mi, $175 mi, $875 mi, $3,75 bi e $17,5 bi) e o Quartinho 1,5× ($225). Simulação de jogador ativo: uma semente ou um imóvel novo a cada 15–70 min, alternando, Bunker com ~7h30 (antes ~4h40); o casual ainda zera em ~5 dias. |
| Vasos mais caros (v3) | O vaso novo custa 12% do lugar onde você está (mínimo $60) e sobe 35% a cada vaso comprado ali (antes 6%, mínimo $20 e +25%). O 2º vaso do Armário custa $60; encher o Bunker custa ~$115 bi (6,5× o Bunker). |
| Começo mais caro (v3) | Vaso: 15% do lugar, mínimo $150, +35% a cada vaso ali. Imóveis: Quartinho $600, Garagem $3.150, Porão $17,5 mil, Sobrado $87,5 mil, Terreno $420 mil, Container $2,1 mi, Galpão $10,5 mi, Sítio $52,5 mi, Fazenda $245 mi, Mina $1,2 bi, Praia $5,25 bi, Bunker $24,5 bi. Simulação ativa: Quartinho com ~26 min, Garagem com ~48 min. |
| Flagrante | Perde a mercadoria, paga multa de 5–25% da grana suja, −20⚡, +15 Paranoia. |
| Batida | Perde **tudo**: grana suja e limpa, estoque, equipamentos e o esconderijo (volta ao Armário, com um vaso só). Mantém atributos (Botânica, Lábia, Furtividade, Segurança), Respeito e Lenda, e ganha metade da Lenda da rodada. Câmeras, bunker e Segurança diminuem a chance de a ronda te achar. |
| Lavagem | Quatro jeitos, todos respeitando uma **reserva para replantar** (3 replantios de todos os vasos). **Fachadas**: 7 negócios (Lava-jato do Primo → Time de Futebol) que lavam sozinhos, até com o jogo fechado; nível até 10, cada nível custa 2,5× e lava 1,7×; taxa de 15% a 10%; +0,4 Paranoia/min por fachada lavando. **Fiscal da Receita**: a cada 7 min, 35% de chance de aparecer na maior fachada; você suborna (8 min de lavagem dela, menos com Lábia), fecha por 15 min ou tenta enrolar (50% + Lábia; se der errado, multa de 30% da grana limpa e +20 Paranoia). Sem resposta em 2 min, ela fecha sozinha. **Maquininha de contar notas**: toque rápido, sem taxa, combo até ×3 (cada toque em menos de 0,5 s soma +0,25; parar zera), −1⚡ e +0,15 Paranoia por toque. **Lavar na hora**: Laranjas e Consultoria com taxa fixa; Crypto e NFTs com taxa que sobe e desce (ciclos de ~10 e ~3 min), com gráfico e aviso de "boa hora". |
| Cidade | Café, Energético, Bar, Biblioteca, Academia, Beco, Praça, Spa e Fliperama, com tempo real, uma por vez. |
| Atributos | Botânica, Lábia, Furtividade e Segurança sobem por experiência (colher, vender, arriscar) e com a cidade. Ficam com você ao passar o ponto. |
| Avó, Agiota, Mendigar | Na aba Cidade, para recomeçar depois de uma batida. |
| Respeito e Nível | Sobem colhendo e vendendo; cada nível dá +1% no preço. |
| Lenda (prestígio) | (log10(vendido) − 4)², +10% de preço por ponto. Passar o ponto dá tudo; batida dá metade. |
| Zé | Vende sozinho no Discreto a cada 20 s, inclusive com o app fechado. |
| Dicas da Vó | Depois de 1 minuto sem tocar em nada, a Vó aparece num balão com a dica que mais ajuda agora (vender o estoque, comprar vaso, lavar dinheiro, mudar de esconderijo, o que falta para a próxima semente…) e um botão que leva à aba certa. Qualquer toque fecha, e ela some sozinha depois de 6 s. |
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
