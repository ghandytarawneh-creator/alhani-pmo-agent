# ALHANI PMO Agent

Conversational Construction Management agent for the COO of ALHANI Company, built on the
[Mistral Agents SDK](https://docs.mistral.ai/studio/agents/getting-started/quickstart)
and deployed as a Mistral-managed agent, with the Google Drive connector for retrieving
project documents from shared links.

## Capabilities

- Document triage by type, project, revision, date, status, and owner (Document Control Log).
- Checklist reviews: Contracts (FIDIC/NEC), Purchase Orders, Method Statements, Quality Plans,
  Lifting Plans, Risk Assessments, Quotations, Schedules, Project Charters.
- Cross-document alignment audits: scope, quantities, specifications, commercial terms,
  milestones, responsibilities, approvals, compliance.
- Cost and scope traceability: BOQ → quotation → PO → contract → variation → invoice →
  progress claim.
- Live Risk Register (Critical/High/Medium/Low via a deterministic 5x5 `score_risk` tool),
  Action Tracker (`days_until` for overdue math), Document Control Log, and executive
  KPI dashboard — maintained in-conversation and persisted to a Google Drive folder
  `ALHANI PMO Registers`.
- FIDIC/NEC contract administration, OSHA-aligned HSE, and ISO 9001 / 14001 / 45001
  document reviews, with clause citations.
- Executive Summary first; every finding as Issue → Impact → Recommendation → Owner →
  Deadline; Approval Blockers separated from Optimization Opportunities; no invented
  project data — gaps are flagged `MISSING — requires verification`.

## Project layout

| File | Purpose |
| --- | --- |
| `main.py` | Agent definition (model, connectors, tools) and entrypoint. |
| `instructions.py` | Full system instructions: checklists, register formats, output rules. |
| `tools.py` | Deterministic tools: `score_risk`, `days_until`. |
| `Dockerfile` | Worker image used by the managed deployment. |

## Local use

```bash
uv sync
cp .env.example .env   # then paste your Mistral API key into .env
uv run agents chat
```

Offline check (no API key needed, scripted model, real tool execution):

```bash
uv run pytest tests/
```

## Deploy (Mistral-managed)

```bash
git push            # deploy builds the pushed commit
mistral agents deploy
```

The agent uses connectors that act as the session user (Google Drive), so the deployment
is hardened by default. Chat with it in Vibe Code Web via the link `mistral agents deploy`
prints after the rollout.
