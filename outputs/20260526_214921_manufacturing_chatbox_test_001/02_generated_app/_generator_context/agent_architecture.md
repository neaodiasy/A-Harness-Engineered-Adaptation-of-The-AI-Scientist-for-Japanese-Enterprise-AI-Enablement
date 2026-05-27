# Maintenance Knowledge Chatbox Composition

## Selected Opportunity

**Maintenance Knowledge Chatbox**

Troubleshooting equipment alarms and finding maintenance procedures

## Inputs

- Enterprise user request or business case
- Target workflow description
- Available documents, tickets, policies, reports, or sample records
- Human approval and compliance constraints

## Outputs

- Recommended action or draft artifact
- Evidence packet with source IDs
- Risk level and risk reasons
- Human approval requirement
- Audit trace for review

## Selected Primitives

intake -> retrieval -> classification -> extraction -> checklist -> drafting -> risk_check -> human_approval -> audit_log -> evaluation

## Agent Steps

1. Normalize the business request, user role, target workflow, available data, and constraints.
2. Classify the workflow case type, urgency, sensitivity, and routing destination.
3. Retrieve supporting evidence from approved documents, manuals, policies, or evidence pack sources.
4. Extract structured fields from documents, forms, emails, or screenshots and mark missing fields.
5. Run completeness and process checks against required fields, approval rules, and next actions.
6. Draft the recommended response, report, checklist, or internal note using only available evidence.
7. Detect regulated, customer-facing, legal, financial, HR, safety, or irreversible decisions.
8. Assemble an approval packet and block external or irreversible action until a human approves.
9. Record evidence IDs, model output, risk reasons, human edits, and final decision.
10. Evaluate the workflow on synthetic business cases and trigger repair if checks fail.

## Knowledge Sources

- e: e
- v: v
- i: i
- d: d
- e: e
- n: n
- c: c
- e: e
- _: _
- o: o
- e: e
- c: c
- d: d
- _: _
- a: a
- i: i
- _: _
- l: l
- a: a
- b: b
- o: o
- u: u
- r: r
- _: _
- j: j
- a: a
- p: p
- a: a
- n: n
- _: _
- 2: 2
- 0: 0
- 2: 2
- 5: 5
- ,: ,
-  :
- e: e
- v: v
- i: i
- d: d
- e: e
- n: n
- c: c
- e: e
- _: _
- m: m
- e: e
- t: t
- i: i
- _: _
- g: g
- e: e
- n: n
- a: a
- i: i
- _: _
- d: d
- x: x
- _: _
- s: s
- k: k
- i: i
- l: l
- l: l
- s: s
- _: _
- 2: 2
- 0: 0
- 2: 2
- 4: 4
- ,: ,
-  :
- e: e
- v: v
- i: i
- d: d
- e: e
- n: n
- c: c
- e: e
- _: _
- i: i
- p: p
- a: a
- _: _
- d: d
- x: x
- _: _
- a: a
- l: l
- l: l
- _: _
- e: e
- m: m
- p: p
- l: l
- o: o
- y: y
- e: e
- e: e
- _: _
- e: e
- n: n
- a: a
- b: b
- l: l
- e: e
- m: m
- e: e
- n: n
- t: t
- enterprise_available_data: User-provided enterprise data assets

## Validation Checks

- Every recommendation cites evidence or declares evidence missing.
- Customer-facing, regulated, HR, legal, financial, safety, or irreversible outputs require human approval.
- Risk reasons are explicit and visible to the reviewer.
- The workflow can run on local sample data before production integration.
- Generated outputs preserve an audit trace.

## Human Approval Points

- Before sending external communication
- Before making regulated or irreversible decisions
- When confidence is low or evidence is missing
- When the case affects customers, employees, finance, legal, safety, or compliance

## Risk Mitigation

- Use evidence-gated generation.
- Prefer bounded PoC scope over broad automation.
- Keep human approval mandatory in pilot phase.
- Log all model outputs and human edits.
- Use synthetic and sanitized samples before real data integration.

## Evaluation Criteria

- Evidence relevance
- Task classification or routing correctness
- Completeness of required fields or checklist items
- Risk flag correctness
- Human approval enforcement
- Clarity and usefulness of generated output
- Traceability and auditability
