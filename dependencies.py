from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth.routes import get_current_user
from auth.models import User, UserType

# Dependency to get DB session
get_db_dep = Depends(get_db)

# Dependency to get current user
get_current_user_dep = Depends(get_current_user)

# Dependency to require admin

def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Dependency to require specialist

def require_specialist(current_user: User = Depends(get_current_user)):
    if current_user.user_type != UserType.SPECIALIST:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    if not current_user.is_active or getattr(current_user, 'status', None) != 'active':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Specialist account is not active"
        )
    return current_user 