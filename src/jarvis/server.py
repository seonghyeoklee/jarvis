"""Jarvis MCP 서버 메인 모듈."""

from fastmcp import FastMCP

from jarvis.tools.calendar import register_calendar_tools
from jarvis.tools.gmail import register_gmail_tools

mcp = FastMCP(
    "Jarvis",
    description="개인 AI 비서 - Google Calendar + Gmail 관리",
)

register_calendar_tools(mcp)
register_gmail_tools(mcp)


def main():
    """MCP 서버를 실행한다."""
    mcp.run()


if __name__ == "__main__":
    main()
