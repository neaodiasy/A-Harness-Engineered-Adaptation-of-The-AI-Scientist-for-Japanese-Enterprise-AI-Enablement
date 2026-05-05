const artifacts = [
  ["consultation", "Consultation"],
  ["evidence_pack", "Evidence Pack"],
  ["opportunities", "Opportunities"],
  ["feasibility", "Feasibility"],
  ["search_trace", "Search Trace"],
  ["selected_opportunity", "Selected Opportunity"],
  ["architecture", "Architecture"],
  ["primitive_trace", "Primitive Trace"],
  ["agent_design", "Agent Design JSON"],
  ["agent_design_md", "Agent Design MD"],
  ["prototype_manifest", "Prototype Manifest"],
  ["software_blueprint", "Software Blueprint"],
  ["implementation_plan", "Implementation Plan"],
  ["file_plan", "File Plan"],
  ["generation_trace", "Generation Trace"],
  ["repair_log", "Repair Log"],
  ["evaluation_results", "Evaluation"],
  ["proposal_report", "Proposal"],
  ["review", "Review"],
  ["architecture_diagram", "Architecture Diagram"],
];

const state = {
  activeArtifact: "consultation",
  isRunning: false,
};

const pipelineStages = [
  ["evidence_pack", "Evidence"],
  ["opportunities", "Ideas"],
  ["feasibility", "Feasibility"],
  ["search_trace", "Search"],
  ["architecture", "Architecture"],
  ["agent_design", "Design"],
  ["prototype_manifest", "Code"],
  ["software_blueprint", "Blueprint"],
  ["implementation_plan", "Plan"],
  ["evaluation_results", "Eval"],
  ["proposal_report", "Proposal"],
  ["review", "Review"],
  ["architecture_diagram", "Visual"],
];

function $(id) {
  return document.getElementById(id);
}

async function getJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || data.stderr || `Request failed: ${response.status}`);
  }
  return data;
}

function format(value) {
  if (typeof value === "string") return value;
  return JSON.stringify(value, null, 2);
}

function renderArtifactNav(availability = {}) {
  const list = $("artifactList");
  list.innerHTML = "";
  for (const [name, label] of artifacts) {
    const button = document.createElement("button");
    button.textContent = `${availability[name] === false ? "○" : "●"} ${label}`;
    button.className = name === state.activeArtifact ? "active" : "";
    button.addEventListener("click", () => loadArtifact(name));
    list.appendChild(button);
  }
}

async function refreshStatus() {
  const status = await getJson("/api/status");
  $("keyState").textContent = status.has_deepseek_key ? "DeepSeek" : "Local";
  $("artifactState").textContent = status.artifacts?.consultation ? "Ready" : "Empty";
  renderArtifactNav(status.artifacts || {});
  renderPipeline(status.artifacts || {});
}

async function loadArtifact(name) {
  state.activeArtifact = name;
  renderArtifactNav();
  const artifact = await getJson(`/api/artifact?name=${encodeURIComponent(name)}`);
  $("artifactTitle").textContent = artifacts.find(([id]) => id === name)?.[1] || name;
  $("artifactType").textContent = artifact.type;
  if (artifact.type === "svg") {
    const encoded = encodeURIComponent(artifact.content);
    $("artifactContent").innerHTML = `<img class="artifact-image" alt="${name}" src="data:image/svg+xml;charset=utf-8,${encoded}">`;
  } else {
    $("artifactContent").textContent = format(artifact.content);
  }
  if (name === "consultation" && artifact.content && typeof artifact.content === "object") {
    renderConsultation(artifact.content);
  }
  await refreshStatus();
}

function readProfile() {
  return {
    company_description: $("companyDescription").value.trim(),
    industry: $("industry").value.trim(),
    main_business: $("mainBusiness").value.trim(),
    ai_objective: $("aiObjective").value.trim(),
    pain_points: $("painPoints").value.trim(),
    available_data: $("availableData").value.trim(),
    constraints: $("constraints").value.trim(),
  };
}

