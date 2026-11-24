"""Render the social card (og-card.png) from the coordinates in data.js.

    python tools/render_card.py og-card.png

Needs Pillow. The typeface is fetched from Google Fonts on first run and
cached next to this script. Everything it draws is real: the structure is the
Boltz-2 prediction stored in data.js under D.spec.
"""
import json, math, os, re, sys, urllib.request
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

# data.js is "window.D={...};" - take the object out of it
_src = open(os.path.join(ROOT, 'data.js'), encoding='utf-8').read()
SPEC = json.loads(_src[_src.index('window.D=') + 9:_src.rstrip().rstrip(';').rindex('}') + 1])['spec']

BRIC = os.path.join(HERE, 'BricolageGrotesque.ttf')
if not os.path.exists(BRIC):
    urllib.request.urlretrieve(
        'https://github.com/google/fonts/raw/main/ofl/bricolagegrotesque/'
        'BricolageGrotesque%5Bopsz,wdth,wght%5D.ttf', BRIC)

def _mono(size):
    for p in ('C:/Windows/Fonts/consola.ttf', '/System/Library/Fonts/Menlo.ttc',
              '/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf'):
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


from PIL import Image, ImageDraw, ImageFilter, ImageFont


BG = (6, 7, 11)
PL = [(90, (77, 139, 255)), (70, (69, 214, 232)), (50, (255, 210, 63)), (0, (255, 125, 69))]
ELEM = {'C': (200, 206, 221), 'N': (77, 139, 255), 'O': (255, 90, 82), 'S': (255, 210, 63)}


def plddt(b):
    for cut, col in PL:
        if b >= cut:
            return col
    return PL[-1][1]


def lerp(a, b, t):
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(3))


# ---------- geometry ----------------------------------------------------
trace = SPEC['trace']
R = max(math.hypot(*r['p']) for r in trace)

SUB = 8
runs, cur = [], [trace[0]]
for i in range(1, len(trace)):
    a, b = trace[i - 1]['p'], trace[i]['p']
    if math.dist(a, b) > 5:
        runs.append(cur); cur = []
    cur.append(trace[i])
runs.append(cur)

curve = []   # (point, plddt, is_run_start)
for run in runs:
    if len(run) < 2:
        continue
    start = len(curve)
    for i in range(len(run) - 1):
        p0 = run[max(0, i - 1)]['p']; p1 = run[i]['p']
        p2 = run[i + 1]['p']; p3 = run[min(len(run) - 1, i + 2)]['p']
        for s in range(SUB):
            t = s / SUB; t2 = t * t; t3 = t2 * t
            q = [0.5 * ((2 * p1[d]) + (-p0[d] + p2[d]) * t
                        + (2 * p0[d] - 5 * p1[d] + 4 * p2[d] - p3[d]) * t2
                        + (-p0[d] + 3 * p1[d] - 3 * p2[d] + p3[d]) * t3) for d in range(3)]
            curve.append([q, run[i]['b'] + (run[i + 1]['b'] - run[i]['b']) * t, False])
    curve.append([run[-1]['p'], run[-1]['b'], False])
    curve[start][2] = True


def projector(yaw, pitch, cx, cy, sc):
    cw, sw = math.cos(yaw), math.sin(yaw)
    cp, sp = math.cos(pitch), math.sin(pitch)

    def f(p):
        x = p[0] * cw + p[2] * sw
        z = -p[0] * sw + p[2] * cw
        return (cx + x * sc, cy + (p[1] * cp - z * sp) * sc, p[1] * sp + z * cp)
    return f


