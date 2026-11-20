"""O neto nos lugares da cidade: uma pose por lugar, 2 quadros cada (animação simples).

Mesmo visual dos retratos (cabelo crespo, camiseta mostarda, jeans) e mesmo jeito de pintar
(Pix: volume pela rampa, contorno só por fora).
Gera assets/sprites/v2/neto_cidade.png: 9 linhas (lugares) × 2 quadros de 28x40.
Ordem: spa, fliperama, cafe, energetico, bar, biblioteca, academia, beco, praca.
    python3 tools/arte/neto_cidade.py [prévia.png]
"""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from personagens import Pix, SK, HR, ST, LF, DN, GD, CR, PA, WHITE, OL
from cenarios import RAMPS, hexrgb
from estilo_topdown import ROOT
from PIL import Image

FW, FH = 28, 40
WD = RAMPS["wood"]; TE = RAMPS["teal"]


def curls(p, mask, seed=0):
    p.fill(mask, HR, 1, "hair")
    for (x, y) in sorted(mask):
        if (x * 3 + y * 5 + seed) % 7 == 0 and (x, y + 1) in mask and (x + 1, y) in mask:
            p.set(x, y, HR[3]); p.set(x + 1, y, HR[2]); p.set(x, y + 1, HR[2])
    for (x, y) in mask:
        if ((x, y - 1) not in mask or (x - 1, y) not in mask) and (x + y) % 2 == 0:
            p.set(x, y, HR[2])


def head_back(p, cx, cy):
    p.fill(p.m_ell(cx - 6, cy + 1, 1, 2), SK, 2, "ear"); p.fill(p.m_ell(cx + 6, cy + 1, 1, 2), SK, 1, "ear2")
    curls(p, p.m_ell(cx, cy - 1, 6, 6))


def head_front(p, cx, cy, look=0, smile=True):
    p.fill(p.m_ell(cx, cy, 5, 5), SK, 2, "face", spec=True)
    curls(p, (p.m_ell(cx, cy - 4, 7, 4) | p.m_ell(cx - 6, cy - 1, 2, 3) | p.m_ell(cx + 6, cy - 2, 2, 3)) - p.m_ell(cx, cy + 1, 4, 4))
    for ex in (cx - 2, cx + 2):
        p.set(ex + look, cy, HR[0]); p.set(ex + look, cy + 1, HR[0])
    if smile:
        p.set(cx - 1, cy + 3, SK[0]); p.set(cx, cy + 3, SK[0]); p.set(cx + 1, cy + 3, SK[0])
    else:
        p.set(cx, cy + 3, SK[0])


def torso_back(p, x0, y0, x1, y1):
    p.fill(p.m_rect(x0, y0, x1, y1), GD, 3, "tee")
    for x in range(x0, x1 + 1): p.set(x, y1, GD[1])


