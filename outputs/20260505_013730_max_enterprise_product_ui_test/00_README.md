# Run Output Index

This folder contains one complete J-Enterprise Agent Scientist run.

## Start Here

- Final summary: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/final_summary.json`
- Generated app code: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app`
- Main app code: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/app.py`
- Local tools: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/tools.py`
- Evaluator: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/evaluation.py`
- Final agent case outputs: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/03_sandbox/case_outputs.json`
- Full sandbox report: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/03_sandbox/sandbox_report.json`
- Product review: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/04_review/review.md`

## Consulting Agent

- Business analysis: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/01_consulting/business_analysis.json`
- Opportunities: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/01_consulting/opportunities.json`
- Selected opportunity: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/01_consulting/selected_opportunity.json`
- Tree search trace: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/01_consulting/tree_search_trace.json`
- Raw DeepSeek consultation: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/01_consulting/llm_consultation_raw.txt`

## Code Agent

- Generated app folder: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app`
- Product requirements: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/product_requirements.json`
- Productization blueprint: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/productization_blueprint.md`
- Production readiness: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/production_readiness.md`
- Project architecture: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/project_architecture.json`
- File manifest: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/file_manifest.json`
- Builder loop trace: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/builder_loop_trace.json`
- Product brief: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/product_brief.json`
- Product spec: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/product_spec.json`
- Backend code: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/backend`
- Frontend code: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/frontend`
- Local data: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/data`
- Deterministic tests: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/tests`
- Prototype manifest: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app/_generator_context/prototype_manifest.json`

## Run Generated Product

```bash
cd "<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/02_generated_app"
python3 app.py --cli
python3 -m unittest discover -s tests
python3 evaluation.py
```

## Visuals

- Opportunity score chart: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/05_visuals/opportunity_score_chart.svg`
- Pipeline diagram: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/05_visuals/solution_pipeline_diagram.svg`
- Architecture diagram: `<repo>/outputs/20260505_013730_max_enterprise_product_ui_test/05_visuals/architecture_diagram.svg`
