from sqlalchemy.orm import Session
from dashboard import models, schemas
from dashboard.queries import get_dashboard_stats, get_admin_by_user_id

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

def get_dashboard_stats_transaction(db: Session):
    return get_dashboard_stats(db) 