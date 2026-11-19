"""Os 13 esconderijos vistos de cima: cômodo flutuando no preto, crescendo a cada imóvel.

Para cada cômodo gera (em assets/sprites/v2/comodos/):
  NN.png      fundo iluminado (paredes, chão, móveis com sombra e luz)
  NN_s.png    o mesmo fundo um degrau mais escuro: o jogo recorta dele a sombra dos vasos
  NN_l.png    mapa de luz (R = 0: -2, 64: -1, 128: 0, 192: +1) para iluminar as plantas no jogo
  meta.json   área dos vasos, posição da luz principal (sombras) e animações

    python3 tools/arte/comodos.py
"""
import json, math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from cenarios import Cv, Sprite, shift, RAMPS, OL, hexrgb, sky, cloud, tree_crown, text
from estilo_topdown import (place, planks_region, wallpaper_region, point_light, poly_light, blob_sprite,
                            potted, VOID, FW, FH, ROOT)
from PIL import Image

W_ = RAMPS["wood"]; S_ = RAMPS["stone"]; PA = RAMPS["paper"]; CR = RAMPS["crimson"]; D_ = RAMPS["denim"]
G_ = RAMPS["gold"]; L_ = RAMPS["leaf"]; B_ = RAMPS["brick"]; SO = RAMPS["soil"]; PL = RAMPS["plum"]; TE = RAMPS["teal"]
OUT = os.path.join(ROOT, "assets", "sprites", "v2", "comodos")
WHITE = "#fffbef"


# ======================================================================= luz
def level(I, x, y, dark):
    """Intensidade -> degraus na rampa. Cômodos escuros ganham um degrau extra de breu."""
    if I >= 0.8:
        n = 1
    elif I >= 0.62:
        n = 1 if (x + y) % 2 == 0 else 0
    elif I >= 0.4:
        n = 0
    elif I >= 0.25:
        n = -1 if (x + y) % 2 == 0 else 0
    else:
        n = -1
    if dark and I < 0.18:
        n = -2 if (I < 0.1 or (x + y) % 2 == 0) else -1
    return n


def lighting(c, room, lights, dark=False):
    x0, y0, w, h = room
    lm = {}
    for y in range(y0 - 6, y0 + h + 6):
        for x in range(x0 - 6, x0 + w + 6):
            I = sum(f(x, y) for f in lights)
            n = level(I, x, y, dark)
            lm[(x, y)] = n
            if not (x0 <= x < x0 + w and y0 <= y < y0 + h):
                continue
            col = c.get(x, y)
            if col and col != OL and n:
                c.px[y][x] = shift(col, n)
    return lm


# ======================================================================= cômodo
class Room:
    def __init__(s, idx, w, h, wall_h=30, cap=(S_[1], S_[2]), door=True, seed=1):
        s.idx = idx
        s.c = Cv(FW, FH, seed)
        s.w, s.h, s.wh = w, h, wall_h
        s.x0 = (FW - w) // 2
        s.y0 = (FH - h) // 2 + 2
        s.fy = s.y0 + wall_h
        s.cap = cap
        s.door = door
        s.objs = []
        s.r = random.Random(seed * 13)
        s.anims = []
        s.bulb = None
        s.extra_busy = []
        s.wall_extra = []   # enfeites pintados junto com a parede (janelas, letreiro, vista)

    @property
    def room(s):
        return (s.x0, s.y0, s.w, s.h)

    def shell(s, wall_fn, floor_fn):
        c, x0, y0, w, h = s.c, s.x0, s.y0, s.w, s.h
        T = 5
        dark, light = s.cap
        c.rect(x0 - T, y0 - T, x0 + w + T - 1, y0 + h + T - 1, dark)
        c.rect(x0 - T, y0 - T, x0 + w + T - 1, y0 - T + 1, light)
        c.rect(x0 - T, y0 - T, x0 - T + 1, y0 + h + T - 1, light)
        for x in range(x0 - T + 3, x0 + w + T - 2, 9):
            c.set(x, y0 - T + 2, light)
        c.rect(x0 - T - 1, y0 - T - 1, x0 + w + T, y0 - T - 1, OL); c.rect(x0 - T - 1, y0 + h + T, x0 + w + T, y0 + h + T, OL)
        c.rect(x0 - T - 1, y0 - T - 1, x0 - T - 1, y0 + h + T, OL); c.rect(x0 + w + T, y0 - T - 1, x0 + w + T, y0 + h + T, OL)
        wall_fn(c, x0, y0, w, s.wh)
        floor_fn(c, x0, s.fy, w, h - s.wh)
        s.plain = [row[:] for row in c.px]   # parede e chão sem enfeites: para achar o que foi pintado por cima
        c.rect(x0 - 1, y0 - 1, x0 + w, y0 - 1, OL); c.rect(x0 - 1, y0 + h, x0 + w, y0 + h, OL)
        c.rect(x0 - 1, y0 - 1, x0 - 1, y0 + h, OL); c.rect(x0 + w, y0 - 1, x0 + w, y0 + h, OL)
        if s.door:
            dw = 20; dx = x0 + w // 2 - dw // 2
            c.rect(dx, y0 + h, dx + dw - 1, y0 + h + T, VOID)
            c.rect(dx - 1, y0 + h, dx - 1, y0 + h + T, OL); c.rect(dx + dw, y0 + h, dx + dw, y0 + h + T, OL)

    def add(s, sp, x, y, height=0.5):
        s.objs.append((sp, s.x0 + x, s.fy + y, height))

    def decor_rects(s, cell=4):
        """Retângulos da parede onde há enfeite (janela, pôster, prateleira...): o jogo não põe nada em cima."""
        c, x0, y0, w, fy = s.c, s.x0, s.y0, s.w, s.fy
        rows = []
        for cy in range(y0, fy + 2, cell):
            run = None
            for cx in range(x0, x0 + w, cell):
                hit = any(c.px[y][x] != s.plain[y][x] for y in range(cy, min(cy + cell, fy + 2)) for x in range(cx, min(cx + cell, x0 + w)))
                if hit and run is None:
                    run = cx
                if not hit and run is not None:
                    rows.append([run - 1, cy - 1, cx + 1, cy + cell + 1]); run = None
            if run is not None:
                rows.append([run - 1, cy - 1, x0 + w + 1, cy + cell + 1])
        return rows + s.wall_extra

    def slots(s, pots, n=12):
        """Lugares livres no chão para os equipamentos comprados (sprite 32x32, canto de cima à esquerda)."""
        px, py, pw, ph = pots
        busy = [(px - 22, py - 42, px + pw + 22, py + ph + 32)]          # vasos/calhas e a altura das plantas
        for sp, xx, yy, hh in s.objs:
            busy.append((xx - 2, yy - 2, xx + sp.w + 2, yy + sp.h + 2))
        busy += s.extra_busy
        x0, y0, w, h, fy = s.x0, s.y0, s.w, s.h, s.fy
        hit = lambda r, a: not (r[2] <= a[0] or r[0] >= a[2] or r[3] <= a[1] or r[1] >= a[3])
        cx, cy = px + pw / 2, py + ph / 2
        cands = []
        for y in range(fy - 18, y0 + h - 31, 2):
            for x in range(x0 + 1, x0 + w - 31, 2):
                body = (x + 4, y + 4, x + 28, y + 32)
                if y + 20 < fy + 2:                                      # o pé tem que estar no chão
                    continue
                if any(hit(body, b) for b in busy):
                    continue
                d = max(abs(x + 16 - cx) - pw / 2, 0) + max(abs(y + 28 - cy) - ph / 2, 0) * 1.4
                cands.append((d, x, y))
        cands.sort()
        out = []
        for d, x, y in cands:
            r = (x + 2, y + 2, x + 30, y + 32)
            if all(not hit(r, (a, b, a + 28, b + 30)) for a, b in out):
                out.append((x, y))
            if len(out) >= n:
                break
        return out

    def finish(s, main_light, lights, pots, dark=False, wall_lights=None):
        """Sombras dos objetos pela luz principal, luz sobre tudo, oclusão; salva as 3 camadas."""
        c = s.c
        s.wall_busy = s.decor_rects()
        lx, ly = main_light
        L = (s.x0 + lx, s.fy + ly)
        s.objs.sort(key=lambda o: o[2] + o[0].h)
        for sp, xx, yy, hh in s.objs:
            place(c, sp, xx, yy, L, height=hh)
        abs_lights = [f(s.x0, s.fy) for f in lights]
        lm = lighting(c, s.room, abs_lights, dark)
        x0, y0, w, h, fy = s.x0, s.y0, s.w, s.h, s.fy
        # oclusão no pé das paredes e nos cantos
        c.tone(x0, fy, x0 + w - 1, fy + 2, -1); c.tone(x0, fy + 3, x0 + w - 1, fy + 5, -1, dither=0)
        c.tone(x0, fy, x0 + 2, y0 + h - 1, -1); c.tone(x0 + 3, fy, x0 + 5, y0 + h - 1, -1, dither=1)
        c.tone(x0 + w - 3, fy, x0 + w - 1, y0 + h - 1, -1); c.tone(x0 + w - 6, fy, x0 + w - 4, y0 + h - 1, -1, dither=0)
        c.tone(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, -1); c.tone(x0, y0, x0 + w - 1, y0 + 1, -1)
        os.makedirs(OUT, exist_ok=True)
        base = os.path.join(OUT, f"{s.idx:02d}")
        bg = img(c)
        bg.save(base + ".png")
        sh = Cv(FW, FH)
        sh.px = [[(shift(col, -1) if col and col != OL else col) for col in row] for row in c.px]
        img(sh).save(base + "_s.png")
        lmi = Image.new("RGBA", (FW, FH), (128, 0, 0, 255))
        for (x, y), n in lm.items():
            if 0 <= x < FW and 0 <= y < FH:
                lmi.putpixel((x, y), ({-2: 0, -1: 64, 0: 128, 1: 192}[n], 0, 0, 255))
        lmi.save(base + "_l.png")
        px, py, pw, ph = pots
        return {
            "w": FW, "h": FH, "room": [x0, y0, w, h], "floor": fy,
            "pots": [x0 + px, fy + py, pw, ph], "light": list(L), "busy": [[xx - 1, yy - 1, xx + sp.w + 1, yy + sp.h + 1] for sp, xx, yy, hh in s.objs] + s.extra_busy,
            "wallBusy": s.wall_busy,
            "anims": s.anims, **({"bulb": s.bulb} if s.bulb else {}), **({"glow": s.glow} if getattr(s, "glow", None) else {}),
        }


