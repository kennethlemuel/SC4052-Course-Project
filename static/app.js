const authScreen = document.querySelector("#auth-screen");
const welcomeScreen = document.querySelector("#welcome-screen");
const welcomePrefix = document.querySelector("#welcome-prefix");
const welcomeText = document.querySelector("#welcome-text");
const appShell = document.querySelector("#app-shell");
const loginForm = document.querySelector("#login-form");
const loginIdentifier = document.querySelector("#login-identifier");
const loginPassword = document.querySelector("#login-password");
const loginError = document.querySelector("#login-error");
const registerForm = document.querySelector("#register-form");
const registerEmail = document.querySelector("#register-email");
const registerUsername = document.querySelector("#register-username");
const registerPassword = document.querySelector("#register-password");
const registerPasswordConfirm = document.querySelector("#register-password-confirm");
const registerError = document.querySelector("#register-error");
const resetPasswordForm = document.querySelector("#reset-password-form");
const resetPassword = document.querySelector("#reset-password");
const resetPasswordConfirm = document.querySelector("#reset-password-confirm");
const resetPasswordError = document.querySelector("#reset-password-error");
const resetBackLogin = document.querySelector("#reset-back-login");
const showRegister = document.querySelector("#show-register");
const showLogin = document.querySelector("#show-login");
const forgotPasswordLink = document.querySelector("#forgot-password-link");
const forgotPasswordStatus = document.querySelector("#forgot-password-status");
const passwordToggles = document.querySelectorAll("[data-password-toggle]");
const logoutToggle = document.querySelector("#logout-toggle");
const logoutButton = document.querySelector("#logout-button");
const logoutCluster = document.querySelector(".logout-cluster");

const chatLog = document.querySelector("#chat-log");
const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");
const chatSubmit = chatForm.querySelector('button[type="submit"]');
const coachTabs = document.querySelector("#coach-tabs");
const coachTabNew = document.querySelector("#coach-tab-new");
const coachMemoryCount = document.querySelector("#coach-memory-count");
const studyMain = document.querySelector(".study-main");
const studySide = document.querySelector(".study-side");
const materialsUpload = document.querySelector(".materials-upload");
const materialsSide = document.querySelector(".materials-side");

const refreshButton = document.querySelector("#refresh-btn");
const targetScoreButton = document.querySelector("#target-score-btn");
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
const panicOutput = document.querySelector("#panic-output");
const recallDeck = document.querySelector("#recall-deck");
const checkinTopic = document.querySelector("#checkin-topic");
const checkinResult = document.querySelector("#checkin-result");
const materialsOutput = document.querySelector("#materials-output");
const overviewPlanTitle = document.querySelector("#overview-plan-title");
const overviewPlanPace = document.querySelector("#overview-plan-pace");
const overviewWeaknessTitle = document.querySelector("#overview-weakness-title");
const studyPlanTitle = document.querySelector("#study-plan-title");
const readinessTitle = document.querySelector("#readiness-title");
const cramPlanTitle = document.querySelector("#cram-plan-title");
const planMinutesLabel = document.querySelector("#plan-minutes-label");
const checkinTopicLabel = document.querySelector("#checkin-topic-label");
const panicHorizonLabel = document.querySelector("#panic-horizon-label");

const planForm = document.querySelector("#plan-form");
const planMinutes = document.querySelector("#plan-minutes");
const planMaterialOptions = document.querySelector("#plan-material-options");
const panicForm = document.querySelector("#panic-form");
const panicHorizon = document.querySelector("#panic-horizon");
const checkinForm = document.querySelector("#checkin-form");
const checkinConfidence = document.querySelector("#checkin-confidence");
const checkinQuiz = document.querySelector("#checkin-quiz");
const checkinMinutes = document.querySelector("#checkin-minutes");
const materialsForm = document.querySelector("#materials-form");
const materialsTitle = document.querySelector("#materials-title");
const materialsItem = document.querySelector("#materials-item");
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
const musicTabs = document.querySelectorAll("[data-music-tab]");
const musicPanels = document.querySelectorAll("[data-music-panel]");
const focusSound = document.querySelector("#focus-sound");
const musicVolume = document.querySelector("#music-volume");
const musicVolumeValue = document.querySelector("#music-volume-value");
const musicPlay = document.querySelector("#music-play");
const musicStop = document.querySelector("#music-stop");
const musicStatus = document.querySelector("#music-status");
const spotifyAccount = document.querySelector("#spotify-account");
const spotifyConnect = document.querySelector("#spotify-connect");
const spotifyPause = document.querySelector("#spotify-pause");
const spotifyPrev = document.querySelector("#spotify-prev");
const spotifyNext = document.querySelector("#spotify-next");
const spotifyShuffle = document.querySelector("#spotify-shuffle");
const spotifyDisconnect = document.querySelector("#spotify-disconnect");
const spotifyStatus = document.querySelector("#spotify-status");
const spotifyArt = document.querySelector("#spotify-art");
const spotifyProgress = document.querySelector("#spotify-progress");
const spotifyProgressTime = document.querySelector("#spotify-progress-time");
const spotifySearch = document.querySelector("#spotify-search");
const spotifySearchButton = document.querySelector("#spotify-search-button");
const spotifyResults = document.querySelector("#spotify-results");

const modalBackdrop = document.querySelector("#modal-backdrop");
const targetScoreModal = document.querySelector("#target-score-modal");
const targetScoreForm = document.querySelector("#target-score-form");
const targetScoreInput = document.querySelector("#target-score-input");
const targetScoreFocus = document.querySelector("#target-score-focus");
const targetScoreError = document.querySelector("#target-score-error");
const targetScoreClose = document.querySelector("#target-score-close");
const targetScoreCancel = document.querySelector("#target-score-cancel");
const academicEditModal = document.querySelector("#academic-edit-modal");
const academicEditForm = document.querySelector("#academic-edit-form");
const academicEditTitle = document.querySelector("#academic-edit-title");
const academicEditSubject = document.querySelector("#academic-edit-subject");
const academicEditKind = document.querySelector("#academic-edit-kind");
const academicEditDate = document.querySelector("#academic-edit-date");
const academicEditError = document.querySelector("#academic-edit-error");
const academicEditClose = document.querySelector("#academic-edit-close");
const academicEditCancel = document.querySelector("#academic-edit-cancel");
const materialEditModal = document.querySelector("#material-edit-modal");
const materialEditForm = document.querySelector("#material-edit-form");
const materialEditTitle = document.querySelector("#material-edit-title");
const materialEditError = document.querySelector("#material-edit-error");
const materialEditClose = document.querySelector("#material-edit-close");
const materialEditCancel = document.querySelector("#material-edit-cancel");

const pageButtons = document.querySelectorAll("[data-page]");
const pages = document.querySelectorAll(".page");

const TEXT_FILE_PATTERN = /\.(txt|md|csv|json)$/i;
const ACTIVE_PAGE_STORAGE_KEY = "studyBuddy.activePage";
const MUSIC_SETTINGS_STORAGE_KEY = "studyBuddy.musicSettings";
const AUTH_TOKEN_STORAGE_KEY = "studyBuddy.sessionToken";

let currentUser = null;
let appBooted = false;
let pendingResetToken = "";
let timerInterval = null;
let totalTimerSeconds = Number(timerMinutesInput.value) * 60;
let remainingTimerSeconds = totalTimerSeconds;
let focusAudioContext = null;
let focusAudioSource = null;
let focusAudioFilter = null;
let focusAudioGain = null;
let focusAudioPlaying = false;
let spotifyStatusState = null;
let spotifyPlayer = null;
let spotifyDeviceId = "";
let spotifySdkPromise = null;
let spotifyLibraryLoaded = false;
let spotifyPlaybackState = null;
let spotifyProgressTimer = null;
let spotifyShuffleEnabled = false;
let currentDashboard = null;
let editingAcademicItemId = "";
let editingMaterialId = "";
let lastFocusedElement = null;
let activeCoachTabId = "";
let coachTabsState = [];
let renamingCoachTabId = "";

function iconSvg(name) {
  const icons = {
    edit: '<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M4 13.6 3.4 16.4 6.2 15.8 14.7 7.3 12.5 5.1 4 13.6Z"></path><path d="M13.4 4.2 14.5 3.1C15 2.6 15.8 2.6 16.3 3.1L16.7 3.5C17.2 4 17.2 4.8 16.7 5.3L15.6 6.4 13.4 4.2Z"></path></svg>',
    close: '<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M5 5 15 15"></path><path d="M15 5 5 15"></path></svg>',
    check: '<svg viewBox="0 0 20 20" aria-hidden="true" focusable="false"><path d="M4 10.4 8.2 14.4 16 5.8"></path></svg>',
  };
  return icons[name] || "";
}