function sleep(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

async function waitForRunArtifact(runId) {
  for (let attempt = 1; attempt <= 120; attempt += 1) {
    await sleep(1000);
    $("artifactContent").textContent = `Waiting for pipeline artifact... ${attempt}s`;
    const artifact = await getJson("/api/artifact?name=consultation");
    const content = artifact.content || {};
    if (content.run_id === runId) {
      return content;
    }
  }
  throw new Error("Timed out waiting for consultation_result.json to update.");
}

function renderConsultation(result) {
  const agent = result.recommended_agent || {};
  const feasibility = (result.feasibility_results || []).find((item) => item.name === agent.name) || {};
  const evaluation = result.evaluation_results || {};
  const review = result.review || {};
  const manifest = result.prototype_manifest || {};
  $("recommendedAgent").textContent = agent.name || "--";
  $("recommendationScore").textContent = feasibility.overall_score ?? agent.score ?? "--";
  $("consultRisk").textContent = agent.key_risk ? "Managed" : "--";
  $("evaluationScore").textContent = evaluation.total ? `${evaluation.passed}/${evaluation.total}` : "--";
  $("reviewScore").textContent = review.overall_score ?? "--";
  $("generatedApp").textContent = manifest.app_dir ? "Ready" : "--";
  $("consultSummary").textContent = [
    agent.expected_business_value,
    agent.japan_enterprise_fit,
    `Human approval: ${agent.human_approval_requirement || "required for sensitive actions"}`,
  ].filter(Boolean).join("\n\n");

  const list = $("opportunityList");
  list.innerHTML = "";
  const architecture = result.recommended_architecture || {};
  if (architecture.selected_primitives?.length) {
    const arch = document.createElement("article");
    arch.className = "opportunity-card architecture-card";
    arch.innerHTML = `
      <div class="opportunity-rank">A</div>
      <div>
        <h3>${architecture.name || "Composed Agent Architecture"}</h3>
        <p>${architecture.selected_primitives.join(" → ")}</p>
        <span>${architecture.why_this_composition || ""}</span>
      </div>
    `;
    list.appendChild(arch);
  }
  (result.opportunities || []).forEach((opportunity, index) => {
    const item = document.createElement("article");
    item.className = "opportunity-card";
    item.innerHTML = `
      <div class="opportunity-rank">${index + 1}</div>
      <div>
        <h3>${opportunity.name}</h3>
        <p>${opportunity.target_workflow}</p>
        <span>Score ${opportunity.score} · Evidence ${(opportunity.evidence_support || []).join(", ") || "n/a"} · ${opportunity.key_risk}</span>
      </div>
    `;
    list.appendChild(item);
  });
  $("roadmapText").textContent = (result.roadmap || []).map((item, index) => `${index + 1}. ${item}`).join("\n");
}

function renderPipeline(availability) {
  const strip = $("pipelineStrip");
  strip.innerHTML = "";
  for (const [artifact, label] of pipelineStages) {
    const item = document.createElement("button");
    item.className = `stage-pill ${availability[artifact] ? "done" : ""}`;
    item.textContent = label;
    item.addEventListener("click", () => loadArtifact(artifact));
    strip.appendChild(item);
  }
}

async function runConsultation() {
  if (state.isRunning) return;
  state.isRunning = true;
  const button = $("consultButton");
  button.disabled = true;
  button.textContent = "Running Analysis...";
  $("consultSummary").textContent = "Analyzing enterprise context...";
  $("recommendedAgent").textContent = "--";
  $("recommendationScore").textContent = "--";
  $("consultRisk").textContent = "--";
  $("evaluationScore").textContent = "--";
  $("reviewScore").textContent = "--";
  $("generatedApp").textContent = "--";
  try {
    const runId = `${Date.now()}-${Math.random().toString(16).slice(2)}`;
    const payload = { ...readProfile(), _run_id: runId };
    $("artifactTitle").textContent = "Running";
    $("artifactType").textContent = "status";
    $("artifactContent").textContent = "Sending request to /api/consult ...";
    const params = new URLSearchParams(payload);
    fetch(`/api/consult_start?${params.toString()}`, {
      method: "GET",
    }).catch((error) => {
      $("artifactContent").textContent = `Request failed before artifact polling completed: ${error.message}`;
    });
    const result = await waitForRunArtifact(runId);
    renderConsultation(result);
    $("artifactTitle").textContent = "Consultation";
    $("artifactType").textContent = "json";
    $("artifactContent").textContent = format(result);
    await refreshStatus();
  } catch (error) {
    $("consultSummary").textContent = `Analysis failed: ${error.message}`;
    $("artifactTitle").textContent = "Error";
    $("artifactType").textContent = "text";
    $("artifactContent").textContent = error.stack || error.message;
  } finally {
    state.isRunning = false;
    button.disabled = false;
    button.textContent = "Generate AI Enablement Analysis";
  }
}

function bindEvents() {
  $("refreshButton").addEventListener("click", async () => {
    await refreshStatus();
    await loadArtifact(state.activeArtifact);
  });
  $("consultButton").addEventListener("click", runConsultation);
}

async function init() {
  bindEvents();
  await refreshStatus();
  await loadArtifact("consultation");
}

init().catch((error) => {
  $("artifactContent").textContent = error.stack || error.message;
});
