from sqlalchemy.orm import Session
from specialists import models, schemas
from auth.models import UserStatus
from specialists.queries import get_specialist, get_specialist_by_user_id

def update_specialist_transaction(db: Session, specialist_id: int, specialist_update: schemas.SpecialistUpdate):
    # Get the specialist
    db_specialist = get_specialist(db, specialist_id)
    if not db_specialist:
        return None, "Specialist not found"
    
    # Update fields
    update_data = specialist_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_specialist, field, value)
    
    db.commit()
    db.refresh(db_specialist)
    return db_specialist, None

def approve_specialist_transaction(db: Session, specialist_id: int):
    # Get the specialist
    db_specialist = get_specialist(db, specialist_id)
    if not db_specialist:
        return None, "Specialist not found"
    
    # Approve the specialist
    db_specialist.is_approved = True
    db_specialist.user.status = UserStatus.ACTIVE
    db_specialist.user.is_active = True
    
    db.commit()
    db.refresh(db_specialist)
    return db_specialist, None 