"""Create the first admin user. Run from api/ with venv active."""

import sys

from sqlalchemy import select

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole

# Import models so metadata is registered
import app.models  # noqa: F401


def main() -> None:
    if len(sys.argv) < 4:
        print("Usage: python scripts/create_admin.py <name> <email> <password>")
        sys.exit(1)

    name, email, password = sys.argv[1], sys.argv[2], sys.argv[3]
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == email))
        if existing:
            print(f"User with email {email} already exists.")
            sys.exit(1)

        user = User(
            name=name,
            email=email,
            password_hash=get_password_hash(password),
            role=UserRole.ADMIN,
        )
        db.add(user)
        db.commit()
        print(f"Admin user created: {email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
