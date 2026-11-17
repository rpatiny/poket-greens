"""Gera os tiles PROVISÓRIOS da cidade (assets/sprites/cidade.png) e os NPCs por troca de cor.

Usa a mesma paleta do projeto Pixelwright "El Cartel – Quarto".
Quando a arte definitiva da cidade for desenhada no Pixelwright, este arquivo pode ser apagado.

    python3 tools/gen_city_tiles.py
"""
import random
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "sprites"

PAL = {
    "a": "#1d1922",  # outline
    "b": "#443a50", "c": "#5f6579", "d": "#93a0b0", "e": "#d2dae3",  # metal 0-3
    "f": "#5a1f2e", "g": "#8f2f3d", "h": "#c4483f",  # cloth 0-2
    "j": "#8a5a24", "G": "#d39b3a", "k": "#f3d27a",  # gold 0-2
    "l": "#3e2a22", "m": "#6b4532",  # leather 0-1
    "n": "#3b3447",  # ground
    "o": "#f4f1e8",  # eye / branco
    "p": "#8c5a4a", "q": "#c98a6b", "r": "#ecc0a0",  # skin 0-2
    "s": "#2f5233", "t": "#4f8a4b", "u": "#93c46a",  # leaf 0-2
    "v": "#2c3e6b", "w": "#4f74b8", "x": "#9cc3ea",  # sky 0-2
    "y": "#6e4126", "z": "#9a6438", "A": "#c38a54", "B": "#dcaa72",  # wood 0-3
    "C": "#4a3b5c", "D": "#bba57e", "E": "#dccaa3", "F": "#efe3c8",  # wall 0-3
    "K": "#6a2e1e", "H": "#a24c2c", "I": "#cd7044", "J": "#e89a64",  # clay 0-3
}
RGBA = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) + (255,) for k, v in PAL.items()}

T = 16
COLS = 8


def blank(fill):
    return [[fill] * T for _ in range(T)]


def stamp(tile, art, ox=0, oy=0):
    for y, row in enumerate(art):
        for x, ch in enumerate(row):
            if ch != ".":
                tile[oy + y][ox + x] = ch
    return tile


def grass(seed, flowers=False):
    rnd = random.Random(seed)
    t = blank("t")
    for _ in range(10):
        x, y = rnd.randrange(T), rnd.randrange(1, T)
        t[y][x] = "u"
        t[y - 1][x] = "s" if rnd.random() < 0.5 else "u"
    for _ in range(6):
        t[rnd.randrange(T)][rnd.randrange(T)] = "s"
    if flowers:
        for cx, cy, col in ((3, 4, "o"), (11, 3, "k"), (7, 10, "h"), (13, 12, "o"), (2, 13, "k")):
            t[cy][cx] = col
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if 0 <= cx + dx < T and 0 <= cy + dy < T:
                    t[cy + dy][cx + dx] = "u" if col != "o" else "e"
            t[cy][cx] = col
    return t


def sidewalk():
    t = blank("e")
    for y in range(T):
        for x in range(T):
            if y % 8 == 7 or x % 8 == 7:
                t[y][x] = "d"
            elif y % 8 == 0 or x % 8 == 0:
                t[y][x] = "o" if (x + y) % 3 else "e"
    return t


def road(seed, line=None):
    rnd = random.Random(seed)
    t = blank("b")
    for _ in range(14):
        t[rnd.randrange(T)][rnd.randrange(T)] = rnd.choice("nc")
    if line == "h":
        for x in range(2, 13):
            t[7][x] = t[8][x] = "k"
    if line == "v":
        for y in range(2, 13):
            t[y][7] = t[y][8] = "k"
    return t


