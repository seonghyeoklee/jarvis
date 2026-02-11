"""Google Calendar MCP 도구."""

from datetime import datetime, timedelta

from fastmcp import FastMCP
from googleapiclient.discovery import build

from jarvis.auth.google_auth import get_credentials
from jarvis.utils.formatting import format_event, format_event_list, format_calendar_list


def _get_calendar_service():
    """Google Calendar API 서비스 객체를 반환한다."""
    creds = get_credentials()
    return build("calendar", "v3", credentials=creds)


def register_calendar_tools(mcp: FastMCP) -> None:
    """Calendar 관련 MCP 도구를 서버에 등록한다."""

    @mcp.tool()
    def list_events(
        start_date: str | None = None,
        end_date: str | None = None,
        max_results: int = 10,
        calendar_id: str = "primary",
    ) -> str:
        """일정 목록을 조회한다. 날짜 형식: YYYY-MM-DD"""
        service = _get_calendar_service()

        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = start_date

        time_min = f"{start_date}T00:00:00Z"
        time_max = f"{end_date}T23:59:59Z"

        result = (
            service.events()
            .list(
                calendarId=calendar_id,
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = result.get("items", [])
        if not events:
            return f"{start_date} ~ {end_date} 기간에 일정이 없습니다."

        return format_event_list(events)

    @mcp.tool()
    def get_event(event_id: str, calendar_id: str = "primary") -> str:
        """특정 일정의 상세 정보를 조회한다."""
        service = _get_calendar_service()
        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()
        return format_event(event, detailed=True)

    @mcp.tool()
    def create_event(
        summary: str,
        start_time: str,
        end_time: str,
        description: str | None = None,
        location: str | None = None,
        attendees: list[str] | None = None,
        calendar_id: str = "primary",
    ) -> str:
        """새 일정을 생성한다. 시간 형식: ISO 8601 (예: 2025-02-12T15:00:00+09:00)"""
        service = _get_calendar_service()

        event_body = {
            "summary": summary,
            "start": {"dateTime": start_time},
            "end": {"dateTime": end_time},
        }

        if description:
            event_body["description"] = description
        if location:
            event_body["location"] = location
        if attendees:
            event_body["attendees"] = [{"email": email} for email in attendees]

        event = (
            service.events().insert(calendarId=calendar_id, body=event_body).execute()
        )

        return f"일정 생성 완료: {event['summary']}\nID: {event['id']}\n링크: {event.get('htmlLink', '')}"

    @mcp.tool()
    def update_event(
        event_id: str,
        summary: str | None = None,
        start_time: str | None = None,
        end_time: str | None = None,
        description: str | None = None,
        location: str | None = None,
        calendar_id: str = "primary",
    ) -> str:
        """기존 일정을 수정한다."""
        service = _get_calendar_service()

        event = service.events().get(calendarId=calendar_id, eventId=event_id).execute()

        if summary:
            event["summary"] = summary
        if start_time:
            event["start"]["dateTime"] = start_time
        if end_time:
            event["end"]["dateTime"] = end_time
        if description is not None:
            event["description"] = description
        if location is not None:
            event["location"] = location

        updated = (
            service.events()
            .update(calendarId=calendar_id, eventId=event_id, body=event)
            .execute()
        )

        return f"일정 수정 완료: {updated['summary']}"

    @mcp.tool()
    def delete_event(event_id: str, calendar_id: str = "primary") -> str:
        """일정을 삭제한다."""
        service = _get_calendar_service()
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        return "일정이 삭제되었습니다."

    @mcp.tool()
    def list_calendars() -> str:
        """사용 가능한 캘린더 목록을 조회한다."""
        service = _get_calendar_service()
        result = service.calendarList().list().execute()
        calendars = result.get("items", [])
        return format_calendar_list(calendars)

    @mcp.tool()
    def search_events(
        query: str,
        start_date: str | None = None,
        end_date: str | None = None,
        max_results: int = 10,
    ) -> str:
        """키워드로 일정을 검색한다."""
        service = _get_calendar_service()

        if not start_date:
            start_date = datetime.now().strftime("%Y-%m-%d")
        if not end_date:
            end_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        time_min = f"{start_date}T00:00:00Z"
        time_max = f"{end_date}T23:59:59Z"

        result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
                q=query,
            )
            .execute()
        )

        events = result.get("items", [])
        if not events:
            return f"'{query}' 검색 결과가 없습니다."

        return format_event_list(events)
