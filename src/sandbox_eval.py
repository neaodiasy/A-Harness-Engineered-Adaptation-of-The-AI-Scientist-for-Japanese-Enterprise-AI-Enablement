from __future__ import annotations

import json
import os
import py_compile
import re
import subprocess
from pathlib import Path
from typing import Any, Dict

from src.ui_quality import check_frontend_responsiveness


REQUIRED_CHILD_FILES = [
    "README.md",
    "requirements.txt",
    "app.py",
    "tools.py",
    "domain_data.json",
    "product_spec.json",
    "product_requirements.json",
    "productization_blueprint.json",
    "productization_blueprint.md",
    "product_readiness.json",
    "production_readiness.md",
    "project_architecture.json",
    "file_manifest.json",
    "llm_app_design.json",
    "app_design.json",
    "generated_product_rules.md",
    "code_task_plan.json",
    "builder_loop_trace.json",
    "agent_spec.json",
    "generated_reasoning_policy.json",
    "generated_domain_logic_validation.json",
    "generated_layout_config.json",
    "generated_interaction_config.json",
    "evaluation_checklist.json",
    "llm_builder_review.json",
    "sample_cases.json",
    "evaluation.py",
    "knowledge_base.md",
    "pipeline_diagram.svg",
    "analysis_charts.svg",
    "backend/agent.py",
    "backend/api.py",
    "backend/data_store.py",
    "backend/guardrails.py",
    "backend/generated_reasoning_policy.py",
    "backend/generated_domain_adapter.py",
    "backend/generated_domain_logic.py",
    "backend/llm_client.py",
    "backend/web_search.py",
    "backend/recommendation_engine.py",
    "backend/tools.py",
    "frontend/index.html",
    "frontend/generated_ui_config.json",
    "frontend/generated_layout_config.json",
    "frontend/generated_interaction_config.json",
    "frontend/styles.css",
    "frontend/app.js",
    "data/areas.json",
    "data/properties.json",
    "data/sample_customers.json",
    "tests/test_recommendations.py",
]

SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{16,}"),
    re.compile(r"deepseek[_-]api[_-]key\\s*[:=]\\s*['\\\"][^'\\\"]+", re.IGNORECASE),
    re.compile(r"DEEPSEEK_API_KEY\\s*=\\s*['\\\"][^'\\\"]+"),
]


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value)


def _tail(value: Any, limit: int = 4000) -> str:
    return _text(value)[-limit:]


