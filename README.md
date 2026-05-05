# J-Enterprise Agent Scientist

**A Sakana AI Scientist-inspired enterprise software discovery and generation harness for Japanese companies.**

Rather than using The AI Scientist to generate machine learning papers, this project adapts its agentic discovery workflow to a Japan-specific enterprise AI transformation setting. The unit of discovery is changed from a research idea to an enterprise AI enablement opportunity.

## What This Project Is

J-Enterprise Agent Scientist takes an arbitrary Japanese enterprise profile and runs a full applied research engineering pipeline:

```text
enterprise profile
-> evidence pack
-> opportunity generation
-> feasibility / risk / Japan-fit check
-> candidate search
-> primitive architecture composition
-> agent workflow design
-> enterprise productization blueprint
-> Software Builder Loop
-> generated multi-file agent product
-> sandbox evaluation
-> proposal writing
-> automated review
```

The generated output is a runnable local product MVP, not a generic demo or JSON dump. It packages a usable web UI, runtime DeepSeek calls, local domain tools, live trusted-domain evidence search, risk controls, human approval, tests, and auditability. It is still not a fully deployed enterprise SaaS until authentication, persistent storage, enterprise connectors, observability, and security review are added.

## Why This Is Based On The AI Scientist

Sakana AI's AI Scientist repo is organized around a launchable autonomous discovery loop: templates define a research environment, ideas are generated, experiments are planned and executed, results are analyzed, papers are written, and generated papers can be reviewed. The repository also emphasizes visible intermediate artifacts such as `templates/`, `experiment.py`, `plot.py`, `prompt.json`, `seed_ideas.json`, and launch scripts.

AI Scientist-v2 extends the direction with agentic tree search: candidate ideas are explored, refined, debugged, and selected through a search process rather than a single one-shot generation.

This project mirrors that design philosophy, but changes the domain:

| The AI Scientist | J-Enterprise Agent Scientist |
|---|---|
| Research template | Enterprise profile / company environment |
| Research idea generation | AI enablement opportunity generation |
| Novelty check | Feasibility / risk / Japan-specific relevance check |
| Experiment planning | Agent workflow design and enterprise productization blueprint |
| Code generation | Software Builder Loop generated product package |
| Experiment execution | Sandbox product evaluation |
| Plot generation | Workflow and architecture SVG generation |
| Result analysis | Business value / risk / software usefulness analysis |
| Paper writing | Enterprise implementation proposal |
| Automated reviewer | Business-technical-risk and software reviewer |
| Agentic tree search | Candidate opportunity search and refinement |

## Why This Is Not A Generic Chatbot

The system does not simply chat with a user and give advice. It writes and preserves a chain of artifacts:

- `outputs/<timestamp>_api_run/00_README.md`
- `outputs/<timestamp>_api_run/final_summary.json`
- `outputs/<timestamp>_api_run/01_consulting/evidence_pack.json`
- `outputs/<timestamp>_api_run/01_consulting/opportunities.json`
- `outputs/<timestamp>_api_run/01_consulting/feasibility_results.json`
- `outputs/<timestamp>_api_run/01_consulting/tree_search_trace.json`
- `outputs/<timestamp>_api_run/01_consulting/selected_opportunity.json`
- `outputs/<timestamp>_api_run/02_generated_app/app.py`
- `outputs/<timestamp>_api_run/02_generated_app/backend/`
- `outputs/<timestamp>_api_run/02_generated_app/frontend/`
- `outputs/<timestamp>_api_run/02_generated_app/data/`
- `outputs/<timestamp>_api_run/02_generated_app/tests/`
- `outputs/<timestamp>_api_run/02_generated_app/tools.py`
- `outputs/<timestamp>_api_run/02_generated_app/evaluation.py`
- `outputs/<timestamp>_api_run/02_generated_app/productization_blueprint.json`
- `outputs/<timestamp>_api_run/02_generated_app/product_requirements.json`
- `outputs/<timestamp>_api_run/02_generated_app/project_architecture.json`
- `outputs/<timestamp>_api_run/02_generated_app/file_manifest.json`
- `outputs/<timestamp>_api_run/02_generated_app/builder_loop_trace.json`
- `outputs/<timestamp>_api_run/03_sandbox/sandbox_report.json`
- `outputs/<timestamp>_api_run/03_sandbox/case_outputs.json`
- `outputs/<timestamp>_api_run/04_review/review.json`
- `outputs/<timestamp>_api_run/05_visuals/architecture_diagram.svg`

That artifact trail is the core product. The app is a generated experiment, not the whole system.

## Software Builder Loop

The Code Agent now builds the generated child app through a software engineering loop:

1. `productization_blueprint`: selects an enterprise product archetype, role model, workbench layout, state model, and visual quality contract.
2. `product_requirements`: writes the generated PRD, users, workflows, acceptance criteria, and safety boundaries.
3. `project_architecture`: designs backend modules, frontend surface, data files, tests, entrypoints, and quality gates.
4. `file_manifest`: defines every generated file before code is written.
5. `code_generation`: writes a runnable project package with `backend/`, `frontend/`, `data/`, `tests/`, `app.py`, and `evaluation.py`.
6. `sandbox_execution`: compiles source, checks project shape, runs unit tests, runs the CLI, and runs API-backed evaluation.
7. `repair_loop`: records failed checks and the next patch/regeneration action.
8. `product_review`: scores the generated product.

