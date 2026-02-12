"""Jarvis MCP 서버 메인 모듈."""

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

from fastmcp import FastMCP

from jarvis.tools.calendar import register_calendar_tools
from jarvis.tools.gmail import register_gmail_tools
from jarvis.tools.github import register_github_tools

mcp = FastMCP("Jarvis")

register_calendar_tools(mcp)
register_gmail_tools(mcp)
register_github_tools(mcp)


def main():
    """MCP 서버를 실행한다."""
    mcp.run()


if __name__ == "__main__":
    main()
