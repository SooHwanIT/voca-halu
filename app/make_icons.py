"""포카보카 안드로이드 아이콘·스플래시·알림 아이콘을 public/icon.svg 모양대로 그린다."""
import os, math
from PIL import Image, ImageDraw, ImageFilter
RES = r'D:\voca-app\android\app\src\main\res'
S = 4  # 크게 그린 뒤 줄인다(계단 현상 방지)

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
def hexc(h): h = h.lstrip('#'); return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def background(n):
    """대각선 보라 그라디언트 + 아래쪽 주황 빛 (512 기준 좌표를 n으로 맞춘다)"""
    im = Image.new('RGB', (n, n))
    px = im.load()
    c0, c1, c2, gl = hexc('3a2f4d'), hexc('1c1826'), hexc('15131b'), hexc('ff6a2e')
    for y in range(n):
        for x in range(n):
            t = (x + y) / (2 * (n - 1))
            c = lerp(c0, c1, t / .6) if t < .6 else lerp(c1, c2, (t - .6) / .4)
            d = math.hypot(x / n - .5, y / n - .95) / .7
            a = max(0, 1 - d) * .55
            px[x, y] = lerp(c, gl, a)
    return im

def card_layer(n, scale=1.0, cx=None, cy=None, color=(244, 239, 248, 255), dot=(255, 106, 46, 255), hole=False):
    """기울어진 카드 + 가운데 주황 점. 512 좌표계에서 카드 156x210 rx22, 점 r34"""
    big = n * S
    lay = Image.new('RGBA', (big, big), (0, 0, 0, 0))
    k = big / 512 * scale
    cx = big / 2 if cx is None else cx * S
    cy = big / 2 if cy is None else cy * S
    w, h, r = 156 * k, 210 * k, 22 * k
    card = Image.new('RGBA', (int(w) + 4, int(h) + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([2, 2, 2 + w, 2 + h], radius=r, fill=color)
    rr = 34 * k
    ccx, ccy = 2 + w / 2, 2 + (257 - 152) * k
    if hole:
        d.ellipse([ccx - rr, ccy - rr, ccx + rr, ccy + rr], fill=(0, 0, 0, 0))
    else:
        d.ellipse([ccx - rr, ccy - rr, ccx + rr, ccy + rr], fill=dot)
    card = card.rotate(10, resample=Image.BICUBIC, expand=True)
    lay.alpha_composite(card, (int(cx - card.width / 2), int(cy - card.height / 2 + 2 * k)))
    return lay.resize((n, n), Image.LANCZOS)

def full_icon(n, round_=False):
    im = background(n).convert('RGBA')
    im.alpha_composite(card_layer(n))
    if round_:
        m = Image.new('L', (n * S, n * S), 0); ImageDraw.Draw(m).ellipse([0, 0, n * S - 1, n * S - 1], fill=255)
        im.putalpha(m.resize((n, n), Image.LANCZOS))
    return im

dens = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
for name, f in dens.items():
    dd = os.path.join(RES, f'mipmap-{name}')
    os.makedirs(dd, exist_ok=True)
    n = int(48 * f)
    full_icon(n).save(os.path.join(dd, 'ic_launcher.png'))
    full_icon(n, True).save(os.path.join(dd, 'ic_launcher_round.png'))
    a = int(108 * f)   # 적응형 아이콘: 108dp 중 가운데 72dp가 보인다
    background(a).save(os.path.join(dd, 'ic_launcher_background.png'))
    card_layer(a, scale=72 / 108).save(os.path.join(dd, 'ic_launcher_foreground.png'))
    # 알림 아이콘: 흰 실루엣(점은 뚫는다)
    ddn = os.path.join(RES, f'drawable-{name}')
    os.makedirs(ddn, exist_ok=True)
    s = int(24 * f)
    card_layer(s, scale=1.9, color=(255, 255, 255, 255), hole=True).save(os.path.join(ddn, 'ic_stat_notify.png'))

# 스플래시(안드로이드 11 이하): 어두운 바탕에 카드
for folder in os.listdir(RES):
    p = os.path.join(RES, folder, 'splash.png')
    if os.path.exists(p):
        w, h = Image.open(p).size
        im = Image.new('RGBA', (w, h), hexc('151516') + (255,))
        m = min(w, h)
        lay = card_layer(m, scale=.55)
        im.alpha_composite(lay, ((w - m) // 2, (h - m) // 2))
        im.convert('RGB').save(p)
print('icons ok')
