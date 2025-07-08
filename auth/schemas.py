from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from auth.models import UserType, UserStatus

class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: int
    user_type: UserType
    status: UserStatus
    is_active: bool
    is_superuser: bool

    class Config:
        orm_mode = True

class SpecialistRegistration(BaseModel):
    # User fields
    username: str
    email: EmailStr
    password: str
    
    # Specialist fields
    name: str
    phone_number: str
    license_number: str
    specialization: str
    hospital: str
    bio: str

class SpecialistRegistrationForm(BaseModel):
    # User fields
    username: str
    email: EmailStr
    password: str
    
    # Specialist fields
    name: str
    phone_number: str
    license_number: str
    specialization: str
    hospital: str
    bio: str

    @validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must be at least 3 characters long')
        if not v.isalnum():
            raise ValueError('Username must contain only letters and numbers')
        return v

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v

    @validator('phone_number')
    def validate_phone(cls, v):
        if not v.startswith('+'):
            raise ValueError('Phone number must start with +')
        if len(v) < 10:
            raise ValueError('Phone number must be at least 10 characters long')
        return v

    @validator('license_number')
    def validate_license(cls, v):
        if len(v) < 3:
            raise ValueError('License number must be at least 3 characters long')
        return v

    @validator('bio')
    def validate_bio(cls, v):
        if len(v) < 10:
            raise ValueError('Bio must be at least 10 characters long')
        return v

class SpecialistRegistrationResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    user_type: UserType
    status: UserStatus
    is_active: bool
    is_superuser: bool
    message: str

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str
    user_type: UserType 