import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal
from auth.models import UserStatus
from auth.queries import get_user_by_username
from specialists.queries import get_specialist_by_user_id

async def approve_specialist(username: str):
    async with AsyncSessionLocal() as db:
        try:
            # Get the user
            user = await get_user_by_username(db, username=username)
            if not user:
                print(f"Error: User '{username}' not found")
                return
            
            # Check if user is a specialist
            if user.user_type.value != "specialist":
                print(f"Error: User '{username}' is not a specialist")
                return
            
            # Check if user already has a specialist profile
            specialist = await get_specialist_by_user_id(db, user.id)
            if not specialist:
                print(f"Error: Specialist profile not found for user '{username}'")
                return
            
            # Approve the user and specialist
            user.status = UserStatus.ACTIVE
            user.is_active = True
            specialist.is_approved = True
            
            await db.commit()
            print(f"Successfully approved specialist: {username}")
            print(f"User ID: {user.id}")
            print(f"Specialist ID: {specialist.id}")
            
        except Exception as e:
            print(f"Error approving specialist: {e}")
            await db.rollback()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python approve_specialist.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    asyncio.run(approve_specialist(username)) 