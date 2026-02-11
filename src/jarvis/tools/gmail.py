"""Gmail MCP 도구."""

import base64
from email.mime.text import MIMEText

from fastmcp import FastMCP
from googleapiclient.discovery import build

from jarvis.auth.google_auth import get_credentials
from jarvis.utils.formatting import (
    format_message,
    format_message_list,
    format_label_list,
)


def _get_gmail_service():
    """Gmail API 서비스 객체를 반환한다."""
    creds = get_credentials()
    return build("gmail", "v1", credentials=creds)


def register_gmail_tools(mcp: FastMCP) -> None:
    """Gmail 관련 MCP 도구를 서버에 등록한다."""

    @mcp.tool()
    def list_messages(
        max_results: int = 10,
        label: str = "INBOX",
        unread_only: bool = False,
    ) -> str:
        """받은편지함의 메일 목록을 조회한다."""
        service = _get_gmail_service()

        label_ids = [label]
        if unread_only:
            label_ids.append("UNREAD")

        result = (
            service.users()
            .messages()
            .list(userId="me", labelIds=label_ids, maxResults=max_results)
            .execute()
        )

        messages = result.get("messages", [])
        if not messages:
            return "메일이 없습니다."

        detailed = []
        for msg in messages:
            detail = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="metadata")
                .execute()
            )
            detailed.append(detail)

        return format_message_list(detailed)

    @mcp.tool()
    def get_message(message_id: str) -> str:
        """특정 메일의 전체 내용을 조회한다."""
        service = _get_gmail_service()
        message = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="full")
            .execute()
        )
        return format_message(message)

    @mcp.tool()
    def search_messages(query: str, max_results: int = 10) -> str:
        """Gmail 검색 문법으로 메일을 검색한다."""
        service = _get_gmail_service()

        result = (
            service.users()
            .messages()
            .list(userId="me", q=query, maxResults=max_results)
            .execute()
        )

        messages = result.get("messages", [])
        if not messages:
            return f"'{query}' 검색 결과가 없습니다."

        detailed = []
        for msg in messages:
            detail = (
                service.users()
                .messages()
                .get(userId="me", id=msg["id"], format="metadata")
                .execute()
            )
            detailed.append(detail)

        return format_message_list(detailed)

    @mcp.tool()
    def send_message(
        to: str,
        subject: str,
        body: str,
        cc: str | None = None,
        bcc: str | None = None,
    ) -> str:
        """새 이메일을 발송한다."""
        service = _get_gmail_service()

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject

        if cc:
            message["cc"] = cc
        if bcc:
            message["bcc"] = bcc

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        result = (
            service.users()
            .messages()
            .send(userId="me", body={"raw": raw})
            .execute()
        )

        return f"메일 발송 완료\nID: {result['id']}\n스레드 ID: {result['threadId']}"

    @mcp.tool()
    def reply_message(
        message_id: str,
        body: str,
        reply_all: bool = False,
    ) -> str:
        """기존 메일에 답장한다."""
        service = _get_gmail_service()

        original = (
            service.users()
            .messages()
            .get(userId="me", id=message_id, format="metadata")
            .execute()
        )

        headers = {h["name"]: h["value"] for h in original["payload"]["headers"]}

        to = headers.get("From", "")
        subject = headers.get("Subject", "")
        if not subject.startswith("Re:"):
            subject = f"Re: {subject}"

        message = MIMEText(body)
        message["to"] = to
        message["subject"] = subject
        message["In-Reply-To"] = headers.get("Message-Id", "")
        message["References"] = headers.get("Message-Id", "")

        if reply_all:
            cc_list = headers.get("Cc", "")
            if cc_list:
                message["cc"] = cc_list

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

        result = (
            service.users()
            .messages()
            .send(
                userId="me",
                body={"raw": raw, "threadId": original["threadId"]},
            )
            .execute()
        )

        return f"답장 발송 완료\nID: {result['id']}"

    @mcp.tool()
    def modify_labels(
        message_id: str,
        add_labels: list[str] | None = None,
        remove_labels: list[str] | None = None,
    ) -> str:
        """메일의 라벨을 추가하거나 제거한다."""
        service = _get_gmail_service()

        body = {
            "addLabelIds": add_labels or [],
            "removeLabelIds": remove_labels or [],
        }

        service.users().messages().modify(
            userId="me", id=message_id, body=body
        ).execute()

        actions = []
        if add_labels:
            actions.append(f"추가: {', '.join(add_labels)}")
        if remove_labels:
            actions.append(f"제거: {', '.join(remove_labels)}")

        return f"라벨 수정 완료 ({'; '.join(actions)})"

    @mcp.tool()
    def list_labels() -> str:
        """사용 가능한 라벨 목록을 조회한다."""
        service = _get_gmail_service()
        result = service.users().labels().list(userId="me").execute()
        labels = result.get("labels", [])
        return format_label_list(labels)

    @mcp.tool()
    def trash_message(message_id: str) -> str:
        """메일을 휴지통으로 이동한다."""
        service = _get_gmail_service()
        service.users().messages().trash(userId="me", id=message_id).execute()
        return "메일이 휴지통으로 이동되었습니다."
