# Mentor Connect — Integrations & Automation Guide

## 1. n8n Cloud Automation Integration

All Google Calendar, Google Meet, and Gmail notifications are orchestrated through **n8n Cloud**.

### Workflow Inventory
1. `01_calendar_availability.json`: Queries host calendar busy periods and returns normalized slots.
2. `02_create_meeting.json`: Creates Google Calendar event with real Google Meet link.
3. `03_booking_confirmation_emails.json`: Sends student confirmation email via Gmail node.
4. `04_pre_meeting_reminders.json`: Scheduled 15-minute poller checking 24h & 30m reminders.
5. `05_reschedule_meeting.json`: Modifies calendar event start/end times.
6. `06_cancel_meeting.json`: Deletes calendar event upon booking cancellation.
7. `07_transcription_coordination.json`: Notetaker bot dispatch coordinator.
8. `08_transcript_completed.json`: Forwards transcript webhook to FastAPI AI pipeline.
9. `09_post_call_followup.json`: Dispatches summary email with action items.
10. `10_automation_error_handler.json`: Global error trigger logging failures back to Mesa Admin.

### Cloud Free-Trial Setup
1. Create a free trial account on [n8n.io](https://n8n.io).
2. Under **Credentials**, connect:
   - `Google Calendar OAuth2 API` (named `Google Calendar Account`)
   - `Gmail OAuth2 API` (named `Gmail Account`)
3. Import the 10 workflow files from `automation/n8n/workflows/`.
4. Toggle all workflows to **Active**.
5. Set backend environment variables in `backend/.env`:
   ```env
   N8N_BASE_URL="https://your-workspace.app.n8n.cloud"
   N8N_WEBHOOK_SECRET="mentor-connect-n8n-shared-secret-key"
   FASTAPI_WEBHOOK_SECRET="mentor-connect-fastapi-callback-secret-key"
   ```

---

## 2. Google OAuth 2.0 Sign-In in FastAPI

Student authentication is owned directly by FastAPI:
- Authorization endpoint: `GET /api/v1/auth/google/login`
- Cryptographic state parameter generated via `secrets.token_urlsafe(32)` and stored in an HttpOnly cookie.
- Callback endpoint: `GET /api/v1/auth/google/callback`
- Token verification: Cryptographically validated using Google's official `google-auth` library (`google.oauth2.id_token.verify_oauth2_token`).
- Verifies signature, issuer (`accounts.google.com`), audience (`GOOGLE_CLIENT_ID`), and expiry.
- Establishes an opaque server-side session in `application_sessions`.

---

## 3. Transcription Provider Evaluation

| Provider | Webhook Support | Google Meet Bot | Consent Audio Prompt | Pricing | Fit for Assignment |
|---|---|---|---|---|---|
| **Recall.ai** | Yes (Signed JSON) | Yes (Headless bot) | Configurable | Free trial / usage-based | Optimal for production |
| **Fireflies.ai** | Yes | Yes (Fred bot) | Enforced | API tier required | Good alternative |
| **Otter.ai** | Limited API | Calendar bot | Enforced | Business tier | Higher friction |
| **Simulation Path** | Native Backend | Simulated Dialogue | N/A | Free & Zero-latency | Optimal for 3-minute evaluation |

Mentor Connect implements an adapter abstraction supporting Recall.ai, Fireflies, and an honest evaluator simulation path that feeds realistic timestamped dialogue directly into the AI report generation pipeline.
