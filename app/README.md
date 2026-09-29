# 포카보카 안드로이드 앱

Capacitor 8 껍데기 앱. 화면은 배포된 사이트(https://voca-halu.suhwanit.workers.dev)를 그대로 띄우고,
앱에서만 되는 것(예약 알림, 뒤로 가기 버튼, 상태 표시줄)을 더한다. 사이트를 배포하면 앱 화면도 바로 바뀐다.

- 앱 id: `com.halustudio.pocavoca` (Play에 올린 뒤에는 바꿀 수 없다)
- 알림: docs/NOTIFICATIONS.md — `@capacitor/local-notifications`, 정확한 알람 권한은 뺐다
- 아이콘: `make_icons.py` (public/icon.svg 모양을 그대로 그림)
- 빌드: `bash app/build.sh` → D:/voca-app/android/app/build/outputs/{apk,bundle}/release
- 버전 올리기: android/app/build.gradle 의 versionCode(+1)·versionName
- 서명 키: D:/voca-keys (저장소 밖). **이 폴더를 따로 백업할 것.**
