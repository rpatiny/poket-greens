"""Gera plantas_estagios.png: 6 estágios de crescimento para cada semente.

Linha 0: estágios genéricos (semente na terra, broto, muda).
Linhas 1..18: para cada semente, jovem (55%), crescida (78%) e adulta (100%).
Célula 32x40, base do caule em (16, 39).
"""
import os, sys, shutil, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import plants
from lib import C, CS, sheet

def scaled(f, k):
    if k >= 1:
        return f()
    o = plants.C
    plants.C = lambda w, h: CS(w, h, k)
    try:
        return f()
    finally:
        plants.C = o

def semente():
    c = C(32, 40)
    # montinho de terra com a semente aparecendo
    c.stamp(10, 35, [
        "....aaaa....",
        "..aaEDDEaa..",
        ".aEDD32DDBa.",
        "aEDDDDDDDDBa",
        ".aaaaaaaaaa.",
    ])
    return c

cells = [semente(), plants.broto(), plants.muda()]
for name, f in plants.PL[2:]:
    cells += [scaled(f, 0.55), scaled(f, 0.78), f()]

if __name__ == "__main__":
    out = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "v2", "plantas_estagios.png")
    tmp = os.path.join(tempfile.mkdtemp(), "e.png")
    sheet(cells, 3, 32, 40, tmp, scale=1)
    shutil.copy(tmp.replace(".png", "_1x.png"), out)
    prev = os.path.join(os.path.dirname(__file__), "estagios_preview.png")
    sheet(cells[:3 + 3 * 6], 3, 32, 40, prev, scale=4)
    print("ok", out)
