let productSpec = null;
let sampleCases = [];
let selectedCaseIndex = 0;
let currentOutput = null;

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

function renderCandidates(output) {
  const areaItems = output.ranked_area_candidates || [];
  const propertyItems = output.ranked_property_candidates || [];
  const items = propertyItems.length ? propertyItems : areaItems;
  document.getElementById("candidateCount").textContent = `${items.length} candidates`;
  if (!items.length) {
    return "<div class='empty-state'>No candidates yet.</div>";
  }
  return `
    <table class="candidate-table">
      <thead>
        <tr><th>Rank</th><th>Candidate</th><th>Score</th><th>Reason</th></tr>
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
  return `
    <div class="metric">Classification<strong>${escapeHtml(classification.label || "-")}</strong></div>
    <div class="metric">Confidence<strong>${escapeHtml(classification.confidence ?? "-")}</strong></div>
    <div class="metric">Risk<strong>${escapeHtml(risk.risk_level || "-")}</strong></div>
    <div class="metric">Candidates<strong>${(output.ranked_area_candidates || []).length + (output.ranked_property_candidates || []).length}</strong></div>
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
  document.getElementById("workspaceLabel").textContent = productSpec.app_kind || "Operations Workspace";
  document.getElementById("fields").innerHTML = productSpec.fields.map(fieldElement).join("");
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

document.getElementById("run").addEventListener("click", run);
document.getElementById("loadSample").addEventListener("click", () => {
  if (sampleCases.length) {
    selectCase((selectedCaseIndex + 1) % sampleCases.length);
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
