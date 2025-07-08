from sqlalchemy.orm import Session
from sqlalchemy import select
from specialists import models, schemas
from auth.models import UserStatus

def get_specialist(db: Session, specialist_id: int):
    return db.query(models.Specialist).filter(models.Specialist.id == specialist_id).first()

def get_specialist_by_user_id(db: Session, user_id: int):
    return db.query(models.Specialist).filter(models.Specialist.user_id == user_id).first()

def get_specialist_by_phone(db: Session, phone_number: str):
    return db.query(models.Specialist).filter(models.Specialist.phone_number == phone_number, models.Specialist.is_approved == True).first()

def get_specialist_by_phone_all(db: Session, phone_number: str):
    return db.query(models.Specialist).filter(models.Specialist.phone_number == phone_number).first()

def get_specialists(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Specialist).filter(models.Specialist.is_approved == True).offset(skip).limit(limit).all()

def get_specialists_by_filter(db: Session, filter_params: schemas.SpecialistFilter, skip: int = 0, limit: int = 100):
    query = db.query(models.Specialist)
    
    # Always filter by approved status unless explicitly requested otherwise
    if filter_params.is_approved is None:
        query = query.filter(models.Specialist.is_approved == True)
    else:
        query = query.filter(models.Specialist.is_approved == filter_params.is_approved)
    
    if filter_params.specialization:
        query = query.filter(models.Specialist.specialization.ilike(f"%{filter_params.specialization}%"))
    if filter_params.hospital:
        query = query.filter(models.Specialist.hospital.ilike(f"%{filter_params.hospital}%"))
    if filter_params.name:
        query = query.filter(models.Specialist.name.ilike(f"%{filter_params.name}%"))
    if filter_params.phone_number:
        query = query.filter(models.Specialist.phone_number.ilike(f"%{filter_params.phone_number}%"))
    
    return query.offset(skip).limit(limit).all()

def create_specialist(db: Session, specialist: schemas.SpecialistCreate, user_id: int):
    db_specialist = models.Specialist(**specialist.dict(), user_id=user_id)
    db.add(db_specialist)
    db.commit()
    db.refresh(db_specialist)
    return db_specialist

def update_specialist(db: Session, specialist: models.Specialist):
    db.commit()
    db.refresh(specialist)
    return specialist

def approve_specialist(db: Session, specialist: models.Specialist):
    specialist.is_approved = True
    specialist.user.status = UserStatus.ACTIVE
    db.commit()
    db.refresh(specialist)
    return specialist

def delete_specialist(db: Session, specialist: models.Specialist):
    db.delete(specialist)
    db.commit()
    return specialist 