function wait(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

function authToken() {
  return window.localStorage?.getItem(AUTH_TOKEN_STORAGE_KEY) || "";
}

function setAuthToken(token) {
  if (token) {
    window.localStorage?.setItem(AUTH_TOKEN_STORAGE_KEY, token);
    return;
  }
  window.localStorage?.removeItem(AUTH_TOKEN_STORAGE_KEY);
}

function authHeaders() {
  const token = authToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function showAuthError(target, message = "") {
  if (!target) {
    return;
  }
  target.textContent = message;
  target.classList.toggle("hidden", !message);
}

function setPasswordVisibility(button, isVisible) {
  const input = document.getElementById(button.dataset.passwordToggle || "");
  if (!input) {
    return;
  }
  input.type = isVisible ? "text" : "password";
  button.classList.toggle("is-visible", isVisible);
  button.setAttribute("aria-pressed", String(isVisible));
  button.setAttribute("aria-label", isVisible ? "Hide password" : "Show password");
}

function hidePasswordFields() {
  passwordToggles.forEach((button) => {
    setPasswordVisibility(button, false);
  });
}

function showAuthMode(mode) {
  const isRegister = mode === "register";
  const isReset = mode === "reset";
  loginForm?.classList.toggle("hidden", isRegister || isReset);
  registerForm?.classList.toggle("hidden", !isRegister);
  resetPasswordForm?.classList.toggle("hidden", !isReset);
  if (forgotPasswordLink) {
    forgotPasswordLink.classList.toggle("hidden", isReset);
    forgotPasswordLink.textContent = isRegister ? "Back to login" : "Forgot password?";
  }
  showAuthError(loginError);
  showAuthError(registerError);
  showAuthError(resetPasswordError);
  hidePasswordFields();
  if (forgotPasswordStatus) {
    forgotPasswordStatus.textContent = "";
  }
  window.requestAnimationFrame(() => {
    if (isReset) {
      resetPassword?.focus();
    } else if (isRegister) {
      registerEmail?.focus();
    } else {
      loginIdentifier?.focus();
    }
  });
}

async function typeWelcomeText(username) {
  if (!welcomeText) {
    await wait(1200);
    return;
  }
  welcomeText.textContent = "";
  const text = username || "student";
  for (const char of text) {
    welcomeText.textContent += char;
    await wait(58);
  }
  await wait(1100);
}

async function showTypingTransition(prefix, user) {
  if (!welcomeScreen || !welcomePrefix) {
    return;
  }
  welcomePrefix.textContent = prefix;
  welcomeScreen.classList.remove("hidden");
  await typeWelcomeText(user?.username || "student");
  welcomeScreen.classList.add("hidden");
}

async function showWelcomeTransition(user, mode) {
  await showTypingTransition(mode === "register" ? "Welcome," : "Welcome back,", user);
}

async function showLogoutTransition(user) {
  authScreen?.classList.add("hidden");
  appShell?.classList.add("hidden");
  await showTypingTransition("See you,", user);
}

async function showAuthenticatedApp(user, mode = "") {
  currentUser = user || null;
  authScreen?.classList.add("hidden");
  appShell?.classList.add("hidden");
  if (mode) {
    await showWelcomeTransition(currentUser, mode);
  }
  await bootAppData();
  appShell?.classList.remove("hidden");
  window.requestAnimationFrame(() => {
    syncStudyRoomLayout();
    syncMaterialsLayout();
  });
}

function showLoggedOutState() {
  currentUser = null;
  appShell?.classList.add("hidden");
  welcomeScreen?.classList.add("hidden");
  authScreen?.classList.remove("hidden");
  logoutCluster?.classList.remove("open");
  logoutToggle?.setAttribute("aria-expanded", "false");
  showAuthMode("login");
}

async function checkAuthSession() {
  const params = new URLSearchParams(window.location.search);
  const resetToken = params.get("reset");
  if (resetToken) {
    pendingResetToken = resetToken;
    params.delete("reset");
    const nextQuery = params.toString();
    const nextUrl = `${window.location.pathname}${nextQuery ? `?${nextQuery}` : ""}${window.location.hash}`;
    window.history.replaceState({}, "", nextUrl);
    setAuthToken("");
    authScreen?.classList.remove("hidden");
    appShell?.classList.add("hidden");
    showAuthMode("reset");
    return;
  }
  try {
    const response = await fetch("/auth/session", { headers: authHeaders() });
    const data = await response.json();
    if (response.ok && data.authenticated) {
      await showAuthenticatedApp(data.user);
      return;
    }
  } catch (error) {
    // Fall through to login if the local session cannot be checked.
  }
  setAuthToken("");
  showLoggedOutState();
}

function setModalError(target, message = "") {
  if (!target) {
    return;
  }
  target.textContent = message;
  target.classList.toggle("hidden", !message);
}

function showEditModal(modal, initialFocus) {
  lastFocusedElement = document.activeElement;
  modalBackdrop.classList.remove("hidden");
  modal.classList.remove("hidden");
  window.requestAnimationFrame(() => {
    initialFocus?.focus();
    initialFocus?.select?.();
  });
}

function closeEditModals() {
  modalBackdrop.classList.add("hidden");
  targetScoreModal.classList.add("hidden");
  academicEditModal.classList.add("hidden");
  materialEditModal.classList.add("hidden");
  editingAcademicItemId = "";
  editingMaterialId = "";
  setModalError(targetScoreError);
  setModalError(academicEditError);
  setModalError(materialEditError);
  lastFocusedElement?.focus?.();
  lastFocusedElement = null;
}

function openTargetScoreModal() {
  const metrics = currentDashboard?.metrics || {};
  targetScoreInput.value = String(metrics.target_readiness ?? 0);
  targetScoreFocus.textContent = `Current focus: ${metrics.focus_title || focusLabel(currentDashboard?.focus_item)}`;
  setModalError(targetScoreError);
  showEditModal(targetScoreModal, targetScoreInput);
}

function openAcademicEditModal(button) {
  editingAcademicItemId = button.dataset.itemId || "";
  academicEditTitle.value = button.dataset.itemTitle || "";
  academicEditSubject.value = button.dataset.itemSubject || "";
  academicEditKind.value = button.dataset.itemKind || "exam";
  academicEditDate.value = button.dataset.itemDueDate || "";
  setModalError(academicEditError);
  showEditModal(academicEditModal, academicEditTitle);
}

function openMaterialEditModal(button) {
  editingMaterialId = button.dataset.materialId || "";
  materialEditTitle.value = button.dataset.materialTitle || "";
  setModalError(materialEditError);
  showEditModal(materialEditModal, materialEditTitle);
}

function scrollChatToBottom(behavior = "smooth") {
  chatLog.scrollTo({
    top: chatLog.scrollHeight,
    behavior,
  });
}

function syncChatInputHeight() {
  chatInput.style.height = "0px";
  chatInput.style.height = `${Math.min(chatInput.scrollHeight, 150)}px`;
}

function setChatBusy(isBusy) {
  chatInput.disabled = isBusy;
  chatSubmit.disabled = isBusy;
}

function syncStudyRoomLayout() {
  if (!studyMain || !studySide) {
    return;
  }

  if (window.innerWidth <= 1180) {
    studyMain.style.height = "";
    studyMain.style.maxHeight = "";
    return;
  }

  if (studySide.offsetHeight <= 0) {
    return;
  }

  const targetHeight = `${studySide.offsetHeight}px`;
  studyMain.style.height = targetHeight;
  studyMain.style.maxHeight = targetHeight;
}

function syncMaterialsLayout() {
  if (!materialsUpload || !materialsSide) {
    return;
  }

  if (window.innerWidth <= 1180) {
    materialsSide.style.height = "";
    materialsSide.style.maxHeight = "";
    return;
  }

  if (materialsUpload.offsetHeight <= 0) {
    return;
  }

  const targetHeight = `${materialsUpload.offsetHeight}px`;
  materialsSide.style.height = targetHeight;
  materialsSide.style.maxHeight = targetHeight;
}

function showPage(pageName) {
  const pageExists = Array.from(pages).some((page) => page.id === `page-${pageName}`);
  const resolvedPage = pageExists ? pageName : "overview";
  pageButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.page === resolvedPage);
  });
  pages.forEach((page) => {
    const shouldShow = page.id === `page-${resolvedPage}`;
    page.classList.toggle("active", shouldShow);
    page.classList.toggle("hidden", !shouldShow);
  });
  targetScoreButton?.classList.toggle("hidden", resolvedPage !== "overview");
  window.localStorage?.setItem(ACTIVE_PAGE_STORAGE_KEY, resolvedPage);
  if (resolvedPage === "study") {
    window.requestAnimationFrame(syncStudyRoomLayout);
  }
  if (resolvedPage === "materials") {
    window.requestAnimationFrame(syncMaterialsLayout);
  }
}

function restoreActivePage() {
  const savedPage = window.localStorage?.getItem(ACTIVE_PAGE_STORAGE_KEY) || "overview";
  showPage(savedPage);
}

function createMessageNode(role) {
  const node = document.createElement("div");
  node.className = `message ${role} entering`;
  chatLog.appendChild(node);
  scrollChatToBottom();
  window.requestAnimationFrame(() => node.classList.remove("entering"));
  return node;
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function safeLinkUrl(url) {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:" ? parsed.href : "";
  } catch (error) {
    return "";
  }
}

function renderRichText(text) {
  const pattern = /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g;
  let html = "";
  let lastIndex = 0;
  let match = pattern.exec(text);
  while (match) {
    html += escapeHtml(text.slice(lastIndex, match.index));
    const href = safeLinkUrl(match[2]);
    if (href) {
      html += `<a href="${escapeHtml(href)}" target="_blank" rel="noreferrer">${escapeHtml(match[1])}</a>`;
    } else {
      html += escapeHtml(match[0]);
    }
    lastIndex = pattern.lastIndex;
    match = pattern.exec(text);
  }
  html += escapeHtml(text.slice(lastIndex));
  return html.replace(/\n/g, "<br>");
}

function renderMessageNode(role, text) {
  const node = document.createElement("div");
  node.className = `message ${role}`;
  if (role === "assistant" || role === "system") {
    node.innerHTML = renderRichText(text);
  } else {
    node.textContent = text;
  }
  return node;
}

function addMessage(role, text) {
  const node = createMessageNode(role);
  if (role === "assistant" || role === "system") {
    node.innerHTML = renderRichText(text);
  } else {
    node.textContent = text;
  }
  return node;
}

function renderChatMessages(messages = []) {
  chatLog.innerHTML = "";
  if (!messages.length) {
    const node = document.createElement("div");
    node.className = "coach-empty";
    node.textContent = "Start a clean chat here. Quiz memory is still shared across every tab.";
    chatLog.appendChild(node);
    return;
  }
  messages.forEach((message) => {
    chatLog.appendChild(renderMessageNode(message.role, message.text));
  });
  scrollChatToBottom("auto");
}

function activeCoachTab() {
  return coachTabsState.find((tab) => tab.id === activeCoachTabId) || coachTabsState[0] || null;
}

