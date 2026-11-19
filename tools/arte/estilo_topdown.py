"""TESTE DE ESTILO: interiores vistos de cima (estilo RPG de portátil), cômodo flutuando no preto,
crescendo a cada imóvel, com acabamento detalhado (luz quente, oclusão, textura).

    python3 tools/arte/estilo_topdown.py   -> docs/arte/estilo-topdown-teste.png
"""
import math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from cenarios import Cv, Sprite, shift, RAMPS, OL, hexrgb
from PIL import Image

W_ = RAMPS["wood"]; S_ = RAMPS["stone"]; PA = RAMPS["paper"]; CR = RAMPS["crimson"]; D_ = RAMPS["denim"]
G_ = RAMPS["gold"]; L_ = RAMPS["leaf"]; B_ = RAMPS["brick"]; SO = RAMPS["soil"]; PL = RAMPS["plum"]; TE = RAMPS["teal"]
VOID = "#120e16"
FW, FH = 320, 180
ROOT = os.path.join(os.path.dirname(__file__), "..", "..")


# ----------------------------------------------------------------- moldura do cômodo
def room_shell(c, x0, y0, w, h, wall_h, wall_fn, floor_fn, door=None):
    """Paredes grossas com tampo escuro (como nos RPGs de portátil), parede do fundo visível."""
    T = 5
    # tampo das paredes (a "grossura" vista de cima)
    c.rect(x0 - T, y0 - T, x0 + w + T - 1, y0 + h + T - 1, S_[1])
    c.rect(x0 - T, y0 - T, x0 + w + T - 1, y0 - T + 1, S_[2])          # quina de cima pega luz
    c.rect(x0 - T, y0 - T, x0 - T + 1, y0 + h + T - 1, S_[2])
    for k in range(2, T):                                              # textura do tampo
        for x in range(x0 - T, x0 + w + T, 7):
            c.set(x + k, y0 - T + k, S_[2])
    # contorno externo preto
    c.rect(x0 - T - 1, y0 - T - 1, x0 + w + T, y0 - T - 1, OL); c.rect(x0 - T - 1, y0 + h + T, x0 + w + T, y0 + h + T, OL)
    c.rect(x0 - T - 1, y0 - T - 1, x0 - T - 1, y0 + h + T, OL); c.rect(x0 + w + T, y0 - T - 1, x0 + w + T, y0 + h + T, OL)
    # interior
    wall_fn(c, x0, y0, w, wall_h)
    floor_fn(c, x0, y0 + wall_h, w, h - wall_h)
    # contorno interno (linha escura entre tampo e cômodo)
    c.rect(x0 - 1, y0 - 1, x0 + w, y0 - 1, OL); c.rect(x0 - 1, y0 + h, x0 + w, y0 + h, OL)
    c.rect(x0 - 1, y0 - 1, x0 - 1, y0 + h, OL); c.rect(x0 + w, y0 - 1, x0 + w, y0 + h, OL)
    # porta embaixo: vão no tampo
    if door:
        dx, dw = door
        c.rect(x0 + dx, y0 + h, x0 + dx + dw - 1, y0 + h + T, VOID)
        c.rect(x0 + dx - 1, y0 + h, x0 + dx - 1, y0 + h + T, OL); c.rect(x0 + dx + dw, y0 + h, x0 + dx + dw, y0 + h + T, OL)
    # oclusão: o chão escurece perto das paredes laterais e de baixo
    fy = y0 + wall_h
    c.tone(x0, fy, x0 + w - 1, fy + 2, -1)
    c.tone(x0, fy + 3, x0 + w - 1, fy + 4, -1, dither=0)
    c.tone(x0, fy, x0 + 2, y0 + h - 1, -1); c.tone(x0 + 3, fy, x0 + 4, y0 + h - 1, -1, dither=1)
    c.tone(x0 + w - 3, fy, x0 + w - 1, y0 + h - 1, -1); c.tone(x0 + w - 5, fy, x0 + w - 4, y0 + h - 1, -1, dither=0)
    c.tone(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, -1)


