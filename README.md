# Mentor Connect — Full-Stack AI Mentorship Platform
### Mesa School of Business Technical Associate Assignment
**Full-Stack AI Engineering • n8n Workflow Automation • Google OAuth • Gemini Structured Outputs**

---

## 1. Executive Summary

**Mentor Connect** is an executive career mentorship SaaS platform engineered for the **Mesa School of Business**. It replaces static directory browsing with an interactive **AI Career Diagnostic Advisor** that diagnoses student challenges, matches them against an authoritative catalogue of **50 verified anonymised industry mentors**, orchestrates Google Calendar and Google Meet scheduling via **n8n Cloud**, synthesizes personalized **Pre-Call Preparation Briefs**, and translates meeting transcripts into **Evidence-Linked Insights** and persistent **Action Items**.

### Key Architectural Highlights
- **Backend**: FastAPI (Python 3.12), Pydantic v2, SQLAlchemy 2.0, Alembic migrations. Dual-engine compatibility: SQLite for zero-friction local development + PostgreSQL for production.
- **Frontend**: Pure JavaScript + React (Vite, Tailwind CSS, Lucide React, Framer Motion). **Zero TypeScript** across the frontend as requested.
- **Authentication**: Native Google OAuth 2.0 and identity-token verification directly in FastAPI with cryptographically secure state parameters and server-side HttpOnly cookie sessions. 1-click Evaluator Demo login for instant review.
- **Automation**: 10 importable workflows built for **n8n Cloud** (Google Calendar events, Google Meet links, Gmail confirmations, reminders, rescheduling, cancellation, and error handling).
- **AI Engine**: Google Gemini (`google-genai` SDK) utilizing Pydantic structured outputs for diagnostic assessment, explainable matching, pre-call briefs, and post-call reports.

---

## 2. Architecture & Boundary Separation

```
React (JavaScript Frontend)
       │
       ▼ (HttpOnly Session Cookie / JSON API)
FastAPI Backend
  ├── Google OAuth 2.0 & Session Management
  ├── Authoritative 50-Mentor Catalogue (mentors_50.csv)
  ├── AI Career Diagnostic Assistant (Gemini / Heuristic Engine)
  ├── Verified & Explainable Mentor Matching
  ├── Pre-Call Brief Generation & Authoritative Persistence
  ├── Post-Call Transcript Ingestion & Evidence-Linked Reports
  ├── Career Progress Memory, Roadmaps, & Action Item Tracking
  ├── Mesa Admin Metrics Aggregations & Recruitment Supply Gaps
  └── Authenticated Outbound Webhooks (X-N8N-Key)
              │
              ▼
        n8n Cloud Engine
          ├── Google Calendar (Host-calendar availability & event creation)
          ├── Google Meet (Native conference link generation)
          ├── Gmail (Confirmation, reminder, and follow-up emails)
          ├── Rescheduling & Cancellation Workflows
          └── Global Error Boundary & Automated Recovery
```

### Why Full-Context Matching for 50 Mentors Beats a Vector DB
For 50 mentors (~14 KB total payload), adding a vector database (RAG) is architectural over-engineering:
1. **Zero Information Loss**: Chunking splits cross-domain practitioner credentials. Full-context passing gives Gemini the entire normalized dataset (domain, sector, role, seniority, AI tools) at once.
2. **Instant Consistency**: When mentor data updates, no vector re-indexing or embedding drift occurs.
3. **Strict Validation**: Every model recommendation is cross-checked against database primary keys; hallucinated IDs and unverified fields are discarded before reaching the student.

---

## 3. Quick Start (Run Locally in 2 Minutes)

### Prerequisites
- Python 3.12+
- Node.js v18+ & npm
- Git

### 1. Clone & Set Up Backend
```bash
# Clone the repository
git clone https://github.com/your-username/mentor-connect.git
cd mentor-connect

# Create Python virtual environment
python -m venv backend/.venv

# Activate virtual environment
# Windows PowerShell:
.\backend\.venv\Scripts\Activate.ps1
# macOS/Linux:
# source backend/.venv/bin/activate

# Install backend dependencies
pip install -r backend/requirements.txt

# Copy environment variables
cp backend/.env.example backend/.env

# Run database migrations (creates SQLite tables automatically)
cd backend
alembic upgrade head
cd ..
```

### 2. Set Up Frontend
```bash
cd frontend
npm install
npm run build   # Verifies zero-error production build
cd ..
```

### 3. Launch the Application
You can use our single PowerShell launcher:
```powershell
.\scripts\run_dev.ps1
```
Or start each service in separate terminals:
- **Backend**: `cd backend && uvicorn app.main:app --reload --port 8000`
- **Frontend**: `cd frontend && npm run dev`

