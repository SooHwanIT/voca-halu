"""단어·예문 발음을 Kokoro(af_heart)로 미리 만들어 Day별 묶음 파일로 넣는다.

실행:  D:\\voca-tts\\venv\\Scripts\\python.exe tools/tts/gen_kokoro.py [--days 0,1] [--jobs 3]
모델:  D:\\voca-tts\\kokoro-v1.0.onnx, voices-v1.0.bin  (Kokoro-82M, Apache 2.0)

출력:  public/tts/heart/<day>.json   {해시: [묶음번호, 시작, 길이]}
       public/tts/heart/<day>-<n>.bin  MP3 여러 개를 이어 붙인 파일
Cloudflare 무료 요금제는 파일이 2만 개까지라서 음성 하나하나를 파일로 두지 않고 묶는다.

앱(index.html)의 packText()와 같은 규칙으로 문장을 만들고 같은 해시(FNV-1a 32)를 쓴다.
이미 만든 Day는 건너뛴다(다시 만들려면 해당 json을 지운다).
"""
import argparse, glob, io, json, os, re, shutil, sys, time
from concurrent.futures import ProcessPoolExecutor

# phonemizer(espeak)가 부를 때마다 임시 폴더에 dll을 복사하고 지우지 못한다(0.4MB × 수천 개).
# C 드라이브가 가득 차서 멈춘 적이 있어 임시 폴더를 D로 옮기고 Day마다 치운다
TMP = r'D:\voca-tts\tmp'
os.makedirs(TMP, exist_ok=True)
os.environ['TMP'] = os.environ['TEMP'] = TMP

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'public', 'tts', 'heart')
MODEL = r'D:\voca-tts\kokoro-v1.0.onnx'
VOICES = r'D:\voca-tts\voices-v1.0.bin'
VOICE, SPEED, CHUNK = 'af_heart', 0.95, 24


def h32(s):
    h = 0x811c9dc5
    for ch in s:  # BMP 문자만 쓰므로 UTF-16 코드 단위와 같다
        h ^= ord(ch)
        h = (h * 0x01000193) & 0xffffffff
    return f'{h:08x}'


def load_data():
    html = open(os.path.join(ROOT, 'public', 'index.html'), encoding='utf-8').read()
    return json.loads(re.search(r'<script id="data" type="application/json">(.*?)</script>', html, re.S).group(1))


def texts_by_day(j):
    """앱이 읽는 영어 문장 전부 — 단어, 예문, 빈칸 예문, 콜로케이션. 처음 나온 Day에 붙인다."""
    days, seen = [], {}
    def add(t, d):
        t = (t or '').strip()
        if not t or t in seen: return
        seen[t] = d
        if d not in days: days.append(d)
    for w in j['words']:
        add(w['w'], w['d'])
        for x in [w] + (w.get('more') or []):
            ex = x.get('ex')
            if not ex: continue
            add(ex.replace('[', '').replace(']', ''), w['d'])
            add(re.sub(r'\[[^\]]+\]', ' ... ', ex, count=1), w['d'])
    for c in j['colls']:
        add(c['c'], c['d'])
    order = list(dict.fromkeys(w['d'] for w in j['words']))  # 앱의 DAYS 순서
    by = {d: [] for d in order}
    for t, d in seen.items(): by[d].append(t)
    return order, by


_k = None
def synth(text):
    import numpy as np, soundfile as sf
    global _k
    if _k is None:
        # 병렬 작업마다 코어를 나눠 쓴다 — 각자 전부 쓰려 하면 서로 부딪혀 오히려 느려진다
        import onnxruntime as ort
        from kokoro_onnx import Kokoro
        so = ort.SessionOptions()
        so.intra_op_num_threads = int(os.environ.get('TTS_THREADS', '3'))
        so.inter_op_num_threads = 1
        _k = Kokoro.from_session(ort.InferenceSession(MODEL, so, providers=['CPUExecutionProvider']), VOICES)
    a, sr = _k.create(text, voice=VOICE, speed=SPEED, lang='en-us')
    thr = np.max(np.abs(a)) * 0.015  # 앞뒤 무음을 줄여 누르자마자 들리게
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx): a = a[max(0, idx[0] - int(sr * .03)): idx[-1] + int(sr * .12)]
    buf = io.BytesIO()
    sf.write(buf, a, sr, format='MP3', compression_level=0.75)
    return buf.getvalue()


def do_day(args):
    di, day, texts = args
    path = os.path.join(OUT, f'{di}.json')
    if os.path.exists(path): return di, 0, 0
    t0, index, size = time.time(), {}, 0
    for n in range(0, len(texts), CHUNK):
        part, blob = texts[n:n + CHUNK], bytearray()
        for t in part:
            mp3 = synth(t)
            index[h32(t)] = [n // CHUNK, len(blob), len(mp3)]
            blob += mp3
        open(os.path.join(OUT, f'{di}-{n // CHUNK}.bin'), 'wb').write(blob)
        size += len(blob)
    json.dump(index, open(path, 'w'), separators=(',', ':'))  # 마지막에 써야 반쯤 된 Day를 건너뛰지 않는다
    for d in glob.glob(os.path.join(TMP, 'tmp*')):
        shutil.rmtree(d, ignore_errors=True)  # 다른 작업이 쓰는 중인 dll은 지워지지 않고 남는다
    return di, len(texts), size, time.time() - t0


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--days', default='')
    ap.add_argument('--jobs', type=int, default=3)
    a = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    order, by = texts_by_day(load_data())
    pick = [int(x) for x in a.days.split(',')] if a.days else range(len(order))
    jobs = [(i, order[i], by[order[i]]) for i in pick]
    print(f'{len(jobs)} days, {sum(len(j[2]) for j in jobs)} clips', flush=True)
    from concurrent.futures import as_completed
    with ProcessPoolExecutor(a.jobs) as ex:
        for f in as_completed([ex.submit(do_day, j) for j in jobs]):
            r = f.result()
            if r[1]: print(f'{time.strftime("%H:%M:%S")} day {r[0]}: {r[1]} clips, {r[2] // 1024} KB, {r[3]:.0f}s', flush=True)
            else: print(f'day {r[0]}: skip', flush=True)
    print('finished', flush=True)
