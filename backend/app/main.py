from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.services.mentor_service import load_mentors_from_csv
from app.models import Mentor

from app.api.v1.auth import router as auth_router
from app.api.v1.mentors import router as mentors_router
from app.api.v1.chat import router as chat_router
from app.api.v1.bookings import router as bookings_router
from app.api.v1.reports import router as reports_router
from app.api.v1.career import router as career_router
from app.api.v1.integrations import router as integrations_router
from app.api.v1.admin import router as admin_router
from app.api.v1.demo import router as demo_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup & shutdown events."""
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        count = db.query(Mentor).count()
        if count == 0 and settings.MENTOR_DATA_PATH.exists():
            loaded = load_mentors_from_csv(db=db)
            print(f"[Mentor Connect] Successfully loaded {loaded} verified mentors from CSV.")
    except Exception as e:
        print(f"[Mentor Connect] Startup dataset verification error: {e}")
    finally:
        db.close()

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Full-Stack AI Mentorship Platform for Mesa School of Business",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS Middleware for React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_v1_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_v1_prefix)
app.include_router(mentors_router, prefix=api_v1_prefix)
app.include_router(chat_router, prefix=api_v1_prefix)
app.include_router(bookings_router, prefix=api_v1_prefix)
app.include_router(reports_router, prefix=api_v1_prefix)
app.include_router(career_router, prefix=api_v1_prefix)
app.include_router(integrations_router, prefix=api_v1_prefix)
app.include_router(admin_router, prefix=api_v1_prefix)
app.include_router(demo_router, prefix=api_v1_prefix)


@app.get("/")
def root():
    return {
        "name": settings.PROJECT_NAME,
        "status": "operational",
        "docs": "/docs",
        "environment": settings.ENVIRONMENT,
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
