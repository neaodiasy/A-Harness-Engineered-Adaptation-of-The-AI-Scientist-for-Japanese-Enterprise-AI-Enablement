let productSpec = null;
let uiConfig = null;
let appDesign = null;
let layoutConfig = null;
let interactionConfig = null;
let runtimeStatus = null;
let sampleCases = [];
let selectedCaseIndex = 0;
let currentOutput = null;
let selectedActionId = "";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function appendLog(message) {
  const log = document.getElementById("activityLog");
  const item = document.createElement("li");
  item.textContent = `${new Date().toLocaleTimeString()}  ${message}`;
  log.prepend(item);
}

function fieldElement(field) {
  const value = field.default || "";
  const label = `<label for="${field.key}">${field.label}</label>`;
  const control = field.type === "textarea"
    ? `<textarea id="${field.key}" data-field="${field.key}">${value}</textarea>`
    : `<input id="${field.key}" data-field="${field.key}" type="${field.type || "text"}" value="${value}">`;
  return `<div class="field">${label}${control}</div>`;
}

function collectCase() {
  const base = sampleCases[selectedCaseIndex] || {};
  const payload = {case_id: base.case_id || "manual_case"};
  document.querySelectorAll("[data-field]").forEach((element) => {
    payload[element.dataset.field] = element.value;
  });
  return payload;
}

function fillCase(sample) {
  Object.entries(sample).forEach(([key, value]) => {
    const element = document.querySelector(`[data-field="${key}"]`);
    if (element) {
      element.value = value;
    }
  });
}

function renderCaseQueue() {
  const queue = document.getElementById("caseQueue");
  if (!sampleCases.length) {
    queue.innerHTML = "<div class='muted'>No cases</div>";
    return;
  }
  queue.innerHTML = sampleCases.map((sample, index) => {
    const active = index === selectedCaseIndex ? " active" : "";
    const title = sample.customer_name || sample.request_owner || sample.case_id || `Case ${index + 1}`;
    const detail = sample.case_id || sample.household || sample.approval_owner || "";
    return `<button class="case-button${active}" data-case-index="${index}">${escapeHtml(title)}<span>${escapeHtml(detail)}</span></button>`;
  }).join("");
  queue.querySelectorAll("[data-case-index]").forEach((button) => {
    button.addEventListener("click", () => selectCase(Number(button.dataset.caseIndex)));
  });
}

function selectCase(index) {
  selectedCaseIndex = index;
  fillCase(sampleCases[index] || {});
  renderCaseQueue();
  appendLog(`Loaded ${sampleCases[index]?.case_id || "manual case"}.`);
}

function candidateName(item) {
  return item.name_ja || item.title_ja || item.equipment_name_ja || item.failure_mode_ja || item.property_id || item.area_id || "Candidate";
}

function candidateReason(item) {
  return item.reason_ja || item.summary_ja || item.risk_note_ja || item.summary || "";
}

function scaffoldId() {
  return uiConfig?.selected_scaffold_id || productSpec?.selected_scaffold_id || productSpec?.app_kind || "";
}

function uiSectionLabel(id, fallback) {
  const labels = uiConfig?.panel_labels || {};
  if (labels[id]) return labels[id];
  const section = (uiConfig?.ui_sections || []).find((item) => item.id === id || item.label === id);
  return section?.label || fallback;
}

function decisionVocabulary() {
  const scaffold = scaffoldId();
  if (scaffold === "customer_support_workbench") {
    return {
      nav: "Support Desk",
      intake: uiSectionLabel("inquiry_intake", "Inquiry Intake"),
      decision: uiSectionLabel("policy_evidence", "Policy Evidence"),
      count: "evidence items",
      empty: uiConfig?.empty_state_text?.policy_evidence || "No policy evidence retrieved yet.",
      firstColumn: "Evidence / workflow",
      scoreColumn: "Match",
      reasonColumn: "Support rationale",
      metric: "Evidence",
      draftTitle: uiSectionLabel("response_draft", "Response Draft"),
    };
  }
  if (scaffold === "risk_review_console") {
    return {nav: "Risk Review", intake: "Case Intake", decision: "Risk Checklist", count: "checks", empty: "No risk checks yet.", firstColumn: "Check", scoreColumn: "Risk", reasonColumn: "Finding", metric: "Checks", draftTitle: "Reviewer Notes"};
  }
  if (scaffold === "knowledge_assistant") {
    return {nav: "Knowledge", intake: "Query Intake", decision: "Document Evidence", count: "sources", empty: "No document evidence yet.", firstColumn: "Source", scoreColumn: "Fit", reasonColumn: "Evidence note", metric: "Sources", draftTitle: "Answer Draft"};
  }
  return {nav: "Recommendations", intake: "Case Intake", decision: "Candidate Comparison", count: "candidates", empty: "No candidates yet.", firstColumn: "Candidate", scoreColumn: "Score", reasonColumn: "Reason", metric: "Candidates", draftTitle: "Draft"};
}

