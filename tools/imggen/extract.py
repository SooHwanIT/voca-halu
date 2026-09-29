"""index.html 안의 단어 데이터에서 예문을 뽑아 sentences.json 과 프롬프트 작성용 조각(chunks/)을 만든다.

이미지 id 는 예문 영어 문장의 sha1 앞 10자리 — 데이터 순서가 바뀌어도 같은 예문은 같은 이미지를 가리킨다.
"""
import hashlib, json, re
from pathlib import Path

HERE = Path(__file__).parent
INDEX = HERE.parent.parent / "public" / "index.html"
CHUNKS = 8


def sid(ex: str) -> str:
    return hashlib.sha1(ex.strip().encode("utf-8")).hexdigest()[:10]


def load_data():
    s = INDEX.read_text(encoding="utf-8")
    m = re.search(r'<script id="data" type="application/json">(.*?)</script>', s, re.S)
    return json.loads(m.group(1))


def main():
    words = load_data()["words"]
    out, seen = [], set()
    for w in words:
        for x in [{"ex": w["ex"], "ek": w["ek"]}] + (w.get("more") or []):
            i = sid(x["ex"])
            if i in seen:
                continue
            seen.add(i)
            out.append({"id": i, "word": w["w"], "mean": w["m"], "ex": x["ex"], "ek": x["ek"]})
    (HERE / "sentences.json").write_text(json.dumps(out, ensure_ascii=False, indent=0), encoding="utf-8")
    cdir = HERE / "chunks"
    cdir.mkdir(exist_ok=True)
    size = -(-len(out) // CHUNKS)
    for c in range(CHUNKS):
        part = out[c * size:(c + 1) * size]
        lines = [f'{x["id"]}\t{x["word"]}\t{x["ex"]}\t{x["ek"]}' for x in part]
        (cdir / f"chunk{c}.tsv").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(len(out), "sentences,", size, "per chunk")


if __name__ == "__main__":
    main()
