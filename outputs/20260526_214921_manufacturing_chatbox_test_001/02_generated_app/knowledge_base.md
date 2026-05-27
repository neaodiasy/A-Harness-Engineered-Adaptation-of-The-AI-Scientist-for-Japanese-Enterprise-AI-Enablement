# Nagoya Precision Components AI Workbench Knowledge Base

## Enterprise Context

- Industry: manufacturing
- Main business: The company manufactures precision mechanical components for industrial equipment. Factory engineers and line supervisors maintain CNC machines, inspection devices, and assembly lines. Staff need to quickly search maintenance manuals, SOPs, troubleshooting notes, past incident reports, and quality-control procedures.
- AI objective:
- Constraints: ['the system must not make final safety decisions', 'the system must not instruct staff to bypass safety interlocks', 'the system must not approve machine restart after a serious alarm', 'human supervisor approval is required for safety-critical, quality-critical, or production-impacting actions', 'the system must cite document evidence or say when evidence is missing', 'the system should answer in clear Japanese and optionally simple English for trainees']

## Selected Opportunity

- Name: Maintenance Knowledge Chatbox
- Target workflow: Troubleshooting equipment alarms and finding maintenance procedures
- Capability: RAG-powered QA over maintenance manuals, alarm codes, and incident reports, with source citations
- Expected business value: Reduce downtime and repetitive senior engineer interruptions; speed up new operator onboarding
- Key risk: Incorrect retrieval due to poor document quality or ambiguous queries

## Operating Rules

- Always run deterministic local tools before DeepSeek drafting.
- Use concrete candidate names from local tool results.
- Never use placeholder recommendations such as Candidate A / Candidate B / エリアA.
- Treat generated output as decision support, not a final legal, financial, safety, employment, medical, or regulated-domain conclusion.
- Keep human_approval_required true and send_allowed false.
- Use concrete local tool candidate names from the loaded domain data when relevant.
- Use source evidence as supporting context, not as final authority.
- Do not make final legal, financial, safety, employment, medical, or regulated decisions.
- Escalate ambiguous, irreversible, customer-facing, or regulated outputs to a human owner.

## Required Human Checks

- Current source evidence and internal policy.
- Domain-specific risk boundaries and approval owner.
- Missing information surfaced by the local tools.
- Human reviewer edits before any customer-facing or operationally consequential use.
- Customer-facing use requires approved source evidence and human review.
- Approval boundary, risk owner, and current policy evidence must be verified.
- Financial, investment, pricing, or payment advice requires human approval.
- Safety-critical or irreversible operational actions require an accountable human owner.
- Check that the domain pack was reviewed by a human owner before installation.
- Verify that risk boundaries and approval rules match the actual enterprise context.
- Confirm that sample cases do not include confidential or personal data.
- Run schema validation and generated-app smoke tests before accepting the pack.
