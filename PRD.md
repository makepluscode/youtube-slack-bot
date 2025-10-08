# PRD (Product Requirements Document)
## Slack YouTube Downloader Bot

---

## 📋 프로젝트 개요

**프로젝트명**: Slack YouTube Auto Downloader  
**버전**: 1.0.0  
**플랫폼**: macOS (Mac mini)  
**개발 언어**: Python 3.11+  
**패키지 관리자**: uv

---

## 🎯 목적

Slack 채널에 공유된 YouTube URL을 자동으로 감지하여 지정된 iCloud Drive 폴더에 다운로드하는 백그라운드 서비스 구축

---

## 📐 시스템 아키텍처

```
┌─────────────┐
│   Slack     │
│  makepluscode│ 
└──────┬──────┘
       │
       │ Socket Mode
       ▼
┌─────────────────┐
│  Python Bot     │
│  (Mac mini)     │
│  - Ollama       │
│  - yt-dlp       │
└────────┬────────┘
         │
         ▼
┌──────────────────┐
│  iCloudDrive     │
│  /Youtube/       │
└──────────────────┘
```

---

## 🔧 기술 스택

### **핵심 기술**
- **Runtime**: Python 3.11+
- **Package Manager**: uv
- **LLM**: Ollama (llama3.2 또는 그 이상)
- **Downloader**: yt-dlp
- **Slack Integration**: slack-sdk (Socket Mode)
- **Background Service**: launchd (macOS)

### **주요 라이브러리**
```toml
[project]
dependencies = [
    "slack-sdk>=3.27.0",
    "ollama>=0.1.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0"
]
```

---

## 📂 프로젝트 구조

```
slack-youtube-downloader/
├── .env                          # 민감 정보 (Git 제외)
├── .env.example                  # 환경변수 템플릿
├── .gitignore                    # Git 제외 파일
├── pyproject.toml               # uv 프로젝트 설정
├── README.md                     # 프로젝트 문서
├── requirements.txt              # 의존성 (uv로 생성)
├── src/
│   ├── __init__.py
│   ├── main.py                   # 진입점
│   ├── config.py                 # 설정 관리
│   ├── slack_handler.py          # Slack 이벤트 처리
│   ├── ollama_handler.py         # URL 추출 (Ollama)
│   └── downloader.py             # YouTube 다운로드
├── scripts/
│   ├── setup.sh                  # 초기 설정 스크립트
│   └── install_service.sh        # launchd 서비스 등록
├── services/
│   └── com.makepluscode.youtube-downloader.plist  # launchd 설정
└── logs/
    └── app.log                   # 애플리케이션 로그
```

---

## ⚙️ 기능 요구사항

### **1. Slack 메시지 모니터링**
- **FR-1.1**: Slack workspace `makepluscode.slack.com` 연결
- **FR-1.2**: 실시간 메시지 수신 (Socket Mode 사용)
- **FR-1.3**: Bot 자신의 메시지는 무시
- **FR-1.4**: 특정 채널만 모니터링 (설정 가능)

### **2. URL 추출 및 명령 인식**
- **FR-2.1**: Ollama를 사용한 자연어 이해
- **FR-2.2**: YouTube URL 패턴 인식
  - `youtube.com/watch?v=*`
  - `youtu.be/*`
  - `youtube.com/shorts/*`
- **FR-2.3**: 다운로드 의도 감지 키워드
  - "다운로드", "받아", "저장", "download", "get"

### **3. YouTube 다운로드**
- **FR-3.1**: yt-dlp를 사용한 비디오 다운로드
- **FR-3.2**: 최고 품질 자동 선택 (MP4 선호)
- **FR-3.3**: 저장 위치: `~/Library/Mobile Documents/com~apple~CloudDocs/Youtube/`
- **FR-3.4**: 파일명: `{비디오 제목}.{확장자}`
- **FR-3.5**: 중복 다운로드 방지 (선택 사항)

### **4. 피드백 및 로깅**
- **FR-4.1**: 다운로드 시작 시 Slack 메시지 전송
- **FR-4.2**: 다운로드 완료/실패 시 Slack 메시지 전송
- **FR-4.3**: 로컬 로그 파일 생성 (`logs/app.log`)
- **FR-4.4**: 에러 상황 상세 로깅

### **5. 백그라운드 서비스**
- **FR-5.1**: macOS launchd를 통한 자동 시작
- **FR-5.2**: 시스템 재부팅 후 자동 재시작
- **FR-5.3**: 프로세스 크래시 시 자동 재시작
- **FR-5.4**: 서비스 상태 모니터링 (선택 사항)

