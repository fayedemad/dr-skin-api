import asyncio
import sys
import os

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from database import AsyncSessionLocal
from sqlalchemy import text

async def add_license_file_path_column():
    async with AsyncSessionLocal() as db:
        try:
            # Check if the column already exists
            result = await db.execute(text("""
                PRAGMA table_info(specialists);
            """))
            columns = result.fetchall()
            column_names = [col[1] for col in columns]
            
            if 'license_file_path' not in column_names:
                # Add the license_file_path column
                await db.execute(text("""
                    ALTER TABLE specialists 
                    ADD COLUMN license_file_path TEXT;
                """))
                await db.commit()
                print("Successfully added license_file_path column to specialists table")
            else:
                print("license_file_path column already exists")
                
        except Exception as e:
            print(f"Error adding column: {e}")
            await db.rollback()

if __name__ == "__main__":
    asyncio.run(add_license_file_path_column()) 