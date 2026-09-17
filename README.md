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
