"""Regera as folhas de sprites em assets/sprites/v2 a partir dos scripts de desenho.

    python3 tools/arte/build.py
"""
import json, os, shutil, sys, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import plants, equip
from lib import CS, sheet

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "assets", "sprites", "v2")


def compact(f):
    o = plants.C
    plants.C = lambda w, h: CS(w, h, 0.62)
    try:
        return f()
    finally:
        plants.C = o


def save(cells, cols, cw, ch, name, names, idx):
    tmp = os.path.join(tempfile.mkdtemp(), "s.png")
    sheet(cells, cols, cw, ch, tmp, scale=1)
    shutil.copy(tmp.replace(".png", "_1x.png"), os.path.join(OUT, name))
    idx[name] = {"cell": [cw, ch], "cols": cols, "frames": names}


if __name__ == "__main__":
    idx = json.load(open(os.path.join(OUT, "index.json")))
    save([f() for _, f in plants.PL], 10, 32, 40, "plantas.png", [n for n, _ in plants.PL], idx)
    save([compact(f) for _, f in plants.PL], 10, 32, 40, "plantas_compactas.png", [n for n, _ in plants.PL], idx)
    save([f() for _, f in equip.EQ], 9, 32, 32, "equipamentos.png", [n for n, _ in equip.EQ], idx)
    save([f() for _, f in equip.CONT], 3, 32, 24, "vasos.png", [n for n, _ in equip.CONT], idx)
    for n, f in equip.BIG:
        o = f()
        save([o], 1, o.w, o.h, n + ".png", [n], idx)
    json.dump(idx, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, indent=1)
    print("ok")
