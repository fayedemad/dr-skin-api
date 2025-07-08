from pydantic import BaseModel
from typing import Optional

class SpecialistBase(BaseModel):
    name: str
    phone_number: str
    specialization: str
    license_number: str
    hospital: str
    bio: str
    profile_image: Optional[str] = None

class SpecialistCreate(SpecialistBase):
    pass

class SpecialistOut(SpecialistBase):
    id: int

    class Config:
        orm_mode = True 