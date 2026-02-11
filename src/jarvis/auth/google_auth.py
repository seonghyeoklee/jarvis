"""Google OAuth 2.0 인증 관리 모듈."""

import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/gmail.send",
]

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
TOKENS_FILE = PROJECT_ROOT / "tokens.json"
CREDENTIALS_FILE = PROJECT_ROOT / "credentials.json"


def get_credentials() -> Credentials:
    """유효한 Google API 자격 증명을 반환한다.

    저장된 토큰이 있으면 로드하고, 만료되었으면 갱신한다.
    토큰이 없으면 OAuth 인증 흐름을 실행한다.
    """
    creds = None

    if TOKENS_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKENS_FILE), SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        _save_tokens(creds)
    elif not creds or not creds.valid:
        creds = _run_auth_flow()
        _save_tokens(creds)

    return creds


def _get_credentials_file() -> Path:
    """credentials.json 파일 경로를 반환한다."""
    env_path = os.getenv("GOOGLE_CREDENTIALS_FILE")
    if env_path:
        path = Path(env_path)
        if not path.is_absolute():
            path = PROJECT_ROOT / path
        return path
    return CREDENTIALS_FILE


def _run_auth_flow() -> Credentials:
    """OAuth 인증 흐름을 실행하여 새 토큰을 발급받는다."""
    credentials_file = _get_credentials_file()
    if not credentials_file.exists():
        raise FileNotFoundError(
            f"credentials.json 파일을 찾을 수 없습니다: {credentials_file}\n"
            "Google Cloud Console에서 OAuth 자격 증명을 다운로드하세요.\n"
            "자세한 방법: docs/05-설정가이드.md"
        )

    flow = InstalledAppFlow.from_client_secrets_file(str(credentials_file), SCOPES)
    creds = flow.run_local_server(port=0)
    return creds


def _save_tokens(creds: Credentials) -> None:
    """토큰을 파일에 저장한다."""
    TOKENS_FILE.write_text(creds.to_json())


def authenticate():
    """CLI 인증 진입점. credentials.json으로 OAuth 인증을 수행한다."""
    print("Google OAuth 인증을 시작합니다...")
    print(f"credentials.json 경로: {_get_credentials_file()}")
    try:
        creds = get_credentials()
        print(f"인증 성공! 토큰 저장 위치: {TOKENS_FILE}")
        return creds
    except FileNotFoundError as e:
        print(f"오류: {e}")
        raise SystemExit(1)
