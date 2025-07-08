import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal
from auth.models import UserStatus
from auth.queries import get_user_by_username

async def fix_admin_status(username: str):
    async with AsyncSessionLocal() as db:
        try:
            # Get the user
            user = await get_user_by_username(db, username=username)
            if not user:
                print(f"Error: User '{username}' not found")
                return
            
            # Check if user is an admin
            if user.user_type.value != "admin":
                print(f"Error: User '{username}' is not an admin")
                return
            
            # Fix the status
            user.status = UserStatus.ACTIVE
            user.is_active = True
            
            await db.commit()
            print(f"Successfully fixed admin status: {username}")
            print(f"Status: {user.status}")
            print(f"Is Active: {user.is_active}")
            
        except Exception as e:
            print(f"Error fixing admin status: {e}")
            await db.rollback()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python fix_admin_status.py <username>")
        sys.exit(1)
    
    username = sys.argv[1]
    asyncio.run(fix_admin_status(username)) 