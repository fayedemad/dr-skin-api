from sqlalchemy import Column, Integer, String, Boolean, Enum
from sqlalchemy.orm import relationship
from models import Base
import enum

class UserType(str, enum.Enum):
    ADMIN = "admin"
    SPECIALIST = "specialist"

class UserStatus(str, enum.Enum):
    ACTIVE = "active"
    PENDING = "pending"
    INACTIVE = "inactive"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    user_type = Column(Enum(UserType), nullable=False)
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

    # Relationship with Specialist model
    specialist = relationship("Specialist", back_populates="user", uselist=False)

# Add the relationship after both models are defined
from specialists.models import Specialist
User.specialist = relationship("Specialist", back_populates="user", uselist=False) 