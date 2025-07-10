from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form, UploadFile, File
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from auth import models, schemas, queries, security, transactions
from database import get_db
import os
import shutil
from pathlib import Path
from fastapi.responses import FileResponse
from typing import Optional

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
LICENSE_DIR = UPLOAD_DIR / "licenses"
LICENSE_DIR.mkdir(exist_ok=True)
PROFILE_DIR = UPLOAD_DIR / "profiles"
PROFILE_DIR.mkdir(exist_ok=True)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token_data = security.verify_token(token)
    if token_data is None:
        raise credentials_exception
    
    username = token_data.get("sub")
    if username is None:
        raise credentials_exception
    
    user = queries.get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user

async def validate_specialist_form_data(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    phone_number: str = Form(...),
    license_number: str = Form(...),
    specialization: str = Form(...),
    hospital: str = Form(...),
    bio: str = Form(...),
) -> schemas.SpecialistRegistrationForm:
    """Validate form data using Pydantic model"""
    try:
        form_data = schemas.SpecialistRegistrationForm(
            username=username,
            email=email,
            password=password,
            name=name,
            phone_number=phone_number,
            license_number=license_number,
            specialization=specialization,
            hospital=hospital,
            bio=bio
        )
        return form_data
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/register", response_model=schemas.UserOut)
async def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Registers a specialist user. All new users are specialists and require admin approval.
    db_user, error = transactions.create_user_transaction(db, user)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return db_user

@router.post("/specialist-register", response_model=schemas.SpecialistRegistrationResponse)
async def register_specialist(
    form_data: schemas.SpecialistRegistrationForm = Depends(validate_specialist_form_data),
    license_file: UploadFile = File(...),
    profile_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    # just 3lshan n3dy l lela
    # allowed_image_types = ["zimage/jpeg", "image/png", "image/jpg"]
    # allowed_document_types = ["application/pdf", "image/jpeg", "image/png", "image/jpg"]
    
    # if license_file.content_type not in allowed_document_types:
    #     raise HTTPException(
    #         status_code=400, 
    #         detail="License file must be PDF, JPEG, or PNG"
    #     )
    
    # if profile_image and profile_image.content_type not in allowed_image_types:
    #     raise HTTPException(
    #         status_code=400, 
    #         detail="Profile image must be JPEG or PNG"
    #     )
    
    # Validate file sizes (5MB for documents, 2MB for images)
    # Read file content to get size
    license_content = await license_file.read()
    if len(license_content) > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=400, 
            detail="License file must be less than 5MB"
        )
    
    # Reset file pointer for later use
    await license_file.seek(0)
    
    profile_content = None
    if profile_image:
        profile_content = await profile_image.read()
        if len(profile_content) > 2 * 1024 * 1024:  # 2MB
            raise HTTPException(
                status_code=400, 
                detail="Profile image must be less than 2MB"
            )
        # Reset file pointer for later use
        await profile_image.seek(0)
    
    # Create registration data
    registration_data = schemas.SpecialistRegistration(
        username=form_data.username,
        email=form_data.email,
        password=form_data.password,
        name=form_data.name,
        phone_number=form_data.phone_number,
        license_number=form_data.license_number,
        specialization=form_data.specialization,
        hospital=form_data.hospital,
        bio=form_data.bio
    )
    
    # Create user and specialist profile (this will flush but not commit)
    db_user, error = transactions.create_specialist_registration_transaction(db, registration_data)
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    # Save license file
    license_filename = f"license_{db_user.id}_{license_file.filename}"
    license_path = LICENSE_DIR / license_filename
    
    with open(license_path, "wb") as buffer:
        shutil.copyfileobj(license_file.file, buffer)
    
    # Save profile image if provided
    profile_filename = None
    profile_path = None
    if profile_image:
        profile_filename = f"profile_{db_user.id}_{profile_image.filename}"
        profile_path = PROFILE_DIR / profile_filename
        
        with open(profile_path, "wb") as buffer:
            shutil.copyfileobj(profile_image.file, buffer)
    
    # Update specialist profile with file paths (this will flush but not commit)
    transactions.update_specialist_files_transaction(
        db, 
        db_user.id, 
        str(license_path), 
        str(profile_path) if profile_path else None
    )
    
    # If everything succeeded, commit the transaction
    db.commit()
    
    return schemas.SpecialistRegistrationResponse(
        id=db_user.id,
        username=db_user.username,
        email=db_user.email,
        user_type=db_user.user_type,
        status=db_user.status,
        is_active=db_user.is_active,
        is_superuser=db_user.is_superuser,
        message="Registration successful! Please wait for admin approval to activate your account."
    )

@router.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = queries.get_user_by_username(db, username=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active and approved
    if not user.is_active or user.status != models.UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is not active. Please wait for admin approval.",
        )
    
    access_token_expires = timedelta(minutes=security.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username, "user_type": user.user_type.value},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=schemas.UserOut)
async def read_users_me(current_user: models.User = Depends(get_current_user)):
    return current_user

@router.get("/files/license/{filename}")
async def get_license_file(filename: str, current_user: models.User = Depends(get_current_user)):
    """Get license file - admin only"""
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access license files"
        )
    
    file_path = LICENSE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path)

@router.get("/files/profile/{filename}")
async def get_profile_image(filename: str, current_user: models.User = Depends(get_current_user)):
    """Get profile image - admin only"""
    if current_user.user_type != models.UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access profile images"
        )
    
    file_path = PROFILE_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(file_path) 