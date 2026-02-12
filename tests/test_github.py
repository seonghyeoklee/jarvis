"""GitHub 도구 테스트."""

from types import SimpleNamespace
from datetime import datetime

from jarvis.utils.formatting import (
    format_repo,
    format_repo_list,
    format_issue,
    format_issue_list,
    format_pull_request,
    format_pull_request_list,
    format_notification_list,
)


def _make_repo(**kwargs):
    defaults = {
        "full_name": "user/test-repo",
        "description": "테스트 저장소",
        "language": "Python",
        "stargazers_count": 42,
        "forks_count": 5,
        "private": False,
        "default_branch": "main",
        "html_url": "https://github.com/user/test-repo",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_label(name):
    return SimpleNamespace(name=name)


def _make_user(login):
    return SimpleNamespace(login=login)


def _make_issue(**kwargs):
    defaults = {
        "number": 1,
        "title": "테스트 이슈",
        "state": "open",
        "user": _make_user("testuser"),
        "created_at": datetime(2025, 2, 12, 10, 0),
        "labels": [],
        "assignees": [],
        "html_url": "https://github.com/user/repo/issues/1",
        "body": "이슈 본문입니다.",
        "pull_request": None,
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_pr(**kwargs):
    defaults = {
        "number": 10,
        "title": "기능 추가",
        "state": "open",
        "merged": False,
        "user": _make_user("devuser"),
        "head": SimpleNamespace(ref="feature-branch"),
        "base": SimpleNamespace(ref="main"),
        "created_at": datetime(2025, 2, 12, 14, 0),
        "labels": [],
        "additions": 100,
        "deletions": 20,
        "changed_files": 5,
        "html_url": "https://github.com/user/repo/pull/10",
        "body": "PR 설명입니다.",
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


def _make_notification(**kwargs):
    defaults = {
        "subject": SimpleNamespace(type="Issue", title="버그 수정 필요"),
        "repository": SimpleNamespace(full_name="user/repo"),
        "reason": "subscribed",
        "unread": True,
        "updated_at": datetime(2025, 2, 12, 15, 30),
    }
    defaults.update(kwargs)
    return SimpleNamespace(**defaults)


# --- Repo 테스트 ---


def test_format_repo():
    repo = _make_repo()
    result = format_repo(repo)
    assert "user/test-repo" in result
    assert "테스트 저장소" in result
    assert "Python" in result
    assert "42" in result


def test_format_repo_private():
    repo = _make_repo(private=True)
    result = format_repo(repo)
    assert "아니오" in result


def test_format_repo_list():
    repos = [_make_repo(full_name="user/repo1"), _make_repo(full_name="user/repo2")]
    result = format_repo_list(repos)
    assert "총 2개 저장소" in result
    assert "user/repo1" in result
    assert "user/repo2" in result


# --- Issue 테스트 ---


def test_format_issue_basic():
    issue = _make_issue()
    result = format_issue(issue)
    assert "#1" in result
    assert "테스트 이슈" in result
    assert "testuser" in result
    assert "🟢" in result


def test_format_issue_closed():
    issue = _make_issue(state="closed")
    result = format_issue(issue)
    assert "🔴" in result


def test_format_issue_with_labels():
    issue = _make_issue(labels=[_make_label("bug"), _make_label("urgent")])
    result = format_issue(issue)
    assert "bug" in result
    assert "urgent" in result


def test_format_issue_with_assignees():
    issue = _make_issue(assignees=[_make_user("dev1"), _make_user("dev2")])
    result = format_issue(issue)
    assert "dev1" in result
    assert "dev2" in result


def test_format_issue_detailed():
    issue = _make_issue()
    result = format_issue(issue, detailed=True)
    assert "이슈 본문입니다." in result
    assert "github.com" in result


def test_format_issue_list():
    issues = [_make_issue(number=1, title="첫 번째"), _make_issue(number=2, title="두 번째")]
    result = format_issue_list(issues)
    assert "총 2개 이슈" in result
    assert "첫 번째" in result
    assert "두 번째" in result


# --- PR 테스트 ---


def test_format_pull_request_open():
    pr = _make_pr()
    result = format_pull_request(pr)
    assert "🟢" in result
    assert "#10" in result
    assert "기능 추가" in result
    assert "feature-branch" in result
    assert "main" in result


def test_format_pull_request_merged():
    pr = _make_pr(state="closed", merged=True)
    result = format_pull_request(pr)
    assert "🟣" in result
    assert "merged" in result


def test_format_pull_request_closed():
    pr = _make_pr(state="closed", merged=False)
    result = format_pull_request(pr)
    assert "🔴" in result


def test_format_pull_request_detailed():
    pr = _make_pr()
    result = format_pull_request(pr, detailed=True)
    assert "+100" in result
    assert "-20" in result
    assert "5개 파일" in result
    assert "PR 설명입니다." in result


def test_format_pull_request_list():
    prs = [_make_pr(number=1, title="PR 1"), _make_pr(number=2, title="PR 2")]
    result = format_pull_request_list(prs)
    assert "총 2개 PR" in result
    assert "PR 1" in result
    assert "PR 2" in result


# --- Notification 테스트 ---


def test_format_notification_list():
    notifications = [_make_notification(), _make_notification(unread=False)]
    result = format_notification_list(notifications)
    assert "총 2개 알림" in result
    assert "🔵" in result
    assert "⚪" in result
    assert "버그 수정 필요" in result


def test_format_notification_list_empty():
    result = format_notification_list([])
    assert "알림이 없습니다" in result
