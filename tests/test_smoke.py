"""Offline smoke test: the agent loop and both tools run with a scripted model.

Requires no API key. Run: uv run pytest -o asyncio_mode=auto tests/
"""

import pytest

from main import agent

from mistralai import agents


@pytest.fixture(autouse=True)
def no_real_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """A placeholder key lets connector assembly succeed; the connector is
    dropped with a notice and no real model call is possible."""
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.delenv("MISTRAL_CLIENT_API_KEY", raising=False)
    monkeypatch.setenv("MISTRAL_API_KEY", "offline-smoke-test-placeholder")


async def test_agent_calls_both_tools_and_replies() -> None:
    model = agents.testing.ScriptedModel(
        [
            agents.testing.run_typescript(
                "return await tools.client.score_risk({likelihood: 4, impact: 5});"
            ),
            agents.testing.run_typescript(
                'return await tools.client.days_until({due_date: "2020-01-01"});'
            ),
            agents.testing.reply(
                "R-001 rated Critical; deadline A-001 is 0 days overdue."
            ),
        ]
    )

    state = await agent.override(model=model).run(
        "Score a risk with likelihood 4 and impact 5, and check the 2020-01-01 deadline."
    )

    assert isinstance(state, agents.Completed), state
    assert state.text == "R-001 rated Critical; deadline A-001 is 0 days overdue."
    assert [call.name for call in state.tool_calls] == [
        "client.score_risk",
        "client.days_until",
    ]
    model.assert_consumed()
