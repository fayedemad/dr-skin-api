from sqlalchemy.orm import Session
from auth import models, schemas
from auth.security import get_password_hash
from auth.queries import get_user_by_username, get_user_by_email
from specialists import models as specialist_models
from specialists.queries import get_specialist_by_user_id, get_specialist_by_phone_all

def create_user_transaction(db: Session, user: schemas.UserCreate):
    # Check if username exists
    existing_user = get_user_by_username(db, username=user.username)
    if existing_user:
        return None, "Username already registered"
    
    # Check if email exists
    existing_email = get_user_by_email(db, email=user.email)
    if existing_email:
        return None, "Email already registered"
    
    # Create new specialist user (default for registration)
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        user_type=models.UserType.SPECIALIST,
        status=models.UserStatus.PENDING,
        is_active=False,
        is_superuser=False
    )
    db.add(db_user)
    db.flush()  # Get the ID without committing
    db.refresh(db_user)
    return db_user, None

def create_specialist_registration_transaction(db: Session, registration: schemas.SpecialistRegistration):
    # Check if username exists
    existing_user = get_user_by_username(db, username=registration.username)
    if existing_user:
        return None, "Username already registered"
    
    # Check if email exists
    existing_email = get_user_by_email(db, email=registration.email)
    if existing_email:
        return None, "Email already registered"
    
    # Check if phone number already exists
    existing_specialist = get_specialist_by_phone_all(db, registration.phone_number)
    if existing_specialist:
        return None, "Phone number already registered"
    
    # Create new specialist user
    hashed_password = get_password_hash(registration.password)
    db_user = models.User(
        username=registration.username,
        email=registration.email,
        hashed_password=hashed_password,
        user_type=models.UserType.SPECIALIST,
        status=models.UserStatus.PENDING,
        is_active=False,
        is_superuser=False
    )
    db.add(db_user)
    db.flush()  # Get the user ID without committing
    
    # Create specialist profile
    db_specialist = specialist_models.Specialist(
        user_id=db_user.id,
        name=registration.name,
        phone_number=registration.phone_number,
        license_number=registration.license_number,
        specialization=registration.specialization,
        hospital=registration.hospital,
        bio=registration.bio,
        is_approved=False
    )
    db.add(db_specialist)
    db.flush()  # Get the specialist ID without committing
    db.refresh(db_user)
    db.refresh(db_specialist)
    
    return db_user, None

def update_specialist_files_transaction(db: Session, user_id: int, license_file_path: str, profile_image_path: str = None):
    """Update specialist profile with file paths after files are saved"""
    specialist = get_specialist_by_user_id(db, user_id)
    if not specialist:
        return None, "Specialist not found"
    
    specialist.license_file_path = license_file_path
    if profile_image_path:
        specialist.profile_image = profile_image_path
    
    db.flush()  # Flush changes without committing
    db.refresh(specialist)
    return specialist, None 