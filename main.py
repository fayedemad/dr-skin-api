from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from specialists import routes as specialist_routes
from database import init_db, get_db
from auth import routes as auth_routes
from dashboard import routes as dashboard_routes
from sqlalchemy.exc import SQLAlchemyError
import traceback
from diagnosis import routes as diagnosis_routes
import os
from sqlalchemy.orm import Session
from auth.models import UserType, UserStatus
from auth.security import get_password_hash
from auth.queries import get_user_by_username

app = FastAPI(
    title="Dr. Skin API",
    description="API for skin specialist management system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    """Middleware to store database session in request state"""
    # Create a database session
    for db in get_db():
        request.state.db = db
        try:
            response = await call_next(request)
            return response
        except Exception:
            # Rollback on any exception
            db.rollback()
            raise
        finally:
            db.close()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler that rolls back database transactions"""
    # Get the database session from the request state if it exists
    db = getattr(request.state, "db", None)
    
    if db:
        try:
            db.rollback()
        except Exception as rollback_error:
            print(f"Error during rollback: {rollback_error}")
    
    # Log the error
    print(f"Unhandled exception: {exc}")
    print(f"Traceback: {traceback.format_exc()}")
    
    # Return a generic error response
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle SQLAlchemy specific errors"""
    # Get the database session from the request state if it exists
    db = getattr(request.state, "db", None)
    
    if db:
        try:
            db.rollback()
        except Exception as rollback_error:
            print(f"Error during rollback: {rollback_error}")
    
    # Log the error
    print(f"SQLAlchemy error: {exc}")
    print(f"Traceback: {traceback.format_exc()}")
    
    # Return a generic error response
    return JSONResponse(
        status_code=500,
        content={"detail": "Database error occurred"}
    )

DEFAULT_ADMIN_USERNAME = "admin"
DEFAULT_ADMIN_EMAIL = "admin@drskin.dev"
DEFAULT_ADMIN_PASSWORD = "admin123"

@app.on_event("startup")
def on_startup():
    init_db()
    env = os.environ.get("DR_SKIN_ENV", "dev")
    if env == "dev":
        # Create default admin if not exists
        db: Session = next(get_db())
        admin_user = get_user_by_username(db, DEFAULT_ADMIN_USERNAME)
        if not admin_user:
            hashed_password = get_password_hash(DEFAULT_ADMIN_PASSWORD)
            from auth import models
            db_user = models.User(
                username=DEFAULT_ADMIN_USERNAME,
                email=DEFAULT_ADMIN_EMAIL,
                hashed_password=hashed_password,
                user_type=UserType.ADMIN,
                status=UserStatus.ACTIVE,
                is_active=True,
                is_superuser=True
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            print("\n[DrSkin] Default admin created:")
            print(f"  Username: {DEFAULT_ADMIN_USERNAME}")
            print(f"  Email: {DEFAULT_ADMIN_EMAIL}")
            print(f"  Password: {DEFAULT_ADMIN_PASSWORD}\n")
        else:
            print("[DrSkin] Default admin already exists.")

@app.get("/")
async def read_root():
    return {"message": "Welcome to Dr. Skin API"}

@app.post("/diagnose")
async def pseudo_diagnose():
    """Pseudo endpoint for skin disease diagnosis (static data)."""
    return {
        "predictions": [
            {"class": "NV", "confidence": 0.82},
            {"class": "BKL", "confidence": 0.10},
            {"class": "MEL", "confidence": 0.08}
        ],
        "top_prediction": {"class": "NV", "confidence": 0.82}
    }

# Include routers
app.include_router(specialist_routes.router)
app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(diagnosis_routes.router) 