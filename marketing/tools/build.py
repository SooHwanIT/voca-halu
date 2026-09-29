"""포카보카 마케팅 이미지 생성기 — copy.json 문구 + 실제 예문 그림/앱 캡처로 HTML을 짜고 Chrome headless로 PNG를 뽑는다.
python build.py            # 전부
python build.py store_1    # 일부만
"""
import json, subprocess, sys, base64
from pathlib import Path

HERE = Path(__file__).parent
APP = Path(r"C:\Users\happy\Downloads\비밀과외 VOCA 단어암기장-20260915T012833Z-1-001\비밀과외 VOCA 단어암기장\voca-site\public")
OUT = HERE / "out"; OUT.mkdir(exist_ok=True)
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
C = json.loads((HERE / "copy.json").read_text(encoding="utf-8"))
VER = {"cartoon": "카툰 ver.", "real": "리얼 ver.", "water": "수채화 ver.", "clay": "클레이 ver."}
_cache = {}


def uri(p):
    p = Path(p)
    if p not in _cache:
        mime = "image/webp" if p.suffix == ".webp" else "image/png"
        _cache[p] = f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()
    return _cache[p]


def pic(i, t): return uri(APP / "img" / t / f"{i}.webp")
def shot(n): return uri(HERE / "shots" / f"{n}.png")


CSS = """
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&display=swap">
<style>
:root{--bg:#121213;--ink:#F1EFEA;--ink2:#A7A5A0;--ink3:#6F6E72;--sig:#FF6A2E;--card:#F6F3EC;--cardInk:#1C1B19}
*{box-sizing:border-box}html,body{margin:0}
body{width:%(w)dpx;height:%(h)dpx;overflow:hidden;background:var(--bg);color:var(--ink);font-family:"Pretendard Variable",Pretendard,sans-serif;word-break:keep-all;-webkit-font-smoothing:antialiased;position:relative}
body::before{content:"";position:absolute;inset:0;background:radial-gradient(70%% 45%% at 50%% 72%%,rgba(255,106,46,.16),transparent 70%%)}
.abs{position:absolute}
.eyebrow{font-weight:600;color:var(--sig);letter-spacing:.005em}
h1{margin:0;font-weight:800;letter-spacing:-.04em;line-height:1.12}
h1 em{font-style:normal;color:var(--sig)}
.sub{color:var(--ink2);font-weight:500;letter-spacing:-.015em;line-height:1.45}
/* photocard — 앱의 카드와 같은 디자인 */
.pc{position:absolute;width:var(--w);aspect-ratio:.72;transform-origin:50%% 80%%}
.pcard{position:absolute;inset:0;border-radius:7%%/5%%;overflow:hidden;background:#1b1b1e;isolation:isolate;container-type:inline-size;
  box-shadow:0 calc(var(--w)*.1) calc(var(--w)*.22) calc(var(--w)*-.07) rgba(0,0,0,.8)}
.pcard>img{position:absolute;inset:0;width:100%%;height:100%%;object-fit:cover}
.pcard::before{content:"";position:absolute;inset:0;z-index:3;border-radius:inherit;pointer-events:none;
  background:linear-gradient(118deg,rgba(255,255,255,0) 28%%,rgba(255,255,255,.24) 40%%,rgba(255,255,255,.04) 47%%,rgba(255,255,255,0) 58%%),
             linear-gradient(to top,rgba(10,8,12,.66),rgba(10,8,12,0) 40%%);
  box-shadow:inset 0 0 0 1px rgba(255,255,255,.32),inset 0 0 0 3.5cqw rgba(255,255,255,.05)}
.pcard .cap{position:absolute;left:8cqw;right:8cqw;bottom:6.5cqw;z-index:4;display:flex;align-items:flex-end;justify-content:space-between;gap:4px;color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.35)}
.pcard .cap em{font-family:"Instrument Serif",Georgia,serif;font-style:italic;font-size:15cqw;line-height:.95;white-space:nowrap}
.pcard .tag{position:absolute;top:6cqw;right:6cqw;z-index:4;font-size:5.4cqw;font-weight:700;letter-spacing:.06em;color:#fff;background:rgba(12,10,16,.42);backdrop-filter:blur(6px);border-radius:99px;padding:1.4cqw 3.4cqw}
.pcard .exl{position:absolute;left:8cqw;right:8cqw;bottom:25cqw;z-index:4;color:#fff;font-size:5.4cqw;line-height:1.4;font-weight:500;text-shadow:0 1px 8px rgba(0,0,0,.5)}
.pcard .exl b{color:#FFB089;font-weight:700}
.pcard.ex::before{background:linear-gradient(118deg,rgba(255,255,255,0) 28%%,rgba(255,255,255,.2) 40%%,rgba(255,255,255,0) 56%%),linear-gradient(to top,rgba(10,8,12,.8),rgba(10,8,12,0) 58%%)}
.pback{position:absolute;inset:0;border-radius:7%%/5%%;overflow:hidden;color:#EEE7F6;container-type:inline-size;
  background:url("data:image/svg+xml,%%3Csvg xmlns='http://www.w3.org/2000/svg' width='44' height='44'%%3E%%3Crect x='15' y='11' width='14' height='19' rx='3.5' transform='rotate(-10 22 20)' fill='none' stroke='white' stroke-opacity='.08' stroke-width='1.4'/%%3E%%3C/svg%%3E"),
             radial-gradient(120%% 70%% at 50%% 110%%,rgba(255,106,46,.4),transparent 60%%),linear-gradient(160deg,#352c46 0%%,#1c1826 58%%,#15131b 100%%);
  box-shadow:0 calc(var(--w)*.1) calc(var(--w)*.22) calc(var(--w)*-.07) rgba(0,0,0,.8),inset 0 0 0 1px rgba(255,255,255,.14)}
.pback .mk{position:absolute;left:50%%;top:44%%;width:16cqw;height:21cqw;border-radius:3.4cqw;background:#EEE7F6;transform:translate(-50%%,-50%%) rotate(-9deg)}
.pback .mk::after{content:"";position:absolute;left:50%%;top:50%%;width:7cqw;height:7cqw;border-radius:50%%;background:var(--sig);transform:translate(-50%%,-50%%)}
.pback .wm{position:absolute;left:0;right:0;top:61%%;text-align:center;font-size:5.4cqw;font-weight:700;letter-spacing:.42em;opacity:.72}
.pback .nn{position:absolute;left:0;right:0;bottom:7cqw;text-align:center;font-family:"Instrument Serif",Georgia,serif;font-style:italic;font-size:8cqw;opacity:.6}
.brand{position:absolute;display:flex;align-items:center;gap:.45em;font-weight:800;letter-spacing:-.03em}
.logo{width:.78em;height:1.02em;border-radius:.16em;background:var(--ink);transform:rotate(-9deg);position:relative;flex:none}
.logo::after{content:"";position:absolute;width:.34em;height:.34em;border-radius:50%%;background:var(--sig);left:50%%;top:50%%;transform:translate(-50%%,-50%%)}
.phone{position:absolute;border-radius:60px;overflow:hidden;background:#000;box-shadow:0 0 0 10px #242528,0 0 0 11px #3a3b3f,0 60px 120px -30px rgba(0,0,0,.85)}
.phone img{display:block;width:100%%}
.stat{display:flex;justify-content:space-between;align-items:baseline;border-top:2px solid #2A2A2D;padding:26px 0}
.stat span{color:var(--ink2);font-weight:500}
.stat b{font-weight:800;letter-spacing:-.035em}
.arrow{position:absolute;color:var(--sig);font-weight:800}
</style>"""