# ---------- drawing -----------------------------------------------------
def draw_protein(img, yaw, pitch, cx, cy, sc, tube=1.0, sheen=True, glow=True):
    proj = projector(yaw, pitch, cx, cy, sc)
    P = [proj(c[0]) for c in curve]
    zs = [p[2] for p in P]
    zmin, zmax = min(zs), max(zs)
    span = (zmax - zmin) or 1.0

    if glow:
        g = Image.new('RGB', img.size, BG)
        gd = ImageDraw.Draw(g)
        for i in range(len(P) - 1):
            if curve[i + 1][2]:
                continue
            gd.line([P[i][:2], P[i + 1][:2]], fill=(38, 80, 172), width=int(tube * 18))
        g = g.filter(ImageFilter.GaussianBlur(tube * 13))
        img.paste(Image.blend(img, g, 0.72), (0, 0))

    d = ImageDraw.Draw(img)
    CH = 7
    chunks, run = [], []
    for i in range(len(P)):
        if curve[i][2] and run:
            chunks.append(run); run = []
        run.append(i)
        if len(run) >= CH + 1 and i < len(P) - 1 and not curve[i + 1][2]:
            chunks.append(run); run = [i]
    if len(run) > 1:
        chunks.append(run)
    chunks.sort(key=lambda ch: sum(P[i][2] for i in ch) / len(ch))

    for ch in chunks:
        z = sum(P[i][2] for i in ch) / len(ch)
        t = (z - zmin) / span
        pts = [P[i][:2] for i in ch]
        w = tube * (7.4 + 4.6 * t)
        col = plddt(sum(curve[i][1] for i in ch) / len(ch))
        d.line(pts, fill=BG, width=int(w + tube * 5.2), joint='curve')
        d.line(pts, fill=lerp(BG, col, 0.13 + 0.87 * t), width=int(w), joint='curve')
        if sheen:
            off = tube * 1.5
            hi = [(x - off, y - off) for x, y in pts]
            d.line(hi, fill=lerp(col, (255, 255, 255), 0.30 + 0.22 * t),
                   width=max(1, int(w * 0.26)), joint='curve')
    return proj


def draw_ligand(img, proj, tube=1.0):
    d = ImageDraw.Draw(img)
    lp = [proj(a['p']) for a in SPEC['lig']['atoms']]
    glow = Image.new('RGB', img.size, BG)
    gd = ImageDraw.Draw(glow)
    for i, j, _ in SPEC['lig']['bonds']:
        gd.line([lp[i][:2], lp[j][:2]], fill=(120, 160, 255), width=int(tube * 13))
    glow = glow.filter(ImageFilter.GaussianBlur(tube * 9))
    img.paste(Image.blend(img, glow, 0.5), (0, 0))

    d = ImageDraw.Draw(img)
    for i, j, _ in SPEC['lig']['bonds']:
        d.line([lp[i][:2], lp[j][:2]], fill=(20, 24, 34), width=int(tube * 8.4))
    for i, j, _ in SPEC['lig']['bonds']:
        d.line([lp[i][:2], lp[j][:2]], fill=(236, 240, 250), width=int(tube * 5.4))
    for a, p in zip(SPEC['lig']['atoms'], lp):
        col = ELEM.get(a['e'], (200, 206, 221))
        r = tube * 6.4
        d.ellipse([p[0] - r - tube * 1.6, p[1] - r - tube * 1.6,
                   p[0] + r + tube * 1.6, p[1] + r + tube * 1.6], fill=(16, 19, 28))
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=col)
        hr = r * 0.42
        d.ellipse([p[0] - hr - r * 0.26, p[1] - hr - r * 0.26,
                   p[0] + hr - r * 0.26, p[1] + hr - r * 0.26],
                  fill=lerp(col, (255, 255, 255), 0.55))




import math, os, sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont


W, H = 1200, 630
SS = 3                      # supersample factor
YAW, PITCH = 0.45, 0.40     # chosen from the contact sheets

BG = BG
INK = (238, 240, 247)
DIM = (139, 148, 171)
CYAN = (69, 214, 232)



def bric(size, weight=800):
    f = ImageFont.truetype(BRIC, size)
    try:
        f.set_variation_by_axes([min(96, max(12, size / SS)), weight, 100])
    except Exception:
        pass
    return f


# tube thickness that looked right on the contact sheet, expressed per unit scale
TUBE_PER_SC = 0.62 / ((560 * 0.44) / R)


