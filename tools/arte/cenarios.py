"""Cenários detalhados dos imóveis (PNG), na paleta do projeto.

Cada cômodo tem tamanho próprio (16:9) e é desenhado na mesma escala de pixel das plantas.
Luz vem de cima/esquerda (ou da janela); sombras e luz trocam a cor pelo degrau vizinho da
própria rampa do material, então nada sai da paleta.

    python3 tools/arte/cenarios.py            # gera assets/sprites/v2/cenarios/*.png
"""
import math, os, random, json
from PIL import Image

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "v2", "cenarios")

RAMPS = {
    "skin": ["#5c2b36", "#8f4a45", "#c27a5c", "#e8a87c", "#f7d4b0"],
    "hair": ["#24161f", "#432532", "#6b3a3a", "#94573f"],
    "leaf": ["#14292b", "#1d4537", "#2c6a40", "#4a8f40", "#7cb342", "#bcd95e"],
    "wood": ["#3b1f2b", "#5e2f2e", "#8a4a33", "#b5703f", "#d99a5b", "#f0c487"],
    "brick": ["#401a2c", "#6e2834", "#a3423a", "#cc6748", "#e99568"],
    "stone": ["#1a1420", "#272436", "#403d54", "#646379", "#8f90a2", "#bfbfc8", "#ebe9e1", "#fffbef"],
    "denim": ["#1b1f45", "#283c74", "#3a5ea3", "#6590cc", "#a6cbeb"],
    "gold": ["#5a2f1f", "#94592a", "#d1952e", "#f0c94f", "#fff0a6"],
    "crimson": ["#3d0f2e", "#6e1b3d", "#a62e4a", "#d95463", "#f2918a"],
    "soil": ["#2b1a24", "#47292b", "#6b4234", "#8f6040"],
    "plum": ["#1f1630", "#352450", "#56397a", "#8160a8"],
    "teal": ["#132b38", "#1b4a55", "#2a7470", "#48a38a", "#8fd4a8"],
    "paper": ["#8f6040", "#bba57e", "#dccaa3", "#efe3c8", "#fffbef"],
}
OL = "#1a1420"
# cor -> (rampa, índice), para clarear/escurecer dentro da rampa
WHERE = {}
for rn, cols in RAMPS.items():
    for i, c in enumerate(cols):
        WHERE.setdefault(c, (rn, i))


def hexrgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))


def shift(col, n):
    if col not in WHERE:
        return col
    rn, i = WHERE[col]
    r = RAMPS[rn]
    return r[max(0, min(len(r) - 1, i + n))]