def page(w, h, body):
    return f"<!doctype html><html lang=ko><head><meta charset=utf-8>{CSS % dict(w=w, h=h)}</head><body>{body}</body></html>"


def en(s): return s.replace("[", "<b>").replace("]", "</b>")


def card(i, theme, w, x, y, rot=0, word="", label=None, ex=None, back=False, z=1, no=None):
    pos = f'style="--w:{w}px;left:{x}px;top:{y}px;transform:rotate({rot}deg);z-index:{z}"'
    if back:
        return f'<div class="pc" {pos}><div class="pback"><span class="mk"></span><span class="wm">POCAVOCA</span><span class="nn">No.{no or "007"}</span></div></div>'
    small = label if label is not None else VER[theme]
    exl = f'<span class="exl">{en(ex)}</span>' if ex else ''
    return (f'<div class="pc" {pos}><div class="pcard{" ex" if ex else ""}"><img src="{pic(i, theme)}">{exl}'
            f'<span class="tag">{small}</span><span class="cap"><em>{word}</em></span></div></div>')


def brand(x, y, fs, color="var(--ink)"):
    return f'<div class="brand" style="left:{x}px;top:{y}px;font-size:{fs}px;color:{color}"><span class="logo"></span>포카보카</div>'


def head(c, W, top=120, size=84, eb=32, subsize=34, pad=84):
    return (f'<div class="abs" style="left:{pad}px;right:{pad}px;top:{top}px"><div class="eyebrow" style="font-size:{eb}px">{c["eyebrow"]}</div>'
            f'<h1 style="font-size:{size}px;margin-top:22px">{c["title"]}</h1>'
            + (f'<div class="sub" style="font-size:{subsize}px;margin-top:24px">{c["sub"]}</div>' if c.get("sub") else '') + '</div>')


def fan(i, cx, y, w, word, spread=1.0):
    order = [("water", -15, -1.55), ("real", -5, -0.52), ("clay", 5, 0.52), ("cartoon", 15, 1.55)]
    return "".join(card(i, t, w, int(cx - w / 2 + dx * w * .56 * spread), int(y + abs(dx) * w * .09), r * spread, word, z=5 - abs(round(dx))) for t, r, dx in order)


