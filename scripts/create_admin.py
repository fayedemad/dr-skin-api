import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal
from auth import models, schemas
from auth.security import get_password_hash
from auth.queries import get_user_by_username, get_user_by_email

async def create_admin_user(username: str, email: str, password: str):
    async with AsyncSessionLocal() as db:
        # Check if username exists
        existing_user = await get_user_by_username(db, username=username)
        if existing_user:
            print(f"Error: Username '{username}' already exists")
            return
        
        # Check if email exists
        existing_email = await get_user_by_email(db, email=email)
        if existing_email:
            print(f"Error: Email '{email}' already exists")
            return
        
        # Create admin user
        hashed_password = get_password_hash(password)
        db_user = models.User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            user_type=models.UserType.ADMIN,
            status=models.UserStatus.ACTIVE,
            is_active=True,
            is_superuser=True
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        print(f"Successfully created admin user: {username}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python create_admin.py <username> <email> <password>")
        sys.exit(1)
    
    username = sys.argv[1]
    email = sys.argv[2]
    password = sys.argv[3]
    
    asyncio.run(create_admin_user(username, email, password)) 