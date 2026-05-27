# Run Output Index

This folder contains one complete J-Enterprise Agent Scientist run.

## Start Here

- Final summary: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/final_summary.json`
- Generated app code: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app`
- Main app code: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/app.py`
- Local tools: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/tools.py`
- Evaluator: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/evaluation.py`
- Final agent case outputs: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/03_sandbox/case_outputs.json`
- Full sandbox report: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/03_sandbox/sandbox_report.json`
- Product review: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/04_review/review.md`

## Consulting Agent

- Business analysis: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/01_consulting/business_analysis.json`
- Opportunities: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/01_consulting/opportunities.json`
- Selected opportunity: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/01_consulting/selected_opportunity.json`
- Tree search trace: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/01_consulting/tree_search_trace.json`
- Raw DeepSeek consultation: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/01_consulting/llm_consultation_raw.txt`

## Code Agent

- Generated app folder: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app`
- Product requirements: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/product_requirements.json`
- Productization blueprint: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/productization_blueprint.md`
- Production readiness: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/production_readiness.md`
- Project architecture: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/project_architecture.json`
- File manifest: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/file_manifest.json`
- Builder loop trace: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/builder_loop_trace.json`
- Product brief: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/product_brief.json`
- Product spec: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/product_spec.json`
- Backend code: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/backend`
- Frontend code: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/frontend`
- Local data: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/data`
- Deterministic tests: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/tests`
- Prototype manifest: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app/_generator_context/prototype_manifest.json`

## Run Generated Product

```bash
cd "/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/02_generated_app"
cp .env.example .env.local
# edit .env.local and fill DEEPSEEK_API_KEY
./run_app.sh --port 8766
```

Open:

```text
http://127.0.0.1:8766
```

Check runtime configuration:

```bash
curl http://127.0.0.1:8766/api/runtime_status
```

Run CLI and evaluation:

```bash
python3 app.py --cli --max-cases 1
python3 -m unittest discover -s tests
python3 evaluation.py --max-cases 1
```

## Visuals

- Opportunity score chart: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/05_visuals/opportunity_score_chart.svg`
- Pipeline diagram: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/05_visuals/solution_pipeline_diagram.svg`
- Architecture diagram: `/Users/zhongxin/Documents/New project/j-enterprise-agent-scientist-v2-live-search/outputs/20260526_214921_manufacturing_chatbox_test_001/05_visuals/architecture_diagram.svg`
