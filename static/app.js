const chatLog = document.querySelector("#chat-log");
const chatForm = document.querySelector("#chat-form");
const chatInput = document.querySelector("#chat-input");
const weekSummary = document.querySelector("#week-summary");
const planningSignals = document.querySelector("#planning-signals");
const quickResults = document.querySelector("#quick-results");
const providerName = document.querySelector("#provider-name");
const voiceStatus = document.querySelector("#voice-status");
const lastHeard = document.querySelector("#last-heard");
const weekHealth = document.querySelector("#week-health");
const connectGoogle = document.querySelector("#connect-google");
const disconnectGoogle = document.querySelector("#disconnect-google");
const calendarSourceNote = document.querySelector("#calendar-source-note");

const speakButton = document.querySelector("#speak-btn");
const stopButton = document.querySelector("#stop-btn");
const refreshButton = document.querySelector("#refresh-btn");
const slotForm = document.querySelector("#slot-form");
const focusForm = document.querySelector("#focus-form");
const slotPurpose = document.querySelector("#slot-purpose");
const slotDuration = document.querySelector("#slot-duration");
const focusDuration = document.querySelector("#focus-duration");

let recognition;
let isListening = false;
let heardTranscript = "";
let listenTimer = null;

function createMessageNode(role) {
  const node = document.createElement("div");
  node.className = `message ${role} entering`;
  chatLog.appendChild(node);
  chatLog.scrollTop = chatLog.scrollHeight;
  window.requestAnimationFrame(() => {
    node.classList.remove("entering");
  });
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
    <span class="pending-label">Planning response</span>
    <span class="thinking-dots" aria-hidden="true">
      <span></span><span></span><span></span>
    </span>
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
    await wait(index === 0 ? 110 : 70);
  }
}

function speak(text) {
  if (!("speechSynthesis" in window)) {
    return;
  }
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.rate = 1;
  utterance.pitch = 1;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  return response.json();
}

function renderCards(target, items, render) {
  target.innerHTML = "";
  if (!items || items.length === 0) {
    const empty = document.createElement("div");
    empty.className = "card muted";
    empty.textContent = "Nothing to show right now.";
    target.appendChild(empty);
    return;
  }
  items.forEach((item, index) => {
    const card = render(item);
    card.classList.add("stagger-in");
    card.style.setProperty("--stagger-index", index);
    target.appendChild(card);
  });
}

function summaryCard(day) {
  const node = document.createElement("div");
  node.className = "card";
  node.innerHTML = `
    <strong>${day.label}</strong>
    <div class="muted">${day.count} events</div>
    <div>${day.headline}</div>
  `;
  return node;
}

function suggestionCard(item) {
  const node = document.createElement("div");
  node.className = "card";
  node.innerHTML = `
    <strong>${item.title}</strong>
    <div class="muted">${item.kind}</div>
    <div>${item.detail}</div>
  `;
  return node;
}

function slotCard(slot) {
  const node = document.createElement("div");
  node.className = "card";
  const start = new Date(slot.start);
  const end = new Date(slot.end);
  node.innerHTML = `
    <strong>${start.toLocaleString()}</strong>
    <div class="muted">Ends ${end.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</div>
    <div>${slot.rationale}</div>
  `;
  return node;
}

function buildWeekHealth(summary, analysis) {
  const events = summary.total_events || 0;
  const issues = (analysis.conflicts?.length || 0) + (analysis.suggestions?.length || 0);
  if (!events) {
    return "No events yet. Block deep work early.";
  }
  if (!issues) {
    return `${events} events with no major planning risks detected.`;
  }
  return `${events} events with ${issues} planning signals to review.`;
}

function applySourceState(source) {
  providerName.textContent = source.label;
  connectGoogle.classList.toggle("hidden", !source.oauth_ready || source.mode === "google");
  disconnectGoogle.classList.toggle("hidden", source.mode !== "google");

  if (!source.oauth_ready) {
    calendarSourceNote.textContent =
      "Owner setup required once: add Google OAuth client credentials on the server, then users can connect normally.";
    return;
  }

  if (source.mode === "google" && source.connected) {
    calendarSourceNote.textContent = "Connected with Google OAuth. Events now come from your Google Calendar.";
    return;
  }

  calendarSourceNote.textContent = "Connect Google Calendar to replace the demo schedule with your real events.";
}

async function loadWeek() {
  const response = await fetch("/calendar/week-summary");
  const data = await response.json();
  applySourceState(data.source);
  renderCards(weekSummary, data.summary.days, summaryCard);
  renderCards(planningSignals, data.analysis.suggestions, suggestionCard);
  weekHealth.textContent = buildWeekHealth(data.summary, data.analysis);
}

async function handleAssistantQuery(text) {
  addMessage("user", text);
  const pendingNode = addPendingAssistantMessage();
  const data = await postJson("/assistant/query", { text });
  await wait(220);
  await revealAssistantMessage(pendingNode, data.reply);
  speak(data.reply);
  if (data.analysis?.suggestions) {
    renderCards(planningSignals, data.analysis.suggestions, suggestionCard);
  }
  if (data.slots) {
    renderCards(quickResults, data.slots, slotCard);
  }
  if (data.event || data.analysis) {
    await loadWeek();
  }
}

function wait(ms) {
  return new Promise((resolve) => window.setTimeout(resolve, ms));
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = chatInput.value.trim();
  if (!text) {
    return;
  }
  chatInput.value = "";
  await handleAssistantQuery(text);
});

refreshButton.addEventListener("click", async () => {
  await loadWeek();
  addMessage("system", "Upcoming schedule refreshed.");
});

slotForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const duration = Number(slotDuration.value || 120);
  const title = slotPurpose.value.trim() || "study";
  const data = await postJson("/planner/suggest-slots", {
    duration_minutes: duration,
    title,
  });
  renderCards(quickResults, data.slots, slotCard);
});

focusForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const duration = Number(focusDuration.value || 120);
  const data = await postJson("/planner/protect-focus-time", { duration_minutes: duration });
  quickResults.innerHTML = "";
  const node = document.createElement("div");
  node.className = "card";
  if (data.slot) {
    const start = new Date(data.slot.start);
    const end = new Date(data.slot.end);
    node.innerHTML = `
      <strong>Suggested focus block</strong>
      <div>${start.toLocaleString()} - ${end.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}</div>
      <div class="muted">${data.reason}</div>
    `;
  } else {
    node.innerHTML = `<strong>No focus block found</strong><div class="muted">${data.reason}</div>`;
  }
  quickResults.appendChild(node);
});

disconnectGoogle.addEventListener("click", async () => {
  const data = await postJson("/calendar/source", { mode: "local" });
  if (data.error) {
    addMessage("system", data.error);
    return;
  }
  addMessage("system", "Switched back to the demo calendar.");
  await loadWeek();
});

function setupVoice() {
  const Recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!Recognition) {
    voiceStatus.textContent = "Voice unavailable in this browser";
    speakButton.disabled = true;
    stopButton.disabled = true;
    addMessage("system", "Voice input is unavailable in this browser. Text input still works.");
    return;
  }

  recognition = new Recognition();
  recognition.lang = "en-SG";
  recognition.interimResults = true;
  recognition.maxAlternatives = 1;
  recognition.continuous = false;

  speakButton.addEventListener("click", () => {
    if (isListening) {
      stopListening("Stopped listening.");
      return;
    }
    startListening();
  });

  stopButton.addEventListener("click", () => {
    stopListening("Stopped listening.");
  });

  recognition.addEventListener("start", () => {
    isListening = true;
    heardTranscript = "";
    speakButton.textContent = "Listening...";
    stopButton.disabled = false;
    voiceStatus.textContent = "Listening for your request";
    lastHeard.textContent = "Listening for transcript...";
    if ("speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    resetListenTimer();
  });

  recognition.addEventListener("result", async (event) => {
    const transcript = Array.from(event.results)
      .map((result) => result[0]?.transcript || "")
      .join(" ")
      .trim();
    if (!transcript) {
      return;
    }
    heardTranscript = transcript;
    chatInput.value = transcript;
    lastHeard.textContent = transcript;
    const finalResult = event.results[event.results.length - 1].isFinal;
    voiceStatus.textContent = finalResult ? "Heard request, sending..." : "Capturing speech...";
    resetListenTimer();
    if (finalResult) {
      recognition.stop();
      await handleAssistantQuery(transcript);
    }
  });

  recognition.addEventListener("speechend", () => {
    voiceStatus.textContent = "Processing speech...";
    recognition.stop();
  });

  recognition.addEventListener("end", () => {
    clearListenTimer();
    isListening = false;
    speakButton.textContent = "Speak to assistant";
    stopButton.disabled = true;
    if (!heardTranscript) {
      voiceStatus.textContent = "No speech captured";
      addMessage("system", "I did not catch anything from the microphone. Try again or type your request.");
      return;
    }
    voiceStatus.textContent = "Ready";
  });

  recognition.addEventListener("error", (event) => {
    clearListenTimer();
    isListening = false;
    speakButton.textContent = "Speak to assistant";
    stopButton.disabled = true;
    const message = voiceErrorMessage(event.error);
    voiceStatus.textContent = message;
    addMessage("system", message);
  });
}

function startListening() {
  try {
    recognition.start();
  } catch (error) {
    voiceStatus.textContent = "Voice start failed";
    addMessage("system", "The browser did not allow speech recognition to start. Try again or refresh the page.");
  }
}

function stopListening(statusText) {
  clearListenTimer();
  if (!recognition || !isListening) {
    voiceStatus.textContent = statusText;
    return;
  }
  try {
    recognition.stop();
  } catch (error) {
    recognition.abort();
  }
  voiceStatus.textContent = statusText;
}

function resetListenTimer() {
  clearListenTimer();
  listenTimer = window.setTimeout(() => {
    stopListening("Listening timed out. Try again.");
  }, 8000);
}

function clearListenTimer() {
  if (listenTimer) {
    window.clearTimeout(listenTimer);
    listenTimer = null;
  }
}

function voiceErrorMessage(code) {
  if (code === "not-allowed") {
    return "Microphone permission was denied.";
  }
  if (code === "no-speech") {
    return "No speech was detected.";
  }
  if (code === "audio-capture") {
    return "No usable microphone was found.";
  }
  if (code === "network") {
    return "The browser speech service hit a network problem.";
  }
  return "Voice recognition failed. You can still type your request.";
}

function handleOAuthResultMessage() {
  const params = new URLSearchParams(window.location.search);
  if (params.get("google_auth") === "success") {
    addMessage("system", "Google Calendar connected successfully.");
  }
  const rawError = params.get("error") || params.get("google_auth_error");
  if (rawError) {
    addMessage("system", rawError);
  }
  if (params.toString()) {
    window.history.replaceState({}, "", window.location.pathname);
  }
}

addMessage(
  "assistant",
  "I can summarize your week, add an event, suggest the best slot for work, or protect focus time.\n\nTry:\n• What does my week look like?\n• Add project sync tomorrow at 3 pm for 1 hour."
);
setupVoice();
handleOAuthResultMessage();
loadWeek();
