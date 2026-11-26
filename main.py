"""ALHANI Construction Management PMO agent, serving the COO."""

import os
from pathlib import Path

from instructions import SYSTEM_INSTRUCTIONS
from tools import days_until, score_risk

from mistralai import agents

_FALLBACK_MODELS = [
    "mistral-large-latest",
    "mistral-medium-latest",
    "mistral-small-latest",
    "open-mistral-nemo",
]
_DEFAULT_MODEL = "mistral-medium-latest"


def _load_dotenv() -> None:
    """Populate os.environ from the project's .env so `uv run agents chat`
    works without --env-file or manual exports. Non-empty shell-exported
    variables win; empty ones are treated as unset.
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
        current = os.environ.get(key)
        if key and value and not (current or "").strip():
            os.environ[key] = value


def _clean(value: str) -> str:
    return value.strip().strip('"').strip("'").strip("<>").strip()


def _resolve_model() -> str:
    """Pick the best model the API key's subscription actually offers.

    Preference: a valid ALHANI_MODEL, then large/medium/small latest. If the
    catalogue cannot be read, fall back to the requested or default model so
    startup never fails because of this check.
    """
    requested = _clean(os.getenv("ALHANI_MODEL") or "")
    api_key = (os.getenv("MISTRAL_API_KEY")
               or os.getenv("MISTRAL_CLIENT_API_KEY") or "").strip()
    if not api_key:
        return requested or _DEFAULT_MODEL
    available: set[str] | None = None
    try:
        import httpx

        response = httpx.get(
            "https://api.mistral.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10,
        )
        if response.status_code == 200:
            available = {
                m.get("id") for m in response.json().get("data", []) if m.get("id")
            }
    except Exception:
        available = None
    if not available:
        return requested or _DEFAULT_MODEL
    for candidate in ([requested] if requested else []) + _FALLBACK_MODELS:
        if candidate in available:
            if requested and candidate != requested:
                print(
                    f"Note: model '{requested}' is not available on this "
                    f"subscription tier; using '{candidate}' instead."
                )
            return candidate
    return requested or _DEFAULT_MODEL


_load_dotenv()

MODEL = _resolve_model()

agent = agents.Agent(
    model=MODEL,
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
