from pydantic import BaseModel
from auth.schemas import UserOut

class AdminBase(BaseModel):
    is_superuser: bool = True

class AdminCreate(AdminBase):
    user_id: int

class AdminOut(AdminBase):
    id: int
    user: UserOut

    class Config:
        orm_mode = True

class DashboardStats(BaseModel):
    total_users: int
    total_specialists: int
    total_appointments: int 