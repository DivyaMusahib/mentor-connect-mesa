# Mentor Connect — Architecture & System Design

## 1. System Overview & Integration Boundaries

Mentor Connect enforces a strict separation of concerns between core application authority, AI reasoning, and workflow automation.

```mermaid
graph TD
    User["Student / Evaluator (Browser)"]
    Frontend["React + JavaScript Frontend (Vite, Tailwind, Lucide)"]
    Backend["FastAPI Backend (Python 3.12, Pydantic v2, SQLAlchemy 2.0)"]
    DB[("PostgreSQL / SQLite Database")]
    Gemini["Google Gemini 2.5 Flash (google-genai SDK)"]
    N8N["n8n Cloud Automation Engine"]
    GoogleCal["Google Calendar & Meet"]
    Gmail["Gmail Notifications"]
    Transcription["Transcription Adapter (Recall.ai / Simulation)"]

    User -->|HttpOnly Cookie / JSON| Frontend
    Frontend -->|REST API v1| Backend
    Backend -->|SQLAlchemy ORM| DB
    Backend -->|Structured JSON Schemas| Gemini
    Backend -->|Signed Webhook (X-N8N-Key)| N8N
    N8N -->|OAuth2 Native Nodes| GoogleCal
    N8N -->|OAuth2 Native Nodes| Gmail
    N8N -->|Signed Callback (X-FastAPI-Key)| Backend
    Transcription -->|Signed Webhook| Backend
```

### Architectural Separation
1. **FastAPI owns Identity, Business Logic & Persistence**:
   - Google OAuth initiation, state generation, cryptographic identity-token verification (`google-auth`).
   - Server-side opaque session lifecycle in `application_sessions` table with HttpOnly cookies.
   - Authoritative mentor catalogue, booking eligibility enforcement, double-booking prevention.
   - Pre-call brief and post-call report schemas, evidence links, and action item task states.
2. **Gemini owns Contextual Reasoning**:
   - Diagnostic conversation analysis.
   - Grounded explainable matching against the verified 50-mentor catalogue.
   - Pre-call brief generation (exactly 3 discussion questions, agenda, checklist).
   - Post-call report synthesis with evidence citations.
3. **n8n Cloud owns Google Workspace & External Orchestration**:
   - Native Google Calendar query for busy periods.
   - Google Calendar event creation with Hangouts/Meet conference links.
   - Gmail notifications and reminders (24h and 30m before call).
   - Rescheduling and calendar cancellation.
   - Error handler boundaries with execution tracking.
4. **React (JavaScript) owns Presentation**:
   - Intuitive, high-clarity interface tailored to Mesa School of Business.
   - Evaluator demo controls and transparent explainability views.

---

## 2. Why Full-Context Matching Over a Vector Database

For a catalogue of 50 mentors, **full-context structured matching in Gemini is strictly superior to a vector database**:

1. **Zero Information Loss from Chunking**:
   - In vector search, chunking fragments cross-attribute qualifications (e.g., "Marketing domain practitioner who also built n8n workflows in Edtech").
   - With full-context matching, Gemini inspects the entire normalized record (domain, master sector, sector expertise, role expertise, seniority, and verified AI tools) simultaneously.
2. **Elimination of Embedding Latency & Infrastructure Cost**:
   - A vector DB (Pinecone, Weaviate, pgvector) adds deployment friction, cold starts, index synchronization overhead, and cost without providing utility for 50 records (~14 KB total payload).
3. **Zero Semantic Drift or Outdated Embeddings**:
   - When a mentor's profile or availability changes, no re-indexing or re-embedding is required. Gemini evaluates the live database catalogue directly.
4. **Deterministic Heuristic Fallback**:
   - If external AI credentials are unconfigured or rate-limited, our keyword/domain overlap scoring engine executes deterministically, maintaining 100% platform availability.

---

## 3. Resiliency, Idempotency & Fault Tolerance

- **Idempotency Keys**: All meeting creation, rescheduling, and cancellation requests require a unique client `idempotency_key`. Duplicate webhook requests return existing records without re-triggering n8n or creating duplicate calendar events.
- **Circuit-Breaking Fallback**: If n8n Cloud is unreachable or execution quota expires, the backend transitions the automation event into `simulated` mode, logs the failure in `automation_events`, and provides a 1-click admin retry endpoint.
- **Dual Engine Compatibility**: Seamlessly runs on local SQLite out-of-the-box for evaluators, and PostgreSQL for production deployments. Datetimes are strictly normalized through `ensure_utc()` to guarantee zero timezone or offset-naive comparison bugs.