def img(c):
    im = Image.new("RGBA", (c.w, c.h), hexrgb(VOID) + (255,))
    for y in range(c.h):
        for x in range(c.w):
            if c.px[y][x]:
                im.putpixel((x, y), hexrgb(c.px[y][x]) + (255,))
    return im


def L_point(dx, dy, r, ry=None, p=1.0):
    return lambda x0, fy: point_light(x0 + dx, fy + dy, r, ry, p)


def L_poly(pts, p=1.0):
    return lambda x0, fy: poly_light([(x0 + a, fy + b) for a, b in pts], p)


# ======================================================================= peças
def box3d(w, d, hgt, top, front=None, lines=0, seed=0):
    """Caixa vista de cima em 3/4: tampo (d px) e frente (hgt px)."""
    front = front or shift(top, -1)
    sp = Sprite(w, d + hgt)
    sp.rect(0, 0, w - 1, d - 1, top); sp.hline(0, w - 1, 0, shift(top, 1)); sp.vline(0, 0, d - 1, shift(top, 1))
    sp.rect(0, d, w - 1, d + hgt - 1, front); sp.hline(0, w - 1, d, shift(front, 1) if lines else front)
    sp.hline(0, w - 1, d + hgt - 1, shift(front, -1))
    if lines:
        for x in range(lines, w - 1, lines):
            sp.vline(x, 1, d - 2, shift(top, -1))
    return sp


def crate(w=18, d=12, hgt=8):
    sp = box3d(w, d, hgt, W_[4], W_[3])
    sp.rect(1, 1, w - 2, d - 2, W_[3]); sp.rect(2, 2, w - 3, d - 3, W_[4])
    sp.line(2, 2, w - 3, d - 3, W_[2])
    for y in range(d + 2, d + hgt - 1, 3):
        sp.hline(0, w - 1, y, W_[2])
    return sp