function renderCandidates(output) {
  const areaItems = output.ranked_area_candidates || [];
  const propertyItems = output.ranked_property_candidates || [];
  const items = propertyItems.length ? propertyItems : areaItems;
  const vocab = decisionVocabulary();
  document.getElementById("candidateCount").textContent = `${items.length} ${vocab.count}`;
  if (!items.length) {
    return `<div class='empty-state'>${escapeHtml(vocab.empty)}</div>`;
  }
  return `
    <table class="candidate-table">
      <thead>
        <tr><th>Rank</th><th>${escapeHtml(vocab.firstColumn)}</th><th>${escapeHtml(vocab.scoreColumn)}</th><th>${escapeHtml(vocab.reasonColumn)}</th></tr>
      </thead>
      <tbody>
        ${items.slice(0, 6).map((item, index) => `
          <tr>
            <td>${index + 1}</td>
            <td><strong>${escapeHtml(candidateName(item))}</strong></td>
            <td><span class="score">${escapeHtml(item.score ?? "-")}</span></td>
            <td>${escapeHtml(candidateReason(item))}</td>
          </tr>
        `).join("")}
      </tbody>
    </table>
  `;
}

function renderSummary(output) {
  const classification = output.classification || {};
  const risk = output.risk || {};
  const evidence = output.evidence || [];
  const liveEvidence = evidence.filter((item) => String(item.retrieval_method || "").includes("live")).length;
  const vocab = decisionVocabulary();
  return `
    <div class="metric">Classification<strong>${escapeHtml(classification.label || "-")}</strong></div>
    <div class="metric">Confidence<strong>${escapeHtml(classification.confidence ?? "-")}</strong></div>
    <div class="metric">Risk<strong>${escapeHtml(risk.risk_level || "-")}</strong></div>
    <div class="metric">${escapeHtml(vocab.metric)}<strong>${(output.ranked_area_candidates || []).length + (output.ranked_property_candidates || []).length}</strong></div>
    <div class="metric">Live Sources<strong>${liveEvidence}</strong></div>
    <div class="metric">Send Allowed<strong>${output.send_allowed ? "Yes" : "No"}</strong></div>
  `;
}

function renderApproval(output) {
  const risk = output.risk || {};
  const packet = output.approval_packet || {};
  const missing = output.missing_information || [];
  const reasons = risk.risk_reasons || [];
  document.getElementById("approvalStatus").textContent = output.human_approval_required ? "Review Required" : "Ready";
  document.getElementById("approvalStatus").classList.toggle("warning", Boolean(output.human_approval_required));
  return `
    <p><strong>Owner:</strong> ${escapeHtml(packet.approval_owner || "-")}</p>
    <p><strong>Decision:</strong> ${escapeHtml((packet.decision_options || []).join(" / "))}</p>
    <p><strong>Boundary:</strong> send_allowed=${escapeHtml(output.send_allowed)}</p>
    <p><strong>Missing information</strong></p>
    <ul class="risk-list">${missing.slice(0, 7).map(item => `<li>${escapeHtml(item)}</li>`).join("") || "<li>-</li>"}</ul>
    <p><strong>Risk reasons</strong></p>
    <ul class="risk-list">${reasons.slice(0, 7).map(item => `<li>${escapeHtml(item)}</li>`).join("") || "<li>-</li>"}</ul>
  `;
}

