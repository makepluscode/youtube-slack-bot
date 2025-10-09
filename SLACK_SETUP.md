# Slack App 설정 가이드

## 🎨 앱 아이콘 설정

### 1. Slack App 관리 페이지 접속
https://api.slack.com/apps

### 2. YouTube Download Agent 앱 선택

### 3. 아이콘 업로드
1. 왼쪽 메뉴 → **"Basic Information"**
2. "Display Information" 섹션 찾기
3. "App Icon & Preview" 섹션에서:
   - **"Upload Image"** 클릭
   - `youtube-agent.png` 파일 선택
   - 이미지 크기: 1024x1024 PNG
4. **"Save Changes"** 클릭

### 4. 앱 이름 확인/변경
- **App Name**: `YouTube Download Agent`
- **Short Description**: AI-powered agent for YouTube downloads
- **Background Color**: `#FF0000` (YouTube Red) 또는 원하는 색상

## ✅ 현재 설정 상태

### Required OAuth Scopes (Bot Token)
- ✅ `channels:history` - 채널 메시지 읽기
- ✅ `channels:read` - 채널 정보 읽기
- ✅ `chat:write` - 메시지 전송
- ✅ `groups:history` - 비공개 채널 메시지
- ✅ `im:history` - DM 메시지
- ✅ `mpim:history` - 그룹 DM 메시지

### Socket Mode
- ✅ Enabled
- ✅ App-Level Token 생성됨
- Scopes:
  - `connections:write`
  - `authorizations:read`

### Event Subscriptions
- ✅ Enabled
- Bot Events:
  - `message.channels`

## 📱 앱 정보 표시

### Display Information
```
App Name: YouTube Download Agent
Short Description: AI-powered YouTube download agent
Long Description:
LangChain 기반 AI Agent로 Slack에서 공유된 YouTube 영상을 
자동으로 iCloud Drive에 다운로드합니다.

- Ollama (gemma3:4b) 자연어 처리
- 한글 명령 지원
- 고품질 MP4 다운로드
- iCloud Drive 자동 동기화
```

### App Icon
- **파일**: `youtube-agent.png`
- **크기**: 1024x1024
- **형식**: PNG
- **위치**: 프로젝트 루트

## 🚀 배포 체크리스트

- [x] Socket Mode 활성화
- [x] Bot Token Scopes 설정
- [x] Event Subscriptions 설정
- [ ] 앱 아이콘 업로드 (`youtube-agent.png`)
- [ ] 앱 이름 확인 (YouTube Download Agent)
- [ ] 워크스페이스에 설치
- [ ] 테스트 채널에 봇 초대

## 💡 사용 방법

### Agent 초대
```
/invite @YouTube Download Agent
```

### 다운로드 요청
```
https://www.youtube.com/watch?v=VIDEO_ID 다운로드해줘
```

### 자연어 명령
- "다운로드해줘"
- "받아줘"
- "저장해줘"
- "download"
- "get"

