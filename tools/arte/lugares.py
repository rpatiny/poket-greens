"""Lugares da cidade (vista de cima, mesmo estilo dos esconderijos). Quando o neto está numa atividade,
a cena vai para o lugar: Café, Energético (conveniência), Bar do Zé, Biblioteca, Academia, Beco, Praça, Spa e Fliperama.

Gera em assets/sprites/v2/comodos/: c_<id>.png, c_<id>_s.png, c_<id>_l.png e cidade.json (meta + animações)
    python3 tools/arte/lugares.py
"""
import json, math, os, random, sys
sys.path.insert(0, os.path.dirname(__file__))
from cenarios import Sprite, shift, RAMPS, OL, text, cloud
from estilo_topdown import planks_region
from comodos import (Room, OUT, L_point, L_poly, box3d, crate, round_top, sack, rug, wall_bricks, concrete,
                     window_on_wall, W_, S_, PA, CR, D_, G_, L_, B_, SO, PL, TE, WHITE)

RW, RH, WH = 224, 132, 40


def tiles(c, x0, y0, w, h, a, b, size=10):
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            c.set(x, y, a if ((x - x0) // size + (y - y0) // size) % 2 else b)
        if (y - y0) % size == 0:
            c.hline(x0, x0 + w - 1, y, shift(b, -1))


def plain_wall(col, trim=None):
    def f(c, x0, y0, w, h):
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, col)
        for y in range(y0 + 3, y0 + h - 4, 6):
            for x in range(x0 + ((y // 6) % 2) * 3, x0 + w, 7):
                c.set(x, y, shift(col, 1 if (x + y) % 3 else -1))
        c.hline(x0, x0 + w - 1, y0 + h - 4, trim or shift(col, -1)); c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, shift(col, -2))
    return f


def stool(col=CR[3]):
    sp = Sprite(10, 14); sp.ell(4.5, 4, 4.5, 3.5, col); sp.ell(3.5, 3, 2, 1.5, shift(col, 1)); sp.rect(4, 8, 5, 13, S_[3]); sp.hline(1, 8, 13, S_[2])
    return sp


def table_round(r=9, col=W_[3]):
    sp = Sprite(2 * r + 2, 2 * r + 6)
    sp.ell(r, r, r, r * 0.8, col); sp.ell(r - 2, r - 2, r * 0.5, r * 0.35, shift(col, 1))
    sp.rect(r - 1, r + 3, r + 1, 2 * r + 4, W_[1]); sp.hline(r - 4, r + 4, 2 * r + 5, W_[1])
    return sp


def plant_pot():
    sp = Sprite(14, 20)
    for (dx, dy) in ((-4, -2), (4, -2), (0, -5), (-2, 2), (3, 2)):
        sp.ell(7 + dx, 8 + dy, 3, 4, L_[3]); sp.ell(6 + dx, 7 + dy, 1, 2, L_[4])
    sp.poly([(2, 12), (12, 12), (10, 19), (4, 19)], B_[3]); sp.hline(2, 12, 12, B_[4])
    return sp


# ======================================================================= Spa
def spa():
    R = Room("c_spa", RW, RH, WH, cap=(TE[1], TE[2]), door=True, seed=31)
    R.shell(lambda c, x, y, w, h: (tiles(c, x, y, w, h - 4, TE[3], TE[4], 8), c.rect(x, y + h - 4, x + w - 1, y + h - 1, TE[1])),
            lambda c, x, y, w, h: tiles(c, x, y, w, h, PA[3], PA[4], 12))
    c, x0, y0, fy = R.c, R.x0, R.y0, R.fy
    # banheira de hidromassagem (no chão)
    tub = Sprite(70, 44)
    tub.rect(0, 0, 69, 43, S_[6]); tub.rect(0, 0, 69, 1, WHITE); tub.rect(0, 40, 69, 43, S_[5])
    tub.rect(5, 5, 64, 37, TE[2]); tub.rect(7, 7, 62, 35, TE[3])
    for k in range(8):
        tub.hline(10 + k * 6, 14 + k * 6, 12 + (k % 3) * 8, TE[4])
    R.add(tub, 12, 36, 0.25)
    # maca de massagem
    mt = box3d(24, 46, 6, WHITE, S_[5]); mt.rect(3, 2, 20, 8, PA[3]); mt.rect(2, 12, 21, 44, PA[4])
    R.add(mt, 120, 30, 0.35)
    # toalhas dobradas, plantas, velas
    for i in range(3):
        tw = box3d(14, 8, 3, [WHITE, TE[4], PA[4]][i], shift([WHITE, TE[4], PA[4]][i], -1)); R.add(tw, 176, 66 - i * 4, 0.2)
    R.add(plant_pot(), 4, 4, 0.8); R.add(plant_pot(), 198, 4, 0.8)
    # rádio na prateleira (parede)
    c.rect(x0 + 150, y0 + 22, x0 + 190, y0 + 24, W_[2]); c.hline(x0 + 150, x0 + 190, y0 + 25, OL)
    rd = Sprite(18, 10); rd.rect(0, 0, 17, 9, CR[2]); rd.hline(0, 17, 0, CR[3]); rd.ell(5, 5, 3, 3, S_[1]); rd.ell(5, 5, 1, 1, S_[3]); rd.rect(10, 2, 15, 4, G_[3]); rd.vline(15, -4, 0, S_[3])
    rd.stamp_on(c, x0 + 160, y0 + 12)
    for (vx, vy) in ((90, 6), (100, 9), (110, 6)):
        c.rect(x0 + vx, y0 + vy, x0 + vx + 2, y0 + vy + 4, PA[4]); c.set(x0 + vx + 1, y0 + vy - 1, G_[4])
    R.anims += [["steam", x0 + 47, fy + 40, 30], ["ripple", x0 + 47, fy + 58, 24], ["candle", x0 + 91, y0 + 5], ["candle", x0 + 101, y0 + 8],
                ["candle", x0 + 111, y0 + 5], ["notes", x0 + 168, y0 + 12]]
    return R.finish((112, -30), [L_point(112, 20, 140, 90, 1.0), L_point(47, 58, 50, 30, 0.5)], pots=(100, 40, 0, 0))


# ======================================================================= Fliperama
def fliperama():
    R = Room("c_fliperama", RW, RH, WH, cap=(PL[0], PL[1]), door=True, seed=32)

    def wall(c, x0, y0, w, h):
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, PL[0])
        for x in range(x0, x0 + w, 4):
            c.vline(x, y0, y0 + h - 1, PL[1])
        # letreiro de neon desenhado: moldura, joystick e duas estrelas
        sx, sy = x0 + 66, y0 + 4
        c.box(sx, sy, sx + 88, sy + 26, PL[2], CR[4])
        c.rect(sx + 1, sy + 1, sx + 87, sy + 25, PL[0])
        c.ell(sx + 44, sy + 9, 4, 4, CR[4]); c.ell(sx + 44, sy + 9, 2, 2, WHITE); c.vline(sx + 44, sy + 13, sy + 19, TE[4])
        c.rect(sx + 36, sy + 19, sx + 52, sy + 22, TE[4]); c.hline(sx + 37, sx + 51, sy + 20, TE[3])
        for (qx, qy, col) in ((sx + 16, sy + 13, G_[4]), (sx + 72, sy + 13, G_[4])):
            for (dx, dy) in ((0, -5), (0, 5), (-5, 0), (5, 0), (-3, -3), (3, 3), (-3, 3), (3, -3)):
                c.line(qx, qy, qx + dx, qy + dy, col)
            c.set(qx, qy, WHITE)
        c.rect(x0, y0 + h - 4, x0 + w - 1, y0 + h - 1, OL)

    def carpet(c, x0, y0, w, h):
        r = random.Random(3)
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, PL[1])
        for _ in range(w * h // 110):
            x, y = r.uniform(x0, x0 + w - 3), r.uniform(y0, y0 + h - 3)
            col = r.choice([TE[2], CR[2], G_[2], D_[2]])
            c.poly([(x, y), (x + 3, y + 1), (x + 1, y + 3)], col)
    R.shell(wall, carpet)
    c, x0, y0, fy = R.c, R.x0, R.y0, R.fy
    # duas máquinas de pinball (vista de cima): mesa inclinada com vidro, rampas e flippers (os flippers são animados)
    def pinball(col):
        sp = Sprite(30, 58)
        sp.rect(0, 0, 29, 12, col); sp.rect(2, 2, 27, 10, OL); sp.rect(3, 3, 26, 9, PL[2])          # placar
        sp.rect(0, 12, 29, 57, shift(col, -1)); sp.rect(3, 14, 26, 52, D_[1])                      # mesa
        for (bx, by, cc) in ((9, 22, CR[3]), (20, 22, G_[3]), (14, 30, TE[3])): sp.ell(bx, by, 3, 3, cc); sp.ell(bx - 1, by - 1, 1, 1, WHITE)
        sp.line(4, 38, 9, 46, S_[5]); sp.line(25, 38, 20, 46, S_[5])
        sp.rect(2, 53, 27, 57, shift(col, -2))
        return sp
    for i, col in enumerate((CR[2], D_[2])):
        R.add(pinball(col), 20 + i * 40, 2, 0.5)
        R.anims.append(["pinball", x0 + 20 + i * 40, fy + 2])
    # fliperamas (arcades) encostados na parede
    def arcade(col):
        sp = Sprite(24, 34)
        sp.rect(0, 0, 23, 33, col); sp.rect(0, 0, 23, 3, shift(col, 1)); sp.rect(3, 5, 20, 17, OL); sp.rect(4, 6, 19, 16, TE[0])
        sp.rect(2, 19, 21, 24, shift(col, -1)); sp.ell(7, 21, 1.5, 1.5, CR[3]); sp.ell(14, 21, 1, 1, G_[3]); sp.ell(17, 21, 1, 1, TE[3])
        sp.rect(2, 26, 21, 33, shift(col, -2))
        return sp
    for i, col in enumerate((G_[2], TE[2], CR[2])):
        R.add(arcade(col), 128 + i * 30, -10, 0.6)
        R.anims.append(["arcade", x0 + 128 + i * 30, fy - 10])
    R.add(box3d(30, 10, 6, S_[2], S_[1]), 150, 60, 0.3)
    R.anims.append(["neon", x0 + 66, y0 + 4, 88, 26])
    return R.finish((112, -10), [L_point(50, 30, 70, 50, 0.7), L_point(160, 10, 70, 50, 0.8)], pots=(100, 40, 0, 0), dark=True)


# ======================================================================= Café
def cafe():
    R = Room("c_cafe", RW, RH, WH, cap=(W_[1], W_[2]), door=True, seed=33)

    def wall(c, x0, y0, w, h):
        wall_bricks(c, x0, y0, w, h, B_, base=3, bw=10, bh=4, seed=331)
        c.box(x0 + 14, y0 + 6, x0 + 60, y0 + 28, W_[2]); c.rect(x0 + 16, y0 + 8, x0 + 58, y0 + 26, OL)       # quadro do cardápio
        for k, yy in enumerate((11, 15, 19, 23)):
            c.hline(x0 + 19, x0 + 19 + 20 + (k * 7) % 14, y0 + yy, WHITE if k % 2 else PA[3]); c.hline(x0 + 48, x0 + 54, y0 + yy, G_[3])
    R.shell(wall, lambda c, x, y, w, h: tiles(c, x, y, w, h, S_[6], S_[2], 8))
    c, x0, y0, fy = R.c, R.x0, R.y0, R.fy
    window_on_wall(c, x0 + 150, y0 + 6, 50, 22)
    counter = box3d(110, 14, 10, W_[3], W_[1], lines=11)
    counter.rect(80, 1, 100, 10, S_[5]); counter.rect(83, 3, 97, 8, S_[2])                               # máquina de café
    for k in range(4): counter.ell(10 + k * 14, 6, 2.5, 2, WHITE)
    R.add(counter, 6, 2, 0.4)
    for k in range(4): R.add(stool(CR[3]), 12 + k * 22, 22, 0.4)
    for (tx, ty) in ((140, 34), (180, 58), (130, 70)):
        t = table_round(9, W_[4]); t.ell(9, 8, 2, 1.5, WHITE); R.add(t, tx, ty, 0.4)
    R.anims += [["steam", x0 + 92, fy + 6, 14], ["steam", x0 + 149, fy + 41, 10], ["steam", x0 + 189, fy + 65, 10]]
    return R.finish((112, -40), [L_point(112, 30, 140, 90, 1.0), L_poly([(150, -40), (200, -40), (200, 40), (150, 40)], 0.5)], pots=(100, 40, 0, 0))


# ======================================================================= Energético (loja de conveniência)
def energetico():
    R = Room("c_energetico", RW, RH, WH, cap=(S_[1], S_[2]), door=True, seed=34)

    def wall(c, x0, y0, w, h):
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, S_[5])
        r = random.Random(4)
        for sy in (6, 18):                                                     # prateleiras com latinhas
            c.rect(x0 + 4, y0 + sy + 8, x0 + 130, y0 + sy + 9, S_[2])
            for x in range(x0 + 6, x0 + 128, 4):
                col = r.choice([G_[3], CR[3], TE[3], D_[3], L_[4], PL[3]])
                c.rect(x, y0 + sy, x + 2, y0 + sy + 7, col); c.set(x, y0 + sy, WHITE)
        c.rect(x0, y0 + h - 4, x0 + w - 1, y0 + h - 1, S_[3])
    R.shell(wall, lambda c, x, y, w, h: tiles(c, x, y, w, h, S_[6], S_[5], 14))
    c, x0, y0, fy = R.c, R.x0, R.y0, R.fy
    # geladeira de bebidas com porta de vidro
    fr = Sprite(56, 40)
    fr.rect(0, 0, 55, 39, S_[2]); fr.rect(3, 3, 52, 33, D_[4])
    r = random.Random(5)
    for row in range(3):
        for k in range(12):
            fr.rect(5 + k * 4, 6 + row * 9, 6 + k * 4, 11 + row * 9, r.choice([G_[3], CR[3], TE[3], L_[4]]))
    fr.vline(27, 3, 33, S_[2])
    fr.stamp_on(c, x0 + 150, y0 + 2)
    cash = box3d(46, 18, 9, S_[5], S_[3]); cash.rect(30, 2, 42, 10, S_[1]); cash.rect(32, 3, 40, 7, TE[2])
    R.add(cash, 160, 54, 0.4)
    for k in range(3): R.add(box3d(28, 10, 14, CR[3] if k % 2 else G_[3], S_[3]), 20 + k * 40, 50, 0.6)
    R.anims += [["fridge", x0 + 153, y0 + 5, 50, 31], ["neon", x0 + 10, y0 + 2, 60, 4]]
    return R.finish((112, -30), [L_point(112, 30, 150, 90, 1.05)], pots=(100, 40, 0, 0))


# ======================================================================= Bar do Zé
def bar():
    R = Room("c_bar", RW, RH, WH, cap=(W_[0], W_[1]), door=True, seed=35)

    def wall(c, x0, y0, w, h):
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, W_[1])
        for x in range(x0, x0 + w, 8): c.vline(x, y0, y0 + h - 1, W_[0])
        r = random.Random(6)
        for sy in (8, 20):
            c.rect(x0 + 20, y0 + sy + 8, x0 + 120, y0 + sy + 9, W_[3])
            for x in range(x0 + 22, x0 + 118, 5):
                col = r.choice([L_[2], G_[2], CR[2], PA[3], TE[2]])
                c.rect(x, y0 + sy, x + 2, y0 + sy + 7, col); c.vline(x + 1, y0 + sy - 2, y0 + sy, col); c.set(x, y0 + sy + 1, WHITE)
        c.rect(x0, y0 + h - 4, x0 + w - 1, y0 + h - 1, W_[0])
    R.shell(wall, lambda c, x, y, w, h: planks_region(c, x, y, w, h, 2, 8, 351))
    c, x0, y0, fy = R.c, R.x0, R.y0, R.fy
    c.box(x0 + 150, y0 + 8, x0 + 196, y0 + 30, S_[1]); c.rect(x0 + 152, y0 + 10, x0 + 194, y0 + 28, D_[1])      # TV
    counter = box3d(130, 14, 10, W_[3], W_[1], lines=13)
    for k in range(6): counter.rect(8 + k * 20, 3, 10 + k * 20, 9, PA[4] if k % 2 else G_[3])
    R.add(counter, 8, 2, 0.4)
    for k in range(5): R.add(stool(CR[2]), 14 + k * 24, 22, 0.4)
    pool = Sprite(60, 36); pool.rect(0, 0, 59, 35, W_[2]); pool.rect(4, 4, 55, 31, L_[2]); pool.rect(6, 6, 53, 29, L_[3])
    for (bx, by, cc) in ((20, 14, CR[3]), (24, 18, G_[3]), (40, 20, WHITE), (28, 12, D_[3])): pool.ell(bx, by, 1.5, 1.5, cc)
    R.add(pool, 140, 44, 0.3)
    R.anims += [["tv", x0 + 152, y0 + 10, 43, 19], ["neon", x0 + 40, y0 + 2, 50, 4]]
    return R.finish((112, -30), [L_point(70, 20, 90, 60, 0.9), L_point(170, 50, 60, 40, 0.8)], pots=(100, 40, 0, 0), dark=True)


