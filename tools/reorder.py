"""Day 01~40 단어 1,000개를 섞어 Day 구성을 새로 짠다. 기출 세트(5/14, 5/28)는 세트 안에서만 순서를 섞는다.

- 각 단어에 고정 id("id")를 먼저 박는다(없을 때만, 현재 배열 위치). 앱의 별표·완료·메모 기록은 이 id로
  저장되므로 순서를 바꿔도 기록이 다른 단어로 옮겨 가지 않는다.
- 같은 단어(철자)가 한 Day에 두 번 들어가지 않게 한다.
- 시드를 고정해 몇 번을 돌려도 같은 결과가 나온다. 이미 재구성된 데이터에는 다시 돌리지 않는다("reordered" 표시).
"""
import json, random, re
from pathlib import Path

INDEX = Path(__file__).parent.parent / "public" / "index.html"
SEED = 20260929
PER_DAY = 25

s = INDEX.read_bytes().decode("utf-8")
m = re.search(r'(<script id="data" type="application/json">)(.*?)(</script>)', s, re.S)
d = json.loads(m.group(2))
if d.get("reordered"):
    raise SystemExit("이미 재구성된 데이터입니다.")
W = d["words"]
for i, w in enumerate(W):
    w.setdefault("id", i)

rng = random.Random(SEED)
main = [w for w in W if w["d"].startswith("Day")]
extra = {}
for w in W:
    if not w["d"].startswith("Day"):
        extra.setdefault(w["d"], []).append(w)

# 한 Day 안에 같은 철자가 겹치지 않을 때까지 다시 섞는다
for attempt in range(1000):
    rng.shuffle(main)
    days = [main[k:k + PER_DAY] for k in range(0, len(main), PER_DAY)]
    if all(len({w["w"].lower() for w in day}) == len(day) for day in days):
        break
else:
    raise SystemExit("겹침 없는 배치를 찾지 못했습니다.")
for k, day in enumerate(days, 1):
    for n, w in enumerate(day, 1):
        w["d"], w["n"] = f"Day {k:02d}", n
for name, ws in extra.items():
    rng.shuffle(ws)
    for n, w in enumerate(ws, 1):
        w["n"] = n

# 원래 순서처럼 기출 세트의 앞뒤 위치를 지킨다: 앞에 있던 세트는 앞으로, 뒤에 있던 세트는 뒤로
first_main = next(i for i, w in enumerate(W) if w["d"].startswith("Day"))
before = [n for n in extra if any(W.index(w) < first_main for w in extra[n])]
after = [n for n in extra if n not in before]
d["words"] = [w for n in before for w in extra[n]] + [w for day in days for w in day] + [w for n in after for w in extra[n]]
d["reordered"] = SEED
INDEX.write_bytes((s[:m.start(2)] + json.dumps(d, ensure_ascii=False) + s[m.end(2):]).encode("utf-8"))
print(f"days {len(days)} × {PER_DAY}, extra sets {list(extra)}; entries total {len(d['words'])}")
