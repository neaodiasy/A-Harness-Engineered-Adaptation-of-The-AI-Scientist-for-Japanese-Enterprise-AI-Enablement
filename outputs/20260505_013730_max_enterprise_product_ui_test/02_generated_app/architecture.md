# Generated Project Architecture

- Runtime: Python standard library HTTP API + static frontend + DeepSeek chat completions

## Entrypoints

- cli: `python3 app.py --cli`
- server: `python3 app.py`
- evaluation: `python3 evaluation.py`
- deterministic_tests: `python3 -m unittest discover -s tests`

## Backend Modules

- `backend/agent.py`: Orchestrates case -> tools -> evidence -> DeepSeek -> guardrails.
- `backend/api.py`: Local JSON API and static frontend server.
- `backend/data_store.py`: Loads generated domain data and sample cases.
- `backend/llm_client.py`: DeepSeek/OpenAI-compatible JSON client with retry.
- `backend/web_search.py`: Runtime trusted-domain web evidence search.
- `backend/recommendation_engine.py`: Deterministic ranking algorithms.
- `backend/tools.py`: Local tool interface used before LLM drafting.
- `backend/guardrails.py`: Schema normalization, placeholder prevention, approval enforcement.

## Frontend Modules

- `frontend/index.html`: Usable product surface.
- `frontend/styles.css`: Work-focused interface styling.
- `frontend/app.js`: Calls local API and displays recommendation packets.