def planks_region(c, x0, y0, w, h, base=3, ph=6, seed=1):
    r = random.Random(seed)
    for y in range(y0, y0 + h, ph):
        x = x0 - r.randrange(0, 30)
        while x < x0 + w:
            L = r.randrange(26, 46)
            col = W_[max(1, min(5, base + r.choice([0, 0, 0, -1, 1])))]
            xa, xb = max(x, x0), min(x + L - 1, x0 + w - 1)
            if xa <= xb:
                c.rect(xa, y, xb, min(y + ph - 1, y0 + h - 1), col)
                c.hline(xa, xb, y, shift(col, 1))
                if y + ph - 1 < y0 + h:
                    c.hline(xa, xb, y + ph - 1, W_[1])
                if x + L - 1 < x0 + w:
                    c.vline(x + L - 1, y, min(y + ph - 1, y0 + h - 1), W_[1])
                for _ in range(2):
                    gx = r.randrange(xa, xb + 1); gy = y + r.randrange(2, ph - 1)
                    if gy < y0 + h:
                        c.hline(gx, min(gx + r.randrange(4, 10), xb), gy, shift(col, -1))
                if r.random() < 0.12:
                    c.set(r.randrange(xa, xb + 1), y + ph // 2, shift(col, -2))
            x += L


def wallpaper_region(c, x0, y0, w, h):
    c.rect(x0, y0, x0 + w - 1, y0 + h - 1, PA[2])
    for x in range(x0, x0 + w, 8):
        c.rect(x, y0, x + 2, y0 + h - 1, PA[3])
    for y in range(y0 + 4, y0 + h - 6, 7):
        for x in range(x0 + 5 + (y // 7 % 2) * 4, x0 + w, 8):
            c.set(x, y, PA[1])
    c.tone(x0, y0, x0 + w - 1, y0 + 1, -1)
    # rodapé
    c.hline(x0, x0 + w - 1, y0 + h - 4, W_[3]); c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, W_[2]); c.hline(x0, x0 + w - 1, y0 + h - 1, W_[1])


def light_pool(c, cx, cy, rx, ry):
    """Luz quente em faixas com borda pontilhada (sem degradê suave)."""
    c.tone(cx - rx, cy - ry, cx + rx, cy + ry, 1, mask=lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 0.55)
    c.tone(cx - rx, cy - ry, cx + rx, cy + ry, 1, mask=lambda x, y: 0.55 < ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1, dither=0)


def paste_plant(img, frame_xy, x, y):
    """Cola um estágio de planta (plantas_estagios.png) com a base em (x, y)."""
    sheet = Image.open(os.path.join(ROOT, "assets/sprites/v2/plantas_estagios.png")).convert("RGBA")
    cx, cy = frame_xy
    cell = sheet.crop((cx * 32, cy * 40, cx * 32 + 32, cy * 40 + 40))
    img.alpha_composite(cell, (x - 16, y - 39))


def paste_pot(img, idx, x, y):
    sheet = Image.open(os.path.join(ROOT, "assets/sprites/v2/vasos.png")).convert("RGBA")
    img.alpha_composite(sheet.crop((idx * 32, 0, idx * 32 + 32, 24)), (x - 16, y - 5))


def to_img(c):
    im = Image.new("RGBA", (c.w, c.h), hexrgb(VOID) + (255,))
    for y in range(c.h):
        for x in range(c.w):
            if c.px[y][x]:
                im.putpixel((x, y), hexrgb(c.px[y][x]) + (255,))
    return im


# ================================================================= QUARTINHO (pequeno)
def quartinho():
    c = Cv(FW, FH, 1)
    x0, y0, w, h, wh = 90, 34, 140, 112, 30
    room_shell(c, x0, y0, w, h, wh, wallpaper_region, lambda c, x, y, w, h: planks_region(c, x, y, w, h, 3, 6, 4), door=(58, 20))
    fy = y0 + wh
    # --- parede: janela com cortina, pôster, prateleira, relógio
    wx, wy = x0 + 82, y0 + 5
    c.box(wx - 2, wy - 2, wx + 29, wy + 18, W_[3])
    for yy in range(wy, wy + 17):
        c.hline(wx, wx + 27, yy, D_[4] if yy < wy + 9 else D_[3])
    c.rect(wx + 3, wy + 3, wx + 9, wy + 4, "#fffbef")
    c.vline(wx + 13, wy, wy + 16, W_[3]); c.vline(wx + 14, wy, wy + 16, W_[2]); c.hline(wx, wx + 27, wy + 8, W_[3])
    for k in range(5):
        c.set(wx + 2 + k, wy + 15 - k, "#fffbef")
    for (cx0, flip) in ((wx - 7, 1), (wx + 27, -1)):
        for i in range(7):
            col = [CR[3], CR[2], CR[3], CR[1], CR[2], CR[3], CR[2]][i]
            c.vline(cx0 + i, wy - 4, wy + 21 - (i if flip < 0 else 6 - i) // 2, col)
        c.set(cx0, wy + 21, OL)
    c.hline(wx - 9, wx + 36, wy - 4, S_[3]); c.hline(wx - 9, wx + 36, wy - 5, OL)
    ps = Sprite(16, 20); ps.rect(0, 0, 15, 19, PL[2]); ps.rect(2, 2, 13, 11, CR[3]); ps.ell(7, 6, 3, 3, G_[3]); ps.rect(6, 7, 8, 11, L_[2]); ps.rect(2, 13, 13, 14, "#fffbef"); ps.rect(2, 16, 9, 16, PA[3])
    ps.stamp_on(c, x0 + 52, y0 + 4)
    c.box(x0 + 116, y0 + 13, x0 + 136, y0 + 15, W_[3])
    for i, col in enumerate((D_[2], CR[2], L_[3], G_[2], PL[2])):
        c.rect(x0 + 118 + i * 3, y0 + 6 + (i % 2), x0 + 119 + i * 3, y0 + 12, col); c.set(x0 + 118 + i * 3, y0 + 6 + (i % 2), shift(col, 1))
    c.ell(x0 + 72, y0 + 10, 4, 4, OL); c.ell(x0 + 72, y0 + 10, 3, 3, "#fffbef"); c.set(x0 + 72, y0 + 8, OL); c.set(x0 + 73, y0 + 10, CR[2])
    # --- luz da janela no chão (entra inclinada)
    c.tone_poly([(wx + 2, fy), (wx + 26, fy), (wx + 14, fy + 40), (wx - 10, fy + 40)], 1)
    c.tone_poly([(wx - 2, fy), (wx + 2, fy), (wx - 10, fy + 40), (wx - 15, fy + 40)], 1, dither=0)
    c.tone_poly([(wx + 26, fy), (wx + 30, fy), (wx + 18, fy + 40), (wx + 14, fy + 40)], 1, dither=0)
    # --- cama vista de cima (cabeceira na parede)
    bed = Sprite(32, 54)
    bed.rect(0, 0, 31, 5, W_[2]); bed.hline(0, 31, 0, W_[3])
    for xx in range(2, 30, 6):
        bed.vline(xx, 1, 4, W_[1])
    bed.rect(1, 6, 30, 50, PA[4])
    bed.rect(4, 8, 27, 15, "#fffbef"); bed.hline(4, 27, 15, PA[2]); bed.hline(6, 25, 11, PA[3]); bed.set(5, 9, PA[3])
    for yy in range(18, 50):
        for xx in range(1, 31):
            wv = math.sin(xx / 3.0 + yy / 5.0) * 0.8 + math.sin(xx / 7.0 - yy / 2.4) * 0.5 + (yy - 18) / 34
            bed.set(xx, yy, D_[3] if wv > 0.9 else D_[2] if wv > -0.4 else D_[1])
    for (xx, yy) in ((6, 24), (16, 30), (24, 40), (10, 44), (20, 22)):
        bed.set(xx, yy, D_[4])
    bed.poly([(18, 18), (31, 18), (31, 30)], D_[3])                      # canto do edredom dobrado
    bed.vline(30, 6, 50, PA[2]); bed.rect(0, 51, 31, 53, W_[1]); bed.hline(0, 31, 51, W_[2])  # frente
    bed.stamp_on(c, x0 + 3, fy - 4)
    c.tone(x0 + 3, fy + 51, x0 + 36, fy + 53, -1)
    c.tone(x0 + 36, fy - 2, x0 + 38, fy + 50, -1, dither=0)
    # --- criado-mudo com abajur (luz quente em volta)
    ns = Sprite(14, 14); ns.rect(0, 0, 13, 10, W_[4]); ns.hline(0, 13, 0, W_[5]); ns.rect(0, 11, 13, 13, W_[2]); ns.set(6, 12, G_[3])
    ns.stamp_on(c, x0 + 38, fy - 2)
    light_pool(c, x0 + 45, fy + 6, 20, 13)
    c.ell(x0 + 44, fy + 3, 4, 4, OL); c.ell(x0 + 44, fy + 3, 3, 3, G_[3]); c.ell(x0 + 43, fy + 2, 1, 1, G_[4])
    c.rect(x0 + 48, fy + 5, x0 + 50, fy + 7, CR[3])
    # --- escrivaninha com computador velho e cadeira
    dk = Sprite(36, 16); dk.rect(0, 0, 35, 11, W_[3]); dk.hline(0, 35, 0, W_[4]); dk.rect(0, 12, 35, 15, W_[1]); dk.hline(0, 35, 12, W_[2])
    for k in range(4):
        dk.hline(2, 33, 3 + k * 2, shift(W_[3], -1) if k % 2 else W_[3])
    dk.stamp_on(c, x0 + 100, fy - 3)
    mon = Sprite(14, 11); mon.rect(0, 0, 13, 10, S_[4]); mon.hline(0, 13, 0, S_[5]); mon.rect(2, 2, 11, 7, TE[1]); mon.rect(3, 3, 7, 4, TE[3]); mon.rect(4, 9, 9, 10, S_[3])
    mon.stamp_on(c, x0 + 103, fy - 7)
    c.rect(x0 + 120, fy + 2, x0 + 130, fy + 4, S_[3]); c.hline(x0 + 120, x0 + 130, fy + 2, S_[5])         # teclado
    for k in range(5):
        c.set(x0 + 121 + k * 2, fy + 3, S_[2])
    c.tone_poly([(x0 + 102, fy + 12), (x0 + 118, fy + 12), (x0 + 122, fy + 26), (x0 + 98, fy + 26)], 1, dither=1)  # brilho da tela
    ch = Sprite(12, 12); ch.ell(5.5, 5.5, 5.5, 5.5, CR[2]); ch.ell(4.5, 4.5, 3, 3, CR[3]); ch.set(3, 3, CR[4]); ch.stamp_on(c, x0 + 110, fy + 16)
    c.tone(x0 + 111, fy + 28, x0 + 123, fy + 29, -1)
    # --- tapete onde ficam os vasos
    rx0, ry0, rw, rh = x0 + 46, fy + 30, 52, 34
    c.box(rx0, ry0, rx0 + rw, ry0 + rh, CR[2])
    c.rect(rx0 + 2, ry0 + 2, rx0 + rw - 2, ry0 + rh - 2, CR[3]); c.rect(rx0 + 4, ry0 + 4, rx0 + rw - 4, ry0 + rh - 4, CR[2])
    for xx in range(rx0 + 6, rx0 + rw - 5, 4):
        for yy in range(ry0 + 6, ry0 + rh - 5, 4):
            if (xx // 4 + yy // 4) % 2 == 0:
                c.set(xx, yy, G_[3])
    for xx in range(rx0 + 1, rx0 + rw, 2):
        c.set(xx, ry0 - 1, PA[3]); c.set(xx, ry0 + rh + 1, PA[3])
    # --- bagunça
    def blob(x, y, col, w=12, hh=7, seed=0):
        sp = Sprite(w, hh, seed)
        for yy in range(hh):
            for xx in range(w):
                if ((xx - w / 2) / (w / 2)) ** 2 + ((yy - hh / 2) / (hh / 2)) ** 2 <= 1 + 0.3 * math.sin(xx * 1.9 + seed):
                    sp.set(xx, yy, col)
        sp.line(2, 2, w - 4, hh - 2, shift(col, -1)); sp.hline(2, w - 4, 1, shift(col, 1))
        sp.stamp_on(c, x, y); c.tone(x + 1, y + hh, x + w, y + hh, -1)
    blob(x0 + 6, fy + 60, L_[3], 14, 8, 1); blob(x0 + 16, fy + 63, CR[2], 12, 7, 2); blob(x0 + 8, fy + 68, S_[5], 10, 6, 3)
    pz = Sprite(18, 16); pz.rect(0, 0, 17, 15, W_[4]); pz.hline(0, 17, 0, W_[5]); pz.rect(2, 2, 15, 13, W_[3]); pz.poly([(4, 4), (14, 4), (9, 12)], G_[3]); pz.set(7, 6, CR[3]); pz.set(11, 6, CR[3]); pz.set(9, 9, CR[3])
    pz.stamp_on(c, x0 + 112, fy + 52)
    c.tone(x0 + 113, fy + 68, x0 + 130, fy + 69, -1)
    for i, col in enumerate((CR[3], L_[4], D_[3])):
        c.ell(x0 + 36 + i * 5, fy + 72 - (i % 2) * 3, 2, 2, OL); c.ell(x0 + 36 + i * 5, fy + 72 - (i % 2) * 3, 1, 1, col)
    c.rect(x0 + 128, fy + 38, x0 + 134, fy + 41, OL); c.rect(x0 + 129, fy + 39, x0 + 133, fy + 40, S_[2])          # controle
    c.line(x0 + 131, fy + 38, x0 + 124, fy + 26, OL)
    c.ell(x0 + 100, fy + 74, 3, 2, OL); c.ell(x0 + 100, fy + 74, 2, 1, "#fffbef")                          # meia
    # --- capacho na porta
    c.box(x0 + 58, y0 + h - 7, x0 + 77, y0 + h - 1, CR[1]); c.rect(x0 + 60, y0 + h - 5, x0 + 75, y0 + h - 3, CR[2])
    img = to_img(c)
    # vasos com plantas no tapete
    for (px, py, pot, fr) in ((rx0 + 14, ry0 + 20, 0, (0, 1)), (rx0 + 38, ry0 + 20, 1, (2, 1))):
        paste_pot(img, pot, px, py)
        paste_plant(img, fr, px, py)
    return img


# ================================================================= GARAGEM (maior)
def garagem():
    c = Cv(FW, FH, 2)
    x0, y0, w, h, wh = 44, 20, 232, 146, 30

    def wall(c, x, y, w, h):
        r = random.Random(3)
        c.rect(x, y, x + w - 1, y + h - 1, S_[4])
        for yy in range(y, y + h - 4, 7):
            off = 0 if ((yy - y) // 7) % 2 else 8
            for xx in range(x - off, x + w, 16):
                col = r.choice([S_[4], S_[4], S_[5]])
                c.rect(max(x, xx + 1), yy + 1, min(x + w - 1, xx + 14), yy + 5, col)
                c.hline(max(x, xx + 1), min(x + w - 1, xx + 14), yy + 1, shift(col, 1))
        c.tone(x, y, x + w - 1, y + 1, -1)
        c.hline(x, x + w - 1, y + h - 4, S_[3]); c.rect(x, y + h - 3, x + w - 1, y + h - 1, S_[2])

    def floor(c, x, y, w, h):
        r = random.Random(7)
        c.rect(x, y, x + w - 1, y + h - 1, S_[4])
        for _ in range(w * h // 14):
            c.set(r.uniform(x, x + w), r.uniform(y, y + h), r.choice([S_[3], S_[3], S_[5]]))
        for yy in range(y + 36, y + h, 36):
            c.hline(x, x + w - 1, yy, S_[3])
        for xx in range(x + 58, x + w, 58):
            c.vline(xx, y, y + h - 1, S_[3])

    room_shell(c, x0, y0, w, h, wh, wall, floor, door=(96, 40))
    fy = y0 + wh
    # portão basculante na parede do fundo (direita)
    gx = x0 + 150
    c.box(gx, y0 + 2, gx + 76, y0 + wh - 2, S_[5])
    for yy in range(y0 + 4, y0 + wh - 3, 3):
        c.hline(gx + 1, gx + 75, yy, S_[3]); c.hline(gx + 1, gx + 75, yy + 1, "#fffbef")
    c.rect(gx + 34, y0 + wh - 7, gx + 42, y0 + wh - 5, S_[2])
    # painel de ferramentas e bancada
    c.box(x0 + 60, y0 + 4, x0 + 116, y0 + 24, W_[4])
    for xx in range(x0 + 63, x0 + 115, 4):
        for yy in range(y0 + 7, y0 + 23, 4):
            c.set(xx, yy, W_[2])
    tl = Sprite(50, 16)
    tl.rect(1, 3, 2, 15, W_[2]); tl.rect(0, 1, 5, 4, S_[3])
    tl.rect(10, 2, 11, 15, S_[4]); tl.ell(10.5, 2, 2, 2, S_[4])
    tl.rect(18, 1, 25, 7, CR[3]); tl.rect(20, 8, 23, 14, OL); tl.rect(25, 3, 29, 5, S_[3])
    tl.rect(36, 1, 37, 14, G_[2]); tl.rect(41, 1, 42, 14, S_[4]); tl.rect(46, 1, 47, 14, W_[2])
    tl.stamp_on(c, x0 + 64, y0 + 6)
    bench = Sprite(70, 16); bench.rect(0, 0, 69, 11, W_[3]); bench.hline(0, 69, 0, W_[4]); bench.rect(0, 12, 69, 15, W_[1]); bench.hline(0, 69, 12, W_[2])
    for xx in range(4, 66, 9):
        bench.vline(xx, 1, 10, W_[2])
    bench.rect(50, 2, 60, 8, S_[3]); bench.hline(50, 60, 2, S_[5])                              # morsa
    bench.rect(6, 3, 14, 8, CR[3]); bench.rect(18, 4, 22, 8, G_[3]); bench.rect(26, 5, 32, 7, S_[4])
    bench.stamp_on(c, x0 + 52, fy - 2)
    c.tone(x0 + 52, fy + 14, x0 + 122, fy + 16, -1)
    # luminária do teto: luz no chão
    light_pool(c, x0 + 120, fy + 62, 70, 40)
    # CARRO visto de cima
    car = Sprite(46, 86)
    car.rect(4, 0, 41, 85, CR[3])
    car.rect(0, 10, 3, 24, OL); car.rect(42, 10, 45, 24, OL); car.rect(0, 62, 3, 76, OL); car.rect(42, 62, 45, 76, OL)   # rodas
    car.rect(4, 0, 41, 4, CR[2]); car.rect(8, 1, 14, 3, G_[4]); car.rect(31, 1, 37, 3, G_[4])                         # faróis
    car.poly([(7, 18), (38, 18), (35, 32), (10, 32)], D_[3]); car.line(12, 20, 16, 30, D_[4]); car.line(20, 20, 24, 30, D_[4])  # para-brisa
    car.rect(9, 33, 36, 60, CR[3]); car.rect(9, 33, 11, 60, CR[4]); car.rect(34, 33, 36, 60, CR[2])                    # teto
    car.poly([(10, 61), (35, 61), (37, 72), (8, 72)], D_[3]); car.line(14, 62, 12, 70, D_[4])                          # vidro traseiro
    car.rect(4, 80, 41, 85, CR[2]); car.rect(7, 82, 12, 84, CR[4]); car.rect(33, 82, 38, 84, CR[4])
    car.vline(4, 5, 79, CR[4]); car.vline(41, 5, 79, CR[1]); car.set(3, 30, CR[2]); car.set(42, 30, CR[2])         # retrovisores
    car.stamp_on(c, x0 + 8, fy + 14)
    c.tone(x0 + 56, fy + 18, x0 + 59, fy + 100, -1); c.tone(x0 + 10, fy + 101, x0 + 58, fy + 103, -1)
    # mancha de óleo, pneus, caixa de ferramentas
    c.tone(x0 + 150, fy + 90, x0 + 190, fy + 104, -1, mask=lambda x, y: ((x - x0 - 170) / 20) ** 2 + ((y - fy - 97) / 6) ** 2 <= 1)
    c.tone(x0 + 160, fy + 93, x0 + 180, fy + 101, -1, mask=lambda x, y: ((x - x0 - 170) / 10) ** 2 + ((y - fy - 97) / 3) ** 2 <= 1)
    for i in range(2):
        tx, ty = x0 + 206 - i * 4, fy + 70 - i * 6
        c.ell(tx, ty, 11, 11, OL); c.ell(tx, ty, 10, 10, S_[1]); c.ell(tx, ty, 9, 9, S_[2]); c.ell(tx, ty, 4, 4, S_[0]); c.ell(tx - 2, ty - 3, 3, 1, S_[3])
    tb = Sprite(20, 12); tb.rect(0, 0, 19, 11, CR[2]); tb.rect(0, 0, 19, 3, CR[3]); tb.rect(7, 4, 12, 6, S_[2]); tb.stamp_on(c, x0 + 196, fy + 4)
    c.tone(x0 + 196, fy + 17, x0 + 216, fy + 18, -1)
    img = to_img(c)
    for i in range(4):
        px, py = x0 + 92 + i * 30, fy + 70
        paste_pot(img, [0, 1, 2, 2][i], px, py)
        paste_plant(img, [(0, 4), (1, 4), (2, 4), (2, 5)][i], px, py)
    return img


if __name__ == "__main__":
    a, b = quartinho(), garagem()
    S = 3
    gap = 12
    sheet = Image.new("RGBA", ((FW * 2 + gap) * S, FH * S), hexrgb(VOID) + (255,))
    sheet.alpha_composite(a.resize((FW * S, FH * S), Image.NEAREST), (0, 0))
    sheet.alpha_composite(b.resize((FW * S, FH * S), Image.NEAREST), ((FW + gap) * S, 0))
    out = os.path.join(ROOT, "docs", "arte", "estilo-topdown-teste.png")
    sheet.save(out)
    a.save(os.path.join(ROOT, "docs", "arte", "estilo-topdown-quartinho.png"))
    print("ok", out)
