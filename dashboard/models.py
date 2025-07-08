from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from models import Base
from auth.models import User

class Admin(Base):
    __tablename__ = 'admins'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), unique=True)
    is_superuser = Column(Boolean, default=True)
    
    # Relationship with User model
    user = relationship("User", backref="admin_profile") 