function renderEvidence(output) {
  const evidence = output.evidence || [];
  document.getElementById("evidenceCount").textContent = `${evidence.length} sources`;
  if (!evidence.length) {
    return "<div class='empty-state'>No evidence yet.</div>";
  }
  return evidence.slice(0, 10).map((item) => {
    const title = escapeHtml(item.title || item.id || "Evidence");
    const url = item.url ? `<a href="${escapeHtml(item.url)}" target="_blank" rel="noreferrer">${title}</a>` : `<strong>${title}</strong>`;
    const method = item.retrieval_method || "local_evidence";
    return `
      <div class="evidence-item">
        <div>${url}</div>
        <div class="evidence-method">${escapeHtml(method)} · ${escapeHtml(item.id || "")}</div>
      </div>
    `;
  }).join("");
}

function renderReadiness(readiness) {
  const implemented = readiness.implemented_capabilities || [];
  const gaps = readiness.production_gaps || readiness.remaining_production_gaps || [];
  const milestones = readiness.recommended_next_milestones || readiness.recommended_milestones || [];
  const rows = [
    ...implemented.slice(0, 4).map(item => ["Built", item.name || item.capability || item.id || item]),
    ...gaps.slice(0, 3).map(item => ["Gap", item.name || item.capability || item.gap || item.id || item]),
    ...milestones.slice(0, 2).map(item => ["Next", item.name || item.milestone || item.id || item])
  ];
  if (!rows.length) {
    return "<p class='muted'>No readiness data.</p>";
  }
  return rows.map(([tag, text]) => `
    <div class="readiness-item">
      <span class="tag">${escapeHtml(tag)}</span>
      <span>${escapeHtml(text)}</span>
    </div>
  `).join("");
}

function renderDesignSections() {
  const target = document.getElementById("designSections");
  if (!target || !uiConfig) return;
  const sections = uiConfig.ui_sections || [];
  if (!sections.length) {
    target.innerHTML = "<div class='muted'>Default scaffold</div>";
    return;
  }
  target.innerHTML = sections.slice(0, 6).map((section) => `
    <div class="design-section-chip">
      <strong>${escapeHtml(section.label || section.id || "Section")}</strong><br>
      ${escapeHtml(section.purpose || "")}
    </div>
  `).join("");
}

function renderAssistantActions() {
  const target = document.getElementById("assistantActions");
  if (!target || !interactionConfig) return;
  const actions = interactionConfig.user_actions || [];
  if (!selectedActionId && actions.length) {
    selectedActionId = actions[0].id || "general";
  }
  target.innerHTML = actions.map((action) => {
    const id = action.id || action.label || "general";
    const active = id === selectedActionId ? " active" : "";
    return `<button class="action-chip${active}" data-action-id="${escapeHtml(id)}">${escapeHtml(action.label || id)}</button>`;
  }).join("");
  target.querySelectorAll("[data-action-id]").forEach((button) => {
    button.addEventListener("click", () => {
      selectedActionId = button.dataset.actionId;
      const action = actions.find((item) => (item.id || item.label) === selectedActionId) || {};
      document.getElementById("assistantMessage").value = action.prompt || document.getElementById("assistantMessage").value;
      renderAssistantActions();
    });
  });
}

function renderAssistantOutput(data) {
  const risk = data.risk || {};
  const evidence = data.used_evidence || [];
  const next = data.suggested_next_actions || [];
  return `
    <div><strong>Reply</strong></div>
    <div>${escapeHtml(data.reply_ja || "")}</div>
    ${data.api_error ? `<div class="runtime-error"><strong>Runtime diagnostic</strong><br>${escapeHtml(data.api_error)}</div>` : ""}
    <div class="evidence-method">Evidence: ${escapeHtml(evidence.join(", ") || "-")}</div>
    <div class="evidence-method">Risk: ${escapeHtml(risk.risk_level || "medium")} · send_allowed=${escapeHtml(data.send_allowed)}</div>
    <div><strong>Next actions</strong></div>
    <ul class="risk-list">${next.map(item => `<li>${escapeHtml(item)}</li>`).join("") || "<li>Human review</li>"}</ul>
    <div><strong>Approval note</strong></div>
    <div>${escapeHtml(data.approval_note || "")}</div>
  `;
}

function designList(items, key = "label", limit = 4) {
  const values = (items || []).slice(0, limit).map((item) => {
    if (typeof item === "string") return item;
    return item?.[key] || item?.id || item?.purpose || "";
  }).filter(Boolean);
  if (!values.length) return "<li>No generated items</li>";
  return values.map((item) => `<li>${escapeHtml(item)}</li>`).join("");
}

