"""Google Calendar 도구 테스트."""

from jarvis.utils.formatting import format_event, format_event_list, format_calendar_list


def test_format_event_basic():
    event = {
        "summary": "팀 미팅",
        "start": {"dateTime": "2025-02-12T15:00:00+09:00"},
        "end": {"dateTime": "2025-02-12T16:00:00+09:00"},
    }
    result = format_event(event)
    assert "팀 미팅" in result
    assert "15:00:00" in result


def test_format_event_detailed():
    event = {
        "id": "abc123",
        "summary": "팀 미팅",
        "start": {"dateTime": "2025-02-12T15:00:00+09:00"},
        "end": {"dateTime": "2025-02-12T16:00:00+09:00"},
        "location": "회의실 A",
        "description": "주간 회의",
        "attendees": [{"email": "test@example.com"}],
        "htmlLink": "https://calendar.google.com/event/abc123",
    }
    result = format_event(event, detailed=True)
    assert "팀 미팅" in result
    assert "회의실 A" in result
    assert "주간 회의" in result
    assert "test@example.com" in result
    assert "abc123" in result


def test_format_event_list():
    events = [
        {
            "summary": "아침 회의",
            "start": {"dateTime": "2025-02-12T09:00:00+09:00"},
            "end": {"dateTime": "2025-02-12T10:00:00+09:00"},
        },
        {
            "summary": "점심 미팅",
            "start": {"dateTime": "2025-02-12T12:00:00+09:00"},
            "end": {"dateTime": "2025-02-12T13:00:00+09:00"},
        },
    ]
    result = format_event_list(events)
    assert "총 2개 일정" in result
    assert "아침 회의" in result
    assert "점심 미팅" in result


def test_format_event_all_day():
    event = {
        "summary": "휴가",
        "start": {"date": "2025-02-12"},
        "end": {"date": "2025-02-13"},
    }
    result = format_event(event)
    assert "휴가" in result
    assert "2025-02-12" in result


def test_format_calendar_list():
    calendars = [
        {"summary": "내 캘린더", "id": "primary", "primary": True},
        {"summary": "업무", "id": "work@group.calendar.google.com"},
    ]
    result = format_calendar_list(calendars)
    assert "총 2개 캘린더" in result
    assert "내 캘린더" in result
    assert "(기본)" in result
    assert "업무" in result