def _json_safe(value: Any) -> Any:
    if isinstance(value, bytes):
        return _text(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    return value


def _run_command(
    app_dir: Path,
    args: list[str],
    timeout: int,
    env_overrides: dict[str, str] | None = None,
) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONUNBUFFERED"] = "1"
    if env_overrides:
        env.update(env_overrides)
    completed = subprocess.run(
        args,
        cwd=str(app_dir),
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return {
        "args": args,
        "success": completed.returncode == 0,
        "returncode": completed.returncode,
        "stdout": _tail(completed.stdout),
        "stderr": _tail(completed.stderr),
    }


def _load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return fallback


def _looks_like_placeholder(match_text: str) -> bool:
    lowered = match_text.lower()
    return any(token in lowered for token in ("...", "your_key", "your-key", "<", "sk-...", "sk_xxx"))


def _check_no_secret_leakage(app_dir: Path) -> dict[str, Any]:
    findings = []
    env_key = os.environ.get("DEEPSEEK_API_KEY", "")
    for path in app_dir.rglob("*"):
        if path.is_dir() or path.suffix in {".pyc", ".png", ".jpg", ".jpeg", ".gif"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for pattern in SECRET_PATTERNS:
            match = pattern.search(text)
            if match and not _looks_like_placeholder(match.group(0)):
                findings.append(str(path.relative_to(app_dir)))
        if env_key and env_key in text:
            findings.append(str(path.relative_to(app_dir)))
    return {"success": not findings, "findings": sorted(set(findings))}


def _check_manifest(app_dir: Path) -> dict[str, Any]:
    manifest = _load_json(app_dir / "file_manifest.json", {})
    files = manifest.get("files", []) if isinstance(manifest, dict) else []
    missing = []
    for item in files:
        if not isinstance(item, dict):
            continue
        path = item.get("path")
        if path and not (app_dir / path).exists():
            missing.append(path)
    return {
        "name": "file_manifest_matches_disk",
        "success": bool(files) and not missing,
        "manifest_file_count": len(files),
        "missing_files": missing,
    }


def _check_project_shape(app_dir: Path) -> dict[str, Any]:
    required_dirs = ["backend", "frontend", "data", "tests"]
    missing_dirs = [name for name in required_dirs if not (app_dir / name).is_dir()]
    return {
        "name": "software_builder_project_shape",
        "success": not missing_dirs,
        "required_dirs": required_dirs,
        "missing_dirs": missing_dirs,
    }


INLINE_ONE_CASE_EVALUATION = """
import json
from pathlib import Path
from backend.agent import run_case
from backend.data_store import load_sample_cases
from evaluation import evaluate_output
case = load_sample_cases()[0]
output = run_case(case)
checks = evaluate_output(case, output)
result = {'case_id': case['case_id'], 'passed': all(checks.values()), 'checks': checks, 'output': output}
summary = {'success': result['passed'], 'passed': 1 if result['passed'] else 0, 'total': 1, 'pass_rate': 1.0 if result['passed'] else 0.0}
Path('evaluation_results.json').write_text(json.dumps([result], ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')
Path('evaluation_summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\\n', encoding='utf-8')
print(json.dumps({'summary': summary, 'checks': checks}, ensure_ascii=False, indent=2))
"""


def run_generated_evaluation(app_dir: Path, timeout: int = 600) -> Dict[str, Any]:
    """Run robust sandbox checks for a generated child agent app using real API mode."""
    app_dir = Path(app_dir)
    app_dir.mkdir(parents=True, exist_ok=True)
    checks: list[dict[str, Any]] = []

    missing_files = [name for name in REQUIRED_CHILD_FILES if not (app_dir / name).exists()]
    checks.append({
        "name": "required_files_exist",
        "success": not missing_files,
        "missing_files": missing_files,
    })
    checks.append(_check_project_shape(app_dir))
    checks.append(_check_manifest(app_dir))
    checks.append(check_frontend_responsiveness(app_dir))
    smoke_env = {
        "GENERATED_APP_LIVE_SEARCH": os.environ.get("GENERATED_APP_LIVE_SEARCH", "1"),
        "GENERATED_APP_SEARCH_QUERY_LIMIT": os.environ.get("SANDBOX_GENERATED_APP_SEARCH_QUERY_LIMIT", "1"),
        "GENERATED_APP_SEARCH_RESULTS_PER_QUERY": os.environ.get("SANDBOX_GENERATED_APP_SEARCH_RESULTS_PER_QUERY", "1"),
        "GENERATED_APP_SEARCH_DELAY_SECONDS": os.environ.get("SANDBOX_GENERATED_APP_SEARCH_DELAY_SECONDS", "0"),
    }

    compile_errors = []
    for path in sorted(app_dir.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            compile_errors.append({"file": str(path.relative_to(app_dir)), "error": str(exc)})
    checks.append({
        "name": "python_syntax_compiles",
        "success": not compile_errors,
        "errors": compile_errors,
    })

    secret_check = _check_no_secret_leakage(app_dir)
    secret_check["name"] = "no_api_key_or_secret_leakage"
    checks.append(secret_check)

    try:
        import_result = _run_command(app_dir, ["python3", "-c", "import app; print('import_ok')"], timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        import_result = {
            "success": False,
            "error": f"app import timed out after {timeout} seconds",
            "stdout": _tail(exc.stdout),
            "stderr": _tail(exc.stderr),
        }
    import_result["name"] = "app_imports"
    checks.append(import_result)

    generated_artifact_result = _run_command(
        app_dir,
        [
            "python3",
            "-c",
            (
                "import json;"
                "from backend.generated_reasoning_policy import GENERATED_REASONING_POLICY as p;"
                "from backend.generated_domain_adapter import GENERATED_DOMAIN_ADAPTER as a;"
                "from backend.generated_domain_logic import adapt_case, build_domain_prompt_context;"
                "allowed={'recommendation_workbench','customer_support_workbench','risk_review_console','knowledge_assistant','approval_workbench','domain_operations_workbench'};"
                "design=json.load(open('llm_app_design.json'));"
                "ui=json.load(open('frontend/generated_ui_config.json'));"
                "layout=json.load(open('frontend/generated_layout_config.json'));"
                "ic=json.load(open('frontend/generated_interaction_config.json'));"
                "ev=json.load(open('evaluation_checklist.json'));"
                "rv=json.load(open('llm_builder_review.json'));"
                "assert p.get('human_approval_required') is True;"
                "assert p.get('send_allowed') is False;"
                "assert a.get('adapter_version');"
                "assert design.get('selected_scaffold_id') in allowed;"
                "assert ui.get('ui_sections');"
                "assert layout.get('interface_type');"
                "assert layout.get('ui_primitives');"
                "assert layout.get('human_approval_required') is True;"
                "assert layout.get('send_allowed') is False;"
                "assert ic.get('user_actions');"
                "assert ic.get('human_approval_required') is True;"
                "assert ic.get('send_allowed') is False;"
                "assert ev.get('approval_checks');"
                "assert 'passed' in rv;"
                "adapted=adapt_case({'case_id':'sandbox_case'}, {'domain_candidates':[], 'item_records':[]}, {'selected_scaffold_id':design.get('selected_scaffold_id')});"
                "assert isinstance(adapted, dict);"
                "ctx=build_domain_prompt_context(adapted, p, a);"
                "assert isinstance(ctx, dict);"
                "print('generated_artifacts_ok')"
            ),
        ],
        timeout=timeout,
    )
    generated_artifact_result["name"] = "generated_llm_design_artifacts_import_and_validate"
    checks.append(generated_artifact_result)

    try:
        unit_result = _run_command(app_dir, ["python3", "-m", "unittest", "discover", "-s", "tests"], timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        unit_result = {
            "success": False,
            "error": f"unit tests timed out after {timeout} seconds",
            "stdout": _tail(exc.stdout),
            "stderr": _tail(exc.stderr),
        }
    unit_result["name"] = "deterministic_unit_tests_pass"
    checks.append(unit_result)

    try:
        cli_result = _run_command(
            app_dir,
            ["python3", "app.py", "--cli", "--max-cases", "1"],
            timeout=timeout,
            env_overrides=smoke_env,
        )
    except subprocess.TimeoutExpired as exc:
        cli_result = {
            "success": False,
            "error": f"app.py --cli --max-cases 1 timed out after {timeout} seconds",
            "stdout": _tail(exc.stdout),
            "stderr": _tail(exc.stderr),
        }
    cli_result["name"] = "api_cli_runs"
    checks.append(cli_result)

    try:
        evaluation_path = app_dir / "evaluation.py"
        supports_case_id = "--case-id" in evaluation_path.read_text(encoding="utf-8")
        evaluation_args = (
            ["python3", "evaluation.py", "--max-cases", "1"]
            if supports_case_id
            else ["python3", "-c", INLINE_ONE_CASE_EVALUATION]
        )
        evaluation_result = _run_command(
            app_dir,
            evaluation_args,
            timeout=timeout,
            env_overrides=smoke_env,
        )
        if not supports_case_id:
            evaluation_result["compatibility_mode"] = "inline_one_case_evaluator_for_legacy_generated_app"
    except subprocess.TimeoutExpired as exc:
        evaluation_result = {
            "success": False,
            "error": f"evaluation.py --max-cases 1 timed out after {timeout} seconds",
            "stdout": _tail(exc.stdout),
            "stderr": _tail(exc.stderr),
        }
    evaluation_result["name"] = "api_evaluation_runs"
    checks.append(evaluation_result)

    evaluation_summary = _load_json(app_dir / "evaluation_summary.json", {})
    evaluation_results = _load_json(app_dir / "evaluation_results.json", [])
    checks.append({
        "name": "evaluation_results_indicate_success",
        "success": bool(evaluation_summary.get("success")),
        "evaluation_summary": evaluation_summary,
    })

    success = all(bool(check.get("success")) for check in checks)
    result: Dict[str, Any] = {
        "success": success,
        "mode": "real_deepseek_api",
        "timeout_seconds": timeout,
        "app_dir": str(app_dir.resolve()),
        "checks": checks,
        "evaluation_summary": evaluation_summary,
        "evaluation_results": evaluation_results,
        "passed": evaluation_summary.get("passed", 0),
        "total": evaluation_summary.get("total", 0),
        "pass_rate": evaluation_summary.get("pass_rate", 0),
    }

    result = _json_safe(result)
    report_path = app_dir / "sandbox_report.json"
    report_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return result
