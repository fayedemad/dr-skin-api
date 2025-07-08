from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models import Base

class Specialist(Base):
    __tablename__ = 'specialists'
    
    # Non-updatable fields (require admin approval)
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    license_number = Column(String, nullable=False)
    specialization = Column(String, nullable=False)
    
    # Updatable fields
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, nullable=False)
    hospital = Column(String, nullable=False)
    bio = Column(Text, nullable=False)
    profile_image = Column(String, nullable=True)
    license_file_path = Column(String, nullable=True)
    is_approved = Column(Boolean, default=False)
    
    # Relationship with User model
    user = relationship("User", back_populates="specialist") 