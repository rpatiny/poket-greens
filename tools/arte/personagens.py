"""Personagens da história: Vó Dita e o neto (jogador), em pixel art detalhada.

Mesmo padrão dos cenários: cada material com 3-4 tons da sua rampa, luz vindo de cima à esquerda,
transição pontilhada, contorno escuro só por fora e linhas internas no tom mais escuro do próprio material.

Gera assets/sprites/v2/personagens.png:
  linha 0 (corpo, 32x48): 0 Vó parada · 1 Vó falando (mão com a sementinha) · 2 neto parado · 3 neto pensando
  linha 1 (retrato, 48x48, para a caixa de diálogo): 0 Vó · 1 Vó falando · 2 neto · 3 neto pensando
    python3 tools/arte/personagens.py [prévia.png]
"""
import math, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from cenarios import RAMPS, OL, hexrgb
from estilo_topdown import ROOT
from PIL import Image

SK = RAMPS["skin"]; HR = RAMPS["hair"]; ST = RAMPS["stone"]; PL = RAMPS["plum"]; CR = RAMPS["crimson"]
LF = RAMPS["leaf"]; DN = RAMPS["denim"]; PA = RAMPS["paper"]; GD = RAMPS["gold"]; WD = RAMPS["wood"]
WHITE = "#fffbef"
BW, BH = 32, 48      # corpo
PW, PH = 48, 48      # retrato


