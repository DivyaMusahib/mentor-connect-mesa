# Mentor Connect — Production Deployment Guide

## 1. Production Architecture Overview

Mentor Connect is built on a high-availability, zero-maintenance cloud architecture designed for the free and hobby tiers:

| Layer | Service | Purpose | Pricing / Tier |
|---|---|---|---|
| **Frontend** | [Vercel](https://vercel.com) | React Vite SPA with client-side routing | Free Hobby Tier |
| **Backend** | [Render](https://render.com) | FastAPI (Python 3.12) Web Service | Free Tier / Hobby |
| **Database** | [Neon](https://neon.tech) / [Supabase](https://supabase.com) | Serverless Managed PostgreSQL 16 | Free Tier |
| **Automation** | [n8n Cloud](https://n8n.io) | Google Calendar, Google Meet & Gmail Workflows | Cloud Free Trial |
| **AI Engine** | [Google AI Studio](https://aistudio.google.com) | Gemini 2.5 Flash Structured Outputs | Free Tier |

---

## 2. Google Cloud Console Setup (Authentication)

Student Google OAuth 2.0 authentication is managed through Google Cloud Console.

### Step 1: Configure OAuth Consent Screen
1. Go to [Google Cloud Console](https://console.cloud.google.com/) -> **APIs & Services** -> **OAuth consent screen** (or **Audience**).
2. **User Type**: Select **External** -> click **Create**.
3. **App Details**: Set App name to `Mentor Connect` and provide your contact email.
4. **Publishing Status**:
   - For public evaluator reviews, click **PUBLISH APP** to switch from *Testing* to *In Production*.
   - Because Mentor Connect only requests basic identity scopes (`openid`, `profile`, `email`), Google allows instant publishing without requiring app verification.
   - If left in *Testing* mode, add all evaluator email addresses under **Test users**.

### Step 2: Configure OAuth 2.0 Client Credentials
1. Navigate to **APIs & Services** -> **Credentials** -> click your **Web Client** (or click **+ Create Credentials** -> **OAuth client ID** -> **Web application**).
2. **Authorized JavaScript origins**:
   ```
   http://localhost:5173
   http://localhost:8000
   https://<your-frontend-name>.vercel.app
   https://<your-backend-name>.onrender.com
   ```
3. **Authorized redirect URIs**:
   ```
   http://localhost:8000/api/v1/auth/google/callback
   https://<your-backend-name>.onrender.com/api/v1/auth/google/callback
   ```
4. Copy your **Client ID** and **Client Secret**.

---

## 3. Step-by-Step Production Deployment

### Step 1: Managed PostgreSQL Database (Neon)
1. Sign up at [Neon.tech](https://neon.tech) (free serverless PostgreSQL).
2. Click **Create Project** -> name it `mentor-connect`.
3. Copy the database connection URI from the dashboard:
   ```text
   postgresql://user:password@ep-sample-123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```
4. Ensure the URI prefix uses `postgresql+psycopg2://` for SQLAlchemy:
   ```text
   postgresql+psycopg2://user:password@ep-sample-123.us-east-2.aws.neon.tech/neondb?sslmode=require
   ```

### Step 2: Backend Deployment (Render)
1. Push your repository to GitHub.
2. Sign in to [Render.com](https://render.com) and click **New +** -> **Web Service**.
3. Connect your GitHub repository.
4. Configure service parameters:
   - **Name**: `mentor-connect-api`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: **Free**
5. Add Environment Variables:
   ```env
   ENVIRONMENT=production
   DEBUG=False
   SECRET_KEY=<generate-a-random-64-character-string>
   DATABASE_URL=<your-neon-postgres-connection-string>
   BACKEND_URL=https://<your-backend-name>.onrender.com
   FRONTEND_URL=https://<your-frontend-name>.vercel.app
   COOKIE_SECURE=True
   COOKIE_SAMESITE=none
   GEMINI_API_KEY=<your-google-ai-studio-gemini-key>
   GEMINI_MODEL=gemini-2.5-flash
   GOOGLE_CLIENT_ID=<your-google-client-id>.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=<your-google-client-secret>
   GOOGLE_REDIRECT_URI=https://<your-backend-name>.onrender.com/api/v1/auth/google/callback
   N8N_BASE_URL=https://<your-workspace>.app.n8n.cloud
   N8N_WEBHOOK_SECRET=mentor-connect-n8n-shared-secret-key
   FASTAPI_WEBHOOK_SECRET=mentor-connect-fastapi-callback-secret-key
   ENABLE_EVALUATOR_DEMO=True
   ```
6. Click **Deploy Web Service**.
   Render will install dependencies, apply Alembic migrations automatically, and load the 50 mentors dataset.

### Step 3: Frontend Deployment (Vercel)
1. Sign in to [Vercel.com](https://vercel.com) and click **Add New...** -> **Project**.
2. Select your GitHub repository.
3. Configure build settings:
   - **Root Directory**: `frontend`
   - **Framework Preset**: `Vite`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable:
   ```env
   VITE_API_BASE_URL=https://<your-backend-name>.onrender.com
   ```
5. Click **Deploy**.
   Vercel automatically applies the `frontend/vercel.json` rewrites for SPA routing.

### Step 4: n8n Cloud Automation
1. Log in to your n8n Cloud instance (e.g., `https://<your-workspace>.app.n8n.cloud`).
2. Under **Credentials**, connect:
   - `Google Calendar OAuth2 API` (named `Google Calendar Account`)
   - `Gmail OAuth2 API` (named `Gmail Account`)
3. Import the 10 JSON workflows from `automation/n8n/workflows/`.
4. Click **Publish** on each workflow.

---

## 4. Evaluator Verification Checklist

After deployment, verify the platform via these check steps:
1. **Health Check**: Open `https://<your-backend-name>.onrender.com/api/v1/integrations/health` (should return `"status": "healthy"`).
2. **Interactive Docs**: Open `https://<your-backend-name>.onrender.com/docs` to verify OpenAPI schemas.
3. **Student Flow**: Open your Vercel URL, click **Continue with Google** (or use the 1-click **Arjun Bansal** demo login).
4. **AI Diagnosis**: Go to `/advisor`, send a career query, and verify ranked mentor cards with fit scores.
5. **Booking**: Book a session to trigger Workflow 02 in n8n Cloud.
6. **Mesa Admin**: Switch to Admin, verify supply gap tracking, email outbox logs, and automation audit events.
