from pydantic import BaseModel

class AdminBase(BaseModel):
    username: str
    password: str

class AdminCreate(AdminBase):
    pass

class AdminOut(AdminBase):
    id: int
    is_superuser: bool

    class Config:
        orm_mode = True 