# ======================================================================= Biblioteca
def biblioteca():
    R = Room("c_biblioteca", RW, RH, WH, cap=(W_[1], W_[2]), door=True, seed=36)

    def wall(c, x0, y0, w, h):
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, W_[1])
        r = random.Random(7)
        for sy in range(y0 + 2, y0 + h - 6, 9):
            c.hline(x0, x0 + w - 1, sy + 8, W_[3])
            x = x0 + 2
            while x < x0 + w - 3:
                bw = r.choice([2, 2, 3]); col = r.choice([CR[2], D_[2], L_[2], G_[2], PL[2], W_[3], TE[2]])
                hh = r.randrange(5, 8)
                c.rect(x, sy + 8 - hh, x + bw - 1, sy + 7, col); c.vline(x, sy + 8 - hh, sy + 7, shift(col, 1))
                x += bw + (1 if r.random() < 0.2 else 0)
        c.rect(x0, y0 + h - 4, x0 + w - 1, y0 + h - 1, W_[0])
    R.shell(wall, lambda c, x, y, w, h: (planks_region(c, x, y, w, h, 3, 8, 361), rug(c, x + 50, y + 22, 120, 56, CR[2], CR[1], G_[3])))
    tb = box3d(80, 26, 8, W_[2], W_[1], lines=0)
    tb.rect(10, 6, 26, 16, PA[4]); tb.vline(18, 6, 16, PA[2]); tb.rect(52, 5, 60, 14, CR[2]); tb.rect(62, 4, 70, 14, D_[2])
    tb.rect(36, 2, 40, 8, S_[2]); tb.ell(38, 2, 5, 2, L_[2])
    R.add(tb, 70, 28, 0.4)
    for k in range(2):
        ch = box3d(16, 12, 8, W_[3], W_[2]); R.add(ch, 80 + k * 46, 60, 0.4)
    gl = round_top(8, [D_[1], D_[2], D_[3], L_[3]]); R.add(gl, 190, 40, 0.6)
    c, x0, fy = R.c, R.x0, R.fy
    R.anims += [["lamp", x0 + 108, fy + 30], ["dust", x0 + 30, fy - 30, 160, 60], ["page", x0 + 80, fy + 34]]
    return R.finish((108, -20), [L_point(108, 34, 70, 45, 1.1), L_point(108, 10, 160, 90, 0.4)], pots=(100, 40, 0, 0), dark=True)


