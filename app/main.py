from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from app.routers import auth, events
from app.database import engine, Base
from app.models import user, event, permission  # Import all models

# Create database tables
Base.metadata.create_all(bind=engine)

# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

app = FastAPI(
    title="NeoFi Event Management API",
    description="A collaborative event management system API",
    version="1.0.0",
    openapi_tags=[
        {
            "name": "Authentication",
            "description": "Operations with user authentication",
        },
        {
            "name": "Events",
            "description": "Operations with events",
        }
    ]
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(events.router, prefix="/api/events", tags=["Events"])

@app.get("/")
def read_root():
    return {"message": "Welcome to NeoFi Event Management API"} 