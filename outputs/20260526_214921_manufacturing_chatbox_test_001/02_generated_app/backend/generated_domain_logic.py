from __future__ import annotations
from typing import Any

def adapt_case(case: dict, domain_data: dict, product_spec: dict) -> dict:
    query = case.get("query", "")
    query_lower = query.lower()

    intent = "unknown"
    if any(w in query_lower for w in ["alarm", "alm", "アラーム", "エラー"]):
        intent = "troubleshooting"
    elif any(w in query_lower for w in ["手順", "procedure", "sop", "方法", "how"]):
        intent = "procedure_lookup"
    elif any(w in query_lower for w in ["安全", "safety", "リスク", "risk", "停止", "インターロック"]):
        intent = "escalation_question"
    else:
        intent = "general"

    alarm_code = ""
    alarm_prefixes = ["alm-", "alarm-", "err-", "fault-"]
    for prefix in alarm_prefixes:
        idx = query_lower.find(prefix)
        if idx >= 0:
            end = idx + len(prefix)
            code_chars = []
            for ch in query[end:]:
                if ch.isalnum() or ch == "-":
                    code_chars.append(ch)
                else:
                    break
            alarm_code = prefix + "".join(code_chars)
            break
    if not alarm_code:
        for word in query.split():
            word_clean = word.strip(".,;:!?\"'").lower()
            if word_clean.startswith("alm-") and len(word_clean) > 4:
                alarm_code = word_clean.upper()

    safety_risk = False
    safety_terms = ["bypass", "無効", "override", "インターロック", "interlock", "restart", "再起動", "safety"]
    for term in safety_terms:
        if term in query_lower:
            safety_risk = True
            break

    requires_escalation = safety_risk or intent == "escalation_question"

    machine_model = case.get("machine_model", "")
    if not machine_model:
        machine_model = product_spec.get("default_machine_model", "")

    document_scope = product_spec.get("document_scope", [])
    if not document_scope:
        document_scope = domain_data.get("document_scope", [])

    adapted = {
        "original_query": query,
        "intent": intent,
        "alarm_code": alarm_code,
        "safety_risk": safety_risk,
        "requires_escalation": requires_escalation,
        "machine_model": machine_model,
        "document_scope": document_scope,
        "language": case.get("language", "ja"),
        "user_role": case.get("user_role", "operator"),
        "context_notes": case.get("context_notes", ""),
    }
    return adapted


def build_domain_prompt_context(adapted_case: dict, policy: dict, adapter: dict) -> dict:
    rules = []
    for rule in policy.get("rules", []):
        rules.append(rule)

    guardrails = []
    for g in policy.get("guardrails", []):
        guardrails.append(g)

    approval_triggers = []
    for trigger in policy.get("approval_triggers", []):
        approval_triggers.append(trigger)

    risk_terms = []
    for term in policy.get("risk_terms", []):
        risk_terms.append(term)

    language = adapted_case.get("language", "ja")
    language_instruction = ""
    if language == "ja":
        language_instruction = "Respond in Japanese. Optionally append a simplified English version."
    else:
        language_instruction = "Respond in " + language + "."

    escalation_note = ""
    if adapted_case.get("requires_escalation", False):
        escalation_note = "This query may require escalation to a human supervisor."

    alarm_note = ""
    alarm_code = adapted_case.get("alarm_code", "")
    if alarm_code:
        alarm_note = "Alarm code detected: " + alarm_code + ". Refer to alarm code tables for resolution steps."

    context = {
        "system_instructions": [
            "You are a maintenance knowledge assistant for factory engineers and operators.",
            "Always cite source document IDs and relevant sections.",
            "If evidence is missing, explicitly state it and recommend supervisor escalation.",
            "Do not provide final safety decisions or bypass instructions.",
            language_instruction,
            "For safety-critical or production-impacting actions, require human approval.",
            escalation_note,
            alarm_note,
        ],
        "rules": rules,
        "guardrails": guardrails,
        "approval_triggers": approval_triggers,
        "risk_terms": risk_terms,
        "adapted_intent": adapted_case.get("intent", "unknown"),
        "machine_model": adapted_case.get("machine_model", ""),
        "document_scope": adapted_case.get("document_scope", []),
        "requires_escalation": adapted_case.get("requires_escalation", False),
        "safety_risk": adapted_case.get("safety_risk", False),
        "adapter_config": {
            "model": adapter.get("model", ""),
            "temperature": adapter.get("temperature", 0.0),
            "max_tokens": adapter.get("max_tokens", 2048),
        },
    }
    return context
