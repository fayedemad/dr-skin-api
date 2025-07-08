from pydantic import BaseModel
from typing import Optional
from auth.schemas import UserOut

class SpecialistBase(BaseModel):
    # Non-updatable fields
    license_number: str
    specialization: str
    
    # Updatable fields
    name: str
    phone_number: str
    hospital: str
    bio: str
    profile_image: Optional[str] = None
    license_file_path: Optional[str] = None

class SpecialistCreate(SpecialistBase):
    user_id: int

class SpecialistUpdate(BaseModel):
    # Only updatable fields
    name: Optional[str] = None
    phone_number: Optional[str] = None
    hospital: Optional[str] = None
    bio: Optional[str] = None
    specialization: Optional[str] = None
    profile_image: Optional[str] = None

class SpecialistOut(SpecialistBase):
    id: int
    user_id: int
    is_approved: bool
    user: UserOut

    class Config:
        orm_mode = True

class SpecialistFilter(BaseModel):
    specialization: Optional[str] = None
    hospital: Optional[str] = None
    name: Optional[str] = None
    is_approved: Optional[bool] = None
    phone_number: Optional[str] = None 