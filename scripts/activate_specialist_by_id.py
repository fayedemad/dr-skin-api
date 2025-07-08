import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal
from auth.models import UserStatus
from auth.queries import get_user
from specialists.queries import get_specialist_by_user_id

async def activate_specialist_by_id(user_id: int):
    async with AsyncSessionLocal() as db:
        # Get the user
        user = await get_user(db, user_id=user_id)
        if not user:
            print(f"Error: User with ID {user_id} not found")
            return
        
        # Check if user is a specialist
        if user.user_type.value != "specialist":
            print(f"Error: User with ID {user_id} is not a specialist (user_type: {user.user_type.value})")
            return
        
        # Check if user already has a specialist profile
        specialist = await get_specialist_by_user_id(db, user_id)
        if not specialist:
            print(f"Error: Specialist profile not found for user ID {user_id}")
            return
        
        # Activate the user and specialist
        user.status = UserStatus.ACTIVE
        user.is_active = True
        specialist.is_approved = True
        
        await db.commit()
        await db.refresh(user)
        await db.refresh(specialist)
        
        print(f"Successfully activated specialist:")
        print(f"  User ID: {user.id}")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Specialist ID: {specialist.id}")
        print(f"  Name: {specialist.name}")
        print(f"  Specialization: {specialist.specialization}")
        print(f"  Status: {user.status}")
        print(f"  Is Active: {user.is_active}")
        print(f"  Is Approved: {specialist.is_approved}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python activate_specialist_by_id.py <user_id>")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
    except ValueError:
        print("Error: user_id must be an integer")
        sys.exit(1)
    
    asyncio.run(activate_specialist_by_id(user_id)) 