function actionPromptForSection(section) {
  const label = section.label || section.id || "this section";
  const purpose = section.purpose || "the selected enterprise workflow";
  return `Help me use the generated ${label} section for this case. Purpose: ${purpose}. Use evidence, local tools, risk rules, and human approval constraints.`;
}

function renderDynamicDesignPanels() {
  const target = document.getElementById("dynamicDesignPanels");
  if (!target || !appDesign) return;
  const sections = layoutConfig?.page_regions?.length ? layoutConfig.page_regions : (appDesign.ui_sections || []);
  const modules = appDesign.backend_modules || [];
  const tools = appDesign.local_tools || [];
  const modes = interactionConfig?.interaction_modes || appDesign.interaction_modes || [];
  document.getElementById("designSource").textContent = appDesign.design_source || "Design";
  const sectionCards = sections.slice(0, 6).map((section) => `
    <article class="design-card">
      <h3>${escapeHtml(section.label || section.id || "Generated section")}</h3>
      <p>${escapeHtml(section.purpose || "Generated by the build-time app design.")}</p>
      <button class="secondary-action design-ask" data-design-prompt="${escapeHtml(actionPromptForSection(section))}">Ask AI about this</button>
    </article>
  `).join("");
  const architectureCard = `
    <article class="design-card">
      <h3>Designed Backend</h3>
      <p>Modules and local tools selected for this enterprise scenario.</p>
      <ul>${designList(modules, "id", 5)}${designList(tools, "id", 4)}</ul>
    </article>
  `;
  const interactionCard = `
    <article class="design-card">
      <h3>Interaction Modes</h3>
      <p>Ways users can interact with DeepSeek inside this generated product.</p>
      <ul>${designList(modes, "label", 5)}</ul>
    </article>
  `;
  const surfaceCard = `
    <article class="design-card">
      <h3>${escapeHtml(layoutConfig?.interface_type || appDesign.frontend_experience?.interface_type || "Generated interface")}</h3>
      <p>${escapeHtml(layoutConfig?.primary_surface || appDesign.frontend_experience?.primary_surface || "Product surface selected by build-time design.")}</p>
      <ul>${designList(layoutConfig?.feature_cards || appDesign.product_feature_plan || [], "label", 5)}</ul>
    </article>
  `;
  target.innerHTML = surfaceCard + sectionCards + architectureCard + interactionCard;
  target.querySelectorAll("[data-design-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
      document.getElementById("assistantMessage").value = button.dataset.designPrompt || "";
      document.getElementById("assistant").scrollIntoView({behavior: "smooth", block: "start"});
    });
  });
}

function primitiveActionPrompt(primitive) {
  const label = primitive.label || primitive.id || primitive.type || "this component";
  const purpose = primitive.purpose || "the generated enterprise workflow";
  return `Use the ${label} component for the current case. Purpose: ${purpose}. Explain what the user should do next, cite evidence when possible, and keep human approval required.`;
}

function renderPrimitiveWorkspace() {
  const target = document.getElementById("primitiveWorkspace");
  if (!target || !layoutConfig) return;
  const primitives = layoutConfig.ui_primitives || [];
  if (!primitives.length) {
    target.innerHTML = "";
    return;
  }
  target.innerHTML = primitives.slice(0, 8).map((primitive) => {
    const span = primitive.span === "wide" ? " wide" : "";
    const type = primitive.type || primitive.id || "component";
    return `
      <article class="primitive-card${span}" data-primitive-type="${escapeHtml(type)}">
        <div class="primitive-meta">
          <span class="primitive-chip">${escapeHtml(type)}</span>
          <span class="primitive-chip">${escapeHtml(primitive.source || "generated")}</span>
        </div>
        <h3>${escapeHtml(primitive.label || primitive.id || "Generated component")}</h3>
        <p>${escapeHtml(primitive.purpose || "Generated from the build-time product blueprint.")}</p>
        <button class="secondary-action primitive-ask" data-primitive-prompt="${escapeHtml(primitiveActionPrompt(primitive))}">Use with AI</button>
      </article>
    `;
  }).join("");
  target.querySelectorAll("[data-primitive-prompt]").forEach((button) => {
    button.addEventListener("click", () => {
      document.getElementById("assistantMessage").value = button.dataset.primitivePrompt || "";
      document.getElementById("assistant").scrollIntoView({behavior: "smooth", block: "start"});
    });
  });
}

