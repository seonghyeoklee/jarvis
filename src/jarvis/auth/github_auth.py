"""GitHub PAT 기반 인증 모듈."""

import os

from github import Github


def get_github_client() -> Github:
    """GitHub 클라이언트를 반환한다.

    환경변수 GITHUB_TOKEN에서 Personal Access Token을 읽어 인증한다.
    """
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError(
            "GITHUB_TOKEN 환경변수가 설정되지 않았습니다.\n"
            "GitHub Personal Access Token을 .env 파일에 설정하세요.\n"
            "예: GITHUB_TOKEN=ghp_xxxxxxxxxxxx"
        )
    return Github(token)
