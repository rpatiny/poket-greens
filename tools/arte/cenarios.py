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


SCENES = {0: quartinho, 1: armario, 2: garagem, 3: porao}


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    meta = {}
    for i, fn in SCENES.items():
        c, m = fn()
        c.save(os.path.join(OUT, f"{i:02d}.png"))
        meta[i] = m
    json.dump(meta, open(os.path.join(OUT, "meta.json"), "w"), indent=1)
    print("ok", list(SCENES))