Open **http://localhost:5173** in your browser.

---

## 4. Evaluator Demo Mode (3-Minute Reviewer Guide)

Reviewers can explore the entire journey without needing Google OAuth or paid third-party API keys:

1. **1-Click Demo Login**:
   - On the login page (`/login`), click **Mesa Student (Arjun Bansal)** or **Mesa Admin**.
   - A persistent **Evaluator Demo Bar** appears at the top of the screen.
2. **Seed Sample Data**:
   - Click the green **Seed Sample Sessions** button in the evaluator banner.
   - This seeds an upcoming meeting with a pre-call brief, a completed meeting with an evidence-linked AI report, active action items, and supply gaps.
3. **Test the Core Student Journey**:
   - **AI Advisor (`/advisor`)**: Type a problem (e.g., *"I want to break into AI automation and product management, but I don't know if my projects are production-grade."*).
   - Watch the AI diagnose the challenge, clarify details, and recommend verified mentors with transparent fit scores.
   - Click **Book Session** on Mentor 042. Select a slot to confirm.
   - **Preparation Brief (`/preparation`)**: Review the personalized 3 discussion questions, 45-minute agenda, and interactive prep checklist.
   - **Simulate Meeting Completion**: In **My Sessions (`/sessions`)**, click **Simulate Completion**. The app immediately feeds realistic dialogue into the real AI pipeline.
   - **AI Report (`/report`)**: Inspect the evidence-linked insights, click to expand verbatim quotes with timestamps, and check off action items.
   - **Roadmap & Progress Tracker (`/roadmap` & `/progress`)**: Watch completed tasks synchronize in real-time.
4. **Inspect Mesa Admin (`/admin`)**:
   - Click **Switch to Admin** in the evaluator banner.
   - Review live platform metrics, mentor demand breakdown, logged recruitment supply gaps, email outbox logs, and automation retry tools.

---

## 5. Automated Test Suite

Mentor Connect includes 25 comprehensive automated tests covering authentication, mentor data integrity, diagnostic matching, double-booking prevention, rescheduling, transcripts, and admin controls.

```bash
cd backend
.\.venv\Scripts\pytest -v
```

**Results**:
```
======================== 25 passed, 1 warning in 7.92s ========================
100% test pass rate across all modules.
```

---

## 6. n8n Cloud Automation Workflows

All 10 workflows are stored as real, importable JSON files in `automation/n8n/workflows/`:

1. `01_calendar_availability.json`: Queries host Google Calendar for open slots.
2. `02_create_meeting.json`: Creates Google Calendar event with real Google Meet link.
3. `03_booking_confirmation_emails.json`: Sends student confirmation via Gmail node.
4. `04_pre_meeting_reminders.json`: Scheduled 15-minute poller checking 24h & 30m reminders.
5. `05_reschedule_meeting.json`: Modifies calendar event start/end times.
6. `06_cancel_meeting.json`: Deletes calendar event upon booking cancellation.
7. `07_transcription_coordination.json`: Notetaker bot dispatch coordinator (Recall.ai).
8. `08_transcript_completed.json`: Forwards transcript webhook to FastAPI AI pipeline.
9. `09_post_call_followup.json`: Dispatches summary email with action items.
10. `10_automation_error_handler.json`: Global error trigger logging failures back to Mesa Admin.

See [automation/n8n/README.md](file:///e:/mentor-connect-assignment/mentor-connect-second/automation/n8n/README.md) for full n8n Cloud setup instructions.

---

## 7. Documentation Index

- [Architecture & System Design](file:///e:/mentor-connect-assignment/mentor-connect-second/docs/architecture.md)
- [Integrations & Automation Guide](file:///e:/mentor-connect-assignment/mentor-connect-second/docs/integrations.md)
- [One-Page Product Design Rationale](file:///e:/mentor-connect-assignment/mentor-connect-second/docs/product-design-note.md)
- [Security Architecture & Threat Model](file:///e:/mentor-connect-assignment/mentor-connect-second/docs/threat-model.md)
- [Production Deployment Guide](file:///e:/mentor-connect-assignment/mentor-connect-second/docs/deployment.md)
- [3-to-5-Minute Video Walkthrough Script](file:///e:/mentor-connect-assignment/mentor-connect-second/docs/walkthrough-script.md)
- [Technical Interview Defense Notes](file:///e:/mentor-connect-assignment/mentor-connect-second/docs/interview-prep.md)

---

## 8. License

Built for the Mesa School of Business Technical Associate Assignment.