function renderCoachTabs(coach) {
  if (!coach || !coachTabs || !coachMemoryCount) {
    return;
  }
  coachTabsState = coach.tabs || [];
  activeCoachTabId = coach.active_tab_id || coachTabsState[0]?.id || "";
  coachMemoryCount.textContent = `${coach.memory_count || 0} remembered`;
  coachTabs.innerHTML = "";

  coachTabsState.forEach((tab) => {
    const item = document.createElement("div");
    item.className = `coach-tab${tab.id === activeCoachTabId ? " active" : ""}`;
    item.dataset.tabId = tab.id;

    if (tab.id === renamingCoachTabId) {
      item.innerHTML = `
        <form class="coach-tab-rename-form" data-tab-id="${escapeHtml(tab.id)}">
          <input type="text" value="${escapeHtml(tab.title)}" maxlength="48" aria-label="Chat title" />
          <button type="submit" class="coach-icon-button" aria-label="Save title" title="Save title">${iconSvg("check")}</button>
        </form>
      `;
    } else {
      item.innerHTML = `
        <button type="button" class="coach-tab-select" data-tab-id="${escapeHtml(tab.id)}">
          <span>${escapeHtml(tab.title)}</span>
          ${tab.has_open_quiz ? '<span class="coach-tab-dot" aria-label="Open quiz"></span>' : ""}
        </button>
        <button type="button" class="coach-tab-action coach-icon-button coach-tab-rename" data-tab-id="${escapeHtml(tab.id)}" aria-label="Rename chat" title="Rename chat">${iconSvg("edit")}</button>
        <button type="button" class="coach-tab-action coach-icon-button coach-tab-close" data-tab-id="${escapeHtml(tab.id)}" aria-label="Close chat" title="Close chat">${iconSvg("close")}</button>
      `;
    }
    coachTabs.appendChild(item);
  });

  const current = activeCoachTab();
  renderChatMessages(current?.messages || []);
  window.requestAnimationFrame(syncStudyRoomLayout);
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
  await wait(140);
  node.classList.remove("pending");
  node.innerHTML = renderRichText(text);
  scrollChatToBottom();
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify(payload),
  });
  const raw = await response.text();
  if (!raw.trim()) {
    return { ok: response.ok, status: response.status };
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    return {
      error: raw.trim() || error.message,
      ok: response.ok,
      status: response.status,
    };
  }
}

