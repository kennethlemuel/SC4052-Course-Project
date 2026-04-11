const chatLog = document.querySelector("#chat-log");
const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");

const refreshButton = document.querySelector("#refresh-btn");
const tonightButton = document.querySelector("#tonight-btn");
const panicButton = document.querySelector("#panic-btn");

const examTitle = document.querySelector("#exam-title");
const examDate = document.querySelector("#exam-date");
const readinessScore = document.querySelector("#readiness-score");
const targetScore = document.querySelector("#target-score");
const confidenceGap = document.querySelector("#confidence-gap");
const confidenceRisk = document.querySelector("#confidence-risk");
const nextFocus = document.querySelector("#next-focus");
const examCountdown = document.querySelector("#exam-countdown");

const academicForm = document.querySelector("#academic-form");
const itemTitle = document.querySelector("#item-title");
const itemSubject = document.querySelector("#item-subject");
const itemKind = document.querySelector("#item-kind");
const itemDate = document.querySelector("#item-date");
const academicList = document.querySelector("#academic-list");

const overviewPlan = document.querySelector("#overview-plan");
const overviewWeakness = document.querySelector("#overview-weakness");
const weaknessMap = document.querySelector("#weakness-map");
const planOutput = document.querySelector("#plan-output");
const panicOutput = document.querySelector("#panic-output");
const recallDeck = document.querySelector("#recall-deck");
const checkinTopic = document.querySelector("#checkin-topic");
const checkinResult = document.querySelector("#checkin-result");
const materialsOutput = document.querySelector("#materials-output");

const planForm = document.querySelector("#plan-form");
const planMinutes = document.querySelector("#plan-minutes");
const panicForm = document.querySelector("#panic-form");
const panicHorizon = document.querySelector("#panic-horizon");
const checkinForm = document.querySelector("#checkin-form");
const checkinConfidence = document.querySelector("#checkin-confidence");
const checkinQuiz = document.querySelector("#checkin-quiz");
const checkinMinutes = document.querySelector("#checkin-minutes");
const materialsForm = document.querySelector("#materials-form");
const materialsTitle = document.querySelector("#materials-title");
const materialsText = document.querySelector("#materials-text");
const materialsFile = document.querySelector("#materials-file");
const materialsFileName = document.querySelector("#materials-file-name");
const materialsFileStatus = document.querySelector("#materials-file-status");

const timerDisplay = document.querySelector("#timer-display");
const timerDisplayText = document.querySelector("#timer-display-text");
const timerStatus = document.querySelector("#timer-status");
const timerStart = document.querySelector("#timer-start");
const timerReset = document.querySelector("#timer-reset");
const timerEditor = document.querySelector("#timer-editor");
const timerMinutesInput = document.querySelector("#timer-minutes-input");
const timerApply = document.querySelector("#timer-apply");
const timerMinus = document.querySelector("#timer-minus");
const timerPlus = document.querySelector("#timer-plus");

const pageButtons = document.querySelectorAll("[data-page]");
const pages = document.querySelectorAll(".page");

const TEXT_FILE_PATTERN = /\.(txt|md|csv|json)$/i;

let timerInterval = null;
let totalTimerSeconds = Number(timerMinutesInput.value) * 60;
let remainingTimerSeconds = totalTimerSeconds;

function wait(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function showPage(pageName) {
  pageButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.page === pageName);
  });
  pages.forEach((page) => {
    const shouldShow = page.id === `page-${pageName}`;
    page.classList.toggle("active", shouldShow);
    page.classList.toggle("hidden", !shouldShow);
  });
}

function createMessageNode(role) {
  const node = document.createElement("div");
  node.className = `message ${role} entering`;
  chatLog.appendChild(node);
  chatLog.scrollTop = chatLog.scrollHeight;
  window.requestAnimationFrame(() => node.classList.remove("entering"));
  return node;
}

function addMessage(role, text) {
  const node = createMessageNode(role);
  node.textContent = text;
  return node;
}

function addPendingAssistantMessage() {
  const node = createMessageNode("assistant pending");
  node.innerHTML = `
    <span class="pending-label">Thinking about your study question</span>
    <span class="thinking-dots" aria-hidden="true"><span></span><span></span><span></span></span>
  `;
  return node;
}

async function revealAssistantMessage(node, text) {
  node.classList.remove("pending");
  node.textContent = "";
  const lines = text.split("\n");
  for (let index = 0; index < lines.length; index += 1) {
    node.textContent += `${index === 0 ? "" : "\n"}${lines[index]}`;
    chatLog.scrollTop = chatLog.scrollHeight;
    await wait(index === 0 ? 80 : 55);
  }
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return response.json();
}