def torso_front(p, x0, y0, x1, y1):
    p.fill(p.m_rect(x0, y0, x1, y1), GD, 3, "tee")
    p.set(x0 + (x1 - x0) // 2 + 2, y0 + 3, LF[4]); p.set(x0 + (x1 - x0) // 2 + 3, y0 + 2, LF[5])
    for x in range(x0 + 3, x1 - 2): p.set(x, y0, GD[2])


def legs(p, cx, y0, y1):
    p.fill(p.m_rect(cx - 5, y0, cx - 1, y1), DN, 1, "legL"); p.fill(p.m_rect(cx + 1, y0, cx + 5, y1), DN, 1, "legR")
    for sx in (cx - 6, cx + 1):
        p.fill(p.m_rect(sx, y1 + 1, sx + 5, y1 + 2), ST, 6, "shoe")


# ---------------------------------------------------------------- poses
def spa(f):
    """Deitado de bruços na maca, toalha na cintura; respira."""
    p = Pix(FW, FH); cx = 14
    p.fill(p.m_ell(cx, 30, 6, 7), SK, 2, "legs")
    p.fill(p.m_rect(cx - 7, 14, cx + 7, 25 + f), SK, 2, "back", spec=True)       # costas sem camisa
    p.line(cx, 16, cx, 23, SK[1])                                                # coluna
    p.fill(p.m_rect(cx - 8, 13, cx - 6, 21), SK, 2, "armL"); p.fill(p.m_rect(cx + 6, 13, cx + 8, 21), SK, 1, "armR")
    p.fill(p.m_rect(cx - 7, 24, cx + 7, 30), PA, 4, "towel")                     # toalha
    for x in range(cx - 7, cx + 8, 3): p.set(x, 27, PA[2])
    p.fill(p.m_rect(cx - 4, 35, cx - 1, 38), SK, 2, "footL"); p.fill(p.m_rect(cx + 1, 35, cx + 4, 38), SK, 1, "footR")
    curls(p, p.m_ell(cx, 7, 6, 5))
    p.seam("towel", PA[2]); p.outline()
    return p


def fliperama(f):
    """De costas jogando pinball; os ombros mexem quando aperta os botões."""
    p = Pix(FW, FH); cx = 14
    legs(p, cx, 27, 35)
    torso_back(p, cx - 7, 14, cx + 7, 26)
    d = 1 if f else 0
    p.fill(p.m_rect(cx - 10, 14, cx - 8, 18 - d), GD, 3, "slL"); p.fill(p.m_rect(cx + 8, 14, cx + 10, 18 - (1 - d)), GD, 2, "slR")
    p.fill(p.m_rect(cx - 10, 19 - d, cx - 8, 21 - d), SK, 2, "hL"); p.fill(p.m_rect(cx + 8, 19 - (1 - d), cx + 10, 21 - (1 - d)), SK, 1, "hR")
    head_back(p, cx, 8)
    p.seam("tee", GD[1]); p.outline()
    return p


def seated_back(f, cup=WHITE, drink=False):
    """Sentado de costas no banquinho; levanta o copo/xícara."""
    p = Pix(FW, FH); cx = 14
    torso_back(p, cx - 7, 16, cx + 7, 28)
    p.fill(p.m_rect(cx - 9, 16, cx - 7, 24), GD, 3, "slL")
    if f:                                                                        # braço levantado (bebendo)
        p.fill(p.m_rect(cx + 7, 10, cx + 9, 18), SK, 1, "armR"); p.fill(p.m_rect(cx + 6, 8, cx + 10, 11), cup, 0, "cup") if False else None
        p.fill(p.m_rect(cx + 7, 7, cx + 10, 10), [cup, cup, cup], 1, "cup")
    else:
        p.fill(p.m_rect(cx + 7, 16, cx + 9, 24), GD, 2, "slR")
    head_back(p, cx, 10 + (1 if f else 0))
    p.seam("tee", GD[1]); p.outline()
    return p


def cafe(f): return seated_back(f, cup=WHITE)
def bar(f): return seated_back(f, cup=GD[4])


def energetico(f):
    """De costas na geladeira, segurando a porta e escolhendo uma latinha."""
    p = Pix(FW, FH); cx = 14
    legs(p, cx, 27, 35)
    torso_back(p, cx - 7, 14, cx + 7, 26)
    p.fill(p.m_rect(cx - 10, 14, cx - 8, 22), GD, 3, "slL")
    p.fill(p.m_rect(cx + 8, 12 - f * 2, cx + 10, 18), SK, 1, "armR")
    p.fill(p.m_rect(cx + 8, 9 - f * 2, cx + 11, 12 - f * 2), [CR[2], CR[3], CR[4]], 1, "can")
    head_back(p, cx, 8)
    p.seam("tee", GD[1]); p.outline()
    return p


def biblioteca(f):
    """Sentado de costas à mesa, cabeça baixa lendo; vira a página."""
    p = Pix(FW, FH); cx = 14
    torso_back(p, cx - 7, 15, cx + 7, 27)
    p.fill(p.m_rect(cx - 9, 13, cx - 7, 20), GD, 3, "slL"); p.fill(p.m_rect(cx + 7, 13 - f, cx + 9, 20), GD, 2, "slR")
    head_back(p, cx, 10)
    p.seam("tee", GD[1]); p.outline()
    return p


def academia(f):
    """De lado socando o saco de pancada (soco para a direita)."""
    p = Pix(FW, FH); cx = 11
    p.fill(p.m_rect(cx - 4, 27, cx - 1, 35), DN, 1, "legL"); p.fill(p.m_rect(cx + 1, 27, cx + 4, 35), DN, 2, "legR")
    p.fill(p.m_rect(cx - 5, 36, cx - 1, 37), ST, 6, "s1"); p.fill(p.m_rect(cx + 1, 36, cx + 6, 37), ST, 6, "s2")
    p.fill(p.m_rect(cx - 5, 14, cx + 4, 26), GD, 3, "tee")
    if f:
        p.fill(p.m_rect(cx + 4, 16, cx + 15, 18), SK, 2, "arm"); p.fill(p.m_ell(cx + 16, 17, 2, 2), CR, 2, "glove")
    else:
        p.fill(p.m_rect(cx + 3, 16, cx + 7, 18), SK, 2, "arm"); p.fill(p.m_ell(cx + 8, 16, 2, 2), CR, 2, "glove")
    p.fill(p.m_ell(cx, 8, 5, 5), SK, 2, "face", spec=True)
    curls(p, p.m_ell(cx - 1, 5, 6, 4) | p.m_ell(cx - 4, 8, 2, 3))
    p.set(cx + 3, 8, HR[0]); p.set(cx + 4, 11, SK[0])
    p.seam("tee", GD[1]); p.outline()
    return p


def beco(f):
    """De frente, encostado no muro, olhando de um lado para o outro."""
    p = Pix(FW, FH); cx = 14
    legs(p, cx, 27, 35)
    torso_front(p, cx - 7, 15, cx + 7, 26)
    p.fill(p.m_rect(cx - 9, 15, cx - 7, 24), GD, 3, "slL"); p.fill(p.m_rect(cx + 7, 15, cx + 9, 24), GD, 2, "slR")
    p.fill(p.m_rect(cx - 9, 25, cx - 7, 26), SK, 2, "hL"); p.fill(p.m_rect(cx + 7, 25, cx + 9, 26), SK, 1, "hR")
    head_front(p, cx, 9, look=(-1 if f else 1), smile=False)
    p.seam("tee", GD[1]); p.outline()
    return p


def praca(f):
    """Sentado no banco de frente, jogando migalha para os pombos."""
    p = Pix(FW, FH); cx = 14
    p.fill(p.m_rect(cx - 6, 25, cx + 6, 29), DN, 1, "lap")
    p.fill(p.m_rect(cx - 5, 30, cx - 2, 34), DN, 1, "shinL"); p.fill(p.m_rect(cx + 2, 30, cx + 5, 34), DN, 2, "shinR")
    for sx in (cx - 6, cx + 2): p.fill(p.m_rect(sx, 35, sx + 4, 36), ST, 6, "shoe")
    torso_front(p, cx - 7, 14, cx + 7, 25)
    p.fill(p.m_rect(cx - 9, 14, cx - 7, 22), GD, 3, "slL")
    if f:
        p.fill(p.m_rect(cx + 7, 18, cx + 13, 20), SK, 2, "arm")
        for (x, y) in ((cx + 15, 22), (cx + 17, 25), (cx + 14, 26)): p.set(x, y, PA[3])
    else:
        p.fill(p.m_rect(cx + 7, 14, cx + 9, 22), GD, 2, "slR")
    head_front(p, cx, 8)
    p.seam("tee", GD[1]); p.outline()
    return p


ORDER = ["spa", "fliperama", "cafe", "energetico", "bar", "biblioteca", "academia", "beco", "praca"]
POSES = {"spa": spa, "fliperama": fliperama, "cafe": cafe, "energetico": energetico, "bar": bar,
         "biblioteca": biblioteca, "academia": academia, "beco": beco, "praca": praca}

if __name__ == "__main__":
    out = Image.new("RGBA", (FW * 2, FH * len(ORDER)), (0, 0, 0, 0))
    for r, k in enumerate(ORDER):
        for f in range(2):
            POSES[k](f).to_img(out, f * FW, r * FH)
    path = os.path.join(ROOT, "assets", "sprites", "v2", "neto_cidade.png")
    out.save(path)
    if len(sys.argv) > 1:
        bg = Image.new("RGBA", out.size, hexrgb(PA[3]) + (255,)); bg.alpha_composite(out)
        sheet = Image.new("RGBA", (FW * 2 * 3 + 20, FH * 3 + 8), hexrgb(PA[3]) + (255,))
        for r in range(len(ORDER)):
            sheet.paste(bg.crop((0, r * FH, FW * 2, (r + 1) * FH)), ((r % 3) * (FW * 2 + 10), (r // 3) * (FH + 4)))
        sheet.resize((sheet.width * 5, sheet.height * 5), Image.NEAREST).save(sys.argv[1])
    print("ok", path)
