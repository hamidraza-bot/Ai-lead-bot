# AI Lead Capture + Voice Receptionist System 🤖📞

![Status](https://img.shields.io/badge/Status-In%20Development-yellow?style=flat-square)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![n8n](https://img.shields.io/badge/n8n-EA4B71?style=flat-square&logo=n8n&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)

> 🚧 **In active development.** This repository documents a system currently being built — an AI front desk that works 24/7 for local service businesses. Code is being added incrementally; the design below is the target architecture, not a finished product.

## 💡 The Idea

What if a local service business — HVAC, dental, cleaning, roofing — could have an **AI front desk working 24/7**? No missed calls, no leads lost after hours, every inquiry answered, qualified, and logged.

That's what this project builds: a complete **lead capture system** combining an AI chatbot and an AI voice receptionist.

## 🎯 What It Will Do

- 💬 **AI chatbot** — answers FAQs, qualifies visitors, and captures lead details (name, phone, service needed, urgency) from the business website
- 📞 **AI voice receptionist** — handles inbound calls: greets callers, answers common questions, books/takes messages, and escalates to a human when needed
- 🔄 **n8n automation** — routes every captured lead to the business's CRM and Google Sheets in real time, and notifies the owner
- 📊 **Lead logging** — every conversation and call is logged with source, summary, and status so nothing is lost

## 🏗️ Planned Architecture

```
Website visitor ──▶ AI Chatbot ──┐
                                 ├──▶ n8n Webhook ──▶ CRM + Google Sheets + Owner notification
Phone caller ────▶ Voice AI ────┘        (lead record, call summary, follow-up status)
```

| Component | Planned stack |
|---|---|
| Chatbot | Python / JavaScript + OpenAI |
| Voice receptionist | Telephony API + speech-to-text / text-to-speech + OpenAI |
| Automation & routing | n8n workflows (webhooks, CRM, Google Sheets) |
| Lead storage | Google Sheets / CRM |

## 📌 Current Status

- [x] Concept & architecture defined
- [x] Demo chatbot + n8n lead flow proven in the [1-way-heating-air](https://github.com/hamidraza-bot/1-way-heating-air) project
- [ ] Chatbot lead-capture module
- [ ] Voice receptionist (inbound call handling)
- [ ] n8n routing workflows (see [n8n-ai-automation-templates](https://github.com/hamidraza-bot/n8n-ai-automation-templates) for reusable templates)
- [ ] End-to-end testing & documentation

## 🤝 Related Projects

- [1-way-heating-air](https://github.com/hamidraza-bot/1-way-heating-air) — working demo of the chatbot + n8n lead flow for an HVAC business
- [n8n-ai-automation-templates](https://github.com/hamidraza-bot/n8n-ai-automation-templates) — reusable n8n workflow templates (lead capture, voice receptionist, scraping, inventory sync)

## 📄 License

MIT — see [LICENSE](LICENSE).

---

Built by [Hamid Raza](https://github.com/hamidraza-bot) · AI Automation Engineer · [Fiverr](https://www.fiverr.com/hamid_buildai)