# ======================================================================= Academia
def academia():
    R = Room("c_academia", RW, RH, WH, cap=(S_[1], S_[2]), door=True, seed=37)

    def wall(c, x0, y0, w, h):
        c.rect(x0, y0, x0 + w - 1, y0 + h - 1, S_[4])
        for x in range(x0 + 20, x0 + 200, 46):                                   # espelhos
            c.box(x, y0 + 4, x + 40, y0 + 30, S_[2]); c.rect(x + 1, y0 + 5, x + 39, y0 + 29, D_[4])
            for k in range(6): c.set(x + 4 + k, y0 + 24 - k, WHITE)
        c.rect(x0, y0 + h - 4, x0 + w - 1, y0 + h - 1, OL)
    R.shell(wall, lambda c, x, y, w, h: (c.rect(x, y, x + w - 1, y + h - 1, S_[1]), [c.hline(x, x + w - 1, yy, S_[2]) for yy in range(y + 4, y + h, 12)]))
    rack = Sprite(60, 16); rack.rect(0, 6, 59, 9, S_[3])
    for k in range(6): rack.ell(5 + k * 10, 6, 3, 5, [S_[1], CR[2], S_[1], D_[2], S_[1], G_[2]][k]); rack.ell(5 + k * 10, 5, 1, 2, S_[4])
    R.add(rack, 10, 0, 0.6)
    bench = box3d(14, 44, 5, CR[2], CR[1]); R.add(bench, 90, 24, 0.3)
    bar = Sprite(50, 10); bar.hline(0, 49, 5, S_[5]); bar.ell(4, 5, 3, 5, S_[1]); bar.ell(45, 5, 3, 5, S_[1]); R.add(bar, 72, 18, 0.5)
    tm = box3d(26, 48, 6, S_[2], S_[1]); tm.rect(4, 6, 21, 44, OL); tm.rect(2, 0, 23, 6, S_[3]); R.add(tm, 150, 16, 0.4)
    c, x0, fy = R.c, R.x0, R.fy
    c.vline(x0 + 205, R.y0 - 4, fy + 4, OL)
    R.anims += [["bag", x0 + 205, fy + 4], ["belt", x0 + 154, fy + 22, 18, 38]]
    return R.finish((112, -30), [L_point(112, 30, 150, 90, 1.0)], pots=(100, 40, 0, 0))


