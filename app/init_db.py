from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models.user import User
from app.models.event import Event, EventVersion
from app.models.permission import EventPermission, Role
from datetime import datetime, timedelta
from app.schemas.user import UserRole
import bcrypt

# Database URL - make sure this matches your configuration
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/neofi"

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def init_db():
    # Create engine and session
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("Dropped all tables")

        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Created all tables")

        # Create test users
        users = [
            User(
                username="testuser1",
                email="test1@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.OWNER
            ),
            User(
                username="testuser2",
                email="test2@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.EDITOR
            ),
            User(
                username="testuser3",
                email="test3@example.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.VIEWER
            )
        ]
        db.add_all(users)
        db.commit()
        print("Created test users")

        # Create some test events
        now = datetime.utcnow()
        events = [
            Event(
                title="Team Meeting",
                description="Weekly team sync",
                start_time=now + timedelta(days=1),
                end_time=now + timedelta(days=1, hours=1),
                location="Conference Room A",
                is_recurring=True,
                recurrence_pattern={"frequency": "weekly", "interval": 1},
                owner_id=1
            ),
            Event(
                title="Project Review",
                description="Quarterly project review meeting",
                start_time=now + timedelta(days=2),
                end_time=now + timedelta(days=2, hours=2),
                location="Virtual",
                is_recurring=False,
                owner_id=1
            ),
            Event(
                title="Client Call",
                description="Meeting with client",
                start_time=now + timedelta(days=3),
                end_time=now + timedelta(days=3, hours=1),
                location="Zoom",
                is_recurring=False,
                owner_id=2
            )
        ]
        db.add_all(events)
        db.commit()
        print("Created test events")

        # Create event versions
        for event in events:
            version = EventVersion(
                event_id=event.id,
                version_number=1,
                data={
                    "title": event.title,
                    "description": event.description,
                    "start_time": event.start_time.isoformat(),
                    "end_time": event.end_time.isoformat(),
                    "location": event.location,
                    "is_recurring": event.is_recurring,
                    "recurrence_pattern": event.recurrence_pattern
                },
                created_by=event.owner_id
            )
            db.add(version)
        db.commit()
        print("Created event versions")

        # Create some permissions
        permissions = [
            EventPermission(
                event_id=1,
                user_id=2,
                role=Role.EDITOR
            ),
            EventPermission(
                event_id=1,
                user_id=3,
                role=Role.VIEWER
            ),
            EventPermission(
                event_id=2,
                user_id=2,
                role=Role.VIEWER
            )
        ]
        db.add_all(permissions)
        db.commit()
        print("Created event permissions")

        print("Database initialization completed successfully!")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db() 