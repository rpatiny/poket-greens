# Greenhood — Direção de Arte

> Substitui a §11 do GDD. A arte do protótipo `el-cartel` (16 px, estilo GBA) fica só como referência.
> Projeto no Pixelwright: **"Greenhood – Direção de Arte"**
> (https://studio.pixelwright.app/?cloud=prj_6aae7707656ed88d).

![Mockup da garagem](arte/mockup-garagem.png)

## 1. Pilares visuais

1. **Pixel art detalhada, não retrô cru.** Escala dobrada em relação ao GBA: mais pixels para
   rosto, roupa, textura de material e luz.
2. **Aconchegante com um fundo de perigo.** Cores quentes, luz do dia entrando pela janela e
   plantas vivas. O risco (polícia, noite, Paranoia) entra com cor fria e roxa.
3. **Leitura antes de tudo.** O personagem e os objetos interativos sempre têm mais contraste
   que o cenário.
4. **Humor visual.** Plantas "inofensivas" exageradas (Alface Mística, Fruto do Éden), placas e
   pôsteres com piadas.

## 2. Escala e câmera

| Item | Antes (M0) | Agora |
|---|---|---|
| Resolução base | 320×180 | **640×360** (ampliada em escala inteira: 2× = 720p, 3× = 1080p, 6× = 4K) |
| Tile | 16×16 | **32×32** |
| Personagem | 16×24 (cabeção) | **48×48 de canvas**, figura de ~45 px (cerca de 2,4 cabeças) |
| Campo de visão | 20×11 tiles | 20×11 tiles (o mesmo enquadramento, com o dobro de detalhe) |

- Visão **3/4 de cima** (top-down): paredes mostram a face da frente; móveis e caixotes mostram
  o tampo e a frente.
- O personagem ocupa 1 tile de largura e anda na grade de 32 px. Os pés ficam na linha de baixo
  do tile e a cabeça sobe por cima do tile de cima (ordenação por Y).

## 3. Paleta

![Paleta](arte/paleta.png)

- **62 cores em 13 rampas** (está no projeto do Pixelwright). Toda arte usa só essas cores.
- **Contorno:** `#1a1420`, um roxo quase preto. Nunca preto puro.
- **Sombras puxam para o roxo/frio, luzes puxam para o amarelo/quente.** Ex.: na pele, o laranja
  desce para vinho; no verde, o amarelado desce para verde-azulado.
- **Rampas por material:** pele, cabelo, folha, madeira, tijolo, pedra/concreto, jeans, ouro,
  carmim (tecidos e alertas), terra, ameixa (noite e UI), verde-água (dinheiro limpo, tecnologia).
- **Cores com significado no jogo:**
  - 💵 Grana suja → `gold` · 💳 grana limpa → `teal`
  - 👁️ Paranoia e polícia → `crimson` e `plum`
  - ⚡ Estamina → `gold.3` / `gold.4`

## 4. Luz e sombra

- **Luz única vinda de cima, à esquerda.** Vale em todo sprite, tile e cena.
- Lado esquerdo e topo em tons claros; lado direito e base em tons escuros.
- **Sombra de contato:** uma elipse escura sob personagens e objetos.
- **Sombras projetadas** vão para baixo e para a direita, com borda dura.
- **Luzes de cena** (janela, luminária, poste): um feixe de 1–2 tons mais claros no chão. Use
  pontilhado 50% só na borda do feixe.
- **Noite** (ciclo dia/noite do GDD): a cena inteira desce um tom e puxa para `plum`; as luzes
  ficam quentes e amarelas.

## 5. Contorno e pixels

- Contorno de 1 px na silhueta. Linhas internas usam o tom mais escuro do material vizinho, não
  o contorno.
- Materiais com volume têm pelo menos 2 px de espessura. A linha de 1 px fica para fios, cordões
  e hastes.
- Sem anti-aliasing na borda de fora. Por dentro, só a partir de 32 px em curvas longas.
- Nada de pixel solto (orphan), escadinha irregular ou duas faixas de tons paralelas
  (banding). O `project_audit` do Pixelwright confere tudo isso.

## 6. Personagens

![Protagonista](arte/protagonista.png)

- **Canvas de 48×48**: cabeça de ~18 px, olhos 2×3 com brilho, boca de 2 px, bochecha rosada.
- **Montados como rig** no Pixelwright (partes: sombra, pernas, tronco, braços, cabeça, cabelo,
  olhos, boca). Desenha-se uma vez e anima-se movendo as partes.
- **Variantes** de olhos (aberto, semicerrado, fechado, feliz) e boca (neutra, sorriso,
  aberta, falando), para diálogos expressivos.
- **Direções:** frente (S), costas (N) e perfil (E). O perfil esquerdo (W) é o direito espelhado.
- **Animações mínimas:** `idle` (respira e pisca), `walk` (4 quadros de 130 ms) e `talk`.
- **Silhueta com assinatura:** cada NPC tem uma forma que o identifica de longe (o coque da Vó,
  o boné do Zé, o avental do vendedor).
- **Personalização** do avatar por troca de rampa: pele, cabelo, camisa e calça trocam de rampa
  sem redesenhar.

### Protagonista
Moletom verde com capuz, cordões e bolso canguru; jeans com barra dobrada; tênis branco com
detalhe carmim; cabelo castanho bagunçado com franja. O verde é a cor do jogo e o liga à marca.

## 7. Cenários e tiles

- **Tiles de 32×32.** Os tiles que se repetem (chão, grama, calçada) precisam emendar sem
  costura. Use textura implícita: poucas manchas, nunca ruído em tudo.
- **Paredes internas** com 2 tiles de altura (64 px) e rodapé. Janelas, pôsteres e prateleiras
  são objetos por cima.
- **Exterior:** cada prédio tem uma cor de fachada e um elemento que o identifica (toldo do
  Growshop, letreiro neon do Bar do Zé, grade da Lavanderia).
- **Objetos interativos** (vasos, equipamentos, NPCs) têm mais contraste e saturação que o fundo.
  O jogador acha o que pode usar sem tutorial.

### Vasos e plantas
- Vaso de barro de 22×12 com terra visível.
- **3 estágios:** broto, muda e planta adulta. A adulta é feita de moitas redondas iluminadas da
  esquerda.
- Balão "!" quando a planta está pronta, à direita da planta.
- Cada semente do catálogo tem uma planta adulta própria (forma e cor diferentes), partindo
  desse vaso.

### Módulos de cultivo (escala do fim de jogo)

![Galpão com módulos](arte/galpao-modulos.png)

O mockup acima tem 54 plantas numa única tela de 640×360, sem zoom: 3 vasos, 3 floreiras,
2 bancadas e 4 racks hidropônicos.
- **Plantas dos módulos** usam versões menores da planta adulta (cerca de 60% do tamanho), para
  caber de 3 a 5 por módulo.
- **Vaso:** 1 planta grande. **Floreira:** 3. **Bancada:** 5. **Rack:** 8 em 2 andares com LED.
- Balão "!" e barra de progresso por módulo, não por planta.
- Equipamentos ficam em pontos fixos do cenário e não competem com os módulos pelo chão.

## 8. Interface

- **Fonte pixel** de altura 8 (a Press Start 2P serve por enquanto). Avaliar uma fonte mais
  estreita para os diálogos longos.
- **Caixas** com fundo `white`, borda dupla (`outline` + `stone.3`) e cantos arredondados de 2 px.
- **Ícones de 16×16** (ícones de item são a única coisa que fica em 16 px) com a mesma luz e o
  mesmo contorno.

## 9. Produção

| Lote | Conteúdo | Status |
|---|---|---|
| 0 – Guia de estilo | Paleta, protagonista (frente + idle + walk), mockup da garagem | ✅ |
| 1 – Protagonista completo | Costas e perfil, walk nas 3 direções, talk | a fazer |
| 2 – Garagem jogável | Tileset interior (piso, parede, rodapé, janela), vasos, 3 estágios, equipamentos | a fazer |
| 2b – Módulos | Floreira, bancada, rack hidropônico, torre; plantas em tamanho de módulo | rascunho ✅ |
| 3 – Vila Clorofila | Tileset exterior (grama, calçada, rua, árvores), fachadas da Avó, Growshop e garagem | a fazer |
| 4 – NPCs | Vó Dita, Zé e Vendedor (rig com variações de rampa + acessório próprio) | a fazer |
| 5 – UI | Caixa de diálogo, HUD, ícones dos recursos | a fazer |

Exportação: Pixelwright → **Godot 4** (SpriteFrames para personagens, TileSet para cenários).