function applyGeneratedLayout() {
  const experience = layoutConfig || appDesign?.frontend_experience || {};
  const interfaceType = experience.interface_type || "operations_console";
  document.body.dataset.interface = interfaceType;
  const tokens = layoutConfig?.theme_tokens || {};
  const colors = tokens.colors || {};
  tokens.accent = tokens.accent || colors.primary || colors.accent;
  tokens.surface = tokens.surface || colors.surface || colors.background;
  tokens.sidebar = tokens.sidebar || colors.sidebar;
  if (tokens.accent) {
    document.documentElement.style.setProperty("--generated-accent", tokens.accent);
    document.querySelectorAll(".primary-action, .brand-mark").forEach((element) => {
      element.style.background = tokens.accent;
      element.style.borderColor = tokens.accent;
    });
  }
  if (tokens.surface) {
    document.body.style.background = tokens.surface;
  }
  if (tokens.sidebar) {
    document.querySelector(".sidebar").style.background = tokens.sidebar;
  }
  document.getElementById("workspaceLabel").textContent = `${interfaceType} · ${experience.layout_variant || "generated layout"}`;
  const order = [...(experience.emphasis_order || [])];
  if (interfaceType === "chat_console") {
    const withoutAssistant = order.filter((item) => item !== "assistant");
    order.splice(0, order.length, "assistant", ...withoutAssistant);
  }
  const orderMap = {intake: "intake", assistant: "assistant", recommendations: "recommendations", evidence: "evidence", draft: "draft-panel", approval: "approval", activity: "activityLog"};
  order.forEach((key, index) => {
    const idOrClass = orderMap[key] || key;
    const element = document.getElementById(idOrClass) || document.querySelector(`.${idOrClass}`);
    if (element) element.style.order = String(index - 10);
  });
}

function setApprovalControls(enabled) {
  ["approveDraft", "requestEdit", "escalate"].forEach((id) => {
    document.getElementById(id).disabled = !enabled;
  });
}

function renderResult(data) {
  currentOutput = data;
  document.getElementById("summaryCards").innerHTML = renderSummary(data);
  document.getElementById("rankings").innerHTML = renderCandidates(data);
  document.getElementById("approvalContent").innerHTML = renderApproval(data);
  document.getElementById("draftEditor").value = data.customer_or_business_draft_ja || data.recommendation_ja || "";
  document.getElementById("evidenceSources").innerHTML = renderEvidence(data);
  document.getElementById("output").textContent = JSON.stringify(data, null, 2);
  setApprovalControls(true);
}

async function load() {
  productSpec = await (await fetch("/api/product_spec")).json();
  const runtimeStatusResponse = await fetch("/api/runtime_status");
  runtimeStatus = runtimeStatusResponse.ok ? await runtimeStatusResponse.json() : null;
  const appDesignResponse = await fetch("/api/app_design");
  appDesign = appDesignResponse.ok ? await appDesignResponse.json() : null;
  const layoutConfigResponse = await fetch("/frontend/generated_layout_config.json");
  layoutConfig = layoutConfigResponse.ok ? await layoutConfigResponse.json() : null;
  const uiConfigResponse = await fetch("/frontend/generated_ui_config.json");
  uiConfig = uiConfigResponse.ok ? await uiConfigResponse.json() : null;
  const interactionConfigResponse = await fetch("/frontend/generated_interaction_config.json");
  interactionConfig = interactionConfigResponse.ok ? await interactionConfigResponse.json() : null;
  sampleCases = await (await fetch("/api/sample_cases")).json();
  const readinessResponse = await fetch("/api/product_readiness");
  if (readinessResponse.ok) {
    const readiness = await readinessResponse.json();
    document.getElementById("readiness").innerHTML = renderReadiness(readiness);
  }
  document.title = productSpec.product_name;
  document.getElementById("productName").textContent = productSpec.product_name;
  document.getElementById("pageTitle").textContent = productSpec.primary_action || "Case Workspace";
  document.getElementById("subtitle").textContent = productSpec.subtitle;
  document.getElementById("workspaceLabel").textContent = uiConfig?.selected_scaffold_id || uiConfig?.product_archetype || productSpec.selected_scaffold_id || productSpec.app_kind || "Operations Workspace";
  document.getElementById("run").textContent = uiConfig?.button_labels?.primary_action || productSpec.primary_action || "Generate Packet";
  if (runtimeStatus && !runtimeStatus.deepseek_api_key_present) {
    document.getElementById("status").textContent = "API Key Missing";
    appendLog("DeepSeek API key is not present in the app.py server environment.");
  }
  document.getElementById("assistantTitle").textContent = interactionConfig?.assistant_title || "AI Copilot";
  document.getElementById("assistantNotice").textContent = interactionConfig?.safety_notice || "AI output is draft-only and requires human approval.";
  document.getElementById("assistantMessage").placeholder = interactionConfig?.input_placeholder || "Ask the AI about this case.";
  document.getElementById("assistantMessage").value = (interactionConfig?.conversation_starters || [])[0] || "";
  const vocab = decisionVocabulary();
  document.getElementById("navIntake").textContent = vocab.intake;
  document.getElementById("navDecision").textContent = vocab.nav;
  document.getElementById("intakeTitle").textContent = vocab.intake;
  document.getElementById("decisionTitle").textContent = vocab.decision;
  document.querySelector(".draft-panel h2").textContent = vocab.draftTitle;
  document.getElementById("fields").innerHTML = productSpec.fields.map(fieldElement).join("");
  applyGeneratedLayout();
  renderDesignSections();
  renderAssistantActions();
  renderDynamicDesignPanels();
  renderPrimitiveWorkspace();
  renderCaseQueue();
  if (sampleCases.length) {
    selectCase(0);
  }
}

