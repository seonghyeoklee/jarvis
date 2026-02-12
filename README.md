# Jarvis

개인 AI 비서를 위한 MCP(Model Context Protocol) 서버입니다.
Claude Code에서 자연어로 Google Calendar, Gmail, GitHub를 제어할 수 있습니다.

```
"오늘 일정 알려줘" → Calendar API 조회 → 결과 반환
"안 읽은 메일 보여줘" → Gmail API 조회 → 결과 반환
"내 GitHub 이슈 목록 보여줘" → GitHub API 조회 → 결과 반환
```

## Features

- **Google Calendar** - 일정 조회, 생성, 수정, 삭제, 검색
- **Gmail** - 메일 조회, 검색, 발송, 답장, 라벨 관리
- **GitHub** - 레포, 이슈, PR, 알림 관리

## Architecture

```
사용자 (자연어)
    │
    ▼
Claude Code (자연어 이해 + 도구 호출)
    │ MCP Protocol
    ▼
Jarvis MCP Server (FastMCP)
    ├── Calendar Tools
    ├── Gmail Tools
    └── GitHub Tools
         │
         ▼
    External APIs
```

## Getting Started

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) 패키지 매니저
- Google Cloud Console OAuth 2.0 자격 증명
- GitHub Personal Access Token

### Installation

```bash
# 레포 클론
git clone https://github.com/seonghyeoklee/jarvis.git
cd jarvis

# 의존성 설치
uv sync
```

### Configuration

```bash
# 환경변수 설정
cp .env.example .env
```

`.env` 파일에 아래 값을 입력합니다:

| 변수 | 설명 |
|------|------|
| `GOOGLE_CLIENT_ID` | Google OAuth 클라이언트 ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth 클라이언트 시크릿 |
| `GITHUB_TOKEN` | GitHub Personal Access Token |

Google OAuth 설정 방법은 [설정 가이드](docs/05-설정가이드.md)를 참고하세요.

### Google 인증

```bash
# 최초 1회 Google OAuth 인증
uv run jarvis-auth
```

### Run

```bash
# MCP 서버 실행
uv run jarvis
```

### Claude Code 연동

```bash
# Claude Code에 MCP 서버 등록
claude mcp add jarvis -- uv run --directory /path/to/jarvis jarvis
```

## Tech Stack

| 구분 | 기술 |
|------|------|
| Language | Python 3.12+ |
| MCP Framework | [FastMCP](https://github.com/jlowin/fastmcp) |
| Google API | google-api-python-client, google-auth-oauthlib |
| GitHub API | PyGithub |
| Package Manager | uv |

## Project Structure

```
jarvis/
├── src/jarvis/
│   ├── server.py              # MCP 서버 엔트리포인트
│   ├── auth/
│   │   ├── google_auth.py     # Google OAuth 인증
│   │   └── github_auth.py     # GitHub PAT 인증
│   ├── tools/
│   │   ├── calendar.py        # Calendar 도구
│   │   ├── gmail.py           # Gmail 도구
│   │   └── github.py          # GitHub 도구
│   └── utils/
│       └── formatting.py      # 출력 포맷팅
├── tests/
├── docs/
├── pyproject.toml
└── .env.example
```

## Roadmap

- [x] Google Calendar 연동
- [x] Gmail 연동
- [x] GitHub 연동
- [ ] Google Drive + Sheets 연동
- [ ] Slack / Telegram 채팅 인터페이스
- [ ] Cron 기반 자동화 (일정 브리핑, 메일 알림)

자세한 로드맵은 [docs/02-로드맵.md](docs/02-로드맵.md)를 참고하세요.

## Contributing

기여를 환영합니다! 아래 방법으로 참여할 수 있습니다.

### 새로운 MCP 도구 추가

1. `src/jarvis/tools/`에 새 도구 모듈 생성
2. `src/jarvis/server.py`에 도구 등록
3. 테스트 작성

### 기여 방법

1. 이 레포를 Fork 합니다
2. Feature 브랜치를 생성합니다 (`git checkout -b feature/amazing-tool`)
3. 변경 사항을 커밋합니다 (`git commit -m 'Add amazing tool'`)
4. 브랜치에 Push 합니다 (`git push origin feature/amazing-tool`)
5. Pull Request를 생성합니다

### 기여 아이디어

- 새로운 서비스 연동 (Notion, Slack, Jira 등)
- 기존 도구 개선 및 버그 수정
- 문서 개선
- 테스트 추가

## License

MIT License - [LICENSE](LICENSE) 파일을 참고하세요.
