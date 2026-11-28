#!/usr/bin/env python3
"""
Aria — AI Voice Receptionist (Full System)
==========================================

A small, dependency-free demo server for a sample dental clinic,
"BrightSmile Dental".  It serves the static frontend from ./public
and exposes a tiny JSON API used by the demo UI:

    POST /api/chat   - rule-based chat with Aria (demo agent)
    POST /api/book   - book an appointment, returns a reference number
    GET  /api/calls  - call / booking log
    POST /api/call   - simulate an incoming phone call (scripted transcript)

Run it with:

    python3 server.py

Then open http://localhost:8000 in your browser.

Standard library only — no pip installs, no external network calls.

IMPORTANT: Aria here is a clearly-labelled RULE-BASED demo agent.
There is no real AI model, no real telephony and no real patient
data.  Everything (services, prices, callers, bookings) is sample
data for demonstration purposes only.
"""

import json
import os
import re
import secrets
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

PORT = 8000
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
CALLS_FILE = os.path.join(BASE_DIR, "calls.json")

# ---------------------------------------------------------------------------
# Demo business data (sample data only — BrightSmile Dental is fictional)
# ---------------------------------------------------------------------------

CLINIC = {
    "name": "BrightSmile Dental",
    "phone": "(555) 014-8890",
    "address": "12 Market Street, Springfield",
    "hours": "Mon–Fri 9:00 AM – 6:00 PM, Sat 10:00 AM – 3:00 PM, Sun closed",
}

SERVICES = {
    "check-up & cleaning": 89,
    "checkup": 89,
    "cleaning": 89,
    "filling": 120,
    "root canal": 450,
    "whitening": 199,
    "tooth extraction": 150,
    "braces consultation": 0,
    "emergency": 0,
}

# ---------------------------------------------------------------------------
# Call log (in-memory + persisted to calls.json)
# ---------------------------------------------------------------------------


