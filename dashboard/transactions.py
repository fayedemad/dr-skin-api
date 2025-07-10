from sqlalchemy.orm import Session
from dashboard import models, schemas
from dashboard.queries import get_dashboard_stats, get_admin_by_user_id
from specialists.models import Specialist
from specialists.schemas import SpecialistUpdate
from auth.models import UserStatus
from sqlalchemy import select

def create_admin_transaction(db: Session, admin: schemas.AdminCreate, user_id: int):
    # Check if user already has an admin profile
    existing_admin = get_admin_by_user_id(db, user_id=user_id)
    if existing_admin:
        return None, "User already has an admin profile"
    
    # Create new admin profile
    db_admin = models.Admin(**admin.dict(), user_id=user_id)
    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)
    return db_admin, None

def get_specialist(db: Session, specialist_id: int):
    return db.query(Specialist).filter(Specialist.id == specialist_id).first()

def update_specialist_transaction(db: Session, specialist_id: int, specialist_update: SpecialistUpdate):
    specialist = get_specialist(db, specialist_id)
    if not specialist:
        return None, "Specialist not found"
    update_data = specialist_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(specialist, field, value)
    db.commit()
    db.refresh(specialist)
    return specialist, None

def get_dashboard_stats_transaction(db: Session):
    return get_dashboard_stats(db) 