# ======================================================================= Beco Escuro
def beco():
    R = Room("c_beco", RW, RH, WH, cap=(B_[0], B_[1]), door=True, seed=38)

    def wall(c, x0, y0, w, h):
        wall_bricks(c, x0, y0, w, h, B_, base=2, bw=12, bh=5, seed=381)
        for (gx, col) in ((30, L_[4]), (70, CR[3]), (120, G_[3])):
            for k in range(14):
                c.set(x0 + gx + k, y0 + 18 + round(4 * math.sin(k / 2)), col); c.set(x0 + gx + k, y0 + 19 + round(4 * math.sin(k / 2)), col)
    R.shell(wall, lambda c, x, y, w, h: concrete(c, x, y, w, h, 2, 30, 382))
    c, x0, fy = R.c, R.x0, R.fy
    dump = box3d(46, 22, 14, L_[1], L_[0]); dump.rect(0, 0, 45, 4, L_[2]); R.add(dump, 150, 2, 0.5)
    for k in range(3): R.add(sack(14, 10, S_[1]), 140 + k * 10, 34 + (k % 2) * 4, 0.4)
    lamp = Sprite(6, 48); lamp.rect(2, 4, 3, 47, S_[2]); lamp.rect(0, 0, 5, 4, S_[3]); R.add(lamp, 20, -20, 1.0)
    for (px, py, rx) in ((60, 70, 14), (110, 50, 10)):
        c.ell(x0 + px, fy + py, rx, rx / 3, D_[1]); c.ell(x0 + px - 2, fy + py - 1, rx * 0.6, rx / 5, D_[2])
    c.ell(x0 + 100, fy + 30, 6, 3, S_[1]); c.ell(x0 + 100, fy + 30, 4, 2, OL)
    R.anims += [["streetlamp", x0 + 23, fy - 18], ["steam", x0 + 100, fy + 28, 26], ["rain", x0, R.y0, RW, RH]]
    return R.finish((23, -30), [L_point(23, 10, 70, 50, 1.1)], pots=(100, 40, 0, 0), dark=True)


