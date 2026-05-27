# Product Rules & Design Document
**Nagoya Precision Components Maintenance Knowledge Assistant**
*Scaffolded knowledge assistant – not production-ready*

## 1. Product Purpose
AI-powered internal chat assistant for factory maintenance staff. Answers technical questions by retrieving, summarising, and citing evidence from machine manuals, SOPs, alarm‑code tables, and incident reports. Outputs are delivered in Japanese (primary) with optional simplified English.

## 2. Target Users
- Factory engineers
- Line supervisors
- Maintenance technicians
- Quality‑control staff
- New operators

## 3. Selected Opportunity
**Maintenance Knowledge Chatbox** – Troubleshooting equipment alarms and finding maintenance procedures.
*Business value:* reduce downtime, off‑load repetitive senior engineer interruptions, speed up new operator onboarding.

## 4. Product Archetype
`knowledge_assistant` – chat‑based interface with mandatory evidence panels, answer drafts, uncertainty flags, and human‑approval workflow.

## 5. UI Sections
| Section | Purpose |
|---|---|
| `chat_thread` | Primary conversation interface (questions & answers) |
| `document_evidence_panel` | Display retrieved documents with highlighted excerpts and source links |
| `answer_draft` | AI‑generated answer draft before final delivery |
| `uncertainty_flags` | Highlight missing information, low confidence, or gaps |
| `approval_panel` | Supervisor decision UI for escalated/risky cases |
| `risk_checklist` | Structured list of safety, quality, and production risks |

## 6. Backend Modules
- `knowledge_lookup` – retrieve relevant document chunks
- `evidence_summarizer` – condense retrieved evidence into concise context
- `answer_drafter` – compose answer with numbered steps and citations
- `guardrails` – enforce citation, uncertainty flagging, and forbidden‑instruction blocks
- `escalation_checker` – detect safety‑critical, quality‑critical, or ambiguous queries
- `audit_logger` – record every query, answer, and human approval event

## 7. Local Tools
- `doc_lookup` – search across document stores
- `evidence_matcher` – match query to relevant passages
- `alarm_code_resolver` – map alarm codes (e.g. ALM‑xxx) to known steps
- `sop_retriever` – fetch full SOPs for multi‑step procedures
- `incident_report_searcher` – find similar past incidents

## 8. Evidence Usage
- Every answer **must** cite source document IDs and relevant sections.
- When evidence is missing, low‑confidence, or contradictory, the system **must** explicitly flag the gap and never fabricate.
- Source documents: machine maintenance manuals, SOP documents, alarm code tables, past incident reports, quality inspection checklists, replacement parts notes, training FAQs.

## 9. Risk Rules & Forbidden Claims
**Rules**
- Cite evidence in every answer.
- Flag uncertainty and missing information.
- Escalate ambiguous or safety‑critical queries to a human supervisor.
- Never approve a machine restart after a serious alarm without human review.
- Never instruct bypass of safety interlocks.
- Never send external communication.

**Forbidden Claims**
- This scaffolded app is **not** production‑ready.
- It does **not** provide final safety, legal, financial, medical, or regulated decisions.
- No guarantee of correctness; human reviewer must validate every critical output.

## 10. Human Approval Policy
Approval is **required** for any output that involves:
- Safety‑critical actions
- Quality‑critical decisions
- Production‑impacting recommendations
- Machine restart after serious alarm
- Bypass of safety interlocks
- Missing evidence or low confidence

**Approval packet** includes: answer draft, full evidence sources, risk flags, and a mandatory reviewer decision (approve/edit/reject).
*Reviewer role:* factory supervisor or delegated knowledge owner.
No output may be sent externally or acted upon until approval is recorded.

## 11. Evaluation Requirements
The system is evaluated via **synthetic test cases** with known evidence and **regular log audits**.
Checks:
- Answer is evidence‑grounded and citations are present.
- Uncertainty is correctly flagged.
- Safety‑critical cases trigger escalation.
- Human approval is enforced for all defined triggers.
- Answers default to Japanese; optional English appended.
- No forbidden instructions (bypass safety, restart without approval) appear in outputs.

## 12. Sandbox Expectations
- This application is a **scaffolded proof‑of‑concept**, not a production system.
- It runs in an isolated sandbox with synthetic/static document stores and no live factory data.
- The domain pack was auto‑generated and requires **human review** before installation in any real environment.
- All risk boundaries, approval rules, and evidence sources must be verified and adapted to the actual enterprise context before any operational use.
- Secrets must **never** be committed to the sandbox repository.
