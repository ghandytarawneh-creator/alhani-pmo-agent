"""ALHANI Construction Management PMO agent, serving the COO."""

from instructions import SYSTEM_INSTRUCTIONS
from tools import days_until, score_risk

from mistralai import agents

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
