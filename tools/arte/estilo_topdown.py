"""TESTE DE ESTILO: interiores vistos de cima (estilo RPG de portátil), cômodo flutuando no preto,
crescendo a cada imóvel, com acabamento detalhado.

Ordem de desenho (é isso que faz as plantas "pertencerem" ao cômodo):
  1. paredes e chão
  2. cada objeto projeta a sombra da própria silhueta, a partir da fonte de luz, e depois é desenhado
     (móveis, vasos e plantas passam pelo mesmo processo)
  3. só no fim entra a iluminação (luz da janela, abajur, oclusão) sobre TUDO, inclusive as plantas

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
SPR = os.path.join(ROOT, "assets", "sprites", "v2")


# ----------------------------------------------------------------- sprites vindos de PNG
_cache = {}


def png(name):
    if name not in _cache:
        _cache[name] = Image.open(os.path.join(SPR, name)).convert("RGBA")
    return _cache[name]


def sprite_from(im):
    sp = Sprite(im.width, im.height)
    for y in range(im.height):
        for x in range(im.width):
            r, g, b, a = im.getpixel((x, y))
            if a > 0:
                sp.px[y][x] = "#%02x%02x%02x" % (r, g, b)
    return sp


def potted(pot_idx, stage_xy):
    """Vaso + planta num sprite só (base do caule na terra do vaso)."""
    sp = Sprite(32, 58)
    pot = sprite_from(png("vasos.png").crop((pot_idx * 32, 0, pot_idx * 32 + 32, 24)))
    cx, cy = stage_xy
    plant = sprite_from(png("plantas_estagios.png").crop((cx * 32, cy * 40, cx * 32 + 32, cy * 40 + 40)))
    for y in range(24):
        for x in range(32):
            if pot.px[y][x]:
                sp.px[34 + y][x] = pot.px[y][x]
    for y in range(40):
        for x in range(32):
            if plant.px[y][x]:
                sp.px[y][x] = plant.px[y][x]
    sp.has_outline = True
    return sp


# ----------------------------------------------------------------- objetos: sombra + desenho + borda de luz
def place(c, sp, x, y, light, height=1.0, outline=True, rim=True, contact=True):
    """Projeta a sombra da silhueta (oposta à luz), desenha o objeto e acende a borda virada para a luz.
    height: quanto o objeto "sobe" do chão (1 = em pé, como planta; 0.2 = chato, como cama)."""
    lx, ly = light
    ground = y + sp.h - 1
    cxo = x + sp.w / 2
    kx = max(-0.7, min(0.7, (cxo - lx) / 70.0)) * height
    ky = 0.45 * height
    marks = set()
    for sy in range(sp.h):
        for sx in range(sp.w):
            if not sp.px[sy][sx]:
                continue
            h = ground - (y + sy)
            tx = x + sx + h * kx
            ty = ground + h * ky
            marks.add((int(round(tx)), int(round(ty))))
            marks.add((int(round(tx)), int(round(ty)) + 1))
    for (tx, ty) in marks:
        col = c.get(tx, ty)
        if col and col != OL:
            c.px[ty][tx] = shift(col, -1)
    if contact:                                       # sombra de contato: a mais escura, junto à base
        bw = sp.w * 0.42
        c.tone(cxo - bw, ground - 1, cxo + bw, ground + 2, -1,
               mask=lambda xx, yy: ((xx - cxo) / bw) ** 2 + ((yy - ground - 0.5) / 2.2) ** 2 <= 1)
    sp.stamp_on(c, x, y, outline=outline and not getattr(sp, "has_outline", False))
    if rim:                                           # luz de borda do lado da fonte de luz
        dx = 1 if lx > cxo + 8 else -1 if lx < cxo - 8 else 0
        for sy in range(sp.h):
            for sx in range(sp.w):
                col = sp.px[sy][sx]
                if not col or col == OL:
                    continue
                up = sp.get(sx, sy - 1)
                side = sp.get(sx + dx, sy) if dx else col
                if (not up or up == OL) or (dx and (not side or side == OL)):
                    c.set(x + sx, y + sy, shift(col, 1))


# ----------------------------------------------------------------- cômodo
def room_shell(c, x0, y0, w, h, wall_h, wall_fn, floor_fn, door=None):
    T = 5
    c.rect(x0 - T, y0 - T, x0 + w + T - 1, y0 + h + T - 1, S_[1])
    c.rect(x0 - T, y0 - T, x0 + w + T - 1, y0 - T + 1, S_[2])
    c.rect(x0 - T, y0 - T, x0 - T + 1, y0 + h + T - 1, S_[2])
    c.rect(x0 - T - 1, y0 - T - 1, x0 + w + T, y0 - T - 1, OL); c.rect(x0 - T - 1, y0 + h + T, x0 + w + T, y0 + h + T, OL)
    c.rect(x0 - T - 1, y0 - T - 1, x0 - T - 1, y0 + h + T, OL); c.rect(x0 + w + T, y0 - T - 1, x0 + w + T, y0 + h + T, OL)
    wall_fn(c, x0, y0, w, wall_h)
    floor_fn(c, x0, y0 + wall_h, w, h - wall_h)
    c.rect(x0 - 1, y0 - 1, x0 + w, y0 - 1, OL); c.rect(x0 - 1, y0 + h, x0 + w, y0 + h, OL)
    c.rect(x0 - 1, y0 - 1, x0 - 1, y0 + h, OL); c.rect(x0 + w, y0 - 1, x0 + w, y0 + h, OL)
    if door:
        dx, dw = door
        c.rect(x0 + dx, y0 + h, x0 + dx + dw - 1, y0 + h + T, VOID)
        c.rect(x0 + dx - 1, y0 + h, x0 + dx - 1, y0 + h + T, OL); c.rect(x0 + dx + dw, y0 + h, x0 + dx + dw, y0 + h + T, OL)


def occlusion(c, x0, y0, w, h, wall_h):
    """Cantos e pé das paredes mais escuros (aplicado no fim, sobre tudo)."""
    fy = y0 + wall_h
    c.tone(x0, fy, x0 + w - 1, fy + 2, -1)
    c.tone(x0, fy + 3, x0 + w - 1, fy + 5, -1, dither=0)
    c.tone(x0, fy, x0 + 2, y0 + h - 1, -1); c.tone(x0 + 3, fy, x0 + 5, y0 + h - 1, -1, dither=1)
    c.tone(x0 + w - 3, fy, x0 + w - 1, y0 + h - 1, -1); c.tone(x0 + w - 6, fy, x0 + w - 4, y0 + h - 1, -1, dither=0)
    c.tone(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, -1)
    c.tone(x0, y0, x0 + w - 1, y0 + 1, -1)


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
            x += L


def wallpaper_region(c, x0, y0, w, h):
    c.rect(x0, y0, x0 + w - 1, y0 + h - 1, PA[2])
    for x in range(x0, x0 + w, 8):
        c.rect(x, y0, x + 2, y0 + h - 1, PA[3])
    for y in range(y0 + 4, y0 + h - 6, 7):
        for x in range(x0 + 5 + (y // 7 % 2) * 4, x0 + w, 8):
            c.set(x, y, PA[1])
    c.hline(x0, x0 + w - 1, y0 + h - 4, W_[3]); c.rect(x0, y0 + h - 3, x0 + w - 1, y0 + h - 1, W_[2]); c.hline(x0, x0 + w - 1, y0 + h - 1, W_[1])


def light_field(c, x0, y0, w, h, lights):
    """Iluminação única do cômodo: soma a intensidade de cada luz e troca a cor pelo degrau da rampa.
    Longe da luz: -1 (penumbra); perto: +1; a transição é pontilhada (nada de degradê suave)."""
    for y in range(y0, y0 + h):
        for x in range(x0, x0 + w):
            col = c.get(x, y)
            if not col or col == OL:
                continue
            I = sum(f(x, y) for f in lights)
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
            if n:
                c.px[y][x] = shift(col, n)


def point_light(cx, cy, r, ry=None, power=1.0):
    ry = ry or r * 0.7
    return lambda x, y: max(0.0, 1 - math.hypot((x - cx) / r, (y - cy) / ry)) * power


def poly_light(pts, power=1.0, soft=6):
    def inside(x, y):
        n = len(pts); c_ = False
        for i in range(n):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % n]
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c_ = not c_
        return c_
    def f(x, y):
        if inside(x, y):
            return power
        for dx in (-soft, soft):
            if inside(x + dx, y):
                return power * 0.5
        return 0.0
    return f


def light_pool(c, cx, cy, rx, ry, steps=1):
    c.tone(cx - rx, cy - ry, cx + rx, cy + ry, steps, mask=lambda x, y: ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 0.5)
    c.tone(cx - rx, cy - ry, cx + rx, cy + ry, 1, mask=lambda x, y: 0.5 < ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1, dither=0)


def to_img(c):
    im = Image.new("RGBA", (c.w, c.h), hexrgb(VOID) + (255,))
    for y in range(c.h):
        for x in range(c.w):
            if c.px[y][x]:
                im.putpixel((x, y), hexrgb(c.px[y][x]) + (255,))
    return im


def blob_sprite(col, w=12, hh=7, seed=0):
    sp = Sprite(w, hh, seed)
    for yy in range(hh):
        for xx in range(w):
            if ((xx - w / 2) / (w / 2)) ** 2 + ((yy - hh / 2) / (hh / 2)) ** 2 <= 1 + 0.3 * math.sin(xx * 1.9 + seed):
                sp.set(xx, yy, col)
    sp.line(2, 2, w - 4, hh - 2, shift(col, -1)); sp.hline(2, w - 4, 1, shift(col, 1))
    return sp


# ================================================================= QUARTINHO (pequeno)
def quartinho():
    c = Cv(FW, FH, 1)
    x0, y0, w, h, wh = 90, 34, 140, 112, 30
    room_shell(c, x0, y0, w, h, wh, wallpaper_region, lambda c, x, y, w, h: planks_region(c, x, y, w, h, 3, 6, 4), door=(58, 20))
    fy = y0 + wh
    wx, wy = x0 + 82, y0 + 5
    SUN = (wx + 14, y0 - 30)            # sol entrando pela janela (alto, atrás da parede)
    LAMP = (x0 + 44, fy + 2)
    # ---- parede: janela, cortinas, pôster, prateleira, relógio
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
    c.hline(wx - 9, wx + 36, wy - 4, S_[3]); c.hline(wx - 9, wx + 36, wy - 5, OL)
    ps = Sprite(16, 20); ps.rect(0, 0, 15, 19, PL[2]); ps.rect(2, 2, 13, 11, CR[3]); ps.ell(7, 6, 3, 3, G_[3]); ps.rect(6, 7, 8, 11, L_[2]); ps.rect(2, 13, 13, 14, "#fffbef"); ps.rect(2, 16, 9, 16, PA[3])
    ps.stamp_on(c, x0 + 52, y0 + 4); c.tone(x0 + 53, y0 + 26, x0 + 70, y0 + 26, -1)
    c.box(x0 + 116, y0 + 13, x0 + 136, y0 + 15, W_[3]); c.tone(x0 + 117, y0 + 16, x0 + 136, y0 + 17, -1)
    for i, col in enumerate((D_[2], CR[2], L_[3], G_[2], PL[2])):
        c.rect(x0 + 118 + i * 3, y0 + 6 + (i % 2), x0 + 119 + i * 3, y0 + 12, col); c.set(x0 + 118 + i * 3, y0 + 6 + (i % 2), shift(col, 1))
    c.ell(x0 + 72, y0 + 10, 4, 4, OL); c.ell(x0 + 72, y0 + 10, 3, 3, "#fffbef"); c.set(x0 + 72, y0 + 8, OL); c.set(x0 + 73, y0 + 10, CR[2])
    # ---- tapete (chato: sem sombra)
    rx0, ry0, rw, rh = x0 + 46, fy + 30, 52, 34
    c.box(rx0, ry0, rx0 + rw, ry0 + rh, CR[2])
    c.rect(rx0 + 2, ry0 + 2, rx0 + rw - 2, ry0 + rh - 2, CR[3]); c.rect(rx0 + 4, ry0 + 4, rx0 + rw - 4, ry0 + rh - 4, CR[2])
    for xx in range(rx0 + 6, rx0 + rw - 5, 4):
        for yy in range(ry0 + 6, ry0 + rh - 5, 4):
            if (xx // 4 + yy // 4) % 2 == 0:
                c.set(xx, yy, G_[3])
    for xx in range(rx0 + 1, rx0 + rw, 2):
        c.set(xx, ry0 - 1, PA[3]); c.set(xx, ry0 + rh + 1, PA[3])
    c.box(x0 + 58, y0 + h - 7, x0 + 77, y0 + h - 1, CR[1]); c.rect(x0 + 60, y0 + h - 5, x0 + 75, y0 + h - 3, CR[2])
    # ---- objetos (de trás para a frente), todos com sombra pela mesma luz
    objs = []
    bed = Sprite(32, 54)
    bed.rect(0, 0, 31, 5, W_[2]); bed.hline(0, 31, 0, W_[3])
    for xx in range(2, 30, 6):
        bed.vline(xx, 1, 4, W_[1])
    bed.rect(1, 6, 30, 50, PA[4]); bed.rect(4, 8, 27, 15, "#fffbef"); bed.hline(4, 27, 15, PA[2]); bed.hline(6, 25, 11, PA[3])
    for yy in range(18, 50):
        for xx in range(1, 31):
            wv = math.sin(xx / 3.0 + yy / 5.0) * 0.8 + math.sin(xx / 7.0 - yy / 2.4) * 0.5 + (yy - 18) / 34
            bed.set(xx, yy, D_[3] if wv > 0.9 else D_[2] if wv > -0.4 else D_[1])
    bed.poly([(18, 18), (31, 18), (31, 30)], D_[3]); bed.vline(30, 6, 50, PA[2]); bed.rect(0, 51, 31, 53, W_[1]); bed.hline(0, 31, 51, W_[2])
    objs.append((bed, x0 + 3, fy - 4, 0.18))
    ns = Sprite(14, 18); ns.rect(0, 4, 13, 14, W_[4]); ns.hline(0, 13, 4, W_[5]); ns.rect(0, 15, 13, 17, W_[2]); ns.set(6, 16, G_[3])
    ns.ell(6.5, 3, 4, 3, G_[3]); ns.ell(5.5, 2, 1, 1, G_[4]); ns.rect(10, 9, 12, 11, CR[3])
    objs.append((ns, x0 + 38, fy - 6, 0.5))
    dk = Sprite(36, 22); dk.rect(0, 6, 35, 17, W_[3]); dk.hline(0, 35, 6, W_[4]); dk.rect(0, 18, 35, 21, W_[1]); dk.hline(0, 35, 18, W_[2])
    dk.rect(3, 0, 16, 10, S_[4]); dk.hline(3, 16, 0, S_[5]); dk.rect(5, 2, 14, 7, TE[1]); dk.rect(6, 3, 10, 4, TE[3])
    dk.rect(20, 10, 30, 12, S_[3]); dk.hline(20, 30, 10, S_[5])
    objs.append((dk, x0 + 100, fy - 9, 0.35))
    ch = Sprite(12, 14); ch.ell(5.5, 7.5, 5.5, 5.5, CR[2]); ch.ell(4.5, 6.5, 3, 3, CR[3]); ch.rect(2, 0, 9, 3, CR[1])
    objs.append((ch, x0 + 110, fy + 14, 0.5))
    for (col, xx, yy, sd) in ((L_[3], x0 + 6, fy + 60, 1), (CR[2], x0 + 16, fy + 63, 2), (S_[5], x0 + 8, fy + 68, 3)):
        objs.append((blob_sprite(col, 13, 7, sd), xx, yy, 0.12))
    pz = Sprite(18, 16); pz.rect(0, 0, 17, 15, W_[4]); pz.hline(0, 17, 0, W_[5]); pz.rect(2, 2, 15, 13, W_[3]); pz.poly([(4, 4), (14, 4), (9, 12)], G_[3]); pz.set(7, 6, CR[3]); pz.set(11, 6, CR[3]); pz.set(9, 9, CR[3])
    objs.append((pz, x0 + 112, fy + 54, 0.1))
    for i, col in enumerate((CR[3], L_[4], D_[3])):
        cn = Sprite(4, 6); cn.rect(0, 0, 3, 5, col); cn.vline(0, 0, 5, shift(col, 1)); cn.hline(0, 3, 0, S_[5])
        objs.append((cn, x0 + 34 + i * 5, fy + 66 - (i % 2) * 3, 1.0))
    # vasos com planta (o mesmo processo dos móveis)
    objs.append((potted(0, (0, 1)), rx0 + 2, ry0 - 26, 1.0))
    objs.append((potted(1, (2, 1)), rx0 + 26, ry0 - 26, 1.0))
    objs.sort(key=lambda o: o[2] + o[0].h)
    for sp, xx, yy, hh in objs:
        place(c, sp, xx, yy, SUN, height=hh, outline=sp.px[0][0] is None or True)
    # ---- iluminação final, sobre tudo
    light_field(c, x0, y0, w, h, [
        poly_light([(wx - 2, y0), (wx + 30, y0), (wx + 16, fy + 52), (wx - 16, fy + 52)], 0.95),   # sol da janela
        point_light(wx + 14, fy + 18, 80, 56, 0.55),                                                # luz rebatida do sol
        point_light(LAMP[0], LAMP[1] + 4, 30, 20, 0.9),                                             # abajur
        point_light(x0 + 110, fy + 18, 18, 12, 0.5),                                                # tela do computador
    ])
    occlusion(c, x0, y0, w, h, wh)
    return to_img(c)


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
    LAMP = (x0 + 124, fy + 30)          # lâmpada no teto, no meio da garagem
    # parede: portão e painel de ferramentas
    gx = x0 + 150
    c.box(gx, y0 + 2, gx + 76, y0 + wh - 2, S_[5])
    for yy in range(y0 + 4, y0 + wh - 3, 3):
        c.hline(gx + 1, gx + 75, yy, S_[3]); c.hline(gx + 1, gx + 75, yy + 1, "#fffbef")
    c.rect(gx + 34, y0 + wh - 7, gx + 42, y0 + wh - 5, S_[2])
    c.box(x0 + 60, y0 + 4, x0 + 116, y0 + 24, W_[4])
    for xx in range(x0 + 63, x0 + 115, 4):
        for yy in range(y0 + 7, y0 + 23, 4):
            c.set(xx, yy, W_[2])
    tl = Sprite(50, 16)
    tl.rect(1, 3, 2, 15, W_[2]); tl.rect(0, 1, 5, 4, S_[3]); tl.rect(10, 2, 11, 15, S_[4]); tl.ell(10.5, 2, 2, 2, S_[4])
    tl.rect(18, 1, 25, 7, CR[3]); tl.rect(20, 8, 23, 14, OL); tl.rect(25, 3, 29, 5, S_[3])
    tl.rect(36, 1, 37, 14, G_[2]); tl.rect(41, 1, 42, 14, S_[4]); tl.rect(46, 1, 47, 14, W_[2])
    tl.stamp_on(c, x0 + 64, y0 + 6)
    c.tone(x0 + 150, fy + 90, x0 + 190, fy + 104, -1, mask=lambda x, y: ((x - x0 - 170) / 20) ** 2 + ((y - fy - 97) / 6) ** 2 <= 1)
    c.tone(x0 + 160, fy + 93, x0 + 180, fy + 101, -1, mask=lambda x, y: ((x - x0 - 170) / 10) ** 2 + ((y - fy - 97) / 3) ** 2 <= 1)
    objs = []
    bench = Sprite(70, 22); bench.rect(0, 6, 69, 17, W_[3]); bench.hline(0, 69, 6, W_[4]); bench.rect(0, 18, 69, 21, W_[1]); bench.hline(0, 69, 18, W_[2])
    for xx in range(4, 66, 9):
        bench.vline(xx, 7, 16, W_[2])
    bench.rect(50, 2, 60, 12, S_[3]); bench.hline(50, 60, 2, S_[5]); bench.rect(6, 4, 14, 12, CR[3]); bench.rect(18, 6, 22, 12, G_[3]); bench.rect(26, 9, 32, 11, S_[4])
    objs.append((bench, x0 + 52, fy - 8, 0.35))
    car = Sprite(46, 86)
    car.rect(4, 0, 41, 85, CR[3])
    car.rect(0, 10, 3, 24, OL); car.rect(42, 10, 45, 24, OL); car.rect(0, 62, 3, 76, OL); car.rect(42, 62, 45, 76, OL)
    car.rect(4, 0, 41, 4, CR[2]); car.rect(8, 1, 14, 3, G_[4]); car.rect(31, 1, 37, 3, G_[4])
    car.poly([(7, 18), (38, 18), (35, 32), (10, 32)], D_[3]); car.line(12, 20, 16, 30, D_[4]); car.line(20, 20, 24, 30, D_[4])
    car.rect(9, 33, 36, 60, CR[3]); car.rect(9, 33, 11, 60, CR[4]); car.rect(34, 33, 36, 60, CR[2])
    car.poly([(10, 61), (35, 61), (37, 72), (8, 72)], D_[3]); car.line(14, 62, 12, 70, D_[4])
    car.rect(4, 80, 41, 85, CR[2]); car.rect(7, 82, 12, 84, CR[4]); car.rect(33, 82, 38, 84, CR[4])
    car.vline(4, 5, 79, CR[4]); car.vline(41, 5, 79, CR[1]); car.set(3, 30, CR[2]); car.set(42, 30, CR[2])
    objs.append((car, x0 + 8, fy + 14, 0.22))
    for i in range(2):
        tr = Sprite(24, 24); tr.ell(11.5, 11.5, 11, 11, S_[1]); tr.ell(11.5, 11.5, 9, 9, S_[2]); tr.ell(11.5, 11.5, 4, 4, S_[0]); tr.ell(9.5, 8.5, 3, 1, S_[3])
        objs.append((tr, x0 + 194 - i * 4, fy + 58 - i * 6, 0.35))
    tb = Sprite(20, 14); tb.rect(0, 2, 19, 13, CR[2]); tb.rect(0, 2, 19, 5, CR[3]); tb.rect(7, 0, 12, 2, S_[2]); tb.rect(7, 7, 12, 9, S_[2])
    objs.append((tb, x0 + 196, fy + 2, 0.6))
    for i in range(4):
        objs.append((potted([0, 1, 2, 2][i], [(0, 4), (1, 4), (2, 4), (2, 5)][i]), x0 + 76 + i * 30, fy + 36, 1.0))
    objs.sort(key=lambda o: o[2] + o[0].h)
    for sp, xx, yy, hh in objs:
        place(c, sp, xx, yy, LAMP, height=hh)
    # iluminação final
    light_field(c, x0, y0, w, h, [point_light(LAMP[0], LAMP[1] + 30, 120, 80, 1.1)])
    occlusion(c, x0, y0, w, h, wh)
    return to_img(c)


if __name__ == "__main__":
    a, b = quartinho(), garagem()
    S, gap = 3, 12
    sheet = Image.new("RGBA", ((FW * 2 + gap) * S, FH * S), hexrgb(VOID) + (255,))
    sheet.alpha_composite(a.resize((FW * S, FH * S), Image.NEAREST), (0, 0))
    sheet.alpha_composite(b.resize((FW * S, FH * S), Image.NEAREST), ((FW + gap) * S, 0))
    out = os.path.join(ROOT, "docs", "arte", "estilo-topdown-teste.png")
    sheet.save(out)
    a.save(os.path.join(ROOT, "docs", "arte", "estilo-topdown-quartinho.png"))
    print("ok", out)
