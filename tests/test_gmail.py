"""Gmail 도구 테스트."""

import base64

from jarvis.utils.formatting import (
    format_message,
    format_message_list,
    format_label_list,
    _extract_body,
    _get_header,
)


def test_get_header():
    message = {
        "payload": {
            "headers": [
                {"name": "Subject", "value": "테스트 메일"},
                {"name": "From", "value": "sender@example.com"},
            ]
        }
    }
    assert _get_header(message, "Subject") == "테스트 메일"
    assert _get_header(message, "From") == "sender@example.com"
    assert _get_header(message, "Missing") == ""


def test_format_message():
    message = {
        "id": "msg123",
        "threadId": "thread456",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "회의록 공유"},
                {"name": "From", "value": "김철수 <kimcs@example.com>"},
                {"name": "To", "value": "me@example.com"},
                {"name": "Date", "value": "Tue, 11 Feb 2025 10:00:00 +0900"},
            ],
            "body": {
                "data": base64.urlsafe_b64encode("안녕하세요, 회의록입니다.".encode()).decode()
            },
        },
    }
    result = format_message(message)
    assert "회의록 공유" in result
    assert "kimcs@example.com" in result
    assert "안녕하세요" in result
    assert "msg123" in result


def test_format_message_list():
    messages = [
        {
            "id": "msg1",
            "snippet": "첫 번째 메일 내용 미리보기",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "첫 번째 메일"},
                    {"name": "From", "value": "a@example.com"},
                    {"name": "Date", "value": "2025-02-11"},
                ]
            },
        },
        {
            "id": "msg2",
            "snippet": "두 번째 메일 내용 미리보기",
            "payload": {
                "headers": [
                    {"name": "Subject", "value": "두 번째 메일"},
                    {"name": "From", "value": "b@example.com"},
                    {"name": "Date", "value": "2025-02-11"},
                ]
            },
        },
    ]
    result = format_message_list(messages)
    assert "총 2개 메일" in result
    assert "첫 번째 메일" in result
    assert "두 번째 메일" in result


def test_format_label_list():
    labels = [
        {"name": "INBOX", "id": "INBOX", "type": "system"},
        {"name": "SENT", "id": "SENT", "type": "system"},
        {"name": "프로젝트", "id": "Label_1", "type": "user"},
    ]
    result = format_label_list(labels)
    assert "총 3개 라벨" in result
    assert "시스템 라벨" in result
    assert "사용자 라벨" in result
    assert "INBOX" in result
    assert "프로젝트" in result


def test_extract_body_plain():
    message = {
        "payload": {
            "body": {
                "data": base64.urlsafe_b64encode("테스트 본문".encode()).decode()
            }
        }
    }
    assert _extract_body(message) == "테스트 본문"


def test_extract_body_multipart():
    message = {
        "payload": {
            "body": {},
            "parts": [
                {
                    "mimeType": "text/plain",
                    "body": {
                        "data": base64.urlsafe_b64encode("멀티파트 본문".encode()).decode()
                    },
                }
            ],
        }
    }
    assert _extract_body(message) == "멀티파트 본문"
