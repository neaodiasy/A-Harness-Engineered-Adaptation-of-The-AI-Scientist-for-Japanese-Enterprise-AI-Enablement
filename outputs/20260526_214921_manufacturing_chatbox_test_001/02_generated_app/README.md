# Nagoya Precision Components AI Workbench

This generated child app is a runnable local product MVP built by the Software Builder Loop, not a single-file demo or JSON dump.

## What Was Built

- Local API-backed product server.
- Static frontend for consultants.
- Backend modules for agent orchestration, deterministic tools, evidence, DeepSeek calls, guardrails, and data loading.
- Runtime trusted-domain web evidence search in `backend/web_search.py`.
- Local domain candidate data and related item records.
- Plan-driven component assembly recorded in `component_plan.json`.
- Deterministic tests and API-backed evaluation.

## Run

```bash
cp .env.example .env.local
# edit .env.local and fill DEEPSEEK_API_KEY
./run_app.sh
```

Open `http://127.0.0.1:8766`.

CLI and evaluation:

```bash
python3 app.py --list-cases
python3 app.py --cli --max-cases 1
python3 app.py --cli
python3 -m unittest discover -s tests
python3 evaluation.py --max-cases 1
python3 evaluation.py
```

`--cli` and `evaluation.py` use the DeepSeek runtime and print progress before each sample case. For a quick smoke test, run one case with `--case-id` first; run the full batch when you want deeper evaluation.

## Product Flow

customer case -> local ranking tools -> evidence retrieval -> DeepSeek draft -> guardrails -> approval packet -> final JSON

The app always keeps `human_approval_required=true` and `send_allowed=false`.
