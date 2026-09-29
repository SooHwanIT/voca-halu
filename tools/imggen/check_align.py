"""prompts/*.tsv 가 chunks/*.tsv 와 줄 단위로 맞게 짝지어졌는지 단어 겹침으로 대략 확인한다."""
import re, sys
from pathlib import Path
HERE = Path(__file__).parent
STOP = set("a an the of to in on at for and or with by from is are was were be been will would can could should our their his her its this that these those it they we you he she as into over after before about all any some new".split())
tok = lambda s: {w for w in re.findall(r"[a-z]+", s.lower()) if len(w) > 2 and w not in STOP}
for name in sys.argv[1:] or sorted(p.name for p in (HERE / "prompts").glob("chunk*.tsv")):
    src = [l.split("\t") for l in (HERE / "chunks" / name).read_text(encoding="utf-8").splitlines()]
    out = [l.split("\t", 1) for l in (HERE / "prompts" / name).read_text(encoding="utf-8").splitlines() if l.strip()]
    bad = []
    if [o[0] for o in out] != [s[0] for s in src]:
        print(name, "ID MISMATCH", len(out), len(src)); continue
    for k, (s, o) in enumerate(zip(src, out)):
        own = len(tok(s[2]) & tok(o[1]))
        nb = max((len(tok(src[j][2]) & tok(o[1])) for j in (k - 1, k + 1) if 0 <= j < len(src)), default=0)
        if nb > own and nb >= 2:
            bad.append(k + 1)
    print(name, len(out), "lines; suspicious:", len(bad), bad[:30])