class Cv:
    def __init__(s, w, h, seed=1):
        s.w, s.h = w, h
        s.px = [[None] * w for _ in range(h)]
        s.r = random.Random(seed)

    # ---- básico
    def set(s, x, y, c):
        x, y = int(round(x)), int(round(y))
        if 0 <= x < s.w and 0 <= y < s.h and c:
            s.px[y][x] = c

    def get(s, x, y):
        return s.px[y][x] if 0 <= x < s.w and 0 <= y < s.h else None

    def rect(s, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                s.set(x, y, c)

    def box(s, x0, y0, x1, y1, c, ol=OL):
        s.rect(x0, y0, x1, y1, ol)
        s.rect(x0 + 1, y0 + 1, x1 - 1, y1 - 1, c)

    def hline(s, x0, x1, y, c):
        s.rect(x0, y, x1, y, c)

    def vline(s, x, y0, y1, c):
        s.rect(x, y0, x, y1, c)

    def line(s, x0, y0, x1, y1, c):
        n = int(max(abs(x1 - x0), abs(y1 - y0), 1))
        for i in range(n + 1):
            s.set(x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n, c)

    def ell(s, cx, cy, rx, ry, c):
        for y in range(int(cy - ry), int(cy + ry) + 1):
            dy = (y - cy) / max(ry, 0.5)
            if abs(dy) > 1:
                continue
            w = rx * math.sqrt(1 - dy * dy)
            s.rect(round(cx - w), y, round(cx + w), y, c)

    def poly(s, pts, c):
        ys = [p[1] for p in pts]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            for i in range(len(pts)):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                s.rect(round(a), y, round(b) - 1, y, c)

    # ---- luz e sombra (dentro da rampa)
    def tone(s, x0, y0, x1, y1, n, mask=None, dither=None):
        """Desloca as cores n degraus na rampa. dither=0/1 aplica em xadrez (borda suave)."""
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                if not (0 <= x < s.w and 0 <= y < s.h):
                    continue
                if mask and not mask(x, y):
                    continue
                if dither is not None and (x + y) % 2 != dither:
                    continue
                c = s.px[y][x]
                if c and c != OL:
                    s.px[y][x] = shift(c, n)

    def tone_poly(s, pts, n, dither=None):
        ys = [p[1] for p in pts]
        inside = set()
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            for i in range(len(pts)):
                (x0, y0), (x1, y1) = pts[i], pts[(i + 1) % len(pts)]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for a, b in zip(xs[::2], xs[1::2]):
                for x in range(round(a), round(b)):
                    inside.add((x, y))
        for (x, y) in inside:
            if dither is not None and (x + y) % 2 != dither:
                continue
            c = s.get(x, y)
            if c and c != OL:
                s.px[y][x] = shift(c, n)

    def shadow_ell(s, cx, cy, rx, ry, n=-1):
        s.tone(cx - rx, cy - ry, cx + rx, cy + ry, n, mask=lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1)

    # ---- texturas
    def speckle(s, x0, y0, x1, y1, n, cols):
        for _ in range(n):
            s.set(s.r.uniform(x0, x1), s.r.uniform(y0, y1), s.r.choice(cols))

    def outline(s, x0=0, y0=0, x1=None, y1=None):
        """Contorno em volta de tudo que foi desenhado numa camada separada (usar com Layer)."""
        pass

    def save(s, path, scale=1):
        im = Image.new("RGBA", (s.w, s.h), (0, 0, 0, 0))
        for y in range(s.h):
            for x in range(s.w):
                c = s.px[y][x]
                if c:
                    im.putpixel((x, y), hexrgb(c) + (255,))
        if scale > 1:
            im = im.resize((s.w * scale, s.h * scale), Image.NEAREST)
        im.save(path)


class Sprite(Cv):
    """Objeto desenhado à parte e colado com contorno automático."""

    def stamp_on(s, dst, ox, oy, outline=True):
        if outline:
            add = []
            for y in range(-1, s.h + 1):
                for x in range(-1, s.w + 1):
                    if s.get(x, y):
                        continue
                    if any(s.get(x + a, y + b) for a, b in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                        add.append((x, y))
            for x, y in add:
                dst.set(ox + x, oy + y, OL)
        for y in range(s.h):
            for x in range(s.w):
                if s.px[y][x]:
                    dst.set(ox + x, oy + y, s.px[y][x])


P = {k: v for k, v in [("ol", OL)]}
W_ = RAMPS["wood"]; S_ = RAMPS["stone"]; PA = RAMPS["paper"]; CR = RAMPS["crimson"]; D_ = RAMPS["denim"]
G_ = RAMPS["gold"]; L_ = RAMPS["leaf"]; B_ = RAMPS["brick"]; SO = RAMPS["soil"]; PL = RAMPS["plum"]; TE = RAMPS["teal"]


# ======================================================================= peças
def plank_floor(c, y0, base=3, plank_h=7, seed=3):
    r = random.Random(seed)
    for y in range(y0, c.h, plank_h):
        off = r.randrange(0, 40)
        x = -off
        while x < c.w:
            L = r.randrange(36, 64)
            tone = base + r.choice([0, 0, 0, -1, 1]) if base < 5 else base
            col = W_[max(1, min(5, tone))]
            c.rect(x, y, x + L - 1, y + plank_h - 1, col)
            c.hline(x, x + L - 1, y, shift(col, 1) if r.random() < 0.6 else col)   # aresta de cima pega luz
            c.hline(x, x + L - 1, y + plank_h - 1, W_[1])                           # fresta
            c.vline(x + L - 1, y, y + plank_h - 1, W_[1])
            for _ in range(r.randrange(1, 3)):                                      # veio da madeira
                gx = x + r.randrange(2, max(3, L - 12)); gy = y + r.randrange(2, plank_h - 2)
                c.hline(gx, gx + r.randrange(5, 12), gy, shift(col, -1))
            if r.random() < 0.15:                                                   # nó
                kx = x + r.randrange(4, max(5, L - 4)); ky = y + plank_h // 2
                c.set(kx, ky, shift(col, -2)); c.set(kx + 1, ky, shift(col, -1))
            x += L


def wallpaper(c, y1, base=2, stripe=3, seed=5):
    r = random.Random(seed)
    c.rect(0, 0, c.w - 1, y1, PA[base])
    for x in range(0, c.w, 9):
        c.rect(x, 0, x + 2, y1, PA[stripe])
        c.vline(x + 3, 0, y1, PA[base - 1] if x % 18 == 0 else PA[base])
    for y in range(4, y1 - 4, 8):                         # florzinhas
        for x in range((y // 8 % 2) * 4 + 5, c.w, 9):
            c.set(x, y, PA[base - 1])
    # sombra do teto e cantos (oclusão)
    c.tone(0, 0, c.w - 1, 1, -2); c.tone(0, 2, c.w - 1, 3, -1); c.tone(0, 4, c.w - 1, 5, -1, dither=0)


def baseboard(c, y, col=None):
    col = col or W_[2]
    c.hline(0, c.w - 1, y - 4, shift(col, 1))
    c.rect(0, y - 3, c.w - 1, y - 1, col)
    c.hline(0, c.w - 1, y, OL)
    c.tone(0, y + 1, c.w - 1, y + 2, -1)
    c.tone(0, y + 3, c.w - 1, y + 3, -1, dither=0)


def window(c, x, y, w, h, frame=None, sky=True):
    frame = frame or W_[3]
    c.box(x - 3, y - 3, x + w + 2, y + h + 2, frame)
    c.rect(x - 2, y - 2, x + w + 1, y - 2, shift(frame, 1))
    # céu com nuvens e prédio distante
    for yy in range(y, y + h):
        t = (yy - y) / h
        c.hline(x, x + w - 1, yy, D_[4] if t < 0.5 else D_[3])
    c.rect(x + 3, y + 5, x + 12, y + 7, "#fffbef"); c.rect(x + 6, y + 4, x + 10, y + 4, "#fffbef")
    c.rect(x + w - 16, y + h - 12, x + w - 6, y + h - 1, S_[4])
    for wy in range(y + h - 10, y + h - 1, 3):
        for wx in range(x + w - 14, x + w - 7, 3):
            c.set(wx, wy, S_[5])
    # caixilho
    c.vline(x + w // 2, y, y + h - 1, frame); c.vline(x + w // 2 + 1, y, y + h - 1, shift(frame, -1))
    c.hline(x, x + w - 1, y + h // 2, frame)
    # reflexo
    for k in range(6):
        c.set(x + 2 + k, y + h - 3 - k, "#fffbef")
        c.set(x + w // 2 + 4 + k, y + h // 2 - 2 - k, "#fffbef")
    # parapeito
    c.box(x - 5, y + h + 2, x + w + 4, y + h + 5, frame)
    c.hline(x - 4, x + w + 3, y + h + 3, shift(frame, 1))


# ======================================================================= 0 · Quartinho dos fundos (240x135)
def quartinho():
    W, H, F = 240, 135, 56
    c = Cv(W, H, 1)
    wallpaper(c, F - 1)
    # mancha de umidade e rachadura
    c.tone(16, 4, 44, 14, -1, mask=lambda x, y: ((x - 30) / 14) ** 2 + ((y - 8) / 5) ** 2 <= 1, dither=1)
    c.tone(20, 5, 40, 12, -1, mask=lambda x, y: ((x - 30) / 9) ** 2 + ((y - 8) / 3) ** 2 <= 1, dither=0)
    c.line(118, 0, 121, 6, PA[1]); c.line(121, 6, 119, 11, PA[1])
    plank_floor(c, F, base=3, seed=11)
    baseboard(c, F)

    # ---- janela com cortinas (luz entra pela direita)
    window(c, 174, 9, 40, 28)
    c.rect(166, 4, 222, 5, S_[3]); c.hline(166, 222, 4, S_[4]); c.set(165, 4, OL); c.set(223, 4, OL)
    for side, x0 in (("l", 165), ("r", 209)):
        cur = Sprite(14, 44)
        for x in range(14):
            k = (x + (0 if side == "l" else 2)) % 5
            col = [CR[3], CR[3], CR[2], CR[1], CR[2]][k]
            for y in range(44):
                if side == "l" and y > 30 and x > 14 - (y - 30) * 0.6:
                    continue
                if side == "r" and y > 30 and x < (y - 30) * 0.6:
                    continue
                cur.set(x, y, col)
        for x in range(0, 14, 5):
            cur.set(x, 0, CR[4])
        cur.stamp_on(c, x0, 5)
    # ---- feixe de luz no chão (losango inclinado), borda pontilhada
    beam = [(160, F + 1), (226, F + 1), (240, H), (176, H)]
    c.tone_poly(beam, 1)
    c.tone_poly([(154, F + 1), (160, F + 1), (176, H), (168, H)], 1, dither=0)
    c.tone_poly([(226, F + 1), (232, F + 1), (240, H - 10), (240, H)], 1, dither=0)

    # ---- pôster (cantos com fita) e relógio
    pos = Sprite(26, 34)
    pos.rect(0, 0, 25, 33, PL[2]); pos.rect(2, 2, 23, 20, CR[3]); pos.ell(12, 11, 6, 6, G_[3]); pos.ell(12, 11, 4, 4, G_[4])
    pos.rect(9, 14, 15, 20, L_[2]); pos.rect(3, 23, 22, 24, "#fffbef"); pos.rect(3, 27, 16, 28, PA[3]); pos.rect(3, 30, 19, 30, PA[2])
    pos.set(25, 33, None); pos.set(24, 33, None); pos.set(25, 32, None)
    pos.stamp_on(c, 106, 12)
    for (tx, ty) in ((104, 10), (129, 10), (104, 44)):
        c.rect(tx, ty, tx + 3, ty + 2, PA[3])
    c.tone(107, 47, 132, 48, -1)                                   # sombra do pôster na parede
    c.ell(148, 18, 6, 6, OL); c.ell(148, 18, 5, 5, "#fffbef"); c.line(148, 18, 148, 14, OL); c.line(148, 18, 151, 19, CR[2])

    # ---- cama (cabeceira na parede, colchão em 3/4)
    bed = Sprite(84, 76)
    bed.rect(0, 0, 83, 20, W_[2])                     # cabeceira
    for x in range(0, 84, 12):
        bed.rect(x, 2, x + 9, 18, W_[3]); bed.hline(x, x + 9, 2, W_[4]); bed.vline(x + 9, 2, 18, W_[2])
    bed.rect(0, 0, 83, 1, W_[4])
    bed.rect(0, 0, 3, 75, W_[2]); bed.rect(80, 0, 83, 75, W_[1])   # colunas
    bed.rect(4, 20, 79, 66, PA[4])                    # lençol
    for k in range(5):
        bed.line(8 + k * 14, 24, 14 + k * 14, 34, PA[3])
    bed.rect(8, 21, 38, 31, "#fffbef"); bed.hline(8, 38, 31, PA[2]); bed.hline(10, 36, 26, PA[3])  # travesseiro
    bed.rect(44, 23, 74, 30, PA[3]); bed.hline(44, 74, 30, PA[2])                                  # travesseiro 2
    # edredom amarrotado
    for y in range(36, 67):
        for x in range(4, 80):
            wv = math.sin(x / 3.2 + y / 6) * 0.8 + math.sin(x / 9 - y / 2.6) * 0.6 + (y - 36) / 40
            col = D_[3] if wv > 0.85 else D_[2] if wv > -0.55 else D_[1]
            if y < 40 and x > 60 - (40 - y) * 3:
                continue
            bed.set(x, y, col)
    for x in range(4, 80, 9):
        for y in range(40, 66, 7):
            bed.set(x + (y // 7) % 3, y, D_[4])       # estampa de estrelinhas
    bed.rect(4, 66, 79, 72, W_[2]); bed.hline(4, 79, 66, W_[3]); bed.hline(4, 79, 72, W_[1])       # frente
    for x in range(10, 78, 7):
        bed.rect(x, 63, x + 3, 70, D_[1])             # edredom caindo
    bed.stamp_on(c, 4, 30)
    c.tone(6, 103, 90, 107, -1); c.tone(6, 108, 92, 109, -1, dither=0)        # sombra no chão

    # ---- criado-mudo com abajur, despertador e latinhas
    ns = Sprite(22, 26)
    ns.rect(0, 0, 21, 5, W_[4]); ns.hline(0, 21, 0, W_[5])
    ns.rect(0, 6, 21, 25, W_[3]); ns.rect(2, 9, 19, 15, W_[2]); ns.rect(2, 17, 19, 23, W_[2])
    ns.set(10, 12, G_[3]); ns.set(10, 20, G_[3])
    ns.stamp_on(c, 92, 64)
    c.tone(92, 91, 116, 93, -1)
    lamp = Sprite(14, 18)
    lamp.poly([(2, 0), (11, 0), (13, 8), (0, 8)], G_[3]); lamp.hline(2, 11, 0, G_[4]); lamp.rect(1, 7, 12, 8, G_[2])
    lamp.rect(6, 9, 7, 15, S_[3]); lamp.rect(3, 15, 10, 17, S_[3])
    lamp.stamp_on(c, 93, 46)
    c.tone_poly([(88, 64), (110, 64), (116, 70), (84, 70)], 1, dither=1)        # luz do abajur no tampo
    clk = Sprite(8, 6); clk.rect(0, 0, 7, 5, CR[2]); clk.rect(1, 1, 6, 4, "#1b1b2a"); clk.rect(2, 2, 5, 2, CR[4])
    clk.stamp_on(c, 108, 59)
    for i, col in enumerate((CR[3], L_[4], D_[3])):
        can = Sprite(4, 6); can.rect(0, 0, 3, 5, col); can.vline(0, 0, 5, shift(col, 1)); can.hline(0, 3, 0, S_[5])
        can.stamp_on(c, 72 + i * 6, 94 + (i % 2) * 3)

    # ---- bagunça: roupas, tênis, pizza, livros, mochila, videogame
    def cloth(x, y, col, w=18, h=8, seed=0):
        sp = Sprite(w, h, seed)
        for yy in range(h):
            for xx in range(w):
                if ((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2 <= 1 + 0.25 * math.sin(xx * 1.7 + seed):
                    sp.set(xx, yy, col)
        for k in range(3):
            sp.line(2 + k * 5, 2, 5 + k * 5, h - 2, shift(col, -1))
        sp.hline(3, w - 4, 1, shift(col, 1))
        sp.stamp_on(c, x, y)
        c.tone(x + 2, y + h, x + w, y + h + 1, -1)
    cloth(100, 104, CR[2], 20, 9, 1)
    cloth(112, 110, L_[3], 18, 8, 2)
    cloth(94, 114, D_[2], 22, 8, 3)
    cloth(118, 100, S_[5], 14, 7, 4)
    # tênis
    for i, x in enumerate((60, 72)):
        sh = Sprite(10, 6)
        sh.rect(0, 1, 9, 4, "#fffbef"); sh.rect(5, 0, 9, 2, S_[5]); sh.hline(0, 9, 5, S_[4]); sh.rect(1, 2, 3, 3, CR[3])
        sh.stamp_on(c, x, 120 + i * 2)
    # caixa de pizza aberta
    pz = Sprite(30, 22)
    pz.rect(0, 0, 29, 8, W_[4]); pz.hline(0, 29, 0, W_[5]); pz.rect(6, 3, 22, 5, CR[3])      # tampa
    pz.rect(0, 9, 29, 21, W_[3]); pz.rect(2, 10, 27, 20, W_[4])
    pz.poly([(6, 11), (22, 11), (14, 20)], G_[3]); pz.poly([(8, 12), (20, 12), (14, 18)], G_[4])
    for (x, y) in ((11, 13), (16, 14), (14, 16)):
        pz.set(x, y, CR[2]); pz.set(x + 1, y, CR[3])
    pz.stamp_on(c, 196, 104)
    c.tone(198, 127, 228, 128, -1)
    # pilha de livros
    for i, col in enumerate((D_[2], CR[2], L_[3], G_[2])):
        bk = Sprite(16 - i, 4); bk.rect(0, 0, 15 - i, 3, col); bk.hline(0, 15 - i, 0, shift(col, 1)); bk.vline(14 - i, 0, 3, PA[3])
        bk.stamp_on(c, 214 + i, 88 - i * 4)
    c.tone(214, 92, 232, 93, -1)
    # videogame + controle com fio
    vg = Sprite(18, 8); vg.rect(0, 0, 17, 7, S_[2]); vg.hline(0, 17, 0, S_[3]); vg.rect(12, 3, 15, 4, TE[3]); vg.set(3, 4, CR[3])
    vg.stamp_on(c, 150, 120)
    ct = Sprite(12, 6); ct.rect(0, 1, 11, 4, S_[2]); ct.rect(1, 0, 3, 5, S_[2]); ct.rect(8, 0, 10, 5, S_[2]); ct.set(2, 2, S_[4]); ct.set(9, 2, CR[3]); ct.set(9, 3, TE[3])
    ct.stamp_on(c, 132, 126)
    c.line(150, 124, 144, 128, OL)
    # mochila encostada na parede
    bp = Sprite(16, 18)
    bp.ell(8, 9, 7, 8, L_[2]); bp.rect(3, 9, 12, 16, L_[2]); bp.rect(4, 10, 11, 15, L_[3]); bp.hline(4, 11, 12, L_[1])
    bp.set(7, 2, G_[3]); bp.vline(3, 4, 12, L_[3])
    bp.stamp_on(c, 220, 44)
    c.tone(220, 62, 238, 63, -1)
    # meias soltas e papel amassado
    c.ell(140, 92, 4, 2, OL); c.ell(140, 92, 3, 1, "#fffbef")
    c.ell(36, 124, 4, 3, OL); c.ell(36, 124, 3, 2, PA[4]); c.set(35, 123, PA[2])
    return c, {"w": W, "h": H, "floor": F, "potArea": [126, 66, 230, 122]}




# ======================================================================= 1 · Armário Grow (240x135)
def armario():
    W, H, F = 240, 135, 52
    c = Cv(W, H, 2)
    r = random.Random(21)
    # fundo de papel alumínio amassado: placas facetadas em tons de metal
    c.rect(0, 0, W - 1, H - 1, S_[4])
    for _ in range(420):
        x, y = r.uniform(0, W), r.uniform(0, H)
        w, h = r.uniform(4, 12), r.uniform(3, 8)
        col = r.choice([S_[3], S_[4], S_[4], S_[5]])
        c.poly([(x, y), (x + w, y + r.uniform(-2, 2)), (x + w * 0.7, y + h), (x - w * 0.2, y + h * 0.8)], col)
    for _ in range(160):
        x, y = r.uniform(0, W), r.uniform(0, H)
        c.line(x, y, x + r.uniform(-5, 5), y + r.uniform(-3, 3), r.choice([S_[3], S_[6]]))
    for _ in range(50):
        c.set(r.uniform(0, W), r.uniform(0, H), "#fffbef")
    # paredes laterais em perspectiva (mais escuras)
    c.tone_poly([(0, 0), (38, 10), (38, H), (0, H)], -1)
    c.tone_poly([(0, 0), (22, 6), (22, H), (0, H)], -1)
    c.tone_poly([(W, 0), (W - 38, 10), (W - 38, H), (W, H)], -1)
    c.tone_poly([(W, 0), (W - 22, 6), (W - 22, H), (W, H)], -1)
    c.line(38, 10, 38, H, S_[2]); c.line(W - 39, 10, W - 39, H, S_[2])
    # piso de madeira escura do armário
    for y in range(F + 30, H, 6):
        c.rect(38, y, W - 40, y + 5, W_[1]); c.hline(38, W - 40, y, W_[2]); c.hline(38, W - 40, y + 5, W_[0])
    c.tone(38, F + 30, W - 40, F + 31, -1)
    # varão com cabides e roupas nos cantos
    c.rect(0, 4, W - 1, 6, S_[3]); c.hline(0, W - 1, 4, S_[5]); c.hline(0, W - 1, 7, OL)
    clothes = [(2, CR[2], "camisa"), (14, D_[2], "jaqueta"), (26, L_[2], "camisa"), (196, G_[2], "camisa"), (210, PL[2], "jaqueta"), (224, CR[1], "camisa")]
    for x, col, kind in clothes:
        c.line(x + 6, 7, x + 6, 10, S_[2]); c.line(x + 1, 12, x + 6, 9, S_[2]); c.line(x + 6, 9, x + 11, 12, S_[2])
        sp = Sprite(13, 40 if kind == "jaqueta" else 32)
        sp.rect(0, 0, 12, sp.h - 1, col)
        sp.rect(0, 0, 2, 10, shift(col, 1)); sp.vline(6, 2, sp.h - 1, shift(col, -1))
        for yy in range(6, sp.h, 7):
            sp.hline(1, 11, yy, shift(col, -1))
        sp.rect(4, 0, 8, 2, shift(col, -1))
        sp.stamp_on(c, x, 12)
    # caixa de sapatos e tênis no chão
    bx = Sprite(26, 14); bx.rect(0, 0, 25, 4, CR[3]); bx.hline(0, 25, 0, CR[4]); bx.rect(0, 5, 25, 13, CR[2]); bx.rect(8, 7, 17, 10, "#fffbef")
    bx.stamp_on(c, 44, 112)
    for i, x in enumerate((176, 188)):
        sh = Sprite(11, 7); sh.rect(0, 2, 10, 5, OL if i == 0 else S_[2]); sh.rect(5, 0, 10, 3, S_[3]); sh.hline(0, 10, 6, S_[5])
        sh.stamp_on(c, x, 118 + i)
    # refletor da luz de cultivo (cabo, corrente, lâmpada roxa)
    c.vline(119, 0, 10, OL); c.vline(120, 0, 10, S_[2])
    lamp = Sprite(84, 10)
    lamp.rect(0, 0, 83, 5, S_[3]); lamp.hline(0, 83, 0, S_[5]); lamp.hline(0, 83, 5, S_[2])
    lamp.rect(4, 6, 79, 8, PL[3])
    for x in range(6, 78, 4):
        lamp.set(x, 7, "#fffbef")
    lamp.stamp_on(c, 78, 11)
    # timer de tomada e extensão (gambiarra)
    tm = Sprite(10, 12); tm.rect(0, 0, 9, 11, "#fffbef"); tm.ell(4, 4, 3, 3, S_[4]); tm.set(4, 2, CR[3]); tm.rect(2, 9, 7, 10, S_[4])
    tm.stamp_on(c, 200, 70)
    c.line(205, 82, 205, 96, OL); c.line(205, 96, 160, 104, OL)
    for (x, y) in ((182, 100), (170, 102)):
        c.rect(x, y, x + 2, y + 1, S_[4])        # fita isolante
    return c, {"w": W, "h": H, "floor": F, "dark": {"a": 0.42, "tint": "53,36,80", "lights": [[120, 34, 95]]}}


# ======================================================================= 2 · Garagem do Vizinho (240x135)
def garagem():
    W, H, F = 240, 135, 54
    c = Cv(W, H, 3)
    r = random.Random(31)
    # parede de blocos de concreto pintados
    c.rect(0, 0, W - 1, F - 1, S_[4])
    for y in range(0, F, 9):
        off = 0 if (y // 9) % 2 else 10
        for x in range(-off, W, 20):
            col = r.choice([S_[4], S_[4], S_[5]])
            c.rect(x + 1, y + 1, x + 18, y + 7, col)
            c.hline(x + 1, x + 18, y + 1, shift(col, 1))
        c.hline(0, W - 1, y + 8, S_[3])
        for x in range(-off, W, 20):
            c.vline(x + 19, y, y + 8, S_[3])
    c.tone(0, 0, W - 1, 1, -1)
    # portão basculante (direita)
    c.box(164, 2, 238, F, S_[5])
    for y in range(4, F, 4):
        c.hline(165, 237, y, S_[3]); c.hline(165, 237, y + 1, "#fffbef")
    c.rect(196, F - 8, 206, F - 6, S_[2]); c.hline(196, 206, F - 8, S_[3])
    c.tone(165, 3, 172, F - 1, -1)
    # painel de ferramentas com sombras
    c.box(84, 6, 150, 36, W_[4])
    for x in range(88, 148, 5):
        for y in range(10, 34, 5):
            c.set(x, y, W_[2])
    tools = Sprite(60, 26)
    tools.rect(2, 4, 4, 22, W_[2]); tools.rect(0, 2, 7, 6, S_[3]); tools.hline(0, 7, 2, S_[5])                 # martelo
    tools.rect(14, 4, 15, 22, S_[4]); tools.ell(14, 3, 3, 3, S_[4]); tools.set(14, 2, None)                  # chave
    tools.rect(24, 2, 33, 10, CR[3]); tools.hline(24, 33, 2, CR[4]); tools.rect(26, 11, 30, 20, OL); tools.rect(33, 5, 38, 7, S_[3])  # furadeira
    tools.rect(44, 2, 45, 20, G_[2]); tools.rect(49, 2, 50, 20, S_[4]); tools.rect(54, 2, 55, 20, W_[2])      # chaves de fenda
    tools.rect(43, 20, 46, 24, CR[2]); tools.rect(48, 20, 51, 24, D_[2]); tools.rect(53, 20, 56, 24, G_[3])
    tools.stamp_on(c, 88, 8)
    c.tone(150, 8, 151, 37, -1); c.tone(85, 37, 151, 37, -1)
    # prateleira com latas e galão
    c.box(10, 18, 70, 21, W_[3]); c.tone(11, 22, 70, 23, -1)
    for i, (col, h) in enumerate(((CR[3], 8), (D_[3], 7), (G_[3], 9), (L_[4], 6))):
        cn = Sprite(8, h); cn.rect(0, 0, 7, h - 1, col); cn.vline(0, 0, h - 1, shift(col, 1)); cn.hline(0, 7, 0, S_[5]); cn.rect(2, 3, 5, 4, "#fffbef")
        cn.stamp_on(c, 14 + i * 13, 17 - h)
    # chão de cimento com manchas
    c.rect(0, F, W - 1, H - 1, S_[4])
    for _ in range(500):
        c.set(r.uniform(0, W), r.uniform(F, H), r.choice([S_[3], S_[3], S_[5]]))
    for y in range(F + 30, H, 40):
        c.hline(0, W - 1, y, S_[3])
    baseboard(c, F, S_[3])
    c.tone(150, 112, 200, 124, -1, mask=lambda x, y: ((x - 175) / 25) ** 2 + ((y - 118) / 6) ** 2 <= 1)
    c.tone(160, 114, 192, 122, -1, mask=lambda x, y: ((x - 175) / 14) ** 2 + ((y - 118) / 3.5) ** 2 <= 1)
    # pneus empilhados
    for i in range(3):
        y = 116 - i * 8
        c.ell(222, y, 16, 6, OL); c.ell(222, y, 15, 5, S_[2]); c.ell(222, y - 1, 13, 3, S_[3]); c.ell(222, y, 6, 2, S_[1])
    # CARRO: hatch vermelho de lado, com reflexos e sombra
    car = Sprite(112, 54)
    car.poly([(26, 2), (70, 2), (84, 20), (14, 20)], CR[3])                 # cabine
    car.poly([(30, 5), (50, 5), (50, 18), (22, 18)], D_[3]); car.poly([(53, 5), (68, 5), (78, 18), (53, 18)], D_[3])
    car.line(32, 6, 26, 16, D_[4]); car.line(57, 6, 55, 16, D_[4])
    car.hline(28, 68, 2, CR[4])
    car.rect(0, 20, 111, 40, CR[3]); car.hline(0, 111, 20, CR[4]); car.hline(0, 111, 21, CR[4])
    car.rect(0, 34, 111, 40, CR[2]); car.hline(0, 111, 40, CR[1])
    car.vline(51, 21, 38, CR[1]); car.rect(40, 26, 46, 27, S_[5]); car.rect(60, 26, 66, 27, S_[5])
    car.rect(104, 23, 110, 29, G_[4]); car.rect(0, 23, 4, 29, CR[4])
    car.rect(0, 41, 111, 44, S_[3]); car.hline(0, 111, 41, S_[5])
    for wx in (24, 88):
        car.ell(wx, 44, 10, 10, OL); car.ell(wx, 44, 8, 8, S_[2]); car.ell(wx, 44, 4, 4, S_[4]); car.set(wx - 1, 42, "#fffbef")
    for wx in (24, 88):
        for yy in range(30, 34):
            car.hline(wx - 12, wx + 12, yy, None) if False else None
    car.line(18, 22, 40, 22, "#fffbef")
    car.stamp_on(c, 6, 62)
    c.tone(8, 116, 118, 120, -1); c.tone(14, 121, 112, 122, -1, dither=0)
    # caixa de ferramentas no chão
    tb = Sprite(22, 12); tb.rect(0, 3, 21, 11, CR[2]); tb.rect(0, 3, 21, 5, CR[3]); tb.rect(7, 0, 14, 2, S_[2]); tb.set(10, 7, S_[5])
    tb.stamp_on(c, 132, 120)
    return c, {"w": W, "h": H, "floor": F}


# ======================================================================= 3 · Porão Abandonado (320x180)
def porao():
    W, H, F = 320, 180, 70
    c = Cv(W, H, 4)
    r = random.Random(41)
    # parede de pedra irregular com musgo
    c.rect(0, 0, W - 1, F - 1, S_[2])
    y = 0
    while y < F:
        rh = r.randrange(8, 12)
        x = -r.randrange(0, 12)
        while x < W:
            rw = r.randrange(14, 24)
            col = r.choice([S_[2], S_[3], S_[2], S_[3], S_[4]])
            c.rect(x + 1, y + 1, x + rw - 2, y + rh - 2, col)
            c.hline(x + 2, x + rw - 3, y + 1, shift(col, 1))
            c.vline(x + 1, y + 2, y + rh - 3, shift(col, 1))
            c.hline(x + 2, x + rw - 2, y + rh - 2, shift(col, -1))
            if r.random() < 0.25:
                for _ in range(5):
                    c.set(x + r.randrange(2, rw - 2), y + rh - 3 - r.randrange(0, 3), r.choice([L_[1], L_[2]]))
            x += rw
        y += rh
    for _ in range(80):
        c.set(r.uniform(0, W), r.uniform(0, F), S_[1])
    # canos no teto, com pingos e ferrugem
    c.rect(0, 3, W - 1, 9, S_[3]); c.hline(0, W - 1, 3, S_[5]); c.hline(0, W - 1, 4, S_[4]); c.hline(0, W - 1, 9, S_[1]); c.hline(0, W - 1, 10, OL)
    for x in range(24, W, 62):
        c.box(x, 1, x + 7, 12, G_[1]); c.vline(x + 1, 2, 11, G_[2])
    c.rect(98, 10, 104, 58, S_[3]); c.vline(98, 10, 58, S_[5]); c.vline(104, 10, 58, S_[1])
    c.box(95, 56, 107, 61, G_[1])
    for (x, y) in ((100, 30), (102, 44), (60, 8), (180, 7)):
        c.set(x, y, G_[1]); c.set(x + 1, y, G_[0])
    # caldeira enferrujada
    bl = Sprite(48, 72)
    bl.rect(0, 0, 47, 71, G_[1]); bl.rect(0, 0, 8, 71, G_[2]); bl.rect(38, 0, 47, 71, G_[0])
    for yy in (10, 34, 58):
        bl.hline(0, 47, yy, G_[0]); bl.hline(0, 47, yy + 1, G_[2])
    bl.ell(24, 24, 9, 9, OL); bl.ell(24, 24, 8, 8, "#fffbef"); bl.line(24, 24, 28, 19, CR[2]); bl.ell(24, 24, 1, 1, OL)
    bl.rect(12, 44, 36, 54, S_[1]); bl.rect(14, 46, 34, 52, CR[1])
    for _ in range(40):
        bl.set(r.randrange(2, 46), r.randrange(2, 70), r.choice([SO[2], G_[0], SO[3]]))
    bl.stamp_on(c, 264, 10)
    # chão de cimento rachado, úmido
    c.rect(0, F, W - 1, H - 1, S_[2])
    for _ in range(700):
        c.set(r.uniform(0, W), r.uniform(F, H), r.choice([S_[1], S_[1], S_[3]]))
    for (pts) in ([(40, 100), (55, 108), (52, 120), (66, 130)], [(220, 150), (236, 146), (250, 156)]):
        for (a, b) in zip(pts, pts[1:]):
            c.line(*a, *b, S_[1])
    baseboard(c, F, S_[1])
    # poça onde a goteira cai
    c.ell(206, 158, 30, 7, OL); c.ell(206, 158, 29, 6, D_[1]); c.ell(204, 157, 22, 4, D_[2]); c.hline(192, 202, 155, D_[3])
    c.ell(101, 150, 12, 3, D_[1])
    # caixas velhas e cadeira quebrada
    cr = Sprite(34, 28)
    cr.rect(0, 0, 33, 5, W_[3]); cr.hline(0, 33, 0, W_[4]); cr.rect(0, 6, 33, 27, W_[2])
    for yy in (11, 17, 23):
        cr.hline(0, 33, yy, W_[1])
    cr.line(2, 7, 31, 26, W_[3]); cr.rect(10, 12, 22, 15, PA[3])
    cr.stamp_on(c, 12, 118)
    cr2 = Sprite(26, 20); cr2.rect(0, 0, 25, 4, W_[4]); cr2.rect(0, 5, 25, 19, W_[3]); cr2.hline(0, 25, 12, W_[2])
    cr2.stamp_on(c, 18, 100)
    c.tone(14, 147, 48, 149, -1)
    ch = Sprite(20, 26)
    ch.rect(0, 0, 3, 25, W_[2]); ch.rect(0, 10, 19, 13, W_[3]); ch.rect(16, 14, 18, 25, W_[2]); ch.line(4, 4, 15, 9, W_[2])
    ch.stamp_on(c, 280, 128)
    # teias de aranha nos cantos
    for (x0, sx) in ((0, 1), (W - 1, -1)):
        for i in range(18):
            c.set(x0 + sx * i, 11 + i * 0.9, S_[5])
        for k in range(4, 18, 5):
            for j in range(k):
                c.set(x0 + sx * j, 11 + k * 0.9 - j * 0.15, S_[5])
    # fio da lâmpada
    c.vline(160, 11, 26, OL)
    return c, {"w": W, "h": H, "floor": F, "dark": {"a": 0.62, "tint": "26,20,32", "lights": [[160, 34, 130]], "flicker": True, "bulb": [160, 30]},
               "drips": [[206, 11, 156], [101, 62, 148]]}




# ======================================================================= utilidades extras
FONT = {
    "G": ["0111", "1000", "1011", "1001", "0111"], "R": ["1110", "1001", "1110", "1010", "1001"],
    "N": ["1001", "1101", "1011", "1001", "1001"], "0": ["0110", "1001", "1001", "1001", "0110"],
    "4": ["1001", "1001", "1111", "0001", "0001"], "5": ["1111", "1000", "1110", "0001", "1110"],
    "1": ["0010", "0110", "0010", "0010", "0111"], " ": ["0000"] * 5, "-": ["0000", "0000", "1111", "0000", "0000"],
    "B": ["1110", "1001", "1110", "1001", "1110"], "K": ["1001", "1010", "1100", "1010", "1001"],
    "E": ["1111", "1000", "1110", "1000", "1111"], "U": ["1001", "1001", "1001", "1001", "0110"],
    "7": ["1111", "0001", "0010", "0100", "0100"], "A": ["0110", "1001", "1111", "1001", "1001"],
    "X": ["1001", "1001", "0110", "1001", "1001"], "C": ["0111", "1000", "1000", "1000", "0111"],
    "S": ["0111", "1000", "0110", "0001", "1110"], "T": ["1111", "0100", "0100", "0100", "0100"],
}


def text(c, x, y, s, col, scale=1):
    for ch in s:
        g = FONT.get(ch, FONT[" "])
        for j, row in enumerate(g):
            for i, b in enumerate(row):
                if b == "1":
                    c.rect(x + i * scale, y + j * scale, x + i * scale + scale - 1, y + j * scale + scale - 1, col)
        x += 5 * scale


def sky(c, y0, y1, cols=None):
    cols = cols or [D_[4], D_[4], D_[3]]
    for y in range(y0, y1):
        t = (y - y0) / max(1, y1 - y0)
        c.hline(0, c.w - 1, y, cols[min(len(cols) - 1, int(t * len(cols)))])
    # faixa de transição pontilhada
    for k in range(1, len(cols)):
        yb = y0 + int((y1 - y0) * k / len(cols))
        for x in range(0, c.w, 2):
            c.set(x + (yb % 2), yb - 1, cols[k])


def cloud(c, x, y, w):
    for i, (dx, dy, r) in enumerate(((0, 0, w * 0.22), (w * 0.25, -w * 0.08, w * 0.28), (w * 0.55, 0, w * 0.22), (w * 0.3, w * 0.06, w * 0.25))):
        c.ell(x + dx, y + dy, r, r * 0.55, "#fffbef")
    c.hline(int(x - w * 0.15), int(x + w * 0.7), int(y + w * 0.12), S_[6])


def tree_crown(c, cx, cy, r, ramp=None, seed=1):
    ramp = ramp or L_
    rr = random.Random(seed)
    blobs = [(cx + rr.uniform(-r, r) * 0.7, cy + rr.uniform(-r, r) * 0.5, r * rr.uniform(0.45, 0.7)) for _ in range(7)]
    blobs.sort(key=lambda b: b[1])
    for (x, y, br) in blobs:
        c.ell(x, y, br + 1, br * 0.85 + 1, OL)
    for (x, y, br) in blobs:
        for yy in range(int(y - br), int(y + br) + 1):
            for xx in range(int(x - br), int(x + br) + 1):
                nx, ny = (xx - x) / br, (yy - y) / (br * 0.85)
                d = nx * nx + ny * ny
                if d <= 1:
                    lit = -(-0.55 * nx - 0.8 * ny)
                    i = 1 if lit < -0.35 else 2 if lit < 0.1 else 3 if lit < 0.5 else 4
                    c.set(xx, yy, ramp[i])


def concrete(c, y0, base=4, seed=9, joints=40):
    r = random.Random(seed)
    c.rect(0, y0, c.w - 1, c.h - 1, S_[base])
    for _ in range(int(c.w * (c.h - y0) / 18)):
        c.set(r.uniform(0, c.w), r.uniform(y0, c.h), r.choice([S_[base - 1], S_[base - 1], S_[base + 1]]))
    for y in range(y0 + joints, c.h, joints):
        c.hline(0, c.w - 1, y, S_[base - 1])
    for x in range(joints * 2, c.w, joints * 3):
        c.vline(x, y0 + 4, c.h - 1, S_[base - 1])


def corrugated(c, y0, y1, ramp, base=2, step=6):
    for x in range(0, c.w, step):
        c.rect(x, y0, x + step - 1, y1, ramp[base])
        c.vline(x, y0, y1, ramp[base + 1] if base + 1 < len(ramp) else ramp[base])
        c.vline(x + 1, y0, y1, ramp[base + 1] if base + 1 < len(ramp) else ramp[base])
        c.vline(x + step - 2, y0, y1, ramp[base - 1])


def pallet(c, x, y, w=44, h=7, load=None):
    p = Sprite(w, h + (load[1] if load else 0))
    if load:
        col, lh = load
        p.rect(0, 0, w - 1, lh - 1, col); p.hline(0, w - 1, 0, shift(col, 1)); p.vline(0, 0, lh - 1, shift(col, 1))
        for xx in range(4, w, 10):
            p.vline(xx, 1, lh - 2, shift(col, -1))
        off = lh
    else:
        off = 0
    p.rect(0, off, w - 1, off + h - 1, W_[4]); p.hline(0, w - 1, off, W_[5])
    for xx in (2, w // 2 - 3, w - 8):
        p.rect(xx, off + 3, xx + 5, off + h - 1, W_[2])
    p.stamp_on(c, x, y)
    c.tone(x + 2, y + p.h + 1, x + w + 1, y + p.h + 2, -1)


def barrel(c, x, y, col=None):
    col = col or B_[2]
    b = Sprite(16, 22)
    for xx in range(16):
        t = xx / 15
        cc = shift(col, 1) if t < 0.25 else col if t < 0.7 else shift(col, -1)
        b.vline(xx, 1, 21, cc)
    b.ell(7.5, 2, 7.5, 2, shift(col, 1)); b.ell(7.5, 2, 5, 1, shift(col, -1))
    for yy in (7, 15):
        b.hline(0, 15, yy, shift(col, -2))
    b.stamp_on(c, x, y)
    c.tone(x + 2, y + 23, x + 19, y + 24, -1)


# ======================================================================= 4 · Terreno Abandonado (320x180)
def terreno():
    W, H, F = 320, 180, 72
    c = Cv(W, H, 5); r = random.Random(51)
    sky(c, 0, 40)
    cloud(c, 40, 12, 34); cloud(c, 210, 8, 26)
    x = 0
    while x < W:                                                # prédios ao fundo
        bw = r.randrange(20, 34); bh = r.randrange(14, 30)
        col = r.choice([S_[4], S_[4], S_[3]])
        c.rect(x, 40 - bh, x + bw - 1, 44, col); c.vline(x, 40 - bh, 44, shift(col, 1))
        for wy in range(42 - bh, 42, 4):
            for wx in range(x + 3, x + bw - 3, 4):
                if r.random() < 0.55:
                    c.set(wx, wy, S_[5] if r.random() < 0.7 else G_[4])
        x += bw + r.randrange(0, 6)
    # muro de tábuas (com frestas, pregos, pichação)
    for x in range(0, W, 13):
        col = r.choice([W_[3], W_[3], W_[4], W_[2]])
        top = 36 + r.randrange(0, 4)
        c.rect(x, top, x + 11, F - 1, col)
        c.vline(x, top, F - 1, shift(col, 1)); c.vline(x + 11, top, F - 1, shift(col, -1)); c.vline(x + 12, top + 2, F - 1, W_[0])
        c.poly([(x, top), (x + 6, top - 4), (x + 12, top)], col)
        for yy in (top + 6, F - 8):
            c.set(x + 5, yy, S_[2])
        for _ in range(3):
            gy = r.randrange(top + 4, F - 2); c.vline(x + r.randrange(2, 10), gy, gy + r.randrange(3, 8), shift(col, -1))
    # pichação em letras grandes com contorno
    gr = Sprite(80, 22)
    for i, (col, dx) in enumerate(((CR[3], 0), (G_[3], 18), (L_[4], 36), (D_[3], 54))):
        gr.ell(dx + 9, 11, 9, 10, col); gr.ell(dx + 9, 11, 4, 5, shift(col, 1)); gr.ell(dx + 7, 8, 2, 2, "#fffbef")
    gr.stamp_on(c, 118, 42)
    c.line(116, 66, 200, 64, PL[3]); c.line(116, 67, 200, 65, PL[2])
    # árvore grande à esquerda
    c.rect(18, 28, 26, F + 26, W_[1]); c.vline(19, 28, F + 26, W_[2]); c.vline(20, 28, F + 26, W_[2])
    c.line(22, 40, 8, 26, W_[1]); c.line(24, 36, 40, 22, W_[1])
    tree_crown(c, 24, 20, 26, seed=4)
    c.tone(10, F + 22, 70, F + 30, -1, mask=lambda x, y: ((x - 40) / 30) ** 2 + ((y - F - 26) / 4) ** 2 <= 1)
    # chão de terra com mato
    c.rect(0, F, W - 1, H - 1, SO[3])
    for _ in range(1400):
        c.set(r.uniform(0, W), r.uniform(F, H), r.choice([SO[2], SO[2], W_[4], SO[3]]))
    c.tone(0, F, W - 1, F + 2, -1)
    for _ in range(46):
        gx, gy = r.uniform(0, W), r.uniform(F + 4, H - 2)
        for k in range(7):
            hgt = r.randrange(2, 6)
            c.vline(gx + k, gy - hgt, gy, r.choice([L_[3], L_[4], L_[2]]))
        c.tone(gx, gy + 1, gx + 7, gy + 1, -1)
    # entulho: tijolos, pneu, TV quebrada, carrinho de supermercado
    for i in range(6):
        bx = 250 + (i % 3) * 10 + (i // 3) * 5; by = 160 - (i // 3) * 5
        b = Sprite(10, 5); b.rect(0, 0, 9, 4, B_[2]); b.hline(0, 9, 0, B_[3]); b.set(3, 2, B_[1]); b.stamp_on(c, bx, by)
    c.ell(292, 140, 16, 6, OL); c.ell(292, 140, 15, 5, S_[2]); c.ell(292, 139, 13, 3, S_[3]); c.ell(292, 140, 6, 2, SO[2])
    tv = Sprite(30, 24)
    tv.rect(0, 0, 29, 23, S_[3]); tv.hline(0, 29, 0, S_[4]); tv.rect(3, 3, 22, 19, S_[1]); tv.line(6, 5, 18, 17, S_[5]); tv.line(9, 4, 20, 12, S_[4])
    tv.ell(26, 7, 1, 1, S_[2]); tv.ell(26, 12, 1, 1, S_[2])
    tv.stamp_on(c, 60, 146)
    cart = Sprite(34, 26)
    for xx in range(2, 32, 4):
        cart.vline(xx, 0, 16, S_[5])
    for yy in range(0, 17, 4):
        cart.hline(1, 32, yy, S_[5])
    cart.rect(0, 16, 33, 17, S_[4]); cart.ell(5, 23, 2, 2, OL); cart.ell(28, 23, 2, 2, OL)
    cart.stamp_on(c, 196, 120)
    return c, {"w": W, "h": H, "floor": F}


# ======================================================================= 5 · Container Marítimo (320x180)
def container():
    W, H, F = 320, 180, 72
    c = Cv(W, H, 6); r = random.Random(61)
    corrugated(c, 0, F - 1, B_, base=3, step=8)
    c.rect(0, 0, W - 1, 5, B_[1]); c.hline(0, W - 1, 6, OL); c.tone(0, 7, W - 1, 9, -1)
    for _ in range(90):                                        # ferrugem
        x, y = r.uniform(0, W), r.uniform(8, F)
        c.rect(x, y, x + r.randrange(1, 4), y + r.randrange(1, 3), r.choice([SO[2], G_[1], B_[1]]))
    # placa de identificação com estêncil
    c.box(96, 18, 220, 44, B_[3], B_[1])
    text(c, 108, 24, "GRN 0451", "#fffbef", 3)
    c.rect(104, 21, 212, 21, B_[4])
    # barras de travamento da porta (lado direito, vistas por dentro)
    for x in (258, 284):
        c.rect(x, 6, x + 5, F - 1, S_[3]); c.vline(x, 6, F - 1, S_[5]); c.vline(x + 5, 6, F - 1, S_[2])
        c.box(x - 3, 30, x + 8, 38, S_[3]); c.hline(x - 2, x + 7, 31, S_[5])
    c.vline(306, 6, F - 1, OL)
    c.tone_poly([(307, 6), (319, 6), (319, F + 40), (300, H)], 1, dither=0)        # luz pela fresta da porta
    # fita de LED (gambiarra presa com fita)
    c.hline(0, W - 1, 11, TE[4]); c.hline(0, W - 1, 12, TE[3])
    for x in range(30, W, 70):
        c.rect(x, 10, x + 4, 13, S_[4])
    # piso de compensado
    c.rect(0, F, W - 1, H - 1, W_[3])
    for y in range(F, H, 18):
        c.hline(0, W - 1, y, W_[2])
        for x in range((y // 18 % 2) * 40, W, 80):
            c.vline(x, y, y + 17, W_[2])
        for _ in range(14):
            c.set(r.uniform(0, W), r.uniform(y + 2, y + 16), W_[2])
    baseboard(c, F, B_[1])
    # carga: palete com fardo, galões, saco de dormir, ventilador de pé
    pallet(c, 10, 100, 50, 7, (S_[5], 20))
    for i in range(3):
        g = Sprite(12, 18); g.rect(0, 2, 11, 17, CR[3] if i != 1 else G_[3]); g.rect(4, 0, 7, 2, S_[2]); g.vline(1, 3, 16, CR[4] if i != 1 else G_[4]); g.rect(3, 7, 8, 10, "#fffbef")
        g.stamp_on(c, 268 + i * 14, 140 - (i % 2) * 2)
    c.tone(268, 159, 310, 160, -1)
    sb = Sprite(46, 14); sb.ell(23, 7, 22, 6, D_[2]); sb.ell(23, 5, 20, 3, D_[3]); sb.ell(6, 7, 5, 5, D_[1]); sb.line(10, 4, 40, 10, D_[1])
    sb.stamp_on(c, 74, 156)
    fan = Sprite(22, 40)
    fan.ell(11, 10, 10, 10, S_[3]); fan.ell(11, 10, 8, 8, S_[4])
    for a in range(0, 360, 90):
        fan.line(11, 10, 11 + 7 * math.cos(math.radians(a + 20)), 10 + 7 * math.sin(math.radians(a + 20)), S_[2])
    fan.ell(11, 10, 2, 2, S_[2]); fan.rect(10, 20, 12, 35, S_[2]); fan.rect(4, 36, 18, 39, S_[2])
    fan.stamp_on(c, 226, 92)
    return c, {"w": W, "h": H, "floor": F}


# ======================================================================= 6 · Sobrado na Favela (320x180)
def sobrado():
    W, H, F = 320, 180, 72
    c = Cv(W, H, 7); r = random.Random(71)
    # tijolo baiano aparente com reboco caindo
    c.rect(0, 0, W - 1, F - 1, B_[1])
    for y in range(0, F, 7):
        off = 0 if (y // 7) % 2 else 7
        for x in range(-off, W, 14):
            col = r.choice([B_[3], B_[3], B_[2], B_[4]])
            c.rect(x + 1, y + 1, x + 12, y + 5, col); c.hline(x + 1, x + 12, y + 1, shift(col, 1))
            c.vline(x + 4, y + 2, y + 4, shift(col, -1)); c.vline(x + 8, y + 2, y + 4, shift(col, -1))
    for (x, y, w, h) in ((20, 6, 50, 24), (232, 40, 40, 20)):                      # reboco
        c.tone(x, y, x + w, y + h, 0)
        c.rect(x, y, x + w, y + h, S_[5])
        for yy in range(y, y + h):
            c.set(x + r.randrange(0, w), yy, S_[4])
        for k in range(0, w, 3):
            c.set(x + k, y + h + r.randrange(0, 3), S_[5])
    # janela com o morro
    window(c, 128, 8, 96, 46, S_[3])
    for y in range(8, 54):
        c.hline(128, 223, y, D_[4] if y < 22 else L_[3])
    c.ell(206, 14, 4, 4, G_[4])
    houses = [CR[3], G_[3], D_[3], L_[5], B_[4], S_[5], CR[4], TE[3], PL[3]]
    for row in range(5):
        for i in range(12):
            hx = 128 + i * 8 + (row % 2) * 4; hy = 16 + row * 7
            if hx + 7 > 223:
                continue
            col = houses[(i * 3 + row * 5) % len(houses)]
            c.rect(hx, hy, hx + 7, hy + 7, col); c.hline(hx, hx + 7, hy, OL)
            c.set(hx + 2, hy + 3, OL); c.set(hx + 5, hy + 3, D_[1])
            if (i + row) % 4 == 0:
                c.rect(hx + 2, hy - 2, hx + 5, hy - 1, D_[2])                     # caixa d'água
    c.line(128, 20, 223, 26, OL); c.line(128, 30, 223, 24, OL)                   # fios
    c.vline(176, 8, 53, S_[3]); c.vline(177, 8, 53, S_[2]); c.hline(128, 223, 31, S_[3])
    # gambiarra de fios na parede
    c.line(20, 0, 26, 40, OL); c.line(26, 40, 60, 46, OL); c.box(58, 42, 66, 50, "#fffbef")
    # ventilador de teto
    c.vline(90, 0, 8, S_[2])
    fan = Sprite(50, 6); fan.rect(0, 2, 49, 3, W_[2]); fan.hline(0, 49, 2, W_[3]); fan.ell(25, 3, 4, 3, S_[3]); fan.stamp_on(c, 65, 8)
    # piso de cerâmica
    c.rect(0, F, W - 1, H - 1, S_[5])
    for y in range(F, H, 16):
        for x in range((y // 16 % 2) * 8, W, 16):
            col = r.choice([S_[5], S_[5], S_[6]])
            c.rect(x + 1, y + 1, x + 15, y + 15, col)
        c.hline(0, W - 1, y, S_[4])
    for x in range(0, W, 16):
        c.vline(x, F, H - 1, S_[4])
    baseboard(c, F, B_[1])
    # sofá verde com almofadas
    so = Sprite(74, 44)
    so.rect(0, 0, 73, 18, L_[2]); so.hline(0, 73, 0, L_[3]); so.hline(0, 73, 1, L_[3])
    so.rect(0, 18, 73, 36, L_[3]); so.hline(0, 73, 18, L_[4]); so.vline(36, 19, 33, L_[2])
    so.rect(0, 8, 7, 40, L_[2]); so.rect(66, 8, 73, 40, L_[1]); so.vline(0, 8, 40, L_[3])
    so.rect(2, 37, 71, 43, L_[1])
    so.rect(12, 12, 26, 24, CR[3]); so.hline(12, 26, 12, CR[4]); so.rect(44, 13, 56, 24, G_[3]); so.hline(44, 56, 13, G_[4])
    so.stamp_on(c, 6, 54)
    c.tone(8, 99, 84, 101, -1)
    # TV de tubo no caixote + antena de palha de aço
    cx = Sprite(40, 24); cx.rect(0, 0, 39, 23, W_[3]); cx.hline(0, 39, 0, W_[4])
    for yy in (7, 15):
        cx.hline(0, 39, yy, W_[2])
    cx.stamp_on(c, 268, 112)
    tv = Sprite(44, 34); tv.rect(0, 0, 43, 33, S_[2]); tv.hline(0, 43, 0, S_[3]); tv.rect(3, 3, 32, 28, TE[1]); tv.rect(5, 5, 14, 8, TE[3]); tv.rect(35, 6, 40, 9, S_[1]); tv.rect(35, 13, 40, 16, S_[1])
    tv.stamp_on(c, 266, 78)
    c.line(276, 78, 268, 64, S_[4]); c.line(296, 78, 304, 64, S_[4]); c.ell(268, 63, 3, 2, S_[5])
    # cadeira de plástico e botijão
    ch = Sprite(20, 28); ch.rect(0, 0, 19, 10, "#fffbef"); ch.rect(0, 11, 19, 14, S_[6]); ch.rect(1, 15, 3, 27, S_[6]); ch.rect(16, 15, 18, 27, S_[5])
    ch.stamp_on(c, 220, 120)
    bj = Sprite(16, 22); bj.ell(8, 12, 7, 9, D_[2]); bj.ell(6, 10, 3, 5, D_[3]); bj.rect(5, 0, 10, 4, S_[3]); bj.stamp_on(c, 92, 148)
    return c, {"w": W, "h": H, "floor": F}


# ======================================================================= 7 · Galpão Industrial (320x180)
def galpao():
    W, H, F = 320, 180, 70
    c = Cv(W, H, 8); r = random.Random(81)
    corrugated(c, 0, F - 1, S_, base=3, step=6)
    # vigas e colunas de aço
    for x in (0, 104, 208, 312):
        c.rect(x, 0, x + 7, F - 1, S_[2]); c.vline(x + 1, 0, F - 1, S_[4]); c.vline(x + 7, 0, F - 1, S_[1])
    c.rect(0, 0, W - 1, 4, S_[2]); c.hline(0, W - 1, 1, S_[4]); c.hline(0, W - 1, 5, OL)
    for x in range(0, W, 16):
        c.line(x, 5, x + 8, 0, S_[1])
    # janelas altas
    for x in (26, 130, 234):
        window(c, x, 10, 52, 18, S_[2])
    # luz entrando em feixes diagonais
    for x in (26, 130, 234):
        c.tone_poly([(x, F), (x + 52, F), (x + 92, H), (x + 30, H)], 1)
        c.tone_poly([(x - 4, F), (x, F), (x + 30, H), (x + 24, H)], 1, dither=1)
    # luminárias industriais penduradas
    for x in (78, 182, 286):
        c.vline(x, 5, 18, OL)
        lm = Sprite(20, 8); lm.poly([(5, 0), (14, 0), (19, 6), (0, 6)], S_[2]); lm.hline(5, 14, 0, S_[4]); lm.rect(5, 6, 14, 7, G_[4]); lm.stamp_on(c, x - 10, 18)
    concrete(c, F, base=4, seed=82, joints=36)
    for x in range(0, W):                                                       # faixa de segurança
        c.vline(x, F + 8, F + 10, G_[3] if (x // 8) % 2 else OL)
    baseboard(c, F, S_[2])
    # paletes empilhados com caixas
    for i in range(3):
        pallet(c, 8, 150 - i * 15, 52, 6, (W_[4] if i % 2 else W_[3], 9))
    # barris
    barrel(c, 268, 150, D_[2]); barrel(c, 286, 154, B_[2]); barrel(c, 277, 132, G_[2])
    # empilhadeira
    fk = Sprite(56, 54)
    fk.rect(14, 22, 55, 44, G_[3]); fk.hline(14, 55, 22, G_[4]); fk.rect(14, 38, 55, 44, G_[2])
    fk.rect(22, 2, 50, 22, S_[1]); fk.rect(25, 5, 47, 20, D_[4]); fk.line(26, 6, 30, 18, "#fffbef")
    fk.rect(20, 0, 52, 2, G_[2])
    fk.rect(6, 4, 9, 50, S_[2]); fk.vline(6, 4, 50, S_[4]); fk.rect(0, 46, 14, 49, S_[2])
    for wx in (24, 48):
        fk.ell(wx, 46, 7, 7, OL); fk.ell(wx, 46, 5, 5, S_[2]); fk.ell(wx, 46, 2, 2, S_[4])
    fk.stamp_on(c, 200, 120)
    c.tone(200, 175, 258, 177, -1)
    return c, {"w": W, "h": H, "floor": F}


# ======================================================================= 8 · Sítio na Serra (320x180)
def sitio():
    W, H, F = 320, 180, 72
    c = Cv(W, H, 9); r = random.Random(91)
    # parede de troncos
    for y in range(0, F, 9):
        c.rect(0, y, W - 1, y + 8, W_[3]); c.hline(0, W - 1, y, W_[4]); c.hline(0, W - 1, y + 1, W_[4]); c.hline(0, W - 1, y + 7, W_[2]); c.hline(0, W - 1, y + 8, W_[1])
        for _ in range(6):
            gx = r.uniform(0, W); c.hline(gx, gx + r.uniform(6, 16), y + r.randrange(3, 6), W_[2])
        for x in (2, W - 9):
            c.ell(x + 3, y + 4, 4, 4, W_[1]); c.ell(x + 3, y + 4, 3, 3, W_[4]); c.ell(x + 3, y + 4, 1, 1, W_[2])
    # janela com montanhas e pinheiros
    window(c, 100, 8, 84, 42, W_[2])
    for y in range(8, 50):
        c.hline(100, 183, y, D_[4] if y < 26 else D_[3])
    c.poly([(100, 50), (128, 16), (150, 50)], S_[4]); c.poly([(120, 22), (128, 16), (136, 22)], "#fffbef")
    c.poly([(132, 50), (162, 12), (184, 50)], S_[3]); c.poly([(155, 20), (162, 12), (169, 20)], "#fffbef")
    c.rect(100, 40, 183, 49, L_[3])
    for x in range(102, 182, 7):
        c.poly([(x, 46), (x + 3, 34 + (x % 3) * 2), (x + 6, 46)], L_[1])
    c.vline(141, 8, 49, W_[2]); c.vline(142, 8, 49, W_[1]); c.hline(100, 183, 29, W_[2])
    # prateleira com potes de conserva
    c.box(30, 26, 84, 29, W_[2])
    for i, col in enumerate((CR[3], G_[3], L_[4], CR[2], G_[2])):
        jar = Sprite(8, 10); jar.rect(0, 2, 7, 9, col); jar.rect(1, 0, 6, 1, S_[3]); jar.vline(1, 3, 8, shift(col, 1)); jar.rect(2, 5, 5, 6, PA[4])
        jar.stamp_on(c, 33 + i * 10, 16)
    # lareira de pedra com fogo (o fogo é animado)
    fp = Sprite(78, F + 10)
    for y in range(0, F + 10, 7):
        for x in range((y // 7 % 2) * 5, 78, 11):
            col = r.choice([S_[4], S_[3], S_[4], S_[5]])
            fp.rect(x, y, x + 9, y + 5, col); fp.hline(x, x + 9, y, shift(col, 1))
    fp.rect(14, 38, 63, F + 9, S_[1]); fp.rect(18, 42, 59, F + 9, OL)
    fp.rect(8, 33, 69, 37, W_[2]); fp.hline(8, 69, 33, W_[3])
    fp.stamp_on(c, 238, 0)
    c.rect(258, F + 2, 296, F + 8, W_[1]); c.rect(262, F + 1, 292, F + 3, W_[2])         # lenha na lareira
    # piso de tábuas largas
    plank_floor(c, F + 4, base=4, plank_h=9, seed=93)
    c.rect(0, F, W - 1, F + 3, W_[2]); c.hline(0, W - 1, F + 3, OL)
    # tapete oval e lenha empilhada
    c.ell(90, 148, 56, 16, OL); c.ell(90, 148, 55, 15, CR[2]); c.ell(90, 148, 46, 11, CR[3]); c.ell(90, 148, 34, 7, G_[3]); c.ell(90, 148, 26, 4, CR[2])
    for i in range(7):
        lg = Sprite(30, 6); lg.rect(0, 0, 29, 5, W_[2]); lg.hline(0, 29, 0, W_[3]); lg.ell(1, 2, 2, 2, W_[4]); lg.set(1, 2, W_[2])
        lg.stamp_on(c, 250 + (i % 3) * 4, 150 - (i // 3) * 6 - (i % 3) * 2)
    # cadeira de balanço
    rk = Sprite(26, 40); rk.rect(2, 0, 21, 18, W_[2])
    for xx in range(4, 20, 4):
        rk.vline(xx, 2, 16, W_[3])
    rk.rect(0, 18, 23, 22, W_[3]); rk.rect(2, 22, 4, 34, W_[2]); rk.rect(19, 22, 21, 34, W_[2]); rk.line(0, 36, 25, 33, W_[1]); rk.line(0, 37, 25, 34, W_[1])
    rk.stamp_on(c, 190, 112)
    return c, {"w": W, "h": H, "floor": F, "anims": [["fire", 258, F + 1, 36]]}


# ======================================================================= 9 · Fazenda Paraíso Verde (320x180)
def fazenda():
    W, H, F = 320, 180, 68
    c = Cv(W, H, 10); r = random.Random(101)
    sky(c, 0, 36); cloud(c, 60, 10, 30); cloud(c, 220, 14, 22)
    c.ell(290, 10, 8, 8, G_[4]); c.ell(290, 10, 6, 6, "#fffbef")
    c.rect(0, 30, W - 1, F - 1, L_[3])                                            # campo
    for y in range(32, F, 3):
        c.hline(0, W - 1, y, L_[4] if (y // 3) % 2 else L_[3])
    # celeiro, silo e moinho
    bn = Sprite(46, 34)
    bn.rect(0, 12, 45, 33, CR[2]); bn.poly([(0, 13), (23, 0), (45, 13)], CR[1]); bn.rect(16, 18, 29, 33, "#fffbef"); bn.line(16, 18, 29, 33, "#fffbef")
    bn.rect(18, 20, 27, 31, CR[2]); bn.line(18, 20, 27, 31, "#fffbef"); bn.line(27, 20, 18, 31, "#fffbef"); bn.rect(20, 4, 25, 9, "#fffbef")
    bn.stamp_on(c, 196, 20)
    sl = Sprite(16, 40); sl.rect(0, 6, 15, 39, S_[5]); sl.ell(7.5, 6, 7.5, 6, S_[4]); sl.vline(0, 6, 39, "#fffbef"); sl.vline(15, 6, 39, S_[4])
    sl.stamp_on(c, 246, 14)
    c.vline(60, 22, 50, S_[3]); c.vline(61, 22, 50, S_[4])
    for a in (20, 110, 200, 290):
        c.line(60, 22, 60 + 12 * math.cos(math.radians(a)), 22 + 12 * math.sin(math.radians(a)), S_[5])
    # estrutura da estufa (vidro com caixilhos brancos e reflexos)
    for x in range(0, W, 46):
        c.rect(x, 0, x + 2, F - 1, S_[6]); c.vline(x + 2, 0, F - 1, S_[4])
    for y in (0, 22, 44):
        c.rect(0, y, W - 1, y + 1, S_[6])
    for x in range(10, W, 46):
        for k in range(10):
            c.set(x + k, 18 - k, "#fffbef"); c.set(x + k + 2, 18 - k, "#fffbef")
    # chão de terra com canteiros e sulcos de irrigação
    c.rect(0, F, W - 1, H - 1, SO[2])
    for y in range(F + 6, H, 22):
        c.rect(0, y, W - 1, y + 12, SO[3]); c.hline(0, W - 1, y, shift(SO[3], 1) if False else W_[3])
        c.hline(0, W - 1, y + 12, SO[1])
        c.rect(0, y + 13, W - 1, y + 16, D_[2]); c.hline(0, W - 1, y + 13, D_[3])
        for _ in range(60):
            c.set(r.uniform(0, W), r.uniform(y + 2, y + 11), r.choice([SO[2], W_[3]]))
    c.rect(0, F, W - 1, F + 2, S_[5]); c.hline(0, W - 1, F + 3, OL)
    # sol entrando em feixes
    for x in (40, 180):
        c.tone_poly([(x, F + 4), (x + 50, F + 4), (x + 80, H), (x + 30, H)], 1, dither=0)
    # carrinho de mão e sacos de adubo
    wb = Sprite(46, 22)
    wb.poly([(0, 2), (34, 2), (30, 14), (6, 14)], L_[3]); wb.hline(0, 34, 2, L_[4]); wb.rect(4, 0, 30, 3, SO[3])
    wb.line(34, 6, 45, 4, W_[2]); wb.line(30, 13, 44, 10, W_[2]); wb.ell(16, 18, 4, 4, OL); wb.ell(16, 18, 2, 2, S_[3]); wb.rect(8, 14, 9, 21, S_[2])
    wb.stamp_on(c, 14, 150)
    for i in range(3):
        sk = Sprite(18, 22); sk.ell(9, 12, 8, 10, PA[3]); sk.rect(1, 2, 16, 18, PA[3]); sk.rect(5, 0, 12, 3, PA[2]); sk.rect(4, 8, 13, 13, L_[3]); sk.vline(2, 4, 18, PA[4])
        sk.stamp_on(c, 272 + i * 15, 146 - (i % 2) * 4)
    return c, {"w": W, "h": H, "floor": F}


# ======================================================================= 10 · Ilha Privada (384x216)
def ilha():
    W, H, F = 384, 216, 84
    c = Cv(W, H, 11); r = random.Random(111)
    sky(c, 0, 46, [D_[4], D_[4], D_[4], D_[3]])
    cloud(c, 60, 14, 40); cloud(c, 250, 22, 28)
    c.ell(320, 20, 12, 12, G_[4]); c.ell(320, 20, 9, 9, "#fffbef")
    # mar com faixas e brilhos, ilha ao longe
    for y in range(46, 74):
        c.hline(0, W - 1, y, TE[2] if y < 56 else TE[3] if y < 66 else TE[3])
    for _ in range(80):
        x, y = r.uniform(0, W), r.uniform(48, 72); c.hline(x, x + r.randrange(3, 8), y, TE[4] if r.random() < 0.6 else "#fffbef")
    c.ell(140, 47, 26, 5, L_[2]); c.ell(140, 46, 18, 3, L_[3]); c.vline(146, 36, 44, W_[1]); c.ell(146, 36, 6, 2, L_[2])
    # areia
    c.rect(0, 74, W - 1, H - 1, W_[5])
    for y in range(74, 80):
        for x in range(0, W, 1):
            if r.random() < 0.4:
                c.set(x, y, "#fffbef")
    for _ in range(1800):
        c.set(r.uniform(0, W), r.uniform(80, H), r.choice([W_[4], W_[4], PA[3], PA[4]]))
    for (x, y) in ((60, 190), (300, 170), (220, 200)):                              # conchas
        c.ell(x, y, 3, 2, OL); c.ell(x, y, 2, 1, CR[4]); c.set(x, y - 1, "#fffbef")
    # coqueiros
    for (bx, flip) in ((24, 1), (356, -1)):
        for i in range(110):
            x = bx + flip * round(math.sin(i / 34) * 14)
            y = 150 - i
            c.rect(x, y, x + 7, y, W_[2] if (i // 4) % 2 else W_[3]); c.set(x, y, OL); c.set(x + 8, y, OL)
        tx = bx + flip * round(math.sin(110 / 34) * 14) + 4; ty = 40
        for (dx, dy) in ((-34, 10), (34, 10), (-24, -10), (24, -10), (-8, -20), (12, 22), (-16, 20)):
            leaf = [(tx, ty), (tx + dx * 0.5, ty + dy * 0.5 - 5), (tx + dx, ty + dy), (tx + dx * 0.5, ty + dy * 0.5 + 2)]
            c.poly([(p[0] - 1, p[1] - 1) for p in leaf], OL)
            c.poly(leaf, L_[3]); c.line(tx, ty, tx + dx, ty + dy, L_[2])
        for k in range(3):
            c.ell(tx - 3 + k * 4, ty + 5, 3, 3, OL); c.ell(tx - 3 + k * 4, ty + 5, 2, 2, W_[1])
        c.tone(bx - 6, 150, bx + 40, 156, -1, mask=lambda x, y, bx=bx: ((x - bx - 16) / 22) ** 2 + ((y - 153) / 3) ** 2 <= 1)
    # rede, cooler, prancha, tocha tiki
    c.line(60, 70, 120, 96, S_[5]) if False else None
    hm = Sprite(80, 20)
    for x in range(80):
        y = int(4 + 10 * math.sin(math.pi * x / 79))
        hm.vline(x, y, y + 4, CR[3] if (x // 6) % 2 else G_[3])
    hm.stamp_on(c, 280, 96)
    c.line(278, 96, 268, 60, W_[2]); c.line(360, 96, 356, 60, W_[2])
    cl = Sprite(30, 20); cl.rect(0, 4, 29, 19, D_[3]); cl.rect(0, 0, 29, 5, "#fffbef"); cl.rect(10, 8, 19, 12, "#fffbef"); cl.stamp_on(c, 70, 176)
    sb = Sprite(14, 56); sb.ell(7, 28, 6, 27, G_[3]); sb.vline(7, 4, 52, CR[3]); sb.stamp_on(c, 62, 96)
    c.vline(330, 120, 176, W_[2]); c.vline(331, 120, 176, W_[1]); c.box(326, 112, 335, 122, W_[3])
    return c, {"w": W, "h": H, "floor": F, "anims": [["waves", 46, 72], ["torch", 330, 110]]}


# ======================================================================= 11 · Mina de Ouro Desativada (384x216)
def mina():
    W, H, F = 384, 216, 84
    c = Cv(W, H, 12); r = random.Random(121)
    c.rect(0, 0, W - 1, H - 1, SO[1])
    for _ in range(260):                                                      # rochas facetadas
        x, y = r.uniform(-10, W), r.uniform(-6, F + 4)
        w, h = r.uniform(10, 26), r.uniform(6, 14)
        col = r.choice([SO[2], SO[1], SO[2], SO[3], SO[0]])
        pts = [(x, y + h * 0.3), (x + w * 0.4, y), (x + w, y + h * 0.2), (x + w * 0.9, y + h), (x + w * 0.1, y + h * 0.9)]
        c.poly(pts, col)
        c.line(x + 1, y + h * 0.3, x + w * 0.4, y + 1, shift(col, 1))
    for _ in range(40):                                                       # veios de ouro
        x, y = r.uniform(0, W), r.uniform(4, F - 4)
        for k in range(r.randrange(3, 7)):
            c.set(x + k, y + math.sin(k) * 1.5, G_[3] if k % 2 else G_[2])
        c.set(x + 1, y - 1, G_[4])
    # escoras de madeira
    for x in (48, 330):
        c.rect(x, 6, x + 11, F + 14, W_[2]); c.vline(x + 1, 6, F + 14, W_[3]); c.vline(x + 11, 6, F + 14, W_[1])
    c.rect(36, 2, 348, 13, W_[2]); c.hline(36, 348, 2, W_[3]); c.hline(36, 348, 3, W_[3]); c.hline(36, 348, 13, W_[1])
    for x in range(60, 330, 40):
        c.set(x, 8, S_[4])
    # chão de pedra com trilhos e dormentes
    c.rect(0, F, W - 1, H - 1, SO[2])
    for _ in range(1500):
        c.set(r.uniform(0, W), r.uniform(F, H), r.choice([SO[1], SO[3], SO[2]]))
    for x in range(-4, W, 14):
        c.rect(x, 186, x + 8, 200, W_[1]); c.hline(x, x + 8, 186, W_[2])
    for y in (188, 197):
        c.hline(0, W - 1, y, S_[4]); c.hline(0, W - 1, y + 1, S_[3]); c.hline(0, W - 1, y + 2, OL)
    # carrinho de mina cheio de ouro
    mc = Sprite(60, 36)
    mc.poly([(0, 8), (59, 8), (54, 30), (5, 30)], S_[2]); mc.hline(0, 59, 8, S_[4]); mc.hline(0, 59, 9, S_[3])
    for xx in (14, 30, 46):
        mc.vline(xx, 10, 29, S_[1])
    for k in range(9):
        mc.ell(6 + k * 6, 7, 4, 4, G_[2]); mc.ell(5 + k * 6, 6, 2, 2, G_[3])
    mc.set(20, 3, G_[4]); mc.set(40, 4, G_[4])
    for wx in (14, 46):
        mc.ell(wx, 31, 5, 5, OL); mc.ell(wx, 31, 3, 3, S_[3])
    mc.stamp_on(c, 20, 158)
    # picareta encostada e caixotes
    c.line(300, 140, 316, 190, W_[2]); c.line(301, 140, 317, 190, W_[3]); c.poly([(290, 142), (312, 134), (314, 138), (294, 146)], S_[4])
    for i in range(2):
        cr = Sprite(30, 22); cr.rect(0, 0, 29, 21, W_[3]); cr.hline(0, 29, 0, W_[4]); cr.box(4, 6, 25, 15, W_[2]); text(cr, 7, 8, "XX", CR[2])
        cr.stamp_on(c, 336, 170 - i * 22)
    # lampiões (a chama é animada; a luz vem do "dark")
    for x in (72, 312):
        c.vline(x, 14, 26, OL)
        ln = Sprite(11, 14); ln.rect(0, 0, 10, 2, S_[2]); ln.rect(1, 3, 9, 11, G_[4]); ln.rect(0, 12, 10, 13, S_[2]); ln.vline(0, 3, 11, S_[2]); ln.vline(10, 3, 11, S_[2])
        ln.stamp_on(c, x - 5, 26)
    return c, {"w": W, "h": H, "floor": F, "dark": {"a": 0.55, "tint": "26,20,32", "lights": [[72, 40, 110], [312, 40, 110]], "flicker": True},
               "anims": [["lantern", 72, 32], ["lantern", 312, 32], ["sparkle", 0, 4, W, F]]}


# ======================================================================= 12 · Bunker Militar (384x216)
def bunker():
    W, H, F = 384, 216, 84
    c = Cv(W, H, 13); r = random.Random(131)
    c.rect(0, 0, W - 1, F - 1, S_[3])
    for y in range(0, F, 21):                                         # painéis de concreto com rebites
        for x in range((y // 21 % 2) * 24, W, 48):
            c.rect(x + 1, y + 1, x + 46, y + 19, S_[3]); c.hline(x + 1, x + 46, y + 1, S_[4]); c.vline(x + 1, y + 1, y + 19, S_[4])
            c.hline(x, x + 47, y + 20, S_[2]); c.vline(x + 47, y, y + 20, S_[2])
            for (rx, ry) in ((4, 4), (43, 4), (4, 16), (43, 16)):
                c.set(x + rx, y + ry, S_[2]); c.set(x + rx - 1, y + ry - 1, S_[5])
    for _ in range(60):
        c.set(r.uniform(0, W), r.uniform(0, F), S_[2])
    # canos
    c.rect(0, 4, W - 1, 8, TE[1]); c.hline(0, W - 1, 4, TE[2]); c.hline(0, W - 1, 9, OL)
    # porta blindada redonda com volante
    c.ell(58, 44, 36, 36, OL); c.ell(58, 44, 35, 35, S_[4]); c.ell(58, 44, 30, 30, S_[3]); c.ell(58, 44, 26, 26, S_[4])
    c.tone(30, 10, 92, 82, -1, mask=lambda x, y: ((x - 58) ** 2 + (y - 44) ** 2 <= 26 ** 2) and (x - 58) + (y - 44) > 8)
    for a in range(0, 360, 45):
        x = 58 + 32.5 * math.cos(math.radians(a)); y = 44 + 32.5 * math.sin(math.radians(a))
        c.ell(x, y, 2, 2, S_[2]); c.set(x - 1, y - 1, S_[5])
    c.ell(58, 44, 12, 12, OL); c.ell(58, 44, 11, 11, CR[2]); c.ell(58, 44, 8, 8, S_[3])
    for a in (0, 60, 120):
        c.line(58 - 11 * math.cos(math.radians(a)), 44 - 11 * math.sin(math.radians(a)), 58 + 11 * math.cos(math.radians(a)), 44 + 11 * math.sin(math.radians(a)), CR[3])
    c.ell(58, 44, 3, 3, S_[5])
    # faixa de perigo
    for x in range(0, W):
        c.vline(x, F - 10, F - 6, G_[3] if ((x + 0) // 7) % 2 else OL)
    # monitores com radar e gráficos
    for i, x in enumerate((150, 196, 242)):
        c.box(x, 14, x + 40, 44, S_[1])
        c.rect(x + 3, 17, x + 37, 41, TE[0])
        if i == 0:
            c.ell(x + 20, 29, 10, 10, TE[1]); c.ell(x + 20, 29, 6, 6, TE[0]); c.line(x + 20, 29, x + 28, 23, TE[4]); c.set(x + 14, 26, CR[3])
        elif i == 1:
            for k in range(30):
                c.set(x + 5 + k, 30 + round(6 * math.sin(k / 3)), TE[4])
        else:
            for k in range(5):
                c.hline(x + 6, x + 6 + 6 + (k * 7) % 22, 20 + k * 4, TE[4] if k % 2 else G_[3])
        c.rect(x + 16, 45, x + 24, 48, S_[2])
    # armários
    for i in range(3):
        lk = Sprite(22, 56); lk.rect(0, 0, 21, 55, L_[2]); lk.hline(0, 21, 0, L_[3]); lk.vline(0, 0, 55, L_[3])
        for yy in range(6, 16, 3):
            lk.hline(5, 16, yy, L_[1])
        lk.rect(16, 26, 18, 32, S_[4])
        lk.stamp_on(c, 300 + i * 24, 26)
    concrete(c, F, base=3, seed=133, joints=44)
    baseboard(c, F, S_[1])
    # sacos de areia
    for row in range(3):
        for i in range(4 - row):
            sb = Sprite(22, 11); sb.ell(11, 5, 10, 5, W_[4]); sb.ell(10, 4, 7, 2, W_[5]); sb.hline(3, 18, 8, W_[3]); sb.set(2, 5, W_[2]); sb.set(19, 5, W_[2])
            sb.stamp_on(c, 288 + i * 20 + row * 10, 188 - row * 9)
    # caixas de suprimento
    for i in range(2):
        bx = Sprite(34, 22); bx.rect(0, 0, 33, 21, L_[2]); bx.hline(0, 33, 0, L_[3]); bx.rect(0, 9, 33, 11, L_[1]); text(bx, 4, 13, "BUNK", "#fffbef") if False else bx.rect(4, 14, 14, 16, "#fffbef")
        bx.stamp_on(c, 14 + i * 36, 176)
    return c, {"w": W, "h": H, "floor": F, "anims": [["siren", 120, 0]]}


# ======================================================================= 13 · Estação Espacial (384x216)
def estacao():
    W, H, F = 384, 216, 84
    c = Cv(W, H, 14); r = random.Random(141)
    c.rect(0, 0, W - 1, F - 1, S_[3])
    for x in range(0, W, 48):                                         # painéis
        c.rect(x, 0, x + 47, F - 1, S_[3]); c.vline(x, 0, F - 1, S_[5]); c.vline(x + 47, 0, F - 1, S_[2]); c.vline(x + 1, 0, F - 1, S_[4])
        for y in range(10, F, 22):
            c.hline(x + 3, x + 44, y, S_[2])
    # janelão com a Terra
    wx, wy, ww, wh = 96, 6, 192, 60
    c.box(wx - 4, wy - 4, wx + ww + 3, wy + wh + 3, S_[2])
    c.rect(wx, wy, wx + ww - 1, wy + wh - 1, PL[0])
    for _ in range(120):
        c.set(wx + r.uniform(0, ww), wy + r.uniform(0, wh), r.choice([S_[5], S_[4], "#fffbef", PL[3]]))
    cx, cy, R = wx + 140, wy + 110, 92
    for y in range(wy, wy + wh):
        for x in range(wx, wx + ww):
            d = math.hypot(x - cx, y - cy)
            if d <= R:
                nx, ny = (x - cx) / R, (y - cy) / R
                lit = -(-0.6 * nx - 0.8 * ny)
                col = D_[3] if lit > 0.55 else D_[2] if lit > 0.2 else D_[1]
                n = math.sin(x / 7) * math.cos(y / 5) + math.sin((x + y) / 11)
                if n > 0.9:
                    col = L_[4] if lit > 0.4 else L_[3]
                if n < -1.3:
                    col = "#fffbef"
                c.set(x, y, col)
            elif d <= R + 2:
                c.set(x, y, D_[4])
    c.ell(wx + 30, wy + 16, 6, 6, S_[5]); c.ell(wx + 28, wy + 14, 3, 3, "#fffbef")          # lua
    c.rect(wx + ww // 2 - 2, wy, wx + ww // 2 + 1, wy + wh - 1, S_[2])
    # luzes e painéis de controle
    c.hline(0, W - 1, 2, TE[4]); c.hline(0, W - 1, F - 12, TE[4]); c.hline(0, W - 1, F - 11, TE[3])
    for (x, kind) in ((14, 0), (304, 1)):
        c.box(x, 14, x + 66, 50, S_[1]); c.rect(x + 3, 17, x + 63, 47, S_[0])
        if kind == 0:
            for k in range(5):
                c.hline(x + 6, x + 6 + 10 + (k * 13) % 40, 21 + k * 5, TE[4] if k % 2 else CR[3])
        else:
            for k in range(8):
                c.box(x + 6 + (k % 4) * 14, 22 + (k // 4) * 12, x + 16 + (k % 4) * 14, 30 + (k // 4) * 12, TE[3] if k % 3 else G_[3], S_[1])
    # piso de grade metálica
    c.rect(0, F, W - 1, H - 1, S_[2])
    for y in range(F, H, 16):
        c.hline(0, W - 1, y, S_[1]); c.hline(0, W - 1, y + 1, S_[3])
    for x in range(0, W, 16):
        c.vline(x, F, H - 1, S_[1]); c.vline(x + 1, F, H - 1, S_[3])
    for y in range(F + 8, H, 16):
        for x in range(8, W, 16):
            c.set(x, y, S_[4])
    baseboard(c, F, S_[1])
    # braço robótico no canto e cápsula de suprimentos
    c.rect(356, F - 6, 372, F + 30, S_[4]); c.vline(356, F - 6, F + 30, "#fffbef")
    c.line(364, F - 6, 340, F - 30, S_[4]); c.line(365, F - 6, 341, F - 30, S_[4]); c.line(366, F - 6, 342, F - 30, S_[3])
    c.box(334, F - 36, 346, F - 28, G_[3])
    cap = Sprite(40, 24); cap.ell(20, 12, 19, 11, S_[5]); cap.ell(20, 10, 15, 7, "#fffbef"); cap.rect(8, 10, 32, 13, TE[3]); cap.stamp_on(c, 10, 182)
    return c, {"w": W, "h": H, "floor": F, "anims": [["stars", wx, wy, wx + ww, wy + wh]]}


SCENES = {0: quartinho, 1: armario, 2: garagem, 3: porao, 4: terreno, 5: container, 6: sobrado, 7: galpao,
          8: sitio, 9: fazenda, 10: ilha, 11: mina, 12: bunker}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for i, fn in SCENES.items():
        c, m = fn()
        c.save(os.path.join(OUT, f"{i:02d}.png"))
        meta[i] = m
    json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
    print("ok", list(SCENES))
