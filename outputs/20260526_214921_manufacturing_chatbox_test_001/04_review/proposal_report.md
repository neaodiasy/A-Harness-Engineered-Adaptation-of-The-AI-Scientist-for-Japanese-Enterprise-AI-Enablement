# Enterprise AI Enablement Proposal: Maintenance Knowledge Chatbox

## Executive Summary

This proposal recommends a bounded PoC for **Maintenance Knowledge Chatbox**. The system composes reusable primitives (intake, retrieval, classification, extraction, checklist, drafting, risk_check, human_approval, audit_log, evaluation) to create a customized agent workflow rather than selecting a fixed template.

## Evidence-Grounded Rationale

- OECD: Artificial Intelligence and the Labour Market in Japan: Japan faces labour and skills shortages, while AI adoption in workplaces remains comparatively low. The report frames AI as a way to improve productivity, job quality, and access to work when introduced safely.
- METI: Human Resources and Skills Required for DX Promotion in the Age of Generative AI: METI positions generative AI as a business opportunity for productivity, added value, and social issue solving, while emphasizing the human skills needed to use AI appropriately and proactively.
- IPA DX SQUARE: Enterprise DX and all-employee digital skill development examples: IPA DX case studies emphasize data utilization, human resource development, digital skill standards, and broad employee enablement.

## Selected Workflow

Troubleshooting equipment alarms and finding maintenance procedures

## Selected Opportunity and Feasibility

- Selected opportunity: Maintenance Knowledge Chatbox
- Feasibility score: 8.1
- Recommendation: advance
- Search refinement: strengthen_human_approval

## Agent Design

- Normalize the business request, user role, target workflow, available data, and constraints.
- Classify the workflow case type, urgency, sensitivity, and routing destination.
- Retrieve supporting evidence from approved documents, manuals, policies, or evidence pack sources.
- Extract structured fields from documents, forms, emails, or screenshots and mark missing fields.
- Run completeness and process checks against required fields, approval rules, and next actions.
- Draft the recommended response, report, checklist, or internal note using only available evidence.
- Detect regulated, customer-facing, legal, financial, HR, safety, or irreversible decisions.
- Assemble an approval packet and block external or irreversible action until a human approves.
- Record evidence IDs, model output, risk reasons, human edits, and final decision.
- Evaluate the workflow on synthetic business cases and trigger repair if checks fail.

## Primitive Architecture

Selected primitives: intake, retrieval, classification, extraction, checklist, drafting, risk_check, human_approval, audit_log, evaluation

The architecture is composed from stable harness primitives rather than a fixed agent template. It reflects the enterprise profile, available data, risk constraints, and Japan-specific approval needs.

## Human Approval and Risk Mitigation

- Before sending external communication
- Before making regulated or irreversible decisions
- When confidence is low or evidence is missing
- When the case affects customers, employees, finance, legal, safety, or compliance

## Sandbox Evaluation

Generated PoC evaluation passed 0/1 cases.
Pass rate: 0.0

## Next Steps

1. Validate sample cases with business owners.
2. Replace generated sample cases with sanitized enterprise examples.
3. Run a staff-reviewed pilot with audit logging.
4. Expand only after quality and governance thresholds are met.