This keeps the framework flexible while avoiding a fixed single-file demo. The real-estate profile can generate an AI-driven property recommendation platform; another profile should generate a different product package with the same builder loop.

## Harness Engineering Components

- `src/harness/llm.py`: DeepSeek/OpenAI-format gateway with cheap/strong stage routing. A real API key is required.
- `src/harness/json_utils.py`: JSON parsing and fallback handling.
- `src/evidence_search.py`: curated Japan-specific evidence retrieval layer with optional trusted-domain live search via `ENABLE_LIVE_SEARCH=1`.
- `src/candidate_search.py`: LATS-lite expand, critique, refine, and select loop.
- `src/architecture_composer.py`: composes workflows from reusable primitives.
- `src/productization.py`: converts the selected opportunity into an enterprise software product blueprint before code generation.
- `src/software_factory.py`: Software Builder Loop artifacts: PRD, architecture, file manifest, implementation plan, and repair trace.
- `src/prototype_builder.py`: writes generated multi-file product packages.
- `src/ui_quality.py`: static frontend responsiveness harness for generated enterprise workbench UIs.
- `src/sandbox_eval.py`: compiles and evaluates generated project packages in the local generated app folder.

## Repository Structure

```text
j-enterprise-agent-scientist/
├── README.md
├── config.yaml
├── run.py
├── launch_enterprise_scientist.py
├── debug_server.py
├── frontend/
│   ├── index.html
│   ├── styles.css
│   └── app.js
├── src/
│   ├── agent_design.py
│   ├── architecture_composer.py
│   ├── candidate_search.py
│   ├── evidence_search.py
│   ├── feasibility.py
│   ├── primitive_registry.py
│   ├── proposal.py
│   ├── productization.py
│   ├── prototype_builder.py
│   ├── sandbox_eval.py
│   ├── software_factory.py
│   ├── visualization.py
│   └── harness/
│       ├── __init__.py
│       ├── json_utils.py
│       └── llm.py
└── outputs/
    └── <timestamp>_api_run/
        ├── 00_README.md
        ├── 01_consulting/
        ├── 02_generated_app/
        ├── 03_sandbox/
        ├── 04_review/
        ├── 05_visuals/
        └── final_summary.json
```

## How To Run

Run the full pipeline from the command line:

```bash
cd path/to/j-enterprise-agent-scientist-v2-live-search
export DEEPSEEK_API_KEY="your_key"
export DEEPSEEK_BASE_URL="https://api.deepseek.com"
export AGENT_MODEL="deepseek-v4-pro"
export DEEPSEEK_THINKING="1"
export DEEPSEEK_REASONING_EFFORT="high"
export ENABLE_LIVE_SEARCH="1"
python3 run.py --profile profiles/example_real_estate.json
```

Each run writes everything into one timestamped folder:

```text
outputs/<timestamp>_api_run/
```

Start with `outputs/<timestamp>_api_run/00_README.md` and `outputs/<timestamp>_api_run/final_summary.json`.

When live search is enabled, inspect:

```text
outputs/<timestamp>_api_run/01_consulting/evidence_pack.json
```

The evidence pack records curated sources, live trusted-domain results, search metadata, and whether live search was enabled for the run.

Run the debug UI:

```bash
python3 debug_server.py
```

Open:

```text
http://127.0.0.1:8765
```

Run the debug UI with DeepSeek:

```bash
export DEEPSEEK_API_KEY="your_key"
python3 debug_server.py
```

If a port is occupied, the debug server and generated app try the next local port automatically.

Run the generated app:

```bash
cd "outputs/<timestamp>_api_run/02_generated_app"
python3 app.py --cli
python3 app.py
```

Open `http://127.0.0.1:8766` after starting the generated app server.

Run only the generated app evaluation:

```bash
cd "outputs/<timestamp>_api_run/02_generated_app"
python3 -m unittest discover -s tests
python3 evaluation.py --case-id case_family_quiet_school
python3 evaluation.py
```

The sandbox runs real-API smoke checks on one representative case so high-reasoning model calls do not turn every pipeline run into a long batch job. The generated product still supports full multi-case CLI and evaluation runs.

## Current Limitations

- Live evidence search is implemented for trusted domains, but high-stakes enterprise use still needs source review, stronger query planning, caching, and citation QA.
- The generated app now includes a product UI, runtime DeepSeek usage, runtime live web evidence search, `product_readiness.json`, and `production_readiness.md`; it is a local product MVP rather than a production-hosted SaaS.
- The repair loop records failures and repair actions; deeper automatic code patching is the next step.
- Runs now require `DEEPSEEK_API_KEY` and fail fast if the DeepSeek API is unavailable.

## Future Work

- Improve live search for company-specific competitive evidence, including better Japanese query expansion and source credibility scoring.
- Add stronger multi-file code generation with generate-run-repair iterations.
- Add a richer reviewer that scores both generated code quality and business usefulness.
- Add optional visual input analysis for screenshots, forms, and documents.
- Add multiple generated app archetypes while preserving flexible blueprint-driven customization.
