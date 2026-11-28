/* Aria — AI Voice Receptionist demo UI
   Talks to the local Python server (server.py):
     POST /api/chat   {message}        -> {reply}
     POST /api/book   {name, phone, service, date, time} -> {reference, message}
     GET  /api/calls                   -> {calls: [...]}
     POST /api/call   {scenario}       -> {scenario, transcript, log_id}
   No external requests. All data shown is demo / illustrative.
*/
"use strict";

const $ = (sel) => document.querySelector(sel);
const chatWindow = $("#chatWindow");
const chatForm = $("#chatForm");
const chatInput = $("#chatInput");
const bookForm = $("#bookForm");
const bookResult = $("#bookResult");
const callsBody = $("#callsBody");
const transcriptBox = $("#transcript");

async function api(path, options = {}) {
  const res = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) {
    const details = Array.isArray(data.details) ? data.details.join("; ") : data.error;
    throw new Error(details || `Request failed (${res.status})`);
  }
  return data;
}

function esc(text) {
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function addMessage(who, text) {
  const div = document.createElement("div");
  div.className = who === "Aria" ? "msg msg-aria" : "msg msg-user";
  div.innerHTML = `<span class="msg-name">${esc(who)}</span>${esc(text)}`;
  chatWindow.appendChild(div);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

/* ---------------- Chat ---------------- */

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  addMessage("You", message);
  chatInput.value = "";
  addMessage("Aria", "…");
  const typing = chatWindow.lastElementChild;
  try {
    const { reply } = await api("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message }),
    });
    typing.innerHTML = `<span class="msg-name">Aria</span>${esc(reply)}`;
  } catch (err) {
    typing.innerHTML = `<span class="msg-name">Aria</span>Sorry — the demo server didn't answer (${esc(err.message)}). Is <code>python3 server.py</code> running?`;
  }
  chatWindow.scrollTop = chatWindow.scrollHeight;
});

document.querySelectorAll("#quickChips button").forEach((btn) => {
  btn.addEventListener("click", () => {
    chatInput.value = btn.dataset.q;
    chatForm.requestSubmit();
  });
});

/* ---------------- Booking ---------------- */

bookForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  bookResult.hidden = true;
  bookResult.classList.remove("error-box");

  // Strip the " — $xx" suffix: server expects the plain service name.
  const serviceRaw = $("#bkService").value;
  const service = serviceRaw.split(" — ")[0];

  const payload = {
    name: $("#bkName").value.trim(),
    phone: $("#bkPhone").value.trim(),
    service,
    date: $("#bkDate").value,
    time: $("#bkTime").value,
  };

  try {
    const data = await api("/api/book", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    bookResult.innerHTML =
      `<strong>✅ ${esc(data.message)}</strong><br>` +
      `A confirmation would be sent by text in the real system. ` +
      `Keep your reference: <code>${esc(data.reference)}</code>`;
    bookResult.hidden = false;
    bookForm.reset();
    await loadCalls();
  } catch (err) {
    bookResult.innerHTML = `<strong>⚠️ Booking failed.</strong> ${esc(err.message)}`;
    bookResult.classList.add("error-box");
    bookResult.hidden = false;
  }
});

/* ---------------- Simulated calls ---------------- */

document.querySelectorAll("[data-scenario]").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const scenario = btn.dataset.scenario;
    transcriptBox.hidden = false;
    transcriptBox.innerHTML = `<div class="msg msg-aria"><span class="msg-name">Aria</span>📞 Incoming ${esc(scenario)} call — connecting…</div>`;
    try {
      const { transcript } = await api("/api/call", {
        method: "POST",
        body: JSON.stringify({ scenario }),
      });
      transcriptBox.innerHTML = transcript
        .map(
          (line) =>
            `<div class="msg ${line.speaker === "Aria" ? "msg-aria" : "msg-user"}">` +
            `<span class="msg-name">${esc(line.speaker)}</span>${esc(line.text)}</div>`
        )
        .join("");
      await loadCalls();
    } catch (err) {
      transcriptBox.innerHTML = `<div class="msg msg-aria"><span class="msg-name">Aria</span>Sorry — the demo server didn't answer (${esc(err.message)}).</div>`;
    }
  });
});

/* ---------------- Call log ---------------- */

async function loadCalls() {
  try {
    const { calls } = await api("/api/calls");
    if (!calls.length) {
      callsBody.innerHTML = `<tr><td colspan="5">No calls or bookings yet.</td></tr>`;
      return;
    }
    callsBody.innerHTML = calls
      .map(
        (c) =>
          `<tr>` +
          `<td><code>${esc(c.id)}</code></td>` +
          `<td><span class="pill ${c.type === "booking" ? "pill-booking" : "pill-call"}">${esc(c.type)}</span></td>` +
          `<td>${esc(c.caller)}</td>` +
          `<td>${esc(c.summary)}</td>` +
          `<td>${esc(c.time)}</td>` +
          `</tr>`
      )
      .join("");
  } catch (err) {
    callsBody.innerHTML = `<tr><td colspan="5">Could not load the log (${esc(err.message)}). Is the server running?</td></tr>`;
  }
}

$("#refreshLog").addEventListener("click", loadCalls);

// Default booking date = tomorrow, so the form works out of the box.
(function setDefaultDate() {
  const tomorrow = new Date(Date.now() + 86400000);
  $("#bkDate").value = tomorrow.toISOString().slice(0, 10);
})();

loadCalls();
