"""GitHub MCP 도구."""

from fastmcp import FastMCP

from jarvis.auth.github_auth import get_github_client
from jarvis.utils.formatting import (
    format_repo,
    format_repo_list,
    format_issue,
    format_issue_list,
    format_pull_request,
    format_pull_request_list,
    format_notification_list,
)


def _take(paginated_list, max_results: int) -> list:
    """PaginatedList에서 최대 max_results개를 안전하게 가져온다."""
    items = []
    for item in paginated_list:
        items.append(item)
        if len(items) >= max_results:
            break
    return items


def register_github_tools(mcp: FastMCP) -> None:
    """GitHub 관련 MCP 도구를 서버에 등록한다."""

    @mcp.tool()
    def list_repos(
        type: str = "owner",
        sort: str = "updated",
        max_results: int = 30,
    ) -> str:
        """내 GitHub 저장소 목록을 조회한다.

        Args:
            type: 저장소 유형 (owner, all, public, private, member)
            sort: 정렬 기준 (created, updated, pushed, full_name)
            max_results: 최대 결과 수
        """
        g = get_github_client()
        user = g.get_user()
        repos = _take(user.get_repos(type=type, sort=sort), max_results)

        if not repos:
            return "저장소가 없습니다."

        return format_repo_list(repos)

    @mcp.tool()
    def get_repo(owner_repo: str) -> str:
        """저장소 상세 정보를 조회한다.

        Args:
            owner_repo: 저장소 전체 이름 (예: owner/repo)
        """
        g = get_github_client()
        repo = g.get_repo(owner_repo)
        return format_repo(repo)

    @mcp.tool()
    def list_issues(
        owner_repo: str,
        state: str = "open",
        labels: str | None = None,
        max_results: int = 30,
    ) -> str:
        """이슈 목록을 조회한다.

        Args:
            owner_repo: 저장소 전체 이름 (예: owner/repo)
            state: 상태 필터 (open, closed, all)
            labels: 라벨 필터 (쉼표 구분)
            max_results: 최대 결과 수
        """
        g = get_github_client()
        repo = g.get_repo(owner_repo)

        kwargs = {"state": state}
        if labels:
            label_list = [l.strip() for l in labels.split(",")]
            kwargs["labels"] = [repo.get_label(name) for name in label_list]

        issues = _take(repo.get_issues(**kwargs), max_results)
        # PR은 제외 (GitHub API는 이슈에 PR도 포함)
        issues = [i for i in issues if not i.pull_request]

        if not issues:
            return f"{owner_repo}에 {state} 상태의 이슈가 없습니다."

        return format_issue_list(issues)

    @mcp.tool()
    def get_issue(owner_repo: str, issue_number: int) -> str:
        """이슈 상세 정보를 조회한다.

        Args:
            owner_repo: 저장소 전체 이름 (예: owner/repo)
            issue_number: 이슈 번호
        """
        g = get_github_client()
        repo = g.get_repo(owner_repo)
        issue = repo.get_issue(number=issue_number)
        return format_issue(issue, detailed=True)

    @mcp.tool()
    def create_issue(
        owner_repo: str,
        title: str,
        body: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
    ) -> str:
        """새 이슈를 생성한다.

        Args:
            owner_repo: 저장소 전체 이름 (예: owner/repo)
            title: 이슈 제목
            body: 이슈 본문
            labels: 라벨 목록
            assignees: 담당자 목록
        """
        g = get_github_client()
        repo = g.get_repo(owner_repo)

        kwargs = {"title": title}
        if body:
            kwargs["body"] = body
        if labels:
            kwargs["labels"] = labels
        if assignees:
            kwargs["assignees"] = assignees

        issue = repo.create_issue(**kwargs)
        return f"이슈 생성 완료: #{issue.number} {issue.title}\nURL: {issue.html_url}"

    @mcp.tool()
    def update_issue(
        owner_repo: str,
        issue_number: int,
        title: str | None = None,
        body: str | None = None,
        state: str | None = None,
        labels: list[str] | None = None,
        assignees: list[str] | None = None,
    ) -> str:
        """이슈를 수정한다.

        Args:
            owner_repo: 저장소 전체 이름 (예: owner/repo)
            issue_number: 이슈 번호
            title: 새 제목
            body: 새 본문
            state: 새 상태 (open, closed)
            labels: 새 라벨 목록
            assignees: 새 담당자 목록
        """
        g = get_github_client()
        repo = g.get_repo(owner_repo)
        issue = repo.get_issue(number=issue_number)

        kwargs = {}
        if title is not None:
            kwargs["title"] = title
        if body is not None:
            kwargs["body"] = body
        if state is not None:
            kwargs["state"] = state
        if labels is not None:
            kwargs["labels"] = labels
        if assignees is not None:
            kwargs["assignees"] = assignees

        issue.edit(**kwargs)
        return f"이슈 수정 완료: #{issue.number} {issue.title}"

    @mcp.tool()
    def list_pull_requests(
        owner_repo: str,
        state: str = "open",
        sort: str = "created",
        max_results: int = 30,
    ) -> str:
        """PR 목록을 조회한다.

        Args:
            owner_repo: 저장소 전체 이름 (예: owner/repo)
            state: 상태 필터 (open, closed, all)
            sort: 정렬 기준 (created, updated, popularity, long-running)
            max_results: 최대 결과 수
        """
        g = get_github_client()
        repo = g.get_repo(owner_repo)
        prs = _take(repo.get_pulls(state=state, sort=sort), max_results)

        if not prs:
            return f"{owner_repo}에 {state} 상태의 PR이 없습니다."

        return format_pull_request_list(prs)

    @mcp.tool()
    def get_pull_request(owner_repo: str, pr_number: int) -> str:
        """PR 상세 정보를 조회한다.

        Args:
            owner_repo: 저장소 전체 이름 (예: owner/repo)
            pr_number: PR 번호
        """
        g = get_github_client()
        repo = g.get_repo(owner_repo)
        pr = repo.get_pull(number=pr_number)
        return format_pull_request(pr, detailed=True)

    @mcp.tool()
    def create_pull_request(
        owner_repo: str,
        title: str,
        head: str,
        base: str,
        body: str | None = None,
    ) -> str:
        """새 PR을 생성한다.

        Args:
            owner_repo: 저장소 전체 이름 (예: owner/repo)
            title: PR 제목
            head: 소스 브랜치
            base: 타겟 브랜치
            body: PR 설명
        """
        g = get_github_client()
        repo = g.get_repo(owner_repo)

        kwargs = {"title": title, "head": head, "base": base}
        if body:
            kwargs["body"] = body

        pr = repo.create_pull(**kwargs)
        return f"PR 생성 완료: #{pr.number} {pr.title}\nURL: {pr.html_url}"

    @mcp.tool()
    def merge_pull_request(
        owner_repo: str,
        pr_number: int,
        merge_method: str = "merge",
        commit_message: str | None = None,
    ) -> str:
        """PR을 머지한다.

        Args:
            owner_repo: 저장소 전체 이름 (예: owner/repo)
            pr_number: PR 번호
            merge_method: 머지 방식 (merge, squash, rebase)
            commit_message: 커밋 메시지
        """
        g = get_github_client()
        repo = g.get_repo(owner_repo)
        pr = repo.get_pull(number=pr_number)

        kwargs = {"merge_method": merge_method}
        if commit_message:
            kwargs["commit_message"] = commit_message

        result = pr.merge(**kwargs)

        if result.merged:
            return f"PR #{pr_number} 머지 완료: {result.message}"
        else:
            return f"PR #{pr_number} 머지 실패: {result.message}"

    @mcp.tool()
    def list_notifications(
        all: bool = False,
        participating: bool = False,
        max_results: int = 30,
    ) -> str:
        """GitHub 알림을 조회한다.

        Args:
            all: 읽은 알림도 포함할지 여부
            participating: 참여 중인 알림만 조회할지 여부
            max_results: 최대 결과 수
        """
        g = get_github_client()
        user = g.get_user()
        notifications = _take(
            user.get_notifications(all=all, participating=participating), max_results
        )

        return format_notification_list(notifications)

    @mcp.tool()
    def mark_notifications_read() -> str:
        """모든 알림을 읽음 처리한다."""
        g = get_github_client()
        g.get_user().mark_notifications_as_read()
        return "모든 알림을 읽음 처리했습니다."