def _seed_calls():
    """A few illustrative log entries so the dashboard is not empty."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    return [
        {
            "id": "CL-1001",
            "type": "call",
            "scenario": "booking",
            "caller": "Sarah M.",
            "summary": "Booked Check-up & Cleaning for Fri 27 Nov at 10:45.",
            "time": now,
            "demo": True,
        },
        {
            "id": "CL-1002",
            "type": "call",
            "scenario": "pricing",
            "caller": "James K.",
            "summary": "Asked about whitening price ($199) and opening hours.",
            "time": now,
            "demo": True,
        },
    ]


def load_calls():
    """Load the log from calls.json, or seed demo entries on first run."""
    if os.path.exists(CALLS_FILE):
        try:
            with open(CALLS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
        except (OSError, json.JSONDecodeError):
            pass
    calls = _seed_calls()
    save_calls(calls)
    return calls


def save_calls(calls):
    """Persist the log.  Best-effort: a failed write never breaks a request."""
    try:
        with open(CALLS_FILE, "w", encoding="utf-8") as f:
            json.dump(calls, f, indent=2)
    except OSError:
        pass


CALLS = load_calls()


def new_reference(prefix="BR"):
    """Short, human-friendly booking reference, e.g. BR-7F3K9Q."""
    return f"{prefix}-{secrets.token_hex(3).upper()}"


def add_log_entry(entry):
    CALLS.insert(0, entry)  # newest first
    save_calls(CALLS)


# ---------------------------------------------------------------------------
# Aria — rule-based demo agent
# ---------------------------------------------------------------------------

SERVICE_LIST = (
    "Check-up & Cleaning — $89, Filling — $120, Root Canal — $450, "
    "Teeth Whitening — $199, Tooth Extraction — $150, "
    "Braces Consultation — free"
)


DISPLAY_NAMES = {
    "check-up & cleaning": "Check-up & Cleaning",
    "checkup": "Check-up & Cleaning",
    "cleaning": "Check-up & Cleaning",
    "filling": "Filling",
    "root canal": "Root Canal",
    "whitening": "Teeth Whitening",
    "tooth extraction": "Tooth Extraction",
    "braces consultation": "Braces Consultation",
    "emergency": "Emergency Visit",
}


def _find_price(message):
    """Return (display name, price) if the message mentions a known service."""
    for service, price in SERVICES.items():
        if service in message:
            return DISPLAY_NAMES[service], price
    return None, None


def aria_reply(message):
    """Rule-based reply.  Keyword matching only — no AI model involved."""
    text = (message or "").strip().lower()

    if not text:
        return "Hi! I'm Aria, the receptionist at BrightSmile Dental. How can I help you today?"

    # Greetings
    if re.search(r"\b(hi|hello|hey|good (morning|afternoon|evening)|salam)\b", text):
        return (
            "Hello! This is Aria, BrightSmile Dental's AI receptionist. "
            "I can tell you about our services and prices, check opening hours, "
            "or book an appointment for you. What would you like to do?"
        )

    # Price questions
    if any(word in text for word in ("price", "cost", "how much", "fee", "charges")):
        service, price = _find_price(text)
        if service:
            if price == 0:
                return (
                    f"The {service} is free of charge. "
                    "Would you like me to book it for you?"
                )
            return (
                f"The {service} costs ${price}. "
                "Would you like me to book an appointment?"
            )
        return (
            "Here are our prices: " + SERVICE_LIST + ". "
            "Which service were you asking about?"
        )

    # Services
    if any(word in text for word in ("service", "treatment", "what do you offer", "do you do")):
        return "We offer: " + SERVICE_LIST + ". Which one do you need?"

    # Opening hours
    if any(word in text for word in ("open", "hours", "timing", "when are you", "closed")):
        return (
            f"We're open {CLINIC['hours']}. "
            "Would you like to book a slot while we're open?"
        )

    # Location / contact
    if any(word in text for word in ("where", "location", "address", "phone", "contact")):
        return (
            f"We're at {CLINIC['address']}. "
            f"You can also reach the clinic at {CLINIC['phone']}."
        )

    # Booking intent
    if any(word in text for word in ("book", "appointment", "schedule", "reserve")):
        return (
            "I'd be happy to book you in! Please use the booking form on this "
            "page (your name, phone, service, date and time) and I'll confirm "
            "it right away with a reference number. Or tell me the service and "
            "day and I'll walk you through it here."
        )

    # Emergency
    if any(word in text for word in ("emergency", "pain", "hurts", "bleeding", "broken tooth")):
        return (
            "I'm sorry to hear that. For a dental emergency, please come to the "
            f"clinic as soon as you can — we're at {CLINIC['address']} — or call "
            f"{CLINIC['phone']}. If it's outside our hours, the emergency line "
            "in the booking form notes will help. Would you like me to book the "
            "earliest available slot?"
        )

    # Cancel / reschedule
    if any(word in text for word in ("cancel", "reschedule", "change my appointment", "move my")):
        return (
            "No problem — I can reschedule or cancel an appointment. "
            "Please share your booking reference number (it starts with BR-) "
            "and the new day/time you'd prefer."
        )

    # Thanks / goodbye
    if any(word in text for word in ("thank", "thanks", "bye", "goodbye")):
        return (
            "You're welcome! Anything else I can help with — booking, prices, "
            "or opening hours?"
        )

    # Fallback — never pretend to know something it doesn't
    return (
        "I can help with services and prices, opening hours, and booking an "
        "appointment. Could you tell me a little more about what you need? "
        "For example: 'How much is whitening?' or 'Book a cleaning on Friday'."
    )


# ---------------------------------------------------------------------------
# Scripted call scenarios (simulated incoming calls)
# ---------------------------------------------------------------------------

CALL_SCRIPTS = {
    "booking": [
        ("Caller", "Hi, I'd like to book a check-up and cleaning, please."),
        ("Aria", "Of course! We have Friday 27 November at 10:45 AM or Monday at 2:15 PM. Which works better for you?"),
        ("Caller", "Friday at 10:45 works for me."),
        ("Aria", "Perfect. Could I take your name and phone number to confirm the booking?"),
        ("Caller", "Sarah Miller, 555-013-4471."),
        ("Aria", "Thank you, Sarah. You're booked for a Check-up & Cleaning on Friday 27 November at 10:45 AM. Your reference is BR-7F3K9Q. We've also sent a confirmation by text. Is there anything else I can help with?"),
        ("Caller", "No, that's all. Thank you!"),
        ("Aria", "You're welcome — see you on Friday!"),
    ],
    "reschedule": [
        ("Caller", "Hi, I need to move my appointment to next week."),
        ("Aria", "No problem at all. Could you share your booking reference number so I can find it?"),
        ("Caller", "It's BR-7F3K9Q."),
        ("Aria", "Found it — Check-up & Cleaning, Friday 27 November at 10:45 AM. What day and time would you like instead?"),
        ("Caller", "Monday at 2:15 PM, please."),
        ("Aria", "Done — your appointment is now Monday at 2:15 PM, same reference BR-7F3K9Q. A confirmation has been sent to your phone."),
        ("Caller", "Great, thanks!"),
        ("Aria", "Anytime! See you on Monday."),
    ],
    "pricing": [
        ("Caller", "Hi, how much is teeth whitening?"),
        ("Aria", "Teeth whitening is $199, and it takes about an hour. A check-up & cleaning is $89 if you'd like both together."),
        ("Caller", "And what are your opening hours?"),
        ("Aria", "We're open Monday to Friday 9 AM to 6 PM, and Saturday 10 AM to 3 PM. Sundays we're closed."),
        ("Caller", "Okay, I'll think about it. Thanks!"),
        ("Aria", "You're welcome! If you'd like to book, I'm here 24/7."),
    ],
    "emergency": [
        ("Caller", "Hello? I broke a tooth, it really hurts."),
        ("Aria", "I'm sorry to hear that. Don't worry — please come to the clinic as soon as you can, we're at 12 Market Street. We keep emergency slots every day."),
        ("Caller", "I'm on my way now, about 20 minutes."),
        ("Aria", "I've noted an emergency arrival for you in 20 minutes and alerted the dentist. If the pain gets worse, please call 555-014-8890 and press 1. See you soon."),
        ("Caller", "Thank you so much."),
        ("Aria", "Take care — we'll look after you when you arrive."),
    ],
}


def simulate_call(scenario):
    """Return the scripted transcript for a scenario, or None if unknown."""
    script = CALL_SCRIPTS.get(scenario)
    if script is None:
        return None
    return [{"speaker": speaker, "text": line} for speaker, line in script]


# ---------------------------------------------------------------------------
# HTTP layer
# ---------------------------------------------------------------------------


class AriaHandler(SimpleHTTPRequestHandler):
    """Serves ./public and the /api/* JSON endpoints."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    # -- helpers ----------------------------------------------------------

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = 0
        if length <= 0:
            return {}
        try:
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError, UnicodeDecodeError):
            return {}

    # -- routing ----------------------------------------------------------

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/calls":
            self._send_json(200, {"calls": CALLS})
            return
        if path == "/api/health":
            self._send_json(200, {"status": "ok", "calls": len(CALLS)})
            return
        # Everything else: static files from ./public
        if path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        data = self._read_json()

        if path == "/api/chat":
            reply = aria_reply(data.get("message", ""))
            self._send_json(200, {"reply": reply, "agent": "Aria (rule-based demo)"})
            return

        if path == "/api/book":
            errors = self._validate_booking(data)
            if errors:
                self._send_json(400, {"error": "Invalid booking", "details": errors})
                return
            ref = new_reference()
            entry = {
                "id": ref,
                "type": "booking",
                "scenario": "booking",
                "caller": data["name"].strip(),
                "summary": (
                    f"Booked {data['service']} for {data['date']} at {data['time']}."
                ),
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "demo": True,
                "details": {
                    "name": data["name"].strip(),
                    "phone": data["phone"].strip(),
                    "service": data["service"],
                    "date": data["date"],
                    "time": data["time"],
                },
            }
            add_log_entry(entry)
            self._send_json(200, {
                "reference": ref,
                "message": (
                    f"Booked! {data['service']} on {data['date']} at {data['time']}. "
                    f"Your reference is {ref}."
                ),
            })
            return

        if path == "/api/call":
            scenario = (data.get("scenario") or "").strip().lower()
            transcript = simulate_call(scenario)
            if transcript is None:
                self._send_json(400, {
                    "error": "Unknown scenario",
                    "valid": sorted(CALL_SCRIPTS),
                })
                return
            entry = {
                "id": new_reference("CL"),
                "type": "call",
                "scenario": scenario,
                "caller": "Demo caller",
                "summary": f"Simulated {scenario} call handled by Aria.",
                "time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "demo": True,
            }
            add_log_entry(entry)
            self._send_json(200, {
                "scenario": scenario,
                "transcript": transcript,
                "log_id": entry["id"],
            })
            return

        self._send_json(404, {"error": "Unknown endpoint"})

    # -- validation --------------------------------------------------------

    @staticmethod
    def _validate_booking(data):
        errors = []
        name = (data.get("name") or "").strip()
        phone = (data.get("phone") or "").strip()
        service = data.get("service") or ""
        date = data.get("date") or ""
        time = data.get("time") or ""

        if len(name) < 2:
            errors.append("name is required (at least 2 characters)")
        if len(re.sub(r"[^\d]", "", phone)) < 7:
            errors.append("phone is required (at least 7 digits)")
        if service not in SERVICES and service not in (
            "Check-up & Cleaning", "Filling", "Root Canal",
            "Teeth Whitening", "Tooth Extraction", "Braces Consultation",
        ):
            errors.append("please choose a valid service")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
            errors.append("date must be YYYY-MM-DD")
        if not re.fullmatch(r"\d{2}:\d{2}", time):
            errors.append("time must be HH:MM")
        return errors

    # Quieter logs: one line per request is enough.
    def log_message(self, format, *args):  # noqa: A002 - stdlib name
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {self.address_string()} "
              f"{format % args}")


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), AriaHandler)
    print("=" * 60)
    print("  Aria — AI Voice Receptionist (Full System)")
    print("  Demo only: rule-based agent, sample data, no real AI calls.")
    print(f"  Open http://localhost:{PORT} in your browser.")
    print("  Press Ctrl+C to stop.")
    print("=" * 60)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Aria. Goodbye!")
        server.shutdown()


if __name__ == "__main__":
    main()
