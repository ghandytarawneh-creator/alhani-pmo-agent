"""ALHANI Construction Management PMO agent, serving the COO."""

import os
from pathlib import Path

from instructions import SYSTEM_INSTRUCTIONS
from tools import days_until, score_risk

from mistralai import agents


def _load_dotenv() -> None:
    """Populate os.environ from the project's .env so `uv run agents chat`
    works without --env-file or manual exports. Shell-exported variables win.
    """
    env_file = Path(__file__).resolve().parent / ".env"
    if not env_file.exists():
        return
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


_load_dotenv()

agent = agents.Agent(
    model="mistral-large-4",
    name="alhani-pmo-agent",
    instructions=SYSTEM_INSTRUCTIONS,
    tools=[score_risk, days_until],
    connectors=[
        agents.connector("google_drive_mcp"),
    ],
)


def main() -> None:
    raise SystemExit(
        "Chat with this agent using 'uv run agents chat', or deploy it with "
        "'mistral agents deploy'. See README.md."
    )


if __name__ == "__main__":
    main()
