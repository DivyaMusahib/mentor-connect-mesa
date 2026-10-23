# Mentor Connect — One-Page Product Design Rationale

**Candidate**: Divya Musahib
**Assignment**: Mesa School of Business — Technical Associate
**Submitted**: October 2026

---

## The Problem I Was Solving

Career mentorship fails most students at the same three points: they pick the wrong mentor (name recognition over fit), they arrive underprepared, and after the call, the advice evaporates with no follow-through. I designed Mentor Connect to fix all three — not separately, but as a single continuous flow.

---

## Decisions I Made

### 1. Lock booking behind AI diagnosis

The biggest temptation was to build a slick directory and let students book freely. I chose not to. Allowing open booking with 50 mentors produces exactly the failure mode the platform is meant to prevent: a student books a VC partner when they need a product manager, spends 45 minutes on the wrong conversation, and walks away frustrated.

Instead, students first talk to an AI Career Diagnostic Advisor. It asks focused questions about their current situation, the specific blocker, what they have already tried, and what they need to walk away with. Booking is only unlocked after that diagnosis is complete and a genuine match is found. This is intentionally a gate — not friction for its own sake, but a quality signal that improves the call before it starts.

### 2. Explainable matching, not black-box scores

A "94% match" badge tells a student nothing. I built the matching to surface *why* a mentor fits: which verified domain overlaps, which specific expertise columns from the dataset were triggered, and what topics the mentor is likely versus unlikely to help with. This also forces the system to stay honest — every explanation is grounded in the actual data rows, not generated freely.

### 3. Full-context Gemini matching over a vector database

For 50 mentors (~14 KB), a vector database would introduce chunking loss, embedding drift, and deployment overhead without any benefit. Passing the entire normalized catalogue to Gemini in a single structured call gives it cross-attribute reasoning (e.g., a mentor with both Edtech sector experience and n8n workflow expertise) that chunked retrieval would miss. If the Gemini API key is absent or rate-limited, a deterministic keyword-overlap heuristic takes over silently — the platform never breaks.

### 4. Pre-call brief generated once, stored and reused everywhere

Rather than generating a new brief every time a student opens the preparation page, the brief is created at booking time and persisted. The same document surfaces in the preparation page, the calendar invite, and the confirmation email. This matters for consistency — a student who re-opens the page on the day of the call sees exactly what was sent to them two days earlier.

### 5. Evidence-linked post-call reports

Generic AI summaries lose trust quickly. I anchored every insight in the report to a verbatim timestamped excerpt from the transcript. Students can expand any bullet to see exactly what the mentor said and when. Action items are concrete (deliverable, deadline, owner) and flow directly into a career roadmap and progress tracker so the call produces observable momentum, not just notes.

### 6. n8n for all Google Workspace orchestration

Moving Google Calendar, Google Meet, and Gmail into n8n rather than calling their APIs directly from FastAPI kept the backend focused on business logic and security boundaries. n8n's native OAuth nodes handle token rotation reliably; n8n's execution logs give the Mesa Admin team a visual audit trail. If an email template needs changing, it changes in n8n without a backend redeploy.

### 7. Mesa Admin dashboard as a product health surface

The assignment asked for visibility into "how all of it is going." I built an admin dashboard that tracks real metrics: total students, diagnostic outcomes, which mentors are most requested, and crucially — Unmatched Mentor Supply Gaps, which log every case where a student's domain request could not be satisfied. This turns the platform into a recruitment signal: the team can see exactly which mentor profiles to add next.

---

## Decisions I Did Not Make

**No real-time availability from mentor calendars.** The 50 mentors are anonymised with placeholder contacts. I modelled availability as configurable slots managed by the Mesa team rather than pulling from individual mentor Google Calendars, which would require 50 separate OAuth grants that are not practical in this context.

**No mobile-first redesign.** The platform is responsive but optimised for a focused desktop session. A career diagnosis conversation benefits from a larger canvas.

**No separate mentor portal.** Mentors do not log in to the platform. This was a deliberate scope choice — the student and Mesa team flows deliver the core value, and a mentor portal would double the surface area without improving the assignment's core demonstration.

---

## Assumptions

- Mentors' availability is managed centrally via a host Google Calendar (one calendar shared with the Mesa team), which n8n queries.
- The 50 mentor records are treated as the authoritative, static catalogue for matching. Any profile with a hallucinated ID that the AI returns is discarded before it reaches the student.
- Students sign in with their own Google accounts. The evaluator demo mode provides 1-click bypass for reviewers without Google accounts or API keys.
