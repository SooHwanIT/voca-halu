"""예문 이미지 일괄 생성기 — 로컬 ComfyUI(http://127.0.0.1:8188) API 를 직접 호출한다.

  python generate.py                 # 빠진 이미지를 전부 만든다 (이어하기 가능)
  python generate.py --watch         # 프롬프트 파일이 아직 늘어나는 중이면 기다렸다가 계속 만든다
  python generate.py --limit 3       # 예문 3개만 (시험용)
  python generate.py --ids a,b       # 특정 예문 id 만 다시 만든다 (--force 와 함께)

- 입력: sentences.json(extract.py), prompts/*.tsv(id<TAB>장면 프롬프트), themes.json(테마 프리셋)
- 출력: ../../public/img/<theme>/<id>.webp
- rendered.tsv 에 예문마다 (테마 설정 + 장면 프롬프트) 해시를 적어 두고, 프롬프트나 themes.json 이 바뀐 예문은 다시 만든다.
- 예문 하나마다 4개 테마를 한 그래프로 묶어 보내고, 같은 시드를 써서 테마끼리 구도가 비슷하게 나오게 한다.
- tools/imggen/STOP 파일을 만들면 지금 작업 중인 예문까지 마치고 멈춘다.
"""
import argparse, hashlib, io, json, os, sys, time, uuid
from pathlib import Path

import requests
from PIL import Image

HERE = Path(__file__).parent
OUT = HERE.parent.parent / "public" / "img"
COMFY = os.environ.get("COMFYUI_URL", "http://127.0.0.1:8188")
COMFY_TEMP = Path(os.environ.get("COMFYUI_TEMP", r"D:\ComfyUI\ComfyUI_windows_portable\ComfyUI\temp"))
IN_FLIGHT = 3  # GPU 가 쉬지 않도록 미리 넣어 두는 그래프 수


