from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from specialists import models, schemas, queries, transactions
from auth.routes import get_current_user
from auth.models import User, UserType, UserStatus
from database import get_db
from typing import Optional

# Dependency to require admin
def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Dependency to require specialist
def require_specialist(current_user: User = Depends(get_current_user)):
    if current_user.user_type != UserType.SPECIALIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    if not current_user.is_active or getattr(current_user, 'status', None) != 'active':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Specialist account is not active"
        )
    return current_user

router = APIRouter(prefix="/specialists", tags=["specialists"])

def get_current_specialist(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.user_type != UserType.SPECIALIST:  # UserType.SPECIALIST
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Specialist account is not active"
        )
    specialist = queries.get_specialist_by_user_id(db, current_user.id)
    if not specialist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specialist profile not found"
        )
    return specialist

@router.get("/me", response_model=schemas.SpecialistOut)
async def read_specialist_me(current_specialist: models.Specialist = Depends(get_current_specialist)):
    return current_specialist

@router.patch("/me", response_model=schemas.SpecialistOut)
async def update_specialist_profile(
    specialist_update: schemas.SpecialistUpdate,
    current_specialist: models.Specialist = Depends(get_current_specialist),
    db: Session = Depends(get_db)
):
    updated_specialist, error = transactions.update_specialist_transaction(db, current_specialist.id, specialist_update)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return updated_specialist

@router.get("/", response_model=list[schemas.SpecialistOut])
async def list_specialists(
    skip: int = 0,
    limit: int = 100,
    specialization: Optional[str] = None,
    hospital: Optional[str] = None,
    name: Optional[str] = None,
    is_approved: Optional[bool] = None,
    phone_number: Optional[str] = None,
    db: Session = Depends(get_db),
):
    filter_params = schemas.SpecialistFilter(
        specialization=specialization,
        hospital=hospital,
        name=name,
        is_approved=is_approved,
        phone_number=phone_number
    )
    return queries.get_specialists_by_filter(db, filter_params, skip=skip, limit=limit)

@router.post("/{specialist_id}/approve", response_model=schemas.SpecialistOut)
async def approve_specialist(
    specialist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
): 
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can approve specialists"
        )
    db_specialist, error = transactions.approve_specialist_transaction(db, specialist_id)
    if error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error)
    return db_specialist

@router.get("/{specialist_id}", response_model=schemas.SpecialistOut)
async def get_specialist(specialist_id: int, db: Session = Depends(get_db)):
    specialist = queries.get_specialist(db, specialist_id)
    if not specialist or not specialist.is_approved or not specialist.user.is_active:
        raise HTTPException(status_code=404, detail="Specialist not found")
    return specialist

@router.patch("/{specialist_id}", response_model=schemas.SpecialistOut)
async def admin_update_specialist(
    specialist_id: int,
    specialist_update: schemas.SpecialistUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    updated_specialist, error = transactions.update_specialist_transaction(db, specialist_id, specialist_update)
    if error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)
    return updated_specialist

@router.post("/{specialist_id}/reject", response_model=schemas.SpecialistOut)
async def reject_specialist(
    specialist_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    db_specialist = queries.get_specialist(db, specialist_id)
    if not db_specialist:
        raise HTTPException(status_code=404, detail="Specialist not found")
    db_specialist.is_approved = False
    db_specialist.user.status = UserStatus.INACTIVE
    db_specialist.user.is_active = False
    db.commit()
    db.refresh(db_specialist)
    return db_specialist

@router.post("/filter", response_model=list[schemas.SpecialistOut])
async def filter_specialists(
    filter: schemas.SpecialistFilter,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return queries.get_specialists_by_filter(db, filter, skip=skip, limit=limit)

# Auth Endpoint (login by phone number)
@router.post("/login", response_model=schemas.SpecialistOut)
async def login(phone_number: str, db: Session = Depends(get_db)):
    specialist = queries.get_specialist_by_phone(db, phone_number)
    if not specialist or not specialist.is_approved or not specialist.user.is_active:
        raise HTTPException(status_code=404, detail="Specialist not found or not approved")
    return specialist 