class Pix:
    """Tela com 'peças': cada peça é uma máscara pintada com volume a partir da sua rampa."""
    def __init__(s, w, h):
        s.w, s.h = w, h
        s.px = [[None] * w for _ in range(h)]
        s.part = [[None] * w for _ in range(h)]

    def inside(s, x, y):
        return 0 <= x < s.w and 0 <= y < s.h

    def set(s, x, y, c, part=None):
        x, y = int(round(x)), int(round(y))
        if s.inside(x, y):
            s.px[y][x] = c
            if part is not None:
                s.part[y][x] = part

    def get(s, x, y):
        return s.px[y][x] if s.inside(x, y) else None

    # ---------- máscaras
    @staticmethod
    def m_ell(cx, cy, rx, ry):
        return {(x, y) for y in range(int(cy - ry - 1), int(cy + ry + 2)) for x in range(int(cx - rx - 1), int(cx + rx + 2))
                if ((x - cx) / (rx + 0.5)) ** 2 + ((y - cy) / (ry + 0.5)) ** 2 <= 1}

    @staticmethod
    def m_poly(pts):
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        out = set()
        for y in range(int(min(ys)), int(max(ys)) + 1):
            for x in range(int(min(xs)), int(max(xs)) + 1):
                inside = False
                j = len(pts) - 1
                for i in range(len(pts)):
                    xi, yi = pts[i]; xj, yj = pts[j]
                    if (yi > y + 0.5) != (yj > y + 0.5) and x + 0.5 < (xj - xi) * (y + 0.5 - yi) / (yj - yi) + xi:
                        inside = not inside
                    j = i
                if inside:
                    out.add((x, y))
        return out

    @staticmethod
    def m_rect(x0, y0, x1, y1):
        return {(x, y) for y in range(y0, y1 + 1) for x in range(x0, x1 + 1)}

    def fill(s, mask, ramp, base, part, light=(-1, -1), spec=False):
        """Pinta com volume: borda virada para a luz +1, borda oposta -1, faixa pontilhada antes da sombra."""
        lx, ly = light
        for (x, y) in mask:
            a = (x + lx, y + ly) in mask and (x, y + ly) in mask and (x + lx, y) in mask
            b = (x - lx, y - ly) in mask and (x - lx, y) in mask and (x, y - ly) in mask
            b2 = (x - 2 * lx, y - 2 * ly) in mask
            k = base
            if not a:
                k = base + 1
            elif not b:
                k = base - 1
            elif not b2 and (x + y) % 2 == 0:
                k = base - 1
            if spec and not a and (x - 2 * lx, y - 2 * ly) in mask and (x + y) % 3 == 0:
                k = base + 2
            s.set(x, y, ramp[max(0, min(len(ramp) - 1, k))], part)

    def seam(s, part, ramp_dark):
        """Linha interna: pixels da peça encostados embaixo/à direita de outra peça ficam no tom escuro."""
        for y in range(s.h):
            for x in range(s.w):
                if s.part[y][x] != part:
                    continue
                for dx, dy in ((0, -1), (-1, 0)):
                    q = (x + dx, y + dy)
                    if s.inside(*q) and s.part[q[1]][q[0]] not in (None, part) and s.px[q[1]][q[0]]:
                        s.px[y][x] = ramp_dark
                        break

    def line(s, x0, y0, x1, y1, c):
        n = int(max(abs(x1 - x0), abs(y1 - y0))) + 1
        for i in range(n):
            t = i / max(1, n - 1)
            s.set(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, c)

    def outline(s):
        """Contorno escuro só na silhueta."""
        add = []
        for y in range(s.h):
            for x in range(s.w):
                if s.px[y][x]:
                    continue
                if any(s.inside(x + dx, y + dy) and s.px[y + dy][x + dx] and s.px[y + dy][x + dx] != OL
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    add.append((x, y))
        for x, y in add:
            s.px[y][x] = OL

    def to_img(s, im, ox, oy):
        for y in range(s.h):
            for x in range(s.w):
                if s.px[y][x]:
                    im.putpixel((ox + x, oy + y), hexrgb(s.px[y][x]) + (255,))


# ======================================================================= corpo: Vó Dita
def vo_body(talk=False):
    p = Pix(BW, BH)
    cx = 16
    # pernas (meia-calça) e sapatos
    p.fill(p.m_rect(cx - 5, 39, cx - 2, 43), SK, 2, "leg"); p.fill(p.m_rect(cx + 2, 39, cx + 5, 43), SK, 2, "leg")
    for sx in (cx - 6, cx + 1):
        p.fill(p.m_rect(sx, 44, sx + 5, 46), HR, 1, "shoe"); p.set(sx + 1, 44, HR[3])
    # saia florida
    skirt = p.m_poly([(cx - 8, 31), (cx + 8, 31), (cx + 10, 40), (cx - 10, 40)])
    p.fill(skirt, CR, 2, "skirt")
    for (x, y, c) in ((cx - 6, 33, CR[4]), (cx - 2, 36, PA[4]), (cx + 3, 33, CR[4]), (cx + 7, 37, PA[4]), (cx - 8, 38, CR[4]),
                      (cx + 1, 39, CR[4]), (cx - 4, 39, PA[4]), (cx + 6, 34, PA[4])):
        p.set(x, y, c); p.set(x + 1, y, CR[1]); p.set(x, y - 1, LF[3])
    for x in range(cx - 10, cx + 11):
        if (x, 40) in skirt: p.set(x, 40, CR[1])
    # casaquinho roxo (aberto na frente), blusa com gola de renda
    card = p.m_poly([(cx - 8, 21), (cx + 8, 21), (cx + 9, 32), (cx - 9, 32)])
    p.fill(card, PL, 2, "card")
    blouse = p.m_poly([(cx - 3, 21), (cx + 3, 21), (cx + 2, 31), (cx - 2, 31)])
    p.fill(blouse, ST, 6, "blouse")
    for x in range(cx - 3, cx + 4, 2): p.set(x, 22, WHITE)
    for y in (25, 28): p.set(cx, y, GD[3]); p.set(cx, y + 1, GD[1])
    p.set(cx - 5, 24, GD[4]); p.set(cx - 5, 25, CR[3])                                 # broche
    for y in range(22, 32): p.set(cx - 4, y, PL[1]); p.set(cx + 4, y, PL[1])           # abertura do casaco
    for x in range(cx - 9, cx + 10):
        if (x, 31) in card: p.set(x, 31, PL[0] if x % 2 else PL[1])                    # barra canelada
    # braços
    p.fill(p.m_poly([(cx - 9, 22), (cx - 6, 22), (cx - 7, 31), (cx - 11, 31)]), PL, 2, "armL")
    p.fill(p.m_rect(cx - 11, 32, cx - 8, 34), SK, 3, "handL")
    if talk:
        p.fill(p.m_poly([(cx + 6, 22), (cx + 9, 22), (cx + 12, 17), (cx + 14, 18), (cx + 10, 25)]), PL, 2, "armR")
        p.fill(p.m_ell(cx + 13, 15, 2, 2), SK, 3, "handR")
        p.fill(p.m_rect(cx + 12, 9, cx + 16, 14), PA, 3, "packet")                       # pacotinho de semente
        p.set(cx + 14, 11, LF[4]); p.set(cx + 13, 12, LF[3]); p.set(cx + 15, 12, LF[3]); p.set(cx + 14, 10, LF[5])
    else:
        p.fill(p.m_poly([(cx + 6, 22), (cx + 9, 22), (cx + 11, 31), (cx + 7, 31)]), PL, 2, "armR")
        p.fill(p.m_rect(cx + 8, 32, cx + 11, 34), SK, 3, "handR")
    # pescoço e cabeça
    p.fill(p.m_rect(cx - 2, 19, cx + 2, 21), SK, 2, "neck")
    face = p.m_ell(cx, 13, 7, 7)
    p.fill(face, SK, 3, "face", spec=True)
    # cabelo grisalho: coque com grampo, ondas
    p.fill(p.m_ell(cx, 3, 4, 3), ST, 5, "bun", spec=True)
    p.set(cx + 3, 2, GD[3]); p.set(cx + 4, 1, GD[4])
    hair = p.m_ell(cx, 9, 8, 5) | p.m_rect(cx - 8, 9, cx - 6, 16) | p.m_rect(cx + 6, 9, cx + 8, 15)
    hair -= p.m_ell(cx, 15, 6, 5)
    p.fill(hair, ST, 5, "hair", spec=True)
    for (x0, y0, x1, y1) in ((cx - 5, 7, cx - 2, 9), (cx + 1, 6, cx + 4, 8), (cx - 7, 11, cx - 7, 14), (cx + 7, 11, cx + 7, 13)):
        p.line(x0, y0, x1, y1, ST[4])
    # rosto: óculos redondos, olhos, rugas, bochechas, boca, brincos
    for ex in (cx - 3, cx + 3):
        for (x, y) in ((ex - 2, 13), (ex + 2, 13), (ex - 1, 12), (ex, 12), (ex + 1, 12), (ex - 1, 15), (ex, 15), (ex + 1, 15), (ex - 2, 14), (ex + 2, 14)):
            p.set(x, y, GD[1])
        for (x, y) in ((ex - 1, 13), (ex, 13), (ex + 1, 13), (ex - 1, 14), (ex + 1, 14)): p.set(x, y, ST[6])
        p.set(ex, 14, HR[0]); p.set(ex - 1, 13, WHITE)
        p.set(ex + (3 if ex > cx else -3), 13, SK[1])                                  # pé de galinha
    p.set(cx, 13, GD[1])
    p.set(cx, 16, SK[2]); p.set(cx + 1, 16, SK[2])                                       # nariz
    p.set(cx - 5, 16, CR[4]); p.set(cx + 5, 16, CR[4]); p.set(cx - 4, 17, CR[4]); p.set(cx + 4, 17, CR[4])
    if talk:
        p.set(cx - 1, 18, CR[1]); p.set(cx, 18, CR[1]); p.set(cx + 1, 18, CR[1]); p.set(cx, 19, CR[3])
    else:
        p.set(cx - 2, 17, SK[1]); p.set(cx - 1, 18, SK[1]); p.set(cx, 18, SK[1]); p.set(cx + 1, 18, SK[1]); p.set(cx + 2, 17, SK[1])
    p.set(cx - 8, 16, ST[7]); p.set(cx + 8, 16, ST[7])                                   # brincos de pérola
    p.seam("card", PL[1]); p.seam("skirt", CR[1]); p.seam("neck", SK[1]); p.seam("armL", PL[1]); p.seam("armR", PL[1])
    p.outline()
    return p


# ======================================================================= corpo: neto
def neto_body(think=False):
    p = Pix(BW, BH)
    cx = 16
    # tênis e jeans
    for sx in (cx - 7, cx + 1):
        p.fill(p.m_rect(sx, 43, sx + 6, 46), ST, 6, "shoe")
        p.set(sx + 1, 46, CR[3]); p.set(sx + 2, 46, CR[3]); p.set(sx + 3, 44, ST[4]); p.set(sx + 4, 44, ST[4])
    jeans = p.m_rect(cx - 6, 33, cx - 1, 42) | p.m_rect(cx + 1, 33, cx + 6, 42) | p.m_rect(cx - 6, 32, cx + 6, 34)
    p.fill(jeans, DN, 2, "jeans")
    for (x, y) in ((cx - 4, 37), (cx - 3, 38), (cx + 3, 36), (cx + 4, 37), (cx - 5, 41), (cx + 5, 40)): p.set(x, y, DN[1])
    p.set(cx, 34, DN[0]); p.set(cx, 35, DN[0])
    # moletom verde com capuz, cordões e bolso canguru
    hood = p.m_poly([(cx - 9, 21), (cx + 9, 21), (cx + 9, 33), (cx - 9, 33)])
    p.fill(hood, LF, 3, "hoodie")
    p.fill(p.m_ell(cx, 21, 6, 2), LF, 2, "hood")
    for y in range(22, 27): p.set(cx - 2, y, ST[6]); p.set(cx + 2, y, ST[6])
    p.set(cx - 2, 27, ST[4]); p.set(cx + 2, 27, ST[4])
    p.fill(p.m_poly([(cx - 5, 28), (cx + 5, 28), (cx + 6, 32), (cx - 6, 32)]), LF, 2, "pocket")
    for x in range(cx - 9, cx + 10): p.set(x, 33, LF[1] if x % 2 else LF[2])           # barra canelada
    p.set(cx + 5, 24, LF[5]); p.set(cx + 6, 23, LF[5]); p.set(cx + 6, 24, LF[4])         # folhinha estampada
    # braços
    p.fill(p.m_poly([(cx - 9, 22), (cx - 7, 22), (cx - 8, 32), (cx - 12, 32)]), LF, 3, "armL")
    p.fill(p.m_rect(cx - 12, 33, cx - 9, 35), SK, 3, "handL")
    if think:
        p.fill(p.m_poly([(cx + 7, 22), (cx + 10, 22), (cx + 8, 27), (cx + 4, 21), (cx + 6, 20)]), LF, 3, "armR")
        p.fill(p.m_ell(cx + 4, 19, 2, 2), SK, 3, "handR")
    else:
        p.fill(p.m_poly([(cx + 7, 22), (cx + 9, 22), (cx + 12, 32), (cx + 8, 32)]), LF, 3, "armR")
        p.fill(p.m_rect(cx + 9, 33, cx + 12, 35), SK, 3, "handR")
    # pescoço, cabeça
    p.fill(p.m_rect(cx - 2, 19, cx + 2, 21), SK, 2, "neck")
    p.fill(p.m_ell(cx, 13, 7, 7), SK, 3, "face", spec=True)
    # cabelo castanho bagunçado saindo do boné
    hair = (p.m_ell(cx, 9, 8, 3) | p.m_rect(cx - 8, 9, cx - 7, 15) | p.m_rect(cx + 7, 9, cx + 8, 14)) - p.m_ell(cx, 15, 6, 4)
    p.fill(hair, HR, 2, "hair")
    for x in range(cx - 6, cx + 6, 2): p.set(x, 11, HR[1]); p.set(x + 1, 10, HR[3])            # franja em mechas
    # boné verde virado para trás: copa, regulador na testa, aba atrás aparecendo em cima
    p.fill(p.m_rect(cx - 9, 3, cx + 9, 5) & p.m_ell(cx, 4, 9, 3), LF, 2, "brim")
    p.fill(p.m_ell(cx, 7, 8, 4), LF, 3, "cap", spec=True)
    p.set(cx, 4, LF[5]); p.set(cx - 1, 5, LF[5]); p.set(cx + 1, 5, LF[5])
    for x in range(cx - 2, cx + 3): p.set(x, 10, LF[1])
    p.set(cx - 1, 9, ST[6]); p.set(cx + 1, 9, ST[6])
    # olhos, sobrancelhas, nariz, boca
    for ex in (cx - 3, cx + 3):
        for (x, y) in ((ex - 1, 13), (ex, 13), (ex - 1, 14), (ex, 14), (ex - 1, 15), (ex, 15)): p.set(x, y, HR[0])
        p.set(ex - 1, 13, WHITE); p.set(ex, 15, DN[1])
        if think:
            p.set(ex - 2, 11 if ex < cx else 10, HR[1]); p.set(ex - 1, 11 if ex < cx else 10, HR[1]); p.set(ex, 11, HR[1])
        else:
            p.set(ex - 1, 11, HR[1]); p.set(ex, 11, HR[1])
    p.set(cx, 16, SK[2]); p.set(cx - 5, 16, CR[4]); p.set(cx + 5, 16, CR[4])
    if think:
        p.set(cx - 1, 18, SK[1]); p.set(cx, 18, SK[1]); p.set(cx + 1, 17, SK[1])
    else:
        p.set(cx - 2, 17, SK[1]); p.set(cx - 1, 18, CR[2]); p.set(cx, 18, CR[2]); p.set(cx + 1, 18, CR[2]); p.set(cx + 2, 17, SK[1])
    p.seam("hoodie", LF[1]); p.seam("pocket", LF[1]); p.seam("jeans", DN[1]); p.seam("neck", SK[1]); p.seam("armL", LF[1]); p.seam("armR", LF[1])
    p.seam("face", SK[2])
    p.outline()
    return p


# ======================================================================= retratos (caixa de diálogo)
def vo_portrait(talk=False):
    p = Pix(PW, PH)
    cx = 24
    # ombros: casaquinho, gola de renda
    p.fill(p.m_poly([(4, 47), (8, 38), (40, 38), (44, 47)]), PL, 2, "card")
    p.fill(p.m_poly([(17, 38), (31, 38), (28, 47), (20, 47)]), ST, 6, "blouse")
    for x in range(17, 32, 2): p.set(x, 39, WHITE); p.set(x + 1, 40, ST[5])
    p.set(24, 43, GD[3]); p.set(24, 44, GD[1]); p.set(13, 42, GD[4]); p.set(13, 43, CR[3]); p.set(12, 43, CR[4])
    p.fill(p.m_rect(20, 33, 28, 38), SK, 2, "neck")
    # rosto
    face = p.m_ell(cx, 23, 13, 13)
    p.fill(face, SK, 3, "face", spec=True)
    # coque, cabelo com ondas
    p.fill(p.m_ell(cx, 6, 7, 5), ST, 5, "bun", spec=True)
    for (x0, y0, x1, y1) in ((cx - 4, 4, cx + 1, 3), (cx - 5, 7, cx + 3, 6)): p.line(x0, y0, x1, y1, ST[4])
    p.set(cx + 6, 3, GD[3]); p.set(cx + 7, 2, GD[4]); p.set(cx + 8, 1, GD[4])
    hair = p.m_ell(cx, 16, 15, 8) | p.m_rect(cx - 15, 16, cx - 11, 30) | p.m_rect(cx + 11, 16, cx + 15, 28)
    hair -= p.m_ell(cx, 26, 11, 10)
    p.fill(hair, ST, 5, "hair", spec=True)
    for (x0, y0, x1, y1) in ((cx - 10, 11, cx - 3, 14), (cx - 2, 10, cx + 6, 12), (cx + 7, 12, cx + 12, 16), (cx - 14, 18, cx - 13, 26),
                             (cx + 13, 18, cx + 13, 24), (cx - 7, 14, cx - 1, 16)):
        p.line(x0, y0, x1, y1, ST[4])
    # óculos redondos
    for ex in (cx - 6, cx + 6):
        lens = p.m_ell(ex, 24, 4, 3)
        ring = p.m_ell(ex, 24, 5, 4) - lens
        for (x, y) in ring: p.set(x, y, GD[1])
        for (x, y) in lens: p.set(x, y, ST[6] if (x + y) % 5 else WHITE)
        # olho atrás da lente
        p.set(ex - 1, 24, HR[0]); p.set(ex, 24, HR[0]); p.set(ex - 1, 25, HR[0]); p.set(ex, 25, HR[0]); p.set(ex - 1, 24, HR[1])
        p.set(ex - 2, 22, SK[1]); p.set(ex - 1, 22, SK[1]); p.set(ex, 22, SK[1]); p.set(ex + 1, 22, SK[1])     # pálpebra
        for k in range(3): p.set(ex + (6 + k if ex > cx else -6 - k), 24 + k - 1, SK[1])                   # pés de galinha
        p.set(ex - 2, 23, WHITE)
    p.line(cx - 1, 23, cx + 1, 23, GD[1])
    p.line(cx - 2, 19, cx - 9, 19, ST[4]); p.line(cx + 2, 19, cx + 9, 19, ST[4])                            # sobrancelhas
    # nariz, bochechas, boca, rugas
    p.set(cx, 27, SK[2]); p.set(cx + 1, 28, SK[2]); p.set(cx - 1, 29, SK[1]); p.set(cx + 2, 29, SK[1])
    for bx in (cx - 9, cx + 9):
        for (x, y) in ((bx - 1, 29), (bx, 29), (bx + 1, 29), (bx, 30)): p.set(x, y, CR[4])
    if talk:
        mouth = p.m_ell(cx, 32, 3, 2)
        for (x, y) in mouth: p.set(x, y, CR[1])
        p.set(cx - 1, 33, CR[3]); p.set(cx, 33, CR[3]); p.set(cx + 1, 33, CR[3]); p.line(cx - 2, 31, cx + 2, 31, ST[7])
    else:
        p.line(cx - 4, 31, cx - 2, 32, SK[1]); p.line(cx - 2, 32, cx + 2, 32, SK[1]); p.line(cx + 2, 32, cx + 4, 31, SK[1])
    p.line(cx - 7, 30, cx - 6, 32, SK[2]); p.line(cx + 7, 30, cx + 6, 32, SK[2])
    p.set(cx - 13, 30, ST[7]); p.set(cx - 13, 31, ST[6]); p.set(cx + 13, 30, ST[7]); p.set(cx + 13, 31, ST[6])
    p.seam("card", PL[1]); p.seam("neck", SK[1])
    p.outline()
    return p


def neto_portrait(think=False):
    p = Pix(PW, PH)
    cx = 24
    # ombros: moletom, capuz, cordões
    p.fill(p.m_poly([(3, 47), (8, 38), (40, 38), (45, 47)]), LF, 3, "hoodie")
    p.fill(p.m_ell(cx, 38, 12, 3), LF, 2, "hood")
    for y in range(40, 47): p.set(cx - 4, y, ST[6]); p.set(cx + 4, y, ST[6])
    p.set(cx - 4, 47, ST[4]); p.set(cx + 4, 47, ST[4])
    p.set(36, 42, LF[5]); p.set(37, 41, LF[5]); p.set(37, 42, LF[4]); p.set(36, 43, LF[4])
    p.fill(p.m_rect(20, 33, 28, 37), SK, 2, "neck")
    p.fill(p.m_ell(cx, 23, 13, 13), SK, 3, "face", spec=True)
    # cabelo castanho saindo do boné
    hair = p.m_ell(cx, 17, 15, 7) | p.m_rect(cx - 15, 17, cx - 12, 28) | p.m_rect(cx + 12, 17, cx + 15, 26)
    hair -= p.m_ell(cx, 26, 11, 9)
    p.fill(hair, HR, 2, "hair")
    for x in range(cx - 13, cx + 13, 3):
        p.line(x, 17, x + 1, 21, HR[3]); p.set(x + 2, 21, HR[1])
    # boné virado para trás
    p.fill(p.m_ell(cx, 5, 15, 3), LF, 2, "brim")
    p.fill(p.m_ell(cx, 12, 14, 7) - p.m_rect(0, 17, 47, 47), LF, 3, "cap", spec=True)
    for (x, y) in ((cx, 7), (cx - 1, 8), (cx + 1, 8), (cx, 9)): p.set(x, y, LF[5])
    p.line(cx - 4, 16, cx + 4, 16, LF[1])
    p.set(cx - 2, 15, ST[6]); p.set(cx + 2, 15, ST[6]); p.set(cx, 15, ST[5])
    # olhos grandes com brilho, sobrancelhas
    for ex in (cx - 6, cx + 6):
        eye = p.m_ell(ex, 25, 2, 3)
        for (x, y) in eye: p.set(x, y, HR[0])
        p.set(ex - 1, 24, WHITE); p.set(ex, 24, WHITE); p.set(ex + 1, 27, DN[2]); p.set(ex, 27, DN[1])
        if think:
            p.line(ex - 3, 20 if ex < cx else 19, ex + 3, 20 if ex < cx else 21, HR[1])
        else:
            p.line(ex - 3, 21, ex + 2, 20, HR[1])
    # nariz, bochechas, boca
    p.set(cx, 28, SK[2]); p.set(cx + 1, 29, SK[2])
    for bx in (cx - 9, cx + 9):
        for (x, y) in ((bx - 1, 30), (bx, 30), (bx + 1, 30)): p.set(x, y, CR[4])
    if think:
        p.line(cx - 2, 32, cx + 2, 32, SK[1]); p.set(cx + 3, 31, SK[1])
        p.fill(p.m_ell(cx + 11, 34, 3, 3), SK, 3, "hand"); p.line(cx + 9, 32, cx + 13, 32, SK[2])       # mão no queixo
    else:
        p.line(cx - 3, 31, cx - 2, 32, SK[1]); p.line(cx - 1, 33, cx + 1, 33, CR[2]); p.line(cx + 2, 32, cx + 3, 31, SK[1])
        p.set(cx - 1, 32, CR[2]); p.set(cx, 32, CR[2]); p.set(cx + 1, 32, CR[2])
    p.seam("hoodie", LF[1]); p.seam("neck", SK[1])
    p.outline()
    return p


if __name__ == "__main__":
    out = Image.new("RGBA", (BW * 4, BH + PH), (0, 0, 0, 0))
    for i, f in enumerate((lambda: vo_body(), lambda: vo_body(True), lambda: neto_body(), lambda: neto_body(True))):
        f().to_img(out, i * BW, 0)
    for i, f in enumerate((lambda: vo_portrait(), lambda: vo_portrait(True), lambda: neto_portrait(), lambda: neto_portrait(True))):
        f().to_img(out, i * PW if i * PW + PW <= out.width else 0, BH) if False else None
    # retratos numa faixa própria (4 x 48 = 192 de largura)
    wide = Image.new("RGBA", (max(BW * 4, PW * 4), BH + PH), (0, 0, 0, 0))
    wide.paste(out.crop((0, 0, BW * 4, BH)), (0, 0))
    for i, f in enumerate((lambda: vo_portrait(), lambda: vo_portrait(True), lambda: neto_portrait(), lambda: neto_portrait(True))):
        f().to_img(wide, i * PW, BH)
    path = os.path.join(ROOT, "assets", "sprites", "v2", "personagens.png")
    wide.save(path)
    if len(sys.argv) > 1:
        bg = Image.new("RGBA", wide.size, hexrgb(RAMPS["paper"][3]) + (255,))
        bg.alpha_composite(wide)
        bg.resize((wide.width * 5, wide.height * 5), Image.NEAREST).save(sys.argv[1])
    print("ok", path, wide.size)
