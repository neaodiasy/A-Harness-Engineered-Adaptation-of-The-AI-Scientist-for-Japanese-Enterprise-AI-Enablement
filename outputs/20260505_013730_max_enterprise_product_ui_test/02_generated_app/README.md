# AI Property Recommendation Platform

This generated child app is a runnable local product MVP built by the Software Builder Loop, not a single-file demo or JSON dump.

## What Was Built

- Local API-backed product server.
- Static frontend for consultants.
- Backend modules for agent orchestration, deterministic tools, evidence, DeepSeek calls, guardrails, and data loading.
- Runtime trusted-domain web evidence search in `backend/web_search.py`.
- Local domain data for areas and properties.
- Deterministic tests and API-backed evaluation.

## Run

```bash
export DEEPSEEK_API_KEY="..."
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export AGENT_MODEL="deepseek-v4-pro"
export DEEPSEEK_THINKING="1"
export DEEPSEEK_REASONING_EFFORT="high"
export GENERATED_APP_LIVE_SEARCH="1"
python3 app.py
```

Open `http://127.0.0.1:8766`.

CLI and evaluation:

```bash
python3 app.py --list-cases
python3 app.py --cli --case-id case_family_quiet_school
python3 app.py --cli
python3 -m unittest discover -s tests
python3 evaluation.py
```

`--cli` uses the DeepSeek runtime and prints progress to stderr before each sample case. For a quick smoke test, run one case with `--case-id` first.

## Product Flow

customer case -> local ranking tools -> evidence retrieval -> DeepSeek draft -> guardrails -> approval packet -> final JSON

The app always keeps `human_approval_required=true` and `send_allowed=false`.