async function postForm(url, formData) {
  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });
  return response.json();
}

function renderStack(target, items, renderer, emptyText = "Nothing to show right now.") {
  target.innerHTML = "";
  if (!items || items.length === 0) {
    const node = document.createElement("div");
    node.className = "card muted";
    node.textContent = emptyText;
    target.appendChild(node);
    return;
  }
  items.forEach((item, index) => {
    const node = renderer(item);
    node.classList.add("stagger-in");
    node.style.setProperty("--stagger-index", index);
    target.appendChild(node);
  });
}

function weaknessCard(item) {
  const node = document.createElement("div");
  node.className = "card risk-card";
  node.innerHTML = `
    <div class="card-topline">
      <strong>${item.title}</strong>
      <span class="pill ${item.status_label.toLowerCase()}">${item.status_label}</span>
    </div>
    <div class="muted">${item.module}</div>
    <div class="meter"><span style="width:${item.mastery}%"></span></div>
    <div class="card-meta">
      <span>Understanding ${item.mastery}</span>
      <span>Confidence ${item.confidence}</span>
      <span>Risk ${item.risk_score}</span>
    </div>
    <div>${item.reason}</div>
  `;
  return node;
}

function planCard(item) {
  const node = document.createElement("div");
  node.className = "card";
  node.innerHTML = `
    <div class="card-topline">
      <strong>${item.title}</strong>
      <span class="pill neutral">${item.minutes} min</span>
    </div>
    <div class="muted">${item.module}</div>
    <div>${item.mode}</div>
    <div class="muted">${item.reason}</div>
  `;
  return node;
}

function recallCard(item) {
  const node = document.createElement("div");
  node.className = "card";
  node.innerHTML = `
    <div class="card-topline">
      <strong>${item.topic}</strong>
      <span class="pill accent">Practice</span>
    </div>
    <div>${item.prompt}</div>
    <div class="muted">${item.check}</div>
  `;
  return node;
}

function simpleCard(title, detail, extra = "") {
  const node = document.createElement("div");
  node.className = "card";
  node.innerHTML = `<strong>${title}</strong><div>${detail}</div>${extra ? `<div class="muted">${extra}</div>` : ""}`;
  return node;
}

function academicItemCard(item, activeItemId) {
  const node = document.createElement("div");
  node.className = "summary-item";
  const buttonLabel = item.id === activeItemId ? "Current focus" : "Set as focus";
  const disabled = item.id === activeItemId ? "disabled" : "";
  node.innerHTML = `
    <div class="card-topline">
      <strong>${item.title}</strong>
      <span class="pill neutral">${item.label}</span>
    </div>
    <div class="muted">${item.subject} • ${item.days_left} day${item.days_left === 1 ? "" : "s"} left</div>
    <div class="card-meta">
      <span>Due ${item.due_date}</span>
    </div>
    <button class="secondary focus-switch" data-item-id="${item.id}" ${disabled}>${buttonLabel}</button>
  `;
  return node;
}

function renderMetrics(metrics) {
  examTitle.textContent = metrics.focus_title;
  examDate.textContent = `${metrics.focus_kind} • ${metrics.focus_subject} • due ${metrics.focus_date}`;
  readinessScore.textContent = `${metrics.readiness_score}/100`;
  targetScore.textContent = `${metrics.target_readiness}/100`;
  confidenceGap.textContent = `${metrics.confidence_gap} pts`;
  confidenceRisk.textContent = `${metrics.confidence_risk_topic} needs a more honest check.`;
  nextFocus.textContent = metrics.next_focus;
  examCountdown.textContent = `${metrics.days_left} day${metrics.days_left === 1 ? "" : "s"} left`;
}

function renderPanic(data) {
  panicOutput.innerHTML = "";
  panicOutput.appendChild(
    simpleCard(
      data.headline,
      data.triage_note,
      data.skip.length ? `Ignore for now: ${data.skip.join(", ")}` : ""
    )
  );
  data.must_cover.forEach((item, index) => {
    const node = simpleCard(`${item.order}. ${item.title}`, `${item.minutes} min`, item.reason);
    node.classList.add("stagger-in");
    node.style.setProperty("--stagger-index", index + 1);
    panicOutput.appendChild(node);
  });
}

