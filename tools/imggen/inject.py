"""index.html 데이터의 예문에 이미지 id("i")를 넣는다.

4개 테마 그림이 모두 있는 예문에만 넣고, 없는 예문에서는 뺀다 — 앱이 없는 그림을 요청하지 않게.
그림을 새로 만들었거나 예문을 고친 뒤 다시 돌리면 된다.
이미지 파일은 public/img/<theme>/<i>.webp — id 규칙은 extract.py 의 sid() 와 같다.
"""
import json, re
from pathlib import Path
from extract import INDEX, sid

HERE = Path(__file__).parent
IMG = INDEX.parent / "img"
THEMES = [t["key"] for t in json.loads((HERE / "themes.json").read_text(encoding="utf-8"))["themes"]]


def tag(x):
    i = sid(x["ex"])
    if all((IMG / t / f"{i}.webp").exists() for t in THEMES):
        x["i"] = i
        return 1
    x.pop("i", None)
    return 0


s = INDEX.read_bytes().decode("utf-8")  # 줄바꿈을 건드리지 않도록 바이트로 읽고 쓴다
m = re.search(r'(<script id="data" type="application/json">)(.*?)(</script>)', s, re.S)
d = json.loads(m.group(2))
have = total = 0
for w in d["words"]:
    for x in [w] + (w.get("more") or []):
        have += tag(x)
        total += 1
INDEX.write_bytes((s[:m.start(2)] + json.dumps(d, ensure_ascii=False) + s[m.end(2):]).encode("utf-8"))
print(f"pictures ready for {have}/{total} sentences")
