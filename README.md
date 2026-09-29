# 비밀과외 VOCA 암기장

토익 단어(Day 01–30 + 기출) 단어장·퀴즈·기출 문제 웹앱. 정적 HTML 한 파일이며, 학습 기록은 브라우저 localStorage에 저장됩니다.

- `index.html` — 앱 본체(데이터 포함)
- `manifest.json`, `icon.*` — 홈 화면 추가용

## 배포

Cloudflare Workers(정적 에셋)로 배포합니다. `CLOUDFLARE_API_TOKEN`이 있는 환경에서:

```bash
npx wrangler deploy
```

- Cloudflare: https://voca-halu.suhwanit.workers.dev
- GitHub Pages: https://soohwanit.github.io/voca-halu/ (main에 push하면 Actions가 자동 배포)
- `public/` 안의 파일이 그대로 서비스됩니다.

## 예문 그림 (ComfyUI)

모든 예문(4,381개)마다 테마 4가지 — 카툰 · 리얼리티 · 수채화 · 3D 클레이 — 그림이 `public/img/<테마>/<id>.webp` 로 들어 있습니다. 단어의 대표 그림은 첫 번째 예문의 그림입니다. 앱의 설정 화면에서 테마를 고르거나 그림을 끌 수 있고, 그림을 누르면 네 테마를 크게 비교해 볼 수 있습니다.

만드는 도구는 `tools/imggen/` 에 있습니다 (로컬 ComfyUI + DreamShaper 8 필요).

| 파일 | 역할 |
| --- | --- |
| `extract.py` | `index.html` 데이터에서 예문을 뽑아 `sentences.json`, `chunks/` 생성. id = 영어 예문의 sha1 앞 10자리 |
| `PROMPT_GUIDE.md` | 예문 → 장면 프롬프트 작성 규칙. 결과는 `prompts/*.tsv` (`id<TAB>장면`) |
| `themes.json` | 테마 프리셋(스타일 프롬프트, 네거티브, 해상도, 품질) |
| `generate.py` | ComfyUI API 로 빠진 그림만 생성 (이어하기 가능, `STOP` 파일로 중단) |
| `inject.py` | `index.html` 의 각 예문에 그림 id(`"i"`) 기록 |
| `check_align.py` | 프롬프트 파일과 예문 줄이 어긋나지 않았는지 확인 |

예문을 고치거나 추가했다면:

```bash
cd tools/imggen
python extract.py        # sentences.json / chunks 갱신
# 새 예문의 장면 프롬프트를 prompts/*.tsv 에 추가
python generate.py       # 없는 그림만 생성
python inject.py         # index.html 에 그림 id 반영
```