function populateTopicOptions(topics) {
  const current = checkinTopic.value;
  checkinTopic.innerHTML = "";
  topics.forEach((topic) => {
    const option = document.createElement("option");
    option.value = topic.id;
    option.textContent = `${topic.title} (${topic.status_label})`;
    if (topic.id === current) {
      option.selected = true;
    }
    checkinTopic.appendChild(option);
  });
}

function renderRecentMaterials(items) {
  renderStack(
    materialsOutput,
    items,
    materialCard,
    "No materials added yet."
  );
}

function materialCard(item) {
  const node = document.createElement("div");
  node.className = "card material-card";
  const topics = item.topics?.length ? item.topics.join(", ") : "No derived topics yet.";
  node.innerHTML = `
    <div class="card-topline">
      <strong>${item.title}</strong>
      <button class="material-delete-button" data-material-id="${item.id}" type="button">Delete</button>
    </div>
    <div>${topics}</div>
    <div class="muted">Imported ${new Date(item.created_at).toLocaleString()}</div>
  `;
  return node;
}

function renderAcademicItems(upcomingItems, activeItemId) {
  renderStack(
    academicList,
    upcomingItems,
    (item) => academicItemCard(item, activeItemId),
    "No other exams or assignments yet."
  );
}

function renderDashboard(data) {
  renderMetrics(data.metrics);
  renderStack(overviewPlan, data.plan.slice(0, 2), planCard, "No plan yet.");
  renderStack(overviewWeakness, data.weakness_map.slice(0, 3), weaknessCard, "No weak topics yet.");
  renderStack(weaknessMap, data.weakness_map, weaknessCard, "No topics yet.");
  renderStack(planOutput, data.plan, planCard, "No plan yet.");
  renderPanic(data.panic_mode);
  renderStack(recallDeck, data.recall_deck, recallCard, "No practice prompts yet.");
  populateTopicOptions(data.topics);
  renderRecentMaterials(data.materials);
  renderAcademicItems(data.upcoming_items, data.focus_item?.id);
}

async function loadDashboard() {
  const response = await fetch("/study/dashboard");
  const data = await response.json();
  renderDashboard(data);
}

async function handleCoachQuery(text) {
  addMessage("user", text);
  const pendingNode = addPendingAssistantMessage();
  const data = await postJson("/assistant/query", { text });
  await revealAssistantMessage(pendingNode, data.reply);
  if (data.plan) {
    renderStack(planOutput, data.plan.plan, planCard);
    renderStack(overviewPlan, data.plan.plan.slice(0, 2), planCard);
  }
  if (data.panic_mode) {
    renderPanic(data.panic_mode);
  }
}

function updateMaterialFileStatus(text, isError = false) {
  materialsFileStatus.textContent = text;
  materialsFileStatus.classList.toggle("error-copy", isError);
}

function updateMaterialFileName(text, isMuted = true) {
  materialsFileName.textContent = text;
  materialsFileName.classList.toggle("muted", isMuted);
}

function formatTimer(seconds) {
  const safe = Math.max(0, seconds);
  const minutes = Math.floor(safe / 60);
  const remainder = safe % 60;
  return `${String(minutes).padStart(2, "0")}:${String(remainder).padStart(2, "0")}`;
}

function renderTimer() {
  timerDisplayText.textContent = formatTimer(remainingTimerSeconds);
}

function updateTimerPrimaryButton() {
  if (timerInterval) {
    timerStart.textContent = "Pause";
    return;
  }

  if (remainingTimerSeconds < totalTimerSeconds) {
    timerStart.textContent = remainingTimerSeconds <= 0 ? "Restart" : "Resume";
    return;
  }

  timerStart.textContent = "Start";
}

function closeTimerEditor() {
  timerEditor.classList.add("hidden");
  timerDisplay.setAttribute("aria-expanded", "false");
}

function openTimerEditor() {
  if (timerInterval) {
    timerStatus.textContent = "Pause the timer before changing the session length.";
    return;
  }
  timerEditor.classList.remove("hidden");
  timerDisplay.setAttribute("aria-expanded", "true");
  timerMinutesInput.focus();
  timerMinutesInput.select();
}

function stopTimer(clearStatus = false) {
  if (timerInterval) {
    window.clearInterval(timerInterval);
    timerInterval = null;
  }
  if (clearStatus) {
    timerStatus.textContent = "Ready to start.";
  }
  updateTimerPrimaryButton();
}

function syncTimerInput() {
  timerMinutesInput.value = String(Math.max(1, Math.round(totalTimerSeconds / 60)));
}