async function run() {
  const status = document.getElementById("status");
  const output = document.getElementById("output");
  const button = document.getElementById("run");
  status.textContent = "Running";
  button.disabled = true;
  setApprovalControls(false);
  output.textContent = "Running...";
  appendLog("Started local tools, runtime search, and DeepSeek drafting.");
  try {
    const response = await fetch("/api/recommend", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(collectCase())
    });
    const data = await response.json();
    renderResult(data);
    status.textContent = response.ok ? "Complete" : "Error";
    appendLog(response.ok ? "Generated review packet." : "Generation returned an error.");
  } catch (error) {
    output.textContent = String(error);
    status.textContent = "Error";
    appendLog("Runtime error.");
  } finally {
    button.disabled = false;
  }
}

async function askAssistant() {
  const button = document.getElementById("askAssistant");
  const target = document.getElementById("assistantOutput");
  button.disabled = true;
  target.classList.remove("empty-state");
  target.textContent = "Thinking with DeepSeek...";
  appendLog("Started interactive AI copilot request.");
  try {
    const response = await fetch("/api/assistant", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        action_id: selectedActionId,
        message: document.getElementById("assistantMessage").value,
        case: collectCase(),
        current_output: currentOutput
      })
    });
    const data = await response.json();
    target.innerHTML = response.ok ? renderAssistantOutput(data) : `<strong>Error</strong><br>${escapeHtml(data.error || JSON.stringify(data))}`;
    document.getElementById("output").textContent = JSON.stringify(data, null, 2);
    appendLog(response.ok ? "AI copilot response generated." : "AI copilot returned an error.");
  } catch (error) {
    target.textContent = String(error);
    appendLog("AI copilot runtime error.");
  } finally {
    button.disabled = false;
  }
}

document.getElementById("run").addEventListener("click", run);
document.getElementById("loadSample").addEventListener("click", () => {
  if (sampleCases.length) {
    selectCase((selectedCaseIndex + 1) % sampleCases.length);
  }
});
document.getElementById("askAssistant").addEventListener("click", askAssistant);
document.getElementById("useStarter").addEventListener("click", () => {
  const starters = interactionConfig?.conversation_starters || [];
  if (starters.length) {
    const current = document.getElementById("assistantMessage").value;
    const index = Math.max(0, starters.indexOf(current));
    document.getElementById("assistantMessage").value = starters[(index + 1) % starters.length];
  }
});
document.getElementById("approveDraft").addEventListener("click", () => appendLog("Draft marked approved in local review state."));
document.getElementById("requestEdit").addEventListener("click", () => appendLog("Edit request added in local review state."));
document.getElementById("escalate").addEventListener("click", () => appendLog("Escalation added in local review state."));
document.querySelectorAll(".nav-item").forEach((item) => {
  item.addEventListener("click", () => {
    document.querySelectorAll(".nav-item").forEach((nav) => nav.classList.remove("active"));
    item.classList.add("active");
  });
});

load();
