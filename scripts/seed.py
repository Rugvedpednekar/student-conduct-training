from app.database import Base, SessionLocal, engine
from app.seed import seed_roles_users_and_content


if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        seed_roles_users_and_content(db)
    print("Seed complete.")
