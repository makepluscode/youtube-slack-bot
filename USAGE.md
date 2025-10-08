# 사용 가이드

## 🚀 빠른 시작

### 1. 설치
```bash
# 자동 설치 스크립트 실행
./scripts/setup.sh
```

### 2. 환경 설정
```bash
# .env 파일 편집
nano .env

# 필수 값 입력:
# SLACK_BOT_TOKEN=xoxb-...
# SLACK_APP_TOKEN=xapp-...
```

### 3. 실행
```bash
# 개발 모드로 실행
uv run youtube-bot

# 또는
uv run python -m src.main
```

## 📝 uv 명령어

### 의존성 관리
```bash
# 의존성 설치
uv sync

# 개발 의존성 포함
uv sync --extra dev

# 의존성 추가
uv add package-name

# 의존성 제거
uv remove package-name
```

### 실행
```bash
# 스크립트 실행
uv run youtube-bot

# Python 모듈 실행
uv run python -m src.main

# 임의의 명령어 실행
uv run python script.py
```

### 개발
```bash
# 포매팅
uv run black src/

# 린팅
uv run ruff check src/

# 테스트
uv run pytest

# REPL
uv run python
```

## 🔧 백그라운드 서비스

### 설치
```bash
./scripts/install_service.sh
```

### 관리
```bash
# 상태 확인
launchctl list | grep youtube-downloader

# 로그 확인
tail -f logs/app.log

# 서비스 중지
launchctl unload ~/Library/LaunchAgents/com.makepluscode.youtube-downloader.plist

# 서비스 시작
launchctl load ~/Library/LaunchAgents/com.makepluscode.youtube-downloader.plist
```

## 💡 유용한 팁

### 빠른 재시작
```bash
# 서비스 재시작
launchctl unload ~/Library/LaunchAgents/com.makepluscode.youtube-downloader.plist && \
launchctl load ~/Library/LaunchAgents/com.makepluscode.youtube-downloader.plist
```

### 디버깅
```bash
# 상세 로그와 함께 실행
LOG_LEVEL=DEBUG uv run youtube-bot

# 실시간 로그 모니터링
tail -f logs/app.log logs/stderr.log
```

### Ollama 관리
```bash
# 모델 확인
ollama list

# 모델 다운로드
ollama pull gemma3:4b

# Ollama 서비스 시작
brew services start ollama

# Ollama 서비스 중지
brew services stop ollama
```

## 🎯 Slack에서 사용하기

### 기본 사용
```
https://www.youtube.com/watch?v=VIDEO_ID 다운로드해줘
```

### 자연어 명령
```
이거 받아줘: https://youtu.be/VIDEO_ID
```

### 여러 영상 다운로드
```
다운로드:
https://www.youtube.com/watch?v=VIDEO1
https://www.youtube.com/watch?v=VIDEO2
https://www.youtube.com/watch?v=VIDEO3
```

## ❓ 문제 해결

### uv 명령어가 없다면
```bash
brew install uv
```

### 의존성 설치 실패
```bash
# 캐시 클리어 후 재설치
rm -rf .venv
uv sync
```

### Ollama 연결 실패
```bash
# Ollama 서비스 상태 확인
brew services list | grep ollama

# Ollama 재시작
brew services restart ollama
```

### 서비스가 시작되지 않을 때
```bash
# 로그 확인
cat logs/stderr.log

# .env 파일 확인
cat .env | grep -v "^#"
```

