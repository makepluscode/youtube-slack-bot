# PRD (Product Requirements Document)
## YouTube Download Agent

---

## 📋 프로젝트 개요

**프로젝트명**: YouTube Download Agent  
**버전**: 1.0.0  
**플랫폼**: macOS (Mac mini)  
**개발 언어**: Python 3.11+  
**패키지 관리자**: uv  
**아이콘**: youtube-agent.png

---

## 🎯 목적

Slack 채널에 공유된 YouTube URL을 자동으로 감지하여 지정된 iCloud Drive 폴더에 다운로드하는 백그라운드 서비스 구축

---

## 📐 시스템 아키텍처

```
┌─────────────────┐
│     Slack       │
│  (Socket Mode)  │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────┐
│      Python Bot (Mac mini)       │
│  ┌────────────────────────────┐  │
│  │    LangChain Agent         │  │
│  │  - ChatPromptTemplate      │  │
│  │  - Ollama LLM (gemma3:4b) │  │
│  │  - URL Extraction Chain    │  │
│  └────────┬───────────────────┘  │
│           │                       │
│           ▼                       │
│  ┌────────────────────────────┐  │
│  │    LangChain Tools         │  │
│  │  - YouTubeDownloadTool     │  │
│  │  - yt-dlp wrapper          │  │
│  └────────┬───────────────────┘  │
└───────────┼───────────────────────┘
            │
            ▼
┌──────────────────────┐
│   iCloud Drive       │
│   /Youtube/          │
└──────────────────────┘
```

---

## 🏗️ 개발 단계 (Development Phases)

### **Phase 1: LangChain Infrastructure** ✅
- LangChain 의존성 설정 (langchain, langchain-ollama, langgraph)
- 프로젝트 디렉토리 구조 생성 (prompts, tools, chains, agents)
- `pyproject.toml` 설정 (uv 패키지 관리자)
- `.env.example`, `.gitignore` 생성
- 환경 설정 관리 구현 (`src/config.py`)

### **Phase 2: Prompt Templates & LLM Setup** 🤖
- ChatPromptTemplate 기반 프롬프트 설계
- SystemMessage + HumanMessage 구조
- URL 추출용 프롬프트 템플릿
- Agent용 프롬프트 템플릿
- Ollama LLM 연동 (gemma3:4b)

### **Phase 3: LangChain Tools Development** 🛠️
- YouTubeDownloadTool 구현 (LangChain Tool 패턴)
- yt-dlp 래퍼를 Tool로 변환
- Tool 입력/출력 스키마 정의
- 에러 처리 및 검증 로직

### **Phase 4: Chains & Agent Workflow** 🔗
- URL 추출 Chain 구현
- LangChain Agent 설정 (React Agent 패턴)
- Tool 실행 워크플로우 구성
- 확장 가능한 구조 설계 (메모리, RAG 준비)

### **Phase 5: Slack Integration** 🔌
- Slack Socket Mode 핸들러
- Agent와 Slack 이벤트 연결
- 메시지 필터링 및 라우팅
- Slack 피드백 메시지 통합

### **Phase 6: Integration & Service Setup** 🚀
- 전체 워크플로우 통합
- 로깅 시스템 설정
- launchd 백그라운드 서비스 설정
- 배포 스크립트 작성

---

## 🔧 기술 스택

### **핵심 기술**
- **Runtime**: Python 3.11+
- **Package Manager**: uv
- **AI Framework**: LangChain + LangGraph
- **LLM**: Ollama (gemma3:4b) via LangChain
- **Downloader**: yt-dlp
- **Slack Integration**: slack-sdk (Socket Mode)
- **Background Service**: launchd (macOS)

### **주요 라이브러리**
```toml
[project]
dependencies = [
    "slack-sdk>=3.27.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.0.0",
    "pydantic-settings>=2.0.0",
    # LangChain ecosystem
    "langchain>=0.1.0",
    "langchain-community>=0.0.20",
    "langchain-ollama>=0.1.0",
    "langgraph>=0.0.20"
]
```

---

## 📂 프로젝트 구조

