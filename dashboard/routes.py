from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from dashboard import models, schemas, queries, transactions
from database import get_db
from auth.routes import get_current_user
from auth.models import User, UserType

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

async def get_current_admin(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions"
        )
    admin = await queries.get_admin_by_user_id(db, current_user.id)
    if not admin:
        raise HTTPException(
            status_code=404,
            detail="Admin profile not found"
        )
    return admin

@router.get("/stats", response_model=schemas.DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admin users can access dashboard stats"
        )
    
    stats, error = await transactions.get_dashboard_data_transaction(db)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return stats

@router.get("/me", response_model=schemas.AdminOut)
async def read_admin_me(current_admin: models.Admin = Depends(get_current_admin)):
    return current_admin

@router.get("/admins", response_model=list[schemas.AdminOut])
async def list_admins(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admin users can list admins"
        )
    return await queries.get_admins(db, skip=skip, limit=limit)

@router.get("/admins/{admin_id}", response_model=schemas.AdminOut)
async def get_admin(
    admin_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admin users can view admin details"
        )
    
    admin = await queries.get_admin(db, admin_id)
    if not admin:
        raise HTTPException(status_code=404, detail="Admin not found")
    return admin 