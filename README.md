# Aria — AI Voice Receptionist (Full System) 🤖📞

![Status](https://img.shields.io/badge/Status-Working%20Demo-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-EA4B71?style=flat-square&logo=n8n&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

> **Demo project — sample data only.** Aria is a clearly-labelled **rule-based demo agent** in this repo: no real AI model, no real telephony, no real patients or clients. The fictional clinic "BrightSmile Dental" and all prices, callers and bookings are illustrative.

## 💡 What is Aria?

Aria is a complete **AI voice receptionist system** for a local service business. A patient calls or chats, Aria answers, books the appointment, and logs everything — 24/7, without a human picking up the phone.

This repo is the **full working system**, not a concept:

- 🖥️ **A runnable demo server** (Python, standard library only) — live chat, appointment booking, simulated incoming calls, and a call log dashboard
- ⚙️ **A production n8n workflow** — Webhook → AI Agent (OpenAI) → Google Sheets → Gmail summary → Respond to Webhook
- 🌐 **A polished demo UI** — try it live, no install needed

**Live demo:** https://muse.ai/s/ai-receptionist-demo-bo6xruxzxjxzxz7xl/MFHMIoRafwIkYWJbyn6NgwLPnq03uU6PE797n4mp13U

## ✨ Features

- 💬 **Live chat with Aria** — asks about services, prices, opening hours, booking (rule-based, instant answers)
- 📅 **Appointment booking** — validates name/phone/service/date/time, returns a reference number (e.g. `BR-7F3K9Q`), saves to the call log
- 📞 **Simulated incoming calls** — four scripted scenarios: booking, reschedule, pricing, emergency — each with a full transcript
- 📋 **Call log dashboard** — every booking and simulated call, newest first
- 🔄 **n8n pipeline** — the same flow, production-ready, importable in one click
- 🛠️ **Zero dependencies** — Python 3 standard library only; no `pip install`, no API keys, no external network calls

## 🚀 Quick start

```bash
git clone https://github.com/hamidraza-bot/Ai-lead-bot.git
cd Ai-lead-bot
python3 server.py
```

Then open **http://localhost:8000** in your browser.

That's it. No setup, no keys, no database — bookings are stored in memory and appended to `calls.json` in the project folder.

## 🧪 Try it

| Try this | What happens |
|---|---|
| Chat: *"How much is teeth whitening?"* | Aria answers: $199 (sample price) |
| Chat: *"What are your opening hours?"* | Mon–Fri 9 AM–6 PM, Sat 10 AM–3 PM, Sun closed |
| Book an appointment | Form validates, returns a reference like `BR-7F3K9Q`, appears in the log |
| Simulate a call → Emergency | Full scripted transcript + entry in the log |

## 🔌 API endpoints

The frontend talks to these endpoints on `http://localhost:8000`:

| Method | Endpoint | Body / Response |
|---|---|---|
| `POST` | `/api/chat` | `{ "message": "..." }` → `{ "reply": "..." }` |
| `POST` | `/api/book` | `{ "name", "phone", "service", "date", "time" }` → `{ "reference", "message" }` (400 with `details` on invalid input) |
| `GET` | `/api/calls` | → `{ "calls": [...] }` newest first |
| `POST` | `/api/call` | `{ "scenario": "booking" \| "reschedule" \| "pricing" \| "emergency" }` → `{ "scenario", "transcript", "log_id" }` |
| `GET` | `/api/health` | → `{ "status": "ok", "calls": N }` |

## ⚙️ n8n workflow (production)

The file [`n8n/aria-voice-receptionist.json`](n8n/aria-voice-receptionist.json) is the production version of the same system, ready to import:

1. In n8n: **Workflows → ⋯ → Import from File**, choose the JSON.
2. Connect your own credentials (nothing real is in the file — only placeholder names):
   - **OpenAI account** — for the AI Agent node
   - **Google Sheets account** — the "Call Log" sheet
   - **Gmail account** — the summary email
3. Replace the placeholder values:
   - `YOUR_GOOGLE_SHEET_ID` → your sheet's ID (or pick it in the node)
   - `owner@brightsmile.example` → the clinic owner's real email
   - The system prompt in the AI Agent node → your business's own services, prices and hours
4. **Activate** the workflow, then point your phone system (e.g. Twilio) or website chat widget at the webhook URL `POST /webhook/aria-call` with `{ "caller", "phone", "message" }`.

### How it flows

```
Phone call / chat ──▶ Webhook ──▶ AI Agent (OpenAI) ──▶ Google Sheets (log)
                                                            │
                                                            ▼
                                              Gmail summary to owner
                                                            │
                                                            ▼
                                              Respond to Webhook
```

More reusable templates: [n8n-ai-automation-templates](https://github.com/hamidraza-bot/n8n-ai-automation-templates)

## 📁 Project structure

```
Ai-lead-bot/
├── server.py                  # Python stdlib-only server + rule-based Aria + JSON API
├── public/
│   ├── index.html             # Demo UI (chat, booking, calls, log, how-it-works)
│   ├── style.css              # Dark theme, no frameworks
│   └── app.js                 # Talks to /api/*, no external requests
├── n8n/
│   └── aria-voice-receptionist.json   # Importable production n8n workflow
├── calls.json                 # Runtime log (created on first run, git-ignored)
├── .gitignore
└── README.md
```

## 🛠️ Tech stack

| Layer | Stack |
|---|---|
| Demo server | Python 3 (stdlib `http.server` only) |
| Frontend | Plain HTML / CSS / JavaScript, no build step |
| Production automation | n8n (Webhook, AI Agent, Google Sheets, Gmail) |
| Production AI | OpenAI via n8n's AI Agent node (your own key) |

## 🗺️ Roadmap

- [x] Rule-based demo server + UI (this repo, live now)
- [x] n8n production workflow
- [ ] Real telephony integration (Twilio / VoIP) for live inbound calls
- [ ] Live LLM mode in the demo server (optional `OPENAI_API_KEY`)
- [ ] SMS confirmation after booking (Twilio)
- [ ] Multi-business config (services/prices/hours from one JSON file)

## ⚠️ Honest notes

- This repo is a **demo**, not a deployed product. Prices, callers and bookings are sample data.
- The local server uses a **rule-based** agent — it matches keywords, it does not call any AI model. The n8n workflow is where the real OpenAI agent lives, and it needs your own credentials.
- No client results, revenue or reviews are claimed anywhere in this project.

## 🤝 Related projects

- [n8n-ai-automation-templates](https://github.com/hamidraza-bot/n8n-ai-automation-templates) — 4 production-ready n8n workflow templates (lead capture, voice receptionist, listings scraper, inventory sync)
- [1-way-heating-air](https://github.com/hamidraza-bot/1-way-heating-air) — HVAC website with AI chatbot + n8n lead flow

## 📄 License

MIT — see [LICENSE](LICENSE).

---

Built by [Hamid Raza](https://github.com/hamidraza-bot) · AI Automation Engineer · [LinkedIn](https://www.linkedin.com/in/hamid-raza-b4338938a) · [Fiverr](https://www.fiverr.com/hamid_buildai) · [Upwork](https://www.upwork.com/freelancers/~016420d484c7f28d4f)