```
youtube-slack-bot/
├── .env                          # 민감 정보 (Git 제외)
├── .env.example                  # 환경변수 템플릿
├── .gitignore                    # Git 제외 파일
├── pyproject.toml               # uv 프로젝트 설정
├── README.md                     # 프로젝트 문서
├── PRD.md                        # 프로덕트 요구사항 문서
├── src/
│   ├── __init__.py
│   ├── main.py                   # 진입점
│   ├── config.py                 # 설정 관리 (Pydantic Settings)
│   ├── slack_handler.py          # Slack Socket Mode 핸들러
│   ├── prompts/                  # LangChain Prompt Templates
│   │   ├── __init__.py
│   │   └── templates.py          # ChatPromptTemplate 정의
│   ├── tools/                    # LangChain Tools
│   │   ├── __init__.py
│   │   └── youtube_tool.py       # YouTube 다운로드 Tool
│   ├── chains/                   # LangChain Chains
│   │   ├── __init__.py
│   │   └── url_extraction.py     # URL 추출 Chain
│   └── agents/                   # LangChain Agents
│       ├── __init__.py
│       └── youtube_agent.py      # 메인 Agent 워크플로우
├── scripts/
│   ├── setup.sh                  # 초기 설정 스크립트
│   └── install_service.sh        # launchd 서비스 등록
├── services/
│   └── com.makepluscode.youtube-downloader.plist
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

### **2. URL 추출 및 명령 인식 (LangChain)**
- **FR-2.1**: LangChain + Ollama를 사용한 자연어 이해
- **FR-2.2**: ChatPromptTemplate 기반 구조화된 프롬프트
- **FR-2.3**: YouTube URL 패턴 인식
  - `youtube.com/watch?v=*`
  - `youtu.be/*`
  - `youtube.com/shorts/*`
- **FR-2.4**: 다운로드 의도 감지 키워드
  - "다운로드", "받아", "저장", "download", "get"
- **FR-2.5**: JSON 구조화된 응답 파싱

### **3. YouTube 다운로드 (LangChain Tool)**
- **FR-3.1**: LangChain Tool 패턴으로 구현된 YouTubeDownloadTool
- **FR-3.2**: yt-dlp를 사용한 비디오 다운로드
- **FR-3.3**: 최고 품질 자동 선택 (MP4 선호)
- **FR-3.4**: 저장 위치: `~/Library/Mobile Documents/com~apple~CloudDocs/Youtube/`
- **FR-3.5**: 파일명: `{비디오 제목}.{확장자}`
- **FR-3.6**: Tool 입출력 스키마 검증
- **FR-3.7**: 중복 다운로드 방지 (선택 사항)

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
OLLAMA_MODEL=gemma3:4b
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

# 3. 의존성 설치
uv sync

# 4. 환경변수 설정
cp .env.example .env
# .env 파일 편집하여 토큰 입력

# 5. yt-dlp 설치
brew install yt-dlp

# 6. Ollama 설치 및 모델 다운로드
brew install ollama
ollama pull gemma3:4b
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

## 📈 향후 확장 가능성 (LangChain 활용)

### **확장성을 고려한 설계**
현재 구조는 LangChain의 확장 기능을 쉽게 추가할 수 있도록 설계되었습니다.

### **Phase 2 확장 계획**
- [ ] **대화 메모리 추가** (ConversationBufferMemory)
  - 이전 다운로드 기억
  - 맥락 있는 대화 지원
  - 사용자별 선호도 학습

- [ ] **RAG 시스템** (Vector Store + Retrieval)
  - 다운로드 이력 검색
  - 유사 비디오 추천
  - 메타데이터 기반 검색

- [ ] **추가 Tools**
  - Playlist 다운로드 Tool
  - 자막 다운로드 Tool
  - 썸네일 추출 Tool
  - 비디오 메타데이터 검색 Tool

- [ ] **LangGraph 활용**
  - 복잡한 워크플로우 관리
  - 조건부 실행 로직
  - 병렬 다운로드 처리

- [ ] **기타 확장**
  - 다운로드 큐 관리
  - 웹 대시보드 (다운로드 이력)
  - 다중 Slack 워크스페이스 지원
  - 다른 플랫폼 지원 (Vimeo, Twitch 등)
  - 품질 선택 옵션

---

## 🐛 에러 처리

| 에러 시나리오 | 처리 방법 |
|--------------|----------|
| Slack 연결 실패 | 재연결 시도 (최대 3회) |
| LangChain Agent 실패 | Tool 실행 재시도, Fallback 로직 |
| Ollama 응답 없음 | LangChain 재시도 + 에러 메시지 |
| JSON 파싱 실패 | 정규식 Fallback 사용 |
| yt-dlp 다운로드 실패 | Tool 에러 처리, Slack 전송 |
| 디스크 용량 부족 | 경고 메시지 전송 |
| iCloud 동기화 중 | 로컬 임시 폴더 사용 |