def round_top(r, ramp, hole=None):
    sp = Sprite(2 * r + 1, 2 * r + 4)
    sp.ell(r, r + 3, r, r, shift(ramp[1], -1)) if len(ramp) > 1 else None
    sp.ell(r, r + 2, r, r, ramp[0])
    sp.ell(r, r, r, r, ramp[1])
    sp.ell(r - 1, r - 1, r - 2, r - 2, ramp[2])
    sp.ell(r - r // 2, r - r // 2, max(1, r // 4), max(1, r // 4), ramp[3] if len(ramp) > 3 else ramp[2])
    if hole:
        sp.ell(r, r, hole, hole, ramp[0])
    return sp


def sack(w, h, col):
    sp = Sprite(w, h)
    sp.ell(w / 2 - 0.5, h / 2, w / 2 - 0.5, h / 2 - 0.5, col)
    sp.ell(w / 2 - 2, h / 2 - 2, w / 3, h / 4, shift(col, 1))
    sp.rect(w // 2 - 2, 0, w // 2 + 1, 2, shift(col, -1))
    return sp


def rug(c, x, y, w, h, base, border, dots):
    c.box(x, y, x + w, y + h, border)
    c.rect(x + 2, y + 2, x + w - 2, y + h - 2, base)
    c.rect(x + 4, y + 4, x + w - 4, y + h - 4, border)
    c.rect(x + 5, y + 5, x + w - 5, y + h - 5, base)
    for xx in range(x + 7, x + w - 6, 4):
        for yy in range(y + 7, y + h - 6, 4):
            if (xx // 4 + yy // 4) % 2 == 0:
                c.set(xx, yy, dots)
    for xx in range(x + 1, x + w, 2):
        c.set(xx, y - 1, PA[3]); c.set(xx, y + h + 1, PA[3])


def wall_bricks(c, x0, y0, w, h, ramp, base=3, bw=12, bh=5, seed=1, plaster=None):
    r = random.Random(seed)
    c.rect(x0, y0, x0 + w - 1, y0 + h - 1, ramp[base - 2])
    for y in range(y0, y0 + h - 4, bh + 1):
        off = 0 if ((y - y0) // (bh + 1)) % 2 else bw // 2
        for x in range(x0 - off, x0 + w, bw + 1):
            col = ramp[base + r.choice([0, 0, 0, -1, 1])] if base + 1 < len(ramp) else ramp[base]
            xa, xb = max(x0, x), min(x0 + w - 1, x + bw - 1)
            if xa <= xb:
                c.rect(xa, y, xb, y + bh - 1, col); c.hline(xa, xb, y, shift(col, 1))
    if plaster:
        for (px, py, pw, ph) in plaster:
            c.rect(x0 + px, y0 + py, x0 + px + pw, y0 + py + ph, S_[5])
            for k in range(pw):
                c.set(x0 + px + k, y0 + py + ph + r.randrange(0, 2), S_[5])
            for k in range(ph):
                c.set(x0 + px + r.randrange(0, pw), y0 + py + k, S_[4])
    c.hline(x0, x0 + w - 1, y0 + h - 4, S_[3]); c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, S_[2])


def concrete(c, x0, y0, w, h, base=4, joints=34, seed=5):
    r = random.Random(seed)
    c.rect(x0, y0, x0 + w - 1, y0 + h - 1, S_[base])
    for _ in range(w * h // 13):
        c.set(r.uniform(x0, x0 + w), r.uniform(y0, y0 + h), r.choice([S_[base - 1], S_[base - 1], S_[base + 1]]))
    for y in range(y0 + joints, y0 + h, joints):
        c.hline(x0, x0 + w - 1, y, S_[base - 1])
    for x in range(x0 + joints * 2, x0 + w, joints * 2):
        c.vline(x, y0, y0 + h - 1, S_[base - 1])


def window_on_wall(c, x, y, w, h, frame=None, view=None):
    frame = frame or W_[3]
    c.box(x - 2, y - 2, x + w + 1, y + h + 1, frame)
    if view:
        view(c, x, y, w, h)
    else:
        for yy in range(y, y + h):
            c.hline(x, x + w - 1, yy, D_[4] if yy < y + h // 2 else D_[3])
        c.rect(x + 2, y + 2, x + 6, y + 3, WHITE)
    c.vline(x + w // 2, y, y + h - 1, frame); c.hline(x, x + w - 1, y + h // 2, frame)
    for k in range(min(5, h - 2)):
        c.set(x + 2 + k, y + h - 2 - k, WHITE)


def hanging_clothes(c, x, y, cols):
    c.hline(x - 2, x + len(cols) * 7 + 1, y, S_[3]); c.hline(x - 2, x + len(cols) * 7 + 1, y - 1, OL)
    for i, col in enumerate(cols):
        sp = Sprite(6, 14 + (i % 2) * 4)
        sp.rect(0, 0, 5, sp.h - 1, col); sp.vline(0, 0, sp.h - 1, shift(col, 1)); sp.vline(3, 2, sp.h - 1, shift(col, -1))
        sp.stamp_on(c, x + i * 7, y + 2)


# ======================================================================= 0 · Quartinho
def r0():
    R = Room(1, 140, 112, 30, seed=1)
    R.shell(wallpaper_region, lambda c, x, y, w, h: planks_region(c, x, y, w, h, 3, 6, 4))
    c, x0, y0, fy = R.c, R.x0, R.y0, R.fy
    wx, wy = x0 + 82, y0 + 5
    window_on_wall(c, wx, wy, 28, 17)
    for (cx0, k) in ((wx - 7, 0), (wx + 28, 1)):
        for i in range(7):
            c.vline(cx0 + i, wy - 4, wy + 21 - (i if k else 6 - i) // 2, [CR[3], CR[2], CR[3], CR[1], CR[2], CR[3], CR[2]][i])
    c.hline(wx - 9, wx + 36, wy - 4, S_[3]); c.hline(wx - 9, wx + 36, wy - 5, OL)
    ps = Sprite(16, 20); ps.rect(0, 0, 15, 19, PL[2]); ps.rect(2, 2, 13, 11, CR[3]); ps.ell(7, 6, 3, 3, G_[3]); ps.rect(6, 7, 8, 11, L_[2]); ps.rect(2, 13, 13, 14, WHITE); ps.rect(2, 16, 9, 16, PA[3])
    ps.stamp_on(c, x0 + 52, y0 + 4)
    c.box(x0 + 116, y0 + 13, x0 + 136, y0 + 15, W_[3])
    for i, col in enumerate((D_[2], CR[2], L_[3], G_[2], PL[2])):
        c.rect(x0 + 118 + i * 3, y0 + 6 + (i % 2), x0 + 119 + i * 3, y0 + 12, col)
    c.ell(x0 + 72, y0 + 10, 4, 4, OL); c.ell(x0 + 72, y0 + 10, 3, 3, WHITE); c.set(x0 + 72, y0 + 8, OL); c.set(x0 + 73, y0 + 10, CR[2])
    rug(c, x0 + 44, fy + 28, 56, 38, CR[3], CR[2], G_[3])
    c.box(x0 + 60, y0 + R.h - 7, x0 + 79, y0 + R.h - 1, CR[1]); c.rect(x0 + 62, y0 + R.h - 5, x0 + 77, y0 + R.h - 3, CR[2])
    bed = Sprite(32, 54)
    bed.rect(0, 0, 31, 5, W_[2]); bed.hline(0, 31, 0, W_[3])
    for xx in range(2, 30, 6):
        bed.vline(xx, 1, 4, W_[1])
    bed.rect(1, 6, 30, 50, PA[4]); bed.rect(4, 8, 27, 15, WHITE); bed.hline(4, 27, 15, PA[2]); bed.hline(6, 25, 11, PA[3])
    for yy in range(18, 50):
        for xx in range(1, 31):
            wv = math.sin(xx / 3.0 + yy / 5.0) * 0.8 + math.sin(xx / 7.0 - yy / 2.4) * 0.5 + (yy - 18) / 34
            bed.set(xx, yy, D_[3] if wv > 0.9 else D_[2] if wv > -0.4 else D_[1])
    bed.poly([(18, 18), (31, 18), (31, 30)], D_[3]); bed.vline(30, 6, 50, PA[2]); bed.rect(0, 51, 31, 53, W_[1]); bed.hline(0, 31, 51, W_[2])
    R.add(bed, 3, -4, 0.18)
    ns = Sprite(14, 18); ns.rect(0, 4, 13, 14, W_[4]); ns.hline(0, 13, 4, W_[5]); ns.rect(0, 15, 13, 17, W_[2]); ns.ell(6.5, 3, 4, 3, G_[3]); ns.ell(5.5, 2, 1, 1, G_[4]); ns.rect(10, 9, 12, 11, CR[3])
    R.add(ns, 38, -6, 0.5)
    dk = Sprite(36, 22); dk.rect(0, 6, 35, 17, W_[3]); dk.hline(0, 35, 6, W_[4]); dk.rect(0, 18, 35, 21, W_[1]); dk.hline(0, 35, 18, W_[2])
    dk.rect(3, 0, 16, 10, S_[4]); dk.hline(3, 16, 0, S_[5]); dk.rect(5, 2, 14, 7, TE[1]); dk.rect(6, 3, 10, 4, TE[3]); dk.rect(20, 10, 30, 12, S_[3])
    R.add(dk, 100, -9, 0.35)
    ch = Sprite(12, 14); ch.ell(5.5, 7.5, 5.5, 5.5, CR[2]); ch.ell(4.5, 6.5, 3, 3, CR[3]); ch.rect(2, 0, 9, 3, CR[1])
    R.add(ch, 110, 14, 0.5)
    for (col, xx, yy, sd) in ((L_[3], 6, 60, 1), (CR[2], 16, 63, 2), (S_[5], 8, 68, 3)):
        R.add(blob_sprite(col, 13, 7, sd), xx, yy, 0.12)
    pz = Sprite(18, 16); pz.rect(0, 0, 17, 15, W_[4]); pz.hline(0, 17, 0, W_[5]); pz.rect(2, 2, 15, 13, W_[3]); pz.poly([(4, 4), (14, 4), (9, 12)], G_[3]); pz.set(7, 6, CR[3]); pz.set(11, 6, CR[3])
    R.add(pz, 112, 54, 0.1)
    for i, col in enumerate((CR[3], L_[4], D_[3])):
        cn = Sprite(4, 6); cn.rect(0, 0, 3, 5, col); cn.vline(0, 0, 5, shift(col, 1)); cn.hline(0, 3, 0, S_[5])
        R.add(cn, 34 + i * 5, 66 - (i % 2) * 3, 1.0)
    return R.finish((96, -60), [L_poly([(80, -30), (112, -30), (98, 52), (66, 52)], 0.95), L_point(96, 18, 80, 56, 0.55),
                                L_point(44, 6, 30, 20, 0.9), L_point(110, 18, 18, 12, 0.5)], pots=(46, 14, 52, 30))


# ======================================================================= 1 · Armário Grow
def r1():
    """Armário Grow: dentro de um guarda-roupa. Uma planta só, num vaso em cima de uma cadeira, debaixo da luz roxa."""
    R = Room(0, 100, 142, 68, cap=(W_[1], W_[2]), door=False, seed=2)   # em pé: guarda-roupa é alto e raso

    def back(c, x0, y0, w, h):
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, W_[2])
        for x in range(x0, x0 + w, 9):                       # tábuas do fundo do armário
            c.vline(x, y0, y0 + h - 1, W_[1]); c.vline(x + 1, y0, y0 + h - 1, W_[3])
        r = random.Random(21)
        for _ in range(30):
            gx, gy = r.uniform(x0, x0 + w), r.uniform(y0, y0 + h - 6)
            c.vline(gx, gy, gy + r.randrange(3, 8), W_[1])
        c.rect(x0, y0, x0 + w - 1, y0 + 4, W_[3]); c.hline(x0, x0 + w - 1, y0, W_[4]); c.hline(x0, x0 + w - 1, y0 + 4, W_[1])   # prateleira de cima
        c.hline(x0, x0 + w - 1, y0 + h - 4, W_[1]); c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, W_[1])

    R.shell(back, lambda c, x, y, w, h: planks_region(c, x, y, w, h, 2, 7, 11))
    c, x0, y0, fy, w = R.c, R.x0, R.y0, R.fy, R.w
    # caixa de sapato e uma lata na prateleira
    c.box(x0 + 6, y0 - 3, x0 + 22, y0 + 3, PA[3]); c.hline(x0 + 7, x0 + 21, y0 - 2, PA[4]); c.rect(x0 + 12, y0, x0 + 16, y0 + 1, CR[2])
    c.box(x0 + 84, y0 - 2, x0 + 90, y0 + 3, S_[4]); c.hline(x0 + 85, x0 + 89, y0 - 1, S_[5])
    # varão com suportes
    ry = y0 + 13
    c.hline(x0 + 1, x0 + w - 2, ry, S_[4]); c.hline(x0 + 1, x0 + w - 2, ry - 1, S_[5]); c.hline(x0 + 1, x0 + w - 2, ry + 1, OL)
    for bx in (x0 + 1, x0 + w - 4):
        c.rect(bx, ry - 2, bx + 2, ry + 2, S_[3])

    def hanger(hx, col, shirt=None):
        c.set(hx, ry - 2, col); c.set(hx + 1, ry - 3, col); c.set(hx + 2, ry - 2, col); c.vline(hx, ry - 1, ry + 3, col)   # gancho
        c.line(hx, ry + 3, hx - 6, ry + 9, col); c.line(hx, ry + 3, hx + 6, ry + 9, col); c.hline(hx - 6, hx + 6, ry + 9, col)
        c.line(hx + 1, ry + 4, hx + 7, ry + 10, OL); c.hline(hx - 5, hx + 7, ry + 10, OL)
        if shirt:                                         # a única camiseta, velha e desbotada
            c.poly([(hx - 7, ry + 9), (hx + 7, ry + 9), (hx + 6, ry + 24), (hx - 6, ry + 24)], shirt)
            c.rect(hx - 9, ry + 9, hx - 7, ry + 14, shirt); c.rect(hx + 7, ry + 9, hx + 9, ry + 14, shirt)
            c.vline(hx - 6, ry + 10, ry + 24, shift(shirt, 1)); c.vline(hx + 5, ry + 11, ry + 24, shift(shirt, -1))
            c.hline(hx - 2, hx + 2, ry + 9, shift(shirt, -1)); c.rect(hx - 3, ry + 15, hx, ry + 16, shift(shirt, 1))
            c.hline(hx - 6, hx + 6, ry + 25, OL); c.vline(hx + 7, ry + 15, ry + 24, OL)

    hanger(x0 + 12, S_[5]); hanger(x0 + 22, PL[3], shirt=D_[2]); hanger(x0 + 30, S_[5])
    hanger(x0 + 76, W_[4]); hanger(x0 + 86, S_[5]); hanger(x0 + 93, CR[3])
    # luz roxa pendurada no varão, bem em cima do vaso, e o fio descendo pela lateral
    lx = x0 + w // 2
    c.vline(lx - 9, ry, ry + 4, OL); c.vline(lx + 9, ry, ry + 4, OL)
    lamp = Sprite(28, 7); lamp.rect(0, 0, 27, 3, S_[2]); lamp.hline(0, 27, 0, S_[3]); lamp.rect(2, 4, 25, 6, PL[2])
    for x in range(3, 25, 3):
        lamp.set(x, 5, PL[-1]); lamp.set(x + 1, 5, WHITE)
    lamp.stamp_on(c, lx - 14, ry + 4)
    c.line(lx + 14, ry + 6, x0 + w - 3, ry + 10, OL); c.vline(x0 + w - 3, ry + 10, fy + 54, OL)
    R.anims.append(["purple", lx - 11, ry + 10, 22])
    R.glow = [lx, fy - 4, 40, 44, "rgba(129,96,168,0.16)"]
    # banquinho de madeira com os dois vasos em cima (os vasos são do jogo; o banco fica no cenário)
    bn = Sprite(62, 19)
    bn.rect(0, 0, 61, 10, W_[3]); bn.hline(0, 61, 0, W_[4]); bn.vline(0, 0, 10, W_[4])
    for yy in (3, 7):
        bn.hline(1, 60, yy, W_[2])
    for xx in (14, 33, 49):
        bn.set(xx, 1 + xx % 5, W_[2]); bn.set(xx + 1, 1 + xx % 5, W_[2])
    bn.rect(0, 11, 61, 13, W_[1]); bn.hline(0, 61, 11, W_[2])
    for lx in (2, 57):
        bn.rect(lx, 14, lx + 2, 18, W_[1]); bn.vline(lx, 14, 18, W_[2])
    R.add(bn, w // 2 - 31, 25, 0.35)
    # no chão: tênis, borrifador e a extensão
    for i, col in enumerate((S_[6], S_[6])):
        sh = Sprite(7, 11); sh.ell(3, 5.5, 3, 5, col); sh.rect(1, 6, 5, 9, CR[3]); sh.ell(3, 2.5, 2, 2, S_[5])
        R.add(sh, 8 + i * 9, 52 - i * 2, 0.15)
    sp = Sprite(8, 16); sp.rect(1, 6, 6, 15, D_[4]); sp.hline(1, 6, 6, WHITE); sp.rect(2, 2, 5, 5, L_[3]); sp.rect(4, 0, 7, 2, L_[3])
    R.add(sp, 82, 44, 0.6)
    ex = box3d(14, 5, 3, WHITE, S_[5]); ex.set(4, 2, OL); ex.set(9, 2, OL)
    R.add(ex, 80, 62, 0.2)
    # portas abertas para fora, presas nas quinas da frente, da base até o topo do guarda-roupa
    yb = y0 + R.h + 5
    H = R.h + 10
    for side in (-1, 1):
        hx = x0 - 6 if side < 0 else x0 + w + 5
        tip = hx + side * 26
        q = lambda a, b: [(hx + side * 4, yb - b), (tip - side * 4, yb + 7 - b), (tip - side * 4, yb + 7 - a), (hx + side * 4, yb - a)]
        c.poly([(hx, yb), (tip, yb + 7), (tip, yb + 7 - H), (hx, yb - H)], W_[2])
        c.poly(q(H - 5, H * 0.55 + 2), W_[1])                         # almofada de cima
        c.poly(q(H * 0.55 - 3, 5), W_[1])                             # almofada de baixo
        if side < 0:                                                 # espelho de corpo inteiro na porta da esquerda
            c.poly(q(H - 8, 8), D_[3])
            for k in range(3):
                c.line(hx - 8 - k * 3, yb - 30 - k * 4, hx - 14 - k * 3, yb - 46 - k * 4, WHITE if k != 1 else D_[4])
        c.line(hx, yb, tip, yb + 7, OL); c.line(tip, yb + 7, tip, yb + 7 - H, OL)
        c.line(hx, yb - H, tip, yb + 7 - H, W_[3]); c.line(hx, yb - H - 1, tip, yb + 6 - H, OL)
        c.vline(hx, yb - H, yb, OL)
        km = yb + 4 - H // 2
        c.rect(tip - side * 3, km, tip - side * 2, km + 2, G_[3])
    return R.finish((50, -50), [L_point(50, 18, 44, 34, 1.15), L_point(50, -36, 40, 30, 0.75), L_poly([(0, 58), (100, 58), (100, 76), (0, 76)], 0.3)],
                    pots=(37, 10, 26, 0), dark=True)


# ======================================================================= 2 · Garagem
def r2():
    R = Room(2, 196, 128, 30, seed=3)

    def wall(c, x, y, w, h):
        wall_bricks(c, x, y, w, h, S_, base=4, bw=15, bh=6, seed=3)

    R.shell(wall, lambda c, x, y, w, h: concrete(c, x, y, w, h, 4, 32, 7))
    c, x0, y0, fy = R.c, R.x0, R.y0, R.fy
    gx = x0 + 128
    c.box(gx, y0 + 2, gx + 64, y0 + 27, S_[5])
    for yy in range(y0 + 4, y0 + 26, 3):
        c.hline(gx + 1, gx + 63, yy, S_[3]); c.hline(gx + 1, gx + 63, yy + 1, WHITE)
    c.box(x0 + 52, y0 + 4, x0 + 100, y0 + 22, W_[4])
    for xx in range(x0 + 55, x0 + 99, 4):
        for yy in range(y0 + 7, y0 + 21, 4):
            c.set(xx, yy, W_[2])
    tl = Sprite(42, 14)
    tl.rect(1, 3, 2, 13, W_[2]); tl.rect(0, 1, 5, 4, S_[3]); tl.rect(10, 2, 11, 13, S_[4]); tl.ell(10.5, 2, 2, 2, S_[4])
    tl.rect(17, 1, 24, 6, CR[3]); tl.rect(19, 7, 22, 12, OL); tl.rect(30, 1, 31, 12, G_[2]); tl.rect(35, 1, 36, 12, S_[4]); tl.rect(39, 1, 40, 12, W_[2])
    tl.stamp_on(c, x0 + 56, y0 + 6)
    c.tone(x0 + 132, fy + 76, x0 + 168, fy + 90, -1, mask=lambda x, y: ((x - x0 - 150) / 18) ** 2 + ((y - fy - 83) / 5) ** 2 <= 1)
    bench = box3d(58, 10, 6, W_[3], W_[2], lines=9)
    bench.rect(40, 1, 48, 6, S_[3]); bench.rect(6, 2, 12, 7, CR[3]); bench.rect(16, 3, 19, 7, G_[3])
    R.add(bench, 46, -6, 0.35)
    car = Sprite(42, 78)
    car.rect(4, 0, 37, 77, CR[3])
    for (a, b) in ((10, 22), (56, 68)):
        car.rect(0, a, 3, b, OL); car.rect(38, a, 41, b, OL)
    car.rect(4, 0, 37, 3, CR[2]); car.rect(7, 1, 12, 2, G_[4]); car.rect(29, 1, 34, 2, G_[4])
    car.poly([(7, 16), (34, 16), (31, 29), (10, 29)], D_[3]); car.line(12, 18, 15, 27, D_[4])
    car.rect(9, 30, 32, 54, CR[3]); car.rect(9, 30, 10, 54, CR[4]); car.rect(31, 30, 32, 54, CR[2])
    car.poly([(10, 55), (31, 55), (33, 65), (8, 65)], D_[3]); car.rect(4, 73, 37, 77, CR[2]); car.rect(6, 75, 10, 76, CR[4]); car.rect(31, 75, 35, 76, CR[4])
    car.vline(4, 4, 72, CR[4]); car.vline(37, 4, 72, CR[1])
    R.add(car, 6, 12, 0.22)
    for i in range(2):
        R.add(round_top(10, [S_[0], S_[1], S_[2], S_[3]], hole=4), 164 - i * 4, 46 - i * 6, 0.35)
    tb = box3d(18, 8, 6, CR[3], CR[2]); tb.rect(6, 0, 11, 1, S_[2])
    R.add(tb, 164, 4, 0.5)
    return R.finish((108, 26), [L_point(108, 40, 110, 72, 1.1)], pots=(54, 22, 100, 56))


# ======================================================================= 3 · Porão
def r3():
    R = Room(3, 212, 134, 32, seed=4)

    def wall(c, x0, y0, w, h):
        r = random.Random(41)
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, S_[1])
        y = y0 + 6
        while y < y0 + h - 4:
            rh = r.randrange(6, 9); x = x0 - r.randrange(0, 8)
            while x < x0 + w:
                rw = r.randrange(10, 18); col = r.choice([S_[2], S_[3], S_[2], S_[3], S_[4]])
                xa, xb = max(x0, x + 1), min(x0 + w - 1, x + rw - 2)
                if xa <= xb:
                    c.rect(xa, y + 1, xb, y + rh - 2, col); c.hline(xa, xb, y + 1, shift(col, 1)); c.hline(xa, xb, y + rh - 2, shift(col, -1))
                    if r.random() < 0.2:
                        c.set(xa + 1, y + rh - 3, L_[2])
                x += rw
            y += rh
        c.rect(x0, y0, x0 + w - 1, y0 + 5, S_[3]); c.hline(x0, x0 + w - 1, y0, S_[5]); c.hline(x0, x0 + w - 1, y0 + 5, OL)
        for x in range(x0 + 20, x0 + w, 50):
            c.box(x, y0, x + 5, y0 + 6, G_[1])
        c.hline(x0, x0 + w - 1, y0 + h - 4, S_[2]); c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, S_[1])

    R.shell(wall, lambda c, x, y, w, h: concrete(c, x, y, w, h, 2, 40, 33))
    c, x0, y0, fy = R.c, R.x0, R.y0, R.fy
    c.rect(x0 + 60, y0 + 5, x0 + 63, y0 + 30, S_[3]); c.vline(x0 + 60, y0 + 5, y0 + 30, S_[5])
    bl = Sprite(30, 34)
    bl.rect(0, 0, 29, 33, G_[1]); bl.rect(0, 0, 5, 33, G_[2]); bl.rect(24, 0, 29, 33, G_[0])
    bl.ell(15, 12, 6, 6, OL); bl.ell(15, 12, 5, 5, WHITE); bl.line(15, 12, 18, 9, CR[2]); bl.rect(8, 22, 22, 29, S_[1]); bl.rect(10, 24, 20, 27, CR[1])
    bl.stamp_on(c, x0 + 176, y0 + 2)
    for (dx, sx) in ((0, 1), (R.w - 1, -1)):
        for i in range(12):
            c.set(x0 + dx + sx * i, y0 + 6 + i, S_[5])
    # poça e goteira
    c.ell(x0 + 150, fy + 82, 22, 6, D_[1]); c.ell(x0 + 148, fy + 81, 16, 4, D_[2]); c.hline(x0 + 138, x0 + 146, fy + 79, D_[3])
    c.vline(x0 + 106, y0 + 6, y0 + 14, OL)
    R.bulb = [x0 + 106, y0 + 16]
    R.anims.append(["drip", x0 + 150, y0 + 6, fy + 80])
    R.add(crate(22, 14, 9), 8, 66, 0.4); R.add(crate(18, 12, 8), 12, 54, 0.4)
    chair = box3d(14, 12, 10, W_[2], W_[1]); chair.rect(0, 0, 13, 2, W_[3])
    R.add(chair, 184, 70, 0.4)
    R.add(round_top(9, [G_[0], G_[1], G_[2], G_[3]]), 186, 6, 0.6)
    return R.finish((106, -4), [L_point(106, 10, 120, 85, 1.1)], pots=(46, 22, 120, 60), dark=True)


# ======================================================================= 4 · Terreno Abandonado (ao ar livre)
def r4():
    R = Room(5, 236, 142, 34, cap=(W_[2], W_[3]), door=True, seed=5)

    def fence(c, x0, y0, w, h):
        r = random.Random(51)
        for y in range(y0, y0 + 14):
            c.hline(x0, x0 + w - 1, y, D_[4] if y < y0 + 8 else D_[3])
        cloud(c, x0 + 30, y0 + 4, 18); cloud(c, x0 + 160, y0 + 3, 14)
        x = x0
        while x < x0 + w:
            bw = r.randrange(12, 22); bh = r.randrange(3, 9); col = r.choice([S_[4], S_[3]])
            c.rect(x, y0 + 14 - bh, min(x0 + w - 1, x + bw - 2), y0 + 15, col)
            x += bw
        for x in range(x0, x0 + w, 9):
            col = r.choice([W_[3], W_[3], W_[4], W_[2]])
            top = y0 + 13 + r.randrange(0, 3)
            c.rect(x, top, min(x0 + w - 1, x + 7), y0 + h - 1, col)
            c.vline(x, top, y0 + h - 1, shift(col, 1)); c.vline(min(x0 + w - 1, x + 8), top, y0 + h - 1, W_[0])
        for i, col in enumerate((CR[3], G_[3], L_[4], D_[3])):
            c.ell(x0 + 90 + i * 13, y0 + 23, 6, 6, col); c.ell(x0 + 90 + i * 13, y0 + 23, 2, 2, shift(col, 1))
        c.hline(x0, x0 + w - 1, y0 + h - 1, W_[1])

    def dirt(c, x0, y0, w, h):
        r = random.Random(52)
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, SO[3])
        for _ in range(w * h // 8):
            c.set(r.uniform(x0, x0 + w), r.uniform(y0, y0 + h), r.choice([SO[2], SO[2], W_[4]]))
        for _ in range(30):
            gx, gy = r.uniform(x0, x0 + w - 8), r.uniform(y0 + 4, y0 + h - 2)
            for k in range(6):
                c.vline(gx + k, gy - r.randrange(1, 4), gy, r.choice([L_[3], L_[4], L_[2]]))

    R.shell(fence, dirt)
    R.wall_extra += [[R.x0 - 1, R.y0 - 1, R.x0 + R.w + 1, R.y0 + 16], [R.x0 + 80, R.y0 + 15, R.x0 + 142, R.y0 + 31]]   # céu e grafite
    c, x0, fy = R.c, R.x0, R.fy
    tr = Sprite(44, 40)
    for (bx, by, rr) in ((14, 16, 13), (28, 14, 13), (22, 24, 14), (10, 26, 10), (34, 26, 10)):
        tr.ell(bx, by, rr, rr * 0.9, L_[2])
    for (bx, by, rr) in ((12, 12, 7), (26, 10, 7), (20, 18, 6)):
        tr.ell(bx, by, rr, rr * 0.8, L_[3])
    for (bx, by) in ((10, 9), (24, 7), (18, 15)):
        tr.ell(bx, by, 3, 2, L_[4])
    R.add(tr, 2, -6, 1.2)
    tv = box3d(22, 8, 14, S_[3], S_[2]); tv.rect(3, 10, 18, 19, S_[1]); tv.line(5, 11, 14, 18, S_[5])
    R.add(tv, 190, 70, 0.5)
    R.add(round_top(10, [S_[0], S_[1], S_[2], S_[3]], hole=4), 196, 6, 0.3)
    cart = Sprite(26, 20)
    for xx in range(1, 25, 3):
        cart.vline(xx, 0, 14, S_[5])
    for yy in range(0, 15, 3):
        cart.hline(1, 24, yy, S_[5])
    cart.rect(0, 15, 25, 16, S_[4]); cart.ell(3, 18, 1, 1, OL); cart.ell(22, 18, 1, 1, OL)
    R.add(cart, 8, 70, 0.6)
    for i in range(5):
        R.add(box3d(9, 3, 3, B_[3], B_[2]), 150 + (i % 3) * 10, 92 - (i // 3) * 5, 0.2)
    return R.finish((-60, -80), [L_point(60, 30, 200, 140, 0.9)], pots=(54, 20, 128, 70))


# ======================================================================= 5 · Container Marítimo
def r5():
    R = Room(6, 248, 124, 30, cap=(B_[1], B_[2]), seed=6)

    def wall(c, x0, y0, w, h):
        r = random.Random(61)
        for x in range(x0, x0 + w, 6):
            c.rect(x, y0, min(x0 + w - 1, x + 5), y0 + h - 1, B_[3])
            c.vline(x, y0, y0 + h - 1, B_[4]); c.vline(min(x0 + w - 1, x + 4), y0, y0 + h - 1, B_[2])
        for _ in range(50):
            xx, yy = r.uniform(x0, x0 + w), r.uniform(y0, y0 + h - 4)
            c.rect(xx, yy, xx + r.randrange(1, 3), yy + r.randrange(1, 2), r.choice([SO[2], G_[1]]))
        c.box(x0 + 80, y0 + 6, x0 + 152, y0 + 20, B_[3], B_[1])
        text(c, x0 + 86, y0 + 9, "GRN 0451", WHITE, 2)
        for xx in (x0 + 196, x0 + 214):
            c.rect(xx, y0, xx + 3, y0 + h - 1, S_[3]); c.vline(xx, y0, y0 + h - 1, S_[5])
        c.hline(x0, x0 + w - 1, y0 + 2, TE[4])
        c.hline(x0, x0 + w - 1, y0 + h - 4, B_[1]); c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, B_[1])

    R.shell(wall, lambda c, x, y, w, h: planks_region(c, x, y, w, h, 3, 12, 62))
    R.wall_extra += [[R.x0 + 78, R.y0 + 4, R.x0 + 154, R.y0 + 22], [R.x0 + 194, R.y0 - 1, R.x0 + 220, R.fy]]   # letreiro e trilhos da porta
    c, x0, fy = R.c, R.x0, R.fy
    pal = box3d(40, 16, 6, S_[5], W_[3]); pal.rect(2, 2, 37, 13, S_[5]); pal.hline(2, 37, 2, WHITE)
    for xx in range(6, 36, 8):
        pal.vline(xx, 3, 13, S_[4])
    R.add(pal, 6, 4, 0.35)
    for i, col in enumerate((CR[3], G_[3], CR[3])):
        g = box3d(10, 7, 9, col, shift(col, -1)); g.rect(3, 0, 6, 1, S_[2])
        R.add(g, 200 + i * 11, 50 - (i % 2) * 2, 0.6)
    sb = Sprite(40, 14); sb.ell(19.5, 7, 19, 6, D_[2]); sb.ell(19.5, 5, 17, 3, D_[3]); sb.ell(4, 7, 4, 4, D_[1])
    R.add(sb, 8, 66, 0.15)
    fan = Sprite(18, 20); fan.ell(8.5, 8.5, 8, 8, S_[3]); fan.ell(8.5, 8.5, 6, 6, S_[4])
    for a in range(0, 360, 90):
        fan.line(8.5, 8.5, 8.5 + 5 * math.cos(math.radians(a + 20)), 8.5 + 5 * math.sin(math.radians(a + 20)), S_[2])
    fan.rect(7, 16, 10, 19, S_[2])
    R.add(fan, 210, 70, 0.8)
    return R.finish((118, -10), [L_poly([(0, -6), (236, -6), (236, 6), (0, 6)], 0.6), L_point(118, 20, 140, 70, 0.8),
                                 L_poly([(236, -10), (248, -10), (248, 90), (222, 90)], 0.5)], pots=(56, 14, 136, 64))


# ======================================================================= 6 · Sobrado na Favela
def r6():
    R = Room(4, 228, 140, 34, cap=(B_[1], B_[2]), seed=7)

    def wall(c, x0, y0, w, h):
        wall_bricks(c, x0, y0, w, h, B_, base=3, bw=10, bh=4, seed=71, plaster=[(8, 4, 30, 12), (190, 14, 24, 10)])

    def tiles(c, x0, y0, w, h):
        r = random.Random(72)
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, S_[5])
        for y in range(y0, y0 + h, 12):
            for x in range(x0 + (((y - y0) // 12) % 2) * 6, x0 + w, 12):
                col = r.choice([S_[5], S_[5], S_[6]])
                c.rect(x + 1, y + 1, min(x0 + w - 1, x + 11), min(y0 + h - 1, y + 11), col)
            c.hline(x0, x0 + w - 1, y, S_[4])

    R.shell(wall, tiles)
    c, x0, y0, fy = R.c, R.x0, R.y0, R.fy

    def favela(c, x, y, w, h):
        for yy in range(y, y + h):
            c.hline(x, x + w - 1, yy, D_[4] if yy < y + 6 else L_[3])
        cols = [CR[3], G_[3], D_[3], L_[5], B_[4], S_[5], CR[4], TE[3], PL[3]]
        for row in range(4):
            for i in range(10):
                hx = x + i * 6 + (row % 2) * 3; hy = y + 5 + row * 5
                if hx + 5 < x + w and hy + 4 < y + h:
                    c.rect(hx, hy, hx + 5, hy + 4, cols[(i * 3 + row * 5) % len(cols)]); c.hline(hx, hx + 5, hy, OL); c.set(hx + 2, hy + 2, OL)
                    if (i + row) % 4 == 0:
                        c.rect(hx + 1, hy - 2, hx + 3, hy - 1, D_[2])
        c.line(x, y + 8, x + w - 1, y + 12, OL)

    window_on_wall(c, x0 + 90, y0 + 6, 62, 22, S_[3], view=favela)
    c.line(x0 + 20, y0, x0 + 26, y0 + 24, OL); c.box(x0 + 24, y0 + 22, x0 + 30, y0 + 28, WHITE)
    sofa = Sprite(60, 30)
    sofa.rect(0, 0, 59, 8, L_[2]); sofa.hline(0, 59, 0, L_[3]); sofa.rect(0, 9, 59, 25, L_[3]); sofa.hline(0, 59, 9, L_[4])
    sofa.rect(0, 0, 6, 27, L_[2]); sofa.rect(53, 0, 59, 27, L_[1]); sofa.rect(0, 26, 59, 29, L_[1]); sofa.vline(29, 10, 24, L_[2])
    sofa.rect(10, 11, 22, 19, CR[3]); sofa.rect(36, 11, 46, 19, G_[3])
    R.add(sofa, 6, -6, 0.3)
    tvc = crate(30, 12, 8); R.add(tvc, 192, 6, 0.4)
    tv = box3d(28, 8, 14, S_[2], S_[1]); tv.rect(3, 10, 21, 19, TE[1]); tv.rect(4, 11, 9, 13, TE[3])
    R.add(tv, 193, -10, 0.6)
    chair = Sprite(16, 16); chair.rect(0, 0, 15, 4, WHITE); chair.rect(0, 5, 15, 13, S_[6]); chair.rect(1, 14, 2, 15, S_[5]); chair.rect(13, 14, 14, 15, S_[5])
    R.add(chair, 200, 70, 0.5)
    R.add(round_top(6, [D_[0], D_[1], D_[2], D_[3]]), 12, 92, 0.8)
    return R.finish((121, -50), [L_poly([(90, -20), (152, -20), (144, 70), (84, 70)], 0.9), L_point(121, 30, 170, 100, 0.55)],
                    pots=(50, 30, 128, 72))


# ======================================================================= 7 · Galpão Industrial
def r7():
    R = Room(7, 260, 152, 34, seed=8)

    def wall(c, x0, y0, w, h):
        for x in range(x0, x0 + w, 5):
            c.rect(x, y0, min(x0 + w - 1, x + 4), y0 + h - 1, S_[3]); c.vline(x, y0, y0 + h - 1, S_[4]); c.vline(min(x0 + w - 1, x + 3), y0, y0 + h - 1, S_[2])
        for x in (x0, x0 + 86, x0 + 172, x0 + w - 6):
            c.rect(x, y0, x + 5, y0 + h - 1, S_[2]); c.vline(x + 1, y0, y0 + h - 1, S_[4])
        for x in (x0 + 24, x0 + 110, x0 + 196):
            window_on_wall(c, x, y0 + 5, 40, 12, S_[2])
        c.hline(x0, x0 + w - 1, y0 + h - 4, S_[2]); c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, S_[1])

    def floor(c, x0, y0, w, h):
        concrete(c, x0, y0, w, h, 4, 36, 82)
        for x in range(x0, x0 + w):
            c.vline(x, y0 + 4, y0 + 5, G_[3] if ((x - x0) // 6) % 2 else OL)

    R.shell(wall, floor)
    R.wall_extra += [[R.x0 + x - 3, R.y0 + 2, R.x0 + x + 43, R.y0 + 20] for x in (24, 110, 196)]   # janelas altas
    for i in range(3):
        pl = box3d(36, 14, 5, W_[4], W_[3], lines=6)
        R.add(pl, 6, 90 - i * 22, 0.25)
        R.add(box3d(30, 10, 8, W_[3], W_[2], lines=10), 9, 80 - i * 22, 0.4)
    for (xx, yy, col) in ((224, 6, D_), (236, 14, B_), (222, 24, G_)):
        R.add(round_top(7, [col[0], col[1], col[2], col[3]], hole=2), xx, yy, 0.7)
    fk = Sprite(34, 46)
    fk.rect(4, 12, 33, 41, G_[3]); fk.hline(4, 33, 12, G_[4]); fk.rect(4, 36, 33, 41, G_[2])
    fk.rect(8, 18, 29, 32, S_[1]); fk.rect(10, 20, 27, 30, S_[2]); fk.ell(18.5, 25, 4, 3, S_[0])
    fk.rect(6, 0, 9, 13, S_[3]); fk.rect(26, 0, 29, 13, S_[3]); fk.rect(0, 40, 4, 45, OL); fk.rect(30, 40, 34, 45, OL)
    R.add(fk, 216, 80, 0.5)
    lights = [L_point(x, 50, 70, 50, 0.85) for x in (60, 130, 200)]
    lights += [L_poly([(x, -20), (x + 40, -20), (x + 58, 40), (x + 18, 40)], 0.45) for x in (24, 110, 196)]
    return R.finish((130, 10), lights, pots=(56, 30, 150, 80))


# ======================================================================= 8 · Sítio na Serra
def r8():
    R = Room(8, 270, 156, 36, cap=(W_[1], W_[2]), seed=9)

    def logs(c, x0, y0, w, h):
        r = random.Random(91)
        for y in range(y0, y0 + h - 3, 7):
            c.rect(x0, y, x0 + w - 1, y + 6, W_[3]); c.hline(x0, x0 + w - 1, y, W_[4]); c.hline(x0, x0 + w - 1, y + 5, W_[2]); c.hline(x0, x0 + w - 1, y + 6, W_[1])
            for _ in range(5):
                gx = r.uniform(x0, x0 + w); c.hline(gx, gx + r.uniform(5, 12), y + 3, W_[2])
        c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, W_[1])

    R.shell(logs, lambda c, x, y, w, h: planks_region(c, x, y, w, h, 4, 8, 93))
    c, x0, y0, fy = R.c, R.x0, R.y0, R.fy

    def mountains(c, x, y, w, h):
        for yy in range(y, y + h):
            c.hline(x, x + w - 1, yy, D_[4] if yy < y + h * 0.5 else D_[3])
        c.poly([(x, y + h), (x + 16, y + 4), (x + 30, y + h)], S_[4]); c.poly([(x + 12, y + 8), (x + 16, y + 4), (x + 20, y + 8)], WHITE)
        c.poly([(x + 22, y + h), (x + 40, y + 2), (x + w, y + h)], S_[3]); c.poly([(x + 36, y + 6), (x + 40, y + 2), (x + 44, y + 6)], WHITE)
        c.rect(x, y + h - 6, x + w - 1, y + h - 1, L_[3])
        for xx in range(x + 1, x + w - 3, 5):
            c.poly([(xx, y + h - 2), (xx + 2, y + h - 9), (xx + 4, y + h - 2)], L_[1])

    window_on_wall(c, x0 + 60, y0 + 6, 56, 24, W_[2], view=mountains)
    c.box(x0 + 14, y0 + 16, x0 + 50, y0 + 18, W_[2])
    for i, col in enumerate((CR[3], G_[3], L_[4], CR[2])):
        c.rect(x0 + 17 + i * 8, y0 + 9, x0 + 22 + i * 8, y0 + 15, col); c.rect(x0 + 18 + i * 8, y0 + 8, x0 + 21 + i * 8, y0 + 8, S_[3])
    fp = Sprite(60, 46)
    r = random.Random(92)
    for y in range(0, 46, 6):
        for x in range(((y // 6) % 2) * 4, 60, 9):
            col = r.choice([S_[4], S_[3], S_[5]])
            fp.rect(x, y, min(59, x + 7), y + 4, col); fp.hline(x, min(59, x + 7), y, shift(col, 1))
    fp.rect(12, 18, 47, 45, S_[1]); fp.rect(15, 21, 44, 45, OL); fp.rect(6, 14, 53, 17, W_[2])
    fp.stamp_on(c, x0 + 196, y0 - 2)
    c.rect(x0 + 212, fy + 4, x0 + 238, fy + 8, W_[1])
    R.anims.append(["fire", x0 + 212, fy + 5, 26])
    rug(c, x0 + 70, fy + 40, 120, 70, CR[3], CR[2], G_[3])
    for i in range(6):
        lg = box3d(24, 4, 4, W_[3], W_[2]); lg.ell(1.5, 4, 1.5, 1.5, W_[4])
        R.add(lg, 236 + (i % 2) * 3, 30 - (i // 2) * 7, 0.4)
    rk = Sprite(22, 26); rk.rect(1, 0, 20, 12, W_[2])
    for xx in range(3, 20, 4):
        rk.vline(xx, 1, 11, W_[3])
    rk.rect(0, 13, 21, 22, W_[3]); rk.line(0, 25, 21, 24, W_[1])
    R.add(rk, 30, 30, 0.6)
    return R.finish((225, 0), [L_point(225, 8, 150, 100, 1.05), L_poly([(60, -30), (116, -30), (108, 50), (52, 50)], 0.55)],
                    pots=(74, 44, 112, 62))


# ======================================================================= 9 · Fazenda Paraíso Verde (estufa)
def r9():
    R = Room(9, 284, 160, 38, cap=(S_[5], WHITE), seed=10)

    def glass(c, x0, y0, w, h):
        for y in range(y0, y0 + 14):
            c.hline(x0, x0 + w - 1, y, D_[4] if y < y0 + 8 else D_[3])
        c.rect(x0, y0 + 14, x0 + w - 1, y0 + h - 1, L_[3])
        for y in range(y0 + 16, y0 + h, 3):
            c.hline(x0, x0 + w - 1, y, L_[4])
        bn = Sprite(30, 22); bn.rect(0, 8, 29, 21, CR[2]); bn.poly([(0, 9), (15, 0), (29, 9)], CR[1]); bn.rect(10, 12, 19, 21, WHITE); bn.rect(12, 14, 17, 21, CR[2])
        bn.stamp_on(c, x0 + 190, y0 + 6)
        c.rect(x0 + 226, y0 + 4, x0 + 236, y0 + 27, S_[5]); c.ell(x0 + 231, y0 + 4, 5, 3, S_[4])
        for x in range(x0, x0 + w, 34):
            c.rect(x, y0, x + 1, y0 + h - 1, S_[6])
        c.rect(x0, y0 + 18, x0 + w - 1, y0 + 19, S_[6])
        for x in range(x0 + 8, x0 + w, 34):
            for k in range(7):
                c.set(x + k, y0 + 14 - k, WHITE)
        c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, S_[5])

    def soil(c, x0, y0, w, h):
        r = random.Random(102)
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, SO[2])
        for y in range(y0 + 4, y0 + h, 20):
            c.rect(x0, y, x0 + w - 1, y + 11, SO[3]); c.hline(x0, x0 + w - 1, y, W_[3]); c.hline(x0, x0 + w - 1, y + 11, SO[1])
            c.rect(x0, y + 12, x0 + w - 1, y + 14, D_[2]); c.hline(x0, x0 + w - 1, y + 12, D_[3])
            for _ in range(w // 3):
                c.set(r.uniform(x0, x0 + w), r.uniform(y + 2, y + 10), r.choice([SO[2], W_[3]]))

    R.shell(glass, soil)
    R.wall_extra.append([R.x0 - 1, R.y0 - 1, R.x0 + R.w + 1, R.fy - 6])   # parede toda é vista (nada pendurado)
    wb = Sprite(30, 18); wb.poly([(0, 2), (22, 2), (19, 11), (3, 11)], L_[3]); wb.rect(3, 0, 19, 3, SO[3]); wb.line(22, 5, 29, 3, W_[2]); wb.ell(10, 14, 3, 3, OL); wb.ell(10, 14, 1, 1, S_[3])
    R.add(wb, 8, 96, 0.4)
    for i in range(3):
        sk = sack(14, 16, PA[3]); sk.rect(3, 6, 10, 9, L_[3])
        R.add(sk, 244 + i * 12, 4 + (i % 2) * 3, 0.5)
    hose = Sprite(20, 14)
    for k in range(3):
        hose.ell(9.5, 7, 9 - k * 3, 6 - k * 2, L_[1]); hose.ell(9.5, 7, 8 - k * 3, 5 - k * 2, L_[3])
    R.add(hose, 250, 96, 0.2)
    return R.finish((150, -120), [L_point(142, 60, 260, 160, 1.0)], pots=(52, 22, 180, 92))


# ======================================================================= 10 · Ilha Privada (deck ao ar livre)
def r10():
    R = Room(11, 304, 168, 40, cap=(W_[2], W_[3]), seed=11)

    def sea(c, x0, y0, w, h):
        r = random.Random(111)
        for y in range(y0, y0 + 16):
            c.hline(x0, x0 + w - 1, y, D_[4] if y < y0 + 10 else D_[3])
        cloud(c, x0 + 40, y0 + 5, 18); cloud(c, x0 + 200, y0 + 7, 14)
        c.ell(x0 + 250, y0 + 7, 6, 6, G_[4]); c.ell(x0 + 250, y0 + 7, 4, 4, WHITE)
        for y in range(y0 + 16, y0 + h):
            c.hline(x0, x0 + w - 1, y, TE[2] if y < y0 + 26 else TE[3])
        for _ in range(60):
            xx, yy = r.uniform(x0, x0 + w), r.uniform(y0 + 17, y0 + h - 2)
            c.hline(xx, xx + r.randrange(2, 6), yy, TE[4] if r.random() < 0.7 else WHITE)
        c.ell(x0 + 110, y0 + 17, 18, 3, L_[2]); c.ell(x0 + 110, y0 + 16, 12, 2, L_[3])

    def sand(c, x0, y0, w, h):
        r = random.Random(112)
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, W_[5])
        for x in range(x0, x0 + w):
            if r.random() < 0.5:
                c.set(x, y0, WHITE)
        for _ in range(w * h // 7):
            c.set(r.uniform(x0, x0 + w), r.uniform(y0 + 1, y0 + h), r.choice([W_[4], W_[4], PA[3], PA[4]]))
        for (sx, sy) in ((30, 100), (240, 80), (160, 110)):
            c.ell(x0 + sx, y0 + sy, 2, 1, CR[4])

    R.shell(sea, sand)
    R.wall_extra.append([R.x0 - 1, R.y0 - 1, R.x0 + R.w + 1, R.fy - 6])   # parede toda é vista (nada pendurado)

    from palmeira import palm
    R.add(palm(), -6, -10, 0.9)                       # uma palmeira só, no canto esquerdo
    ch = Sprite(20, 40)                               # espreguiçadeira listrada
    ch.rect(0, 0, 19, 13, W_[3]); ch.rect(1, 1, 18, 12, WHITE)
    for yy in range(14, 36):
        ch.hline(0, 19, yy, W_[2] if yy in (14, 35) else (D_[3] if (yy // 3) % 2 else WHITE))
    ch.vline(0, 0, 35, W_[2]); ch.vline(19, 0, 35, W_[2]); ch.rect(0, 36, 1, 39, W_[1]); ch.rect(18, 36, 19, 39, W_[1])
    R.add(ch, 252, 60, 0.3)
    tw = Sprite(18, 10); tw.rect(0, 0, 17, 9, CR[3]); tw.hline(0, 17, 3, WHITE); tw.hline(0, 17, 6, WHITE)
    R.add(tw, 228, 100, 0.05)
    cl = box3d(24, 10, 9, WHITE, D_[3]); cl.rect(8, 12, 15, 15, WHITE)
    R.add(cl, 20, 104, 0.5)
    sb = Sprite(12, 44); sb.ell(5.5, 22, 5, 21, G_[3]); sb.vline(5, 4, 40, CR[3])
    R.add(sb, 8, 50, 0.2)
    for tx in (64, 236):
        tk = Sprite(6, 26); tk.rect(2, 6, 3, 25, W_[2]); tk.rect(0, 0, 5, 6, W_[3])
        R.add(tk, tx, 30, 1.0)
        R.anims.append(["torch", R.x0 + tx + 3, R.fy + 29])
    R.anims.append(["waves", R.y0 + 18, R.fy - 2])
    return R.finish((-80, -140), [L_point(152, 40, 300, 180, 1.05)], pots=(52, 24, 200, 96))


# ======================================================================= 11 · Mina de Ouro Desativada
def r11():
    R = Room(10, 296, 164, 40, cap=(SO[0], SO[1]), seed=12)

    def rock(c, x0, y0, w, h):
        r = random.Random(121)
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, SO[1])
        for _ in range(140):
            x, y = r.uniform(x0 - 6, x0 + w), r.uniform(y0 - 4, y0 + h - 4)
            ww, hh = r.uniform(8, 18), r.uniform(5, 10)
            col = r.choice([SO[2], SO[1], SO[2], SO[3], SO[0]])
            c.poly([(x, y + hh * 0.3), (x + ww * 0.4, y), (x + ww, y + hh * 0.2), (x + ww * 0.9, y + hh), (x + ww * 0.1, y + hh * 0.9)], col)
        for _ in range(26):
            x, y = r.uniform(x0, x0 + w - 6), r.uniform(y0 + 3, y0 + h - 6)
            for k in range(r.randrange(3, 6)):
                c.set(x + k, y + math.sin(k) * 1.4, G_[3] if k % 2 else G_[2])
        for x in (x0 + 30, x0 + w - 40):
            c.rect(x, y0, x + 7, y0 + h - 1, W_[2]); c.vline(x + 1, y0, y0 + h - 1, W_[3])
        c.rect(x0, y0, x0 + w - 1, y0 + 6, W_[2]); c.hline(x0, x0 + w - 1, y0 + 1, W_[3]); c.hline(x0, x0 + w - 1, y0 + 6, W_[1])
        c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, SO[0])

    def floor(c, x0, y0, w, h):
        r = random.Random(122)
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, SO[2])
        for _ in range(w * h // 9):
            c.set(r.uniform(x0, x0 + w), r.uniform(y0, y0 + h), r.choice([SO[1], SO[3], SO[2]]))
        ry = y0 + h - 18
        for x in range(x0, x0 + w, 10):
            c.rect(x, ry - 2, x + 5, ry + 9, W_[1]); c.hline(x, x + 5, ry - 2, W_[2])
        for yy in (ry, ry + 6):
            c.hline(x0, x0 + w - 1, yy, S_[4]); c.hline(x0, x0 + w - 1, yy + 1, S_[3])

    R.shell(rock, floor)
    c, x0, y0 = R.c, R.x0, R.y0
    for lx in (34, 148, 262):
        c.vline(x0 + lx, y0 + 6, y0 + 14, OL)
        ln = Sprite(9, 11); ln.rect(0, 0, 8, 1, S_[2]); ln.rect(1, 2, 7, 8, G_[4]); ln.rect(0, 9, 8, 10, S_[2]); ln.vline(0, 2, 8, S_[2]); ln.vline(8, 2, 8, S_[2])
        ln.stamp_on(c, x0 + lx - 4, y0 + 15)
        R.anims.append(["lantern", x0 + lx, y0 + 20])
    R.anims.append(["sparkle", x0, y0 + 6, x0 + R.w, y0 + R.wh - 4])
    mc = Sprite(44, 28)
    mc.poly([(0, 6), (43, 6), (40, 22), (3, 22)], S_[2]); mc.hline(0, 43, 6, S_[4])
    for xx in (10, 22, 34):
        mc.vline(xx, 7, 21, S_[1])
    for k in range(7):
        mc.ell(5 + k * 6, 5, 4, 3, G_[2]); mc.ell(4 + k * 6, 4, 2, 1, G_[3])
    for wx in (10, 34):
        mc.ell(wx, 24, 4, 3, OL)
    R.add(mc, 12, 92, 0.5)
    for i in range(2):
        cr = crate(20, 12, 9); text(cr, 4, 14, "XX", CR[2])
        R.add(cr, 270, 70 - i * 18, 0.5)
    pk = Sprite(20, 24); pk.line(4, 2, 16, 23, W_[2]); pk.line(5, 2, 17, 23, W_[3]); pk.poly([(0, 4), (12, 0), (13, 3), (2, 7)], S_[4])
    R.add(pk, 250, 90, 0.6)
    return R.finish((152, -10), [L_point(34, 0, 120, 90, 1.05), L_point(148, 0, 110, 90, 0.95), L_point(262, 0, 120, 90, 1.05)], pots=(52, 20, 192, 86), dark=True)


# ======================================================================= 12 · Bunker Militar
def r12():
    R = Room(12, 312, 170, 40, cap=(S_[1], S_[2]), seed=13)

    def panels(c, x0, y0, w, h):
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, S_[3])
        for y in range(y0, y0 + h - 4, 13):
            for x in range(x0 + (((y - y0) // 13) % 2) * 16, x0 + w, 32):
                c.rect(x + 1, y + 1, min(x0 + w - 1, x + 30), y + 11, S_[3]); c.hline(x + 1, min(x0 + w - 1, x + 30), y + 1, S_[4])
                c.set(x + 3, y + 3, S_[2]); c.set(min(x0 + w - 1, x + 28), y + 3, S_[2])
        c.rect(x0, y0, x0 + w - 1, y0 + 4, TE[1]); c.hline(x0, x0 + w - 1, y0, TE[2])
        for x in range(x0, x0 + w):
            c.vline(x, y0 + h - 8, y0 + h - 5, G_[3] if ((x - x0) // 6) % 2 else OL)
        c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, S_[1])

    R.shell(panels, lambda c, x, y, w, h: concrete(c, x, y, w, h, 3, 40, 133))
    c, x0, y0 = R.c, R.x0, R.y0
    cx, cy = x0 + 34, y0 + 18
    c.ell(cx, cy, 16, 16, OL); c.ell(cx, cy, 15, 15, S_[4]); c.ell(cx, cy, 12, 12, S_[3]); c.ell(cx, cy, 6, 6, OL); c.ell(cx, cy, 5, 5, CR[2])
    for a in range(0, 360, 45):
        c.set(cx + 13.5 * math.cos(math.radians(a)), cy + 13.5 * math.sin(math.radians(a)), S_[5])
    for a in (0, 60, 120):
        c.line(cx - 5 * math.cos(math.radians(a)), cy - 5 * math.sin(math.radians(a)), cx + 5 * math.cos(math.radians(a)), cy + 5 * math.sin(math.radians(a)), CR[3])
    for i, mx in enumerate((x0 + 90, x0 + 124, x0 + 158)):
        c.box(mx, y0 + 8, mx + 28, y0 + 28, S_[1]); c.rect(mx + 2, y0 + 10, mx + 26, y0 + 26, TE[0])
        if i == 0:
            c.ell(mx + 14, y0 + 18, 6, 6, TE[1]); c.line(mx + 14, y0 + 18, mx + 19, y0 + 14, TE[4])
        elif i == 1:
            for k in range(22):
                c.set(mx + 3 + k, y0 + 18 + round(4 * math.sin(k / 2.5)), TE[4])
        else:
            for k in range(4):
                c.hline(mx + 4, mx + 6 + (k * 7) % 16, y0 + 13 + k * 3, TE[4] if k % 2 else G_[3])
    for i in range(3):
        lk = box3d(18, 4, 32, L_[2], L_[2]); lk.rect(13, 18, 14, 24, S_[4])
        for yy in range(8, 14, 2):
            lk.hline(4, 13, yy, L_[1])
        lk.stamp_on(c, x0 + 230 + i * 20, y0 + 4)
    R.anims.append(["siren", x0 + 196, y0 + 6])
    for row in range(3):
        for i in range(4 - row):
            R.add(sack(18, 9, W_[4]), 240 + i * 16 + row * 8, 108 - row * 7, 0.4)
    for i in range(2):
        bx = box3d(26, 12, 9, L_[2], L_[1]); bx.rect(4, 14, 12, 16, WHITE)
        R.add(bx, 10 + i * 30, 104, 0.5)
    lights = [L_point(x, 50, 80, 56, 0.8) for x in (70, 156, 242)]
    return R.finish((156, 0), lights, pots=(50, 22, 216, 90))


ROOMS = [r1, r0, r2, r3, r6, r4, r5, r7, r8, r9, r11, r10, r12]   # ordem do jogo


if __name__ == "__main__":
    only = [int(a) for a in sys.argv[1:]] or range(len(ROOMS))
    os.makedirs(OUT, exist_ok=True)
    mp = os.path.join(OUT, "meta.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    for i in only:
        meta[str(i)] = ROOMS[i]()
        print("ok", i)
    json.dump(meta, open(mp, "w"), indent=1)
    from cenarios import WHERE
    # um degrau para baixo / para cima na rampa de cada cor: o jogo ilumina as plantas com isso
    json.dump({c: [shift(c, -1), shift(c, 1)] for c in WHERE}, open(os.path.join(OUT, "shift.json"), "w"))
