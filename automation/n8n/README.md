# Mentor Connect — n8n Cloud Automation Architecture

This directory contains the 10 production-ready n8n workflows that orchestrate Google Calendar, Google Meet link generation, Gmail notifications, reminders, transcription bots, and error recovery for **Mentor Connect**.

---

## 1. Workflows Inventory

| # | Workflow File | Inbound Webhook / Trigger | Purpose |
|---|---|---|---|
| **01** | `01_calendar_availability.json` | `POST /webhook/mentor-connect/availability` | Queries host Google Calendar & returns normalized open slots |
| **02** | `02_create_meeting.json` | `POST /webhook/mentor-connect/create-meeting` | Creates Google Calendar event with Hangouts/Meet link & triggers callbacks |
| **03** | `03_booking_confirmation_emails.json` | `POST /webhook/mentor-connect/confirmation-emails` | Dispatches formatted confirmation email via Gmail node |
| **04** | `04_pre_meeting_reminders.json` | Schedule Trigger (every 15 mins) | Checks pending sessions and sends 24h & 30m reminders |
| **05** | `05_reschedule_meeting.json` | `POST /webhook/mentor-connect/reschedule` | Updates Google Calendar event start/end times |
| **06** | `06_cancel_meeting.json` | `POST /webhook/mentor-connect/cancel` | Deletes calendar event and frees up slot |
| **07** | `07_transcription_coordination.json` | `POST /webhook/mentor-connect/transcription/coordinate` | Coordinates Fathom AI notetaker calendar verification |
| **08** | `08_transcript_completed.json` | `POST /webhook/mentor-connect/transcript-ready` | Ingests Fathom transcript payload & forwards to FastAPI AI engine |
| **09** | `09_post_call_followup.json` | `POST /webhook/mentor-connect/post-call-followup` | Sends summary, next milestone & action items via Gmail |
| **10** | `10_automation_error_handler.json` | Error Trigger | Global error boundary logging failures back to Mesa Admin |

---

## 2. n8n Cloud Free-Trial Setup Guide

### Step 1: Sign Up for n8n Cloud
1. Go to [https://n8n.io](https://n8n.io) and create a free trial workspace (e.g., `your-workspace.app.n8n.cloud`).
2. Note your instance base URL.

### Step 2: Connect Google Credentials in n8n
> [!IMPORTANT]
> Google Workspace credentials live exclusively inside n8n's encrypted credential store. FastAPI never holds Google Calendar or Gmail secrets.

1. In n8n Cloud, navigate to **Credentials** -> **New Credential**.
2. Select **Google Calendar OAuth2 API**:
   - Provide your Google Client ID and Secret (or use n8n's pre-configured Google App).
   - Authorize your calendar account.
   - Name the credential `Google Calendar Account`.
3. Select **Gmail OAuth2**:
   - Authorize your email sending account.
   - Name the credential `Gmail Account`.

### Step 3: Import Workflows
1. In n8n, click **Workflows** -> **Import from File**.
2. Select each JSON file from `automation/n8n/workflows/` (01 through 10).
3. Toggle the workflow to **Active** (in the top right corner).

### Step 4: Configure Backend Environment Variables
In `backend/.env`:
```env
N8N_BASE_URL="https://your-workspace.app.n8n.cloud"
N8N_WEBHOOK_SECRET="mentor-connect-n8n-shared-secret-key"
FASTAPI_WEBHOOK_SECRET="mentor-connect-fastapi-callback-secret-key"
```

---

## 3. Production vs Test Webhook URLs
- **Test Webhook (`/webhook-test/...`)**: Only active for 120 seconds while you click "Listen for test event" inside the editor. Do NOT use in production backend.
- **Production Webhook (`/webhook/...`)**: Active permanently once the workflow is set to **Active**. This is what Mentor Connect calls.

---

## 4. Quota Optimization & Graceful Degradation
Under the n8n Cloud free trial:
1. **Execution Quota**: Free trials allocate execution counts (e.g., 1,000 executions). Workflows combine related logic and avoid infinite polling loops.
2. **Offline Resilience**: If n8n execution quota expires, credentials disconnect, or network times out, Mentor Connect automatically activates its resilient local simulation layer, logging the event as `simulated` in the Mesa Admin audit trail so reviewers can always evaluate the end-to-end platform seamlessly.
