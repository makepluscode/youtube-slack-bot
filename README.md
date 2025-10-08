# Slack YouTube Downloader Bot (LangChain Edition)

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/🦜_LangChain-Powered-green.svg)](https://python.langchain.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Slack 채널에 공유된 YouTube URL을 자동으로 감지하여 지정된 iCloud Drive 폴더에 다운로드하는 **LangChain 기반 AI Agent 시스템**입니다.

## 🎯 주요 기능

- ✅ Slack Socket Mode를 통한 실시간 메시지 모니터링
- 🦜 **LangChain Agent 기반 워크플로우 orchestration**
- 🤖 **ChatPromptTemplate을 활용한 구조화된 프롬프트**
- 🔗 **LangChain Tools 패턴으로 구현된 모듈식 구조**
- 🧠 Ollama (gemma3:4b) LLM을 활용한 자연어 이해 및 URL 추출
- 📥 yt-dlp를 사용한 고품질 YouTube 비디오 다운로드
- ☁️ iCloud Drive 자동 동기화
- 🔄 macOS launchd를 통한 백그라운드 서비스 실행
- 📝 상세한 로깅 및 Slack 피드백 메시지
- 🚀 **확장 가능한 구조** (메모리, RAG, 추가 Tools 등)

## 📋 사전 요구사항

### 시스템 요구사항
- macOS (Mac mini 또는 다른 macOS 기기)
- Python 3.11 이상
- Homebrew 패키지 관리자

### 필수 소프트웨어
1. **uv** - Python 패키지 관리자
2. **yt-dlp** - YouTube 다운로더
3. **Ollama** - 로컬 LLM 실행 환경
4. **LangChain** - AI Agent 프레임워크 (자동 설치됨)

### Slack 설정
Slack App을 생성하고 다음 권한이 필요합니다:

#### Bot Token Scopes
- `channels:history` - 채널 메시지 읽기
- `channels:read` - 채널 정보 읽기
- `chat:write` - 메시지 전송
- `groups:history` - 비공개 채널 메시지 읽기
- `im:history` - DM 메시지 읽기
- `mpim:history` - 그룹 DM 메시지 읽기

#### Socket Mode
- Socket Mode를 활성화하고 App-Level Token 생성
- Event Subscriptions에서 `message.channels` 이벤트 구독

## 🚀 설치 방법

### 1. 저장소 클론 및 이동

```bash
git clone <repository-url>
cd youtube-slack-bot
```

### 2. 필수 소프트웨어 설치

```bash
# uv 설치
brew install uv

# yt-dlp 설치
brew install yt-dlp

# Ollama 설치
brew install ollama

# Ollama 모델 다운로드
ollama pull gemma3:4b
```

### 3. Python 환경 설정

```bash
# uv로 의존성 설치 (자동으로 가상환경 생성)
uv sync

# 또는 직접 설치
uv pip install -e .
```

### 4. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env

# .env 파일 편집 (필수!)
nano .env
```

`.env` 파일에 다음 정보를 입력하세요:

```bash
# Slack Configuration
SLACK_BOT_TOKEN=xoxb-your-actual-bot-token
SLACK_APP_TOKEN=xapp-your-actual-app-token

# Ollama Configuration
OLLAMA_MODEL=gemma3:4b
OLLAMA_HOST=http://localhost:11434

# Download Configuration
DOWNLOAD_DIR=~/Library/Mobile Documents/com~apple~CloudDocs/Youtube

# Optional: Monitor specific channels only
SLACK_CHANNELS=C01234567,C98765432

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

### 5. 다운로드 디렉토리 생성

```bash
# iCloud Drive 경로에 Youtube 폴더 생성
mkdir -p ~/Library/Mobile\ Documents/com~apple~CloudDocs/Youtube
```

## 💻 사용 방법

### 개발/테스트 모드로 실행

```bash
# uv run으로 직접 실행 (가상환경 자동 활성화)
uv run python -m src.main

# 또는 정의된 스크립트 사용
uv run youtube-bot
```

### 백그라운드 서비스로 실행

```bash
# 서비스 설치
./scripts/install_service.sh

# 서비스 시작
launchctl load ~/Library/LaunchAgents/com.makepluscode.youtube-downloader.plist

# 서비스 중지
launchctl unload ~/Library/LaunchAgents/com.makepluscode.youtube-downloader.plist

# 서비스 상태 확인
launchctl list | grep youtube-downloader
```

## 📝 사용 예시

Slack 채널에서 다음과 같이 메시지를 보내면 자동으로 다운로드됩니다:

### 기본 사용법

```
https://www.youtube.com/watch?v=dQw4w9WgXcQ 다운로드해줘
```

### 자연어 명령

```
이거 받아줘: https://youtu.be/dQw4w9WgXcQ
```

```
https://www.youtube.com/shorts/abc123 저장
```

### 여러 URL 동시 다운로드

```
이 영상들 다운로드:
https://www.youtube.com/watch?v=video1
https://www.youtube.com/watch?v=video2
https://www.youtube.com/watch?v=video3
```

### Bot 응답 예시

✅ **다운로드 시작**
```
⏳ Downloading: Video Title (4:32)
https://www.youtube.com/watch?v=...
```

✅ **다운로드 완료**
```
✅ Download complete!
Video Title
📁 Saved to: Video Title.mp4
```

❌ **다운로드 실패**
```
❌ Download failed: Error message
https://www.youtube.com/watch?v=...
```

## 📂 프로젝트 구조 (LangChain 기반)

```
youtube-slack-bot/
├── .env                          # 환경 변수 (Git 제외)
├── .env.example                  # 환경 변수 템플릿
├── .gitignore                    # Git 제외 파일
├── pyproject.toml               # 프로젝트 설정 (LangChain 포함)
├── README.md                     # 이 파일
├── PRD.md                        # 프로덕트 요구사항 문서
├── src/
│   ├── __init__.py
│   ├── main.py                   # 진입점 (Agent 오케스트레이션)
│   ├── config.py                 # 설정 관리 (Pydantic Settings)
│   ├── slack_handler.py          # Slack Socket Mode 핸들러
│   ├── prompts/                  # 🦜 LangChain Prompts
│   │   ├── __init__.py
│   │   └── templates.py          # ChatPromptTemplate 정의
│   ├── tools/                    # 🛠️ LangChain Tools
│   │   ├── __init__.py
│   │   └── youtube_tool.py       # YouTubeDownloadTool
│   ├── chains/                   # 🔗 LangChain Chains
│   │   ├── __init__.py
│   │   └── url_extraction.py     # URL 추출 Chain
│   └── agents/                   # 🤖 LangChain Agents
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

### 🏗️ LangChain 아키텍처

```
Slack Message
     ↓
YouTubeAgent (agents/youtube_agent.py)
     ↓
URLExtractionChain (chains/url_extraction.py)
     ├── ChatPromptTemplate (prompts/templates.py)
     ├── Ollama LLM (gemma3:4b)
     └── Output: {urls: [...], download_intent: bool}
     ↓
YouTubeDownloadTool (tools/youtube_tool.py)
     ├── Input Validation (Pydantic Schema)
     ├── yt-dlp Execution
     └── Output: {success, message, title, file_path}
     ↓
Slack Feedback Message
```

## 🔧 문제 해결

### Ollama 연결 실패

```bash
# Ollama가 실행 중인지 확인
ollama list

# Ollama 서비스 시작
brew services start ollama

# 모델이 다운로드되어 있는지 확인
ollama list | grep gemma3
```

### Slack 연결 실패

- `.env` 파일의 토큰이 올바른지 확인
- Slack App에 Socket Mode가 활성화되어 있는지 확인
- Bot이 채널에 추가되어 있는지 확인

### yt-dlp 다운로드 실패

```bash
# yt-dlp 업데이트
brew upgrade yt-dlp

# 또는 pip로 업데이트
pip install -U yt-dlp
```

### iCloud Drive 동기화 문제

- iCloud Drive가 macOS에서 활성화되어 있는지 확인
- 충분한 저장 공간이 있는지 확인
- 로컬 임시 폴더로 변경 가능: `DOWNLOAD_DIR=~/Downloads/Youtube`

## 📊 로그 확인

```bash
# 실시간 로그 모니터링
tail -f logs/app.log

# 최근 100줄 확인
tail -n 100 logs/app.log

# 에러 로그만 필터링
grep ERROR logs/app.log
```

## 🛠️ 개발 가이드

### LangChain 컴포넌트 구조

이 프로젝트는 LangChain의 모듈식 구조를 활용합니다:

1. **Prompts** (`src/prompts/`): ChatPromptTemplate을 사용한 구조화된 프롬프트
2. **Tools** (`src/tools/`): BaseTool을 상속한 재사용 가능한 도구
3. **Chains** (`src/chains/`): LLM + Prompt + Parser의 조합
4. **Agents** (`src/agents/`): 전체 워크플로우를 관리하는 Agent

### 새로운 기능 추가 방법

#### 1. 새로운 Tool 추가
```python
# src/tools/my_new_tool.py
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    param: str = Field(description="Tool parameter")

class MyNewTool(BaseTool):
    name = "my_new_tool"
    description = "What this tool does"
    args_schema = MyToolInput
    
    def _run(self, param: str) -> str:
        # Tool logic here
        return result
```

#### 2. Agent에 Tool 추가
```python
# src/agents/youtube_agent.py
from ..tools.my_new_tool import MyNewTool

self.tools = get_youtube_tools(settings.download_dir) + [
    MyNewTool()
]
```

#### 3. 메모리 추가 (향후 확장)
```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(memory_key="chat_history")
```

### 개발 환경 설정

```bash
# 개발 의존성 포함 설치
uv sync --extra dev

# 코드 포매팅
uv run black src/

# 린팅
uv run ruff check src/

# 테스트 실행
uv run pytest
```

### 커밋 메시지 규칙

이 프로젝트는 Conventional Commits 스타일을 따릅니다:

```
feat: Add new feature
fix: Fix bug
docs: Update documentation
chore: Update dependencies
```

## 📈 향후 개발 계획 (LangChain 활용)

### Phase 2: 고급 LangChain 기능

#### 🧠 대화 메모리
- [ ] **ConversationBufferMemory** 추가
  - 이전 다운로드 기억
  - 사용자별 대화 컨텍스트
  - "방금 받은 비디오" 같은 참조 이해

#### 🔍 RAG 시스템
- [ ] **Vector Store 통합** (Chroma, FAISS)
  - 다운로드 이력 임베딩
  - 유사 비디오 검색
  - "지난주에 받은 요리 영상 찾아줘"

#### 🛠️ 추가 Tools
- [ ] **PlaylistDownloadTool** - 재생목록 전체 다운로드
- [ ] **SubtitleDownloadTool** - 자막 자동 다운로드
- [ ] **ThumbnailExtractTool** - 썸네일 추출
- [ ] **MetadataSearchTool** - 비디오 메타데이터 검색
- [ ] **QualitySelectionTool** - 품질 선택 (1080p, 720p 등)

#### 🔀 LangGraph 워크플로우
- [ ] **복잡한 워크플로우 관리**
  - 조건부 실행 (파일 크기에 따른 처리)
  - 병렬 다운로드 처리
  - 에러 복구 플로우

#### 🌐 멀티모달 확장
- [ ] 다른 플랫폼 지원 Tools
  - Vimeo, Twitch, Instagram 등
- [ ] 웹 대시보드 (다운로드 이력)
- [ ] 다중 Slack 워크스페이스 지원

## 📄 라이센스

MIT License

## 🤝 기여

이슈와 풀 리퀘스트는 언제나 환영합니다!

## 👤 작성자

makepluscode

---

**Note**: 이 봇은 개인적인 용도로 설계되었으며, YouTube의 서비스 약관을 준수해야 합니다.