async function postForm(url, formData) {
  const response = await fetch(url, {
    method: "POST",
    headers: authHeaders(),
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

function groupStatusLabel(riskScore) {
  if (riskScore >= 75) {
    return "Critical";
  }
  if (riskScore >= 58) {
    return "Shaky";
  }
  return "Stable";
}

function averageValue(items, key) {
  if (!items.length) {
    return 0;
  }
  return Math.round(items.reduce((sum, item) => sum + Number(item[key] || 0), 0) / items.length);
}

function groupTopicsByModule(items) {
  const groupsByName = new Map();
  items.forEach((item) => {
    const title = item.module || "Unsorted topics";
    if (!groupsByName.has(title)) {
      groupsByName.set(title, []);
    }
    groupsByName.get(title).push(item);
  });

  return Array.from(groupsByName.entries())
    .map(([title, topics]) => {
      const confidence = averageValue(topics, "confidence");
      const mastery = averageValue(topics, "mastery");
      const risk = averageValue(topics, "risk_score");
      return {
        title,
        topics,
        confidence,
        mastery,
        risk,
        status: groupStatusLabel(risk),
      };
    })
    .sort((first, second) => {
      const confidenceDelta = first.confidence - second.confidence;
      if (confidenceDelta !== 0) {
        return confidenceDelta;
      }
      const riskDelta = second.risk - first.risk;
      if (riskDelta !== 0) {
        return riskDelta;
      }
      return first.title.localeCompare(second.title, undefined, { numeric: true, sensitivity: "base" });
    });
}

function topicGroupCard(group, isOpen) {
  const node = document.createElement("details");
  node.className = "topic-group";
  node.open = isOpen;

  const topicNoun = group.topics.length === 1 ? "topic" : "topics";
  const topics = group.topics
    .map((topic) => {
      const topicNode = weaknessCard(topic);
      topicNode.classList.add("topic-group-item");
      return topicNode.outerHTML;
    })
    .join("");

  node.innerHTML = `
    <summary class="topic-group-summary">
      <div class="topic-group-main">
        <span class="micro-label">Lesson</span>
        <strong>${group.title}</strong>
        <span class="muted">${group.topics.length} ${topicNoun}</span>
      </div>
      <div class="topic-group-readiness">
        <span class="pill ${group.status.toLowerCase()}">${group.status}</span>
        <strong>${group.confidence}/100</strong>
        <span>Total confidence</span>
      </div>
    </summary>
    <div class="topic-group-meter" aria-hidden="true"><span style="width:${group.confidence}%"></span></div>
    <div class="topic-group-meta">
      <span>Average understanding ${group.mastery}</span>
      <span>Average risk ${group.risk}</span>
    </div>
    <div class="topic-group-list">${topics}</div>
  `;
  return node;
}

function renderWeaknessMap(target, items) {
  target.innerHTML = "";
  if (!items || items.length === 0) {
    const node = document.createElement("div");
    node.className = "card muted";
    node.textContent = "No topics yet.";
    target.appendChild(node);
    return;
  }

  groupTopicsByModule(items).forEach((group, index) => {
    const node = topicGroupCard(group, false);
    node.classList.add("stagger-in");
    node.style.setProperty("--stagger-index", index);
    target.appendChild(node);
  });
}

function planCard(item) {
  const node = document.createElement("div");
  node.className = "card";
  node.innerHTML = `
    <div class="card-topline">
      <strong>${escapeHtml(item.title)}</strong>
      <span class="pill neutral">${escapeHtml(item.minutes)} min</span>
    </div>
    <div class="muted">${escapeHtml(item.module)}</div>
    <div>${escapeHtml(item.mode)}</div>
    <div class="muted">${escapeHtml(item.reason)}</div>
  `;
  return node;
}

function selectedPlanMaterialIds() {
  if (!planMaterialOptions) {
    return [];
  }
  return Array.from(planMaterialOptions.querySelectorAll('input[name="plan-material"]:checked')).map((input) => input.value);
}

function planMinutesValue() {
  const fallback = Number(currentDashboard?.plan_meta?.minutes || 90);
  const value = Number(planMinutes?.value || fallback);
  if (!Number.isFinite(value)) {
    return Math.max(15, Math.min(720, fallback || 90));
  }
  return Math.max(15, Math.min(720, Math.round(value)));
}

function planPaceLabel(minutes) {
  if (minutes <= 90) {
    return "Fast";
  }
  if (minutes <= 180) {
    return "Balanced";
  }
  return "Chill";
}

function syncOverviewPlanPace(pace) {
  if (overviewPlanPace) {
    overviewPlanPace.textContent = pace || planPaceLabel(planMinutesValue());
  }
}

function applyPlanPayload(payload, minutes = planMinutesValue()) {
  renderStack(overviewPlan, payload.plan, planCard, "No plan yet.");
  syncOverviewPlanPace(payload.pace);
  if (currentDashboard) {
    currentDashboard.plan = payload.plan;
    currentDashboard.plan_meta = {
      ...(currentDashboard.plan_meta || {}),
      minutes,
      pace: payload.pace || planPaceLabel(minutes),
      selected_material_ids: payload.selected_material_ids || selectedPlanMaterialIds(),
    };
    renderFocusContext(currentDashboard);
  }
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

function cramGoalCard(data) {
  const node = document.createElement("div");
  node.className = "card cram-goal-card";
  node.innerHTML = `
    <div class="cram-goal-label">Goal</div>
    <strong>${escapeHtml(data.headline)}</strong>
    <div>${escapeHtml(data.triage_note)}</div>
    ${
      data.skip.length
        ? `<div class="cram-goal-skip">Ignore for now: ${escapeHtml(data.skip.join(", "))}</div>`
        : ""
    }
  `;
  return node;
}

function academicItemCard(item, activeItemId) {
  const node = document.createElement("div");
  node.className = "summary-item";
  const buttonLabel = item.id === activeItemId ? "Current focus" : "Set as focus";
  const disabled = item.id === activeItemId ? "disabled" : "";
  const itemKind = item.kind || item.label?.toLowerCase() || "exam";
  node.innerHTML = `
    <div class="card-topline">
      <strong>${escapeHtml(item.title)}</strong>
      <span class="pill neutral">${escapeHtml(item.label)}</span>
    </div>
    <div class="muted">${escapeHtml(item.subject)} • ${item.days_left} day${item.days_left === 1 ? "" : "s"} left</div>
    <div class="card-meta">
      <span>Due ${escapeHtml(item.due_date)}</span>
    </div>
    <div class="item-actions">
      <button class="secondary focus-switch" data-item-id="${item.id}" ${disabled}>${buttonLabel}</button>
      <button
        class="academic-edit-button"
        data-item-id="${item.id}"
        data-item-title="${escapeHtml(item.title)}"
        data-item-subject="${escapeHtml(item.subject)}"
        data-item-kind="${escapeHtml(itemKind)}"
        data-item-due-date="${escapeHtml(item.due_date)}"
        type="button"
      >
        Edit
      </button>
      <button class="academic-delete-button" data-item-id="${item.id}" type="button">Delete</button>
    </div>
  `;
  return node;
}

function focusLabel(focusItem) {
  return focusItem?.title || "your current focus";
}

function renderFocusContext(data) {
  const focus = focusLabel(data.focus_item);
  overviewPlanTitle.textContent = `Tonight for ${focus}`;
  overviewWeaknessTitle.textContent = `Topics for ${focus}`;
  studyPlanTitle.textContent = `Tonight for ${focus}`;
  if (readinessTitle) {
    readinessTitle.textContent = `Readiness check for ${focus}`;
  }
  cramPlanTitle.textContent = `Build a cram plan for ${focus}`;
  planMinutesLabel.textContent = `Time available for ${focus}`;
  if (checkinTopicLabel) {
    checkinTopicLabel.textContent = `Topic for ${focus}`;
  }
  panicHorizonLabel.textContent = `How much time is left for ${focus}?`;
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
  panicOutput.appendChild(cramGoalCard(data));
  data.must_cover.forEach((item, index) => {
    const node = simpleCard(`${item.order}. ${item.title}`, `${item.minutes} min`, item.reason);
    node.classList.add("stagger-in");
    node.style.setProperty("--stagger-index", index + 1);
    panicOutput.appendChild(node);
  });
}

function populateTopicOptions(topics) {
  if (!checkinTopic) {
    return;
  }
  const current = checkinTopic.value;
  checkinTopic.innerHTML = "";
  if (!topics || topics.length === 0) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "No topics for this focus yet";
    checkinTopic.appendChild(option);
    checkinTopic.disabled = true;
    return;
  }
  checkinTopic.disabled = false;
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
  if (!materialsOutput) {
    return;
  }
  materialsOutput.innerHTML = "";
  if (!items || items.length === 0) {
    const node = document.createElement("div");
    node.className = "card muted";
    node.textContent = "No materials added yet.";
    materialsOutput.appendChild(node);
    return;
  }

  const academicItems = currentDashboard?.academic_items || [];
  const academicIndex = new Map(academicItems.map((item) => [item.id, item]));
  const groups = [];
  const groupIndex = new Map();

  items.forEach((material) => {
    const academicItem = academicIndex.get(material.academic_item_id);
    const groupId = academicItem?.id || material.academic_item_id || "unassigned";
    if (!groupIndex.has(groupId)) {
      const title = academicItem ? `${academicItem.title} Materials` : "Unassigned Materials";
      const label = academicItem?.label || "Materials";
      const subject = academicItem?.subject || "";
      const group = { id: groupId, title, label, subject, materials: [] };
      groupIndex.set(groupId, group);
      groups.push(group);
    }
    groupIndex.get(groupId).materials.push(material);
  });

  groups.forEach((group) => {
    const details = document.createElement("details");
    details.className = "material-group";
    details.innerHTML = `
      <summary class="material-group-summary">
        <div class="material-group-heading">
          <span class="micro-label">${escapeHtml(group.label)}</span>
          <strong>${escapeHtml(group.title)}</strong>
          ${group.subject ? `<span class="muted">${escapeHtml(group.subject)}</span>` : ""}
        </div>
        <div class="material-group-meta">
          <span>${group.materials.length} document${group.materials.length === 1 ? "" : "s"}</span>
          <span class="material-group-toggle">Open</span>
        </div>
      </summary>
      <div class="material-group-list"></div>
    `;
    const list = details.querySelector(".material-group-list");
    group.materials.forEach((material) => {
      list.appendChild(materialCard(material));
    });
    details.addEventListener("toggle", () => {
      const toggle = details.querySelector(".material-group-toggle");
      if (toggle) {
        toggle.textContent = details.open ? "Close" : "Open";
      }
    });
    materialsOutput.appendChild(details);
  });
}

function renderPlanMaterialOptions(data) {
  if (!planMaterialOptions) {
    return;
  }
  const focusId = data.focus_item?.id || "";
  const materials = (data.materials || []).filter((material) => material.academic_item_id === focusId);
  const selectedIds = new Set(data.plan_meta?.selected_material_ids || []);
  planMaterialOptions.innerHTML = "";

  if (!materials.length) {
    const empty = document.createElement("div");
    empty.className = "helper-copy";
    empty.textContent = "No lecture materials for this focus yet.";
    planMaterialOptions.appendChild(empty);
    return;
  }

  materials.forEach((material) => {
    const label = document.createElement("label");
    label.className = "plan-material-option";
    label.innerHTML = `
      <input type="checkbox" name="plan-material" value="${escapeHtml(material.id)}" ${selectedIds.has(material.id) ? "checked" : ""} />
      <span>
        <strong>${escapeHtml(material.title)}</strong>
        <small>${material.topics?.length || 0} topic${material.topics?.length === 1 ? "" : "s"}</small>
      </span>
    `;
    planMaterialOptions.appendChild(label);
  });
}

function materialCard(item) {
  const node = document.createElement("div");
  node.className = "card material-card";
  const topics = item.topics?.length ? item.topics.join(", ") : "No derived topics yet.";
  node.innerHTML = `
    <div class="card-topline">
      <strong>${escapeHtml(item.title)}</strong>
      <div class="material-actions">
        <button
          class="material-edit-button"
          data-material-id="${escapeHtml(item.id)}"
          data-material-title="${escapeHtml(item.title)}"
          type="button"
          aria-label="Edit ${escapeHtml(item.title)} title"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">
            <path d="M4 16.8V20h3.2L18.7 8.5l-3.2-3.2L4 16.8Zm16.1-10.9c.4-.4.4-1 0-1.4l-.6-.6c-.4-.4-1-.4-1.4 0l-1.2 1.2 3.2 3.2 1.2-1.2Z"></path>
          </svg>
        </button>
        <button class="material-delete-button" data-material-id="${escapeHtml(item.id)}" type="button">Delete</button>
      </div>
    </div>
    <div>${escapeHtml(topics)}</div>
    <div class="muted">Imported ${new Date(item.created_at).toLocaleString()}</div>
  `;
  return node;
}

function renderAcademicItems(items, activeItemId) {
  renderStack(
    academicList,
    items,
    (item) => academicItemCard(item, activeItemId),
    "No exams or assignments yet."
  );
}

function populateMaterialsItemOptions(items, activeItemId) {
  const current = materialsItem.value || activeItemId || "";
  materialsItem.innerHTML = "";
  if (!items || items.length === 0) {
    const option = document.createElement("option");
    option.value = "";
    option.textContent = "Add an exam, assignment, or quiz first";
    materialsItem.appendChild(option);
    materialsItem.disabled = true;
    return;
  }

  materialsItem.disabled = false;
  items.forEach((item) => {
    const option = document.createElement("option");
    option.value = item.id;
    option.textContent = `${item.title} (${item.label})`;
    if (item.id === current) {
      option.selected = true;
    }
    materialsItem.appendChild(option);
  });
}

function renderDashboard(data) {
  currentDashboard = data;
  renderMetrics(data.metrics);
  renderFocusContext(data);
  renderStack(overviewPlan, data.plan, planCard, "No plan yet.");
  syncOverviewPlanPace(data.plan_meta?.pace);
  renderWeaknessMap(overviewWeakness, data.weakness_map);
  renderWeaknessMap(weaknessMap, data.weakness_map);
  renderPanic(data.panic_mode);
  if (recallDeck) {
    renderStack(recallDeck, data.recall_deck, recallCard, "No practice prompts yet.");
  }
  populateTopicOptions(data.topics);
  populateMaterialsItemOptions(data.academic_items, data.focus_item?.id);
  if (data.plan_meta?.minutes && planMinutes) {
    planMinutes.value = String(data.plan_meta.minutes);
  }
  renderPlanMaterialOptions(data);
  renderRecentMaterials(data.materials);
  renderAcademicItems(data.academic_items, data.focus_item?.id);
  renderCoachTabs(data.coach);
  window.requestAnimationFrame(syncStudyRoomLayout);
  window.requestAnimationFrame(syncMaterialsLayout);
}

async function loadDashboard() {
  const response = await fetch("/study/dashboard", { headers: authHeaders() });
  const data = await response.json();
  if (response.status === 401) {
    setAuthToken("");
    showLoggedOutState();
    return;
  }
  renderDashboard(data);
}

async function handleCoachQuery(text) {
  addMessage("user", text);
  const pendingNode = addPendingAssistantMessage();
  setChatBusy(true);
  try {
    const data = await postJson("/assistant/query", { text, tab_id: activeCoachTabId });
    await revealAssistantMessage(pendingNode, data.reply);
    if (data.coach) {
      renderCoachTabs(data.coach);
    }
    if (data.plan) {
      applyPlanPayload(data.plan, data.plan.minutes || planMinutesValue());
    }
    if (data.panic_mode) {
      renderPanic(data.panic_mode);
    }
    if (data.dashboard) {
      renderDashboard(data.dashboard);
    }
  } catch (error) {
    pendingNode.classList.remove("pending");
    pendingNode.textContent = "I couldn't reach the coach just now. Try again in a moment.";
    scrollChatToBottom();
  } finally {
    setChatBusy(false);
    chatInput.focus();
  }
}

async function updateCoachTabs(payload) {
  const data = await postJson("/assistant/tabs", payload);
  if (data.error) {
    addMessage("system", data.error);
    return;
  }
  if (currentDashboard) {
    currentDashboard.coach = data;
  }
  renderCoachTabs(data);
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

function getMusicVolume() {
  return Math.max(0, Math.min(100, Number(musicVolume?.value || 35))) / 100;
}

function getFocusSoundLabel() {
  const option = focusSound?.selectedOptions?.[0];
  return option ? option.textContent : "Focus sound";
}

function saveMusicSettings() {
  if (!focusSound || !musicVolume) {
    return;
  }
  localStorage.setItem(
    MUSIC_SETTINGS_STORAGE_KEY,
    JSON.stringify({
      sound: focusSound.value,
      volume: musicVolume.value,
    }),
  );
}

function restoreMusicSettings() {
  if (!focusSound || !musicVolume) {
    return;
  }
  try {
    const settings = JSON.parse(localStorage.getItem(MUSIC_SETTINGS_STORAGE_KEY) || "{}");
    if (settings.sound && Array.from(focusSound.options).some((option) => option.value === settings.sound)) {
      focusSound.value = settings.sound;
    }
    if (settings.volume !== undefined) {
      musicVolume.value = String(Math.max(0, Math.min(100, Number(settings.volume))));
    }
  } catch (error) {
    localStorage.removeItem(MUSIC_SETTINGS_STORAGE_KEY);
  }
}

function syncMusicVolume() {
  if (!musicVolume || !musicVolumeValue) {
    return;
  }
  const volumePercent = Math.round(getMusicVolume() * 100);
  musicVolumeValue.textContent = `${volumePercent}%`;
  if (focusAudioGain && focusAudioContext) {
    focusAudioGain.gain.setTargetAtTime(getMusicVolume() * 0.36, focusAudioContext.currentTime, 0.03);
  }
  if (spotifyPlayer) {
    spotifyPlayer.setVolume(getMusicVolume()).catch(() => {});
  }
  saveMusicSettings();
}

function buildNoiseBuffer(context, soundType) {
  const frameCount = context.sampleRate * 2;
  const buffer = context.createBuffer(1, frameCount, context.sampleRate);
  const data = buffer.getChannelData(0);
  let brown = 0;

  for (let index = 0; index < frameCount; index += 1) {
    const white = Math.random() * 2 - 1;
    if (soundType === "brown") {
      brown = (brown + 0.02 * white) / 1.02;
      data[index] = brown * 3.4;
    } else if (soundType === "rain") {
      const shimmer = 0.45 + Math.random() * 0.55;
      data[index] = white * shimmer * 0.72;
    } else {
      data[index] = white * 0.64;
    }
  }

  return buffer;
}

function stopFocusAudio(updateStatus = true) {
  if (focusAudioSource) {
    try {
      focusAudioSource.stop();
    } catch (error) {
      // Source may already be stopped by the browser.
    }
    focusAudioSource.disconnect();
  }
  if (focusAudioFilter) {
    focusAudioFilter.disconnect();
  }
  if (focusAudioGain) {
    focusAudioGain.disconnect();
  }
  focusAudioSource = null;
  focusAudioFilter = null;
  focusAudioGain = null;
  focusAudioPlaying = false;
  if (musicPlay) {
    musicPlay.textContent = "Start";
  }
  if (updateStatus && musicStatus) {
    musicStatus.textContent = "Sound stopped.";
  }
}

async function startFocusAudio() {
  if (!focusSound || !musicStatus || !musicPlay) {
    return;
  }
  const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
  if (!AudioContextCtor) {
    musicStatus.textContent = "This browser cannot play built-in study sounds.";
    return;
  }

  stopFocusAudio(false);
  if (!focusAudioContext) {
    focusAudioContext = new AudioContextCtor();
  }
  if (focusAudioContext.state === "suspended") {
    await focusAudioContext.resume();
  }

  const soundType = focusSound.value;
  const source = focusAudioContext.createBufferSource();
  const gain = focusAudioContext.createGain();
  source.buffer = buildNoiseBuffer(focusAudioContext, soundType);
  source.loop = true;
  gain.gain.value = getMusicVolume() * 0.36;

  if (soundType === "rain" || soundType === "brown") {
    const filter = focusAudioContext.createBiquadFilter();
    filter.type = soundType === "rain" ? "bandpass" : "lowpass";
    filter.frequency.value = soundType === "rain" ? 950 : 420;
    filter.Q.value = soundType === "rain" ? 0.8 : 0.55;
    source.connect(filter);
    filter.connect(gain);
    focusAudioFilter = filter;
  } else {
    source.connect(gain);
  }

  gain.connect(focusAudioContext.destination);
  source.start();
  focusAudioSource = source;
  focusAudioGain = gain;
  focusAudioPlaying = true;
  musicPlay.textContent = "Stop";
  musicStatus.textContent = `${getFocusSoundLabel()} playing.`;
}

function setMusicTab(selectedTab) {
  musicTabs.forEach((tab) => {
    const isSelected = tab.dataset.musicTab === selectedTab;
    tab.classList.toggle("active", isSelected);
    tab.setAttribute("aria-selected", String(isSelected));
  });
  musicPanels.forEach((panel) => {
    panel.classList.toggle("hidden", panel.dataset.musicPanel !== selectedTab);
  });
  if (selectedTab === "spotify" && spotifyStatusState?.connected) {
    loadSpotifyLibrary();
  }
}

function renderSpotifyResults(data, emptyText = "Search Spotify or play one of your playlists.") {
  if (!spotifyResults) {
    return;
  }
  const tracks = Array.isArray(data?.tracks) ? data.tracks : [];
  const playlists = Array.isArray(data?.playlists) ? data.playlists : [];
  spotifyResults.innerHTML = "";

  const renderSection = (title, items) => {
    if (!items.length) {
      return;
    }
    const heading = document.createElement("div");
    heading.className = "spotify-section-title";
    heading.textContent = title;
    spotifyResults.appendChild(heading);
    items.forEach((item) => {
      const node = document.createElement("div");
      node.className = "spotify-result-card";
      const image = item.image_url
        ? `<img class="spotify-result-art" src="${escapeHtml(item.image_url)}" alt="" loading="lazy" />`
        : '<span class="spotify-result-art" aria-hidden="true"></span>';
      const meta = item.type === "playlist"
        ? `${item.owner || "Playlist"}${item.tracks_total ? ` - ${item.tracks_total} tracks` : ""}`
        : [item.artists, item.album].filter(Boolean).join(" - ");
      node.innerHTML = `
        ${image}
        <div class="spotify-result-body">
          <span class="spotify-result-title">${escapeHtml(item.name || "Untitled")}</span>
          <span class="spotify-result-meta">${escapeHtml(meta || item.type || "Spotify")}</span>
        </div>
        <button
          class="spotify-play-button"
          type="button"
          data-spotify-uri="${escapeHtml(item.uri || "")}"
          data-spotify-type="${escapeHtml(item.type || "track")}"
        >
          Play
        </button>
      `;
      spotifyResults.appendChild(node);
    });
  };

  renderSection("Tracks", tracks);
  renderSection("Playlists", playlists);
  if (!tracks.length && !playlists.length) {
    spotifyResults.innerHTML = `<div class="spotify-status-card"><span>${escapeHtml(emptyText)}</span></div>`;
  }
}

function formatSpotifyTime(milliseconds) {
  const totalSeconds = Math.max(0, Math.floor(Number(milliseconds || 0) / 1000));
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${String(seconds).padStart(2, "0")}`;
}

function spotifyTrackImage(track) {
  const images = track?.album?.images;
  if (!Array.isArray(images) || !images.length) {
    return "";
  }
  return images[0]?.url || "";
}

function spotifyTrackArtists(track) {
  const artists = Array.isArray(track?.artists) ? track.artists : [];
  return artists.map((artist) => artist?.name).filter(Boolean).join(", ");
}

function currentSpotifyPosition() {
  if (!spotifyPlaybackState) {
    return 0;
  }
  const elapsed = spotifyPlaybackState.paused ? 0 : Date.now() - spotifyPlaybackState.updatedAt;
  return Math.min(spotifyPlaybackState.duration, spotifyPlaybackState.position + elapsed);
}

function updateSpotifyProgress() {
  const duration = spotifyPlaybackState?.duration || 0;
  const position = currentSpotifyPosition();
  const percent = duration ? Math.max(0, Math.min(100, (position / duration) * 100)) : 0;
  if (spotifyProgress) {
    spotifyProgress.style.width = `${percent}%`;
  }
  if (spotifyProgressTime) {
    spotifyProgressTime.textContent = `${formatSpotifyTime(position)} / ${formatSpotifyTime(duration)}`;
  }
}

function stopSpotifyProgressTimer() {
  if (spotifyProgressTimer) {
    window.clearInterval(spotifyProgressTimer);
    spotifyProgressTimer = null;
  }
}

function syncSpotifyProgressTimer() {
  stopSpotifyProgressTimer();
  if (spotifyPlaybackState && !spotifyPlaybackState.paused) {
    spotifyProgressTimer = window.setInterval(updateSpotifyProgress, 1000);
  }
}

function renderSpotifyIdle(title, detail) {
  spotifyPlaybackState = null;
  stopSpotifyProgressTimer();
  if (spotifyArt) {
    spotifyArt.style.backgroundImage = "";
  }
  if (spotifyAccount) {
    spotifyAccount.textContent = title;
  }
  if (spotifyStatus) {
    spotifyStatus.textContent = detail;
  }
  if (spotifyPause) {
    spotifyPause.classList.remove("is-playing");
    spotifyPause.setAttribute("aria-label", "Play");
    spotifyPause.setAttribute("title", "Play");
    spotifyPause.disabled = !spotifyDeviceId;
  }
  [spotifyPrev, spotifyNext, spotifyShuffle].forEach((button) => {
    if (button) {
      button.disabled = !spotifyDeviceId;
    }
  });
  updateSpotifyProgress();
}

function renderSpotifyPlaybackState(state) {
  if (!state) {
    renderSpotifyIdle(
      spotifyDeviceId ? "Ready to play" : "Spotify player starting",
      spotifyDeviceId ? "Search or choose a playlist below." : "Preparing this browser as the playback device.",
    );
    return;
  }

  const track = state.track_window?.current_track || {};
  spotifyPlaybackState = {
    paused: Boolean(state.paused),
    position: Number(state.position || 0),
    duration: Number(state.duration || track.duration_ms || 0),
    updatedAt: Date.now(),
  };

  const image = spotifyTrackImage(track);
  if (spotifyArt) {
    spotifyArt.style.backgroundImage = image ? `url(${JSON.stringify(image)})` : "";
  }
  if (spotifyAccount) {
    spotifyAccount.textContent = track.name || "Ready to play";
  }
  if (spotifyStatus) {
    const artists = spotifyTrackArtists(track);
    spotifyStatus.textContent = artists ? `${state.paused ? "Paused" : "Playing"} - ${artists}` : "Spotify";
  }
  if (spotifyPause) {
    spotifyPause.classList.toggle("is-playing", !state.paused);
    spotifyPause.setAttribute("aria-label", state.paused ? "Play" : "Pause");
    spotifyPause.setAttribute("title", state.paused ? "Play" : "Pause");
    spotifyPause.disabled = false;
  }
  [spotifyPrev, spotifyNext, spotifyShuffle].forEach((button) => {
    if (button) {
      button.disabled = false;
    }
  });
  updateSpotifyProgress();
  syncSpotifyProgressTimer();
}

async function loadSpotifyLibrary(force = false) {
  if (!spotifyResults || !spotifyStatusState?.connected || (spotifyLibraryLoaded && !force)) {
    return;
  }
  spotifyResults.innerHTML = '<div class="spotify-status-card"><span>Loading your Spotify playlists...</span></div>';
  try {
    const response = await fetch("/spotify/library");
    const data = await response.json();
    if (!response.ok || data.error) {
      throw new Error(data.error || "Spotify library could not be loaded.");
    }
    spotifyLibraryLoaded = true;
    renderSpotifyResults(data, "No playlists were returned by Spotify.");
  } catch (error) {
    spotifyResults.innerHTML = `<div class="spotify-status-card"><span>${escapeHtml(error.message)}</span></div>`;
  }
}

async function searchSpotify() {
  if (!spotifyStatusState?.connected) {
    window.location.href = "/spotify/login";
    return;
  }
  const query = spotifySearch?.value?.trim() || "";
  if (!query) {
    await loadSpotifyLibrary(true);
    return;
  }
  spotifyResults.innerHTML = '<div class="spotify-status-card"><span>Searching Spotify...</span></div>';
  try {
    const response = await fetch(`/spotify/search?q=${encodeURIComponent(query)}`);
    const data = await response.json();
    if (!response.ok || data.error) {
      throw new Error(data.error || "Spotify search failed.");
    }
    renderSpotifyResults(data, "No Spotify results matched that search.");
  } catch (error) {
    spotifyResults.innerHTML = `<div class="spotify-status-card"><span>${escapeHtml(error.message)}</span></div>`;
  }
}

async function ensureSpotifyPlayerReady() {
  if (!spotifyStatusState?.connected) {
    window.location.href = "/spotify/login";
    return false;
  }
  if (!spotifyDeviceId) {
    await startSpotifyPlayer();
    const startedAt = Date.now();
    while (!spotifyDeviceId && Date.now() - startedAt < 5000) {
      await new Promise((resolve) => window.setTimeout(resolve, 150));
    }
  }
  return Boolean(spotifyDeviceId);
}

async function playSpotifyItem(uri, type) {
  if (!uri) {
    return;
  }
  if (!(await ensureSpotifyPlayerReady())) {
    return;
  }
  spotifyStatus.textContent = "Starting Spotify playback...";
  const payload = type === "playlist"
    ? { device_id: spotifyDeviceId, context_uri: uri }
    : { device_id: spotifyDeviceId, uri };
  try {
    const data = await postJson("/spotify/play", payload);
    if (data.error) {
      throw new Error(data.error);
    }
    spotifyStatus.textContent = "Spotify playback started in this browser.";
    await new Promise((resolve) => window.setTimeout(resolve, 500));
    const state = await spotifyPlayer.getCurrentState();
    if (state) {
      renderSpotifyPlaybackState(state);
    }
    if (spotifyPause) {
      spotifyPause.disabled = false;
    }
  } catch (error) {
    spotifyStatus.textContent = error.message;
  }
}

async function pauseSpotifyPlayback() {
  if (!(await ensureSpotifyPlayerReady())) {
    return;
  }
  spotifyPause.disabled = true;
  try {
    await spotifyPlayer.togglePlay();
    const state = await spotifyPlayer.getCurrentState();
    if (state) {
      renderSpotifyPlaybackState(state);
    } else {
      spotifyStatus.textContent = "Choose a Spotify track or playlist first.";
      spotifyPause.disabled = false;
    }
  } catch (error) {
    spotifyStatus.textContent = error.message;
    spotifyPause.disabled = false;
  }
}

async function skipSpotifyTrack(direction) {
  if (!(await ensureSpotifyPlayerReady())) {
    return;
  }
  const method = direction === "previous" ? "previousTrack" : "nextTrack";
  const button = direction === "previous" ? spotifyPrev : spotifyNext;
  if (!spotifyPlayer?.[method]) {
    spotifyStatus.textContent = "Spotify skip controls are not available.";
    return;
  }
  if (button) {
    button.disabled = true;
  }
  try {
    await spotifyPlayer[method]();
    await new Promise((resolve) => window.setTimeout(resolve, 400));
    const state = await spotifyPlayer.getCurrentState();
    if (state) {
      renderSpotifyPlaybackState(state);
    }
  } catch (error) {
    spotifyStatus.textContent = error.message;
  } finally {
    if (button) {
      button.disabled = false;
    }
  }
}

async function toggleSpotifyShuffle() {
  if (!spotifyShuffle) {
    return;
  }
  if (!(await ensureSpotifyPlayerReady())) {
    return;
  }
  const nextState = !spotifyShuffleEnabled;
  spotifyShuffle.disabled = true;
  try {
    const data = await postJson("/spotify/shuffle", { device_id: spotifyDeviceId, state: nextState });
    if (data.error) {
      throw new Error(data.error);
    }
    spotifyShuffleEnabled = nextState;
    spotifyShuffle.classList.toggle("active", spotifyShuffleEnabled);
    spotifyShuffle.setAttribute("aria-pressed", String(spotifyShuffleEnabled));
    spotifyShuffle.setAttribute("aria-label", spotifyShuffleEnabled ? "Disable shuffle" : "Enable shuffle");
    spotifyShuffle.setAttribute("title", spotifyShuffleEnabled ? "Disable shuffle" : "Enable shuffle");
    spotifyStatus.textContent = spotifyShuffleEnabled ? "Shuffle enabled." : "Shuffle disabled.";
  } catch (error) {
    spotifyStatus.textContent = error.message;
  } finally {
    spotifyShuffle.disabled = false;
  }
}

function renderSpotifyStatus(status) {
  spotifyStatusState = status || {};
  if (!spotifyAccount || !spotifyStatus || !spotifyConnect || !spotifyDisconnect) {
    return;
  }

  if (!spotifyStatusState.configured) {
    renderSpotifyIdle("Spotify is not configured", "Add Spotify credentials before connecting.");
    spotifyConnect.textContent = "Connect Spotify";
    spotifyConnect.disabled = true;
    spotifyConnect.classList.remove("hidden");
    if (spotifyPause) {
      spotifyPause.disabled = true;
    }
    [spotifyPrev, spotifyNext, spotifyShuffle].forEach((button) => {
      if (button) {
        button.disabled = true;
      }
    });
    spotifyDisconnect.disabled = true;
    if (spotifyResults) {
      spotifyResults.innerHTML = "";
    }
    spotifyShuffleEnabled = false;
    spotifyShuffle?.classList.remove("active");
    spotifyShuffle?.setAttribute("aria-pressed", "false");
    return;
  }

  if (!spotifyStatusState.connected) {
    renderSpotifyIdle(
      spotifyStatusState.auth_pending ? "Spotify connection not finished" : "Spotify not connected",
      spotifyStatusState.auth_pending
        ? "A previous Spotify connection attempt did not finish. Reconnect, or reset it first."
        : "Spotify Premium is required for browser playback.",
    );
    spotifyConnect.textContent = spotifyStatusState.auth_pending ? "Reconnect Spotify" : "Connect Spotify";
    spotifyConnect.disabled = false;
    spotifyConnect.classList.remove("hidden");
    if (spotifyPause) {
      spotifyPause.disabled = true;
    }
    [spotifyPrev, spotifyNext, spotifyShuffle].forEach((button) => {
      if (button) {
        button.disabled = true;
      }
    });
    spotifyDisconnect.textContent = "Reset";
    spotifyDisconnect.disabled = !spotifyStatusState.auth_pending;
    spotifyLibraryLoaded = false;
    if (spotifyResults) {
      spotifyResults.innerHTML = "";
    }
    spotifyShuffleEnabled = false;
    spotifyShuffle?.classList.remove("active");
    spotifyShuffle?.setAttribute("aria-pressed", "false");
    return;
  }

  spotifyConnect.classList.add("hidden");
  spotifyConnect.disabled = false;
  if (!spotifyPlaybackState) {
    renderSpotifyIdle(
      spotifyDeviceId ? "Ready to play" : "Spotify player starting",
      spotifyDeviceId ? "Search or choose a playlist below." : "Preparing this browser as the playback device.",
    );
  }
  spotifyDisconnect.textContent = "Disconnect";
  spotifyDisconnect.disabled = false;
  loadSpotifyLibrary();
  if (!spotifyPlayer) {
    startSpotifyPlayer({ silent: true });
  }
}

async function loadSpotifyStatus() {
  if (!spotifyAccount) {
    return;
  }
  try {
    const response = await fetch("/spotify/status");
    renderSpotifyStatus(await response.json());
  } catch (error) {
    renderSpotifyStatus({ configured: false, connected: false });
    spotifyStatus.textContent = "Could not check Spotify status.";
  }
}

function handleSpotifyReturnStatus() {
  const params = new URLSearchParams(window.location.search);
  const spotifyResult = params.get("spotify");
  if (!spotifyResult) {
    return;
  }
  showPage("cram");
  setMusicTab("spotify");
  if (spotifyResult === "connected") {
    spotifyStatus.textContent = "Spotify connected. Preparing the browser player...";
  } else {
    const message = params.get("spotify_message");
    spotifyStatus.textContent = message || "Spotify connection did not finish. Try connecting again.";
  }
  params.delete("spotify");
  const nextQuery = params.toString();
  const nextUrl = `${window.location.pathname}${nextQuery ? `?${nextQuery}` : ""}${window.location.hash}`;
  window.history.replaceState({}, "", nextUrl);
}

function loadSpotifySdk() {
  if (window.Spotify) {
    return Promise.resolve();
  }
  if (spotifySdkPromise) {
    return spotifySdkPromise;
  }

  spotifySdkPromise = new Promise((resolve, reject) => {
    window.onSpotifyWebPlaybackSDKReady = () => resolve();
    const script = document.createElement("script");
    script.src = "https://sdk.scdn.co/spotify-player.js";
    script.async = true;
    script.onerror = () => reject(new Error("Spotify Web Playback SDK could not be loaded."));
    document.body.appendChild(script);
  });
  return spotifySdkPromise;
}

async function spotifyAccessToken() {
  const response = await fetch("/spotify/access-token");
  const data = await response.json();
  if (!response.ok || data.error) {
    throw new Error(data.error || "Spotify access token was not available.");
  }
  return data.access_token;
}

async function transferSpotifyPlayback(deviceId) {
  const data = await postJson("/spotify/transfer-playback", { device_id: deviceId, play: false });
  if (data.error) {
    throw new Error(data.error);
  }
  return data;
}

async function startSpotifyPlayer({ silent = false } = {}) {
  if (!spotifyStatusState?.connected) {
    window.location.href = "/spotify/login";
    return;
  }
  spotifyConnect.disabled = true;
  if (!silent) {
    spotifyStatus.textContent = "Starting Spotify player...";
  }
  try {
    await loadSpotifySdk();
    if (spotifyPlayer) {
      spotifyConnect.disabled = false;
      if (!spotifyPlaybackState) {
        renderSpotifyIdle(
          spotifyDeviceId ? "Ready to play" : "Spotify player starting",
          spotifyDeviceId ? "Search or choose a playlist below." : "Preparing this browser as the playback device.",
        );
      }
      return;
    }

    spotifyPlayer = new window.Spotify.Player({
      name: "Study Buddy",
      getOAuthToken: async (callback) => {
        try {
          callback(await spotifyAccessToken());
        } catch (error) {
          spotifyStatus.textContent = error.message;
          callback("");
        }
      },
      volume: getMusicVolume(),
    });

    spotifyPlayer.addListener("ready", async ({ device_id }) => {
      spotifyDeviceId = device_id;
      try {
        await transferSpotifyPlayback(device_id);
        renderSpotifyIdle("Ready to play", "Search or choose a playlist below.");
        const state = await spotifyPlayer.getCurrentState();
        if (state) {
          renderSpotifyPlaybackState(state);
        }
      } catch (error) {
        spotifyStatus.textContent = error.message;
      }
      renderSpotifyStatus(spotifyStatusState);
    });

    spotifyPlayer.addListener("not_ready", () => {
      spotifyDeviceId = "";
      renderSpotifyIdle("Spotify player disconnected", "The browser playback device is offline.");
      renderSpotifyStatus(spotifyStatusState);
    });

    spotifyPlayer.addListener("player_state_changed", (state) => {
      renderSpotifyPlaybackState(state);
    });

    spotifyPlayer.addListener("initialization_error", ({ message }) => {
      spotifyStatus.textContent = message;
      spotifyConnect.disabled = false;
    });
    spotifyPlayer.addListener("authentication_error", ({ message }) => {
      spotifyStatus.textContent = message;
      spotifyConnect.disabled = false;
    });
    spotifyPlayer.addListener("account_error", ({ message }) => {
      spotifyStatus.textContent = message || "Spotify Premium is required for browser playback.";
      spotifyConnect.disabled = false;
    });
    spotifyPlayer.addListener("playback_error", ({ message }) => {
      spotifyStatus.textContent = message;
    });

    const connected = await spotifyPlayer.connect();
    if (!connected) {
      spotifyStatus.textContent = "Spotify player could not connect.";
      spotifyConnect.disabled = false;
    } else {
      spotifyConnect.disabled = false;
      if (!spotifyDeviceId) {
        renderSpotifyIdle("Spotify player starting", "Preparing this browser as the playback device.");
      }
    }
  } catch (error) {
    spotifyStatus.textContent = error.message;
    spotifyConnect.disabled = false;
  }
}

pageButtons.forEach((button) => {
  button.addEventListener("click", () => {
    showPage(button.dataset.page);
  });
});

showRegister?.addEventListener("click", () => {
  showAuthMode("register");
});

showLogin?.addEventListener("click", () => {
  showAuthMode("login");
});

passwordToggles.forEach((button) => {
  button.addEventListener("click", () => {
    const input = document.getElementById(button.dataset.passwordToggle || "");
    setPasswordVisibility(button, input?.type === "password");
    input?.focus();
  });
});

resetBackLogin?.addEventListener("click", () => {
  pendingResetToken = "";
  showAuthMode("login");
});

forgotPasswordLink?.addEventListener("click", async () => {
  if (!registerForm?.classList.contains("hidden")) {
    showAuthMode("login");
    return;
  }
  const typed = loginIdentifier?.value?.trim() || "";
  const email = typed.includes("@") ? typed : window.prompt("Enter your email for the reset link") || "";
  if (!email.trim()) {
    return;
  }
  forgotPasswordLink.disabled = true;
  if (forgotPasswordStatus) {
    forgotPasswordStatus.textContent = "Preparing reset link...";
  }
  try {
    const data = await postJson("/auth/forgot-password", { email: email.trim() });
    if (forgotPasswordStatus) {
      forgotPasswordStatus.textContent = data.reset_url
        ? `${data.message} Local reset link: ${data.reset_url}`
        : data.message || "If that email is registered, a reset link will be sent to it.";
    }
  } finally {
    forgotPasswordLink.disabled = false;
  }
});

loginForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = loginForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  showAuthError(loginError);
  try {
    const data = await postJson("/auth/login", {
      identifier: loginIdentifier.value.trim(),
      password: loginPassword.value,
    });
    if (data.error) {
      showAuthError(loginError, data.error);
      return;
    }
    setAuthToken(data.session_token);
    loginPassword.value = "";
    hidePasswordFields();
    await showAuthenticatedApp(data.user, "login");
  } finally {
    submitButton.disabled = false;
  }
});

registerForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = registerForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  showAuthError(registerError);
  try {
    const data = await postJson("/auth/register", {
      email: registerEmail.value.trim(),
      username: registerUsername.value.trim(),
      password: registerPassword.value,
      password_confirm: registerPasswordConfirm.value,
    });
    if (data.error) {
      showAuthError(registerError, data.error);
      return;
    }
    setAuthToken(data.session_token);
    registerPassword.value = "";
    registerPasswordConfirm.value = "";
    hidePasswordFields();
    await showAuthenticatedApp(data.user, "register");
  } finally {
    submitButton.disabled = false;
  }
});

resetPasswordForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const submitButton = resetPasswordForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  showAuthError(resetPasswordError);
  try {
    const data = await postJson("/auth/reset-password", {
      token: pendingResetToken,
      password: resetPassword.value,
      password_confirm: resetPasswordConfirm.value,
    });
    if (data.error) {
      showAuthError(resetPasswordError, data.error);
      return;
    }
    setAuthToken(data.session_token);
    pendingResetToken = "";
    resetPassword.value = "";
    resetPasswordConfirm.value = "";
    hidePasswordFields();
    await showAuthenticatedApp(data.user, "login");
  } finally {
    submitButton.disabled = false;
  }
});

logoutToggle?.addEventListener("click", () => {
  const isOpen = !logoutCluster?.classList.contains("open");
  logoutCluster?.classList.toggle("open", isOpen);
  logoutToggle.setAttribute("aria-expanded", String(isOpen));
});

logoutButton?.addEventListener("click", async () => {
  logoutButton.disabled = true;
  const user = currentUser;
  try {
    await postJson("/auth/logout", {});
  } finally {
    setAuthToken("");
    stopFocusAudio(false);
    stopSpotifyProgressTimer();
    logoutButton.disabled = false;
    await showLogoutTransition(user);
    showLoggedOutState();
  }
});

targetScoreButton?.addEventListener("click", () => {
  openTargetScoreModal();
});

targetScoreForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const target = Number(targetScoreInput.value);
  if (!Number.isFinite(target) || target < 0 || target > 100) {
    setModalError(targetScoreError, "Target readiness must be between 0 and 100.");
    return;
  }

  const submitButton = targetScoreForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  setModalError(targetScoreError);
  try {
    const data = await postJson("/study/target", { target_readiness: Math.round(target) });
    if (data.error) {
      setModalError(targetScoreError, data.error);
      return;
    }
    closeEditModals();
    renderDashboard(data.dashboard);
    addMessage("system", `Target score changed to ${Math.round(target)}/100.`);
  } finally {
    submitButton.disabled = false;
  }
});

academicEditForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    item_id: editingAcademicItemId,
    title: academicEditTitle.value.trim(),
    subject: academicEditSubject.value.trim(),
    due_date: academicEditDate.value.trim(),
    kind: academicEditKind.value.trim().toLowerCase(),
  };
  if (!payload.item_id || !payload.title || !payload.subject || !payload.due_date || !payload.kind) {
    setModalError(academicEditError, "Title, subject, due date, and type are required.");
    return;
  }

  const submitButton = academicEditForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  setModalError(academicEditError);
  try {
    const data = await postJson("/study/academic-items/update", payload);
    if (data.error) {
      setModalError(academicEditError, data.error);
      return;
    }
    closeEditModals();
    renderDashboard(data.dashboard);
    addMessage("system", `${payload.title} updated.`);
  } finally {
    submitButton.disabled = false;
  }
});

materialEditForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = materialEditTitle.value.trim();
  if (!editingMaterialId || !title) {
    setModalError(materialEditError, "Material title is required.");
    return;
  }

  const submitButton = materialEditForm.querySelector('button[type="submit"]');
  submitButton.disabled = true;
  setModalError(materialEditError);
  try {
    const data = await postJson("/study/materials/rename", { material_id: editingMaterialId, title });
    if (data.error) {
      setModalError(materialEditError, data.error);
      return;
    }
    closeEditModals();
    renderDashboard(data.dashboard);
    addMessage("system", `${title} updated.`);
  } finally {
    submitButton.disabled = false;
  }
});

modalBackdrop.addEventListener("click", () => {
  closeEditModals();
});

targetScoreClose?.addEventListener("click", () => {
  closeEditModals();
});

targetScoreCancel?.addEventListener("click", () => {
  closeEditModals();
});

academicEditClose.addEventListener("click", () => {
  closeEditModals();
});

academicEditCancel.addEventListener("click", () => {
  closeEditModals();
});

materialEditClose.addEventListener("click", () => {
  closeEditModals();
});

materialEditCancel.addEventListener("click", () => {
  closeEditModals();
});

window.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !targetScoreModal.classList.contains("hidden")) {
    closeEditModals();
  }
  if (event.key === "Escape" && !academicEditModal.classList.contains("hidden")) {
    closeEditModals();
  }
  if (event.key === "Escape" && !materialEditModal.classList.contains("hidden")) {
    closeEditModals();
  }
});

academicList.addEventListener("click", async (event) => {
  const editTarget = event.target.closest(".academic-edit-button");
  if (editTarget) {
    openAcademicEditModal(editTarget);
    return;
  }

  const deleteTarget = event.target.closest(".academic-delete-button");
  if (deleteTarget) {
    const itemId = deleteTarget.dataset.itemId;
    if (!itemId || !window.confirm("Delete this exam, assignment, or quiz?")) {
      return;
    }

    deleteTarget.disabled = true;
    const data = await postJson("/study/academic-items/delete", { item_id: itemId });
    if (data.error) {
      deleteTarget.disabled = false;
      addMessage("system", data.error);
      return;
    }
    renderDashboard(data.dashboard);
    addMessage("system", `${data.deleted_item_title} deleted.`);
    return;
  }

  const focusTarget = event.target.closest(".focus-switch");
  if (!focusTarget) {
    return;
  }
  const data = await postJson("/study/focus", { item_id: focusTarget.dataset.itemId });
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
  syncChatInputHeight();
  await handleCoachQuery(text);
});

chatInput.addEventListener("input", () => {
  syncChatInputHeight();
});

chatInput.addEventListener("keydown", (event) => {
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    chatForm.requestSubmit();
  }
});

coachTabNew.addEventListener("click", async () => {
  renamingCoachTabId = "";
  await updateCoachTabs({ action: "create" });
  chatInput.focus();
});

coachTabs.addEventListener("click", async (event) => {
  const closeTarget = event.target.closest(".coach-tab-close");
  if (closeTarget) {
    if (closeTarget.dataset.tabId === renamingCoachTabId) {
      renamingCoachTabId = "";
    }
    await updateCoachTabs({ action: "delete", tab_id: closeTarget.dataset.tabId });
    return;
  }

  const renameTarget = event.target.closest(".coach-tab-rename");
  if (renameTarget) {
    renamingCoachTabId = renameTarget.dataset.tabId;
    renderCoachTabs({ active_tab_id: activeCoachTabId, memory_count: currentDashboard?.coach?.memory_count || 0, tabs: coachTabsState });
    coachTabs.querySelector(".coach-tab-rename-form input")?.focus();
    return;
  }

  const selectTarget = event.target.closest(".coach-tab-select");
  if (selectTarget && selectTarget.dataset.tabId !== activeCoachTabId) {
    renamingCoachTabId = "";
    await updateCoachTabs({ action: "activate", tab_id: selectTarget.dataset.tabId });
  }
});

coachTabs.addEventListener("submit", async (event) => {
  const form = event.target.closest(".coach-tab-rename-form");
  if (!form) {
    return;
  }
  event.preventDefault();
  const input = form.querySelector("input");
  const title = input.value.trim();
  if (!title) {
    input.focus();
    return;
  }
  renamingCoachTabId = "";
  await updateCoachTabs({ action: "rename", tab_id: form.dataset.tabId, title });
});

window.addEventListener("resize", () => {
  syncStudyRoomLayout();
  syncMaterialsLayout();
});

if ("ResizeObserver" in window && studySide) {
  const studySideObserver = new ResizeObserver(() => {
    syncStudyRoomLayout();
  });
  studySideObserver.observe(studySide);
}

if ("ResizeObserver" in window && materialsUpload) {
  const materialsObserver = new ResizeObserver(() => {
    syncMaterialsLayout();
  });
  materialsObserver.observe(materialsUpload);
}

refreshButton?.addEventListener("click", async () => {
  await loadDashboard();
  addMessage("system", "Everything is up to date.");
});

panicButton?.addEventListener("click", async () => {
  showPage("cram");
  const data = await postJson("/study/panic-mode", { horizon: panicHorizon.value });
  renderPanic(data);
  addMessage("system", `${data.headline} is ready.`);
});

planForm?.addEventListener("submit", async (event) => {
  event.preventDefault();
  const minutes = planMinutesValue();
  if (planMinutes) {
    planMinutes.value = String(minutes);
  }
  const data = await postJson("/study/plan", {
    minutes,
    material_ids: selectedPlanMaterialIds(),
  });
  applyPlanPayload(data, minutes);
  showPage("overview");
  addMessage("system", `${data.headline} is ready.`);
});

panicForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const data = await postJson("/study/panic-mode", { horizon: panicHorizon.value });
  renderPanic(data);
});

if (checkinForm) {
  checkinForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!checkinTopic.value) {
      addMessage("system", "Add notes for this focus before saving a readiness check.");
      return;
    }
    const data = await postJson("/study/check-in", {
      topic_id: checkinTopic.value,
      confidence: Number(checkinConfidence.value),
      quiz_score: Number(checkinQuiz.value),
      minutes_studied: Number(checkinMinutes.value),
    });
    if (data.error) {
      addMessage("system", data.error);
      return;
    }
    renderDashboard(data.dashboard);
    renderStack(
      checkinResult,
      [data],
      (item) => simpleCard("Check-in saved", item.topic.title || item.topic.name, item.insight)
    );
    addMessage("system", data.insight);
  });
}

materialsForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const title = materialsTitle.value.trim();
  const academicItemId = materialsItem.value;
  const text = materialsText.value.trim();
  const [file] = materialsFile.files || [];
  const isPdf = file && (file.type === "application/pdf" || /\.pdf$/i.test(file.name));

  if (!title && !file) {
    addMessage("system", "Add a material title first.");
    return;
  }
  if (!academicItemId) {
    addMessage("system", "Choose which exam, assignment, or quiz this material belongs to.");
    return;
  }

  let data;
  if (isPdf) {
    const formData = new FormData();
    formData.append("title", title);
    formData.append("academic_item_id", academicItemId);
    formData.append("file", file);
    data = await postForm("/study/materials/upload", formData);
  } else {
    if (!title || !text) {
      addMessage("system", "Add a material title and some notes first, or upload a PDF.");
      return;
    }
    data = await postJson("/study/materials", { title, text, academic_item_id: academicItemId });
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
  const importSuffix = data.import_note ? ` ${data.import_note}` : "";
  const analysisSuffix = data.analysis_source ? ` Analysis: ${data.analysis_source}.` : "";
  addMessage(
    "system",
    `Created ${data.created_topics.length} topic${data.created_topics.length === 1 ? "" : "s"} from your notes.${importSuffix}${analysisSuffix}`
  );
});

materialsOutput.addEventListener("click", async (event) => {
  const editTarget = event.target.closest(".material-edit-button");
  if (editTarget) {
    openMaterialEditModal(editTarget);
    return;
  }

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

musicTabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    setMusicTab(tab.dataset.musicTab);
  });
});

musicPlay?.addEventListener("click", async () => {
  if (focusAudioPlaying) {
    stopFocusAudio();
    return;
  }
  await startFocusAudio();
});

musicStop?.addEventListener("click", () => {
  stopFocusAudio();
});

focusSound?.addEventListener("change", async () => {
  saveMusicSettings();
  if (focusAudioPlaying) {
    await startFocusAudio();
    return;
  }
  musicStatus.textContent = `${getFocusSoundLabel()} selected.`;
});

musicVolume?.addEventListener("input", () => {
  syncMusicVolume();
});

spotifyConnect?.addEventListener("click", () => {
  if (!spotifyStatusState?.connected) {
    window.location.href = "/spotify/login";
    return;
  }
  startSpotifyPlayer();
});

spotifyPause?.addEventListener("click", () => {
  pauseSpotifyPlayback();
});

spotifyPrev?.addEventListener("click", () => {
  skipSpotifyTrack("previous");
});

spotifyNext?.addEventListener("click", () => {
  skipSpotifyTrack("next");
});

spotifyShuffle?.addEventListener("click", () => {
  toggleSpotifyShuffle();
});

spotifySearchButton?.addEventListener("click", () => {
  searchSpotify();
});

spotifySearch?.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    event.preventDefault();
    searchSpotify();
  }
});

spotifyResults?.addEventListener("click", (event) => {
  const button = event.target.closest("[data-spotify-uri]");
  if (!button) {
    return;
  }
  playSpotifyItem(button.dataset.spotifyUri || "", button.dataset.spotifyType || "track");
});

spotifyDisconnect?.addEventListener("click", async () => {
  spotifyDisconnect.disabled = true;
  if (spotifyPlayer) {
    spotifyPlayer.disconnect();
    spotifyPlayer = null;
  }
  spotifyDeviceId = "";
  spotifyLibraryLoaded = false;
  spotifyPlaybackState = null;
  spotifyShuffleEnabled = false;
  spotifyShuffle?.classList.remove("active");
  spotifyShuffle?.setAttribute("aria-pressed", "false");
  stopSpotifyProgressTimer();
  if (spotifyResults) {
    spotifyResults.innerHTML = "";
  }
  const data = await postJson("/spotify/disconnect", {});
  renderSpotifyStatus(data);
});

window.addEventListener("beforeunload", () => {
  stopFocusAudio(false);
  stopSpotifyProgressTimer();
});

async function bootAppData() {
  if (appBooted) {
    await loadDashboard();
    return;
  }
  appBooted = true;
  restoreActivePage();
  restoreMusicSettings();
  syncMusicVolume();
  await loadSpotifyStatus();
  handleSpotifyReturnStatus();
  syncTimerInput();
  renderTimer();
  updateTimerPrimaryButton();
  syncChatInputHeight();
  syncStudyRoomLayout();
  syncMaterialsLayout();
  await loadDashboard();
}

async function boot() {
  await checkAuthSession();
}

boot();
