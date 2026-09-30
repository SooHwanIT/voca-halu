"""포카보카 아이콘(M7: 주황→분홍 그라데이션 바탕 + 기운 흰 카드)을 모든 크기로 만든다.

1. SVG 원본 4장을 크롬(헤드리스)으로 1024px PNG로 그린다 — 전체, 카드만(투명), 바탕만, 알림용 흰 실루엣
2. PIL로 웹(public/)·안드로이드(app/android/.../res)·스토어(marketing/play) 크기로 줄인다

실행: python marketing/icon/build_icons.py   (크롬 필요)
"""
import os, subprocess, tempfile
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.dirname(os.path.dirname(HERE))
PUB = os.path.join(SITE, 'public')
RES = os.path.join(SITE, 'app', 'android', 'app', 'src', 'main', 'res')
PLAY = os.path.join(SITE, 'marketing', 'play')
CHROME = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
TMP = r'D:\voca-mkt\icon\build'   # 크롬이 한글 경로를 못 여는 경우가 있어 ASCII 경로에서 그린다

GRAD = '<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FF8A3D"/><stop offset="1" stop-color="#FF3D8B"/></linearGradient>'
SHADOW = '<filter id="sh" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="0" dy="18" stdDeviation="20" flood-color="#7a1030" flood-opacity=".35"/></filter>'
CARD = '<g transform="rotate(-8 256 256)"><rect x="136" y="88" width="240" height="336" rx="32" fill="{fill}"/></g>'

SVGS = {
    'full': f'<defs>{GRAD}{SHADOW}</defs><rect width="512" height="512" fill="url(#bg)"/><g filter="url(#sh)">{CARD.format(fill="#fff")}</g>',
    'fg': f'<defs>{SHADOW}</defs><g filter="url(#sh)">{CARD.format(fill="#fff")}</g>',
    'bg': f'<defs>{GRAD}</defs><rect width="512" height="512" fill="url(#bg)"/>',
    'mono': CARD.format(fill='#fff'),
}


def svg(body):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="1024" height="1024">{body}</svg>'


def render():
    os.makedirs(TMP, exist_ok=True)
    out = {}
    for name, body in SVGS.items():
        html = os.path.join(TMP, f'{name}.html')
        open(html, 'w', encoding='utf-8').write(f'<!doctype html><html><body style="margin:0;background:transparent">{svg(body)}</body></html>')
        png = os.path.join(TMP, f'{name}.png')
        subprocess.run([CHROME, '--headless=new', '--disable-gpu', '--hide-scrollbars', '--default-background-color=00000000',
                        '--window-size=1024,1024', f'--screenshot={png}', 'file:///' + html.replace('\\', '/')],
                       check=True, capture_output=True)
        out[name] = Image.open(png).convert('RGBA')
    open(os.path.join(PUB, 'icon.svg'), 'w', encoding='utf-8').write(svg(SVGS['full']).replace(' width="1024" height="1024"', ''))
    return out


def rounded(im, r):
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=int(im.width * r), fill=255)
    o = im.copy(); o.putalpha(m); return o


def circle(im):
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).ellipse([0, 0, im.width - 1, im.height - 1], fill=255)
    o = im.copy(); o.putalpha(m); return o


def fit(im, n):
    return im.resize((n, n), Image.LANCZOS)


def main():
    M = render()
    full, fg, bg, mono = M['full'], M['fg'], M['bg'], M['mono']
    # 웹 · PWA (전체를 채운 정사각형 — 기기가 모서리를 깎는다)
    for n, name in ((512, 'icon-512.png'), (192, 'icon-192.png'), (180, 'icon-180.png')):
        fit(full, n).convert('RGB').save(os.path.join(PUB, name))
    # 스토어 아이콘
    fit(full, 512).convert('RGB').save(os.path.join(PLAY, 'icon-512.png'))
    # 안드로이드
    dens = {'mdpi': 1, 'hdpi': 1.5, 'xhdpi': 2, 'xxhdpi': 3, 'xxxhdpi': 4}
    for d, f in dens.items():
        mm = os.path.join(RES, f'mipmap-{d}'); os.makedirs(mm, exist_ok=True)
        n = int(48 * f)
        rounded(fit(full, n), .22).save(os.path.join(mm, 'ic_launcher.png'))
        circle(fit(full, n)).save(os.path.join(mm, 'ic_launcher_round.png'))
        a = int(108 * f)   # 적응형: 108dp 중 가운데 72dp가 보인다 → 512 그림을 72/108로 줄여 가운데
        fit(bg, a).convert('RGB').save(os.path.join(mm, 'ic_launcher_background.png'))
        lay = Image.new('RGBA', (a, a), (0, 0, 0, 0)); s = round(a * 72 / 108)
        lay.alpha_composite(fit(fg, s), ((a - s) // 2, (a - s) // 2)); lay.save(os.path.join(mm, 'ic_launcher_foreground.png'))
        dn = os.path.join(RES, f'drawable-{d}'); os.makedirs(dn, exist_ok=True)
        s24 = int(24 * f)   # 알림 아이콘: 흰 실루엣, 여백 조금
        lay = Image.new('RGBA', (s24, s24), (0, 0, 0, 0)); k = round(s24 * 1.25)
        big = fit(mono, k); c = (k - s24) // 2
        lay.alpha_composite(big.crop((c, c, c + s24, c + s24))); lay.save(os.path.join(dn, 'ic_stat_notify.png'))
        # 안드로이드 12+ 시작 화면 아이콘: 원 안에 전체 아이콘
        sp = int(240 * f); lay = Image.new('RGBA', (sp, sp), (0, 0, 0, 0)); ci = int(sp * 160 / 240)
        lay.alpha_composite(circle(fit(full, ci)), ((sp - ci) // 2, (sp - ci) // 2)); lay.save(os.path.join(dn, 'splash_icon.png'))
    # 안드로이드 11 이하 시작 화면(splash.png): 바탕색 + 가운데 아이콘
    for folder in os.listdir(RES):
        p = os.path.join(RES, folder, 'splash.png')
        if os.path.exists(p):
            w, h = Image.open(p).size
            dark = 'night' in folder
            im = Image.new('RGBA', (w, h), (21, 21, 22, 255) if dark else (230, 228, 223, 255))
            n = int(min(w, h) * .28)
            im.alpha_composite(rounded(fit(full, n), .22), ((w - n) // 2, (h - n) // 2))
            im.convert('RGB').save(p)
    print('icons ok')


if __name__ == '__main__':
    main()
