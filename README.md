# ARIA

**Environmental Decision Intelligence**

Measuring environmental capacity. Connecting science, regulation, industry, and nature.

ARIA helps people examine what a specific environment may support by keeping observations, evidence, uncertainty, regulatory context, and human review connected throughout an assessment.

> ARIA does not speak for nature. It makes environmental evidence understandable enough to include environmental capacity in human decisions.

## IBM TechXchange 2026 hackathon prototype

The current prototype proves one narrow, honest workflow: assessing whether the evidence for a native pollinator habitat is sufficient to advance the idea for specialist review.

It demonstrates:

- structured environmental evidence with source, date, location, method, and quality metadata
- validation before analysis
- separate soil, water, terrain, ecology, and regulatory findings
- explicit missing information and uncertainty
- evidence-linked explanations
- mandatory human review boundaries
- no hidden composite score

Agriculture and habitat assessment are initial proving grounds. ARIA's documented architecture extends to broader environmental and industrial decision contexts.

## Run locally

Requirements: Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1`.

## Fast demo

1. Open the **Balanced evidence** scenario and run the assessment.
2. Show that every finding links back to evidence metadata.
3. Switch to **Missing water evidence** to show graceful uncertainty.
4. Switch to **Regulatory restriction** to show that AI reasoning cannot bypass a known constraint.
5. Open **What this prototype does not claim** before closing.

## Test and verify

```bash
pip install -r requirements-dev.txt
python -m unittest discover -s tests -v
python scripts/check_secrets.py
python scripts/check_docs.py
python -m compileall app.py src tests scripts
ruff check app.py src tests scripts
ruff format --check app.py src tests scripts
```

## Architecture

```text
User context
    ↓
Evidence records
    ↓
Validation
    ↓
Domain findings
    ↓
Environmental capacity status
    ↓
Evidence and uncertainty explanation
    ↓
Human review
```

The implementation is intentionally small. The governing architecture, capability map, knowledge model, and development workflow remain in [`docs/`](docs/).

## IBM Bob 2.0 development story

ARIA is the real project used to demonstrate an improved developer workflow with IBM Bob 2.0. The team should retain only real Bob plans, agent activity, parallel work, test results, timings, and review evidence in [`reports/bob/`](reports/bob/). No Bob capability or productivity improvement should be claimed without recorded evidence.

## Current boundaries

- The prototype uses manually entered evidence and illustrative reference rules.
- It does not retrieve scientific or regulatory sources automatically.
- It is not legal, regulatory, scientific, ecological, agricultural, or engineering advice.
- A displayed status is decision support, not approval, certification, or authorization.
- External integrations, multimodal ingestion, geospatial analysis, agent orchestration, and production deployment remain outside this implementation.

## Security

Copy `.env.example` to `.env` and store credentials only in the ignored local file. Never commit, paste, log, or share live credentials. Run the secret check before every push and follow [`SECURITY.MD`](SECURITY.MD).

## Project documents

- [`ARIA_PROJECT_CONSTITUTION.md`](docs/ARIA_PROJECT_CONSTITUTION.md)
- [`ARIA_ARCHITECTURE.md`](docs/ARIA_ARCHITECTURE.md)
- [`ARIA_CAPABILITIES.md`](docs/ARIA_CAPABILITIES.md)
- [`ARIA_KNOWLEDGE_MODEL.md`](docs/ARIA_KNOWLEDGE_MODEL.md)
- [`ARIA_DEVELOPMENT_WORKFLOW.md`](docs/ARIA_DEVELOPMENT_WORKFLOW.md)
- [`DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md)
- [`HACKATHON_SUBMISSION_CHECKLIST.md`](docs/HACKATHON_SUBMISSION_CHECKLIST.md)

## License

No open source license has been selected. All rights remain with the project contributors until the team chooses one.