def fit(yaw, pitch, box_w, box_h):
    """scale so the projected structure fills the box"""
    pj = projector(yaw, pitch, 0, 0, 1)
    pts = [pj(c[0]) for c in curve] + [pj(a['p']) for a in SPEC['lig']['atoms']]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    return min(box_w / (max(xs) - min(xs)), box_h / (max(ys) - min(ys))), \
        (max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2


def build():
    w, h = W * SS, H * SS
    img = Image.new('RGB', (w, h), BG)
    d = ImageDraw.Draw(img)

    # faint graph paper, fading out to the edges
    grid = Image.new('RGB', (w, h), BG)
    gd = ImageDraw.Draw(grid)
    step = 24 * SS
    for x in range(0, w, step):
        gd.line([(x, 0), (x, h)], fill=(14, 19, 34), width=1)
    for y in range(0, h, step):
        gd.line([(0, y), (w, y)], fill=(14, 19, 34), width=1)
    for x in range(0, w, step * 5):
        gd.line([(x, 0), (x, h)], fill=(20, 28, 50), width=2)
    for y in range(0, h, step * 5):
        gd.line([(0, y), (w, y)], fill=(20, 28, 50), width=2)
    img.paste(grid, (0, 0))

    # structure, right of centre
    cx, cy = int(w * 0.665), int(h * 0.50)
    sc, ox, oy = fit(YAW, PITCH, w * 0.60, h * 0.90)
    tube = sc * TUBE_PER_SC

    # pool of blue light behind it
    glow = Image.new('RGB', (w, h), BG)
    gdr = ImageDraw.Draw(glow)
    rad = int(h * 0.46)
    gdr.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], fill=(44, 76, 158))
    glow = glow.filter(ImageFilter.GaussianBlur(h * 0.10))
    img.paste(Image.blend(img, glow, 0.95), (0, 0))

    pj = projector(YAW, PITCH, cx - ox * sc, cy - oy * sc, sc)

    # catalytic side chains, quiet, behind the ligand
    SC = {'ASP232': (255, 90, 82), 'HIS48': (69, 214, 232),
          'VAL174': (255, 210, 63), 'TRP46': (160, 123, 255)}
    draw_protein(img, YAW, PITCH, cx - ox * sc, cy - oy * sc, sc,
                    tube=tube, sheen=True, glow=True)
    d = ImageDraw.Draw(img)
    for res in SPEC['side']:
        col = SC.get(res['n'], DIM)
        pts = [pj(a['p']) for a in res['atoms']]
        for i, j in res['bonds']:
            d.line([pts[i][:2], pts[j][:2]], fill=col, width=max(2, int(tube * 2.4)))
    draw_ligand(img, pj, tube=tube * 1.15)

    # ---- type -----------------------------------------------------------
    d = ImageDraw.Draw(img)
    x0 = 74 * SS
    mono_s = _mono(int(13.5 * SS))
    mono_b = _mono(int(12 * SS))
    name = bric(int(63 * SS), 800)

    d.text((x0, 196 * SS), 'DE NOVO ENZYME POCKET', font=mono_b, fill=CYAN)
    d.text((x0, 228 * SS), 'MAXIMILIAN', font=name, fill=INK)
    d.text((x0, 284 * SS), 'ALEXANDROV', font=name, fill=INK)
    d.line([(x0, 364 * SS), (x0 + 300 * SS, 364 * SS)], fill=(48, 62, 94), width=max(1, SS))
    d.text((x0, 382 * SS), 'Protein design  ·  ML for biology', font=mono_s, fill=DIM)

    # provenance, bottom left
    d.text((x0, 536 * SS), '01.c04.mutate.d8ca9d  ·  260 aa', font=mono_b, fill=(104, 114, 136))
    d.text((x0, 556 * SS), 'score 0.8658  ·  iPTM 0.922  ·  Boltz-2', font=mono_b, fill=(104, 114, 136))

    # vignette
    vig = Image.new('L', (w, h), 0)
    ImageDraw.Draw(vig).ellipse([-int(w * 0.18), -int(h * 0.30),
                                 int(w * 1.18), int(h * 1.30)], fill=255)
    vig = vig.filter(ImageFilter.GaussianBlur(h * 0.10))
    img = Image.composite(img, Image.new('RGB', (w, h), (2, 3, 6)), vig)

    out = img.resize((W, H), Image.LANCZOS)
    return out




if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, 'og-card.png')
    card = build()
    card.save(out, optimize=True)
    print('wrote', out, card.size, os.path.getsize(out), 'bytes')
