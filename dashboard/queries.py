from sqlalchemy.orm import Session
from sqlalchemy import select, func
from dashboard import models

def get_admin(db: Session, admin_id: int):
    return db.query(models.Admin).filter(models.Admin.id == admin_id).first()

def get_admin_by_user_id(db: Session, user_id: int):
    return db.query(models.Admin).filter(models.Admin.user_id == user_id).first()

def get_admins(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Admin).offset(skip).limit(limit).all()

def create_admin(db: Session, admin: models.Admin):
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin

def update_admin(db: Session, admin: models.Admin):
    db.commit()
    db.refresh(admin)
    return admin

def delete_admin(db: Session, admin: models.Admin):
    db.delete(admin)
    db.commit()
    return admin

def get_dashboard_stats(db: Session):
    # Get total specialists
    total_specialists = db.query(models.Specialist).count()
    
    # Get approved specialists
    approved_specialists = db.query(models.Specialist).filter(models.Specialist.is_approved == True).count()
    
    # Get pending specialists
    pending_specialists = db.query(models.Specialist).filter(models.Specialist.is_approved == False).count()
    
    # Get total users
    total_users = db.query(models.User).count()
    
    return {
        "total_specialists": total_specialists,
        "approved_specialists": approved_specialists,
        "pending_specialists": pending_specialists,
        "total_users": total_users
    } 