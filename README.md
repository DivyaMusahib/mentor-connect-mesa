# Mentor Connect — Full-Stack AI Mentorship Platform
### Mesa School of Business · Technical Associate Assignment

**Full-Stack AI Engineering · n8n Workflow Automation · Google OAuth · Gemini Structured Outputs**

> **Live Demo**: [mentor-connect-mesa.vercel.app](https://mentor-connect-mesa.vercel.app) | **API Docs**: [mentor-connect-api.onrender.com/docs](https://mentor-connect-api.onrender.com/docs) | **Repository**: [github.com/DivyaMusahib/mentor-connect-mesa](https://github.com/DivyaMusahib/mentor-connect-mesa)

---

## 1. Executive Summary

**Mentor Connect** is an AI-powered career mentorship platform built for Mesa School of Business. It replaces passive directory browsing with an **AI Career Diagnostic Advisor** that diagnoses each student's specific challenge, matches them against a verified catalogue of **50 anonymised industry mentors**, and orchestrates the full lifecycle — from calendar scheduling and pre-call preparation through to evidence-linked post-call insights and action-item tracking.

### Key Architectural Highlights

| Layer | Stack |
|---|---|
| **Backend** | FastAPI (Python 3.12), Pydantic v2, SQLAlchemy 2.0, Alembic migrations. SQLite locally, PostgreSQL in production. |
| **Frontend** | React 18 + JavaScript (Vite, Tailwind CSS, Lucide React). No TypeScript. |
| **Authentication** | Native Google OAuth 2.0 verified in FastAPI with HttpOnly cookie sessions + 1-click evaluator demo login. |
| **Automation** | 10 importable n8n Cloud workflows — Google Calendar, Google Meet, Gmail, rescheduling, cancellation, error handling. |
| **AI Engine** | Google Gemini 2.5 Flash via `google-genai` SDK with Pydantic structured output schemas and heuristic fallback. |

---

## 2. Architecture & Boundary Separation

```
React (JavaScript Frontend)
       │
       ▼ (HttpOnly Session Cookie / JSON API)
FastAPI Backend
  ├── Google OAuth 2.0 & Session Management
  ├── Authoritative 50-Mentor Catalogue (mentors_50.csv)
  ├── AI Career Diagnostic Assistant (Gemini / Heuristic Fallback)
  ├── Verified & Explainable Mentor Matching
  ├── Pre-Call Brief Generation & Persistence
  ├── Post-Call Transcript Ingestion & Evidence-Linked Reports
  ├── Career Progress Memory, Roadmaps & Action Item Tracking
  ├── Mesa Admin Metrics Aggregations & Recruitment Supply Gaps
  └── Authenticated Outbound Webhooks (X-N8N-Key)
              │
              ▼
        n8n Cloud Engine
          ├── Google Calendar (availability queries & event creation)
          ├── Google Meet (native conference link generation)
          ├── Gmail (confirmation, reminder, and follow-up emails)
          ├── Rescheduling & Cancellation Workflows
          └── Global Error Boundary & Automated Recovery
```

### Why Full-Context Matching for 50 Mentors Beats a Vector DB

For 50 mentors (~14 KB total payload), a vector database introduces chunking loss, embedding drift, latency, and unnecessary infrastructure complexity:

1. **Zero Information Loss**: Full-context passing gives Gemini the entire normalized dataset — domain, sector, role, seniority, and AI tools — simultaneously.
2. **Instant Consistency**: When mentor data updates, no re-indexing or embedding drift occurs.
3. **Strict Validation**: Every recommendation is cross-checked against database primary keys; hallucinated IDs and unverified fields are discarded before reaching the student.

---

## 3. Quick Start (Run Locally in 2 Minutes)

### Prerequisites
- Python 3.12+
- Node.js v18+ & npm
- Git

### 1. Clone & Set Up Backend
```bash
git clone https://github.com/DivyaMusahib/mentor-connect-mesa.git
cd mentor-connect-mesa

# Create & activate Python virtual environment
python -m venv backend/.venv

# Windows PowerShell:
.\backend\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source backend/.venv/bin/activate

pip install -r backend/requirements.txt
cp backend/.env.example backend/.env

cd backend
alembic upgrade head
cd ..
```

### 2. Set Up Frontend
```bash
cd frontend
npm install
cd ..
```

### 3. Launch the Application
Use the single PowerShell launcher:
```powershell
.\scripts\run_dev.ps1
```
Or start each service separately:
- **Backend**: `cd backend && uvicorn app.main:app --reload --port 8000`
- **Frontend**: `cd frontend && npm run dev`

Open **http://localhost:5173** in your browser.

---

## 4. Evaluator Demo Mode (No API Keys Required)

The entire platform can be explored without Google OAuth or third-party API keys:

1. **1-Click Demo Login**: On `/login`, click **Mesa Student (Arjun Bansal)** or **Mesa Admin**. A persistent Evaluator Demo Bar appears.

2. **Seed Sample Data**: Click the green **Seed Sample Sessions** button. This creates an upcoming meeting with a pre-call brief, a completed meeting with an AI report, active action items, and supply gap records.

3. **Test the Full Student Journey**:
   - **AI Advisor (`/advisor`)**: Type a career problem (e.g., *"I want to break into AI automation and product management but my projects look like tutorial clones."*)
   - The AI diagnoses the challenge, asks clarifying questions, and recommends verified mentors with transparent fit scores.
   - Click **Book Session** on a recommended mentor and select a time slot.
   - **Preparation Brief (`/preparation`)**: Review personalized discussion questions, agenda, and interactive prep checklist.
   - **Simulate Completion**: In **My Sessions (`/sessions`)**, click **Simulate Completion** to feed realistic dialogue into the real AI pipeline.
   - **AI Report (`/report`)**: Inspect evidence-linked insights, expand verbatim quotes with timestamps, and check off action items.
   - **Roadmap & Progress (`/roadmap`, `/progress`)**: Watch completed tasks synchronize in real-time.

4. **Mesa Admin (`/admin`)**: Switch via the evaluator banner to review platform metrics, mentor demand breakdown, unmatched supply gaps, email outbox logs, and automation retry tools.

---

## 5. Automated Test Suite

Mentor Connect includes 25 automated tests covering authentication, mentor data integrity, diagnostic matching, double-booking prevention, rescheduling, transcripts, and admin controls.

```bash
cd backend
.\.venv\Scripts\pytest -v
```

```
======================== 25 passed, 1 warning in 7.92s ========================
```

---

## 6. n8n Cloud Automation Workflows

All 10 workflows are importable JSON files in `automation/n8n/workflows/`:

| # | File | Purpose |
|---|---|---|
| 01 | `01_calendar_availability.json` | Queries host Google Calendar for open slots |
| 02 | `02_create_meeting.json` | Creates Calendar event with Google Meet link |
| 03 | `03_booking_confirmation_emails.json` | Sends student confirmation via Gmail |
| 04 | `04_pre_meeting_reminders.json` | 15-minute poller for 24h & 30m reminders |
| 05 | `05_reschedule_meeting.json` | Modifies Calendar event start/end times |
| 06 | `06_cancel_meeting.json` | Deletes Calendar event on cancellation |
| 07 | `07_transcription_coordination.json` | Notetaker bot dispatch coordinator |
| 08 | `08_transcript_completed.json` | Forwards transcript webhook to AI pipeline |
| 09 | `09_post_call_followup.json` | Dispatches summary email with action items |
| 10 | `10_automation_error_handler.json` | Global error trigger logging to Mesa Admin |

See [automation/n8n/README.md](automation/n8n/README.md) for full n8n Cloud setup instructions.

---

## 7. Documentation

| Document | Description |
|---|---|
| [Architecture & System Design](docs/architecture.md) | System diagram, integration boundaries, and resiliency patterns |
| [Integrations & Automation Guide](docs/integrations.md) | n8n setup, Google OAuth flow, and transcription provider comparison |
| [One-Page Product Design Rationale](docs/product-design-note.md) | Core problem, UX decisions, and design principles |
| [Security Architecture & Threat Model](docs/threat-model.md) | OAuth CSRF, session security, prompt injection, and webhook spoofing mitigations |
| [Production Deployment Guide](docs/deployment.md) | Step-by-step Vercel + Render + Neon + n8n Cloud setup |

---

## 8. License

Built for the Mesa School of Business Technical Associate Assignment.