function setTimerMinutes(minutes) {
  const safeMinutes = Math.max(1, Math.round(minutes));
  totalTimerSeconds = safeMinutes * 60;
  remainingTimerSeconds = totalTimerSeconds;
  syncTimerInput();
  renderTimer();
  timerStatus.textContent = "Ready to start.";
  updateTimerPrimaryButton();
}

function resetTimerFromInput() {
  stopTimer(true);
  setTimerMinutes(Number(timerMinutesInput.value || 25));
}

function startTimer() {
  if (timerInterval) {
    return;
  }
  if (remainingTimerSeconds <= 0) {
    remainingTimerSeconds = totalTimerSeconds;
    renderTimer();
  }
  timerStatus.textContent = "Timer running. Stay with one task until it ends.";
  timerInterval = window.setInterval(() => {
    remainingTimerSeconds -= 1;
    renderTimer();
    if (remainingTimerSeconds <= 0) {
      stopTimer();
      remainingTimerSeconds = 0;
      renderTimer();
      timerStatus.textContent = "Time is up. Take a quick break or save a readiness check.";
      updateTimerPrimaryButton();
    }
  }, 1000);
  updateTimerPrimaryButton();
}

function nudgeTimer(minutesDelta) {
  if (timerInterval) {
    timerStatus.textContent = "Pause the timer before changing the session length.";
    return;
  }
  setTimerMinutes(Math.round(totalTimerSeconds / 60) + minutesDelta);
  closeTimerEditor();
}

pageButtons.forEach((button) => {
  button.addEventListener("click", () => {
    showPage(button.dataset.page);
  });
});

academicList.addEventListener("click", async (event) => {
  const target = event.target.closest(".focus-switch");
  if (!target) {
    return;
  }
  const data = await postJson("/study/focus", { item_id: target.dataset.itemId });
  if (data.error) {
    addMessage("system", data.error);
    return;
  }
  renderDashboard(data.dashboard);
  addMessage("system", "Current focus updated.");
});

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = chatInput.value.trim();
  if (!text) {
    return;
  }
  chatInput.value = "";
  await handleCoachQuery(text);
});

refreshButton.addEventListener("click", async () => {
  await loadDashboard();
  addMessage("system", "Everything is up to date.");
});

tonightButton.addEventListener("click", async () => {
  showPage("study");
  const data = await postJson("/study/plan", { minutes: Number(planMinutes.value || 90) });
  renderStack(planOutput, data.plan, planCard);
  renderStack(overviewPlan, data.plan.slice(0, 2), planCard);
  addMessage("system", `${data.headline} is ready.`);
});

panicButton.addEventListener("click", async () => {
  showPage("cram");
  const data = await postJson("/study/panic-mode", { horizon: panicHorizon.value });
  renderPanic(data);
  addMessage("system", `${data.headline} is ready.`);
});

planForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = await postJson("/study/plan", { minutes: Number(planMinutes.value || 90) });
  renderStack(planOutput, data.plan, planCard);
  renderStack(overviewPlan, data.plan.slice(0, 2), planCard);
});

panicForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = await postJson("/study/panic-mode", { horizon: panicHorizon.value });
  renderPanic(data);
});

checkinForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = await postJson("/study/check-in", {
    topic_id: checkinTopic.value,
    confidence: Number(checkinConfidence.value),
    quiz_score: Number(checkinQuiz.value),
    minutes_studied: Number(checkinMinutes.value),
  });
  renderDashboard(data.dashboard);
  renderStack(
    checkinResult,
    [data],
    (item) => simpleCard("Check-in saved", item.topic.title || item.topic.name, item.insight)
  );
  addMessage("system", data.insight);
});

materialsForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = materialsTitle.value.trim();
  const text = materialsText.value.trim();
  const [file] = materialsFile.files || [];
  const isPdf = file && (file.type === "application/pdf" || /\.pdf$/i.test(file.name));

  if (!title && !file) {
    addMessage("system", "Add a material title first.");
    return;
  }

  let data;
  if (isPdf) {
    const formData = new FormData();
    formData.append("title", title);
    formData.append("file", file);
    data = await postForm("/study/materials/upload", formData);
  } else {
    if (!title || !text) {
      addMessage("system", "Add a material title and some notes first, or upload a PDF.");
      return;
    }
    data = await postJson("/study/materials", { title, text });
  }

  if (data.error) {
    addMessage("system", data.error);
    return;
  }

  renderDashboard(data.dashboard);
  materialsTitle.value = "";
  materialsText.value = "";
  materialsFile.value = "";
  updateMaterialFileName("No file chosen");
  updateMaterialFileStatus("Upload a text file to fill the notes box, or upload a PDF to extract its text when you save.");
  showPage("materials");
  const suffix = data.import_note ? ` ${data.import_note}` : "";
  addMessage(
    "system",
    `Created ${data.created_topics.length} topic${data.created_topics.length === 1 ? "" : "s"} from your notes.${suffix}`
  );
});

