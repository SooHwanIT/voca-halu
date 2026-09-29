#!/usr/bin/env bash
# 포카보카 안드로이드 앱 빌드 — 서명된 APK와 AAB를 만든다.
# 한글 경로에서는 안드로이드 빌드 도구가 깨지므로 D:/voca-app 로 옮겨서 빌드한다.
# 서명 키: D:/voca-keys/keystore.properties (저장소에 넣지 않는다. 잃어버리면 Play 업데이트 키를 재설정해야 한다)
set -e
HERE="$(cd "$(dirname "$0")" && pwd)"
OUT=/d/voca-app
mkdir -p "$OUT"
cp -r "$HERE"/. "$OUT"/
cd "$OUT"
npm ci --no-audit --no-fund
npx cap sync android
echo 'sdk.dir=C:/Users/happy/AppData/Local/Android/Sdk' > android/local.properties
export JAVA_HOME="${JAVA_HOME:-/c/Program Files/Java/jdk-21.0.11}"
cd android && ./gradlew assembleRelease bundleRelease --no-daemon -q
ls -la app/build/outputs/apk/release/app-release.apk app/build/outputs/bundle/release/app-release.aab
