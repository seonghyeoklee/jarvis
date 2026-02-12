"""응답 포맷팅 유틸리티."""

import base64


def format_event(event: dict, detailed: bool = False) -> str:
    """캘린더 이벤트를 포맷팅한다."""
    summary = event.get("summary", "(제목 없음)")
    start = event.get("start", {})
    end = event.get("end", {})

    start_time = start.get("dateTime", start.get("date", ""))
    end_time = end.get("dateTime", end.get("date", ""))

    lines = [f"📅 {summary}", f"  시간: {start_time} ~ {end_time}"]

    location = event.get("location")
    if location:
        lines.append(f"  장소: {location}")

    if detailed:
        lines.append(f"  ID: {event.get('id', '')}")

        description = event.get("description")
        if description:
            lines.append(f"  설명: {description}")

        attendees = event.get("attendees", [])
        if attendees:
            names = [a.get("email", "") for a in attendees]
            lines.append(f"  참석자: {', '.join(names)}")

        link = event.get("htmlLink")
        if link:
            lines.append(f"  링크: {link}")

    return "\n".join(lines)


def format_event_list(events: list[dict]) -> str:
    """이벤트 목록을 포맷팅한다."""
    formatted = [format_event(e) for e in events]
    return f"총 {len(events)}개 일정:\n\n" + "\n\n".join(formatted)


def format_calendar_list(calendars: list[dict]) -> str:
    """캘린더 목록을 포맷팅한다."""
    lines = [f"총 {len(calendars)}개 캘린더:"]
    for cal in calendars:
        name = cal.get("summary", "(이름 없음)")
        cal_id = cal.get("id", "")
        primary = " (기본)" if cal.get("primary") else ""
        lines.append(f"  - {name}{primary} [{cal_id}]")
    return "\n".join(lines)


def _get_header(message: dict, name: str) -> str:
    """메일 헤더에서 특정 필드를 추출한다."""
    headers = message.get("payload", {}).get("headers", [])
    for header in headers:
        if header["name"].lower() == name.lower():
            return header["value"]
    return ""


def format_message(message: dict) -> str:
    """메일을 상세 포맷팅한다."""
    subject = _get_header(message, "Subject") or "(제목 없음)"
    from_addr = _get_header(message, "From")
    to_addr = _get_header(message, "To")
    date = _get_header(message, "Date")

    lines = [
        f"📧 {subject}",
        f"  보낸 사람: {from_addr}",
        f"  받는 사람: {to_addr}",
        f"  날짜: {date}",
        f"  ID: {message.get('id', '')}",
        f"  스레드 ID: {message.get('threadId', '')}",
    ]

    body = _extract_body(message)
    if body:
        lines.append(f"\n--- 본문 ---\n{body}")

    return "\n".join(lines)


def format_message_list(messages: list[dict]) -> str:
    """메일 목록을 포맷팅한다."""
    lines = [f"총 {len(messages)}개 메일:"]
    for msg in messages:
        subject = _get_header(msg, "Subject") or "(제목 없음)"
        from_addr = _get_header(msg, "From")
        date = _get_header(msg, "Date")
        snippet = msg.get("snippet", "")
        msg_id = msg.get("id", "")

        lines.append(f"\n📧 {subject}")
        lines.append(f"  보낸 사람: {from_addr}")
        lines.append(f"  날짜: {date}")
        lines.append(f"  미리보기: {snippet[:100]}")
        lines.append(f"  ID: {msg_id}")

    return "\n".join(lines)


def format_label_list(labels: list[dict]) -> str:
    """라벨 목록을 포맷팅한다."""
    system_labels = []
    user_labels = []

    for label in labels:
        name = label.get("name", "")
        label_id = label.get("id", "")
        label_type = label.get("type", "")

        entry = f"  - {name} [{label_id}]"
        if label_type == "system":
            system_labels.append(entry)
        else:
            user_labels.append(entry)

    lines = [f"총 {len(labels)}개 라벨:"]
    if system_labels:
        lines.append("\n시스템 라벨:")
        lines.extend(system_labels)
    if user_labels:
        lines.append("\n사용자 라벨:")
        lines.extend(user_labels)

    return "\n".join(lines)


