# Jarvis - 개인 AI 비서 시스템

자연어로 Google 서비스를 제어하는 개인 AI 비서.
Claude Code + MCP 기반으로 Google Calendar, Gmail부터 시작하여 점진적으로 확장합니다.

## 특징

- Google Calendar 일정 관리 (조회, 생성, 수정, 삭제)
- Gmail 이메일 관리 (조회, 검색, 발송, 라벨 관리)
- FastMCP 기반 도구 서버
- Claude Code에서 자연어로 바로 사용

## 빠른 시작

### 1. 의존성 설치

```bash
cd ~/jarvis
uv sync
```

### 2. Google OAuth 설정

[설정 가이드](docs/05-설정가이드.md)를 참고하여 Google Cloud Console에서 OAuth 자격 증명을 생성합니다.

### 3. 환경변수 설정

```bash
cp .env.example .env
# .env 파일에 Google OAuth 자격 증명 입력
```

### 4. MCP 서버 실행

```bash
uv run jarvis
```

### 5. Claude Code 연결

```bash
claude mcp add jarvis -- uv run --directory ~/jarvis jarvis
```

## 문서

자세한 문서는 [docs/INDEX.md](docs/INDEX.md)를 참고하세요.

## 기술 스택

- **언어**: Python 3.12+
- **MCP 프레임워크**: FastMCP
- **Google API**: google-api-python-client, google-auth-oauthlib
- **패키지 관리**: uv

## 예산

- 월 $10 이내 운영 목표
- Cloudflare Workers 무료 티어 활용 (향후)

## 라이선스

개인 프로젝트