def log(*a):
    line = time.strftime("%H:%M:%S ") + " ".join(str(x) for x in a)
    print(line, flush=True)
    with open(HERE / "gen.log", "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_prompts():
    p = {}
    for f in sorted((HERE / "prompts").glob("*.tsv")):
        for line in f.read_text(encoding="utf-8").splitlines():
            if "\t" in line:
                i, s = line.split("\t", 1)
                if s.strip():
                    p[i.strip()] = s.strip().rstrip(".")
    return p


def seed_of(sid):
    return int(hashlib.sha1(sid.encode()).hexdigest()[:8], 16)


def build_graph(cfg, scene, seed):
    size = cfg["gen_size"]
    g = {
        "ckpt": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": cfg["checkpoint"]}},
        "lat": {"class_type": "EmptyLatentImage", "inputs": {"width": size, "height": size, "batch_size": 1}},
    }
    for t in cfg["themes"]:
        k = t["key"]
        g[f"{k}_pos"] = {"class_type": "CLIPTextEncode", "inputs": {"clip": ["ckpt", 1], "text": t["prompt"].replace("{scene}", scene)}}
        g[f"{k}_neg"] = {"class_type": "CLIPTextEncode", "inputs": {"clip": ["ckpt", 1], "text": t["negative"] + ", " + cfg["negative_base"]}}
        g[f"{k}_ks"] = {"class_type": "KSampler", "inputs": {
            "model": ["ckpt", 0], "positive": [f"{k}_pos", 0], "negative": [f"{k}_neg", 0], "latent_image": ["lat", 0],
            "seed": seed, "steps": cfg["steps"], "cfg": cfg["cfg"], "sampler_name": cfg["sampler"],
            "scheduler": cfg["scheduler"], "denoise": 1.0}}
        g[f"{k}_vae"] = {"class_type": "VAEDecode", "inputs": {"samples": [f"{k}_ks", 0], "vae": ["ckpt", 2]}}
        g[f"{k}_out"] = {"class_type": "PreviewImage", "inputs": {"images": [f"{k}_vae", 0]}}
    return g


def submit(graph):
    r = requests.post(f"{COMFY}/prompt", json={"prompt": graph, "client_id": str(uuid.uuid4())}, timeout=30)
    r.raise_for_status()
    d = r.json()
    if d.get("node_errors"):
        raise RuntimeError(json.dumps(d["node_errors"], ensure_ascii=False))
    return d["prompt_id"]


def wait(pid, timeout=900):
    end = time.time() + timeout
    while time.time() < end:
        h = requests.get(f"{COMFY}/history/{pid}", timeout=15).json()
        if pid in h:
            e = h[pid]
            if e.get("status", {}).get("status_str") == "error":
                raise RuntimeError("execution error: " + json.dumps(e["status"].get("messages", [])[-1:], ensure_ascii=False)[:500])
            return e["outputs"]
        time.sleep(0.4)
    raise TimeoutError(pid)


def save(cfg, outputs, sid):
    for t in cfg["themes"]:
        k = t["key"]
        img = outputs[f"{k}_out"]["images"][0]
        r = requests.get(f"{COMFY}/view", params={"filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img["type"]}, timeout=30)
        r.raise_for_status()
        im = Image.open(io.BytesIO(r.content)).convert("RGB")
        if cfg["out_size"] != im.width:
            im = im.resize((cfg["out_size"], cfg["out_size"]), Image.LANCZOS)
        dst = OUT / k / f"{sid}.webp"
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp = dst.with_suffix(".tmp")
        im.save(tmp, "WEBP", quality=cfg["webp_quality"], method=6)
        os.replace(tmp, dst)
        try:  # ComfyUI temp 폴더에 쌓이는 원본 PNG 정리
            (COMFY_TEMP / img.get("subfolder", "") / img["filename"]).unlink()
        except OSError:
            pass


MANIFEST = HERE / "rendered.tsv"


def render_key(cfg, scene):
    return hashlib.sha1((json.dumps(cfg, sort_keys=True, ensure_ascii=False) + "\n" + scene).encode()).hexdigest()[:12]


def load_manifest():
    m = {}
    if MANIFEST.exists():
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            if "\t" in line:
                i, k = line.split("\t", 1)
                m[i] = k  # 뒤에 적힌 줄이 최신
    return m


def todo(cfg, order, prompts, force_ids=None):
    keys = [t["key"] for t in cfg["themes"]]
    made = load_manifest()
    out = []
    for sid in order:
        if sid not in prompts:
            continue
        if force_ids is not None:
            if sid in force_ids:
                out.append(sid)
        elif made.get(sid) != render_key(cfg, prompts[sid]) or any(not (OUT / k / f"{sid}.webp").exists() for k in keys):
            out.append(sid)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--ids", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    cfg = json.loads((HERE / "themes.json").read_text(encoding="utf-8"))
    order = [s["id"] for s in json.loads((HERE / "sentences.json").read_text(encoding="utf-8"))]
    force_ids = set(a.ids.split(",")) if (a.ids and a.force) else None
    requests.get(f"{COMFY}/system_stats", timeout=5).raise_for_status()

    done_total, t0, failed = 0, time.time(), set()
    while True:
        prompts = load_prompts()
        jobs = [j for j in todo(cfg, order, prompts, force_ids) if j not in failed]
        if a.ids and not a.force:
            jobs = [j for j in jobs if j in set(a.ids.split(","))]
        if a.limit:
            jobs = jobs[: max(0, a.limit - done_total)]
        if not jobs:
            if a.watch and len(prompts) < len(order) and not (HERE / "STOP").exists():
                time.sleep(60)
                continue
            break
        log(f"batch: {len(jobs)} sentences to render (prompts ready {len(prompts)}/{len(order)})")
        pending = []  # (sid, prompt_id)
        it = iter(jobs)
        stop = False
        while True:
            while not stop and len(pending) < IN_FLIGHT:
                sid = next(it, None)
                if sid is None:
                    break
                pending.append((sid, submit(build_graph(cfg, prompts[sid], seed_of(sid)))))
            if not pending:
                break
            sid, pid = pending.pop(0)
            try:
                save(cfg, wait(pid), sid)
                with open(MANIFEST, "a", encoding="utf-8") as f:
                    f.write(f"{sid}\t{render_key(cfg, prompts[sid])}\n")
            except Exception as e:  # 한 예문 실패로 전체를 멈추지 않는다
                failed.add(sid)
                log("FAIL", sid, repr(e)[:300])
                continue
            done_total += 1
            if done_total % 20 == 0:
                rate = (time.time() - t0) / done_total
                left = len(todo(cfg, order, prompts)) if done_total % 200 == 0 else None
                log(f"done {done_total} sentences, {rate:.1f}s/sentence" + (f", remaining {left} (~{left*rate/3600:.1f}h)" if left is not None else ""))
            if (HERE / "STOP").exists():
                stop = True
        if stop or force_ids is not None:
            break
    log(f"finished: {done_total} sentences in {(time.time()-t0)/60:.1f} min")


if __name__ == "__main__":
    sys.exit(main())