def bricks(base="I", mortar="H"):
    t = blank(base)
    for y in range(T):
        for x in range(T):
            off = 4 if (y // 4) % 2 else 0
            if y % 4 == 3 or (x + off) % 8 == 7:
                t[y][x] = mortar
            elif y % 4 == 0 and (x + off) % 8 < 3:
                t[y][x] = "J"
    return t


def siding():
    t = blank("E")
    for y in range(T):
        for x in range(T):
            if y % 4 == 3:
                t[y][x] = "D"
            elif y % 4 == 0:
                t[y][x] = "F"
    return t


WINDOW = [
    "aaaaaaaaaa",
    "ayyyyyyyya",
    "ayxxewxxya",
    "ayxewwxxya",
    "ayxxxxxxya",
    "ayyyyyyyya",
    "aywwwwwwya",
    "aywwvvwwya",
    "ayyyyyyyya",
    "aBBBBBBBBa",
]

DOOR = [
    "aaaaaaaaaaaa",
    "ayyyyyyyyyya",
    "ayzAAAAAAzya",
    "ayzAzzzzAzya",
    "ayzAzzzzAzya",
    "ayzAAAAAAzya",
    "ayzzzzzzzzya",
    "ayzAAAAAAzya",
    "ayzAzzzzAkya",
    "ayzAzzzzAGya",
    "ayzAzzzzAzya",
    "ayzAAAAAAzya",
    "ayzzzzzzzzya",
    "aaaaaaaaaaaa",
]

GLASS_DOOR = [
    "aaaaaaaaaaaa",
    "acccccccccca",
    "acxxeexxxxca",
    "acxexxxxxwca",
    "acxxxxxxwwca",
    "acxxxxxwwwca",
    "acdddddddddca"[:12],
    "acxxxxwwwwca",
    "acxxxwwwvvca",
    "acxxwwwvvvca",
    "acxwwwvvvvca",
    "acwwwvvvvvca",
    "acccccccccca",
    "aaaaaaaaaaaa",
]


def roof(main, dark, light, edge=False):
    t = blank(main)
    for y in range(T):
        for x in range(T):
            off = 2 if (y // 4) % 2 else 0
            if y % 4 == 3:
                t[y][x] = dark
            elif (x + off) % 4 == 0 and y % 4 != 0:
                t[y][x] = dark
            elif y % 4 == 0 and (x + off) % 4 == 1:
                t[y][x] = light
    if edge:
        for x in range(T):
            t[12][x] = dark
            t[13][x] = "a"
            t[14][x] = "a"
            t[15][x] = "C"
    return t


TREE_TOP = [
    "................",
    ".....aaaaaa.....",
    "...aauuuttsaa...",
    "..auuuuttttssa..",
    ".auuuttttttttsa.",
    ".auutttttttttsa.",
    "auuttttttsttttsa",
    "auttttttssttttsa",
    "atttsttttttttssa",
    "attssttttttttssa",
    "atttttttttttsssa",
    "atttttttttttssssa"[:16],
    ".atttttssttsssa.",
    ".attttssssssssa.",
    "..atssssssssss..",
    "..aatsssssssaa..",
]

TREE_BOTTOM = [
    "...aassssssaa...",
    ".....aaaaaa.....",
    "......aymya.....",
    "......aymya.....",
    "......aymya.....",
    "......aymya.....",
    ".....aymmmya....",
    "....aaaaaaaaa...",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
]

BUSH = [
    "................",
    "................",
    "................",
    ".....aaaaaa.....",
    "...aauuuttsaa...",
    "..auuutttttssa..",
    ".auuttttttttssa.",
    ".auttttsttttssa.",
    "atttttssttttsssa",
    "attsttttttttsssa",
    "atttttttttttsssa",
    ".atttttsssssssa.",
    ".aassssssssssaa.",
    "...aaaaaaaaaa...",
    "................",
    "................",
]

FENCE = [
    "................",
    "................",
    "..aa........aa..",
    ".aBAa......aBAa.",
    ".aAza......aAza.",
    "aaAzaaaaaaaaAzaa",
    "aBBBBBBBBBBBBBBa",
    "azzzzzzzzzzzzzza",
    "aaAzaaaaaaaaAzaa",
    ".aAza......aAza.",
    "aaAzaaaaaaaaAzaa",
    "aBBBBBBBBBBBBBBa",
    "azzzzzzzzzzzzzza",
    "aaAzaaaaaaaaAzaa",
    ".aAza......aAza.",
    ".aaaa......aaaa.",
]

SIGN = [
    "................",
    "..aaaaaaaaaaaa..",
    ".aBBBBBBBBBBBBa.",
    ".aBAAAAAAAAAABa.",
    ".aBAyyyAyyyAABa.",
    ".aBAAAAAAAAAABa.",
    ".aBAyyAyyyyAABa.",
    ".aBAAAAAAAAAABa.",
    ".azzzzzzzzzzzza.",
    "..aaaaaAzaaaaa..",
    "......aAza......",
    "......aAza......",
    "......aAza......",
    ".....aaAzaa.....",
    "....asaaaasa....",
    "................",
]

AWNING = [
    "aaaaaaaaaaaaaaaa",
    "hhooohhhooohhhoo",
    "hhooohhhooohhhoo",
    "ghhoogghhoogghho",
    "ghhoogghhoogghho",
    "ghhoogghhoogghho",
    "gghhogghhhogghhh",
    "agghaagghaagghaa",
    ".aaa..aaa..aaa..",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
]

MAILBOX = [
    "................",
    "................",
    "................",
    "....aaaaaaa.....",
    "...ahhhhhhha....",
    "..ahhhhhhhhha...",
    "..ahaaaaaaaha...",
    "..ahhhhhhhhha...",
    "..agggggggga....",
    "...aaaaaaaa.....",
    "......aca.......",
    "......aca.......",
    "......aca.......",
    ".....aacaa......",
    "....asaaaas.....",
    "................",
]


def with_bg(bg, art):
    return stamp(bg, art)


def build_city():
    tiles = {}
    tiles[0] = grass(1)
    tiles[1] = grass(2, flowers=True)
    tiles[2] = with_bg(grass(3), BUSH)
    tiles[3] = sidewalk()
    tiles[4] = road(4)
    tiles[5] = road(5, "h")
    tiles[6] = road(6, "v")
    tiles[7] = with_bg(grass(7), MAILBOX)
    tiles[8] = with_bg(grass(8), TREE_TOP)
    tiles[9] = bricks()
    tiles[10] = stamp(bricks(), WINDOW, 3, 3)
    tiles[11] = roof("g", "f", "h")
    tiles[12] = roof("g", "f", "h", edge=True)
    tiles[13] = stamp(bricks(), DOOR, 2, 2)
    tiles[14] = with_bg(bricks(), AWNING)
    tiles[15] = with_bg(grass(15), FENCE)
    tiles[16] = with_bg(grass(16), TREE_BOTTOM)
    tiles[17] = with_bg(grass(17), SIGN)
    tiles[18] = siding()
    tiles[19] = stamp(siding(), WINDOW, 3, 3)
    tiles[20] = stamp(siding(), DOOR, 2, 2)
    tiles[21] = roof("w", "v", "x")
    tiles[22] = roof("w", "v", "x", edge=True)
    tiles[23] = stamp(bricks(), GLASS_DOOR, 2, 2)
    # 24: portão de garagem (metal ondulado)
    gate = blank("d")
    for y in range(T):
        for x in range(T):
            if y % 3 == 2:
                gate[y][x] = "c"
            elif y % 3 == 0:
                gate[y][x] = "e"
        gate[y][0] = gate[y][15] = "a"
    tiles[24] = gate
    tiles[25] = with_bg(sidewalk(), SIGN)

    rows = (max(tiles) // COLS) + 1
    img = Image.new("RGBA", (COLS * T, rows * T), (0, 0, 0, 0))
    for idx, tile in tiles.items():
        ox, oy = (idx % COLS) * T, (idx // COLS) * T
        for y, row in enumerate(tile):
            assert len(row) == T, (idx, y, len(row))
            for x, ch in enumerate(row):
                img.putpixel((ox + x, oy + y), RGBA[ch])
    img.save(OUT / "cidade.png")
    return img


def recolor(src, mapping, name):
    """Troca de cores do avatar para gerar NPCs (o mesmo sistema da personalização)."""
    img = Image.open(OUT / src).convert("RGBA")
    px = img.load()
    m = {RGBA[a]: RGBA[b] for a, b in mapping.items()}
    for y in range(img.height):
        for x in range(img.width):
            if px[x, y] in m:
                px[x, y] = m[px[x, y]]
    img.save(OUT / name)


if __name__ == "__main__":
    build_city()
    # Avó: cabelo grisalho, vestido roxo/vinho
    recolor("avatar.png", {"m": "d", "l": "c", "t": "g", "u": "h", "s": "f", "w": "C", "v": "a", "b": "y"}, "npc_avo.png")
    # Zé: cabelo preto, camisa amarela, calça marrom, pele mais escura
    recolor("avatar.png", {"m": "a", "l": "a", "t": "G", "u": "k", "s": "j", "w": "z", "v": "y",
                           "r": "q", "q": "p"}, "npc_ze.png")
    # Vendedor do Growshop: camisa vermelha, cabelo ruivo
    recolor("avatar.png", {"m": "I", "l": "H", "t": "h", "u": "J", "s": "g", "w": "c", "v": "b"}, "npc_vendedor.png")
    print("ok")