---

## 🔐 보안 요구사항

### **SR-1: 민감 정보 관리**
- **SR-1.1**: 모든 인증 정보는 `.env` 파일에 저장
- **SR-1.2**: `.env` 파일은 Git에 커밋하지 않음
- **SR-1.3**: `.env.example` 템플릿 제공
- **SR-1.4**: 파일 권한: `.env`는 `600` (소유자만 읽기/쓰기)

### **SR-2: 필수 환경변수**
```bash
# Slack 인증
SLACK_BOT_TOKEN=xoxb-*****
SLACK_APP_TOKEN=xapp-*****

# Ollama 설정
OLLAMA_MODEL=llama3.2
OLLAMA_HOST=http://localhost:11434

# 다운로드 설정
DOWNLOAD_DIR=~/Library/Mobile... (iCloud의 Youtube 디렉토리)
```

---

## 📝 .gitignore 요구사항

```gitignore
# 환경변수 및 민감 정보
.env
.env.local
*.key
*.pem

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# uv
.uv/
uv.lock

# 로그
logs/
*.log

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# macOS
.DS_Store
.AppleDouble
.LSOverride

# 테스트
.pytest_cache/
.coverage
htmlcov/

# 다운로드된 파일 (선택사항)
downloads/
```

---

## 🚀 설치 및 배포

### **1. 초기 설정**
```bash
# 1. 저장소 클론
git clone <repository-url>
cd slack-youtube-downloader

# 2. uv 설치 (Homebrew)
brew install uv

# 3. 프로젝트 초기화
uv venv
source .venv/bin/activate

# 4. 의존성 설치
uv pip install -e .

# 5. 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 토큰 입력

# 6. yt-dlp 설치
brew install yt-dlp

# 7. Ollama 설치 및 모델 다운로드
brew install ollama
ollama pull llama3.2
```

### **2. 백그라운드 서비스 등록**
```bash
# launchd 서비스 설치
./scripts/install_service.sh

# 서비스 시작
launchctl load ~/Library/LaunchAgents/com.makepluscode.youtube-downloader.plist

# 서비스 상태 확인
launchctl list | grep youtube-downloader
```

---

## 🧪 테스트 시나리오

### **TS-1: 기본 다운로드**
- **입력**: "https://www.youtube.com/watch?v=w7vqXL4PWEE 를 다운로드 해."
- **예상 결과**: 
  - Bot 응답: "⏳ 다운로드 시작: ..."
  - 파일 저장: `~/Library/.../Youtube/{제목}.mp4`
  - Bot 응답: "✅ 다운로드 완료"

### **TS-2: 자연어 명령**
- **입력**: "이거 받아줘 https://youtu.be/abc123"
- **예상 결과**: URL 추출 및 다운로드

### **TS-3: 여러 URL**
- **입력**: 3개의 URL이 포함된 메시지
- **예상 결과**: 순차적으로 3개 다운로드

### **TS-4: 잘못된 URL**
- **입력**: "https://example.com/video"
- **예상 결과**: "❌ YouTube URL이 아닙니다"

### **TS-5: 서비스 재시작**
- **조건**: 시스템 재부팅
- **예상 결과**: 자동으로 서비스 재시작

---

## 📊 성능 요구사항

- **PR-1**: 메시지 수신 후 5초 이내 응답
- **PR-2**: Ollama URL 추출 3초 이내
- **PR-3**: 메모리 사용량 < 500MB
- **PR-4**: CPU 사용률 (대기 시) < 5%

---

## 📈 향후 확장 가능성

- [ ] 다운로드 큐 관리 (동시 다운로드 제한)
- [ ] 웹 대시보드 (다운로드 이력)
- [ ] 다중 Slack 워크스페이스 지원
- [ ] 다른 플랫폼 지원 (Vimeo, Twitch 등)
- [ ] 자막 자동 다운로드
- [ ] 품질 선택 옵션 (1080p, 720p, 등)

---

## 🐛 에러 처리

| 에러 시나리오 | 처리 방법 |
|--------------|----------|
| Slack 연결 실패 | 재연결 시도 (최대 3회) |
| Ollama 응답 없음 | Fallback: 정규식 사용 |
| yt-dlp 다운로드 실패 | 에러 메시지 Slack 전송 |
| 디스크 용량 부족 | 경고 메시지 전송 |
| iCloud 동기화 중 | 로컬 임시 폴더 사용 |