materialsOutput.addEventListener("click", async (event) => {
  const button = event.target.closest(".material-delete-button");
  if (!button) {
    return;
  }

  const materialId = button.dataset.materialId;
  if (!materialId) {
    return;
  }

  if (!window.confirm("Delete this material and remove its linked study topics?")) {
    return;
  }

  button.disabled = true;
  const data = await postJson("/study/materials/delete", { material_id: materialId });
  if (data.error) {
    button.disabled = false;
    addMessage("system", data.error);
    return;
  }

  renderDashboard(data.dashboard);
  addMessage(
    "system",
    `${data.deleted_material_title} deleted. Removed ${data.removed_topics} linked topic${data.removed_topics === 1 ? "" : "s"}.`
  );
});

academicForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    title: itemTitle.value.trim(),
    subject: itemSubject.value.trim(),
    kind: itemKind.value,
    due_date: itemDate.value,
  };
  if (!payload.title || !payload.subject || !payload.due_date) {
    addMessage("system", "Add a title, subject, and due date first.");
    return;
  }
  const data = await postJson("/study/academic-items", payload);
  if (data.error) {
    addMessage("system", data.error);
    return;
  }
  renderDashboard(data.dashboard);
  itemTitle.value = "";
  itemSubject.value = "";
  itemDate.value = "";
  addMessage("system", `${payload.kind[0].toUpperCase()}${payload.kind.slice(1)} added.`);
});

materialsFile.addEventListener("change", async (event) => {
  const [file] = event.target.files || [];
  if (!file) {
    updateMaterialFileName("No file chosen");
    updateMaterialFileStatus("Upload a text file to fill the notes box, or upload a PDF to extract its text when you save.");
    return;
  }

  updateMaterialFileName(file.name, false);

  const supportedTextFile =
    file.type.startsWith("text/") ||
    file.type === "application/json" ||
    TEXT_FILE_PATTERN.test(file.name);
  const isPdf = file.type === "application/pdf" || /\.pdf$/i.test(file.name);

  if (!supportedTextFile && !isPdf) {
    updateMaterialFileStatus("That file type is not supported yet. Use a text file or a PDF.", true);
    return;
  }

  if (isPdf) {
    materialsText.value = "";
    if (!materialsTitle.value.trim()) {
      materialsTitle.value = file.name.replace(/\.[^.]+$/, "");
    }
    updateMaterialFileStatus(`PDF selected: ${file.name}. Its text will be extracted when you save.`);
    showPage("materials");
    return;
  }

  try {
    const text = await file.text();
    materialsText.value = text;
    if (!materialsTitle.value.trim()) {
      materialsTitle.value = file.name.replace(/\.[^.]+$/, "");
    }
    updateMaterialFileStatus(`Loaded ${file.name}. You can edit the text before saving.`);
    showPage("materials");
  } catch (error) {
    updateMaterialFileStatus("Could not read that file. Try a different text-based file.", true);
  }
});

timerDisplay.addEventListener("click", () => {
  openTimerEditor();
});

timerApply.addEventListener("click", () => {
  resetTimerFromInput();
  closeTimerEditor();
});

timerMinutesInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    resetTimerFromInput();
    closeTimerEditor();
  }
  if (event.key === "Escape") {
    event.preventDefault();
    syncTimerInput();
    closeTimerEditor();
  }
});

timerMinus.addEventListener("click", () => {
  nudgeTimer(-5);
});

timerPlus.addEventListener("click", () => {
  nudgeTimer(5);
});

timerStart.addEventListener("click", () => {
  if (timerInterval) {
    stopTimer();
    timerStatus.textContent = "Timer paused.";
    return;
  }
  startTimer();
});

timerReset.addEventListener("click", () => {
  resetTimerFromInput();
  closeTimerEditor();
});

async function boot() {
  syncTimerInput();
  renderTimer();
  updateTimerPrimaryButton();
  addMessage(
    "assistant",
    "I can help you choose what to study, build a quick plan, make a cram plan, and turn notes into practice prompts."
  );
  await loadDashboard();
}

boot();