def format_repo(repo) -> str:
    """GitHub 저장소를 포맷팅한다."""
    lines = [
        f"📦 {repo.full_name}",
        f"  설명: {repo.description or '(없음)'}",
        f"  언어: {repo.language or '(없음)'}",
        f"  ⭐ {repo.stargazers_count}  🍴 {repo.forks_count}",
        f"  공개: {'예' if not repo.private else '아니오'}",
        f"  기본 브랜치: {repo.default_branch}",
        f"  URL: {repo.html_url}",
    ]
    return "\n".join(lines)


def format_repo_list(repos: list) -> str:
    """저장소 목록을 포맷팅한다."""
    formatted = [format_repo(r) for r in repos]
    return f"총 {len(repos)}개 저장소:\n\n" + "\n\n".join(formatted)


def format_issue(issue, detailed: bool = False) -> str:
    """GitHub 이슈를 포맷팅한다."""
    state_icon = "🟢" if issue.state == "open" else "🔴"
    lines = [
        f"{state_icon} #{issue.number} {issue.title}",
        f"  상태: {issue.state}",
        f"  작성자: {issue.user.login}",
        f"  생성일: {issue.created_at.strftime('%Y-%m-%d %H:%M')}",
    ]

    if issue.labels:
        label_names = [label.name for label in issue.labels]
        lines.append(f"  라벨: {', '.join(label_names)}")

    if issue.assignees:
        assignee_names = [a.login for a in issue.assignees]
        lines.append(f"  담당자: {', '.join(assignee_names)}")

    if detailed:
        lines.append(f"  URL: {issue.html_url}")
        if issue.body:
            lines.append(f"\n--- 본문 ---\n{issue.body}")

    return "\n".join(lines)


def format_issue_list(issues: list) -> str:
    """이슈 목록을 포맷팅한다."""
    formatted = [format_issue(i) for i in issues]
    return f"총 {len(issues)}개 이슈:\n\n" + "\n\n".join(formatted)


def format_pull_request(pr, detailed: bool = False) -> str:
    """GitHub PR을 포맷팅한다."""
    state_icon = "🟢" if pr.state == "open" else ("🟣" if pr.merged else "🔴")
    lines = [
        f"{state_icon} #{pr.number} {pr.title}",
        f"  상태: {pr.state}{'(merged)' if pr.merged else ''}",
        f"  작성자: {pr.user.login}",
        f"  브랜치: {pr.head.ref} → {pr.base.ref}",
        f"  생성일: {pr.created_at.strftime('%Y-%m-%d %H:%M')}",
    ]

    if pr.labels:
        label_names = [label.name for label in pr.labels]
        lines.append(f"  라벨: {', '.join(label_names)}")

    if detailed:
        lines.append(f"  변경: +{pr.additions} -{pr.deletions} ({pr.changed_files}개 파일)")
        lines.append(f"  URL: {pr.html_url}")
        if pr.body:
            lines.append(f"\n--- 설명 ---\n{pr.body}")

    return "\n".join(lines)


def format_pull_request_list(prs: list) -> str:
    """PR 목록을 포맷팅한다."""
    formatted = [format_pull_request(p) for p in prs]
    return f"총 {len(prs)}개 PR:\n\n" + "\n\n".join(formatted)


def format_notification_list(notifications: list) -> str:
    """알림 목록을 포맷팅한다."""
    if not notifications:
        return "알림이 없습니다."

    lines = [f"총 {len(notifications)}개 알림:"]
    for n in notifications:
        subject = n.subject
        repo_name = n.repository.full_name
        reason = n.reason
        unread = "🔵" if n.unread else "⚪"
        lines.append(f"\n{unread} [{subject.type}] {subject.title}")
        lines.append(f"  저장소: {repo_name}")
        lines.append(f"  사유: {reason}")
        lines.append(f"  업데이트: {n.updated_at.strftime('%Y-%m-%d %H:%M')}")

    return "\n".join(lines)


def _extract_body(message: dict) -> str:
    """메일 본문을 추출한다."""
    payload = message.get("payload", {})

    if "body" in payload and payload["body"].get("data"):
        return base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")

    parts = payload.get("parts", [])
    for part in parts:
        if part.get("mimeType") == "text/plain":
            data = part.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8")

    for part in parts:
        if part.get("mimeType") == "text/html":
            data = part.get("body", {}).get("data", "")
            if data:
                return base64.urlsafe_b64decode(data).decode("utf-8")

    return ""
