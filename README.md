# Mentor Connect

**Full-Stack AI Mentorship Platform**

An AI-powered mentorship platform that connects students with the right industry mentor. Instead of browsing a static directory, students describe their career challenge to a diagnostic AI, get matched to verified mentors with explainable fit scores, book a session via Google Calendar, and receive an evidence-linked post-call report that turns one conversation into trackable progress.

> **Live Demo**: [mentor-connect-mesa.vercel.app](https://mentor-connect-mesa.vercel.app) | **API**: [mentor-connect-api.onrender.com/docs](https://mentor-connect-api.onrender.com/docs) | **Repo**: [github.com/DivyaMusahib/mentor-connect-mesa](https://github.com/DivyaMusahib/mentor-connect-mesa)

---

## Tech Stack

| Layer | Stack |
|---|---|
| **Backend** | FastAPI (Python 3.12), Pydantic v2, SQLAlchemy 2.0, Alembic, SQLite / PostgreSQL |
| **Frontend** | React 18 + JavaScript (Vite, Tailwind CSS, Lucide React) |
| **Auth** | Google OAuth 2.0 verified natively in FastAPI with HttpOnly cookie sessions |
| **Automation** | n8n Cloud — 10 importable workflows for Calendar, Meet, Gmail, rescheduling, and error handling |
| **AI** | Google Gemini 2.5 Flash via `google-genai` SDK with Pydantic structured output schemas |

---

## Architecture

```
React Frontend
       │
       ▼  (HttpOnly Cookie / REST API)
FastAPI Backend
  ├── Google OAuth 2.0 & Session Management
  ├── 50-Mentor Catalogue (CSV-seeded, DB-verified)
  ├── AI Career Diagnostic (Gemini + heuristic fallback)
  ├── Explainable Mentor Matching
  ├── Pre-Call Brief Generation & Persistence
  ├── Post-Call Transcript Ingestion & Evidence-Linked Reports
  ├── Action Items, Career Roadmap & Progress Tracking
  ├── Admin Analytics & Recruitment Gap Logging
  └── Signed Outbound Webhooks (X-N8N-Key)
              │
              ▼
        n8n Cloud
          ├── Google Calendar (availability & event creation)
          ├── Google Meet (conference link generation)
          ├── Gmail (confirmations, reminders, follow-ups)
          ├── Rescheduling & Cancellation
          └── Global Error Handler & Retry
```

### Why full-context matching instead of a vector DB

For a 50-mentor catalogue (~14 KB), a vector database adds chunking loss, embedding drift, deployment overhead, and cost — with no real benefit. Passing the full normalized catalogue to Gemini in a single structured call gives it complete cross-attribute reasoning. A deterministic keyword-overlap heuristic takes over silently if the Gemini API key is absent or rate-limited, so the platform never breaks.

---

## Quick Start

### Prerequisites
- Python 3.12+
- Node.js v18+ & npm
- Git

### 1. Clone & set up backend
```bash
git clone https://github.com/DivyaMusahib/mentor-connect-mesa.git
cd mentor-connect-mesa

python -m venv backend/.venv
# Windows:
.\backend\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source backend/.venv/bin/activate

pip install -r backend/requirements.txt
cp backend/.env.example backend/.env

cd backend && alembic upgrade head && cd ..
```

### 2. Set up frontend
```bash
cd frontend && npm install && cd ..
```

### 3. Run
```powershell
.\scripts\run_dev.ps1
```
Or separately:
- `cd backend && uvicorn app.main:app --reload --port 8000`
- `cd frontend && npm run dev`

Open **http://localhost:5173**.

---

## Demo Mode (No API Keys Needed)

The full platform can be explored without Google OAuth or third-party credentials:

1. On `/login`, click **Demo Student** or **Demo Admin** — a persistent demo bar appears.
2. Click **Seed Sample Sessions** to populate an upcoming booking with a pre-call brief, a completed session with an AI report, action items, and analytics data.
3. Walk through the student flow:
   - **`/advisor`** — describe a career problem, get AI-matched mentor recommendations with fit explanations
   - **`/preparation`** — review the auto-generated pre-call brief and discussion questions
   - **`/sessions`** → **Simulate Completion** — runs real AI report generation on synthetic transcript
   - **`/report`** — evidence-linked insights, verbatim quotes, and checkable action items
   - **`/roadmap`**, **`/progress`** — action items sync here automatically
4. Switch to **Admin** via the banner to see platform metrics, mentor demand data, unmatched gap logs, and automation audit events.

---

## Tests

```bash
cd backend
.\.venv\Scripts\pytest -v
```

```
======================== 25 passed, 1 warning in 7.92s ========================
```

---

## n8n Workflows

10 importable JSON files in `automation/n8n/workflows/`:

| # | File | Purpose |
|---|---|---|
| 01 | `01_calendar_availability.json` | Query host Google Calendar for open slots |
| 02 | `02_create_meeting.json` | Create Calendar event with Google Meet link |
| 03 | `03_booking_confirmation_emails.json` | Student confirmation email via Gmail |
| 04 | `04_pre_meeting_reminders.json` | 24h & 30-minute reminder poller |
| 05 | `05_reschedule_meeting.json` | Modify Calendar event times |
| 06 | `06_cancel_meeting.json` | Delete Calendar event on cancellation |
| 07 | `07_transcription_coordination.json` | Notetaker bot dispatch |
| 08 | `08_transcript_completed.json` | Forward transcript webhook to AI pipeline |
| 09 | `09_post_call_followup.json` | Summary email with action items |
| 10 | `10_automation_error_handler.json` | Global error trigger → admin log |

See [automation/n8n/README.md](automation/n8n/README.md) for setup.

---

## Documentation

| Doc | Description |
|---|---|
| [Architecture](docs/architecture.md) | System diagram, integration boundaries, resiliency patterns |
| [Integrations](docs/integrations.md) | n8n setup, OAuth flow, transcription provider comparison |
| [Threat Model](docs/threat-model.md) | OAuth CSRF, session security, prompt injection, webhook spoofing |
| [Deployment](docs/deployment.md) | Vercel + Render + Neon + n8n Cloud step-by-step |

---

## License

MIT
