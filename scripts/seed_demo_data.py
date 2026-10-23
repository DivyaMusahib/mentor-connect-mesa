import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.database import SessionLocal
from app.models import User
from app.api.v1.demo import seed_demo_environment


async def main():
    print("[*] Seeding Mentor Connect demo data...")
    db = SessionLocal()
    try:
        # Find or create demo student
        user = db.query(User).filter(User.role == "student").first()
        if not user:
            user = User(
                email="arjun.bansal.student@mesa.edu",
                full_name="Arjun Bansal (Mesa Student)",
                role="student",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        res = await seed_demo_environment(user=user, db=db)
        print(f"[✓] {res.get('message', 'Demo data seeded successfully!')}")
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
