"""Palmeira vista de cima em 3/4: tronco curvo com anéis e copa de folhas serrilhadas que caem."""
import math
from cenarios import Sprite, RAMPS, shift

W_ = RAMPS["wood"]; L_ = RAMPS["leaf"]


def _frond(sp, cx, cy, ang, length, droop, width, light, dark, mid):
    """Uma folha: nervura curva e lâminas dos dois lados, mais largas no meio e serrilhadas."""
    dx, dy = math.cos(ang), math.sin(ang)
    steps = int(length * 3)
    pts = []
    for k in range(steps + 1):
        t = k / steps
        x = cx + dx * length * t
        y = cy + dy * length * t * 0.62 + droop * t * t - droop * 0.75 * t   # sobe um pouco e cai na ponta
        pts.append((x, y, t))
    for i in range(len(pts) - 1):
        x, y, t = pts[i]
        x2, y2, _ = pts[i + 1]
        tx, ty = x2 - x, y2 - y
        n = math.hypot(tx, ty) or 1
        nx, ny = -ty / n, tx / n                              # normal
        if ny > 0:
            nx, ny = -nx, -ny                                 # lado "a" sempre o de cima (aceso)
        s = t * length
        tooth = 0.55 + 0.45 * ((s * 0.55) % 1)                # serrilhado: folíolos apontando para a ponta
        w = width * math.sin(math.pi * min(1, t * 1.15)) ** 0.7 * tooth
        if t < 0.08:
            w = 0
        for side, col in ((1, light), (-1, dark)):
            for k in range(int(w * 2) + 1):
                d = k / 2
                sp.set(x + nx * d * side, y + ny * d * side, col)
    for (x, y, t) in pts:
        if t < 0.9:
            sp.set(x, y, mid)


def palm(w=96, h=92):
    sp = Sprite(w, h)
    base = (w * 0.38, h - 3)
    top = (w * 0.52, 30)
    # tronco: curva quadrática, anéis alternados, lado esquerdo aceso
    ctrl = (w * 0.30, h * 0.55)
    prev = None
    n = 120
    for k in range(n + 1):
        t = k / n
        x = (1 - t) ** 2 * base[0] + 2 * (1 - t) * t * ctrl[0] + t * t * top[0]
        y = (1 - t) ** 2 * base[1] + 2 * (1 - t) * t * ctrl[1] + t * t * top[1]
        r = 3.6 - 1.2 * t
        ring = int((1 - t) * 40) % 3 == 0
        for dx in range(-4, 5):
            if abs(dx) > r:
                continue
            col = W_[3] if dx < -r * 0.3 else W_[2] if dx < r * 0.45 else W_[1]
            if ring:
                col = shift(col, -1)
            if dx <= -r + 1 and not ring:
                col = W_[4]
            sp.set(x + dx, y, col)
    # pé do tronco alargado
    sp.ell(base[0], base[1], 5, 2, W_[2]); sp.ell(base[0] - 1, base[1] - 1, 3, 1, W_[3])
    cx, cy = top[0], top[1] - 2
    # folhas de trás (mais escuras), depois as da frente
    back = [(-2.7, 36, 16), (-2.0, 30, 12), (-1.15, 30, 12), (-0.45, 36, 16)]
    front = [(-3.1, 42, 24), (0.05, 42, 24), (2.45, 34, 20), (0.7, 34, 20), (1.6, 22, 12)]
    for a, ln, dr in back:
        _frond(sp, cx, cy, a, ln, dr, 4.2, L_[2], L_[1], L_[1])
    for a, ln, dr in front:
        _frond(sp, cx, cy, a, ln, dr, 4.8, L_[4], L_[2], L_[1])
    # cocos
    for (ox, oy) in ((-3, 2), (2, 3), (-1, 5)):
        sp.ell(cx + ox, cy + oy, 2.2, 2.2, W_[1]); sp.set(cx + ox - 1, cy + oy - 1, W_[3])
    sp.ell(cx, cy - 1, 2, 1.5, L_[5])
    return sp


if __name__ == "__main__":
    import sys
    from cenarios import Cv
    from estilo_topdown import to_img as img
    c = Cv(110, 100); c.rect(0, 0, 109, 99, RAMPS["wood"][5])
    palm().stamp_on(c, 6, 4)
    img(c).resize((440, 400), 0).save(sys.argv[1])
