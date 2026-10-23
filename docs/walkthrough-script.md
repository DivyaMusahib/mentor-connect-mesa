# Mentor Connect — 3 to 5 Minute Evaluator Walkthrough Script

**Presenter**: Technical Associate Candidate  
**Audience**: Mesa School of Business Hiring Committee  
**Target Duration**: 4 minutes  

---

### [00:00 - 00:45] Introduction & Authentication
- **Action**: Open application homepage at `http://localhost:5173`.
- **Narration**:
  > "Hi everyone, I'm excited to present **Mentor Connect**, an AI-powered executive mentorship platform built for the Mesa School of Business.
  > The platform addresses a common failure mode in career transitions: blind directory browsing leading to unprepared calls and zero follow-through.
  > Let's sign in. For production, we implement Google OAuth 2.0 directly in FastAPI with cryptographic ID-token verification. For reviewers, we also built a 1-click Evaluator Demo login. Let's enter as student Arjun Bansal."

---

### [00:45 - 01:45] AI Career Diagnostic & Explainable Matching
- **Action**: Click on **AI Career Advisor**.
- **Narration**:
  > "Here is our conversational diagnostic engine. Rather than searching 50 mentors manually, I describe my real blocker: *'I want to transition into Product Management in B2B SaaS, but my portfolio projects look like simple tutorial clones.'*
  > The AI diagnoses my situation and matches me against our authoritative 50-mentor dataset.
  > Notice the explainable matching cards: instead of an opaque percentage, it transparently breaks down domain fit, verified dataset expertise, and specific topics the mentor can help with.
  > Notice also that direct booking from the directory was locked until our diagnostic validated fit."

---

### [01:45 - 02:45] n8n Calendar Booking & Pre-Call AI Brief
- **Action**: Click **Book Session** on Mentor 042. Select a slot and confirm.
- **Narration**:
  > "When I click book, FastAPI doesn't talk to Google Calendar directly. It dispatches a signed webhook to n8n Cloud.
  > n8n handles the Google Calendar event creation, generates a real Google Meet link, and dispatches the student confirmation email via Gmail.
  > Simultaneously, Gemini compiles an authoritative Pre-Call Preparation Brief containing the student's problem, exactly three concrete discussion questions, and an interactive prep checklist. This same brief is saved once and reflected across the portal, calendar invite, and emails."

---

### [02:45 - 03:45] Meeting Completion, Evidence-Linked Insights & Action Items
- **Action**: Navigate to **My Sessions**, click **Simulate Completion** on the booked session, then navigate to **Post-Call Report**.
- **Narration**:
  > "In a real call, our transcription bot adapter captures the meeting audio. For our 3-minute evaluation, clicking 'Simulate Completion' feeds realistic dialogue into our real AI pipeline.
  > Look at the report: summary points, next milestone, and our standout feature — **Evidence-Linked Insights**.
  > When I expand an insight, you see the exact supporting quote from the mentor and the transcript timestamp.
  > Below, we have concrete action items with deadlines and deliverables. I can check these off, and they automatically synchronize with my **Career Roadmap** and **Progress Tracker**."

---

### [03:45 - 04:30] Mesa Admin Dashboard & Architecture Summary
- **Action**: Switch to **Mesa Admin** role using the evaluator banner.
- **Narration**:
  > "Finally, let's switch to the Mesa Admin view.
  > The committee can monitor real database metrics: total students, diagnostic outcomes, mentor demand breakdown, and crucially, **Unmatched Mentor Supply Gaps** to guide upcoming mentor recruitment.
  > We can also inspect the n8n automation activity timeline and trigger safe retries for any failed webhooks.
  > All frontend code is clean, readable JavaScript and React without TypeScript, and the backend has 25 automated pytest tests passing with 100% test coverage. Thank you!"