# ---------------- store 1080x1920 ----------------
def store(c):
    W, H = 1080, 1920
    k = c["kind"]; hero = C["heroes"]
    if k == "fan":
        h = hero["fan"]
        body = head(c, W) + fan(h["id"], 540, 640, 360, h["word"], .8) + \
            f'<div class="sub abs" style="left:84px;right:84px;top:1390px;text-align:center;font-size:32px">{en(h["ex"])}</div>' + brand(84, 1740, 52)
    elif k == "reveal":
        h = hero["reveal"]
        body = head(c, W) + card(h["id"], "cartoon", 420, 70, 640, -5, back=True, no="014") + \
            card(h["id"], "cartoon", 420, 590, 640, 4, h["word"], label="No.014") + \
            '<div class="arrow" style="left:503px;top:880px;font-size:72px">→</div>' + brand(84, 1740, 52)
    elif k == "versions":
        h = hero["versions"]; w = 430
        pos = [("cartoon", 84, 520, -3), ("real", 566, 510, 3), ("water", 84, 1160, 2), ("clay", 566, 1150, -2)]
        body = head(c, W) + "".join(card(h["id"], t, w, x, y, r, h["word"]) for t, x, y, r in pos)
    elif k == "four":
        h = hero["four"]; w = 430
        pos = [(84, 440, -2), (566, 430, 2), (84, 1080, 2), (566, 1070, -2)]
        body = head(c, W) + "".join(card(x["i"], "cartoon", w, px, py, r, h["word"], label=f"No.{n+1:03d}", ex=x["ex"]) for n, (x, (px, py, r)) in enumerate(zip(h["xs"], pos)))
    elif k == "phone":
        body = head(c, W) + f'<div class="phone" style="left:175px;top:{c.get("phoneTop", 700)}px;width:730px"><img src="{shot(c["shot"])}"></div>'
    else:  # free
        rows = "".join(f'<div class="stat"><span style="font-size:38px">{a}</span><b style="font-size:92px">{b}</b></div>' for a, b in C["numbers"])
        body = head(c, W) + f'<div class="abs" style="left:84px;right:84px;top:760px">{rows}</div>' + brand(84, 1720, 52)
    return page(W, H, body)


# ---------------- feature graphic 1024x500 ----------------
def feature():
    h = C["heroes"]["fan"]; f = C["feature"]
    body = (brand(58, 54, 40) +
            f'<div class="abs" style="left:58px;top:150px;width:470px"><h1 style="font-size:58px">{f["title"]}</h1>'
            f'<div class="sub" style="font-size:22px;margin-top:20px">{f["sub"]}</div></div>' +
            fan(h["id"], 770, 70, 205, h["word"], .9))
    return page(1024, 500, body)


# ---------------- social 1080x1350 ----------------
def social(c):
    W, H = 1080, 1350; k = c["kind"]; hero = C["heroes"]
    top = head(c, W, top=90, size=74, eb=30, subsize=30, pad=80)
    foot = brand(80, H - 122, 46) + f'<div class="abs" style="right:80px;top:{H-106}px;font-size:26px;color:var(--ink3);font-weight:500">{C["url"]}</div>'
    if k == "fan":
        h = hero[c.get("hero", "fan")]; mid = fan(h["id"], 540, 470, 320, h["word"], .9)
    elif k == "reveal":
        h = hero["reveal"]
        mid = card(h["id"], "cartoon", 380, 90, 420, -5, back=True, no="014") + card(h["id"], "cartoon", 380, 610, 420, 4, h["word"], label="No.014") + \
            '<div class="arrow" style="left:503px;top:650px;font-size:66px">→</div>'
    elif k == "versions":
        h = hero["versions"]; w = 300
        pos = [("cartoon", 200, 380, -3), ("real", 580, 372, 3), ("water", 200, 830, 2), ("clay", 580, 822, -2)]
        mid = "".join(card(h["id"], t, w, x, y, r, h["word"]) for t, x, y, r in pos)
        foot = ''  # 카드가 바닥까지 채운다
    else:
        rows = "".join(f'<div class="stat"><span style="font-size:34px">{a}</span><b style="font-size:84px">{b}</b></div>' for a, b in C["numbers"])
        mid = f'<div class="abs" style="left:80px;right:80px;top:420px">{rows}</div>'
    return page(W, H, top + mid + foot)


JOBS = {}
for n, c in enumerate(C["store"], 1): JOBS[f"store_{n}"] = (1080, 1920, lambda c=c: store(c))
JOBS["feature"] = (1024, 500, feature)
for n, c in enumerate(C["social"], 1): JOBS[f"social_{n}"] = (1080, 1350, lambda c=c: social(c))

for name in (sys.argv[1:] or list(JOBS)):
    w, h, fn = JOBS[name]
    html = HERE / "html" / f"{name}.html"; html.parent.mkdir(exist_ok=True)
    html.write_text(fn(), encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--force-device-scale-factor=1",
                    f"--window-size={w},{h}", "--virtual-time-budget=6000", f"--screenshot={OUT / (name + '.png')}", html.as_uri()], capture_output=True)
    print("rendered", name)