# ======================================================================= Praça
def praca():
    R = Room("c_praca", RW, RH, WH, cap=(L_[1], L_[2]), door=True, seed=39)

    def view(c, x0, y0, w, h):
        for y in range(y0, y0 + 16): c.hline(x0, x0 + w - 1, y, D_[4] if y < y0 + 9 else D_[3])
        cloud(c, x0 + 30, y0 + 4, 16); cloud(c, x0 + 150, y0 + 6, 12)
        for k in range(0, w, 16):
            c.ell(x0 + k + 8, y0 + 22, 10, 9, L_[2]); c.ell(x0 + k + 6, y0 + 19, 5, 4, L_[3])
        c.rect(x0, y0 + h - 8, x0 + w - 1, y0 + h - 1, L_[3])
    R.shell(view, lambda c, x, y, w, h: (c.rect(x, y, x + w - 1, y + h - 1, L_[3]), [c.set(x + (k * 37) % w, y + (k * 23) % h, L_[4]) for k in range(400)],
                                          c.ell(x + w // 2, y + h // 2, 60, 34, PA[3]), c.ell(x + w // 2, y + h // 2, 56, 30, PA[2])))
    c, x0, fy = R.c, R.x0, R.fy
    ft = Sprite(40, 30); ft.ell(19.5, 15, 19, 13, S_[4]); ft.ell(19.5, 15, 16, 10, D_[3]); ft.ell(19.5, 13, 4, 3, S_[5]); ft.rect(18, 4, 21, 13, S_[5])
    R.add(ft, RW // 2 - 20, 30, 0.4)
    for (bx, by) in ((20, 20), (170, 20), (30, 66)):
        bn = box3d(30, 8, 6, W_[3], W_[2], lines=6); R.add(bn, bx, by, 0.4)
    from cenarios import RAMPS as _R
    R.anims += [["fountain", x0 + RW // 2, fy + 40], ["pigeon", x0 + 60, fy + 70], ["pigeon", x0 + 150, fy + 60]]
    return R.finish((-40, -80), [L_point(112, 40, 200, 140, 1.0)], pots=(100, 40, 0, 0))


PLACES = {"spa": spa, "fliperama": fliperama, "cafe": cafe, "energetico": energetico, "bar": bar,
          "biblioteca": biblioteca, "academia": academia, "beco": beco, "praca": praca}

if __name__ == "__main__":
    only = sys.argv[1:] or list(PLACES)
    mp = os.path.join(OUT, "cidade.json")
    meta = json.load(open(mp)) if os.path.exists(mp) else {}
    for k in only:
        meta["c_" + k] = PLACES[k]()
        print("ok", k)
    json.dump(meta, open(mp, "w"), indent=1)
